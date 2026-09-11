# ============================================================
# Garuda AI - Scam Intelligence MCP Tool
# ============================================================

from rag.retriever import search_knowledge


# ============================================================
# SCAM INTELLIGENCE TOOL
# ============================================================

def search_scam_intelligence(
    query: str,
    n_results: int = 3
):
    """
    Search Garuda AI's trusted fraud intelligence
    knowledge base and return grounded evidence.
    """

    results = search_knowledge(
        query=query,
        n_results=n_results
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    formatted_results = []

    for index, document in enumerate(documents):

        # Get metadata safely
        metadata = (
            metadatas[index]
            if index < len(metadatas)
            else {}
        )

        # Get relevance distance safely
        distance = (
            distances[index]
            if index < len(distances)
            else None
        )

        # Format grounded evidence
        formatted_results.append({

            "title": metadata.get(
                "title",
                "Untitled evidence"
            ),

            "fraud_type": metadata.get(
                "fraud_type",
                "UNKNOWN"
            ),

            "evidence": document,

            "source": metadata.get(
                "source",
                "Unknown source"
            ),

            "source_url": metadata.get(
                "source_url",
                ""
            ),

            "relevance_distance": distance
        })

    # Return structured MCP response
    return {
        "query": query,
        "results": formatted_results
    }