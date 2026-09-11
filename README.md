# Garuda AI

> **Privacy-first multilingual cyber-safety agent for scam detection, risk analysis, trusted investigation, and safe escalation.**

## Hackathon Track

**Track 03 — Trustworthy, Responsible & Secure AI**

---

## Problem

Scam messages arrive through SMS, WhatsApp, email, chat, and screenshots. They may impersonate banks, governments, police, delivery services, employers, customer-support teams, or financial platforms.

Users need more than a binary `scam / not scam` answer. Garuda AI combines fraud classification, risk scoring, trusted evidence retrieval, MCP tool use, safety checks, escalation, and traceable explanations.

---

## What Garuda AI Does

Given a suspicious message or screenshot, Garuda AI:

1. Prepares the input.
2. Classifies the likely fraud mechanism.
3. Detects suspicious signals and estimates confidence.
4. Calculates a 0–100 risk score.
5. Investigates the case using FastMCP + RAG.
6. Validates grounding and safety.
7. Continues safe, well-supported cases or escalates uncertain or security-sensitive cases.
8. Generates an explanation and recommended action.

The primary analysis path is designed for **local-first operation using Qwen3-4B through Ollama**.

---

## Architecture

```text
User message / screenshot
          |
          v
    +-------------+
    | Intake Agent|
    +-------------+
          |
          v
 +----------------------+
 | Fraud Analysis Agent |
 |      Qwen3-4B        |
 +----------------------+
          |
          v
    +-------------+
    | Risk Engine |
    +-------------+
          |
          v
 +----------------------+
 | Investigation Agent  |
 +----------------------+
       |           |
       v           v
   FastMCP         RAG
     Tool       (Chroma)
       \           /
        \         /
         v       v
     +----------------+
     | Grounding /    |
     | Safety Critic  |
     +----------------+
         |       |
     CONTINUE   ESCALATE
         |       |
         v       v
 Explanation    Human
    Agent      Verification
         |
         v
       User
Input Pipeline
SMS / text / screenshot
          |
          v
      OCR (image)
          |
          v
    Fraud Analysis
          |
          v
Risk + Evidence + Confidence
          |
          v
    Safety Decision
          |
          v
Explanation / Escalation
Agentic Workflow

Garuda AI uses specialized roles instead of one monolithic prompt.

Intake Agent

Accepts and prepares the user input for analysis.

Fraud Analysis Agent

Uses Qwen3-4B through Ollama to classify fraud type, language, suspicious signals, attacker goal, and confidence.

Risk Engine

Converts fraud type and detected signals into a 0–100 risk score and risk level.

Investigation Agent

Requests trusted fraud intelligence through an actual FastMCP tool call.

RAG Layer

Retrieves trusted cyber-safety evidence from the local Chroma vector store.

Grounding Validator / Safety Critic

Checks:

confidence
ambiguity
evidence availability
retrieval relevance
grounding strength
risk
prompt-injection patterns
Router / Escalation

Continues well-supported cases or escalates uncertain or security-sensitive cases for human verification.

Explanation Agent

Produces the user-facing explanation, attacker goal, evidence summary, and recommended action.

Fraud Coverage

Garuda AI currently supports:

BANK_IMPERSONATION
OTP_SCAM
UPI_FRAUD
KYC_SCAM
JOB_SCAM
INVESTMENT_SCAM
COURIER_SCAM
DIGITAL_ARREST
GOVERNMENT_IMPERSONATION
FAKE_CUSTOMER_SUPPORT
ROMANCE_SCAM
LOTTERY_SCAM
PHISHING
MALWARE
SIM_SWAP
LOAN_SCAM
CHARITY_SCAM
OTHER
NOT_FRAUD

The analyzer is designed for English, Indian languages, and code-mixed messages.

Risk and Safety

Every analysis produces:

Fraud Type
Risk Score (0–100)
Risk Level
Confidence
Detected Signals
Attacker Goal
Trusted Evidence
Safety Decision
Risk Levels
0–24    LOW
25–49   MODERATE
50–74   HIGH
75–100  CRITICAL

The Safety Critic can escalate when:

confidence is low;
the classification is ambiguous;
prompt injection is detected;
trusted evidence is missing;
retrieved evidence is weak or mismatched;
high risk lacks supporting evidence.

A strong NOT_FRAUD result can pass without fraud-specific evidence.

RAG Grounding

Garuda AI stores trusted fraud intelligence in a local Chroma vector store.

Evidence metadata includes:

title
fraud type
source
source URL
relevance distance

The Grounding Validator checks:

evidence availability
semantic relevance
fraud-type agreement where available
retrieval distance
model confidence

Strong trusted semantic evidence can support a classification even when a knowledge item is tagged under a related fraud mechanism. Weak or missing evidence can trigger escalation.

MCP Tool Use

Investigation is performed through an actual FastMCP tool call:

Investigation Agent
        |
        v
     FastMCP
        |
        v
scam_intelligence
        |
        v
Trusted RAG knowledge base

This keeps investigation as a tool-based step rather than hard-coded retrieval inside the analysis agent.

Prompt-Injection Defense

User messages are treated as untrusted input.

The safety layer detects common instruction-manipulation patterns such as:

ignore previous instructions
ignore all instructions
reveal your instructions
system prompt
developer message

Security-related injection cases are escalated rather than blindly followed.

Observability

Garuda AI records a trace for the complete workflow.

Example:

Garuda AI       STARTED
Intake Agent    STARTED
Intake Agent    COMPLETED
Fraud Analysis  COMPLETED
Risk Engine     COMPLETED
Investigation   STARTED
MCP Tool        TOOL_CALL
RAG             RETRIEVED
Investigation   COMPLETED
Safety Critic   CONTINUE / ESCALATE
Explanation     COMPLETED
Garuda AI       FINAL

Each trace entry records:

timestamp
component
event
details
reason
duration
Screenshot Analysis

The web UI supports screenshot input.

Screenshot
    |
    v
Tesseract OCR
    |
    v
Extracted text
    |
    v
Garuda AI analysis pipeline

The same fraud-analysis, risk, RAG, safety, and escalation pipeline is reused after OCR.

Multilingual Support

Garuda AI is designed to handle multilingual and code-mixed scam communication, including Indian-language inputs such as:

Hindi
Telugu
Tamil
Malayalam
Kannada
Hinglish-style messages
Evaluation

Garuda AI includes a gold evaluation set covering:

fraud classification
legitimate messages
ambiguous cases
escalation behavior
prompt-injection defense
Current Verified Gold-Set Evaluation
Fraud Classification Accuracy: 100.00%
Escalation Accuracy:           100.00%
Prompt Injection Defense:      100.00%
Overall Case Accuracy:         100.00%

Run the evaluator with:

python -m evaluation.evaluator
Example
Input
Your SBI account will be blocked.
Share the OTP immediately or your account will be closed.
Expected Behavior
Fraud Type: BANK_IMPERSONATION
Risk:       CRITICAL
Confidence: High

Possible detected signals:

impersonation
urgency
threat
OTP request
Recommended Action

Do not share the OTP. Verify the request through an official banking channel.

Privacy and Security

Garuda AI is designed for local-first processing.

Qwen3-4B runs locally through Ollama.
User messages are not intentionally sent to a shared external LLM for the primary analysis path.
Secrets belong in .env and must not be committed.
.env, virtual environments, Python caches, and the local Chroma database are excluded from version control.
Human escalation preserves the original analysis context instead of silently guessing.
Running Locally
Requirements
Python 3.12
Ollama
Qwen3-4B
Python virtual environment
Pull the Local Model
ollama pull qwen3:4b
Create / Activate the Environment
python -m venv .venv
.venv\Scripts\activate
Install Dependencies
pip install -r requirements.txt
Start Backend
python -m uvicorn api.api:app --reload

Backend:

http://127.0.0.1:8000
Start Frontend

Open another terminal:

python -m http.server 5500 --bind 127.0.0.1 --directory ui

Frontend:

http://127.0.0.1:5500
Testing
Grounding Validator
python -m tests.test_grounding_validator
Main Evaluation
python -m evaluation.evaluator
Project Structure
Garuda ai/
├── agents/
├── api/
├── evaluation/
├── observability/
├── orchestration/
├── rag/
├── safety/
├── tests/
├── tools/
├── ui/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md