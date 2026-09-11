import asyncio

from orchestration.garuda_ai import analyze_with_garuda


# ============================================================
# Garuda AI - Escalation Test
# ============================================================

message = (
    "Hi, your account has an issue. "
    "Please check this immediately."
)


result = asyncio.run(
    analyze_with_garuda(message)
)


print("\n")
print("=" * 60)
print("GARUDA AI ESCALATION TEST")
print("=" * 60)


print("\nSTATUS:")
print(result["status"])


print("\nANALYSIS:")
print(result["analysis"])


print("\nRISK:")
print(result["risk"])


print("\nINVESTIGATION:")
print(result["investigation"])


print("\nSAFETY:")
print(result["safety"])


if result["status"] == "ESCALATED":

    print("\nESCALATION:")
    print(result["escalation"])

else:

    print("\nEXPLANATION:")
    print(result["explanation"])


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


print("\n")
print("=" * 60)
print("END OF ESCALATION TEST")
print("=" * 60)