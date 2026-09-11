# ============================================================
# Garuda AI - Escalation
# ============================================================


def create_escalation(
    user_message,
    risk_score,
    confidence,
    reasons,
    analysis=None,
    investigation=None,
    safety=None,
    trace=None
):
    """
    Create a complete human-review escalation package.

    The escalation contains the original message,
    AI analysis, risk information, retrieved evidence,
    safety decision, reasons, and execution trace.
    """

    # --------------------------------------------------------
    # Safely handle optional values
    # --------------------------------------------------------

    analysis = analysis or {}
    investigation = investigation or {}
    safety = safety or {}
    trace = trace or []

    # --------------------------------------------------------
    # Extract investigation results
    # --------------------------------------------------------

    investigation_results = investigation.get(
        "results",
        []
    )

    # --------------------------------------------------------
    # Prepare grounded evidence for human reviewer
    # --------------------------------------------------------

    evidence = []

    for result in investigation_results:

        evidence.append({
            "title": result.get(
                "title",
                "Untitled evidence"
            ),

            "fraud_type": result.get(
                "fraud_type",
                "UNKNOWN"
            ),

            "evidence": result.get(
                "evidence",
                ""
            ),

            "source": result.get(
                "source",
                "Unknown source"
            ),

            "source_url": result.get(
                "source_url",
                ""
            ),

            "relevance_distance": result.get(
                "relevance_distance"
            )
        })

    # --------------------------------------------------------
    # Return escalation package
    # --------------------------------------------------------

    return {

        "status": "ESCALATED",

        "message": (
            "Garuda AI could not safely complete this analysis. "
            "The case requires human verification."
        ),

        # Original user input
        "original_message": user_message,

        # AI analysis
        "analysis": analysis,

        # Risk information
        "risk": {
            "risk_score": risk_score,
            "confidence": confidence
        },

        # Why the case was escalated
        "escalation_reasons": reasons,

        # Safety decision
        "safety": safety,

        # Retrieved trusted evidence
        "grounding_evidence": evidence,

        # Original investigation response
        "investigation": investigation,

        # Full execution trace
        "trace": trace
    }