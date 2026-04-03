# Documentation Index

This folder contains the working delivery documentation for the VIC vacancy reporting solution.

## Read In This Order

1. `project_overview.md`
   Purpose, scope, confirmed business rules, and delivery boundaries.
2. `fabric_implementation.md`
   End-to-end Fabric build steps and operational deployment guidance.
3. `semantic_model.md`
   Model layout, relationships, and DAX measures.
4. `report_pages.md`
   Power BI page design, filter usage, and audit layout.
5. `tables.md`
   Source table map and the columns currently used by the notebook.
6. `../vacancy_rule_parameter_maintenance_notebook.py`
   Notebook-style script for reviewing and changing governed date-correction parameters.

Recommended usage:

- review current active rules first,
- only set `EXECUTE_CHANGES = True` when the change set is ready,
- rerun the main vacancy notebook after any parameter change.

## Main Implementation Asset

The notebook source of truth is:

- `../vacancy_reporting_vic_notebook.py`

## Working Principle

The report is designed to be:

- auditable,
- configurable through Fabric data-layer parameters,
- aligned with the workbook logic in `Vacant Calc.xlsx`,
- safe to extend without inventing unsupported rules.

Current counting approach:

- `Vacancy Days` follows workbook parity,
- the vacancy start boundary day is excluded from the day count,
- report-period counts are driven by the date slicer over `fact_vacancy_day_vic`.
