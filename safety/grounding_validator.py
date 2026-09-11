# safety/grounding_validator.py

STRONG_DISTANCE = 1.50


def validate_grounding(
    fraud_type,
    rag_results,
    confidence
):
    """
    Validate whether retrieved RAG evidence supports
    the predicted fraud type.

    Returns:
        grounded: bool
        status: STRONG / WEAK / MISMATCH / NONE / NOT_REQUIRED / LOW_CONFIDENCE
        score: evidence score
        reason: explanation
        best_distance: best relevance distance
        matching_evidence: evidence matching the fraud type
    """

    # ------------------------------------------------------------
    # Normalize inputs
    # ------------------------------------------------------------

    fraud_type = str(fraud_type or "OTHER").upper()

    if not isinstance(rag_results, dict):
        rag_results = {}

    results = rag_results.get("results", []) or []

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0

    # ------------------------------------------------------------
    # NOT_FRAUD
    # ------------------------------------------------------------

    if fraud_type == "NOT_FRAUD":
        return {
            "grounded": True,
            "status": "NOT_REQUIRED",
            "score": 1.0,
            "reason": (
                "Legitimate messages do not require fraud-specific "
                "grounding evidence."
            ),
            "best_distance": None,
            "matching_evidence": [],
        }

    # ------------------------------------------------------------
    # No evidence
    # ------------------------------------------------------------

    if not results:
        return {
            "grounded": False,
            "status": "NONE",
            "score": 0.0,
            "reason": (
                "No investigation evidence was retrieved."
            ),
            "best_distance": None,
            "matching_evidence": [],
        }

    # ------------------------------------------------------------
    # Confidence guard
    # ------------------------------------------------------------

    if confidence <= 0.70:
        return {
            "grounded": False,
            "status": "LOW_CONFIDENCE",
            "score": 0.0,
            "reason": (
                "Classification confidence is too low for "
                "strong grounding."
            ),
            "best_distance": None,
            "matching_evidence": [],
        }

    # ------------------------------------------------------------
    # Examine retrieved evidence
    # ------------------------------------------------------------

    matching = []
    scored = []

    for item in results:

        if not isinstance(item, dict):
            continue

        evidence_type = str(
            item.get("fraud_type", "")
        ).upper()

        distance = item.get("relevance_distance")

        try:
            distance = float(distance)
        except (TypeError, ValueError):
            distance = None

        entry = {
            "item": item,
            "distance": distance,
        }

        scored.append(entry)

        # Exact fraud-type match
        if evidence_type == fraud_type:
            matching.append(entry)

    # ------------------------------------------------------------
    # Matching evidence exists
    # ------------------------------------------------------------

    if matching:

        # Prefer the closest matching evidence.
        matching_with_distance = [
            entry
            for entry in matching
            if entry["distance"] is not None
        ]

        if matching_with_distance:

            best = min(
                matching_with_distance,
                key=lambda entry: entry["distance"]
            )

            best_distance = best["distance"]

            # Strong enough matching evidence
            if best_distance <= STRONG_DISTANCE:

                return {
                    "grounded": True,
                    "status": "STRONG",
                    "score": round(
                        1.0 / (1.0 + best_distance),
                        4
                    ),
                    "reason": (
                        f"Retrieved evidence matches "
                        f"{fraud_type} with strong relevance."
                    ),
                    "best_distance": best_distance,
                    "matching_evidence": [
                        entry["item"]
                        for entry in sorted(
                            matching_with_distance,
                            key=lambda entry: entry["distance"]
                        )
                    ],
                }

            # Matching type exists, but evidence is weak
            return {
                "grounded": False,
                "status": "WEAK",
                "score": round(
                    1.0 / (1.0 + best_distance),
                    4
                ),
                "reason": (
                    f"Evidence matches {fraud_type}, "
                    f"but relevance is weak."
                ),
                "best_distance": best_distance,
                "matching_evidence": [
                    entry["item"]
                    for entry in sorted(
                        matching_with_distance,
                        key=lambda entry: entry["distance"]
                    )
                ],
            }

        # Matching metadata exists but no relevance score.
        return {
            "grounded": False,
            "status": "WEAK",
            "score": 0.0,
            "reason": (
                f"Evidence matches {fraud_type}, "
                f"but no grounding relevance score was provided."
            ),
            "best_distance": None,
            "matching_evidence": [
                entry["item"]
                for entry in matching
            ],
        }

    # ------------------------------------------------------------
    # No matching fraud type
    # ------------------------------------------------------------

    scored_with_distance = [
        entry
        for entry in scored
        if entry["distance"] is not None
    ]

    if scored_with_distance:

        best_any = min(
            scored_with_distance,
            key=lambda entry: entry["distance"]
        )

        best_distance = best_any["distance"]

        return {
            "grounded": False,
            "status": "MISMATCH",
            "score": round(
                1.0 / (1.0 + best_distance),
                4
            ),
            "reason": (
                f"No matching fraud-type evidence was "
                f"retrieved for {fraud_type}."
            ),
            "best_distance": best_distance,
            "matching_evidence": [],
        }

    # ------------------------------------------------------------
    # Evidence exists but no relevance scores
    # ------------------------------------------------------------

    return {
        "grounded": False,
        "status": "MISMATCH",
        "score": 0.0,
        "reason": (
            f"No matching fraud-type evidence was "
            f"retrieved for {fraud_type}."
        ),
        "best_distance": None,
        "matching_evidence": [],
    }


__all__ = ["validate_grounding"]