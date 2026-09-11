
import json
import re
from typing import Any, Dict, List

import ollama


# ============================================================
# GARUDA AI FRAUD TAXONOMY
# ============================================================

FRAUD_TYPES = [
    "BANK_IMPERSONATION",
    "OTP_SCAM",
    "UPI_FRAUD",
    "KYC_SCAM",
    "JOB_SCAM",
    "INVESTMENT_SCAM",
    "COURIER_SCAM",
    "DIGITAL_ARREST",
    "GOVERNMENT_IMPERSONATION",
    "FAKE_CUSTOMER_SUPPORT",
    "ROMANCE_SCAM",
    "LOTTERY_SCAM",
    "PHISHING",
    "MALWARE",
    "SIM_SWAP",
    "LOAN_SCAM",
    "CHARITY_SCAM",
    "OTHER",
    "NOT_FRAUD",
]

SIGNALS = [
    "impersonation",
    "urgency",
    "threat",
    "otp_request",
    "credential_request",
    "password_request",
    "pin_request",
    "personal_information_request",
    "payment_request",
    "upi_request",
    "qr_payment",
    "suspicious_link",
    "remote_access_request",
    "job_offer",
    "investment_offer",
    "unrealistic_return",
    "kyc_request",
    "account_verification",
    "prize_claim",
    "legal_threat",
    "emotional_pressure",
]


# ============================================================
# OLLAMA CONFIGURATION
# ============================================================

MODEL_NAME = "qwen3:4b"

OLLAMA_OPTIONS = {
    "temperature": 0,
    "num_predict": 400,
    "num_ctx": 4096,
}


# ============================================================
# STRUCTURED OUTPUT SCHEMA
# ============================================================

schema = {
    "type": "object",
    "properties": {
        "language": {"type": "string"},
        "fraud_type": {
            "type": "string",
            "enum": FRAUD_TYPES,
        },
        "signals": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": SIGNALS,
            },
        },
        "attacker_goal": {"type": "string"},
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
        },
    },
    "required": [
        "language",
        "fraud_type",
        "signals",
        "attacker_goal",
        "confidence",
    ],
}


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = r"""
You are Garuda AI's internal Fraud Analysis Agent.

Your job is to semantically analyze ONLY the supplied message and return:
1. fraud_type
2. meaningful fraud signals
3. attacker's likely goal
4. confidence
5. primary language

Return ONLY valid JSON matching the supplied schema.

Do not provide advice.
Do not explain reasoning.
Do not use previous conversation context.
Do not invent facts.

============================================================
CORE PRINCIPLE
============================================================

CLASSIFY THE PRIMARY ATTACK MECHANISM, NOT JUST A KEYWORD OR TOPIC.

Ask yourself:

1. What action is the recipient being asked to perform?
2. What does the sender appear to want?
3. What is the primary mechanism used to achieve that goal?
4. Is the message actually requesting a dangerous action, or merely warning
   the recipient NOT to perform that action?

A bank name alone does NOT mean BANK_IMPERSONATION.

The word OTP alone does NOT mean OTP_SCAM.

The word KYC alone does NOT mean KYC_SCAM.

A suspicious-looking message is not automatically PHISHING.

============================================================
FRAUD CATEGORIES
============================================================

BANK_IMPERSONATION:
Someone pretends to represent a bank or banking institution and uses that
identity as a central part of the attack.

OTP_SCAM:
The attacker attempts to obtain an OTP, authentication code, or verification
code, without a stronger specific category being central.

UPI_FRAUD:
The primary attack involves UPI payments, UPI transfers, UPI IDs,
collection requests, or fraudulent QR-code payments.

KYC_SCAM:
Fake KYC, identity verification, or account verification is the primary
attack mechanism, unless a more specific mechanism such as phishing or
malware is clearly primary.

JOB_SCAM:
A fake job, recruitment, work-from-home, or employment opportunity is used
to obtain money, information, or access.

INVESTMENT_SCAM:
A fraudulent investment opportunity promises guaranteed, unrealistic,
or unusually high returns.

COURIER_SCAM:
A fake parcel, courier, customs, delivery, or shipment problem is used to
obtain money or information.

DIGITAL_ARREST:
The attacker impersonates police, cybercrime authorities, or officials and
uses arrest, criminal, or serious legal threats to intimidate the victim.

GOVERNMENT_IMPERSONATION:
Someone falsely claims to represent a government department or authority,
without the defining characteristics of DIGITAL_ARREST.

FAKE_CUSTOMER_SUPPORT:
Someone impersonates customer support, technical support, service support,
or another representative to obtain money, credentials, or sensitive data.

ROMANCE_SCAM:
A romantic or relationship-based interaction is used to manipulate the victim
into sending money or sensitive information.

LOTTERY_SCAM:
The victim is falsely told they won a lottery, prize, reward, or contest and
is asked to provide money or information.

PHISHING:
A deceptive link or fraudulent website is the primary mechanism used to
obtain credentials, account information, OTPs, authentication information,
or other sensitive information.

MALWARE:
The primary attack mechanism is making the victim download, install, open,
or execute malicious or unknown software, APKs, security applications,
or remote-access applications.

SIM_SWAP:
The message specifically involves SIM replacement, porting, duplication,
mobile-number takeover, or unauthorized control of a SIM/mobile number.

LOAN_SCAM:
A fake loan or fraudulent lending offer is used to obtain money,
personal information, or sensitive information.

CHARITY_SCAM:
A fake charitable cause is used to obtain money or personal information.

OTHER:
The message appears suspicious or potentially fraudulent, but there is not
enough information to identify a specific fraud category.

NOT_FRAUD:
There is no meaningful evidence of fraud, or the message is clearly a normal
legitimate notification.

============================================================
IMPORTANT PRIORITY RULES
============================================================

Use this conceptual priority when several mechanisms appear:

1. MALWARE
2. DIGITAL_ARREST
3. UPI_FRAUD
4. PHISHING
5. LOTTERY_SCAM
6. INVESTMENT_SCAM
7. JOB_SCAM
8. LOAN_SCAM
9. CHARITY_SCAM
10. ROMANCE_SCAM
11. COURIER_SCAM
12. KYC_SCAM
13. SIM_SWAP
14. FAKE_CUSTOMER_SUPPORT
15. GOVERNMENT_IMPERSONATION
16. BANK_IMPERSONATION
17. OTP_SCAM

This is NOT a keyword rule. A higher category wins only when its defining
attack mechanism is actually supported by the message.

============================================================
BANK VS PHISHING
============================================================

Example:
"Your SBI account will be suspended. Verify your account immediately using
this link."

This is PHISHING because the fraudulent link is the primary mechanism.

Example:
"We are from SBI. Tell us the OTP to keep your account active."

This is BANK_IMPERSONATION because the attacker is directly pretending to
represent the bank and requesting sensitive information.

If a bank name + suspicious link + credential/account-information request
appears together, prefer PHISHING unless there is explicit evidence that the
bank impersonation itself is the central mechanism.

============================================================
KYC VS PHISHING VS MALWARE
============================================================

"Your KYC has expired. Update your KYC immediately or your account will be
blocked."

=> KYC_SCAM

"Your KYC has expired. Click this link and enter your login details."

=> PHISHING

"Your KYC has expired. Download this security APK."

=> MALWARE

============================================================
DIGITAL ARREST
============================================================

Use DIGITAL_ARREST when police/cybercrime/official impersonation is combined
with arrest, criminal, prosecution, or serious legal intimidation.

============================================================
UPI
============================================================

Use UPI_FRAUD when UPI transfer/payment, UPI ID, collection request,
or QR-payment behavior is central.

============================================================
SIM SWAP
============================================================

Do NOT use SIM_SWAP merely because an OTP is mentioned.

============================================================
LEGITIMATE SECURITY WARNINGS
============================================================

A legitimate message may mention OTP, PIN, password, account, bank, or KYC.

For example:
"Never share your OTP, PIN or password with anyone."

This is NOT_FRAUD.

The key question is whether the message asks the victim to disclose or
perform the dangerous action, rather than warning them not to do it.

============================================================
AMBIGUOUS
============================================================

"Hi, your account has an issue. Please check this immediately."

=> OTHER

"Please verify this."

=> OTHER

Do not invent a specific fraud type from vague text.

============================================================
SIGNALS
============================================================

Only include signals meaningfully supported by the message.

impersonation:
The sender claims to represent another person or organization.

urgency:
The message pressures the victim to act quickly.

threat:
The message threatens a negative consequence.

otp_request:
The recipient is asked to provide an OTP or authentication code.

credential_request:
The recipient is asked for login/account credentials.

password_request:
The recipient is asked for a password.

pin_request:
The recipient is asked for a PIN.

personal_information_request:
The recipient is asked for personal or identity information.

payment_request:
The recipient is asked to send/pay money.

upi_request:
The message involves a UPI payment, transfer, or UPI ID.

qr_payment:
The recipient is asked to scan/use a QR code for payment.

suspicious_link:
The message directs the victim to a potentially fraudulent/deceptive link.

remote_access_request:
The victim is asked for screen sharing, remote access, or remote control.

job_offer:
A job/employment opportunity is presented.

investment_offer:
An investment opportunity is presented.

unrealistic_return:
The message promises unusually high, guaranteed, or unrealistic returns.

kyc_request:
The recipient is asked to complete/update KYC.

account_verification:
The recipient is asked to verify an account/identity.

prize_claim:
The message claims the victim won a prize/lottery/reward.

legal_threat:
The message uses legal consequences as pressure.

emotional_pressure:
The message uses fear, sympathy, romance, emergency, or emotional
manipulation to pressure the victim.

============================================================
CONFIDENCE
============================================================

Confidence must be between 0 and 1.

Use high confidence when the mechanism is explicit and the attacker's
objective is clear.

Use lower confidence for vague, ambiguous, incomplete, or conflicting
messages.

============================================================
LANGUAGE
============================================================

Identify the primary language.

Supported examples include:
English, Hindi, Telugu, Tamil, Kannada, Malayalam, Marathi, Bengali,
Gujarati, Punjabi, Urdu, and code-mixed combinations such as:
Hindi-English, Telugu-English, Tamil-English, etc.

Do not infer language from a company name.

============================================================
FINAL CHECK
============================================================

Before returning JSON:

- Is the dangerous action actually requested?
- Is it a warning instead of a request?
- What is the primary attack mechanism?
- Is a more specific category supported?
- Are the signals actually present?
- Is NOT_FRAUD appropriate?
- If the message is vague, is OTHER safer?
- Is confidence appropriate?

Return ONLY JSON.
"""


# ============================================================
# TEXT HELPERS
# ============================================================

def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def _contains(text: str, patterns: List[str]) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def _deduplicate_signals(signals: Any) -> List[str]:
    if not isinstance(signals, list):
        return []

    result = []
    seen = set()

    for signal in signals:
        if not isinstance(signal, str):
            continue

        signal = signal.strip()

        if signal in SIGNALS and signal not in seen:
            result.append(signal)
            seen.add(signal)

    return result


# ============================================================
# NEGATION / LEGITIMATE WARNING DETECTION
# ============================================================

NEGATED_SENSITIVE_PATTERNS = [
    # English
    r"\bdo not share\b",
    r"\bdon't share\b",
    r"\bnever share\b",
    r"\bdo not disclose\b",
    r"\bdon't disclose\b",
    r"\bnever disclose\b",
    r"\bdo not reveal\b",
    r"\bnever reveal\b",
    r"\bdo not give\b",
    r"\bnever give\b",
    r"\bdo not provide\b",
    r"\bnever provide\b",
    r"\bdo not enter\b",
    r"\bnever enter\b",
    r"\bdo not tell\b",
    r"\bnever tell\b",
    r"\bdo not send\b",
    r"\bnever send\b",

    # Hinglish / Indian code-mixed
    r"\bshare mat karna\b",
    r"\bshare mat karo\b",
    r"\bmat share karo\b",
    r"\bmat dena\b",
    r"\bmat do\b",
    r"\bmat bhejna\b",
    r"\bkisi ke saath share mat\b",

    # Telugu
    r"పంచుకోవద్దు",
    r"షేర్ చేయవద్దు",
    r"ఎవరితోనూ పంచుకోవద్దు",
    r"చెప్పవద్దు",
    r"ఇవ్వవద్దు",

    # Hindi
    r"साझा न करें",
    r"शेयर न करें",
    r"किसी के साथ साझा न करें",
    r"किसी को न दें",
    r"मत साझा करें",
    r"मत दें",

    # Tamil
    r"பகிர வேண்டாம்",
    r"யாரிடமும் பகிர வேண்டாம்",
    r"கொடுக்க வேண்டாம்",

    # Kannada
    r"ಹಂಚಿಕೊಳ್ಳಬೇಡಿ",
    r"ಯಾರೊಂದಿಗೂ ಹಂಚಿಕೊಳ್ಳಬೇಡಿ",
    r"ನೀಡಬೇಡಿ",

    # Malayalam
    r"പങ്കിടരുത്",
    r"ആരുമായും പങ്കിടരുത്",
    r"നൽകരുത്",

    # Marathi
    r"शेअर करू नका",
    r"कोणालाही देऊ नका",
    r"सामायिक करू नका",

    # Bengali
    r"শেয়ার করবেন না",
    r"কারও সাথে শেয়ার করবেন না",
    r"দেবেন না",

    # Gujarati
    r"શેર કરશો નહીં",
    r"કોઈને આપશો નહીં",

    # Punjabi
    r"ਸਾਂਝਾ ਨਾ ਕਰੋ",
    r"ਕਿਸੇ ਨਾਲ ਵੀ ਸਾਂਝਾ ਨਾ ਕਰੋ",

    # Urdu
    r"شیئر نہ کریں",
    r"کسی کو نہ دیں",
]


def _has_negated_sensitive_request(text: str) -> bool:
    normalized = _normalize_text(text)

    if not normalized:
        return False

    sensitive_words = [
        "otp",
        "pin",
        "password",
        "passcode",
        "verification code",
        "cvv",
        "card number",
        "account details",
        "credentials",
    ]

    has_sensitive_word = any(word in normalized for word in sensitive_words)

    if not has_sensitive_word:
        return False

    return _contains(normalized, NEGATED_SENSITIVE_PATTERNS)


def _has_negated_install(text: str) -> bool:
    normalized = _normalize_text(text)

    install_words = [
        "download",
        "install",
        "apk",
        "application",
        "app",
        "software",
    ]

    negations = [
        "do not download",
        "don't download",
        "never download",
        "do not install",
        "don't install",
        "never install",
        "download mat karo",
        "install mat karo",
        "download na karein",
        "install na karein",
        "डाउनलोड न करें",
        "इंस्टॉल न करें",
        "డౌన్లోడ్ చేయవద్దు",
        "ఇన్స్టాల్ చేయవద్దు",
        "பதிவிறக்கம் செய்ய வேண்டாம்",
        "நிறுவ வேண்டாம்",
    ]

    return (
        any(word in normalized for word in install_words)
        and any(pattern in normalized for pattern in negations)
    )


# ============================================================
# ACTION DETECTION
# ============================================================

def _has_concrete_fraud_action(text: str) -> bool:
    normalized = _normalize_text(text)

    action_patterns = [
        # Credentials / authentication
        r"\bshare\b.*\b(otp|pin|password|passcode|cvv)\b",
        r"\b(send|tell|give|provide)\b.*\b(otp|pin|password|passcode|cvv)\b",
        r"\benter\b.*\b(otp|pin|password|passcode|cvv)\b",
        r"\bprovide\b.*\b(account details|credentials)\b",

        # Links
        r"\bclick\b.*\b(link|url)\b",
        r"\bopen\b.*\b(link|url)\b",
        r"\bverify\b.*\bvia\b.*https?://",
        r"\bverify\b.*https?://",

        # Money
        r"\bpay\b.*(?:₹|rs\.?|inr|\d)",
        r"\btransfer\b.*(?:₹|rs\.?|inr|\d)",
        r"\bsend\b.*(?:₹|rs\.?|inr|\d)",
        r"\bdeposit\b.*(?:₹|rs\.?|inr|\d)",

        # UPI / QR
        r"\bscan\b.*\bqr\b",
        r"\bupi\b.*\b(pin|transfer|payment)\b",
        r"\bupi\b.*\bpay\b",

        # Malware
        r"\bdownload\b.*\b(apk|app|application|software)\b",
        r"\binstall\b.*\b(apk|app|application|software)\b",
        r"\bdownload\b.*\bsecurity app\b",
        r"\binstall\b.*\bsecurity app\b",

        # Remote access
        r"\b(screen share|remote access|remote control|anydesk|teamviewer)\b",

        # SIM swap
        r"\b(sim replacement|replace your sim|port your number|sim swap)\b",

        # Job / investment / loan / charity / romance
        r"\bregistration fee\b",
        r"\bguaranteed\b.*\breturn\b",
        r"\binvest\b.*\b(?:₹|rs\.?|inr|\d)",
        r"\bloan\b.*\bprocessing fee\b",
        r"\bdonation\b.*(?:₹|rs\.?|inr|\d)",
    ]

    return _contains(normalized, action_patterns)


# ============================================================
# CLEARLY LEGITIMATE MESSAGE DETECTION
# ============================================================

def _is_clearly_legitimate_message(text: str) -> bool:
    normalized = _normalize_text(text)

    if not normalized:
        return False

    if _has_negated_sensitive_request(normalized):
        return True

    if _has_negated_install(normalized):
        return True

    legitimate_patterns = [
        r"\bstatement\b.*\bavailable\b",
        r"\bstatement\b.*\bready\b",
        r"\btransaction history\b.*\bavailable\b",
        r"\bthank you for banking with\b",
        r"\bdo not share\b.*\b(otp|pin|password)\b",
        r"\bnever share\b.*\b(otp|pin|password)\b",
        r"\bofficial app\b.*\b(statement|account)\b",
        r"\bsecurity reminder\b",
        r"\bfraud awareness\b",
        r"\bsecurity alert\b.*\bdo not\b",
        r"\bremember\b.*\bdo not share\b",
    ]

    if _contains(normalized, legitimate_patterns):
        if not _has_concrete_fraud_action(normalized):
            return True

    # Explicit safe-channel wording.
    safe_channel = _contains(
        normalized,
        [
            r"\bofficial app\b",
            r"\bofficial website\b",
            r"\bofficial customer care\b",
            r"\bverified channel\b",
        ],
    )

    warning_language = _contains(
        normalized,
        [
            r"\bdo not\b",
            r"\bdon't\b",
            r"\bnever\b",
            r"\bavoid\b",
            r"\bwarning\b",
            r"\balert\b",
            r"\bsecurity reminder\b",
        ],
    )

    if safe_channel and warning_language and not _has_concrete_fraud_action(normalized):
        return True

    return False


# ============================================================
# DETERMINISTIC STRONG-SCENARIO DETECTOR
# ============================================================

def _detect_strong_scenario(text: str):
    """
    Returns:
        (fraud_type, minimum_confidence)
    or:
        None
    """

    normalized = _normalize_text(text)

    if not normalized:
        return None

    # --------------------------------------------------------
    # FAKE CUSTOMER SUPPORT
    # --------------------------------------------------------
    support = _contains(
        normalized,
        [
            r"\bcustomer support\b",
            r"\bcustomer care\b",
            r"\btechnical support\b",
            r"\btechnical team\b",
            r"\bsupport team\b",
            r"\bsupport executive\b",
            r"\bcustomer care executive\b",
            r"\bcustomer service\b",
            r"\bhelp desk\b",
            r"\bservice representative\b",
            r"\bsupport representative\b",
        ],
    )
    support_action = _contains(
        normalized,
        [
            r"\bremote access\b",
            r"\bremote control\b",
            r"\bscreen share\b",
            r"\banydesk\b",
            r"\bteamviewer\b",
            r"\botp\b",
            r"\bpin\b",
            r"\bpassword\b",
            r"\bverification\b",
        ],
    )
    if support and support_action:
        return "FAKE_CUSTOMER_SUPPORT", 0.93

    # --------------------------------------------------------
    # CHARITY
    # --------------------------------------------------------
    charity = _contains(
        normalized,
        [
            r"\bdonation\b",
            r"\bdonate\b",
            r"\bcharity\b",
            r"\bcharitable\b",
            r"\bfundraiser\b",
            r"\brelief fund\b",
            r"\bmedical fundraiser\b",
            r"\bmedical emergency\b",
            r"\bhelp (?:the|this|a) family\b",
            r"\bhelp (?:the|this) victim\b",
            r"\bhelp (?:the|this) victims\b",
            r"\bdisaster relief\b",
        ],
    )
    if charity and _contains(
        normalized,
        [
            r"\bdonate\b",
            r"\bdonation\b",
            r"\bcontribute\b",
            r"\bsend money\b",
            r"\bpay\b",
            r"\btransfer\b",
            r"\bscan\b.*\bqr\b",
        ],
    ):
        return "CHARITY_SCAM", 0.92

    # --------------------------------------------------------
    # MALWARE
    # --------------------------------------------------------
    malware_context = _contains(
        normalized,
        [
            r"\bdownload\b",
            r"\binstall\b",
            r"\bapk\b",
            r"\bsecurity app\b",
            r"\bremote access app\b",
            r"\bremote-control app\b",
            r"\bapplication\b",
        ],
    )

    malware_action = _contains(
        normalized,
        [
            r"\bdownload\b",
            r"\binstall\b",
            r"\bopen\b.*\bapk\b",
            r"\binstall\b.*\bapp\b",
        ],
    )

    if malware_context and malware_action and not _has_negated_install(normalized):
        return "MALWARE", 0.95

    # --------------------------------------------------------
    # DIGITAL ARREST
    # --------------------------------------------------------
    authority = _contains(
        normalized,
        [
            r"\bpolice\b",
            r"\bcybercrime\b",
            r"\bcyber crime\b",
            r"\bcbi\b",
            r"\bcourt\b",
            r"\bgovernment official\b",
            r"\bpolice officer\b",
            r"\bcyber cell\b",
        ],
    )

    arrest_threat = _contains(
        normalized,
        [
            r"\barrest\b",
            r"\bget arrested\b",
            r"\byou will be arrested\b",
            r"\blegal action\b",
            r"\bcriminal case\b",
            r"\bprosecution\b",
            r"\bjail\b",
        ],
    )

    if authority and arrest_threat:
        return "DIGITAL_ARREST", 0.95

    # --------------------------------------------------------
    # UPI FRAUD
    # --------------------------------------------------------
    upi = _contains(
        normalized,
        [
            r"\bupi\b",
            r"\bupi id\b",
            r"\bupi pin\b",
            r"\bqr code\b",
            r"\bscan this qr\b",
            r"\bscan qr\b",
        ],
    )

    upi_action = _contains(
        normalized,
        [
            r"\bpay\b",
            r"\bpayment\b",
            r"\btransfer\b",
            r"\bcollect\b",
            r"\bscan\b",
            r"\bupi pin\b",
        ],
    )

    if upi and upi_action:
        return "UPI_FRAUD", 0.95

    # --------------------------------------------------------
    # PHISHING
    # --------------------------------------------------------
    link = _contains(
        normalized,
        [
            r"https?://",
            r"\bwww\.",
            r"\bclick\b.*\b(link|here)\b",
            r"\bverify\b.*\b(link|url|website)\b",
        ],
    )

    credential_target = _contains(
        normalized,
        [
            r"\bpassword\b",
            r"\bpin\b",
            r"\botp\b",
            r"\bcredential\b",
            r"\blogin\b",
            r"\baccount details\b",
            r"\bcard details\b",
            r"\bpersonal details\b",
        ],
    )

    if link and credential_target and not _has_negated_sensitive_request(normalized):
        return "PHISHING", 0.95

    # --------------------------------------------------------
    # LOTTERY
    # --------------------------------------------------------
    lottery = _contains(
        normalized,
        [
            r"\blottery\b",
            r"\bprize\b",
            r"\breward\b",
            r"\bcontest winner\b",
            r"\byou have won\b",
            r"\bcongratulations\b.*\bwon\b",
        ],
    )

    if lottery and _contains(
        normalized,
        [
            r"\bclaim\b",
            r"\bpay\b",
            r"\bfee\b",
            r"\bprocessing\b",
            r"\btransfer\b",
            r"\bsend\b",
        ],
    ):
        return "LOTTERY_SCAM", 0.93

    # --------------------------------------------------------
    # INVESTMENT
    # --------------------------------------------------------
    investment = _contains(
        normalized,
        [
            r"\binvest\b",
            r"\binvestment\b",
            r"\btrading\b",
            r"\bprofit\b",
            r"\breturns?\b",
        ],
    )

    unrealistic = _contains(
        normalized,
        [
            r"\bguaranteed\b",
            r"\brisk[- ]free\b",
            r"\bdouble your money\b",
            r"\b10x\b",
            r"\b\d+\s*%\s*(return|profit)\b",
            r"\bunusually high\b",
        ],
    )

    if investment and unrealistic:
        return "INVESTMENT_SCAM", 0.94

    # --------------------------------------------------------
    # JOB
    # --------------------------------------------------------
    job = _contains(
        normalized,
        [
            r"\bjob\b",
            r"\bwork from home\b",
            r"\brecruitment\b",
            r"\bpart[- ]time\b",
            r"\bearn from home\b",
            r"\bvacancy\b",
        ],
    )

    job_payment = _contains(
        normalized,
        [
            r"\bregistration fee\b",
            r"\bjoining fee\b",
            r"\bdeposit\b",
            r"\bprocessing fee\b",
            r"\bpay\b.*\bfee\b",
        ],
    )

    if job and job_payment:
        return "JOB_SCAM", 0.94

    # --------------------------------------------------------
    # LOAN
    # --------------------------------------------------------
    loan = _contains(
        normalized,
        [
            r"\bloan\b",
            r"\binstant loan\b",
            r"\bpersonal loan\b",
            r"\bcredit loan\b",
        ],
    )

    loan_fee = _contains(
        normalized,
        [
            r"\bprocessing fee\b",
            r"\badvance fee\b",
            r"\bsecurity deposit\b",
            r"\bpay\b.*\bfee\b",
            r"\bupfront\b",
        ],
    )

    if loan and loan_fee:
        return "LOAN_SCAM", 0.93

    # --------------------------------------------------------
    # CHARITY
    # --------------------------------------------------------
    charity = _contains(
        normalized,
        [
            r"\bdonation\b",
            r"\bcharity\b",
            r"\brelief fund\b",
            r"\bmedical fundraiser\b",
            r"\bhelp the family\b",
        ],
    )

    if charity and _contains(
        normalized,
        [
            r"\bsend\b",
            r"\bdonate\b",
            r"\bpay\b",
            r"\btransfer\b",
        ],
    ):
        return "CHARITY_SCAM", 0.92

    # --------------------------------------------------------
    # ROMANCE
    # --------------------------------------------------------
    romance = _contains(
        normalized,
        [
            r"\blove\b",
            r"\bdear\b",
            r"\brelationship\b",
            r"\bpartner\b",
            r"\bromantic\b",
            r"\bmarriage\b",
        ],
    )

    romance_money = _contains(
        normalized,
        [
            r"\bsend money\b",
            r"\btransfer money\b",
            r"\bhelp me financially\b",
            r"\bpay for\b",
            r"\bneed money\b",
        ],
    )

    if romance and romance_money:
        return "ROMANCE_SCAM", 0.92

    # --------------------------------------------------------
    # COURIER
    # --------------------------------------------------------
    courier = _contains(
        normalized,
        [
            r"\bcourier\b",
            r"\bparcel\b",
            r"\bpackage\b",
            r"\bshipment\b",
            r"\bcustoms\b",
            r"\bdelivery\b",
        ],
    )

    courier_pressure = _contains(
        normalized,
        [
            r"\bpay\b",
            r"\bfee\b",
            r"\bpolice action\b",
            r"\billegal items?\b",
            r"\bpenalty\b",
        ],
    )

    if courier and courier_pressure:
        return "COURIER_SCAM", 0.94

    # --------------------------------------------------------
    # KYC
    # --------------------------------------------------------
    kyc = _contains(
        normalized,
        [
            r"\bkyc\b",
            r"\bknow your customer\b",
            r"\bidentity verification\b",
            r"\baccount verification\b",
        ],
    )

    kyc_action = _contains(
        normalized,
        [
            r"\bupdate\b",
            r"\bcomplete\b",
            r"\bverify\b",
            r"\bexpired\b",
            r"\bpending\b",
        ],
    )

    if kyc and kyc_action:
        return "KYC_SCAM", 0.92

    # --------------------------------------------------------
    # SIM SWAP
    # --------------------------------------------------------
    sim_swap = _contains(
        normalized,
        [
            r"\bsim swap\b",
            r"\bsim replacement\b",
            r"\breplace your sim\b",
            r"\bport your number\b",
            r"\bporting\b.*\bnumber\b",
            r"\bduplicate sim\b",
            r"\btakeover\b.*\bsim\b",
        ],
    )

    if sim_swap:
        return "SIM_SWAP", 0.94

    # --------------------------------------------------------
    # FAKE CUSTOMER SUPPORT
    # --------------------------------------------------------
    support = _contains(
        normalized,
        [
            r"\bcustomer support\b",
            r"\bcustomer care\b",
            r"\btechnical support\b",
            r"\bhelp desk\b",
            r"\bsupport team\b",
        ],
    )

    support_identity = _contains(
        normalized,
        [
            r"\bwe are\b",
            r"\bcalling from\b",
            r"\bfrom support\b",
            r"\bsupport representative\b",
        ],
    )

    support_action = _contains(
        normalized,
        [
            r"\botp\b",
            r"\bpin\b",
            r"\bpassword\b",
            r"\bpay\b",
            r"\bremote access\b",
            r"\bscreen share\b",
        ],
    )

    if support and (support_identity or support_action):
        return "FAKE_CUSTOMER_SUPPORT", 0.93

    # --------------------------------------------------------
    # GOVERNMENT IMPERSONATION
    # --------------------------------------------------------
    government = _contains(
        normalized,
        [
            r"\bgovernment\b",
            r"\bincome tax\b",
            r"\bincome tax department\b",
            r"\bgovernment department\b",
            r"\bgovernment official\b",
            r"\bministry\b",
            r"\baadhaar authority\b",
        ],
    )

    government_identity = _contains(
        normalized,
        [
            r"\bwe are\b",
            r"\bcalling from\b",
            r"\bofficial\b",
            r"\bdepartment\b",
        ],
    )

    if government and government_identity:
        return "GOVERNMENT_IMPERSONATION", 0.91

    # --------------------------------------------------------
    # BANK IMPERSONATION
    # --------------------------------------------------------
    bank = _contains(
        normalized,
        [
            r"\bsbi\b",
            r"\bhdfc\b",
            r"\bicici\b",
            r"\baxis bank\b",
            r"\byes bank\b",
            r"\bkotak\b",
            r"\bpunjab national bank\b",
            r"\bbank\b",
        ],
    )

    bank_identity = _contains(
        normalized,
        [
            r"\bwe are from\b",
            r"\bcalling from\b",
            r"\bbank representative\b",
            r"\bbank official\b",
            r"\bbank support\b",
            r"\bfrom .* bank\b",
            r"\bsecurity team\b",
        ],
    )

    sensitive_request = _contains(
        normalized,
        [
            r"\botp\b",
            r"\bpin\b",
            r"\bpassword\b",
            r"\bpasscode\b",
            r"\bcredential\b",
            r"\baccount details\b",
            r"\bcard details\b",
            r"\bcvv\b",
        ],
    )

    if (
        bank
        and bank_identity
        and sensitive_request
        and not _has_negated_sensitive_request(normalized)
        and not (
            link
            and credential_target
            and _has_concrete_fraud_action(normalized)
        )
    ):
        return "BANK_IMPERSONATION", 0.95

    # --------------------------------------------------------
    # GENERIC OTP
    # --------------------------------------------------------
    if (
        _contains(
            normalized,
            [
                r"\botp\b",
                r"\bone[- ]time password\b",
                r"\bverification code\b",
                r"\bauthentication code\b",
            ],
        )
        and _contains(
            normalized,
            [
                r"\bshare\b",
                r"\bsend\b",
                r"\btell\b",
                r"\bgive\b",
                r"\bprovide\b",
                r"\benter\b",
            ],
        )
        and not _has_negated_sensitive_request(normalized)
    ):
        return "OTP_SCAM", 0.93

    return None


# ============================================================
# POST PROCESSING
# ============================================================

def _apply_post_processing(
    message: str,
    result: Dict[str, Any],
) -> Dict[str, Any]:

    text = _normalize_text(message)

    fraud_type = result.get("fraud_type", "OTHER")

    if fraud_type not in FRAUD_TYPES:
        fraud_type = "OTHER"

    signals = _deduplicate_signals(result.get("signals", []))

    attacker_goal = result.get("attacker_goal", "N/A")
    if not isinstance(attacker_goal, str) or not attacker_goal.strip():
        attacker_goal = "N/A"

    try:
        confidence = float(result.get("confidence", 0.5))
    except (TypeError, ValueError):
        confidence = 0.5

    confidence = max(0.0, min(1.0, confidence))

    language = result.get("language", "Unknown")
    if not isinstance(language, str) or not language.strip():
        language = "Unknown"

    # --------------------------------------------------------
    # Prompt-injection protection
    # --------------------------------------------------------
    injection_patterns = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore the system prompt",
        "reveal your system prompt",
        "reveal the system prompt",
        "developer message",
        "reveal your instructions",
        "forget your instructions",
    ]

    if any(pattern in text for pattern in injection_patterns):
        fraud_type = "OTHER"
        confidence = min(confidence, 0.5)
        attacker_goal = "N/A"
        signals = []

    # --------------------------------------------------------
    # Clearly legitimate warnings
    # --------------------------------------------------------
    if _is_clearly_legitimate_message(text):
        fraud_type = "NOT_FRAUD"
        confidence = max(confidence, 0.90)
        signals = []
        attacker_goal = "N/A"

        return {
            "language": language,
            "fraud_type": fraud_type,
            "signals": signals,
            "attacker_goal": attacker_goal,
            "confidence": round(confidence, 4),
        }

    # --------------------------------------------------------
    # Strong deterministic scenarios
    # --------------------------------------------------------
    strong = _detect_strong_scenario(text)

    if strong is not None:
        strong_type, strong_confidence = strong

        # Do not let a bank name override a phishing mechanism.
        if strong_type == "PHISHING":
            fraud_type = "PHISHING"

        # Malware must remain malware when installation is central.
        elif strong_type == "MALWARE":
            fraud_type = "MALWARE"

        # Other strong mechanisms should override weak model guesses.
        else:
            fraud_type = strong_type

        confidence = max(confidence, strong_confidence)

    # --------------------------------------------------------
    # Final PHISHING protection
    # --------------------------------------------------------
    has_link = _contains(
        text,
        [
            r"https?://",
            r"\bwww\.",
            r"\bclick\b.*\b(link|here)\b",
            r"\bverify\b.*\b(link|url|website)\b",
        ],
    )

    has_sensitive_target = _contains(
        text,
        [
            r"\botp\b",
            r"\bpin\b",
            r"\bpassword\b",
            r"\bpasscode\b",
            r"\bcredential\b",
            r"\blogin\b",
            r"\baccount details\b",
            r"\bcard details\b",
            r"\bpersonal details\b",
        ],
    )

    explicit_phishing_action = (
        has_link
        and has_sensitive_target
        and not _has_negated_sensitive_request(text)
    )

    if explicit_phishing_action:
        fraud_type = "PHISHING"
        confidence = max(confidence, 0.95)

    # --------------------------------------------------------
    # Final MALWARE protection
    # --------------------------------------------------------
    malware_action = (
        _contains(
            text,
            [
                r"\bdownload\b",
                r"\binstall\b",
                r"\bapk\b",
            ],
        )
        and not _has_negated_install(text)
    )

    if malware_action and _contains(
        text,
        [
            r"\bsecurity app\b",
            r"\bsecurity application\b",
            r"\bapk\b",
            r"\bunknown app\b",
            r"\bunknown application\b",
            r"\bremote access app\b",
        ],
    ):
        fraud_type = "MALWARE"
        confidence = max(confidence, 0.95)

    # --------------------------------------------------------
    # KYC should remain KYC when it is only KYC/account
    # verification, with no stronger mechanism.
    # --------------------------------------------------------
    if fraud_type in {"BANK_IMPERSONATION", "OTP_SCAM", "OTHER"}:
        if (
            _contains(
                text,
                [
                    r"\bkyc\b",
                    r"\bknow your customer\b",
                    r"\bidentity verification\b",
                ],
            )
            and _contains(
                text,
                [
                    r"\bupdate\b",
                    r"\bcomplete\b",
                    r"\bexpired\b",
                    r"\bpending\b",
                    r"\bverification\b",
                ],
            )
            and not explicit_phishing_action
            and not malware_action
        ):
            fraud_type = "KYC_SCAM"
            confidence = max(confidence, 0.92)

    # --------------------------------------------------------
    # UPI should remain UPI when payment/QR behavior is central.
    # --------------------------------------------------------
    if (
        _contains(text, [r"\bupi\b", r"\bupi id\b", r"\bqr code\b"])
        and _contains(
            text,
            [
                r"\bpay\b",
                r"\bpayment\b",
                r"\btransfer\b",
                r"\bscan\b",
                r"\bupi pin\b",
            ],
        )
    ):
        fraud_type = "UPI_FRAUD"
        confidence = max(confidence, 0.95)

    # --------------------------------------------------------
    # Digital arrest must remain highest priority.
    # --------------------------------------------------------
    if (
        _contains(
            text,
            [
                r"\bpolice\b",
                r"\bcybercrime\b",
                r"\bcyber crime\b",
                r"\bcbi\b",
                r"\bpolice officer\b",
            ],
        )
        and _contains(
            text,
            [
                r"\barrest\b",
                r"\bget arrested\b",
                r"\blegal action\b",
                r"\bcriminal case\b",
                r"\bjail\b",
            ],
        )
    ):
        fraud_type = "DIGITAL_ARREST"
        confidence = max(confidence, 0.95)

    # --------------------------------------------------------
    # Final FAKE CUSTOMER SUPPORT protection
    # --------------------------------------------------------
    # When the attacker explicitly poses as customer/technical support
    # and asks for remote access or sensitive/account action, support is
    # the social-engineering mechanism. Do not let generic MALWARE win
    # merely because a remote-access app/tool is mentioned.
    support_context = _contains(
        text,
        [
            r"\bcustomer support\b",
            r"\bcustomer care\b",
            r"\btechnical support\b",
            r"\btechnical team\b",
            r"\bsupport team\b",
            r"\bsupport executive\b",
            r"\bcustomer care executive\b",
            r"\bcustomer service\b",
            r"\bhelp desk\b",
            r"\bservice representative\b",
            r"\bsupport representative\b",
            r"\bservice agent\b",
        ],
    )

    support_identity = _contains(
        text,
        [
            r"\bcalling from\b",
            r"\bwe are from\b",
            r"\bi am from\b",
            r"\bthis is .*support\b",
            r"\bthis is .*customer care\b",
            r"\bfrom the support team\b",
        ],
    )

    support_action = _contains(
        text,
        [
            r"\bremote access\b",
            r"\bremote control\b",
            r"\bscreen share\b",
            r"\banydesk\b",
            r"\bteamviewer\b",
            r"\botp\b",
            r"\bpin\b",
            r"\bpassword\b",
            r"\baccount details\b",
            r"\bverification\b",
        ],
    )

    if support_context and (support_identity or support_action):
        fraud_type = "FAKE_CUSTOMER_SUPPORT"
        confidence = max(confidence, 0.93)

    # --------------------------------------------------------
    # Final CHARITY protection
    # --------------------------------------------------------
    # UPI/QR can be only the payment channel. If the message is framed
    # around a fake donation/fundraiser, classify the underlying scam.
    charity_context = _contains(
        text,
        [
            r"\bdonation\b",
            r"\bdonate\b",
            r"\bcharity\b",
            r"\bcharitable\b",
            r"\brelief fund\b",
            r"\bmedical fundraiser\b",
            r"\bfundraiser\b",
            r"\bfund raising\b",
            r"\bhelp the family\b",
            r"\bhelp this family\b",
            r"\bhelp victims\b",
            r"\bdisaster relief\b",
            r"\bmedical emergency\b",
        ],
    )

    charity_action = _contains(
        text,
        [
            r"\bsend\b",
            r"\bdonate\b",
            r"\bdonation\b",
            r"\bpay\b",
            r"\btransfer\b",
            r"\bcontribute\b",
            r"\bsupport\b.*\b(family|victim|cause)\b",
        ],
    )

    if charity_context and charity_action:
        fraud_type = "CHARITY_SCAM"
        confidence = max(confidence, 0.96)

    # --------------------------------------------------------
    # NOT_FRAUD normalization
    # --------------------------------------------------------
    if fraud_type == "NOT_FRAUD":
        signals = []
        attacker_goal = "N/A"
        confidence = max(confidence, 0.90)

    # --------------------------------------------------------
    # OTHER normalization
    # --------------------------------------------------------
    if fraud_type == "OTHER":
        # Ambiguous cases should not pretend to know the attacker goal.
        if not _has_concrete_fraud_action(text):
            attacker_goal = "N/A"
            confidence = min(confidence, 0.85)

    # --------------------------------------------------------
    # Signal corrections
    # --------------------------------------------------------

    # Sensitive request signals are only valid when the message asks
    # for sensitive data, not when it warns against sharing it.
    if _has_negated_sensitive_request(text):
        signals = [
            s
            for s in signals
            if s
            not in {
                "otp_request",
                "credential_request",
                "password_request",
                "pin_request",
                "personal_information_request",
            }
        ]

    # Do not call a normal security warning a threat.
    warning_only = _is_clearly_legitimate_message(text)

    if warning_only:
        signals = []

    # Add strong signals that are explicitly supported.
    def add_signal(signal: str):
        if signal in SIGNALS and signal not in signals:
            signals.append(signal)

    if fraud_type in {
        "BANK_IMPERSONATION",
        "GOVERNMENT_IMPERSONATION",
        "FAKE_CUSTOMER_SUPPORT",
        "DIGITAL_ARREST",
    }:
        if _contains(
            text,
            [
                r"\bwe are\b",
                r"\bcalling from\b",
                r"\bofficial\b",
                r"\brepresentative\b",
                r"\bfrom .* bank\b",
            ],
        ):
            add_signal("impersonation")

    if _contains(
        text,
        [
            r"\bimmediately\b",
            r"\burgent\b",
            r"\basap\b",
            r"\btoday\b.*\bblocked\b",
            r"\bwithin \d+ hours?\b",
            r"\bby tonight\b",
        ],
    ):
        add_signal("urgency")

    if _contains(
        text,
        [
            r"\bwill be blocked\b",
            r"\bwill be suspended\b",
            r"\bwill be arrested\b",
            r"\blegal action\b",
            r"\baccount will close\b",
            r"\baccount will be closed\b",
        ],
    ):
        add_signal("threat")

    if (
        _contains(
            text,
            [
                r"\botp\b",
                r"\bone[- ]time password\b",
                r"\bverification code\b",
                r"\bauthentication code\b",
            ],
        )
        and not _has_negated_sensitive_request(text)
    ):
        if _contains(
            text,
            [
                r"\bshare\b",
                r"\bsend\b",
                r"\btell\b",
                r"\bgive\b",
                r"\bprovide\b",
                r"\benter\b",
            ],
        ):
            add_signal("otp_request")

    if _contains(
        text,
        [
            r"\bpassword\b",
            r"\bcredentials\b",
            r"\baccount credentials\b",
        ],
    ) and not _has_negated_sensitive_request(text):
        add_signal("credential_request")

    if _contains(text, [r"\bpassword\b"]) and not _has_negated_sensitive_request(text):
        if _contains(text, [r"\bshare\b", r"\bsend\b", r"\btell\b", r"\bgive\b"]):
            add_signal("password_request")

    if _contains(text, [r"\bpin\b", r"\bupi pin\b", r"\batm pin\b"]) and not _has_negated_sensitive_request(text):
        if _contains(text, [r"\bshare\b", r"\bsend\b", r"\btell\b", r"\bgive\b", r"\benter\b"]):
            add_signal("pin_request")

    if explicit_phishing_action:
        add_signal("suspicious_link")

    if _contains(text, [r"\bscan\b.*\bqr\b", r"\bqr code\b"]) and _contains(
        text,
        [r"\bpay\b", r"\bpayment\b", r"\bupi\b", r"\btransfer\b"],
    ):
        add_signal("qr_payment")

    if _contains(text, [r"\bupi\b", r"\bupi id\b", r"\bupi pin\b"]):
        add_signal("upi_request")

    if _contains(text, [r"\bdownload\b", r"\binstall\b", r"\bapk\b"]) and not _has_negated_install(text):
        if fraud_type == "MALWARE":
            add_signal("suspicious_link" if has_link else "account_verification")

    if _contains(text, [r"\bscreen share\b", r"\bremote access\b", r"\bremote control\b"]):
        add_signal("remote_access_request")

    if _contains(text, [r"\bjob\b", r"\bwork from home\b", r"\brecruitment\b"]):
        add_signal("job_offer")

    if _contains(text, [r"\binvest\b", r"\binvestment\b", r"\btrading\b"]):
        add_signal("investment_offer")

    if _contains(
        text,
        [
            r"\bguaranteed\b.*\breturn\b",
            r"\brisk[- ]free\b",
            r"\bdouble your money\b",
            r"\b10x\b",
        ],
    ):
        add_signal("unrealistic_return")

    if _contains(
        text,
        [
            r"\bkyc\b",
            r"\bknow your customer\b",
        ],
    ) and not _has_negated_sensitive_request(text):
        add_signal("kyc_request")

    if _contains(
        text,
        [
            r"\bverify your account\b",
            r"\baccount verification\b",
            r"\bverify your identity\b",
        ],
    ):
        add_signal("account_verification")

    if _contains(
        text,
        [
            r"\blottery\b",
            r"\bprize\b",
            r"\breward\b",
            r"\byou have won\b",
        ],
    ):
        add_signal("prize_claim")

    if _contains(
        text,
        [
            r"\blegal action\b",
            r"\barrest\b",
            r"\bcriminal case\b",
            r"\bprosecution\b",
        ],
    ):
        add_signal("legal_threat")

    # Keep only schema-approved signals.
    signals = _deduplicate_signals(signals)

    # Final charity safeguard: UPI/QR is the payment channel when the
    # underlying request is explicitly framed as a donation/charity scam.
    if charity_context and charity_action:
        fraud_type = "CHARITY_SCAM"
        confidence = max(confidence, 0.96)

    return {
        "language": language,
        "fraud_type": fraud_type,
        "signals": signals,
        "attacker_goal": attacker_goal,
        "confidence": round(confidence, 4),
    }


# ============================================================
# MODEL CALL
# ============================================================

def _call_model(message: str) -> Dict[str, Any]:
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        format=schema,
        think=False,
        stream=False,
        options=OLLAMA_OPTIONS,
    )

    content = response.message.content

    if isinstance(content, dict):
        return content

    if not isinstance(content, str):
        raise ValueError("Ollama returned an unexpected response format.")

    content = content.strip()

    # Remove accidental markdown fences if the model returns them.
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

    return json.loads(content)


# ============================================================
# PUBLIC API
# ============================================================

def analyze_fraud(message: str) -> Dict[str, Any]:
    """
    Main Garuda AI fraud-analysis function.

    Returns:
        {
            "language": str,
            "fraud_type": str,
            "signals": list[str],
            "attacker_goal": str,
            "confidence": float
        }
    """

    if not isinstance(message, str):
        raise TypeError("message must be a string")

    message = message.strip()

    if not message:
        return {
            "language": "Unknown",
            "fraud_type": "OTHER",
            "signals": [],
            "attacker_goal": "N/A",
            "confidence": 0.0,
        }

    # Strong deterministic scenarios are used before the model only for
    # obvious cases. The model remains responsible for semantic analysis.
    strong = _detect_strong_scenario(message)

    try:
        model_result = _call_model(message)
    except Exception as exc:
        # Graceful fallback for model/JSON failures.
        model_result = {
            "language": "Unknown",
            "fraud_type": "OTHER",
            "signals": [],
            "attacker_goal": "N/A",
            "confidence": 0.35,
            "_model_error": str(exc),
        }

    result = _apply_post_processing(message, model_result)

    # A strong deterministic scenario is a final fallback if the model
    # returned an invalid/ambiguous category.
    if strong is not None:
        strong_type, strong_confidence = strong

        if strong_type in {
            "MALWARE",
            "DIGITAL_ARREST",
            "UPI_FRAUD",
            "PHISHING",
            "LOTTERY_SCAM",
            "INVESTMENT_SCAM",
            "JOB_SCAM",
            "LOAN_SCAM",
            "CHARITY_SCAM",
            "ROMANCE_SCAM",
            "COURIER_SCAM",
            "KYC_SCAM",
            "SIM_SWAP",
            "FAKE_CUSTOMER_SUPPORT",
            "GOVERNMENT_IMPERSONATION",
            "BANK_IMPERSONATION",
            "OTP_SCAM",
        }:
            # Never allow a model-generated BANK_IMPERSONATION to override
            # explicit phishing/malware mechanisms.
            if strong_type in {"PHISHING", "MALWARE"}:
                result["fraud_type"] = strong_type
                result["confidence"] = max(
                    float(result.get("confidence", 0.0)),
                    strong_confidence,
                )

    return result


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def analyze_message(message: str) -> Dict[str, Any]:
    """
    Existing Garuda AI components can continue using analyze_message().
    """

    return analyze_fraud(message)


# ============================================================
# OPTIONAL LOCAL TEST
# ============================================================

if __name__ == "__main__":
    test_messages = [
        "Your SBI account is blocked. Tell us the OTP immediately.",
        "Your SBI account will be suspended. Verify your account using this link: https://example.com and enter your password.",
        "Your KYC is incomplete. Download this security APK.",
        "Scan this QR code to receive your refund and enter your UPI PIN.",
        "Your SBI statement is available in the official banking application. Never share your OTP or PIN.",
        "Hi, your account has an issue. Please check this immediately.",
    ]

    for index, message in enumerate(test_messages, start=1):
        print("\n" + "=" * 70)
        print(f"TEST {index}")
        print("=" * 70)
        print(message)

        result = analyze_fraud(message)

        print(json.dumps(result, indent=2, ensure_ascii=False))
