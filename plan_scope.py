"""LLM proposes Phase 2 scope as MASTER refs + quantities only.

Freedom is by MASTER *section* (tab), not a hand-picked item list.

- INTERPRETIVE_SECTIONS: model may use any Ref in those sections.
- Widen the set when you trust the planner more (e.g. add H, I, J, E).
- Prices still never come from the LLM — only refs + quantities.
"""

from llm import MODEL, client
from rates import RateLine, load_master_rates
from schemas import Phase2Scope, SiteInfo

# MASTER section codes the model may use freely (all lines in that tab).
INTERPRETIVE_SECTIONS: frozenset[str] = frozenset(
    {
        "A",  # Consulting Fees
        "B",  # Mobilisation
        "C",  # Cable Percussion Boreholes
        "D",  # Window Sampling
        "F",  # Monitoring Wells
        "G",  # Trial Pitting & BRE Soakage
        "K",  # Miscellaneous Items
        "E",  # Rotary Coring
        "H",  # Geotechnical Testing
        "I",  # Soils Chemical Testing
        "J",  # Waters Chemical Testing
    }
)

PROMPT = """
You are an environmental consultant proposing an indicative Phase 2 SI scope
for Lustre Consulting.

You may ONLY use Item IDs (refs) from the allowed catalogue below.
Those refs come from the MASTER rate sections marked interpretive for this run.
Propose quantities in each item's unit.
Do NOT invent prices, and do NOT invent new refs outside the catalogue.
If information is weak, set needs_consultant_review=true and list uncertainties.
Use margin_pct=15 unless the site clearly warrants 10 or 20.

Commercial restraint:
- Prefer one primary investigation method unless Phase 1 clearly needs two
  (e.g. do not default to both a full window-sample programme and a full
  cable-percussion programme).
- Prefer packaged lab suites over stacking the same suite plus many single
  determinands that the suite already covers. Add single tests only where
  Phase 1 identifies a specific extra risk.
- Keep sample / test counts proportional to the number of exploratory holes
  and monitoring rounds — provisional allowances, not exhaustive testing.
- Put optional or design-led extras (e.g. CBR, extra attendance, specialist
  surveys) in uncertainties or assumptions unless Phase 1 clearly requires
  them in the core bill.
- Include practical prelims the Phase 1 implies (H&S, hardstanding coring /
  breaker access, utility plans/clearance, supervision, monitoring, reporting)
  without padding rig-days or kit hire.
- Prefer a lean, consultant-reviewable first estimate. If unsure between a
  smaller and larger quantity, choose the smaller and flag it under
  uncertainties.
"""


def refs_for_interpretive_sections(
    rates: dict[str, RateLine],
    sections: frozenset[str] = INTERPRETIVE_SECTIONS,
) -> list[str]:
    """Return every MASTER ref whose section_code is interpretive."""
    return sorted(
        ref
        for ref, line in rates.items()
        if line.section_code in sections
    )


def _catalogue_for_prompt(
    rates: dict[str, RateLine],
    allowed_refs: list[str],
) -> str:
    blocks: list[str] = []
    current_section: str | None = None

    for ref in allowed_refs:
        line = rates[ref]
        label = f"{line.section_code} — {line.section}"
        if label != current_section:
            current_section = label
            blocks.append(f"\n### {label}")
        blocks.append(
            f"- {line.ref} | {line.unit} | {line.group} | {line.description}"
        )

    return "\n".join(blocks).strip()


def plan_phase2_scope(
    site: SiteInfo,
    rates: dict[str, RateLine] | None = None,
    sections: frozenset[str] | None = None,
) -> Phase2Scope:
    """Ask the LLM for MASTER refs + quantities from SiteInfo."""
    catalogue = rates if rates is not None else load_master_rates()
    open_sections = sections if sections is not None else INTERPRETIVE_SECTIONS
    allowed_refs = refs_for_interpretive_sections(catalogue, open_sections)
    if not allowed_refs:
        raise ValueError(f"No MASTER lines for sections: {sorted(open_sections)}")

    allowed_text = _catalogue_for_prompt(catalogue, allowed_refs)
    allowed_set = set(allowed_refs)

    completion = client.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": PROMPT},
            {
                "role": "user",
                "content": (
                    "Allowed catalogue by interpretive MASTER section "
                    "(ref | unit | group | description):\n"
                    f"{allowed_text}\n\n"
                    "Site information JSON:\n"
                    f"{site.model_dump_json(indent=2)}\n\n"
                    "Propose a Phase 2 scope using only those refs."
                ),
            },
        ],
        response_format=Phase2Scope,
    )
    scope = completion.choices[0].message.parsed
    if scope is None:
        raise ValueError("Model did not return parsed Phase2Scope")

    # Defence in depth: drop anything outside open sections.
    scope.lines = [line for line in scope.lines if line.ref in allowed_set]
    return scope
