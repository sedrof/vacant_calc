# Semantic Model Guide

## Purpose

This model must support two things at the same time:

- accurate date-sliced vacancy analysis,
- a clear audit path back to the day-level calculation.

For that reason, the daily fact table is the center of the model.

The date slicer is not limited to quarters or fixed periods. Management can choose any `From Date` and `To Date`, and the model must return the relevant vacancy activity for that selected window.

## Tables To Load

Load these tables from Fabric:

- `` `Evolve-TechOne`.Shortcut.dbo.dim_date ``
- `vacancy_reporting.dim_property_vic`
- `vacancy_reporting.dim_active_vacancy_rule_parameters`
- `vacancy_reporting.fact_vacancy_day_vic`
- `vacancy_reporting.fact_vacancy_interval_vic`
- `vacancy_reporting.fact_void_interval_vic`
- `vacancy_reporting.audit_property_vic`
- `vacancy_reporting.audit_tenancy_vic`
- `vacancy_reporting.audit_void_vic`
- `vacancy_reporting.audit_keys_vic`
- `vacancy_reporting.audit_exceptions_vic`

## Recommended Relationships

Create these relationships:

- `dim_date[date]` 1:* `fact_vacancy_day_vic[vacancy_date]`
- `dim_property_vic[property_id]` 1:* `fact_vacancy_interval_vic[property_id]`
- `fact_vacancy_interval_vic[vacancy_id]` 1:* `fact_vacancy_day_vic[vacancy_id]`
- `dim_property_vic[property_id]` to `audit_property_vic[property_id]`
- `dim_property_vic[property_id]` 1:* `audit_tenancy_vic[property_id]`
- `dim_property_vic[property_id]` 1:* `audit_void_vic[property_id]`
- `dim_property_vic[property_id]` 1:* `audit_keys_vic[property_id]`
- `dim_property_vic[property_id]` 1:* `audit_exceptions_vic[property_id]`

Relationship settings:

- Do not create a direct active relationship from `dim_property_vic[property_id]` to `fact_vacancy_day_vic[property_id]`.
- Use `Both` cross-filter direction on `fact_vacancy_interval_vic[vacancy_id]` to `fact_vacancy_day_vic[vacancy_id]`.
- Keep all other relationships single direction.
- For `audit_property_vic`, accept `1:1` if the modeling tool infers it. Single direction from `dim_property_vic` is still the intended behavior.
- Do not relate `dim_active_vacancy_rule_parameters` to the rest of the model. It is a display and governance table.
- Do not create a separate active relationship to `stg_keys_vic` for the report model. Keys fields are already embedded into `fact_vacancy_interval_vic`.

## Why The Model Is Built This Way

The report filters by date range. If date filtering only touches the interval table, partial-period calculations become unreliable.

Using `fact_vacancy_day_vic` as the main fact solves that problem because every day in the selected range is explicit.

To avoid ambiguous filter paths, `dim_property_vic` should filter `fact_vacancy_day_vic` through `fact_vacancy_interval_vic`, not through a second direct relationship.

This means the `dim_date[date]` slicer filters day rows first. With the `Both` cross-filter on `vacancy_id`, that date selection then filters vacancy interval rows back through `fact_vacancy_day_vic`.

Important behavior:

- the date slicer controls the selected reporting window, not just calendar labels,
- `From Date` removes vacancy day rows before the chosen start date,
- `To Date` removes vacancy day rows after the chosen end date,
- descriptive columns such as `property_start_date`, `property_end_date`, `vacancy_start_date`, and `void_start_date` can still display values outside the slicer if the vacancy overlaps the selected window.
- `vacancy_end_exclusive` is a technical boundary. If you need a user-facing inclusive end inside a measure, convert it with `vacancy_end_exclusive - 1`.

Important counting note:

- the workbook logic excludes the vacancy start boundary day from `Vacancy Days`,
- the notebook matches that behavior,
- so selected-period vacancy days align with the workbook formula `MIN(end_date, report_to_date) - start_date`.
- if the report is filtered to `2026-03-31`, a vacancy starting on `2026-01-02` contributes `88` days, not `89`.

## Date Table

Use the existing physical table:

- `` `Evolve-TechOne`.Shortcut.dbo.dim_date ``

Recommended semantic model settings:

- mark `dim_date[date]` as the date column if your modeling tool supports it,
- use `dim_date[date]` for all report date slicers,
- keep quarter, month, and year attributes from this shared table instead of recreating them in DAX.

## Core Measures

Use these measures as the default report measures.

```DAX
Vacancy Days =
SUM ( fact_vacancy_day_vic[vacancy_day_count] )
```

```DAX
Tenantable Days =
SUM ( fact_vacancy_day_vic[tenantable_day_count] )
```

```DAX
Untenantable Days =
SUM ( fact_vacancy_day_vic[untenantable_day_count] )
```

```DAX
Other Days =
SUM ( fact_vacancy_day_vic[other_day_count] )
```

Worked example:

- vacancy start boundary = `2026-01-02`
- vacancy end boundary = `2026-01-10`
- counted vacancy days = `2026-01-03` to `2026-01-09`
- overlapping void period = `2026-01-05` to `2026-01-06`
- counted void days = `2026-01-06`

Result:

- `Vacancy Days` = `7`
- `Untenantable Days` = `1`
- `Tenantable Days` = `6`

This follows the implemented rule:

- vacancy day rows are created from `vacancy_start_date + 1` through `vacancy_end_exclusive - 1`
- void day rows are created the same way
- a counted vacancy day is `Tenantable` only when it does not overlap a counted void day

```DAX
Vacancy Count =
DISTINCTCOUNT ( fact_vacancy_day_vic[vacancy_id] )
```

```DAX
Average Vacancy Days =
DIVIDE ( [Vacancy Days], [Vacancy Count] )
```

```DAX
Vacancies LE 21 Days =
SUMX (
    VALUES ( fact_vacancy_interval_vic[vacancy_id] ),
    IF ( CALCULATE ( [Vacancy Days] ) <= 21, 1, 0 )
)
```

```DAX
Vacancies GT 21 Days =
SUMX (
    VALUES ( fact_vacancy_interval_vic[vacancy_id] ),
    IF ( CALCULATE ( [Vacancy Days] ) > 21, 1, 0 )
)
```

```DAX
Vacancies LE 48 Days =
SUMX (
    VALUES ( fact_vacancy_interval_vic[vacancy_id] ),
    IF ( CALCULATE ( [Vacancy Days] ) <= 48, 1, 0 )
)
```

```DAX
Vacancies GT 48 Days =
SUMX (
    VALUES ( fact_vacancy_interval_vic[vacancy_id] ),
    IF ( CALCULATE ( [Vacancy Days] ) > 48, 1, 0 )
)
```

```DAX
Pct LE 21 Days =
DIVIDE ( [Vacancies LE 21 Days], [Vacancy Count] )
```

```DAX
Pct LE 48 Days =
DIVIDE ( [Vacancies LE 48 Days], [Vacancy Count] )
```

```DAX
Vacancy Overlaps Selected Period =
VAR ReportFrom =
    MIN ( dim_date[date] )
VAR ReportTo =
    MAX ( dim_date[date] )
VAR VacancyStart =
    SELECTEDVALUE ( fact_vacancy_interval_vic[vacancy_start_date] )
VAR VacancyEnd =
    VAR EndExclusive =
        SELECTEDVALUE ( fact_vacancy_interval_vic[vacancy_end_exclusive] )
    RETURN
        IF ( NOT ISBLANK ( EndExclusive ), EndExclusive - 1 )
RETURN
IF (
    NOT ISBLANK ( VacancyStart ) &&
    VacancyStart <= ReportTo &&
    ( ISBLANK ( VacancyEnd ) || VacancyEnd >= ReportFrom ),
    1,
    0
)
```

```DAX
Property Overlaps Selected Period =
VAR ReportFrom =
    MIN ( dim_date[date] )
VAR ReportTo =
    MAX ( dim_date[date] )
VAR PropertyStart =
    SELECTEDVALUE ( dim_property_vic[property_start_date] )
VAR PropertyEnd =
    SELECTEDVALUE ( dim_property_vic[property_end_date] )
RETURN
IF (
    ( ISBLANK ( PropertyStart ) || PropertyStart <= ReportTo ) &&
    ( ISBLANK ( PropertyEnd ) || PropertyEnd >= ReportFrom ),
    1,
    0
)
```

```DAX
Exception Count =
COUNTROWS ( audit_exceptions_vic )
```

```DAX
Vacancy Has Exception =
MAX ( fact_vacancy_interval_vic[has_exception_flag] )
```

Use `Vacancy Overlaps Selected Period` as the main row-visibility filter on detail visuals that should only show vacancies relevant to the selected date window.

Use `Property Overlaps Selected Period` only where the business explicitly wants to filter by property lifecycle overlap with the selected date window.

## Fields To Expose

Expose these business-facing fields.

From `dim_property_vic`:

- `property_number`
- `property_short_address`
- `suburb`
- `entity`
- `ownership`
- `housing_program`
- `property_source`
- `property_start_date`
- `property_end_date`

From `fact_vacancy_interval_vic`:

- `property_id`
- `vacancy_id`
- `vacancy_origin`
- `vacancy_reason`
- `vacancy_start_tenancy_id`
- `vacancy_start_tenancy_start_date`
- `vacancy_start_tenancy_end_date`
- `vacancy_end_tenancy_id`
- `vacancy_end_tenancy_start_date`
- `vacancy_end_tenancy_end_date`
- `vacancy_start_date`
- `vacancy_end_exclusive`
- `void_id`
- `void_reference`
- `void_start_date`
- `void_end_date`
- `void_reason_code`
- `void_reason`
- `overlap_void_start_date`
- `overlap_void_end_date`
- `has_exception_flag`
- `exception_count`
- `exception_types`
- `full_vacancy_days`
- `full_tenantable_days`
- `full_untenantable_days`
- `full_other_days`
- `key_id`
- `key_reference`
- `key_date_received_from_tenant`
- `key_outgoing_inspection_date`
- `key_contractor_notified_date`
- `key_to_lockbox_onsite`
- `key_contractor_collect_key_date`
- `key_contractor_name_comments`
- `key_contractor_return_key_date`
- `key_new_activated_property`
- `key_vacancy_exemptions_code`
- `key_vacancy_exemptions_desc`
- `key_property_condition_code`
- `key_property_condition`
- `meets_21_day_benchmark`
- `meets_48_day_benchmark`

From `dim_active_vacancy_rule_parameters`:

- `rule_name`
- `offset_days`
- `effective_from`
- `comment`
- `updated_by`
- `updated_at`

From the `audit_*` tables, expose the fields needed for the `Property Trace` page:

- `audit_property_vic[property_id]`
- `audit_property_vic[property_number]`
- `audit_property_vic[property_short_address]`
- `audit_property_vic[raw_effective_property_start_date]`
- `audit_property_vic[property_start_date]`
- `audit_property_vic[raw_property_end_date]`
- `audit_property_vic[property_end_date]`
- `audit_property_vic[source_date_offset_days]`
- `audit_tenancy_vic[tenancy_id]`
- `audit_tenancy_vic[tenancy_reference]`
- `audit_tenancy_vic[raw_tenancy_start_date]`
- `audit_tenancy_vic[tenancy_start_date]`
- `audit_tenancy_vic[raw_tenancy_end_date]`
- `audit_tenancy_vic[tenancy_end_date]`
- `audit_tenancy_vic[tenancy_end_reason]`
- `audit_tenancy_vic[source_date_offset_days]`
- `audit_void_vic[void_id]`
- `audit_void_vic[void_reference]`
- `audit_void_vic[raw_void_start_date]`
- `audit_void_vic[void_start_date]`
- `audit_void_vic[raw_void_end_date]`
- `audit_void_vic[void_end_date]`
- `audit_void_vic[void_reason]`
- `audit_void_vic[source_date_offset_days]`
- `audit_keys_vic[key_id]`
- `audit_keys_vic[key_reference]`
- `audit_keys_vic[raw_date_received_from_tenant]`
- `audit_keys_vic[date_received_from_tenant]`
- `audit_keys_vic[raw_contractor_notified_date]`
- `audit_keys_vic[contractor_notified_date]`
- `audit_keys_vic[vacancy_exemptions_desc]`
- `audit_keys_vic[property_condition]`
- `audit_keys_vic[source_date_offset_days]`

From `audit_exceptions_vic`, expose the fields needed for the exception page:

- `audit_exceptions_vic[exception_id]`
- `audit_exceptions_vic[exception_type]`
- `audit_exceptions_vic[exception_severity]`
- `audit_exceptions_vic[property_id]`
- `audit_exceptions_vic[property_number]`
- `audit_exceptions_vic[property_short_address]`
- `audit_exceptions_vic[entity]`
- `audit_exceptions_vic[ownership]`
- `audit_exceptions_vic[housing_program]`
- `audit_exceptions_vic[tenancy_id]`
- `audit_exceptions_vic[tenancy_reference]`
- `audit_exceptions_vic[raw_tenancy_start_date]`
- `audit_exceptions_vic[tenancy_start_date]`
- `audit_exceptions_vic[raw_tenancy_end_date]`
- `audit_exceptions_vic[tenancy_end_date]`
- `audit_exceptions_vic[void_id]`
- `audit_exceptions_vic[void_reference]`
- `audit_exceptions_vic[raw_void_start_date]`
- `audit_exceptions_vic[void_start_date]`
- `audit_exceptions_vic[raw_void_end_date]`
- `audit_exceptions_vic[void_end_date]`
- `audit_exceptions_vic[overlap_start_date]`
- `audit_exceptions_vic[overlap_end_date]`
- `audit_exceptions_vic[overlap_days]`
- `audit_exceptions_vic[exception_summary]`

Hide technical columns such as codes, join keys that users do not need, and intermediate fields.

## Important Modeling Notes

- Use measures from `fact_vacancy_day_vic` on any page that must respect the selected date range.
- Treat the `full_*` columns in `fact_vacancy_interval_vic` as lifetime interval totals, not selected-period totals.
- Label `vacancy_end_exclusive` clearly in the report so users do not mistake it for a plain inclusive end date.
- Keep `dim_active_vacancy_rule_parameters` disconnected and visible for governance only.
- If you already created `dim_property_vic[property_id]` -> `fact_vacancy_day_vic[property_id]`, delete or deactivate it before creating the `vacancy_id` relationship.
- `void_*` fields in `fact_vacancy_interval_vic` represent one selected overlapping void row per vacancy. Use `overlap_void_record_count` if you later expose it and need to identify multiple overlaps.
- `vacancy_start_tenancy_*` fields represent the tenancy that ended into the vacancy.
- `vacancy_end_tenancy_*` fields represent the next tenancy that closes the vacancy. For initial property vacancies, the start-side tenancy fields are blank by design.
- Keep the global `dim_date[date]` slicer. Do not replace it with slicers on `vacancy_start_date` or `vacancy_end_date`.
- If a detail visual should show only vacancies relevant to the selected window, use a visual-level filter with `Vacancy Overlaps Selected Period = 1`.
- If a visual should also respect property lifecycle overlap, add `Property Overlaps Selected Period = 1` as an additional visual-level filter.
- The `Property Trace` page should be driven primarily by `property_id`, not by the global date slicer.
- Keep the `audit_*` tables for validation and development use. Hide them from the main field list if you do not want management users to build visuals from them.
- The exception page should also be property-driven and should not rely on the global date slicer unless you add a separate date modeling pattern for exceptions.

## Filter Mapping

Use these filters:

- `Entity` = `dim_property_vic[entity]`
- `From Date` / `To Date` = `dim_date[date]`
- `Ownership` = `dim_property_vic[ownership]`
- `CAH Program` = `dim_property_vic[housing_program]`
- `Property Source` = `dim_property_vic[property_source]`
