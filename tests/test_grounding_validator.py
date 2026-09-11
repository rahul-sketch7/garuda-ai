
from safety.grounding_validator import validate_grounding


def run():
    strong = {
        "results": [{
            "title": "RBI bank warning",
            "fraud_type": "BANK_IMPERSONATION",
            "evidence": "Fraudsters may impersonate banks and request OTPs.",
            "source": "RBI",
            "source_url": "https://rbi.org.in/",
            "relevance_distance": 0.80,
        }]
    }

    mismatch = {
        "results": [{
            "title": "RBI malware warning",
            "fraud_type": "MALWARE",
            "evidence": "Fraudsters may persuade victims to install malicious applications.",
            "source": "RBI",
            "source_url": "https://rbi.org.in/",
            "relevance_distance": 0.80,
        }]
    }

    no_evidence = {"results": []}

    a = validate_grounding("BANK_IMPERSONATION", strong, 0.95)
    b = validate_grounding("BANK_IMPERSONATION", mismatch, 0.95)
    c = validate_grounding("BANK_IMPERSONATION", no_evidence, 0.95)
    d = validate_grounding("NOT_FRAUD", no_evidence, 1.0)

    assert a["grounded"] is True
    assert a["status"] == "STRONG"

    assert b["grounded"] is False
    assert b["status"] == "MISMATCH"

    assert c["grounded"] is False
    assert c["status"] == "NONE"

    assert d["grounded"] is True
    assert d["status"] == "NOT_REQUIRED"

    print("GROUNDING VALIDATOR TEST: PASS")
    print("Strong evidence      :", a["status"])
    print("Type mismatch         :", b["status"])
    print("No evidence           :", c["status"])
    print("Legitimate message    :", d["status"])


if __name__ == "__main__":
    run()
