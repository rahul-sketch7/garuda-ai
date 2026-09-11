from pathlib import Path
import re


# ============================================================
# GARUDA AI — COMPATIBILITY FIX
# ============================================================
#
# This script fixes:
#
# 1. grounding_validator.py
#    - Strict fraud-type mismatch handling
#
# 2. safety_critic.py
#    - Adds weak_grounding reason for mismatch
#
# 3. signal_normalizer.py
#    - Adds normalize_result compatibility alias
#
# 4. explanation_agent.py
#    - Makes investigation optional for older callers/tests
#
# IMPORTANT:
# This script does NOT modify fraud_analyzer.py.
# ============================================================


ROOT = Path.cwd()


# ============================================================
# HELPER
# ============================================================

def replace_once(path, old, new, label):
    file_path = ROOT / path

    if not file_path.exists():
        print(f"[ERROR] {label}: file not found -> {file_path}")
        return False

    text = file_path.read_text(encoding="utf-8")

    if old not in text:
        print(f"[SKIP] {label}: target block not found")
        return False

    updated = text.replace(old, new, 1)

    file_path.write_text(updated, encoding="utf-8")

    print(f"[FIX]  {label}")
    return True


# ============================================================
# 1. FIX GROUNDING VALIDATOR
# ============================================================
#
# We want strict grounding:
#
# Correct fraud type + strong evidence
#       -> GROUNDED
#
# Wrong fraud type metadata
#       -> MISMATCH
#
# This prevents unrelated evidence from being treated as
# strong grounding merely because it is semantically similar.
# ============================================================


grounding_old = """    if not matching:
        # The fraud_type metadata is useful, but it is not the evidence
        # itself. Some trusted knowledge chunks can legitimately cover
        # multiple scam mechanisms even when stored under another category.
        # Forcing exact metadata equality would create false escalations.
        best_any = max(scored, key=lambda entry: entry["score"])
        best_distance = best_any["item"].get("relevance_distance")

        if (
            isinstance(best_distance, (int, float))
            and best_distance <= STRONG_DISTANCE
        ):
            return {
                "grounded": True,
                "status": "STRONG_SEMANTIC",
                "score": best_any["score"],
                "reason": (
                    "Strong trusted evidence was retrieved; category metadata "
                    "does not exactly match, but semantic relevance is strong."
                ),
                "best_distance": best_distance,
                "matching_evidence": [
                    entry["item"]
                    for entry in sorted(
                        scored,
                        key=lambda entry: entry["item"].get(
                            "relevance_distance", 999
                        )
                    )
                ],
            }

        return {
            "grounded": False,
            "status": "MISMATCH",
            "score": best_any["score"],
            "reason": (
                f"No matching fraud-type evidence was retrieved for "
                f"{fraud_type}, and the available evidence is not strongly "
                f"relevant."
            ),
            "best_distance": best_distance,
            "matching_evidence": [],
        }
"""


grounding_new = """    if not matching:
        best_any = max(scored, key=lambda entry: entry["score"])
        best_distance = best_any["item"].get("relevance_distance")

        return {
            "grounded": False,
            "status": "MISMATCH",
            "score": best_any["score"],
            "reason": (
                f"No matching fraud-type evidence was retrieved for "
                f"{fraud_type}."
            ),
            "best_distance": best_distance,
            "matching_evidence": [],
        }
"""


replace_once(
    "safety/grounding_validator.py",
    grounding_old,
    grounding_new,
    "strict grounding mismatch",
)


# ============================================================
# 2. FIX SAFETY CRITIC
# ============================================================
#
# Existing behavior:
#
#     grounding_type_mismatch
#
# The compatibility test additionally expects:
#
#     weak_grounding
#
# We keep BOTH reasons.
# ============================================================


safety_path = ROOT / "safety/safety_critic.py"

if safety_path.exists():

    text = safety_path.read_text(encoding="utf-8")

    safety_old = """            if grounding["status"] == "MISMATCH":
                reasons.append("grounding_type_mismatch")
            elif grounding["status"] == "LOW_CONFIDENCE":
"""

    safety_new = """            if grounding["status"] == "MISMATCH":
                reasons.append("grounding_type_mismatch")
                reasons.append("weak_grounding")
            elif grounding["status"] == "LOW_CONFIDENCE":
"""

    if safety_old in text:

        text = text.replace(
            safety_old,
            safety_new,
            1,
        )

        safety_path.write_text(
            text,
            encoding="utf-8",
        )

        print("[FIX]  safety weak-grounding reason")

    elif (
        'reasons.append("grounding_type_mismatch")' in text
        and 'reasons.append("weak_grounding")' in text
    ):

        print("[SKIP] safety weak-grounding reason: already fixed")

    else:

        print(
            "[SKIP] safety weak-grounding reason: target block not found"
        )

else:

    print(
        f"[ERROR] safety critic file not found -> {safety_path}"
    )


# ============================================================
# 3. FIX SIGNAL NORMALIZER
# ============================================================
#
# Your production function is:
#
#     normalize_signals()
#
# Older tests/components expect:
#
#     normalize_result()
#
# We simply create an alias.
# ============================================================


normalizer_path = ROOT / "agents/signal_normalizer.py"

if normalizer_path.exists():

    text = normalizer_path.read_text(
        encoding="utf-8"
    )

    if "normalize_result = normalize_signals" not in text:

        with normalizer_path.open(
            "a",
            encoding="utf-8",
        ) as file:

            file.write(
                "\n\n"
                "# ============================================================\n"
                "# BACKWARD COMPATIBILITY\n"
                "# ============================================================\n"
                "# Older tests/components use normalize_result().\n"
                "# Keep normalize_signals() as the main implementation.\n"
                "\n"
                "normalize_result = normalize_signals\n"
            )

        print(
            "[FIX]  signal normalizer backward compatibility"
        )

    else:

        print(
            "[SKIP] signal normalizer backward compatibility: "
            "already present"
        )

else:

    print(
        f"[ERROR] signal normalizer file not found -> "
        f"{normalizer_path}"
    )


# ============================================================
# 4. FIX EXPLANATION AGENT
# ============================================================
#
# Older test:
#
#     generate_explanation(
#         analysis,
#         risk,
#         rag_results
#     )
#
# Current production function also accepts:
#
#     investigation
#
# Make investigation optional so both callers work.
# ============================================================


explanation_path = ROOT / "agents/explanation_agent.py"

if explanation_path.exists():

    text = explanation_path.read_text(
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Case 1:
    # investigation is already optional
    # --------------------------------------------------------

    if "investigation=None" in text:

        print(
            "[SKIP] explanation investigation default: "
            "already optional"
        )

    else:

        # ----------------------------------------------------
        # Find the generate_explanation function.
        # ----------------------------------------------------

        pattern = r"""
        (def\s+generate_explanation\s*\(
            [^)]*?
        )
        """

        match = re.search(
            pattern,
            text,
            flags=re.DOTALL | re.VERBOSE,
        )

        if match:

            function_header = match.group(1)

            # ------------------------------------------------
            # Find the investigation parameter.
            # ------------------------------------------------

            investigation_match = re.search(
                r"\binvestigation\s*(?=[,)])",
                function_header,
            )

            if investigation_match:

                start = investigation_match.start()
                end = investigation_match.end()

                new_header = (
                    function_header[:start]
                    + "investigation=None"
                    + function_header[end:]
                )

                text = (
                    text[:match.start()]
                    + new_header
                    + text[match.end():]
                )

                explanation_path.write_text(
                    text,
                    encoding="utf-8",
                )

                print(
                    "[FIX]  explanation investigation default"
                )

            else:

                print(
                    "[SKIP] explanation investigation parameter "
                    "not found"
                )

        else:

            print(
                "[SKIP] explanation function not found"
            )

else:

    print(
        f"[ERROR] explanation agent file not found -> "
        f"{explanation_path}"
    )


# ============================================================
# FINISHED
# ============================================================

print()
print("=" * 60)
print("GARUDA AI COMPATIBILITY FIX COMPLETE")
print("=" * 60)
print()
print("Files checked:")
print("  1. safety/grounding_validator.py")
print("  2. safety/safety_critic.py")
print("  3. agents/signal_normalizer.py")
print("  4. agents/explanation_agent.py")
print()
print("fraud_analyzer.py was NOT modified.")
print()
print("Next command:")
print('python -m unittest discover -s tests -p "test_*.py" -v')
print()