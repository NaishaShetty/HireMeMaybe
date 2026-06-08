from sklearn.metrics.pairwise import (
    cosine_similarity
)

from app.similarity.embedding_service import (
    generate_embedding
)


def calculate_similarity(
    resume_text,
    jd_text
):

    resume_embedding = (
        generate_embedding(
            resume_text
        )
    )

    jd_embedding = (
        generate_embedding(
            jd_text
        )
    )

    similarity = cosine_similarity(
        [resume_embedding],
        [jd_embedding]
    )[0][0]

    return round(
        float(similarity),
        4
    )