from agents.explanation_agent import generate_explanation


result = generate_explanation(
    fraud_type="BANK_IMPERSONATION_OTP",

    signals=[
        "bank_impersonation",
        "account_blocking_threat",
        "otp_request",
        "urgency"
    ],

    attacker_goal="Obtain an authentication code",

    risk_score=90,

    risk_level="CRITICAL",

    confidence=0.95
)


print("EXPLANATION")
print("===========")

print("Fraud Type:", result["fraud_type"])
print("Risk:", result["risk_score"])
print("Level:", result["risk_level"])
print("Confidence:", result["confidence"])

print("\nSummary:")
print(result["summary"])

print("\nEvidence:")

for item in result["evidence"]:
    print("-", item)

print("\nAttacker Goal:")
print(result["attacker_goal"])

print("\nRecommended Action:")
print(result["recommended_action"])