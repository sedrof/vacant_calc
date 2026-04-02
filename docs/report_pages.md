# Report Build Guide

## Objective

The report should support three reporting modes:

- management summary,
- exportable operational detail,
- audit and rule transparency.

This is not a presentation dashboard. Build it as a working operational report.

## Global Slicers

Use these slicers consistently where relevant:

- `Dim Date[Date]` as a between slicer
- `dim_property_vic[entity]`
- `dim_property_vic[ownership]`
- `dim_property_vic[housing_program]`
- `dim_property_vic[property_source]`

Enable multi-select.

## Page 1: Summary

Purpose:

- show current performance quickly,
- support annual benchmark review,
- support ad hoc operational review.

Add KPI cards:

- `[Vacancy Count]`
- `[Vacancy Days]`
- `[Tenantable Days]`
- `[Untenantable Days]`
- `[Pct <= 21 Days]`
- `[Pct <= 48 Days]`

Add visuals:

- clustered column chart by `entity` using `[Average Vacancy Days]`
- stacked column chart by `housing_program` using `[Tenantable Days]` and `[Untenantable Days]`
- matrix by `ownership` and `property_source` using:
  - `[Vacancy Count]`
  - `[Vacancy Days]`
  - `[Average Vacancy Days]`
  - `[Pct <= 21 Days]`
  - `[Pct <= 48 Days]`

## Page 2: Vacancy Detail

Purpose:

- provide exportable row-level detail,
- support operational follow-up,
- support regulator-ready extracts.

Use a table visual with:

- `fact_vacancy_interval_vic[vacancy_id]`
- `dim_property_vic[property_number]`
- `dim_property_vic[property_short_address]`
- `dim_property_vic[entity]`
- `dim_property_vic[ownership]`
- `dim_property_vic[housing_program]`
- `dim_property_vic[property_source]`
- `fact_vacancy_interval_vic[vacancy_origin]`
- `fact_vacancy_interval_vic[vacancy_reason]`
- `dim_property_vic[property_start_date]`
- `dim_property_vic[property_end_date]`
- `fact_vacancy_interval_vic[vacancy_start_date]`
- `fact_vacancy_interval_vic[vacancy_end_exclusive]`
- measure `[Vacancy Days]`
- measure `[Tenantable Days]`
- measure `[Untenantable Days]`
- measure `[Other Days]`

Configuration:

- sort by `vacancy_start_date` descending,
- enable export to Excel,
- keep widths stable for exported output,
- rename `vacancy_end_exclusive` on the page to `Vacancy End Boundary`.

## Page 3: Audit

Purpose:

- show how each vacancy was split at day level,
- make void overlaps visible,
- support reconciliation against the workbook logic.

Add a table from `fact_vacancy_day_vic` with:

- `vacancy_id`
- `vacancy_date`
- `day_type`
- `void_id`
- `void_reason`

Add a table from `fact_void_interval_vic` with:

- `void_id`
- `property_id`
- `void_reference`
- `void_start_date`
- `void_end_exclusive`
- `void_reason`
- `property_condition`

Enable drillthrough on `vacancy_id` from the Vacancy Detail page to this page.

## Page 4: Config

Purpose:

- show the active date-correction rules,
- make the report auditable,
- avoid confusion about why boundaries may differ from raw source dates.

Add a table from `dim_active_vacancy_rule_parameters` with:

- `rule_name`
- `offset_days`
- `effective_from`
- `comment`
- `updated_by`
- `updated_at`

Add a note:

- `These parameters are maintained in Fabric and applied during notebook refresh. They are not report-side what-if settings.`

## Report Notes

- Use measures, not stored `full_*` columns, when a visual should respect the selected date range.
- Keep the detail page export-friendly.
- Keep the audit page plain and readable.
- Add a tooltip or text note that the vacancy logic follows `Vacant Calc.xlsx`.
