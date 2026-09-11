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
7. Continues safe, well-supported cases or escalates uncertain/security-sensitive cases.
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
    |  Risk Engine |
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