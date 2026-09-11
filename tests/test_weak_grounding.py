# ============================================================
# Garuda AI - Weak Grounding Safety Test
# ============================================================

from safety.safety_critic import check_safety


print()
print("=" * 60)
print("GARUDA AI WEAK GROUNDING TEST")
print("=" * 60)


# ============================================================
# SIMULATED WEAK RAG RESULT
# ============================================================

weak_rag_results = {

    "results": [

        {
            "title": "Weakly related evidence",
            "fraud_type": "GENERAL",
            "evidence": "This evidence is not strongly related to the message.",
            "source": "Test Source",
            "source_url": "https://example.com",
            "relevance_distance": 1.80
        },

        {
            "title": "Another weak result",
            "fraud_type": "GENERAL",
            "evidence": "This is another weakly related evidence chunk.",
            "source": "Test Source",
            "source_url": "https://example.com",
            "relevance_distance": 1.90
        }
    ]
}


# ============================================================
# RUN SAFETY CHECK
# ============================================================

result = check_safety(

    confidence=0.95,

    risk_score=90,

    rag_results=weak_rag_results,

    user_message="Please check this unusual message."
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print()
print("SAFETY RESULT:")
print(result)


# ============================================================
# VALIDATION
# ============================================================

assert result["decision"] == "ESCALATE"

assert result["safe"] is False

assert "weak_grounding" in result["reasons"]


print()
print("TEST PASSED")
print("Weak RAG evidence correctly triggered escalation.")


print()
print("=" * 60)
print("END OF WEAK GROUNDING TEST")
print("=" * 60)