# ============================================================
# Garuda AI - Observability Tracer
# ============================================================

from datetime import datetime


class GarudaTracer:
    """
    Records every important step in the Garuda AI workflow.

    Each trace entry contains:
        - timestamp
        - component
        - event
        - details
        - reason
        - duration_ms
    """

    def __init__(self):
        self.trace = []

    # ========================================================
    # LOG EVENT
    # ========================================================

    def log(
        self,
        component,
        event,
        details="",
        reason=""
    ):
        """
        Add a structured event to the trace.
        """

        timestamp = datetime.now()

        entry = {
            "timestamp": timestamp.isoformat(
                timespec="milliseconds"
            ),

            "component": component,

            "event": event,

            "details": details,

            "reason": reason,

            "duration_ms": None
        }

        self.trace.append(entry)

        return entry

    # ========================================================
    # START TIMER
    # ========================================================

    def start_timer(self):
        """
        Start a timer for measuring workflow duration.
        """

        return datetime.now()

    # ========================================================
    # CALCULATE DURATION
    # ========================================================

    def calculate_duration(self, start_time):
        """
        Calculate elapsed time in milliseconds.
        """

        elapsed = (
            datetime.now() - start_time
        )

        return round(
            elapsed.total_seconds() * 1000,
            2
        )

    # ========================================================
    # ADD DURATION TO LAST EVENT
    # ========================================================

    def add_duration(
        self,
        start_time
    ):
        """
        Add execution duration to the most recent trace event.
        """

        if not self.trace:
            return

        self.trace[-1]["duration_ms"] = (
            self.calculate_duration(start_time)
        )

    # ========================================================
    # GET TRACE
    # ========================================================

    def get_trace(self):
        """
        Return the complete execution trace.
        """

        return self.trace

    # ========================================================
    # CLEAR TRACE
    # ========================================================

    def clear(self):
        """
        Clear all trace entries.
        """

        self.trace.clear()