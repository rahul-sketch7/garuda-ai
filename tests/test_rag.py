# ============================================================
# Garuda AI - RAG Test
# ============================================================

from rag.retriever import search_knowledge


query = (
    "Someone claiming to be from my bank "
    "is asking me for my OTP"
)


results = search_knowledge(
    query=query,
    n_results=3
)


print("\n")
print("=" * 60)
print("GARUDA AI RAG RESULTS")
print("=" * 60)


for index, result in enumerate(
    results["documents"][0],
    start=1
):

    metadata = results["metadatas"][0][index - 1]

    distance = results["distances"][0][index - 1]

    print(f"\n[{index}]")

    print(
        "Title:",
        metadata.get("title")
    )

    print(
        "Fraud Type:",
        metadata.get("fraud_type")
    )

    print(
        "Source:",
        metadata.get(
            "source",
            "N/A"
        )
    )

    print(
        "Relevance Distance:",
        distance
    )

    print(
        "Evidence:",
        result
    )


print("\n")
print("=" * 60)
print("END OF RAG TEST")
print("=" * 60)