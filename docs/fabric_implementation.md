# Fabric Implementation Guide

## Objective

This guide explains how to deploy the VIC vacancy reporting solution into Microsoft Fabric in a controlled order.

The implementation has three layers:

1. data preparation in a Spark notebook,
2. semantic modeling in Power BI / Fabric,
3. reporting pages for operational and regulatory use.

## Files Used

Notebook:

- `../vacancy_reporting_vic_notebook.py`

Documentation:

- `project_overview.md`
- `semantic_model.md`
- `report_pages.md`
- `tables.md`

Parameter maintenance notebook:

- `../vacancy_rule_parameter_maintenance_notebook.py`

## Step 1: Review The Inputs

Before building anything, confirm these inputs:

- `Vacant Calc.xlsx` is the date-logic reference.
- TechOne data is available in Fabric through the warehouse prefix used in the notebook.
- The target state is `VIC`.
- The report requires `Entity`, `From Date`, `To Date`, `Ownership`, `CAH Program`, and `Property Source` filters.

Do not start model or report work before confirming the workbook boundary logic.

## Step 2: Create And Run The Notebook

1. Create a new Spark notebook in Fabric.
2. Paste the content of `../vacancy_reporting_vic_notebook.py`.
3. Review the top parameters:
   - `WAREHOUSE_PREFIX`
   - `OUTPUT_DATABASE`
   - `TARGET_STATE`
   - `AS_AT_DATE`
4. Run the notebook.

On first run, the notebook will also create the config table if it does not already exist:

- `vacancy_reporting.cfg_vacancy_rule_parameters`

The notebook then writes these reporting tables:

- `vacancy_reporting.dim_property_vic`
- `vacancy_reporting.dim_active_vacancy_rule_parameters`
- `vacancy_reporting.fact_vacancy_day_vic`
- `vacancy_reporting.fact_vacancy_interval_vic`
- `vacancy_reporting.fact_void_interval_vic`
- `vacancy_reporting.stg_keys_vic`

## Step 3: Validate The Parameter Table

Review the active date-correction rules before building the semantic model.

Use:

- `../vacancy_rule_parameter_maintenance_notebook.py`

Recommended notebook flow:

1. Start with `ACTION = "view_active"`.
2. Review the current active rules.
3. Prepare `RULE_UPDATES`.
4. Change `ACTION` to `"apply_rule_updates"`.
5. Set `EXECUTE_CHANGES = True`.
6. Run the maintenance notebook.
7. Rerun `../vacancy_reporting_vic_notebook.py`.

The key rules are:

- `tenancy_end_to_vacancy_start`
- `next_tenancy_start_to_vacancy_end`
- `property_start_to_vacancy_start`
- optional raw source offsets for `Property`, `Tenancy`, `Void`, and `Keys`

Expected default behavior:

- tenancy end `2026-01-01` becomes vacancy start `2026-01-02`
- next tenancy start `2026-04-05` becomes vacancy inclusive end `2026-04-04`
- workbook `Vac days` for a report ending `2026-03-31` becomes `88`, because the workbook formula is `MIN(vacancy_end, report_to_date) - vacancy_start`

If the business wants different offsets, change the config table first and rerun the notebook.

## Step 4: Validate The Data Outputs

Before moving to the semantic model, validate the outputs with a small set of examples:

1. Confirm there is one row per vacancy day in `fact_vacancy_day_vic`.
2. Confirm `Tenantable Days + Untenantable Days + Other Days = Vacancy Days`.
3. Confirm `Other Days = 0` in the current version.
4. Confirm properties with no earlier tenancy can still produce an initial vacancy.
5. Confirm open vacancies use the notebook snapshot boundary.
6. Confirm a workbook example such as `2026-01-02` to `2026-03-31` returns `88` vacancy days, not `89`.
7. Confirm the active rules displayed in `dim_active_vacancy_rule_parameters` match the intended maintenance change.

If any of these checks fail, stop there and fix the notebook before continuing.

## Step 5: Build The Semantic Model

Follow `semantic_model.md`.

Important design choice:

- date filtering must primarily work through `fact_vacancy_day_vic`,
- interval tables are supporting structures, not the main date filter path.

Keep the model auditable and avoid report-only logic that duplicates the notebook rules.

## Step 6: Build The Report

Follow `report_pages.md`.

The report should include:

- a summary page,
- a vacancy detail page,
- an audit page,
- a config page showing active rule parameters.

The report is operational and regulatory. Keep the layout clear and export-friendly.

## Step 7: Refresh Process

Use this order whenever source data or rule parameters change:

1. Run `../vacancy_rule_parameter_maintenance_notebook.py` if a parameter change is required.
2. Run `../vacancy_reporting_vic_notebook.py`.
3. Refresh the semantic model.
4. Validate the report outputs.

Do not change offsets in the report itself for the official reporting process.

## Current Assumptions

- `Property Program` is used as `Property Source`.
- `Keys` remains staged only.
- `Resident_Data` is not required for the current vacancy logic.
- `Other Days` remains `0` until a real rule is approved.

## Extension Guidance

Future development should follow this order:

1. confirm the business rule,
2. update the notebook,
3. update the documentation,
4. update the semantic model only if needed,
5. update the report last.

That order keeps the reporting logic governed in the data layer.
