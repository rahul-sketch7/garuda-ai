from agents.risk_engine import analyze_risk


signals = [
    "account_blocking_threat",
    "bank_impersonation",
    "otp_request",
    "urgency"
]


result = analyze_risk(signals)


print("RISK ENGINE RESULT")
print("==================")

print("Risk Score:", result["risk_score"])
print("Risk Level:", result["risk_level"])