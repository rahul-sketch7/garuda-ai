import json
import ollama

message = """
SBI account block avuthundi, OTP cheppandi immediately.
"""

schema = {
    "type": "object",
    "properties": {
        "language": {
            "type": "string"
        },
        "fraud_type": {
            "type": "string"
        },
        "signals": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "attacker_goal": {
            "type": "string"
        },
        "confidence": {
            "type": "number"
        }
    },
    "required": [
        "language",
        "fraud_type",
        "signals",
        "attacker_goal",
        "confidence"
    ]
}

response = ollama.chat(
    model="qwen3:4b",

    messages=[
        {
            "role": "system",
            "content": """
You are FraudShield's internal fraud detection engine.

Analyze ONLY the supplied message.

Return ONLY JSON matching the schema.

Do not:
- explain
- give advice
- use Markdown
- write paragraphs
- use previous conversation
- invent facts
- invent sources
- say 100% scam

Extract:
- language
- fraud type
- suspicious signals
- attacker goal
- confidence
"""
        },
        {
            "role": "user",
            "content": message
        }
    ],

    format=schema,

    think=False,
    stream=False,

    options={
        "temperature": 0,
        "num_predict": 150,
        "num_ctx": 4096
    }
)

content = response.message.content

print(content)

try:
    result = json.loads(content)

    print("\nFraud Type:", result["fraud_type"])
    print("Confidence:", result["confidence"])
    print("Signals:", result["signals"])

except json.JSONDecodeError:
    print("\nERROR: Model did not return valid JSON.")