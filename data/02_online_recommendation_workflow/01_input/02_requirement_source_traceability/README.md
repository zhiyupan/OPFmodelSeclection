# Source Traceability Materials for Online User Requirements

This directory centrally stores the source materials supporting the authoritative set of 54 natural-language requirements. It belongs to the input layer of the online-recommendation workflow, but its two roles must be distinguished: `../01_user_requirements.csv` is the sole machine input actually read by the GUI, Notebook, and batch Validation; the reports and mirrored paper manifest in this directory support the human construction, review, and explanation of those requirements, and the program does not parse their contents automatically.

## Directory Contents

- `01_enterprise_grid_reports/`: 28 reports published by enterprises, grid operators, market organizations, and international energy organizations, totaling 166,663,995 bytes. They primarily support the human construction and review of R01–R19. The directory's `enterprise_grid_reports_manifest.csv` is the report-level master source manifest and records the official publication page, official PDF, actual download source of the local file, access date, requirement mapping, page number, license, version, and SHA-256.
- `02_paper_corpus_manifest.csv`: a 36-row mirror of the paper manifest corresponding to the 36 PaperModel instances in the knowledge graph. It contains P001–P036, titles, authors, years, DOIs, formal sources, open-access links, license notes, and historical local filenames. It keeps the in-project citations for R14–R16, R19, and M01–M35 within this workflow's source directory; P036 does not yet have a corresponding paper-motivation requirement. The manifest is neither the full text of the papers nor a second knowledge graph.
- The editable authoritative paper manifest is located at `data/01_paper_ingestion_workflow/01_input/01_source_papers/paper_corpus_manifest.csv`. This mirror must be byte-identical to it, and `check_project_paths()` prevents an unsynchronized state from passing preflight checks. The 28 reports remain only in this directory and are no longer duplicated by Validation. The original 13-page secondary summary PDF has been removed because it did not bind individual claims to specific report files and canonical citation entries. Formal traceability is governed by the row-level citation columns in `../01_user_requirements.csv` and the report-level metadata in `01_enterprise_grid_reports/enterprise_grid_reports_manifest.csv`.

Every row of `../01_user_requirements.csv` now directly stores one primary citation: R01–R13 and R17–R18 primarily cite enterprise/grid reports verified page by page; R14–R16 and R19 cite more direct academic papers; and M01–M35 collectively cite P001–P035 in a one-to-one correspondence. P036 is an additional bibliography and knowledge-graph entry and does not yet have a corresponding paper-motivation requirement. The 19 R requirements also contain `report_source_*` fields: 15 reuse their primary report evidence, while R14–R16 and R19 link to page-verified report background marked as non-direct evidence. `enterprise_grid_reports_manifest.csv` is the complete machine-readable index of the 28 reports; the table in this README is only a quick reference.

## Interpreting Evidence Grades

- **A-direct**: the report or paper directly states the core issue represented by the requirement.
- **A-academic**: no enterprise report provides more direct evidence, so an individually verified academic paper serves as the primary citation.
- **B-synthesis**: the report supports the business context, but the specific OPF wording is synthesized by the project rather than quoted from the report.
- **C-background**: the source can serve only as supplementary background and cannot be the requirement's sole provenance.

R14 (data privacy/distributed coordination), R15 (computational speed and online feasibility), R16 (unit-commitment coupling), and R19 (computational scalability for large systems) use P006, P008, P004, and P033 as their respective primary citations. Enterprise-report background material must not be represented as direct OPF evidence for these requirements.

## Index of the 28 Original Reports

| ID | Canonical filename | Organization | Year | Grade | Mapped enterprise requirements | Original filename |
|---|---|---:|---:|:---:|---|---|
| 01 | `01_ENTSO-E_Regional_Coordination_Assessment_Annual_Report_2024.pdf` | ENTSO-E | 2025 (reporting period 2024) | A | R02, R10; supplementary R04, R08, R09, R17 | `2024 ARCA Report.pdf` |
| 02 | `02_Europex_EU_Grids_Package_Comments_2026-02-04.pdf` | Europex | 2026 | A | R01, R17; supplementary R05, R08, R10, R13 | `20260203_Europex-comments-on-Grids-Package.pdf` |
| 03 | `03_Europex_Marginal_Pricing_Statement_2026-03-12.pdf` | Europex | 2026 | A | R13; supplementary R01, R10 | `20261103_Statement_Marginal-Pricing_Final-2.pdf` |
| 04 | `04_ENTSO-E_Heavy_Duty_EVs_and_Power_System_2023-10.pdf` | ENTSO-E | 2023 | B | R05, R07, R12, R17, R18 | `231006_ENTSO-E_Position Paper_Deployment of Heavy-Duty EVs and Impact on the Power System.pdf` |
| 05 | `05_ENTSO-E_EU_Grid_Action_Plan_Recommendations_2023-11-16.pdf` | ENTSO-E | 2023 | B | R01, R02, R05, R08, R09, R10, R17 | `231116_ENTSO-E Position Paper on Grids.pdf` |
| 06 | `06_ENTSO-E_Flexibility_from_RES_Position_2025-11.pdf` | ENTSO-E | 2025 | B | R03, R05, R08, R09, R17 | `251118_Entso-e_flexibility_from_RES_Position_Paper.pdf` |
| 07 | `07_ENTSO-E_Flexibility_from_RES_Report_2025-11.pdf` | ENTSO-E | 2025 | A | R03, R09, R10; supplementary R12, R17 | `251118_entso-e_flexibility_from_RES_Report.pdf` |
| 08 | `08_Ofgem_Demand_Connections_Update_2025-11-06.pdf` | Ofgem | 2025 | B | R06, R07, R09, R17 | `Demand connections update.pdf` |
| 09 | `09_IEA_Renewables_2025_Documentation_Corrigendum.pdf` | IEA | 2025 (revised 2026-01-07) | C | Renewables 2025 data-product documentation; not mapped independently | `Documentation-IEAMarketReportSeriesRenewables2025_Corrigendum20260107.pdf` |
| 10 | `10_IEA_Electricity_2026.pdf` | IEA | 2026 | A | R06, R07, R08; supplementary R01, R03, R05, R09, R10, R12, R13, R17 | `Electricity_2026.pdf` |
| 11 | `11_ENTSO-E_European_Grids_Package_Position_2026-02-27.pdf` | ENTSO-E | 2026 | A | R17; supplementary R10 | `ENTSO-E Position on European Grids Package.pdf` |
| 12 | `12_ENTSO-E_Annual_Report_2025.pdf` | ENTSO-E | 2026 (reporting period 2025) | A | R12; supplementary R01, R02, R03, R04, R09, R10, R13 | `ENTSO-E Report GS V12.pdf` (the local copy is a consultation draft) |
| 13 | `13_ENTSO-E_Annual_Report_2024.pdf` | ENTSO-E | 2025 (reporting period 2024) | B | R01, R02, R03, R04, R05, R08, R09, R10, R13, R17 | `ENTSO-E_Annual-Report_2024.pdf` |
| 14 | `14_ENTSO-E_Annual_Work_Programme_2026.pdf` | ENTSO-E | 2025 (2026 work programme) | B | R02, R04, R08, R09, R10, R13, R17 | `ENTSO-E_AWP 2026_.pdf` |
| 15 | `15_ENTSO-E_Strategic_Roadmap_2024.pdf` | ENTSO-E | 2024 | B | R02, R03, R04, R05, R08, R10, R13, R17 | `entso-e_strategic_roadmap_WEB_240215.pdf` |
| 16 | `16_ENTSO-E_Market_Report_2025.pdf` | ENTSO-E | 2025 | B | R01, R04, R09, R10, R13, R17 | `entso_e_Market_report_2025_250709_c2e8192c2c.pdf` |
| 17 | `17_ENTSO-E_Market_and_Balancing_Reports_2024_Webinar.pdf` | ENTSO-E | 2024 | C | Supplementary R04, R09, R10, R13, R17 | `ENTSO_E_Webinar_Market_and_Balancing_Reports_2024_4b8db8d767.pdf` |
| 18 | `18_ENTSO-E_Market_Design_and_System_Operation_Vision_2030.pdf` | ENTSO-E | 2019 (vision target 2030) | B | R01, R02, R03, R04, R08, R09, R10, R11, R12, R13, R17, R18 | `entsoe_fp_vision_2030_web.pdf` |
| 19 | `19_ENTSO-E_ERAA_2025_Annex1_Input_Data_and_Assumptions.pdf` | ENTSO-E | 2025 | B | R03, R09, R10, R12 | `ERAA_2025_Annex1_InputData_ENTSOEProposal_Dec2025.pdf` |
| 20 | `20_ENTSO-E_ERAA_2025_Executive_Report.pdf` | ENTSO-E | 2025 | A | R09; supplementary R03, R08, R10; computational-scale background for R19 | `ERAA_2025_ExecutiveReport_ENTSOEProposal_Dec2025.pdf` |
| 21 | `21_BDEW_Renewable_Expansion_and_System_Efficiency_2025-08-22.pdf` | BDEW | 2025 | B | R01, R03, R05, R12, R17 | `erneuerbare-energien-ausbauziele-beibehalten-systemeffizienter-ausbauen.pdf` |
| 22 | `22_ENTSO-E_Spain_Portugal_Grid_Incident_Final_Report_2026-03-20.pdf` | ENTSO-E | 2026 | A | R11; supplementary R02, R04, R08, R15, R16 | `Final Report on the Grid Incident in Spain and Portugal on 28 April 2025.pdf` |
| 23 | `23_IEA_Global_EV_Outlook_2025_Policy_Explorer.pdf` | IEA | 2025 | C | Weak supplementary support for R05, R07 | `GlobalEVOutlook2025PolicyExplorer.pdf` |
| 24 | `24_BDEW_Distribution_Grid_Connections.pdf` | BDEW | 2026 | B | R06, R07, R12, R17 | `netzanschluss-verteilnetz.pdf` |
| 25 | `25_IEA_Renewables_2025.pdf` | IEA | 2025 | A | R05; supplementary R01, R03, R08, R09, R12, R17 | `Renewables2025.pdf` |
| 26 | `26_EU_DSO_Entity_Distributed_Flexibility_Practices_2026-02.pdf` | EU DSO Entity | 2026 | A | R18; supplementary R04, R13, R14, R17 | `Report-on-Distributed-Flexibility-Practices-Markets-for-Local-Services-2.pdf` |
| 27 | `27_IEA_World_Energy_Outlook_2024.pdf` | IEA | 2024 | B | R01, R02, R03, R05, R06, R07, R08, R09, R12, R17 | `WorldEnergyOutlook2024.pdf` |
| 28 | `28_IEA_World_Energy_Outlook_2025.pdf` | IEA | 2025 | B/C | Supplementary R02, R03, R05, R06, R07, R08; background only for R19, not a primary citation | `WorldEnergyOutlook2025.pdf` |

## Consumers of These Files

The current GUI and Python code do not automatically parse the contents of these 28 reports or the paper manifest to generate recommendations. Online recommendation actually reads the four requirement fields in `../01_user_requirements.csv`; the citation and report-source columns attached to the same row support human verification. The requirement-table loader validates the ordering of all 54 entries, the 19 report mappings, URLs, Boolean flags, and local file paths. The project path preflight separately checks that both paper manifests exist and are byte-identical. Recommendation scoring consistently reads `data/03_validation/01_input/01_recommendation_human_gold/recommendation_human_gold_54_requirements.csv`. When updating the paper bibliography in the future, first edit the authoritative manifest in workflow 01 and synchronize this mirror. When modifying R01–R19 or M01–M35, also update the authoritative 54-requirement table and the unified Gold data in sync.
