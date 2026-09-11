from agents.signal_normalizer import normalize_signals


TEST_MESSAGES = [

    (
        "BANK + OTP",
        "I'm calling from SBI. Your account will be blocked today. Tell me the OTP."
    ),

    (
        "UPI",
        "Your UPI refund is ready. Scan this QR code and pay the verification fee."
    ),

    (
        "JOB SCAM",
        "Congratulations! You have been selected for a work from home job. Pay a registration fee of ₹2000."
    ),

    (
        "INVESTMENT",
        "Invest ₹10,000 today and get guaranteed returns of 40%."
    ),

    (
        "COURIER",
        "Your parcel is held at customs. Pay the processing fee using this link."
    ),

    (
        "DIGITAL ARREST",
        "This is cyber crime police. Your Aadhaar is linked to a criminal case. You will be arrested."
    ),

    (
        "KYC",
        "Your KYC expires today. Verify your account immediately using this link."
    ),

    (
        "NORMAL",
        "Your order has been delivered successfully. Thank you for shopping with us."
    ),
]


print("\nFRAUDSHIELD SIGNAL TEST")
print("========================")


for name, message in TEST_MESSAGES:

    signals = normalize_signals(message)

    print(f"\n{name}")
    print("Message:", message)
    print("Signals:", signals)