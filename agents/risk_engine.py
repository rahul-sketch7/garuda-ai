# ============================================================
# FraudShield Risk Engine
# ============================================================

SIGNAL_SCORES = {

    "impersonation": 20,
    "urgency": 15,
    "threat": 20,

    "otp_request": 40,
    "credential_request": 35,
    "password_request": 40,
    "pin_request": 40,
    "personal_information_request": 25,

    "payment_request": 30,
    "upi_request": 30,
    "qr_payment": 30,

    "suspicious_link": 25,
    "remote_access_request": 40,

    "job_offer": 10,
    "investment_offer": 15,
    "unrealistic_return": 30,

    "kyc_request": 20,
    "account_verification": 15,

    "prize_claim": 15,

    "legal_threat": 20,
    "emotional_pressure": 15,
}


FRAUD_TYPE_BASE_SCORES = {

    "BANK_IMPERSONATION": 20,
    "OTP_SCAM": 35,
    "UPI_FRAUD": 30,
    "KYC_SCAM": 25,
    "JOB_SCAM": 25,
    "INVESTMENT_SCAM": 30,
    "COURIER_SCAM": 25,
    "DIGITAL_ARREST": 40,
    "GOVERNMENT_IMPERSONATION": 25,
    "FAKE_CUSTOMER_SUPPORT": 25,
    "ROMANCE_SCAM": 25,
    "LOTTERY_SCAM": 25,
    "PHISHING": 25,
    "MALWARE": 35,
    "SIM_SWAP": 40,
    "LOAN_SCAM": 25,
    "CHARITY_SCAM": 20,
    "OTHER": 10,
    "NOT_FRAUD": 0,
}


def calculate_risk(
    signals: list[str],
    fraud_type: str = "OTHER"
) -> int:

    # --------------------------------------------------------
    # 1. Start with the base severity of the fraud category
    # --------------------------------------------------------

    score = FRAUD_TYPE_BASE_SCORES.get(
        fraud_type,
        FRAUD_TYPE_BASE_SCORES["OTHER"]
    )

    # --------------------------------------------------------
    # 2. Add evidence from detected signals
    # --------------------------------------------------------

    for signal in signals:

        score += SIGNAL_SCORES.get(signal, 0)

    # --------------------------------------------------------
    # 3. Special combinations
    # --------------------------------------------------------

    signal_set = set(signals)

    # Sensitive information + impersonation
    if (
        "impersonation" in signal_set
        and "otp_request" in signal_set
    ):
        score += 20

    # Payment + suspicious link
    if (
        "payment_request" in signal_set
        and "suspicious_link" in signal_set
    ):
        score += 15

    # UPI + QR payment
    if (
        "upi_request" in signal_set
        and "qr_payment" in signal_set
    ):
        score += 15

    # Job + payment
    if (
        "job_offer" in signal_set
        and "payment_request" in signal_set
    ):
        score += 15

    # Investment + unrealistic return
    if (
        "investment_offer" in signal_set
        and "unrealistic_return" in signal_set
    ):
        score += 20

    # KYC + link
    if (
        "kyc_request" in signal_set
        and "suspicious_link" in signal_set
    ):
        score += 20

    # Urgency + threat
    if (
        "urgency" in signal_set
        and "threat" in signal_set
    ):
        score += 15

    # Digital arrest style combination
    if (
        "legal_threat" in signal_set
        and "impersonation" in signal_set
    ):
        score += 20

    # --------------------------------------------------------
    # 4. NOT_FRAUD must not receive fraud risk
    # --------------------------------------------------------

    if fraud_type == "NOT_FRAUD":
        return 0

    # --------------------------------------------------------
    # 5. Keep score within 0-100
    # --------------------------------------------------------

    return min(score, 100)


def get_risk_level(score: int) -> str:

    if score <= 20:
        return "LOW"

    if score <= 50:
        return "SUSPICIOUS"

    if score <= 75:
        return "HIGH"

    return "CRITICAL"


def analyze_risk(
    signals: list[str],
    fraud_type: str = "OTHER"
) -> dict:

    score = calculate_risk(
        signals,
        fraud_type
    )

    return {
        "risk_score": score,
        "risk_level": get_risk_level(score)
    }