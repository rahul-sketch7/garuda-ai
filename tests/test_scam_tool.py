from tools.scam_intelligence import search_scam_intelligence


result = search_scam_intelligence(
    "bank account blocked OTP request"
)


print("SCAM INTELLIGENCE TOOL")
print("======================")

print("Query:", result["query"])

for item in result["results"]:
    print("\nTitle:", item["title"])
    print("Fraud Type:", item["fraud_type"])
    print("Evidence:", item["evidence"])