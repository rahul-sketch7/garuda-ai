import re


# ============================================================
# SIGNAL PATTERNS
# ============================================================

SIGNAL_PATTERNS = {

    # -------------------------
    # IMPERSONATION
    # -------------------------

    "bank_impersonation": [
        "sbi",
        "hdfc",
        "icici",
        "axis bank",
        "bank employee",
        "bank officer",
        "bank official",
        "bank representative",
    ],

    "government_impersonation": [
        "government",
        "income tax",
        "aadhaar",
        "uidai",
        "government officer",
    ],

    "police_impersonation": [
        "police",
        "cyber crime",
        "cybercrime",
        "police officer",
    ],

    "customer_support_impersonation": [
        "customer support",
        "customer care",
        "support team",
        "technical support",
    ],

    # -------------------------
    # PRESSURE / MANIPULATION
    # -------------------------

    "urgency": [
        "immediately",
        "urgent",
        "right now",
        "act now",
        "today",
        "within 24 hours",
        "immediate",
    ],

    "threat": [
        "arrest",
        "police case",
        "legal action",
        "case will be filed",
        "account will be blocked",
        "account blocked",
        "account suspended",
        "you will be arrested",
    ],

    "emotional_pressure": [
        "help me urgently",
        "emergency",
        "please help",
        "i am stuck",
        "don't tell anyone",
    ],

    # -------------------------
    # SENSITIVE INFORMATION
    # -------------------------

    "otp_request": [
        "otp",
        "one time password",
        "one-time password",
    ],

    "password_request": [
        "password",
        "login password",
        "account password",
    ],

    "pin_request": [
        "pin",
        "upi pin",
        "atm pin",
        "card pin",
    ],

    "card_details_request": [
        "card number",
        "cvv",
        "expiry date",
        "debit card",
        "credit card",
    ],

    "personal_information_request": [
        "aadhaar number",
        "pan number",
        "date of birth",
        "personal details",
        "bank details",
    ],

    # -------------------------
    # MONEY / PAYMENT
    # -------------------------

    "payment_request": [
        "send money",
        "transfer money",
        "pay now",
        "make a payment",
        "payment",
        "registration fee",
        "processing fee",
    ],

    "upi_request": [
        "upi",
        "upi id",
        "upi payment",
        "upi transfer",
    ],

    "qr_payment": [
        "scan this qr",
        "scan qr",
        "qr code",
    ],

    # -------------------------
    # DIGITAL ATTACK
    # -------------------------

    "suspicious_link": [
        "http://",
        "https://",
        "www.",
        "click this link",
        "click the link",
        "click here",
        "this link",
        "verify here",
        "verify using this link",
    ],

    "remote_access_request": [
        "anydesk",
        "teamviewer",
        "remote access",
        "screen sharing",
        "share your screen",
    ],

    "credential_harvesting": [
        "verify your login",
        "verify your account",
        "login here",
        "enter your password",
        "enter your credentials",
    ],

    # -------------------------
    # FRAUD PROMISES
    # -------------------------

    "unrealistic_return": [
        "guaranteed returns",
        "guaranteed profit",
        "double your money",
        "100% profit",
        "40% returns",
        "huge returns",
    ],

    "prize_claim": [
        "you won",
        "you have won",
        "lottery",
        "prize",
        "winner",
        "claim your reward",
        "claim your prize",
    ],

    "job_offer": [
        "work from home",
        "job offer",
        "you have been selected",
        "earn money",
        "part time job",
    ],

    # -------------------------
    # VERIFICATION / KYC
    # -------------------------

    "kyc_request": [
        "kyc",
        "complete kyc",
        "update kyc",
        "kyc verification",
    ],

    "account_verification": [
        "verify your account",
        "account verification",
        "verify immediately",
    ],
}


# ============================================================
# MESSAGE EXTRACTION
# ============================================================

def _extract_message(value) -> str:
    """
    Extract the actual message from different input formats.

    Supported:
        String
        Dictionary containing message/text/content
        Dictionary containing slm_result
        Dictionary containing result
    """

    # Normal string
    if isinstance(value, str):
        return value

    # Dictionary input
    if isinstance(value, dict):

        # Direct message fields
        for key in ("message", "text", "content"):
            candidate = value.get(key)

            if isinstance(candidate, str):
                return candidate

        # Nested SLM result
        if isinstance(value.get("slm_result"), dict):
            return _extract_message(value["slm_result"])

        # Nested result
        if isinstance(value.get("result"), dict):
            return _extract_message(value["result"])

        return ""

    # Anything else
    return ""


# ============================================================
# SIGNAL NORMALIZER
# ============================================================

def normalize_signals(message) -> list[str]:
    """
    Detect security/fraud signals from a message.

    Returns:
        list[str]

    Example:
        [
            "bank_impersonation",
            "urgency",
            "threat",
            "otp_request"
        ]
    """

    message = _extract_message(message)

    if not message:
        return []

    message_lower = message.lower()

    detected_signals = []

    for signal, patterns in SIGNAL_PATTERNS.items():

        for pattern in patterns:

            # Whole-word style matching.
            #
            # This prevents accidental partial matches.
            #
            # Example:
            # "today" should match
            # "today!"
            #
            # but random substrings should not.
            if re.search(
                rf"(?<!\w){re.escape(pattern)}(?!\w)",
                message_lower
            ):
                detected_signals.append(signal)
                break

    return detected_signals


# ============================================================
# STRUCTURED RESULT NORMALIZER
# ============================================================

def normalize_result(slm_result):
    """
    Normalize a complete SLM result.

    The test suite expects normalize_result() to return
    a dictionary, not only a list of signals.

    Example input:

        {
            "language": "English",
            "fraud_type": "BANK_IMPERSONATION",
            "signals": [
                "impersonation",
                "otp_request"
            ],
            "attacker_goal": "Obtain OTP",
            "confidence": 0.95
        }

    Example output:

        {
            "language": "English",
            "fraud_type": "BANK_IMPERSONATION",
            "signals": [...],
            "attacker_goal": "Obtain OTP",
            "confidence": 0.95
        }
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not isinstance(slm_result, dict):
        return {
            "language": "Unknown",
            "fraud_type": "OTHER",
            "signals": [],
            "attacker_goal": "N/A",
            "confidence": 0.0,
        }

    # Make a copy so the original SLM result is not modified.
    result = dict(slm_result)

    # --------------------------------------------------------
    # Extract message if available
    # --------------------------------------------------------

    message = _extract_message(result)

    # --------------------------------------------------------
    # Normalize signals
    # --------------------------------------------------------

    if message:

        # Detect signals directly from the original message.
        result["signals"] = normalize_signals(message)

    else:

        # If the SLM result doesn't contain the original message,
        # preserve the signals already supplied by the model.
        existing_signals = result.get("signals", [])

        if not isinstance(existing_signals, list):
            existing_signals = []

        result["signals"] = existing_signals

    # --------------------------------------------------------
    # Guarantee required fields
    # --------------------------------------------------------

    result.setdefault(
        "language",
        "Unknown"
    )

    result.setdefault(
        "fraud_type",
        "OTHER"
    )

    result.setdefault(
        "attacker_goal",
        "N/A"
    )

    result.setdefault(
        "confidence",
        0.0
    )

    # --------------------------------------------------------
    # Normalize confidence
    # --------------------------------------------------------

    try:
        result["confidence"] = float(result["confidence"])
    except (TypeError, ValueError):
        result["confidence"] = 0.0

    result["confidence"] = max(
        0.0,
        min(1.0, result["confidence"])
    )

    # --------------------------------------------------------
    # Normalize language
    # --------------------------------------------------------

    if not isinstance(result["language"], str):
        result["language"] = "Unknown"

    # --------------------------------------------------------
    # Normalize fraud type
    # --------------------------------------------------------

    if not isinstance(result["fraud_type"], str):
        result["fraud_type"] = "OTHER"

    # --------------------------------------------------------
    # Normalize attacker goal
    # --------------------------------------------------------

    if not isinstance(result["attacker_goal"], str):
        result["attacker_goal"] = "N/A"

    return result


# ============================================================
# OPTIONAL ALIAS
# ============================================================

# Some older code may import this name.
# It should NOT be:
#
#     normalize_result = normalize_signals
#
# because normalize_result must return a dictionary.

__all__ = [
    "SIGNAL_PATTERNS",
    "normalize_signals",
    "normalize_result",
]


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    test_message = (
        "I'm calling from SBI. "
        "Your account will be blocked today. "
        "Tell me the OTP."
    )

    print("=" * 60)
    print("SIGNAL NORMALIZER TEST")
    print("=" * 60)

    print("\nOriginal Message:")
    print(test_message)

    print("\nnormalize_signals():")
    print(normalize_signals(test_message))

    print("\nnormalize_result():")

    sample_slm_result = {
        "language": "English",
        "fraud_type": "BANK_IMPERSONATION",
        "message": test_message,
        "signals": [],
        "attacker_goal": "Obtain OTP",
        "confidence": 0.95,
    }

    result = normalize_result(sample_slm_result)

    print(result)

    print("\nLanguage:")
    print(result["language"])

    print("\nFraud Type:")
    print(result["fraud_type"])

    print("\nSignals:")
    print(result["signals"])

    print("\nAttacker Goal:")
    print(result["attacker_goal"])

    print("\nConfidence:")
    print(result["confidence"])

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)