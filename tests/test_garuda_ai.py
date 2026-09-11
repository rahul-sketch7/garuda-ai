import asyncio

from orchestration.garuda_ai import analyze_with_garuda


# ============================================================
# TEST MESSAGE
# ============================================================

message = (
    "I'm calling from SBI. "
    "Your account will be blocked today. "
    "Tell me the OTP you received."
)


# ============================================================
# RUN GARUDA AI
# ============================================================

result = asyncio.run(
    analyze_with_garuda(message)
)


# ============================================================
# DISPLAY RESULT
# ============================================================

print("\n")
print("=" * 60)
print("GARUDA AI RESULT")
print("=" * 60)


# ============================================================
# STATUS
# ============================================================

print("\nSTATUS:")
print(result["status"])


# ============================================================
# AI ANALYSIS
# ============================================================

print("\nANALYSIS:")
print(result["analysis"])


# ============================================================
# RISK
# ============================================================

print("\nRISK:")
print(result["risk"])


# ============================================================
# INVESTIGATION
# ============================================================

print("\nINVESTIGATION:")
print(result["investigation"])


# ============================================================
# SAFETY
# ============================================================

print("\nSAFETY:")
print(result["safety"])


# ============================================================
# ESCALATION OR EXPLANATION
# ============================================================

if result["status"] == "ESCALATED":

    print("\nESCALATION:")
    print(result["escalation"])

else:

    print("\nEXPLANATION:")
    print(result["explanation"])


# ============================================================
# OBSERVABILITY TRACE
# ============================================================

print("\nTRACE:")
print("=" * 60)

for index, event in enumerate(
    result["trace"],
    start=1
):

    print(
        f"[{index}] "
        f"{event['component']} | "
        f"{event['event']} | "
        f"{event['details']}"
    )

    if event["reason"]:

        print(
            f"     Reason: {event['reason']}"
        )


# ============================================================
# END
# ============================================================

print("\n")
print("=" * 60)
print("END OF GARUDA AI ANALYSIS")
print("=" * 60)