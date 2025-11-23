import os
from langchain_astradb import AstraDBVectorStore
from utils.config_loader import load_config
from utils.model_loader import ModelLoader
from dotenv import load_dotenv  
from langchain_classic.retrievers.document_compressors import LLMChainFilter
from langchain_classic.retrievers import ContextualCompressionRetriever
from evaluations.ragas_eval import evaluate_response_relevancy, evaluate_context_precision

class Retriever:
    def __init__(self):
        """
        Initialize the Retriever object.

        This class is responsible for retrieving the most relevant
        documents from the AstraDB vector store based on the user's
        query.
        """
        self.model_loader = ModelLoader()
        self.config = load_config()
        self._load_env_variables()
        self.vstore = None
        self.retriever = None

    def _load_env_variables(self):
        """
        Load and validate required environment variables.
        """
        load_dotenv()
        
        required_vars = ["OPENAI_API_KEY", "ASTRA_DB_API_ENDPOINT", "ASTRA_DB_APPLICATION_TOKEN", "ASTRA_DB_KEYSPACE"]
        
        missing_vars = [var for var in required_vars if os.getenv(var) is None]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.db_api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        self.db_application_token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        self.db_keyspace = os.getenv("ASTRA_DB_KEYSPACE")

    def load_retriever(self):
        """
        Load the retriever model.

        If the retriever model is not already loaded, this method will load it.
        The retriever model is used to retrieve the most relevant documents from the AstraDB vector store based on the user's query.

        Returns:
            langchain.retriever.Retriever: The loaded retriever model.
        """
        if not self.vstore: 
            collection_name=self.config["astra_db"]["collection_name"]
            self.vstore = AstraDBVectorStore(
                embedding= self.model_loader.load_embeddings(),
                collection_name=collection_name,
                api_endpoint=self.db_api_endpoint,
                token=self.db_application_token,
                namespace=self.db_keyspace,
            )
            
        if not self.retriever:
            top_k = self.config["retriever"]["top_k"] if "retriever" in self.config else 3
            mmr_retriever = self.vstore.as_retriever(
                search_kwargs={"k": top_k, 
                               "fetch_k": 20, 
                               "score_threshold":0.3, 
                               "lambda_mult": 0.7 },
                search_type="mmr",
            )

            llm = self.model_loader.load_llm()

            compressor = LLMChainFilter.from_llm(llm=llm)
            self.retriever = ContextualCompressionRetriever(
                base_compressor=compressor,
                base_retriever=mmr_retriever
            )
            print("Retriever loaded successfully")
            return self.retriever

    def call_retriever(self, query):
        """
        Call the retriever with the given query and return the output.

        Parameters:
        query (str): The query to be passed to the retriever.

        Returns:
        List[Document]: The output of the retriever.
        """
        retriever = self.load_retriever()
        output = retriever.invoke(query)
        return output        

    
if __name__ == "__main__":
    user_query = "Can you tell me Samsung Galaxy S24?"
    retriever_obj  =  Retriever()
    retrieved_docs = retriever_obj.call_retriever(user_query)

    def _format_docs(docs) -> str:
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
        
    retrieved_contexts = [_format_docs(doc) for doc in retrieved_docs]
    
    #this is not an actual output this have been written to test the pipeline
    response="iphone 16 plus, iphone 16, iphone 15 are best phones under 1,00,000 INR."
    
    context_score = evaluate_context_precision(user_query,response,retrieved_contexts)
    relevancy_score = evaluate_response_relevancy(user_query,response,retrieved_contexts)
    
    print("\n--- Evaluation Metrics ---")
    print("Context Precision Score:", context_score)
    print("Response Relevancy Score:", relevancy_score)