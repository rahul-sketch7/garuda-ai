# ============================================================
# Garuda AI - RAG Retriever
# ============================================================

from rag.knowledge_base import KNOWLEDGE
from rag.vector_store import collection


# ============================================================
# INITIALIZE KNOWLEDGE BASE
# ============================================================

def initialize_knowledge_base():
    """
    Add Garuda AI fraud knowledge to ChromaDB
    if the collection is empty.
    """

    existing = collection.count()

    # Knowledge already exists
    if existing > 0:
        return

    documents = []
    metadatas = []
    ids = []

    for index, item in enumerate(KNOWLEDGE):

        documents.append(
            item["evidence"]
        )

        metadatas.append({
            "title": item["title"],
            "fraud_type": item["fraud_type"],
            "source": item.get(
                "source",
                "Unknown source"
            ),
            "source_url": item.get(
                "source_url",
                ""
            )
        })

        ids.append(
            f"garuda_knowledge_{index + 1}"
        )

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )


# ============================================================
# SEARCH KNOWLEDGE
# ============================================================

def search_knowledge(
    query: str,
    n_results: int = 3
):
    """
    Retrieve relevant fraud knowledge from ChromaDB.
    """

    # Make sure knowledge exists
    initialize_knowledge_base()

    # Search ChromaDB
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    return results