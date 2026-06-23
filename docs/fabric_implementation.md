# Fabric Implementation Guide

## Objective

This guide explains how to deploy the VIC vacancy reporting solution into Microsoft Fabric in a controlled order.

The implementation has three layers:

1. data preparation in a Spark notebook,
2. semantic modeling in Power BI / Fabric,
3. reporting pages for operational and regulatory use.

## Files Used

Notebooks (Medallion Pipeline):

- `../notebooks/vac_reporting_vic_bronze_notebook.py`
- `../notebooks/vac_reporting_vic_silver_notebook.py`
- `../notebooks/vac_reporting_vic_dimensions_notebook.py`
- `../notebooks/vac_reporting_vic_gold_notebook.py`

Documentation:

- `project_overview.md`
- `semantic_model.md`
- `report_pages.md`
- `tables.md`

Parameter maintenance notebook:

- `../notebooks/vac_reporting_vic_parameter_maintenance_notebook.py`

Conformed local date dimension (replicated in the local database):

- `vacancy_reporting.dim_date`

## Step 1: Review The Inputs

Before building anything, confirm these inputs:

- `Vacant Calc.xlsx` is the date-logic reference.
- TechOne data is available in Fabric through the warehouse prefix used in the notebook.
- The target state is `VIC`.
- The report requires `Entity`, `From Date`, `To Date`, `Ownership`, `CAH Program`, and `Property Source` filters.

The date window is management-selected. Do not assume quarter-only reporting. The final report must work for any `From Date` and `To Date` chosen in the slicer.

Do not start model or report work before confirming the vacancy boundary logic and the intended day-counting rule.

## Step 2: Create And Run The Medallion Notebook Pipeline

To process data and build the analytical model, execute the notebooks in sequence:

1. **Run the Bronze Ingestion Notebook (`../notebooks/vac_reporting_vic_bronze_notebook.py`):**
   * Paste the Bronze code into a Fabric notebook.
   * Ingests TechOne tables 1:1 into raw Delta staging tables:
     * `vacancy_reporting.Bronze_TechOne_Property`
     * `vacancy_reporting.Bronze_TechOne_Tenancy`
     * `vacancy_reporting.Bronze_TechOne_Void`
     * `vacancy_reporting.Bronze_TechOne_Keys`

2. **Run the Silver Standardization Notebook (`../notebooks/vac_reporting_vic_silver_notebook.py`):**
   * Paste the Silver code into a Fabric notebook.
   * Standardizes data types, performs timezone shifting (`Australia/Melbourne`), asserts column completeness (`ensure_columns`), and writes conformed Silver tables:
     * `vacancy_reporting.silver_techone_property`
     * `vacancy_reporting.silver_techone_tenancy`
     * `vacancy_reporting.silver_techone_void`
     * `vacancy_reporting.silver_techone_keys`

3. **Run the conformed Dimensions Notebook (`../notebooks/vac_reporting_vic_dimensions_notebook.py`):**
   * Paste the Dimensions code into a Fabric notebook.
   * Builds conformed Gold dimension:
     * `vacancy_reporting.dim_property_vic`

4. **Run the Gold Facts & Audits Notebook (`../notebooks/vac_reporting_vic_gold_notebook.py`):**
   * Paste the Gold code into a Fabric notebook.
   * Review top parameters (`AS_AT_DATE`).
   * Loads parameters gracefully (with try-except degradation fallback) and applies vacancy calculation boundaries, exploding intervals to daily grains, and generating exception rules.
   * The notebook writes these Gold and audit tables:
     * `vacancy_reporting.dim_active_vacancy_rule_parameters`
     * `vacancy_reporting.fact_vacancy_day_vic`
     * `vacancy_reporting.fact_vacancy_interval_vic`
     * `vacancy_reporting.stg_keys_vic`
     * `vacancy_reporting.audit_property_vic`
     * `vacancy_reporting.audit_tenancy_vic`
     * `vacancy_reporting.audit_void_vic`
     * `vacancy_reporting.audit_keys_vic`
     * `vacancy_reporting.audit_exceptions_vic`

The vacancy interval table includes:

- overlapping void start and end values where available,
- one representative keys row per vacancy using the confirmed `PARENT_ENGAGEMENT_ID = property_id` mapping.
- one representative overlapping void row per vacancy including `void_id`, `void_start_date`, `void_end_date`, and `void_reason`.
- tenancy context for the tenancy that ends into the vacancy and the next tenancy that closes it, including tenancy IDs and tenancy start/end dates where available.

The new `audit_*` tables are intentionally separate from the management tables:

- they preserve source-aligned rows for property, tenancy, void, and keys,
- they include raw and adjusted dates where relevant,
- they support property-level trace and validation without changing the current report logic.

The exception table is also separate:

- `audit_exceptions_vic` contains source/data-quality issues that should not occur under normal business logic,
- the first implemented rule flags any tenancy interval that overlaps a void interval on the same property.

## Step 3: Validate The Parameter Table

Review the active date-correction rules before building the semantic model.

Use:

- `../notebooks/vac_reporting_vic_parameter_maintenance_notebook.py`

Recommended notebook flow:

1. Start with `ACTION = "view_active"`.
2. Review the current active rules.
3. Prepare `RULE_UPDATES`.
4. Change `ACTION` to `"apply_rule_updates"`.
5. Set `EXECUTE_CHANGES = True`.
6. Run the maintenance notebook.
7. Rerun `../notebooks/vac_reporting_vic_gold_notebook.py`.

The key rules are:

- `property_source_date_offset`
- `tenancy_source_date_offset`
- `void_source_date_offset`
- `keys_source_date_offset`
- `tenancy_end_to_vacancy_start`
- `next_tenancy_start_to_vacancy_end`
- `property_start_to_vacancy_start`
- `property_end_to_vacancy_end`

Expected default behavior:

- tenancy end `2026-01-01` becomes vacancy start `2026-01-02`
- next tenancy start `2026-04-05` becomes vacancy inclusive end `2026-04-04`
- selected `Vacancy Days` for a report ending `2026-03-31` becomes `89` for a vacancy starting `2026-01-02`, because the current model counts the vacancy start date and therefore uses `MIN(vacancy_end, report_to_date) - vacancy_start + 1`

If the confirmed business rule is that the TechOne source dates are one day behind, set these raw source offset rules to `1` before rerunning the main notebook:

- `property_source_date_offset`
- `tenancy_source_date_offset`
- `void_source_date_offset`
- `keys_source_date_offset`

That shifts the raw dates in the notebook before the vacancy and void interval logic is applied.

If the business wants different offsets, change the config table first and rerun the notebook.

## Step 4: Validate The Data Outputs

Before moving to the semantic model, validate the outputs with a small set of examples:

1. Confirm there is one row per vacancy day in `fact_vacancy_day_vic`.
2. Confirm `Tenantable Days + Untenantable Days + Other Days = Vacancy Days`.
3. Confirm `Other Days` are populated only where the Void table has an `OTHER_VACANCY_FROM_DATE` / `OTHER_VACANCY_TO_DATE` range overlapping the vacancy.
4. Confirm `Void End Date` is counted inclusively by checking that `void_end_exclusive = void_end_date + 1` when `void_end_date` is populated.
5. Confirm `Other End Date` is counted inclusively by checking that `other_end_exclusive = other_end_date + 1` when `other_end_date` is populated.
6. Confirm `Other Days` do not count outside the parent void period.
7. Confirm `audit_exceptions_vic` flags `OTHER_VACANCY_OUTSIDE_VOID` when the source other-vacancy range starts before the void or ends after it.
8. Confirm properties with no earlier tenancy can still produce an initial vacancy.
9. Confirm open vacancies are capped by the property end date, or use the notebook snapshot boundary if still active.
10. Confirm an example such as `2026-01-02` to `2026-03-31` returns `89` vacancy days under the current inclusive-start rule.
11. Confirm the active rules displayed in `dim_active_vacancy_rule_parameters` match the intended maintenance change.
12. Confirm the new `audit_*` tables show both raw and adjusted dates for the same test property.
13. Confirm `audit_exceptions_vic` returns expected records for known bad source scenarios and stays empty for clean test properties.
14. Confirm `Property Type`, `Property Program`, and `Property Current Stage` are populated consistently across `dim_property_vic`, the `audit_*` tables, and `fact_vacancy_interval_vic`.
15. Confirm `dim_property_vic[is_standard_address]` is available for report filtering and that no row counts change unless the report explicitly filters on it.

If any of these checks fail, stop there and fix the notebook before continuing.

## Step 5: Build The Semantic Model

Follow `semantic_model.md`.

Important design choice:

- date filtering must primarily work through `fact_vacancy_day_vic`,
- interval tables are supporting structures, not the main date filter path.
- property should filter day-level rows through `fact_vacancy_interval_vic`, not through a second direct property-to-day relationship.
- use the existing physical `dim_date` table in Fabric, not a DAX-generated calendar table.
- for detail visuals, use overlap measures to control which vacancy or property rows remain visible for the selected date window.
- add direct `property_id` relationships from `dim_property_vic` to the new `audit_*` tables for the trace page.
- add a direct `property_id` relationship from `dim_property_vic` to `audit_exceptions_vic` for the exception page.

Keep the model auditable and avoid report-only logic that duplicates the notebook rules.

## Step 6: Build The Report

Follow `report_pages.md`.

The report should include:

- a summary page,
- a vacancy detail page,
- an audit page,
- a config page showing active rule parameters,
- a property trace page for source-vs-derived validation.
- an exception monitor page for invalid source patterns.

The report is operational and regulatory. Keep the layout clear and export-friendly.

## Step 7: Refresh Process

Use this order whenever source data or rule parameters change:

1. Run `../notebooks/vac_reporting_vic_parameter_maintenance_notebook.py` if a parameter change is required.
2. Run `../notebooks/vac_reporting_vic_gold_notebook.py`.
3. Refresh the semantic model.
4. Validate the report outputs.

For property-trace testing after a notebook change:

1. choose one test `property_id`,
2. review `audit_property_vic`,
3. review `audit_tenancy_vic`,
4. review `audit_void_vic`,
5. review `audit_keys_vic`,
6. compare those rows to `fact_vacancy_interval_vic`,
7. only then inspect `fact_vacancy_day_vic` if the interval still looks wrong.

For exception monitoring after a notebook change:

1. review `audit_exceptions_vic`,
2. confirm any returned rows are genuine source issues,
3. use the `Property Trace` page to inspect the affected property in detail.

Do not change offsets in the report itself for the official reporting process.

## Current Assumptions

- `Property Program` is used as `Property Source`.
- `Keys.PARENT_ENGAGEMENT_ID` is treated as `property_id`.
- one representative keys row is selected per vacancy based on property match and date proximity.
- `Resident_Data` is not required for the current vacancy logic.
- `Other Days` are derived from the Void table's other vacancy date range and are mutually exclusive from `Untenantable Days`.
- `is_standard_address` is a report-performance helper flag. It classifies property addresses containing bracket markers as non-standard, but the notebook does not filter on it.

## Extension Guidance

Future development should follow this order:

1. confirm the business rule,
2. update the notebook,
3. update the documentation,
4. update the semantic model only if needed,
5. update the report last.

That order keeps the reporting logic governed in the data layer.
