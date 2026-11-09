"""Single fail-closed risk policy shared by trading engines."""
from __future__ import annotations
BASE_RISK_PCT = 0.25
A_PLUS_RISK_PCT = 0.50
MIN_VALIDATED_TRADES_FOR_A_PLUS = 30

def risk_pct_for_setup(grade=None, validation_n=0, validation_passed=False):
    """0.50% only for explicitly validated A+ with >=30 OOS trades; otherwise 0.25%."""
    # The validation count is evidence metadata, not user text: accept only a real integer.
    # Reject bools, strings, and fractional values rather than coercing them upward/downward.
    n = validation_n if type(validation_n) is int else 0
    if grade == "A+" and validation_passed is True and n >= MIN_VALIDATED_TRADES_FOR_A_PLUS:
        return A_PLUS_RISK_PCT
    return BASE_RISK_PCT
