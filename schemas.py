"""Structured outputs for the costing pipeline.

SiteInfo  →  Phase2Scope (LLM, quantities only)
Phase2Scope  →  CostEstimate (Python + MASTER rates)
"""

from pydantic import BaseModel, Field


class SiteInfo(BaseModel):
    """Fields the costing pipeline needs from a Phase 1 report."""

    site_current_use: str = Field(
        description="Current use of the site, or 'unknown' if not stated."
    )
    proposed_use: str = Field(
        description="Proposed development/use, or 'unknown' if not stated."
    )
    historical_contamination_sources: list[str] = Field(
        description="Past uses or sources that may cause contamination."
    )
    geology_hydrogeology: str = Field(
        description="Brief geology/hydrogeology summary, or 'unknown'."
    )
    phase_1_recommendations: list[str] = Field(
        description="Phase 1 recommendations relevant to intrusive investigation."
    )


class ScopeLine(BaseModel):
    """One proposed investigation line — quantity only, never a price."""

    ref: str = Field(description="MASTER Item ID, e.g. D.ws_day")
    quantity: float = Field(description="Quantity in the MASTER unit for that ref.")
    rationale: str = Field(
        description="Short reason this line is needed from the Phase 1 info."
    )


class Phase2Scope(BaseModel):
    """Indicative Phase 2 scope as MASTER line items."""

    lines: list[ScopeLine] = Field(description="Proposed bill lines.")
    assumptions: list[str] = Field(
        description="Assumptions made because Phase 1 detail was limited."
    )
    uncertainties: list[str] = Field(
        description="Items needing consultant review before finalising."
    )
    needs_consultant_review: bool = Field(
        description="True if the scope should not be treated as final."
    )
    margin_pct: int = Field(
        default=15,
        description="Commercial margin for THIRD PARTY lines: 10, 15 or 20.",
    )


class CostedLine(BaseModel):
    """A scope line after Python applied MASTER rates."""

    ref: str
    description: str
    unit: str
    cost_class: str
    quantity: float
    unit_sell: float
    line_total: float
    rationale: str


class CostEstimate(BaseModel):
    """Deterministic cost summary — no LLM prices."""

    margin_pct: int
    lines: list[CostedLine]
    subtotal_lustre_fee: float
    subtotal_lustre_exp: float
    subtotal_third_party: float
    grand_total: float
    unknown_refs: list[str] = Field(
        default_factory=list,
        description="Refs the LLM proposed that are not in MASTER.",
    )
