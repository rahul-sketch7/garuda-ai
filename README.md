Garuda AI

Privacy-first multilingual cyber-safety agent

Garuda AI analyzes suspicious digital messages and helps users understand:

what type of fraud is being attempted

which signals make the message suspicious

what the attacker is trying to obtain

how risky the message is

what action the user should take

when the system is uncertain and needs human verification

Garuda AI is designed around local-first AI using Qwen3-4B through Ollama.

Problem

Scam messages increasingly use bank impersonation, fake KYC requests, UPI/payment tricks, phishing links, fake jobs, investment promises, courier threats, digital-arrest tactics, malicious applications, and other social-engineering techniques.

Users need more than a binary "scam/not scam" answer. Garuda AI combines classification, risk scoring, trusted evidence retrieval, tool use, safety checks, escalation, and traceable explanations.

Architecture

                         USER
                           |
                           v
                    +-------------+
                    | Intake Agent|
                    +-------------+
                           |
                           v
                 +-------------------+
                 | Fraud Analysis     |
                 | Agent (Qwen3-4B)   |
                 +-------------------+
                           |
                           v
                    +-------------+
                    | Risk Engine |
                    +-------------+
                           |
                           v
                 +-------------------+
                 | Investigation     |
                 | Agent             |
                 +-------------------+
                    |             |
                    v             v
                 FastMCP          RAG
                 Tool             |
                    |             |
                    +------+------+
                           |
                           v
                  +----------------+
                  | Grounding /    |
                  | Safety Critic  |
                  +----------------+
                       |       |
                 CONTINUE    ESCALATE
                       |       |
                       v       v
                Explanation   Human
                   Agent     Verification
                       |
                       v
                     USER

Input pipeline

SMS / text / screenshot
          |
          v
OCR (for screenshots)
          |
          v
Fraud Analysis
          |
          v
Risk + Evidence + Confidence
          |
          v
Safety decision
          |
          v
Explanation / Escalation

Agentic workflow

Garuda AI uses separate roles rather than one monolithic prompt:

Intake Agent — accepts and prepares the user input.

Fraud Analysis Agent — classifies the fraud type, signals, attacker goal, language, and confidence.

Risk Engine — converts fraud type and signals into a 0–100 risk score.

Investigation Agent — requests trusted fraud intelligence through an MCP tool.

RAG layer — retrieves evidence from a persistent Chroma vector store.

Grounding Validator / Safety Critic — checks confidence, prompt injection, ambiguity, evidence availability, and grounding strength.

Router — continues safe cases or escalates uncertain cases.

Explanation Agent — produces an evidence-backed user-facing result.

Escalation — preserves the original message, analysis, risk, confidence, reasons, evidence, investigation output, and trace for human review.

Fraud coverage

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

Risk and safety

Every analysis produces:

Fraud Type
Risk Score (0–100)
Risk Level
Confidence
Signals
Attacker Goal
Trusted Evidence
Safety Decision

Risk levels:

0–20    LOW
21–50   SUSPICIOUS
51–75   HIGH
76–100  CRITICAL

The Safety Critic can escalate when:

confidence is low

the classification is ambiguous

prompt injection is detected

trusted evidence is missing

retrieved evidence is weak or mismatched

A strong NOT_FRAUD result does not require fraud evidence.

RAG grounding

Garuda AI stores trusted fraud intelligence in Chroma.

Evidence metadata includes:

title
fraud_type
source
source_url
relevance_distance

The Grounding Validator checks:

evidence availability

semantic relevance

fraud-type agreement where available

retrieval distance

model confidence

Strong trusted semantic evidence can support a classification even when a knowledge item is tagged under a related fraud mechanism. Weak or missing evidence can trigger escalation.

MCP tool use

Investigation is performed through a FastMCP tool:

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

This keeps the investigation step as an actual tool call rather than hard-coded retrieval inside the agent.

Prompt-injection defense

User messages are treated as untrusted input.

The system detects common attempts such as:

ignore previous instructions
ignore all instructions
reveal your instructions
system prompt
developer message

Security-related injection cases are escalated rather than followed.

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

Each trace entry records a timestamp, component, event, details, reason, and duration.

Screenshot analysis

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

Running locally

Requirements

Python 3.12

Ollama

Qwen3-4B

Python virtual environment

Pull the local model:

ollama pull qwen3:4b

Activate the environment:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Backend

python -m uvicorn api.api:app --reload

Backend:

http://127.0.0.1:8000

Frontend

Open another terminal:

python -m http.server 5500 --bind 127.0.0.1 --directory ui

Frontend:

http://127.0.0.1:5500

Testing

Grounding validator:

python -m tests.test_grounding_validator

Main evaluation:

python -m evaluation.evaluator

The current gold evaluation covers fraud classification, escalation behavior, and prompt-injection defense.

Current verified evaluation:

Fraud Classification Accuracy: 100.00%
Escalation Accuracy:           100.00%
Prompt Injection Defense:      100.00%
Overall Case Accuracy:         100.00%

Example

Input:

Your SBI account will be blocked.
Share the OTP immediately or your account will be closed.

Expected system behavior:

Fraud Type: BANK_IMPERSONATION
Risk:       CRITICAL
Confidence: High

Signals:
- impersonation
- urgency
- threat
- OTP request

Attacker Goal:
Obtain the victim's OTP.

Action:
Do not share the OTP.
Verify through an official banking channel.

Privacy and security

Garuda AI is designed for local-first processing.

Qwen3-4B runs locally through Ollama.

User messages are not intentionally sent to a shared external LLM.

Secrets belong in .env.

.env, virtual environments, Python caches, and the local Chroma database should not be committed.

Human escalation preserves context for verification instead of silently guessing.

Hackathon requirements coverage

Requirement

Garuda AI

Multi-agent orchestration

Intake, Analysis, Investigation, Safety, Explanation, Escalation

Tool use / MCP

FastMCP scam_intelligence

RAG grounding

Chroma + trusted evidence + grounding validator

Confidence & guardrails

Confidence, risk, grounding, prompt-injection checks

Escalation / resilience

Human verification with full context

Observability

Full workflow trace with reasons and timings

Evaluation

Gold dataset + evaluator

Security / data care

Local model + .env / .gitignore controls

Local-first bonus

Qwen3-4B through Ollama

3-minute demo plan

Demo 1 — Bank impersonation

Paste an urgent SBI + OTP scam.

Show:

classification

risk score

signals

attacker goal

trusted evidence

recommended action

Demo 2 — Multilingual

Use a Hindi, Telugu, or Hinglish scam.

Show that the same pipeline handles Indian-language/code-mixed input.

Demo 3 — Screenshot

Upload a scam screenshot.

Show:

Screenshot -> OCR -> Agents -> RAG -> Safety -> Result

Demo 4 — Uncertain case

Use:

Hi, your account has an issue. Please check this immediately.

Show:

OTHER
    |
    v
Insufficient certainty
    |
    v
ESCALATED

This demonstrates that Garuda AI does not blindly invent a fraud classification.

Project structure

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
├── chroma_db/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

Team / submission

Project: Garuda AI

Track: Cyber safety / fraud detection

Core positioning:

A multilingual, privacy-first personal cyber-safety agent that detects suspicious digital messages, explains how the attack works, grounds decisions in trusted evidence, and safely escalates uncertain cases.