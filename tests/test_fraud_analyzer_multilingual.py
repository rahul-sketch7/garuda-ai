from agents.fraud_analyzer import analyze_fraud


TEST_CASES = [
    {
        "name": "English OTP Scam",
        "message": (
            "Your SBI account is blocked. "
            "Share your OTP immediately or your account will be closed."
        ),
        "expected": "BANK_IMPERSONATION",
    },

    {
        "name": "English Legitimate OTP Warning",
        "message": (
            "Your SBI account statement is ready. "
            "Review your transactions in the official YONO app. "
            "Never share your OTP, PIN or password with anyone."
        ),
        "expected": "NOT_FRAUD",
    },

    {
        "name": "Telugu OTP Scam",
        "message": (
            "మీ SBI ఖాతా బ్లాక్ చేయబడుతుంది. "
            "ఖాతాను కొనసాగించడానికి మీ OTP వెంటనే మాకు పంపండి."
        ),
        "expected": "OTP_SCAM",
    },

    {
        "name": "Telugu Legitimate Security Warning",
        "message": (
            "ప్రియమైన కస్టమర్, మీ SBI ఖాతా స్టేట్‌మెంట్‌ జూలై నెలకు సిద్ధంగా ఉంది. "
            "మీ ఖాతాలోని లావాదేవీలను పరిశీలించడానికి SBI YONO యాప్‌ను తెరిచి "
            "Account Statement విభాగానికి వెళ్లండి. "
            "ఏదైనా అనుమానాస్పద లావాదేవీ కనిపిస్తే వెంటనే SBI అధికారిక "
            "Customer Care నంబర్‌ను సంప్రదించండి. "
            "మీ OTP, PIN లేదా Password ఎవరితోనూ పంచుకోవద్దు."
        ),
        "expected": "NOT_FRAUD",
    },

    {
        "name": "Hindi OTP Scam",
        "message": (
            "आपका SBI खाता बंद होने वाला है। "
            "खाता चालू रखने के लिए अपना OTP तुरंत भेजें।"
        ),
        "expected": "OTP_SCAM",
    },

    {
        "name": "Hindi Legitimate Warning",
        "message": (
            "अपना OTP, PIN या पासवर्ड किसी के साथ साझा न करें। "
            "संदिग्ध लेनदेन होने पर बैंक के आधिकारिक नंबर पर संपर्क करें।"
        ),
        "expected": "NOT_FRAUD",
    },

    {
        "name": "Tamil Legitimate Warning",
        "message": (
            "உங்கள் OTP, PIN அல்லது கடவுச்சொல்லை யாரிடமும் பகிர வேண்டாம். "
            "சந்தேகமான பரிவர்த்தனை இருந்தால் அதிகாரப்பூர்வ வங்கி எண்ணை தொடர்பு கொள்ளுங்கள்."
        ),
        "expected": "NOT_FRAUD",
    },

    {
        "name": "Hinglish Scam",
        "message": (
            "Your SBI account block hone wala hai. "
            "KYC complete karne ke liye OTP immediately share karo."
        ),
        "expected": "KYC_SCAM",
    },

    {
        "name": "Telugu-English Malware",
        "message": (
            "మీ KYC incomplete ఉంది. "
            "Security verification కోసం ఈ APK install చేయండి."
        ),
        "expected": "MALWARE",
    },

    {
        "name": "Normal English",
        "message": (
            "Your SBI account statement for July is available "
            "in the official YONO application."
        ),
        "expected": "NOT_FRAUD",
    },
]


def main():
    passed = 0

    print("\n========================================")
    print("GARUDA AI MULTILINGUAL ANALYZER TEST")
    print("========================================\n")

    for case in TEST_CASES:
        print(f"TEST: {case['name']}")

        try:
            result = analyze_fraud(case["message"])

            actual = result["fraud_type"]
            confidence = result["confidence"]
            language = result["language"]

            print(f"Language   : {language}")
            print(f"Expected   : {case['expected']}")
            print(f"Actual     : {actual}")
            print(f"Confidence: {confidence}")
            print(f"Signals    : {result['signals']}")

            if actual == case["expected"]:
                print("RESULT     : PASS")
                passed += 1
            else:
                print("RESULT     : FAIL")

        except Exception as e:
            print("RESULT     : ERROR")
            print(f"Error      : {e}")

        print("----------------------------------------")

    total = len(TEST_CASES)

    print("\n========================================")
    print("TEST SUMMARY")
    print("========================================")
    print(f"Passed: {passed}/{total}")
    print(f"Accuracy: {(passed / total) * 100:.2f}%")
    print("========================================\n")


if __name__ == "__main__":
    main()