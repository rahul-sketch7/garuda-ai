from agents.signal_normalizer import normalize_result


slm_result = {
    "language": "Tamil",

    "fraud_type": "Account block",

    "signals": [
        "SBI account block",
        "OTP cheppandi immediately"
    ],

    "attacker_goal": "Immediate account takeover via OTP theft",

    "confidence": 0.85
}


result = normalize_result(slm_result)


print("NORMALIZED RESULT")
print("=================")

print("Language:", result["language"])
print("Fraud Type:", result["fraud_type"])
print("Signals:", result["signals"])
print("Attacker Goal:", result["attacker_goal"])
print("Confidence:", result["confidence"])