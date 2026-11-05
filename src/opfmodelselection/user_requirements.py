"""Canonical natural-language requirements shared by recommendation and validation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import ONLINE_USER_REQUIREMENTS_CSV, PROJECT_ROOT


USER_REQUIREMENT_COLUMNS = [
    "requirement_id",
    "requirement_group",
    "requirement_name",
    "requirement_text",
]
CITATION_REQUIRED_COLUMNS = [
    "citation_key",
    "citation_type",
    "citation_authors_or_organization",
    "citation_title",
    "citation_year",
    "citation_official_url",
    "citation_local_reference",
    "citation_page_or_section",
    "citation_evidence_level",
    "citation_is_direct",
    "citation_license",
    "citation_evidence_summary",
]
CITATION_OPTIONAL_VALUE_COLUMNS = [
    "citation_doi",
    "citation_open_access_url",
]
REPORT_SOURCE_COLUMNS = [
    "report_source_key",
    "report_source_role",
    "report_source_organization",
    "report_source_title",
    "report_source_year",
    "report_source_official_url",
    "report_source_pdf_url",
    "report_source_local_file_source_url",
    "report_source_accessed_date",
    "report_source_local_reference",
    "report_source_page_or_section",
    "report_source_evidence_level",
    "report_source_is_direct",
    "report_source_license",
    "report_source_license_url",
    "report_source_evidence_summary",
]
SUPPLEMENTARY_REPORT_REQUIREMENT_IDS = {"R14", "R15", "R16", "R19"}
EXPECTED_USER_REQUIREMENT_IDS = [
    *[f"R{index:02d}" for index in range(1, 20)],
    *[f"M{index:02d}" for index in range(1, 36)],
]


def load_user_requirements(
    path: Path = ONLINE_USER_REQUIREMENTS_CSV,
) -> list[dict[str, str]]:
    """Load and validate the one canonical 54-case requirement table."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Canonical user-requirement CSV not found: {path}")

    table = pd.read_csv(path, dtype=str, keep_default_na=False)
    required_value_columns = USER_REQUIREMENT_COLUMNS + CITATION_REQUIRED_COLUMNS
    expected_columns = (
        required_value_columns
        + CITATION_OPTIONAL_VALUE_COLUMNS
        + REPORT_SOURCE_COLUMNS
    )
    missing_columns = [column for column in expected_columns if column not in table.columns]
    if missing_columns:
        raise ValueError(
            f"Canonical user-requirement CSV is missing columns {missing_columns}: {path}"
        )

    for column in expected_columns:
        table[column] = table[column].astype(str).str.strip()
    if table[required_value_columns].eq("").any().any():
        raise ValueError(
            "Canonical user-requirement CSV contains empty requirement or citation "
            f"cells: {path}"
        )

    enterprise_mask = table["requirement_id"].str.startswith("R")
    motivation_mask = table["requirement_id"].str.startswith("M")
    if table.loc[enterprise_mask, REPORT_SOURCE_COLUMNS].eq("").any().any():
        raise ValueError(
            "Canonical enterprise requirements contain empty report-source cells: "
            f"{path}"
        )
    if table.loc[motivation_mask, REPORT_SOURCE_COLUMNS].ne("").any().any():
        raise ValueError(
            "Canonical motivation requirements must not contain enterprise report "
            f"source values: {path}"
        )

    invalid_urls = table.loc[
        ~table["citation_official_url"].str.match(r"^https?://", case=False),
        ["requirement_id", "citation_official_url"],
    ]
    if not invalid_urls.empty:
        raise ValueError(
            "Canonical user-requirement CSV contains invalid citation URLs: "
            f"{invalid_urls.to_dict(orient='records')}"
        )

    invalid_direct_flags = table.loc[
        ~table["citation_is_direct"].str.lower().isin({"true", "false"}),
        ["requirement_id", "citation_is_direct"],
    ]
    if not invalid_direct_flags.empty:
        raise ValueError(
            "Canonical user-requirement CSV contains invalid citation_is_direct "
            f"values: {invalid_direct_flags.to_dict(orient='records')}"
        )

    invalid_report_urls = table.loc[
        enterprise_mask
        & (
            ~table["report_source_official_url"].str.match(
                r"^https?://", case=False
            )
            | ~table["report_source_pdf_url"].str.match(r"^https?://", case=False)
            | ~table["report_source_local_file_source_url"].str.match(
                r"^https?://", case=False
            )
            | ~table["report_source_license_url"].str.match(
                r"^https?://", case=False
            )
        ),
        [
            "requirement_id",
            "report_source_official_url",
            "report_source_pdf_url",
            "report_source_local_file_source_url",
            "report_source_license_url",
        ],
    ]
    if not invalid_report_urls.empty:
        raise ValueError(
            "Canonical enterprise requirements contain invalid report-source URLs: "
            f"{invalid_report_urls.to_dict(orient='records')}"
        )

    invalid_report_flags = table.loc[
        enterprise_mask
        & ~table["report_source_is_direct"].str.lower().isin({"true", "false"}),
        ["requirement_id", "report_source_is_direct"],
    ]
    if not invalid_report_flags.empty:
        raise ValueError(
            "Canonical enterprise requirements contain invalid "
            "report_source_is_direct values: "
            f"{invalid_report_flags.to_dict(orient='records')}"
        )

    invalid_report_roles = table.loc[
        enterprise_mask
        & ~table["report_source_role"].isin(
            {"primary", "supplementary-background"}
        ),
        ["requirement_id", "report_source_role"],
    ]
    if not invalid_report_roles.empty:
        raise ValueError(
            "Canonical enterprise requirements contain invalid report-source roles: "
            f"{invalid_report_roles.to_dict(orient='records')}"
        )

    supplementary_ids = set(
        table.loc[
            table["report_source_role"].eq("supplementary-background"),
            "requirement_id",
        ]
    )
    if supplementary_ids != SUPPLEMENTARY_REPORT_REQUIREMENT_IDS:
        raise ValueError(
            "Supplementary enterprise-report mappings must be exactly "
            f"{sorted(SUPPLEMENTARY_REPORT_REQUIREMENT_IDS)}; found "
            f"{sorted(supplementary_ids)}"
        )

    invalid_primary_report_keys = table.loc[
        enterprise_mask
        & table["report_source_role"].eq("primary")
        & table["citation_key"].ne(table["report_source_key"]),
        ["requirement_id", "citation_key", "report_source_key"],
    ]
    if not invalid_primary_report_keys.empty:
        raise ValueError(
            "Primary enterprise report sources must match the row citation key: "
            f"{invalid_primary_report_keys.to_dict(orient='records')}"
        )

    missing_local_references = []
    for row in table[["requirement_id", "citation_local_reference"]].to_dict(
        orient="records"
    ):
        reference_path = row["citation_local_reference"].split("#", 1)[0]
        candidate = Path(reference_path)
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        if not candidate.exists():
            missing_local_references.append(
                {
                    "requirement_id": row["requirement_id"],
                    "citation_local_reference": row["citation_local_reference"],
                }
            )
    if missing_local_references:
        raise FileNotFoundError(
            "Canonical user-requirement citations reference missing local sources: "
            f"{missing_local_references}"
        )

    missing_report_references = []
    for row in table.loc[
        enterprise_mask, ["requirement_id", "report_source_local_reference"]
    ].to_dict(orient="records"):
        candidate = Path(row["report_source_local_reference"])
        if not candidate.is_absolute():
            candidate = PROJECT_ROOT / candidate
        if not candidate.exists():
            missing_report_references.append(row)
    if missing_report_references:
        raise FileNotFoundError(
            "Canonical enterprise requirements reference missing report sources: "
            f"{missing_report_references}"
        )

    requirement_ids = table["requirement_id"].tolist()
    if requirement_ids != EXPECTED_USER_REQUIREMENT_IDS:
        raise ValueError(
            "Canonical user-requirement IDs/order must be exactly R01-R19 followed "
            f"by M01-M35; found {requirement_ids}"
        )
    for column in ("requirement_name", "requirement_text"):
        duplicate_values = table.loc[table[column].duplicated(), column].tolist()
        if duplicate_values:
            raise ValueError(
                f"Canonical user-requirement CSV contains duplicate {column}: "
                f"{duplicate_values}"
            )

    return table[USER_REQUIREMENT_COLUMNS].to_dict(orient="records")


USER_REQUIREMENTS: list[dict[str, str]] = load_user_requirements()
USER_REQUIREMENTS_BY_ID = {
    requirement["requirement_id"]: requirement
    for requirement in USER_REQUIREMENTS
}
