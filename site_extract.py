"""Turn Phase 1 report text into structured SiteInfo."""

from llm import MODEL, client
from schemas import SiteInfo

max_chars = 80_000
prompt = """
You are an Environmental Consultant, extracting site information from a Phase 1 report.
Only use the information within the report, if something is missing, report it as 'unknown' or use an empty list.
Keep it factual without making inventions.
"""


def extract_site_info(report_text: str) -> SiteInfo:
    clipped = report_text[:max_chars]
    completion = client.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user",
                "content": (
                    "Extract structured site information from this Phase 1 report text:\n\n"
                    f"{clipped}"
                ),
            },
        ],
        response_format=SiteInfo,
    )
    site_info = completion.choices[0].message.parsed
    if site_info is None:
        raise ValueError("Model did not return parsed SiteInfo")
    return site_info
