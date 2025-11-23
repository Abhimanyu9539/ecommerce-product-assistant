from ragas import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import LLMContextPrecisionWithoutReference, ResponseRelevancy
from utils.model_loader import ModelLoader
import grpc.experimental.aio as grpc_aio
import asyncio
from exception.custom_exception import ProductAssistantException
grpc_aio.init_grpc_aio()

model_loader = ModelLoader()


def evaluate_context_precision(query, response, retrieved_context):
    try:
        sample = SingleTurnSample(
            user_input=query,
            response=response,
            retrieved_contexts=retrieved_context,
        )

        async def main():
            llm = model_loader.load_llm()
            evaluator_llm = LangchainLLMWrapper(llm)
            context_precision = LLMContextPrecisionWithoutReference(llm=evaluator_llm)
            result = await context_precision.single_turn_ascore(sample)
            return result

        return asyncio.run(main())
    except Exception as e:
        #log.error("Error evaluating context precision", error=str(e))
        raise ProductAssistantException("Failed to evaluate context precision", e)

def evaluate_response_relevancy(query, response, retrieved_context):
    try:
        sample = SingleTurnSample(
            user_input=query,
            response=response,
            retrieved_contexts=retrieved_context,
        )

        async def main():
            llm = model_loader.load_llm()
            evaluator_llm = LangchainLLMWrapper(llm)
            embedding_model = model_loader.load_embeddings()
            evaluator_embeddings = LangchainEmbeddingsWrapper(embedding_model)
            scorer = ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings)
            result = await scorer.single_turn_ascore(sample)
            return result

        return asyncio.run(main())
    except Exception as e:
        #log.error("Error evaluating response relevancy", error=str(e))
        raise ProductAssistantException("Failed to evaluate response relevancy", e)