# Phase 2 Costing Agent

A learning-focused FAC project for Lustre Consulting.

The goal is to build an agent that reads a Phase 1 Desk Study, extracts the information relevant to intrusive investigation, proposes a structured Phase 2 scope of works, and eventually calculates an indicative cost using deterministic rates.

## Core principle

The LLM decides **what investigation may be required**.

Python decides **what that investigation costs**.

The model should never invent prices or perform uncontrolled costing.

## Initial architecture

```text
Phase 1 PDF
    ↓
Report extraction
    ↓
Structured site information
    ↓
Phase 2 planning agent
    ↓
Structured scope of works
    ↓
Deterministic costing engine
    ↓
Consultant-reviewable estimate
```

## Phase 1: Report extraction

Start with one existing Phase 1 PDF.

Extract a small structured representation:

```python
{
    "site_current_use": "",
    "proposed_use": "",
    "historical_contamination_sources": [],
    "geology_hydrogeology": "",
    "phase_1_recommendations": []
}
```

The first milestone is simply:

> Phase 1 PDF in → valid structured site information out.

Do not build costing or a UI yet.

## Phase 2: Investigation planning

Once extraction works, pass the structured site information to an LLM and have it generate a strict Phase 2 scope.

Possible fields include:

```python
{
    "boreholes": 0,
    "borehole_depth_m": null,
    "monitoring_wells": 0,
    "soil_samples": 0,
    "lab_suites": [],
    "groundwater_monitoring": false,
    "assumptions": [],
    "uncertainties": []
}
```

The model should explicitly return `unknown` or flag consultant review when the Phase 1 report does not contain enough information.

## Phase 3: Costing

Create a separate rate table in Python.

For example:

```python
rates = {
    "borehole": 350,
    "monitoring_well": 200,
    "soil_sample": 80
}
```

The costing engine multiplies quantities by known rates and calculates subtotals, allowances and contingency.

The LLM does not generate prices.

## Phase 4: Agent harness

Once the basic pipeline works, turn the planner into a tool-using agent.

Possible tools:

```python
search_report()
get_report_section()
get_csm()
lookup_cost_item()
calculate_cost()
```

The agent should decide when it needs additional information rather than receiving the entire report in one prompt.

## Phase 5: Evaluation

Eventually use real historical Lustre projects containing:

* Phase 1 report
* actual Phase 2 scope/proposal
* real project rates

Compare the agent's proposed scope against the consultant-created scope.

Useful metrics include:

* required investigation items identified
* critical omissions
* unnecessary investigation items
* quantity differences
* cost variance
* uncertainty handling

For now, any expected Phase 2 scope is development-only and must not be treated as consultant-validated ground truth.

## Learning goals

Build this progressively rather than relying on an agent framework.

The intended learning sequence is:

```text
PDF/text handling
→ structured LLM output
→ schema design
→ decomposition
→ deterministic Python functions
→ tool calling
→ agent loop
→ evaluation
```

Prefer plain Python initially so every part of the harness is understandable.

Do not introduce LangGraph or other orchestration frameworks until the underlying agent loop is understood.

## Current milestone

Use an existing final Lustre Phase 1 report, such as Ninn Lane or Mems.

Build:

```text
Phase 1 PDF
    ↓
extract text
    ↓
LLM
    ↓
structured site JSON
```

Nothing more until this works reliably.
