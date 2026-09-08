"""Deterministic costing against the MASTER rate library.

The LLM proposes refs + quantities. This module owns all money maths.
"""

from rates import RateLine, load_master_rates, sell_rate
from schemas import CostEstimate, CostedLine, Phase2Scope


def cost_scope(
    scope: Phase2Scope,
    rates: dict[str, RateLine] | None = None,
) -> CostEstimate:
    """Multiply scope quantities by MASTER sell rates.

    Args:
        scope: Proposed lines (refs + quantities only).
        rates: Optional pre-loaded MASTER catalogue.

    Returns:
        CostEstimate with line totals and class subtotals.
    """
    catalogue = rates if rates is not None else load_master_rates()
    margin = scope.margin_pct
    if margin not in (10, 15, 20):
        raise ValueError("scope.margin_pct must be 10, 15 or 20")

    costed: list[CostedLine] = []
    unknown: list[str] = []
    fee = exp = third = 0.0

    for item in scope.lines:
        ref = item.ref.strip()
        line = catalogue.get(ref)
        if line is None:
            unknown.append(ref)
            continue

        unit_sell = sell_rate(line, margin)
        total = round(item.quantity * unit_sell, 2)

        costed.append(
            CostedLine(
                ref=line.ref,
                description=line.description,
                unit=line.unit,
                cost_class=line.cost_class,
                quantity=item.quantity,
                unit_sell=unit_sell,
                line_total=total,
                rationale=item.rationale,
            )
        )

        if line.cost_class == "LUSTRE FEE":
            fee += total
        elif line.cost_class == "LUSTRE EXP":
            exp += total
        elif line.cost_class == "THIRD PARTY":
            third += total
        else:
            raise ValueError(f"Unknown cost_class on {line.ref}: {line.cost_class!r}")

    fee = round(fee, 2)
    exp = round(exp, 2)
    third = round(third, 2)

    return CostEstimate(
        margin_pct=margin,
        lines=costed,
        subtotal_lustre_fee=fee,
        subtotal_lustre_exp=exp,
        subtotal_third_party=third,
        grand_total=round(fee + exp + third, 2),
        unknown_refs=unknown,
    )
