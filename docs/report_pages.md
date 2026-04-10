# Report Build Guide

## Objective

The report should support three reporting modes:

- management summary,
- exportable operational detail,
- audit and rule transparency.

This is not a presentation dashboard. Build it as a working operational report.

The global date slicer is a free management-selected reporting window. It is not tied to quarter-end logic. Users can choose any `From Date` and `To Date` and the visuals should show the relevant vacancy activity for that exact date range.

## Before You Start

Use these model objects:

- table `dim_date`
- table `dim_property_vic`
- table `fact_vacancy_interval_vic`
- table `fact_vacancy_day_vic`
- table `fact_void_interval_vic`
- table `dim_active_vacancy_rule_parameters`

Use these measures:

- `[Vacancy Count]`
- `[Vacancy Days]`
- `[Tenantable Days]`
- `[Untenantable Days]`
- `[Other Days]`
- `[Average Vacancy Days]`
- `[Vacancies LE 21 Days]`
- `[Vacancies GT 21 Days]`
- `[Vacancies LE 48 Days]`
- `[Vacancies GT 48 Days]`
- `[Pct LE 21 Days]`
- `[Pct LE 48 Days]`

## Global Slicers

Add these slicers at the top of the report and sync them across pages where appropriate.

### Date slicer

Visual type:

- `Slicer`

Field well:

- `Field` = `dim_date[date]`

Settings:

- slicer type = `Between`
- show date input boxes = `On`

Behavior:

- `From Date` removes vacancy day rows before the selected start date
- `To Date` removes vacancy day rows after the selected end date
- this slicer does not automatically force descriptive columns such as `property_start_date` or `void_start_date` to sit inside the selected range

### Entity slicer

Visual type:

- `Slicer`

Field well:

- `Field` = `dim_property_vic[entity]`

Settings:

- style = `Dropdown`
- multi-select = `On`

### Ownership slicer

Visual type:

- `Slicer`

Field well:

- `Field` = `dim_property_vic[ownership]`

Settings:

- style = `Dropdown`
- multi-select = `On`

### CAH Program slicer

Visual type:

- `Slicer`

Field well:

- `Field` = `dim_property_vic[housing_program]`

Settings:

- style = `Dropdown`
- multi-select = `On`

### Property Source slicer

Visual type:

- `Slicer`

Field well:

- `Field` = `dim_property_vic[property_source]`

Settings:

- style = `Dropdown`
- multi-select = `On`

## Page 1: Summary

Purpose:

- show current performance quickly,
- support annual benchmark review,
- support ad hoc operational review.

### KPI card 1

Visual type:

- `Card`

Field well:

- `Data` = `[Vacancy Count]`

### KPI card 2

Visual type:

- `Card`

Field well:

- `Data` = `[Vacancy Days]`

### KPI card 3

Visual type:

- `Card`

Field well:

- `Data` = `[Tenantable Days]`

### KPI card 4

Visual type:

- `Card`

Field well:

- `Data` = `[Untenantable Days]`

### KPI card 5

Visual type:

- `Card`

Field well:

- `Data` = `[Pct LE 21 Days]`

Formatting:

- display units = `None`
- show as percentage

### KPI card 6

Visual type:

- `Card`

Field well:

- `Data` = `[Pct LE 48 Days]`

Formatting:

- display units = `None`
- show as percentage

### Visual 1: Average Vacancy Days by Entity

Visual type:

- `Clustered column chart`

Field well:

- `X-axis` = `dim_property_vic[entity]`
- `Y-axis` = `[Average Vacancy Days]`
- `Tooltips` = `[Vacancy Count]`, `[Vacancy Days]`

Formatting:

- sort by `[Average Vacancy Days]` descending

### Visual 2: Tenantable vs Untenantable by CAH Program

Visual type:

- `Stacked column chart`

Field well:

- `X-axis` = `dim_property_vic[housing_program]`
- `Y-axis` = `[Tenantable Days]`, `[Untenantable Days]`
- `Tooltips` = `[Vacancy Days]`, `[Vacancy Count]`

Formatting:

- keep legend on

### Visual 3: Summary matrix

Visual type:

- `Matrix`

Field well:

- `Rows` = `dim_property_vic[ownership]`
- `Columns` = `dim_property_vic[property_source]`
- `Values` = `[Vacancy Count]`, `[Vacancy Days]`, `[Average Vacancy Days]`, `[Pct LE 21 Days]`, `[Pct LE 48 Days]`

Formatting:

- show values on rows = `Off`
- format percentage measures as percentages

Page note:

- `Vacancy Days` follows workbook counting logic and excludes the vacancy start boundary day.

## Page 2: Vacancy Detail

Purpose:

- provide exportable row-level detail,
- support operational follow-up,
- support regulator-ready extracts.

### Visual 1: Vacancy detail table

Visual type:

- `Table`

Field well:

- `Columns` = `fact_vacancy_interval_vic[vacancy_id]`
- `Columns` = `fact_vacancy_interval_vic[property_id]`
- `Columns` = `dim_property_vic[property_number]`
- `Columns` = `dim_property_vic[property_short_address]`
- `Columns` = `dim_property_vic[entity]`
- `Columns` = `dim_property_vic[ownership]`
- `Columns` = `dim_property_vic[housing_program]`
- `Columns` = `dim_property_vic[property_source]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_origin]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_reason]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_start_tenancy_id]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_start_tenancy_end_date]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_start_date]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_end_exclusive]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_end_tenancy_id]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_end_tenancy_start_date]`
- `Columns` = `fact_vacancy_interval_vic[void_id]`
- `Columns` = `fact_vacancy_interval_vic[void_reference]`
- `Columns` = `fact_vacancy_interval_vic[void_start_date]`
- `Columns` = `fact_vacancy_interval_vic[void_end_date]`
- `Columns` = `fact_vacancy_interval_vic[void_reason]`
- `Columns` = `fact_vacancy_interval_vic[overlap_void_start_date]`
- `Columns` = `fact_vacancy_interval_vic[overlap_void_end_date]`
- `Columns` = `[Vacancy Days]`
- `Columns` = `[Tenantable Days]`
- `Columns` = `[Untenantable Days]`
- `Columns` = `[Other Days]`
- `Columns` = `fact_vacancy_interval_vic[key_id]`
- `Columns` = `fact_vacancy_interval_vic[key_reference]`
- `Columns` = `fact_vacancy_interval_vic[key_vacancy_exemptions_code]`
- `Columns` = `fact_vacancy_interval_vic[key_vacancy_exemptions_desc]`
- `Columns` = `fact_vacancy_interval_vic[key_property_condition_code]`
- `Columns` = `fact_vacancy_interval_vic[key_property_condition]`
- `Columns` = `fact_vacancy_interval_vic[key_contractor_notified_date]`
- `Columns` = `fact_vacancy_interval_vic[key_to_lockbox_onsite]`
- `Columns` = `fact_vacancy_interval_vic[key_contractor_collect_key_date]`
- `Columns` = `fact_vacancy_interval_vic[key_contractor_name_comments]`
- `Columns` = `fact_vacancy_interval_vic[key_contractor_return_key_date]`

Formatting:

- sort by `fact_vacancy_interval_vic[vacancy_start_date]` descending
- rename `fact_vacancy_interval_vic[vacancy_id]` display label to `Vacancy ID`
- rename `fact_vacancy_interval_vic[property_id]` display label to `Property ID`
- rename `dim_property_vic[property_number]` display label to `Property Number`
- rename `dim_property_vic[property_short_address]` display label to `Property Address`
- rename `dim_property_vic[entity]` display label to `Entity`
- rename `dim_property_vic[ownership]` display label to `Ownership`
- rename `dim_property_vic[housing_program]` display label to `Housing Program`
- rename `dim_property_vic[property_source]` display label to `Property Source`
- rename `fact_vacancy_interval_vic[vacancy_origin]` display label to `Vacancy Origin`
- rename `fact_vacancy_interval_vic[vacancy_reason]` display label to `Vacancy Reason`
- rename `fact_vacancy_interval_vic[vacancy_start_tenancy_id]` display label to `Previous Tenancy ID`
- rename `fact_vacancy_interval_vic[vacancy_start_tenancy_end_date]` display label to `Previous Tenancy End Date`
- rename `fact_vacancy_interval_vic[vacancy_start_date]` display label to `Vacancy Start Date`
- rename `fact_vacancy_interval_vic[vacancy_end_exclusive]` display label to `Vacancy End Boundary`
- rename `fact_vacancy_interval_vic[vacancy_end_tenancy_id]` display label to `Next Tenancy ID`
- rename `fact_vacancy_interval_vic[vacancy_end_tenancy_start_date]` display label to `Next Tenancy Start Date`
- rename `dim_property_vic[property_start_date]` display label to `Property Start Date`
- rename `dim_property_vic[property_end_date]` display label to `Property End Date`
- rename `fact_vacancy_interval_vic[void_id]` display label to `Void ID`
- rename `fact_vacancy_interval_vic[void_reference]` display label to `Void Reference`
- rename `fact_vacancy_interval_vic[void_start_date]` display label to `Selected Void Start Date`
- rename `fact_vacancy_interval_vic[void_end_date]` display label to `Selected Void End Date`
- rename `fact_vacancy_interval_vic[void_reason]` display label to `Void Reason`
- rename `fact_vacancy_interval_vic[overlap_void_start_date]` display label to `Overall Void Start Date`
- rename `fact_vacancy_interval_vic[overlap_void_end_date]` display label to `Overall Void End Date`
- rename `[Vacancy Days]` display label to `Vacancy Days`
- rename `[Tenantable Days]` display label to `Tenantable Days`
- rename `[Untenantable Days]` display label to `Untenantable Days`
- rename `[Other Days]` display label to `Other Days`
- rename `fact_vacancy_interval_vic[key_id]` display label to `Keys Record ID`
- rename `fact_vacancy_interval_vic[key_reference]` display label to `Keys Reference`
- rename `fact_vacancy_interval_vic[key_vacancy_exemptions_code]` display label to `Vacancy Exemption Code`
- rename `fact_vacancy_interval_vic[key_vacancy_exemptions_desc]` display label to `Vacancy Exemption`
- rename `fact_vacancy_interval_vic[key_property_condition_code]` display label to `Property Condition Code`
- rename `fact_vacancy_interval_vic[key_property_condition]` display label to `Property Condition`
- rename `fact_vacancy_interval_vic[key_contractor_notified_date]` display label to `Contractor Notified Date`
- rename `fact_vacancy_interval_vic[key_to_lockbox_onsite]` display label to `Lockbox On Site`
- rename `fact_vacancy_interval_vic[key_contractor_collect_key_date]` display label to `Contractor Collected Key Date`
- rename `fact_vacancy_interval_vic[key_contractor_name_comments]` display label to `Contractor Comments`
- rename `fact_vacancy_interval_vic[key_contractor_return_key_date]` display label to `Contractor Returned Key Date`
- set column widths manually for export readability

Recommended final column order for management:

- `Vacancy ID`
- `Property Number`
- `Property Address`
- `Entity`
- `Ownership`
- `Housing Program`
- `Property Source`
- `Vacancy Origin`
- `Vacancy Reason`
- `Property Start Date`
- `Property End Date`
- `Previous Tenancy ID`
- `Previous Tenancy End Date`
- `Vacancy Start Date`
- `Vacancy End Boundary`
- `Next Tenancy ID`
- `Next Tenancy Start Date`
- `Vacancy Days`
- `Tenantable Days`
- `Untenantable Days`
- `Other Days`
- `Void ID`
- `Void Reference`
- `Selected Void Start Date`
- `Selected Void End Date`
- `Void Reason`
- `Overall Void Start Date`
- `Overall Void End Date`
- `Keys Record ID`
- `Keys Reference`
- `Vacancy Exemption`
- `Property Condition`
- `Contractor Notified Date`
- `Lockbox On Site`
- `Contractor Collected Key Date`
- `Contractor Comments`
- `Contractor Returned Key Date`

Optional technical columns to keep only if the business asks:

- `Property ID`
- `Vacancy Exemption Code`
- `Property Condition Code`

Clarification:

- `vacancy_start_tenancy_*` columns describe the tenancy that ended into the vacancy.
- `vacancy_end_tenancy_*` columns describe the next tenancy that closes the vacancy.
- `void_*` columns are the first selected overlapping void row for the vacancy.
- `overlap_void_*` columns show the overall overlap range across all matching void rows for that vacancy.

Behavior:

- enable export to Excel
- add visual-level filter `Vacancy Overlaps Selected Period`
- set `Vacancy Overlaps Selected Period` to `is 1`
- add visual-level filter `Property Overlaps Selected Period` only if the business wants to hide properties that do not overlap the selected date range
- keep the `dim_date[date]` global slicer in place so the day-based measures still count only the selected date window

## Page 3: Audit

Purpose:

- show how each vacancy was split at day level,
- make void overlaps visible,
- support reconciliation against the workbook logic.

### Drillthrough setup

Create this page as a drillthrough target.

Field well:

- `Drillthrough` = `fact_vacancy_interval_vic[vacancy_id]`

Keep all drillthrough filters on this page.

### Visual 1: Vacancy day audit table

Visual type:

- `Table`

Field well:

- `Columns` = `fact_vacancy_day_vic[vacancy_id]`
- `Columns` = `fact_vacancy_day_vic[vacancy_date]`
- `Columns` = `fact_vacancy_day_vic[day_type]`
- `Columns` = `fact_vacancy_day_vic[void_id]`
- `Columns` = `fact_vacancy_day_vic[void_reason]`

Formatting:

- sort by `fact_vacancy_day_vic[vacancy_date]` ascending

### Visual 2: Void interval table

Visual type:

- `Table`

Field well:

- `Columns` = `fact_void_interval_vic[void_id]`
- `Columns` = `fact_void_interval_vic[property_id]`
- `Columns` = `fact_void_interval_vic[void_reference]`
- `Columns` = `fact_void_interval_vic[void_start_date]`
- `Columns` = `fact_void_interval_vic[void_end_exclusive]`
- `Columns` = `fact_void_interval_vic[void_reason]`
- `Columns` = `fact_void_interval_vic[property_condition]`

Formatting:

- rename `void_end_exclusive` display label to `Void End Boundary`

### Visual 3: Keys audit table

Visual type:

- `Table`

Field well:

- `Columns` = `fact_vacancy_interval_vic[property_id]`
- `Columns` = `fact_vacancy_interval_vic[key_id]`
- `Columns` = `fact_vacancy_interval_vic[key_reference]`
- `Columns` = `fact_vacancy_interval_vic[key_vacancy_exemptions_desc]`
- `Columns` = `fact_vacancy_interval_vic[key_property_condition]`
- `Columns` = `fact_vacancy_interval_vic[key_contractor_notified_date]`
- `Columns` = `fact_vacancy_interval_vic[key_to_lockbox_onsite]`
- `Columns` = `fact_vacancy_interval_vic[key_contractor_collect_key_date]`
- `Columns` = `fact_vacancy_interval_vic[key_contractor_name_comments]`
- `Columns` = `fact_vacancy_interval_vic[key_contractor_return_key_date]`

## Page 4: Config

Purpose:

- show the active date-correction rules,
- make the report auditable,
- avoid confusion about why boundaries may differ from raw source dates.

### Visual 1: Active rule table

Visual type:

- `Table`

Field well:

- `Columns` = `dim_active_vacancy_rule_parameters[rule_name]`
- `Columns` = `dim_active_vacancy_rule_parameters[offset_days]`
- `Columns` = `dim_active_vacancy_rule_parameters[effective_from]`
- `Columns` = `dim_active_vacancy_rule_parameters[comment]`
- `Columns` = `dim_active_vacancy_rule_parameters[updated_by]`
- `Columns` = `dim_active_vacancy_rule_parameters[updated_at]`

### Visual 2: explanatory text

Add a text box with this wording:

- `These parameters are maintained in Fabric and applied during notebook refresh. They are not report-side what-if settings.`

## Report Notes

- Use measures, not stored `full_*` columns, when a visual should respect the selected date range.
- Keep the detail page export-friendly.
- Keep the audit page plain and readable.
- Add a tooltip or text note that the vacancy logic follows `Vacant Calc.xlsx`.
- After any parameter change, rerun the main notebook and refresh the semantic model before relying on report output.
