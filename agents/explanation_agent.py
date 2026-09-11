from typing import Any, Dict, List, Optional


# ============================================================
# GARUDA AI — EXPLANATION AGENT
# ============================================================

SIGNAL_EXPLANATIONS = {
    "impersonation":
        "The sender appears to be impersonating a trusted organization or person.",

    "urgency":
        "The message creates urgency and pressures the recipient to act quickly.",

    "threat":
        "The message uses threats or intimidation to pressure the recipient.",

    "otp_request":
        "The message asks for an OTP or authentication code.",

    "credential_request":
        "The message requests sensitive account credentials.",

    "password_request":
        "The message asks for a password or authentication secret.",

    "pin_request":
        "The message asks for a PIN or security code.",

    "personal_information_request":
        "The message requests personal or sensitive information.",

    "payment_request":
        "The message asks the recipient to make a payment.",

    "upi_request":
        "The message involves a UPI payment or UPI-related action.",

    "qr_payment":
        "The message asks the recipient to scan or use a QR code for payment.",

    "suspicious_link":
        "The message contains or refers to a potentially suspicious link.",

    "remote_access_request":
        "The message requests remote access, screen sharing, or device control.",

    "job_offer":
        "The message presents a job or work opportunity that may be fraudulent.",

    "investment_offer":
        "The message promotes an investment opportunity that may be fraudulent.",

    "unrealistic_return":
        "The message promises unusually high or unrealistic financial returns.",

    "kyc_request":
        "The message requests KYC or identity verification.",

    "account_verification":
        "The message requests account verification.",

    "prize_claim":
        "The message claims that the recipient has won a prize, reward, or lottery.",

    "legal_threat":
        "The message uses legal or law-enforcement consequences to pressure the recipient.",

    "emotional_pressure":
        "The message uses emotional pressure to influence the recipient's decision.",
}


FRAUD_TYPE_DESCRIPTIONS = {
    "BANK_IMPERSONATION":
        "The sender appears to be pretending to represent a bank or banking institution.",

    "OTP_SCAM":
        "The message attempts to obtain an OTP, authentication code, or verification code.",

    "UPI_FRAUD":
        "The message attempts to trick the recipient into making a fraudulent UPI payment or transfer.",

    "KYC_SCAM":
        "The message uses KYC or identity verification as a pretext to obtain sensitive information or money.",

    "JOB_SCAM":
        "The message uses a fake job or employment opportunity to obtain money or sensitive information.",

    "INVESTMENT_SCAM":
        "The message promotes a fraudulent investment opportunity, often using unrealistic or guaranteed returns.",

    "COURIER_SCAM":
        "The message uses a fake parcel, courier, customs, or delivery problem to obtain money or sensitive information.",

    "DIGITAL_ARREST":
        "The message impersonates law enforcement and uses arrest or legal threats to pressure the recipient.",

    "GOVERNMENT_IMPERSONATION":
        "The sender appears to be impersonating a government department or official.",

    "FAKE_CUSTOMER_SUPPORT":
        "The sender appears to be impersonating customer or technical support to obtain access, credentials, or money.",

    "ROMANCE_SCAM":
        "The message uses a deceptive romantic or emotional relationship to obtain money or sensitive information.",

    "LOTTERY_SCAM":
        "The message falsely claims that the recipient has won a lottery, prize, or reward.",

    "PHISHING":
        "The message attempts to trick the recipient into opening a suspicious link or providing sensitive information.",

    "MALWARE":
        "The message attempts to make the recipient install or download potentially malicious software.",

    "SIM_SWAP":
        "The message involves a fraudulent SIM replacement, porting, or account takeover attempt.",

    "LOAN_SCAM":
        "The message uses a fraudulent loan offer or processing requirement to obtain money or sensitive information.",

    "CHARITY_SCAM":
        "The message uses a fake donation, fundraiser, or charitable cause to obtain money.",

    "OTHER":
        "The message contains suspicious or unclear behavior that cannot be confidently assigned to a specific fraud category.",

    "NOT_FRAUD":
        "The message does not contain meaningful evidence of fraudulent behavior.",
}


DEFAULT_SAFE_ACTION = (
    "Do not share OTPs, passwords, PINs, or other sensitive information. "
    "Verify the request using an official channel."
)


# ============================================================
# HELPERS
# ============================================================

def _safe_list(value: Any) -> List[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def _extract_rag_results(rag_results: Any) -> List[Dict[str, Any]]:
    """
    Accept both:
        {"results": [...]}

    and:
        [...]
    """

    if rag_results is None:
        return []

    if isinstance(rag_results, list):
        return [
            item for item in rag_results
            if isinstance(item, dict)
        ]

    if isinstance(rag_results, dict):

        results = rag_results.get("results", [])

        if isinstance(results, list):
            return [
                item for item in results
                if isinstance(item, dict)
            ]

    return []


def _normalize_rag_evidence(
    rag_results: Any
) -> List[Dict[str, Any]]:

    normalized = []

    for result in _extract_rag_results(rag_results):

        normalized.append({
            "title": result.get(
                "title",
                "Trusted fraud intelligence"
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
            ),
        })

    return normalized


def _build_summary(
    fraud_type: str,
    risk_level: str
) -> str:

    if fraud_type == "NOT_FRAUD":
        return (
            "This message does not contain meaningful indicators "
            "of fraudulent behavior."
        )

    if fraud_type == "OTHER":
        return (
            "The message contains suspicious or unclear behavior, "
            "but the fraud type could not be determined confidently."
        )

    if risk_level == "CRITICAL":
        return (
            "This message contains multiple strong indicators "
            "of a potentially dangerous scam."
        )

    if risk_level == "HIGH":
        return (
            "This message contains several indicators associated "
            "with potentially fraudulent activity."
        )

    if risk_level == "SUSPICIOUS":
        return (
            "This message contains suspicious characteristics "
            "that should be verified before taking action."
        )

    return (
        "The message has been analyzed for potential fraud indicators."
    )


def _build_evidence(
    signals: List[Any],
    fraud_type: str
) -> List[str]:

    evidence = []

    for signal in signals:

        signal = str(signal)

        explanation = SIGNAL_EXPLANATIONS.get(
            signal,
            f"The message contains the signal: "
            f"{signal.replace('_', ' ')}."
        )

        if explanation not in evidence:
            evidence.append(explanation)

    # If there are no individual signals, use the fraud type
    # description when appropriate.

    if (
        not evidence
        and fraud_type not in {
            "NOT_FRAUD",
            "OTHER"
        }
    ):

        description = FRAUD_TYPE_DESCRIPTIONS.get(
            fraud_type
        )

        if description:
            evidence.append(description)

    return evidence


def _build_attacker_goal(
    fraud_type: str,
    attacker_goal: Optional[str]
) -> str:

    if (
        isinstance(attacker_goal, str)
        and attacker_goal.strip()
        and attacker_goal.strip().lower() != "n/a"
    ):
        return attacker_goal.strip()

    if fraud_type == "NOT_FRAUD":
        return "N/A"

    if fraud_type == "OTHER":
        return "N/A"

    default_goals = {

        "BANK_IMPERSONATION":
            "Obtain sensitive banking information or authentication codes.",

        "OTP_SCAM":
            "Obtain the victim's OTP or authentication code.",

        "UPI_FRAUD":
            "Obtain money through a fraudulent UPI payment or transfer.",

        "KYC_SCAM":
            "Obtain sensitive identity or banking information.",

        "JOB_SCAM":
            "Obtain money or personal information through a fake job offer.",

        "INVESTMENT_SCAM":
            "Obtain money through a fraudulent investment opportunity.",

        "COURIER_SCAM":
            "Obtain money by creating a fake courier or customs problem.",

        "DIGITAL_ARREST":
            "Obtain money or sensitive information using threats of arrest.",

        "GOVERNMENT_IMPERSONATION":
            "Obtain money or sensitive information by impersonating a government authority.",

        "FAKE_CUSTOMER_SUPPORT":
            "Obtain credentials, payment information, or device access.",

        "ROMANCE_SCAM":
            "Obtain money or sensitive information through emotional manipulation.",

        "LOTTERY_SCAM":
            "Obtain money or personal information by falsely claiming a prize.",

        "PHISHING":
            "Steal credentials or sensitive information through a deceptive link.",

        "MALWARE":
            "Install malicious software or gain access to information on the device.",

        "SIM_SWAP":
            "Take control of the victim's mobile number or related accounts.",

        "LOAN_SCAM":
            "Obtain money or sensitive information through a fraudulent loan offer.",

        "CHARITY_SCAM":
            "Obtain money through a fraudulent donation or fundraising request.",
    }

    return default_goals.get(
        fraud_type,
        "Obtain money, credentials, sensitive information, or account access."
    )


# ============================================================
# MAIN FUNCTION
# ============================================================

def generate_explanation(
    fraud_type: str = "OTHER",
    risk_score: int = 0,
    risk_level: str = "LOW",
    confidence: float = 0.0,
    signals: Optional[List[str]] = None,
    rag_results: Any = None,
    attacker_goal: Optional[str] = None,
    investigation: Any = None,
    analysis: Optional[Dict[str, Any]] = None,
    risk: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate the final Garuda AI explanation.

    Supports both calling styles.

    Style 1 — keyword/test style:

        generate_explanation(
            fraud_type="BANK_IMPERSONATION",
            risk_score=100,
            risk_level="CRITICAL",
            confidence=0.95,
            signals=["impersonation", "otp_request"],
            rag_results={}
        )

    Style 2 — structured pipeline style:

        generate_explanation(
            analysis=analysis,
            risk=risk,
            rag_results=rag_results,
            investigation=investigation
        )

    This compatibility is intentional so existing tests and
    the current Garuda AI orchestration pipeline both work.
    """

    # ========================================================
    # SUPPORT STRUCTURED ANALYSIS CALL
    # ========================================================

    if isinstance(analysis, dict):

        fraud_type = analysis.get(
            "fraud_type",
            fraud_type
        )

        signals = analysis.get(
            "signals",
            signals
        )

        confidence = analysis.get(
            "confidence",
            confidence
        )

        attacker_goal = analysis.get(
            "attacker_goal",
            attacker_goal
        )

    # ========================================================
    # SUPPORT STRUCTURED RISK CALL
    # ========================================================

    if isinstance(risk, dict):

        risk_score = risk.get(
            "risk_score",
            risk_score
        )

        risk_level = risk.get(
            "risk_level",
            risk_level
        )

    # ========================================================
    # NORMALIZE VALUES
    # ========================================================

    if signals is None:
        signals = []

    if not isinstance(signals, list):
        signals = [signals]

    try:
        confidence = float(confidence)
    except (
        TypeError,
        ValueError
    ):
        confidence = 0.0

    confidence = max(
        0.0,
        min(
            confidence,
            1.0
        )
    )

    try:
        risk_score = int(risk_score)
    except (
        TypeError,
        ValueError
    ):
        risk_score = 0

    risk_score = max(
        0,
        min(
            risk_score,
            100
        )
    )

    fraud_type = str(
        fraud_type or "OTHER"
    )

    risk_level = str(
        risk_level or "LOW"
    )

    # ========================================================
    # BUILD EXPLANATION
    # ========================================================

    summary = _build_summary(
        fraud_type,
        risk_level
    )

    evidence = _build_evidence(
        signals,
        fraud_type
    )

    rag_evidence = _normalize_rag_evidence(
        rag_results
    )

    final_attacker_goal = _build_attacker_goal(
        fraud_type,
        attacker_goal
    )

    # ========================================================
    # SAFE RECOMMENDATION
    # ========================================================

    if fraud_type == "NOT_FRAUD":

        recommended_action = (
            "No immediate fraud action is indicated. "
            "Continue to use official applications and channels."
        )

    elif fraud_type == "OTHER":

        recommended_action = (
            "Do not take irreversible action. "
            "Verify the message through an official channel "
            "before responding or sharing information."
        )

    else:

        recommended_action = DEFAULT_SAFE_ACTION

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "fraud_type": fraud_type,

        "risk_score": risk_score,

        "risk_level": risk_level,

        "confidence": round(
            confidence,
            2
        ),

        "summary": summary,

        "evidence": evidence,

        "rag_evidence": rag_evidence,

        "attacker_goal": final_attacker_goal,

        "recommended_action": recommended_action,
    }


# ============================================================
# COMPATIBILITY ALIAS
# ============================================================

create_explanation = generate_explanation


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    result = generate_explanation(
        fraud_type="BANK_IMPERSONATION",
        risk_score=100,
        risk_level="CRITICAL",
        confidence=0.95,
        signals=[
            "impersonation",
            "otp_request",
            "threat"
        ],
        rag_results={
            "results": [
                {
                    "title":
                        "RBI warning on impersonation and OTP requests",

                    "fraud_type":
                        "BANK_IMPERSONATION",

                    "evidence":
                        "Fraudsters may impersonate banks or officials "
                        "and pressure users into sharing OTPs.",

                    "source":
                        "Reserve Bank of India",

                    "source_url":
                        "https://rbi.org.in/",
                    
                    "relevance_distance":
                        0.92,
                }
            ]
        },

        attacker_goal="Obtain OTP to access the account"
    )

    print()
    print("=" * 60)
    print("GARUDA AI EXPLANATION TEST")
    print("=" * 60)

    for key, value in result.items():

        print()
        print(f"{key}:")
        print(value)

    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)