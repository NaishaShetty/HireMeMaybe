from app.similarity.model_loader import (
    get_model
)


def generate_embedding(
    text
):

    model = get_model()

    embedding = model.encode(
        text,
        convert_to_numpy=True
    )

    return embedding