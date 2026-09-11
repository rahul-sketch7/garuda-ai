from safety.escalation import create_escalation


result = create_escalation(
    user_message="Your account has a problem. Contact us.",
    risk_score=65,
    confidence=0.45,
    reasons=["low_confidence"]
)


print("ESCALATION RESULT")
print("=================")

for key, value in result.items():
    print(f"{key}: {value}")