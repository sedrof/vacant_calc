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
6. `sql/vacancy_rule_parameter_maintenance.sql`
   SQL for reviewing and changing governed date-correction parameters.

## Main Implementation Asset

The notebook source of truth is:

- `../vacancy_reporting_vic_notebook.py`

## Working Principle

The report is designed to be:

- auditable,
- configurable through Fabric data-layer parameters,
- aligned with the workbook logic in `Vacant Calc.xlsx`,
- safe to extend without inventing unsupported rules.
