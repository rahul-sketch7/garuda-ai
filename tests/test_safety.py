from safety.safety_critic import check_safety


rag_results = {
    "documents": [
        [
            "Scammers may impersonate bank employees and request OTPs."
        ]
    ]
}


result = check_safety(
    confidence=0.45,
    risk_score=90,
    rag_results=rag_results,
    user_message="Your bank account will be blocked. Give me the OTP."
)


print("SAFETY CHECK")
print("============")

print("Decision:", result["decision"])
print("Safe:", result["safe"])
print("Reasons:", result["reasons"])