from safety.grounding_validator import validate_grounding


# Chroma distance:
# lower = stronger semantic similarity
MAX_GROUNDING_DISTANCE = 1.50


def check_safety(
    confidence,
    risk_score,
    rag_results,
    user_message,
    fraud_type="OTHER"
):
    reasons = []

    # ------------------------------------------------------------
    # Normalize inputs
    # ------------------------------------------------------------

    if not isinstance(rag_results, dict):
        rag_results = {}

    investigation_results = rag_results.get("results", []) or []

    fraud_type = str(fraud_type or "OTHER").upper()

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0

    try:
        risk_score = int(risk_score)
    except (TypeError, ValueError):
        risk_score = 0

    # ------------------------------------------------------------
    # Prompt-injection defense
    # ------------------------------------------------------------

    injection_patterns = [
        "ignore previous instructions",
        "ignore all instructions",
        "system prompt",
        "reveal your instructions",
        "developer message",
    ]

    message_lower = (user_message or "").lower()

    for pattern in injection_patterns:
        if pattern in message_lower:
            reasons.append("possible_prompt_injection")
            break

    # ------------------------------------------------------------
    # Confidence guardrail
    # ------------------------------------------------------------

    if confidence <= 0.70:
        reasons.append("low_confidence")

    # ------------------------------------------------------------
    # Ambiguous classification guardrail
    # ------------------------------------------------------------

    if fraud_type == "OTHER":
        reasons.append("ambiguous_classification")

    # ------------------------------------------------------------
    # Grounding validation
    # ------------------------------------------------------------

    grounding = validate_grounding(
        fraud_type=fraud_type,
        rag_results=rag_results,
        confidence=confidence,
    )

    # ------------------------------------------------------------
    # NOT_FRAUD
    # ------------------------------------------------------------

    is_confident_not_fraud = (
        fraud_type == "NOT_FRAUD"
        and confidence > 0.70
        and risk_score == 0
    )

    # ------------------------------------------------------------
    # Grounding guardrail
    # ------------------------------------------------------------

    if not is_confident_not_fraud:

        # No evidence at all
        if not investigation_results:
            reasons.append("insufficient_grounding")

        # Evidence exists but validator says not grounded
        elif not grounding.get("grounded", False):

            status = grounding.get("status", "")

            # ----------------------------------------------------
            # STRONG semantic evidence with metadata mismatch
            #
            # For a confidently classified, known fraud type,
            # strong trusted semantic evidence can still support
            # the classification even if the stored RAG category
            # differs.
            #
            # IMPORTANT:
            # OTHER is NOT allowed through this path.
            # Ambiguous cases must still escalate.
            # ----------------------------------------------------

            best_distance = grounding.get("best_distance")

            strong_semantic_evidence = (
                fraud_type != "OTHER"
                and fraud_type != "NOT_FRAUD"
                and status == "MISMATCH"
                and isinstance(best_distance, (int, float))
                and best_distance <= MAX_GROUNDING_DISTANCE
                and confidence > 0.70
            )

            if strong_semantic_evidence:
                # Do NOT add an escalation reason.
                #
                # The evidence is semantically strong enough
                # for a known and confidently classified fraud.
                pass

            elif status == "MISMATCH":
                reasons.append("grounding_type_mismatch")
                reasons.append("weak_grounding")

            elif status == "LOW_CONFIDENCE":
                # low_confidence already recorded above
                reasons.append("weak_grounding")

            else:
                reasons.append("weak_grounding")

    # ------------------------------------------------------------
    # High-risk evidence guardrail
    # ------------------------------------------------------------

    if risk_score >= 75 and not investigation_results:
        reasons.append("high_risk_without_evidence")

    # ------------------------------------------------------------
    # Final decision
    # ------------------------------------------------------------

    decision = "ESCALATE" if reasons else "CONTINUE"

    return {
        "decision": decision,
        "safe": decision == "CONTINUE",
        "reasons": reasons,
        "grounding": grounding,
    }