from app.core.config import get_settings


def get_embedding_model():
    from langchain_huggingface import HuggingFaceEmbeddings

    return HuggingFaceEmbeddings(model_name=get_settings().embedding_model)
