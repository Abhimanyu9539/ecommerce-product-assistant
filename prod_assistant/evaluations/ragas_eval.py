from ragas import SingleTurnSample
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import LLMContextPrecisionWithoutReference, ResponseRelevancy
from utils.model_loader import ModelLoader
import grpc.experimental.aio as grpc_aio
grpc_aio.init_grpc_aio()

model_loader = ModelLoader()


def evaluate_context_precision():
    """
    """
    pass

def evaluate_response_relevancy():
    """
    """
    pass
