# ============================================================
# Garuda AI - Trusted Fraud Knowledge Base
# ============================================================

from rag.vector_store import collection


# ============================================================
# TRUSTED KNOWLEDGE
# ============================================================

KNOWLEDGE = [

    # --------------------------------------------------------
    # BANK / OTP / CREDENTIAL FRAUD
    # Source: RBI
    # --------------------------------------------------------

    {
        "title": "RBI warning on impersonation and OTP requests",
        "fraud_type": "BANK_IMPERSONATION",
        "evidence": (
            "Fraudsters may impersonate RBI, banks, or government "
            "officials and use alarming issues such as account blocking "
            "to pressure people into sharing personal information, "
            "account details, PINs, passwords, or OTPs."
        ),
        "source": "Reserve Bank of India",
        "source_url": (
            "https://systemhealth.rbi.org.in/"
            "Scripts/FS_PressRelease.aspx_prid%3D58595%26fn%3D14.html"
        )
    },

    {
        "title": "RBI guidance on protecting OTP and PIN",
        "fraud_type": "OTP_SCAM",
        "evidence": (
            "RBI advises customers not to share account login details, "
            "personal information, KYC documents, card information, "
            "PINs, passwords, or OTPs with unidentified persons or "
            "through unverified websites or applications."
        ),
        "source": "Reserve Bank of India",
        "source_url": (
            "https://systemhealth.rbi.org.in/"
            "Scripts/FS_PressRelease.aspx_prid%3D58595%26fn%3D14.html"
        )
    },

    {
        "title": "RBI digital banking safety",
        "fraud_type": "PHISHING",
        "evidence": (
            "RBI advises users not to share passwords, PINs, OTPs, or "
            "CVV information and warns users against clicking suspicious "
            "links received through SMS, email, or social media."
        ),
        "source": "Reserve Bank of India",
        "source_url": (
            "https://rbikehtahai.rbi.org.in/"
            "digital-banking-cyber-security.html"
        )
    },


    # --------------------------------------------------------
    # UPI / QR FRAUD
    # Source: NPCI + RBI
    # --------------------------------------------------------

    {
        "title": "NPCI warning on QR code payment scams",
        "fraud_type": "UPI_FRAUD",
        "evidence": (
            "NPCI warns that QR codes sent by unknown people may be used "
            "in deceptive payment schemes. Scanning a QR code and entering "
            "a UPI PIN is intended for making a payment, not receiving money."
        ),
        "source": "National Payments Corporation of India",
        "source_url": (
            "https://www.npci.org.in/fraud-awareness"
        )
    },

    {
        "title": "RBI warning on unknown QR codes",
        "fraud_type": "UPI_FRAUD",
        "evidence": (
            "RBI advises users to be cautious with QR codes or links "
            "received from unknown sources and states that entering a "
            "PIN or OTP is not required to receive money."
        ),
        "source": "Reserve Bank of India",
        "source_url": (
            "https://rbikehtahai.rbi.org.in/qr"
        )
    },

    {
        "title": "NPCI UPI PIN safety",
        "fraud_type": "UPI_FRAUD",
        "evidence": (
            "NPCI states that the UPI PIN is used to authorize bank "
            "transactions and should not be shared with anyone. "
            "Customers should verify payment requests before authorizing them."
        ),
        "source": "National Payments Corporation of India",
        "source_url": (
            "https://www.npci.org.in/what-we-do/upi/faqs"
        )
    },


    # --------------------------------------------------------
    # DIGITAL ARREST / GOVERNMENT IMPERSONATION
    # Source: RBI + I4C
    # --------------------------------------------------------

    {
        "title": "RBI warning on digital arrest and intimidation",
        "fraud_type": "DIGITAL_ARREST",
        "evidence": (
            "RBI has reported cases where fraudsters impersonate "
            "government or RBI officials, intimidate victims with claims "
            "about illegal activity or suspicious transactions, and demand "
            "money or sensitive information. RBI also notes incidents "
            "described as digital arrest."
        ),
        "source": "Reserve Bank of India",
        "source_url": (
            "https://systemhealth.rbi.org.in/"
            "Scripts/FS_PressRelease.aspx_prid%3D58595%26fn%3D14.html"
        )
    },

    {
        "title": "Indian Cyber Crime Portal digital arrest advisory",
        "fraud_type": "DIGITAL_ARREST",
        "evidence": (
            "The National Cyber Crime Reporting Portal publishes an "
            "advisory specifically addressing digital-arrest-based "
            "cybercrime involving intimidation and blackmail."
        ),
        "source": "National Cyber Crime Reporting Portal",
        "source_url": (
            "https://cybercrime.gov.in/Webform/Advisory.aspx"
        )
    },


    # --------------------------------------------------------
    # JOB SCAMS
    # Source: I4C
    # --------------------------------------------------------

    {
        "title": "Cyber Crime Portal fake job advisory",
        "fraud_type": "JOB_SCAM",
        "evidence": (
            "The National Cyber Crime Reporting Portal has published "
            "an advisory concerning fake job offer SMS messages used "
            "to perpetrate cybercrime."
        ),
        "source": "National Cyber Crime Reporting Portal",
        "source_url": (
            "https://cybercrime.gov.in/Webform/Advisory.aspx"
        )
    },


    # --------------------------------------------------------
    # PHISHING
    # Source: CERT-In
    # --------------------------------------------------------

    {
        "title": "CERT-In phishing safety guidance",
        "fraud_type": "PHISHING",
        "evidence": (
            "CERT-In advises users to check the integrity of URLs before "
            "providing login credentials or clicking links and to avoid "
            "submitting personal information to unknown or unfamiliar "
            "websites."
        ),
        "source": "Indian Computer Emergency Response Team",
        "source_url": (
            "https://www.cert-in.org.in/"
            "s2cMainServlet?CACODE=CICA-2020-2788&pageid=PUBADV01"
        )
    },

    {
        "title": "CERT-In suspicious link guidance",
        "fraud_type": "PHISHING",
        "evidence": (
            "CERT-In recommends accessing genuine websites directly "
            "through the organization's website rather than following "
            "suspicious links and advises users to report unusual activity."
        ),
        "source": "Indian Computer Emergency Response Team",
        "source_url": (
            "https://www.cert-in.org.in/"
            "s2cMainServlet?CACODE=CICA-2020-2788&pageid=PUBADV01"
        )
    },


    # --------------------------------------------------------
    # MALICIOUS APPLICATIONS / MALWARE
    # Source: RBI
    # --------------------------------------------------------

    {
        "title": "RBI warning on unverified applications",
        "fraud_type": "MALWARE",
        "evidence": (
            "RBI warns that fraudsters may persuade victims to install "
            "unauthorised or unverified applications through links in "
            "fraudulent communications. Users should be cautious when "
            "a suspicious message asks them to download an application "
            "to complete KYC, account verification, security checks, "
            "or other banking-related processes."
        ),
        "source": "Reserve Bank of India",
        "source_url": (
            "https://systemhealth.rbi.org.in/"
            "Scripts/FS_PressRelease.aspx_prid%3D58595%26fn%3D14.html"
        )
    },

    {
        "title": "RBI warning on malicious applications",
        "fraud_type": "MALWARE",
        "evidence": (
            "RBI has warned about users being tricked into downloading "
            "spurious applications that can access critical information "
            "stored on devices. Fraudulent communications may persuade "
            "victims to install unknown or unauthorised applications "
            "under the pretext of security, KYC, account verification, "
            "or similar requirements."
        ),
        "source": "Reserve Bank of India",
        "source_url": (
            "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=11917"
        )
    },

    {
        "title": "RBI guidance on suspicious application downloads",
        "fraud_type": "MALWARE",
        "evidence": (
            "Fraudsters may use messages about KYC, account problems, "
            "security verification, or other urgent banking issues "
            "to persuade users to download or install unverified "
            "applications. Installing such applications can expose "
            "information stored on the device."
        ),
        "source": "Reserve Bank of India",
        "source_url": (
            "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=11917"
        )
    },


    # --------------------------------------------------------
    # GENERAL DIGITAL PAYMENT FRAUD
    # Source: RBI / NPCI
    # --------------------------------------------------------

    {
        "title": "RBI digital payment fraud awareness",
        "fraud_type": "GENERAL",
        "evidence": (
            "RBI identifies disclosure of critical personal information, "
            "opening links received through messages or email, SIM swapping, "
            "and downloading suspicious applications as fraud risks."
        ),
        "source": "Reserve Bank of India",
        "source_url": (
            "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=11917"
        )
    },

    {
        "title": "NPCI fraud awareness",
        "fraud_type": "GENERAL",
        "evidence": (
            "NPCI warns users about fraud patterns involving fake cashback "
            "links, QR codes, fake investment schemes, threatening SMS or "
            "social-media messages, unknown applications, and online scams."
        ),
        "source": "National Payments Corporation of India",
        "source_url": (
            "https://www.npci.org.in/fraud-awareness"
        )
    }

]


# ============================================================
# LOAD KNOWLEDGE INTO CHROMA
# ============================================================

def load_knowledge():

    # --------------------------------------------------------
    # Remove old knowledge
    # --------------------------------------------------------

    existing = collection.get()

    existing_ids = existing.get("ids", [])

    if existing_ids:

        collection.delete(ids=existing_ids)

        print(
            f"Removed {len(existing_ids)} old knowledge entries."
        )


    # --------------------------------------------------------
    # Prepare trusted knowledge
    # --------------------------------------------------------

    documents = []
    metadatas = []
    ids = []

    for index, item in enumerate(KNOWLEDGE):

        documents.append(
            item["evidence"]
        )

        metadatas.append({
            "title": item["title"],
            "fraud_type": item["fraud_type"],
            "source": item["source"],
            "source_url": item["source_url"]
        })

        ids.append(
            f"garuda_trusted_{index + 1}"
        )


    # --------------------------------------------------------
    # Insert trusted knowledge
    # --------------------------------------------------------

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(
        f"Loaded {len(KNOWLEDGE)} trusted knowledge entries "
        "into Garuda AI RAG."
    )


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":
    load_knowledge()