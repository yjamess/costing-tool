"""Phase 1 PDF → site JSON → Phase 2 scope lines → deterministic cost."""

from costing import cost_scope
from pdf_extract import extract_pdf_text
from plan_scope import plan_phase2_scope
from rates import load_master_rates
from site_extract import extract_site_info


def main() -> None:
    pdf_path = "docs/5516_Phase 1 Desk Study.pdf"
    rates = load_master_rates()

    text = extract_pdf_text(pdf_path)
    site = extract_site_info(text)
    scope = plan_phase2_scope(site, rates=rates)
    estimate = cost_scope(scope, rates=rates)

    print("=== Site info ===")
    print(site.model_dump_json(indent=2))

    print("\n=== Phase 2 scope (quantities only) ===")
    print(scope.model_dump_json(indent=2))

    print("\n=== Cost estimate (Python + MASTER) ===")
    print(estimate.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
