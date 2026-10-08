import faiss
import numpy as np

from backend.tools.agriculture_documents import (
    get_documents,
    get_embeddings,
    get_embedding_model
)


# ==================================================
# LOAD DOCUMENTS
# ==================================================

documents = get_documents()

embeddings = get_embeddings()

embedding_model = get_embedding_model()


# ==================================================
# CREATE FAISS INDEX
# ==================================================

embeddings = np.array(
    embeddings
).astype("float32")


dimension = embeddings.shape[1]


index = faiss.IndexFlatL2(
    dimension
)


index.add(
    embeddings
)


# ==================================================
# RAG SEARCH TOOL
# ==================================================

def agriculture_rag_tool(
    query,
    top_k=5
):

    # ----------------------------------------------
    # CREATE QUERY EMBEDDING
    # ----------------------------------------------

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True
    )


    query_embedding = np.array(
        query_embedding
    ).astype("float32")


    # ----------------------------------------------
    # SEARCH FAISS
    # ----------------------------------------------

    distances, indices = index.search(
        query_embedding,
        top_k
    )


    results = []


    # ----------------------------------------------
    # COLLECT RESULTS
    # ----------------------------------------------

    for i, distance in zip(
        indices[0],
        distances[0]
    ):

        if i < 0:
            continue


        results.append({

            "content": documents[i],

            "similarity_score": round(
                float(distance),
                4
            )

        })


    # ----------------------------------------------
    # RETURN RESULTS
    # ----------------------------------------------

    return {

        "query": query,

        "results": results

    }