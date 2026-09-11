import asyncio

from agents.fraud_analyzer import analyze_message
from agents.investigation_agent import investigate


message = (
    "I'm calling from SBI. "
    "Your account will be blocked today. "
    "Tell me the OTP you received."
)


# ---------------------------------------
# STEP 1: AI ANALYSIS
# ---------------------------------------

analysis = analyze_message(message)

print("\nAI ANALYSIS")
print("===========")

print(analysis)


# ---------------------------------------
# STEP 2: INVESTIGATION
# ---------------------------------------

investigation = asyncio.run(
    investigate(
        message,
        analysis["fraud_type"],
        analysis["signals"]
    )
)


print("\nINVESTIGATION RESULT")
print("====================")

print(investigation)