# Vacancy Reporting - VIC (Fabric Delivery Pack)

This repository delivers a Microsoft Fabric-based vacancy turnaround and reporting pipeline for Victoria (VIC), replacing manual turnaround calculations with a conformed, Repeatable, and auditable Medallion Architecture.

---

## 📂 Repository Organization

The repository has been structured in a clean, logical manner to make onboarding and maintenance straightforward:

```text
vacant_calc/
├── AGENTS.md                    # System instructions for LLM and coding agents
├── Vacant Calc.xlsx             # Source Excel logic and benchmark workbook
├── notebooks/                   # Medallion Architecture notebooks (Spark / Python)
│   ├── vac_reporting_vic_bronze_notebook.py
│   ├── vac_reporting_vic_silver_notebook.py
│   ├── vac_reporting_vic_dimensions_notebook.py
│   ├── vac_reporting_vic_gold_notebook.py
│   └── vac_reporting_vic_parameter_maintenance_notebook.py
└── docs/                        # Complete design, semantic model, and page guidelines
    ├── project_overview.md       # Scope, logic rules, and medallion mapping
    ├── fabric_implementation.md  # Step-by-step deploy, validation, and refresh guide
    ├── semantic_model.md         # Relationships, exposed fields, and conformed DAX measures
    ├── report_pages.md           # Visual page layouts (KPI cards, charts, detail tables)
    ├── tables.md                 # TechOne source tables and conformed mappings
    └── assets/                   # High-fidelity visual mockup and icon design assets
        ├── vacancy_detail_mockup.png
        ├── vacancy_kpi_icons.png
        ├── vacancy_count_icon.png
        ├── vacancy_days_icon.png
        ├── tenantable_days_icon.png
        ├── untenantable_days_icon.png
        └── benchmark_achievement_icon.png
```

---

## 📖 Navigation Guide

Before modifying any data logic or report layouts, please read the documentation in this conformed order:

1. **[Project Overview](file:///Users/abdulla/Documents/vacant_calc/docs/project_overview.md)**
   * Scope of the VIC solution, key stakeholders, and the core boundary rules (e.g., how daily vacancy and void durations are strictly counted).
2. **[Fabric Implementation Guide](file:///Users/abdulla/Documents/vacant_calc/docs/fabric_implementation.md)**
   * Deployment sequencing, parameter configurations, and the conformed pipeline refresh process.
3. **[Semantic Model Guide](file:///Users/abdulla/Documents/vacant_calc/docs/semantic_model.md)**
   * Fabric-to-Power BI schema relationships, fields to expose/hide, and conformed DAX measures for benchmark compliance.
4. **[Report Build Guide](file:///Users/abdulla/Documents/vacant_calc/docs/report_pages.md)**
   * Detailed layouts for all 6 pages in the report: Summary, Vacancy Detail (enhanced with visual KPI cards, reference labels, and distribution charts), Audit, Config, Property Trace, and Exception Monitor.
5. **[Source Table Guide](file:///Users/abdulla/Documents/vacant_calc/docs/tables.md)**
   * Standard definitions and properties for Bronze stage columns sourced from TechOne (`Property`, `Tenancy`, `Void`, and `Keys`).

---

## 🎨 Visual Assets & Design Mockups

High-quality assets for constructing modern, professional, and glassmorphic Power BI layouts are stored in the conformed assets folder:
* **[Vacancy Detail Page UI Mockup](file:///Users/abdulla/Documents/vacant_calc/docs/assets/vacancy_detail_mockup.png):** Visual representation of the enhanced split-screen page layout.
* **[KPI Card Glowing Icons Set](file:///Users/abdulla/Documents/vacant_calc/docs/assets/vacancy_kpi_icons.png):** The complete outline icon sheet.
* **[Individual KPI Icons Directory](file:///Users/abdulla/Documents/vacant_calc/docs/assets/):** Separate PNG files for each individual metric card (Vacancy Count, Vacancy Days, Tenantable Days, Untenantable Days, and Benchmark Achievement).
