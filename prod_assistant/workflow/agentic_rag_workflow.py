from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from prompt_library.prompts import PROMPT_REGISTRY, PromptType
from retriever.retrieval import Retriever
from utils.model_loader import ModelLoader

retriever_obj = Retriever()
model_loader = ModelLoader()
llm = model_loader.load_llm()


# ---------- State Definition ----------
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# ---------- Helper for formatting ----------
def format_docs(docs) -> str:
    """Format a list of documents into a string.

    Args:
        docs (List[Document]): The list of documents to be formatted.

    Returns:
        str: The formatted string containing the titles, prices, ratings, and reviews of the documents.
    """
    if not docs:
        return "No relevant documents found."
    formatted_chunks = []
    for d in docs:
        meta = d.metadata or {}
        formatted = (
            f"Title: {meta.get('product_title', 'N/A')}\n"
            f"Price: {meta.get('price', 'N/A')}\n"
            f"Rating: {meta.get('rating', 'N/A')}\n"
            f"Reviews:\n{d.page_content.strip()}"
        )
        formatted_chunks.append(formatted)
    return "\n\n---\n\n".join(formatted_chunks)


# ---------- Nodes ----------
def ai_assistant(state: AgentState):
    """Decide whether to call retriever or just answer directly."""
    print("--- CALL ASSISTANT ---")
    messages = state["messages"]
    last_message = messages[-1].content

    # Simple routing: if query mentions product → go retriever
    if any(word in last_message.lower() for word in ["price", "review", "product"]):
        return {"messages": [HumanMessage(content="TOOL: retriever")]}
    else:
        # direct answer without retriever
        prompt = ChatPromptTemplate.from_template(
            "You are a helpful assistant. Answer the user directly.\n\nQuestion: {question}\nAnswer:"
        )
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"question": last_message})
        return {"messages": [HumanMessage(content=response)]}


def vector_retriever(state: AgentState):
    """Fetch product info from vector DB."""
    print("--- RETRIEVER ---")
    query = state["messages"][-1].content
    retriever = retriever_obj.load_retriever()
    docs = retriever.invoke(query)
    context = format_docs(docs)
    return {"messages": [HumanMessage(content=context)]}


def grade_documents(state: AgentState) -> Literal["generator", "rewriter"]:
    """Grade docs relevance."""
    print("--- GRADER ---")
    question = state["messages"][0].content
    docs = state["messages"][-1].content

    prompt = PromptTemplate(
        template="""You are a grader. Question: {question}\nDocs: {docs}\n
        Are docs relevant to the question? Answer yes or no.""",
        input_variables=["question", "docs"],
    )
    chain = prompt | llm | StrOutputParser()
    score = chain.invoke({"question": question, "docs": docs})
    return "generator" if "yes" in score.lower() else "rewriter"


def generate(state: AgentState):
    """Generate final answer with docs."""
    print("--- GENERATE ---")
    question = state["messages"][0].content
    docs = state["messages"][-1].content
    prompt = ChatPromptTemplate.from_template(
        PROMPT_REGISTRY[PromptType.PRODUCT_BOT].template
    )
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"context": docs, "question": question})
    return {"messages": [HumanMessage(content=response)]}


def rewrite(state: AgentState):
    """Rewrite bad query."""
    print("--- REWRITE ---")
    question = state["messages"][0].content
    new_q = llm.invoke(
        [HumanMessage(content=f"Rewrite the query to be clearer: {question}")]
    )
    return {"messages": [HumanMessage(content=new_q.content)]}


# ---------- Build Workflow ----------
workflow = StateGraph(AgentState)
workflow.add_node("Assistant", ai_assistant)
workflow.add_node("Retriever", vector_retriever)
workflow.add_node("Generator", generate)
workflow.add_node("Rewriter", rewrite)

# edges
workflow.add_edge(START, "Assistant")
workflow.add_conditional_edges(
    "Assistant",
    lambda state: "Retriever" if "TOOL" in state["messages"][-1].content else END,
    {"Retriever": "Retriever", END: END},
)
workflow.add_conditional_edges(
    "Retriever",
    grade_documents,
    {"generator": "Generator", "rewriter": "Rewriter"},
)
workflow.add_edge("Generator", END)
workflow.add_edge("Rewriter", "Assistant")

app = workflow.compile()


# ---------- Run ----------
if __name__ == "__main__":
    result = app.invoke({"messages": [HumanMessage(content="What is the price of iPhone 15?")]})
    print("\nFinal Answer:\n", result["messages"][-1].content)