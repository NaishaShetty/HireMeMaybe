from sentence_transformers import (
    SentenceTransformer
)

MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

model = SentenceTransformer(
    MODEL_NAME
)


def get_model():

    return model