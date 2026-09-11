# ============================================================
# Garuda AI - Tracer Test
# ============================================================

from observability.tracer import GarudaTracer


print()
print("=" * 60)
print("GARUDA AI TRACER TEST")
print("=" * 60)


# ============================================================
# CREATE TRACER
# ============================================================

tracer = GarudaTracer()


# ============================================================
# TEST EVENT
# ============================================================

start_time = tracer.start_timer()

tracer.log(
    component="Test Agent",
    event="STARTED",
    details="Testing tracer",
    reason="Verify structured observability"
)

tracer.add_duration(start_time)


# ============================================================
# GET TRACE
# ============================================================

trace = tracer.get_trace()


print()
print("TRACE:")
print(trace)


# ============================================================
# VALIDATION
# ============================================================

assert len(trace) == 1

assert trace[0]["component"] == "Test Agent"

assert trace[0]["event"] == "STARTED"

assert trace[0]["details"] == "Testing tracer"

assert trace[0]["reason"] == "Verify structured observability"

assert trace[0]["timestamp"] is not None

assert trace[0]["duration_ms"] is not None

assert trace[0]["duration_ms"] >= 0


print()
print("TEST PASSED")
print("Structured tracing and duration measurement work correctly.")


print()
print("=" * 60)
print("END OF TRACER TEST")
print("=" * 60)