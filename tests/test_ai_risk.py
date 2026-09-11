from agents.fraud_analyzer import analyze_message
from agents.risk_engine import analyze_risk


TEST_MESSAGES = [

    "I'm calling from SBI. Your account will be blocked today. Tell me the OTP.",

    "Your UPI refund is ready. Scan this QR code and pay the verification fee.",

    "Congratulations! You have been selected for a work from home job. Pay ₹2000 registration fee.",

    "Invest ₹10,000 today and get guaranteed returns of 40%.",

    "Your parcel is held at customs. Pay the processing fee using this link.",

    "This is cyber crime police. Your Aadhaar is linked to a criminal case. You will be arrested.",

    "Your KYC expires today. Verify your account immediately using this link.",

    "Your order has been delivered successfully. Thank you for shopping with us."
]


for message in TEST_MESSAGES:

    print("\n" + "=" * 70)

    print("MESSAGE:")
    print(message)

    # -----------------------------
    # AI ANALYSIS
    # -----------------------------

    analysis = analyze_message(message)

    print("\nAI ANALYSIS:")
    print("Fraud Type:", analysis["fraud_type"])
    print("Signals:", analysis["signals"])
    print("Confidence:", analysis["confidence"])

    # -----------------------------
    # RISK ANALYSIS
    # -----------------------------

    risk = analyze_risk(
        analysis["signals"],
        analysis["fraud_type"],
    )

    print("\nRISK ANALYSIS:")
    print("Risk Score:", risk["risk_score"])
    print("Risk Level:", risk["risk_level"])