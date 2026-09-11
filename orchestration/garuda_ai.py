# ============================================================
# Garuda AI - Main Orchestrator
# ============================================================

from agents.fraud_analyzer import analyze_message
from agents.risk_engine import analyze_risk
from agents.investigation_agent import investigate
from agents.explanation_agent import generate_explanation

from safety.safety_critic import check_safety
from safety.escalation import create_escalation

from observability.tracer import GarudaTracer


async def analyze_with_garuda(message: str) -> dict:

    # ========================================================
    # CREATE TRACE
    # ========================================================

    tracer = GarudaTracer()

    # Overall pipeline timer
    pipeline_start = tracer.start_timer()

    tracer.log(
        component="Garuda AI",
        event="STARTED",
        details="Garuda AI analysis pipeline started",
        reason="New fraud analysis request"
    )

    # ========================================================
    # STEP 1 — INTAKE AGENT
    # ========================================================

    intake_start = tracer.start_timer()

    tracer.log(
        component="Intake Agent",
        event="STARTED",
        details="User message received",
        reason="New fraud analysis request"
    )

    # Intake currently performs message acceptance.
    # More preprocessing can be added here later.

    tracer.log(
        component="Intake Agent",
        event="COMPLETED",
        details="Input accepted",
        reason="Message ready for fraud analysis"
    )

    tracer.add_duration(intake_start)

    # ========================================================
    # STEP 2 — FRAUD ANALYSIS AGENT
    # ========================================================

    analysis_start = tracer.start_timer()

    analysis = analyze_message(message)

    fraud_type = analysis["fraud_type"]
    signals = analysis["signals"]
    attacker_goal = analysis["attacker_goal"]
    confidence = analysis["confidence"]

    tracer.log(
        component="Fraud Analysis Agent",
        event="COMPLETED",
        details=(
            f"Fraud Type: {fraud_type} | "
            f"Confidence: {confidence}"
        ),
        reason="Semantic analysis completed by Qwen3-4B"
    )

    tracer.add_duration(analysis_start)

    # ========================================================
    # STEP 3 — RISK ENGINE
    # ========================================================

    risk_start = tracer.start_timer()

    risk = analyze_risk(
        signals,
        fraud_type
    )

    risk_score = risk["risk_score"]
    risk_level = risk["risk_level"]

    tracer.log(
        component="Risk Engine",
        event="COMPLETED",
        details=(
            f"Risk: {risk_score} | "
            f"Level: {risk_level}"
        ),
        reason="Risk calculated from fraud type and detected signals"
    )

    tracer.add_duration(risk_start)

    # ========================================================
    # STEP 4 — INVESTIGATION AGENT START
    # ========================================================

    investigation_start = tracer.start_timer()

    tracer.log(
        component="Investigation Agent",
        event="STARTED",
        details="Preparing fraud intelligence investigation",
        reason="Ground the AI analysis with trusted knowledge"
    )

    # ========================================================
    # STEP 5 — MCP TOOL CALL
    # ========================================================

    mcp_start = tracer.start_timer()

    tracer.log(
        component="MCP Tool",
        event="TOOL_CALL",
        details="scam_intelligence",
        reason="Retrieve trusted fraud intelligence"
    )

    # ========================================================
    # STEP 6 — INVESTIGATION
    # ========================================================

    investigation = await investigate(
        message,
        fraud_type,
        signals
    )

    tracer.add_duration(mcp_start)

    # ========================================================
    # STEP 7 — RAG RETRIEVAL
    # ========================================================

    rag_start = tracer.start_timer()

    investigation_results = investigation.get(
        "results",
        []
    )

    tracer.log(
        component="RAG",
        event="RETRIEVED",
        details=(
            f"{len(investigation_results)} "
            f"evidence chunks"
        ),
        reason="Ground the analysis with retrieved evidence"
    )

    tracer.add_duration(rag_start)

    # ========================================================
    # STEP 8 — INVESTIGATION AGENT COMPLETE
    # ========================================================

    tracer.log(
        component="Investigation Agent",
        event="COMPLETED",
        details="Investigation completed",
        reason="MCP tool returned fraud intelligence"
    )

    tracer.add_duration(investigation_start)

    # ========================================================
    # STEP 9 — SAFETY CRITIC
    # ========================================================

    safety_start = tracer.start_timer()

    safety = check_safety(
        confidence=confidence,
        risk_score=risk_score,
        rag_results=investigation,
        user_message=message,
        fraud_type=fraud_type
    )

    tracer.log(
        component="Safety Critic",
        event=safety["decision"],
        details=(
            f"Safe: {safety['safe']} | "
            f"Reasons: {safety['reasons']}"
        ),
        reason=(
            "Confidence, grounding, risk and "
            "prompt-injection checks"
        )
    )

    tracer.add_duration(safety_start)

    # ========================================================
    # STEP 10 — ESCALATION
    # ========================================================

    if safety["decision"] == "ESCALATE":

        escalation_start = tracer.start_timer()

        escalation = create_escalation(
            user_message=message,
            risk_score=risk_score,
            confidence=confidence,
            reasons=safety["reasons"],
            analysis=analysis,
            investigation=investigation,
            safety=safety,
            trace=tracer.get_trace()
        )

        tracer.log(
            component="Escalation",
            event="ESCALATED",
            details="Case routed for further verification",
            reason=", ".join(safety["reasons"])
        )

        tracer.add_duration(escalation_start)

        # Final pipeline timing
        tracer.log(
            component="Garuda AI",
            event="FINAL",
            details="ESCALATED",
            reason="Safety Critic blocked normal completion"
        )

        tracer.add_duration(pipeline_start)

        return {
            "status": "ESCALATED",
            "analysis": analysis,
            "risk": risk,
            "investigation": investigation,
            "safety": safety,
            "escalation": escalation,
            "trace": tracer.get_trace()
        }

    # ========================================================
    # STEP 11 — EXPLANATION AGENT
    # ========================================================

    explanation_start = tracer.start_timer()

    explanation = generate_explanation(
        fraud_type=fraud_type,
        signals=signals,
        attacker_goal=attacker_goal,
        risk_score=risk_score,
        risk_level=risk_level,
        confidence=confidence,
        investigation=investigation
    )

    tracer.log(
        component="Explanation Agent",
        event="COMPLETED",
        details="Final explanation generated",
        reason="Safety Critic approved the analysis"
    )

    tracer.add_duration(explanation_start)

    # ========================================================
    # STEP 12 — FINAL RESULT
    # ========================================================

    tracer.log(
        component="Garuda AI",
        event="FINAL",
        details=(
            f"{fraud_type} | "
            f"{risk_level} | "
            f"Risk {risk_score}"
        ),
        reason="All required analysis stages completed"
    )

    # Calculate total pipeline duration
    tracer.add_duration(pipeline_start)

    # ========================================================
    # RETURN COMPLETE RESULT
    # ========================================================

    return {
        "status": "COMPLETED",
        "analysis": analysis,
        "risk": risk,
        "investigation": investigation,
        "safety": safety,
        "explanation": explanation,
        "trace": tracer.get_trace()
    }