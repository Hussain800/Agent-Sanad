"""Rule 2 — period compliance, per path (see PRD 3.4)."""
import math
from backend.schemas import Case, PolicyConfig


def update_months_ok(case: Case, policy: PolicyConfig, additional_months: int) -> bool:
    """UPDATE_INSTALLMENT: the catch-up surcharge must finish within the remaining term."""
    if not policy.respect_approved_period:
        return True
    return additional_months <= case.loan.remaining_term_months


def transfer_period_ok(case: Case, policy: PolicyConfig) -> bool:
    """TRANSFER_ARREARS: appending arrears at the end may push past the original end date.
    Prototype (remaining_term basis): months to clear arrears at the current installment
    must not extend beyond the remaining term."""
    if not policy.respect_approved_period:
        return True
    emi = case.loan.current_installment_aed
    if emi <= 0:
        return False
    months_to_clear = math.ceil(case.arrears.arrears_amount_aed / emi)
    return months_to_clear <= case.loan.remaining_term_months
