# Semantic Model Guide

## Purpose

This model must support two things at the same time:

- accurate date-sliced vacancy analysis,
- a clear audit path back to the day-level calculation.

For that reason, the daily fact table is the center of the model.

## Tables To Load

Load these tables from Fabric:

- `vacancy_reporting.dim_property_vic`
- `vacancy_reporting.dim_active_vacancy_rule_parameters`
- `vacancy_reporting.fact_vacancy_day_vic`
- `vacancy_reporting.fact_vacancy_interval_vic`
- `vacancy_reporting.fact_void_interval_vic`

Create one DAX calendar table in the semantic model.

## Recommended Relationships

Create these relationships:

- `Dim Date[Date]` 1:* `fact_vacancy_day_vic[vacancy_date]`
- `dim_property_vic[property_id]` 1:* `fact_vacancy_day_vic[property_id]`
- `dim_property_vic[property_id]` 1:* `fact_vacancy_interval_vic[property_id]`
- `fact_vacancy_interval_vic[vacancy_id]` 1:* `fact_vacancy_day_vic[vacancy_id]`

Relationship settings:

- Use `Both` cross-filter direction only on `fact_vacancy_interval_vic[vacancy_id]` to `fact_vacancy_day_vic[vacancy_id]`.
- Keep all other relationships single direction.
- Do not relate `dim_active_vacancy_rule_parameters` to the rest of the model. It is a display and governance table.
- Do not activate a `Keys` relationship yet.

## Why The Model Is Built This Way

The report filters by date range. If date filtering only touches the interval table, partial-period calculations become unreliable.

Using `fact_vacancy_day_vic` as the main fact solves that problem because every day in the selected range is explicit.

Important counting note:

- the workbook logic excludes the vacancy start boundary day from `Vacancy Days`,
- the notebook matches that behavior,
- so selected-period vacancy days align with the workbook formula `MIN(end_date, report_to_date) - start_date`.
- if the report is filtered to `2026-03-31`, a vacancy starting on `2026-01-02` contributes `88` days, not `89`.

## Calendar Table

Create this table:

```DAX
Dim Date =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2020, 1, 1 ), DATE ( 2035, 12, 31 ) ),
    "Year", YEAR ( [Date] ),
    "Month Number", MONTH ( [Date] ),
    "Month", FORMAT ( [Date], "MMM" ),
    "Year Month", FORMAT ( [Date], "YYYY-MM" ),
    "Quarter", "Q" & FORMAT ( [Date], "Q" )
)
```

Mark `Dim Date` as the date table on `Dim Date[Date]`.

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

```DAX
Vacancy Count =
DISTINCTCOUNT ( fact_vacancy_day_vic[vacancy_id] )
```

```DAX
Average Vacancy Days =
DIVIDE ( [Vacancy Days], [Vacancy Count] )
```

```DAX
Vacancies <= 21 Days =
COUNTROWS (
    FILTER (
        VALUES ( fact_vacancy_day_vic[vacancy_id] ),
        CALCULATE ( [Vacancy Days] ) <= 21
    )
)
```

```DAX
Vacancies > 21 Days =
COUNTROWS (
    FILTER (
        VALUES ( fact_vacancy_day_vic[vacancy_id] ),
        CALCULATE ( [Vacancy Days] ) > 21
    )
)
```

```DAX
Vacancies <= 48 Days =
COUNTROWS (
    FILTER (
        VALUES ( fact_vacancy_day_vic[vacancy_id] ),
        CALCULATE ( [Vacancy Days] ) <= 48
    )
)
```

```DAX
Vacancies > 48 Days =
COUNTROWS (
    FILTER (
        VALUES ( fact_vacancy_day_vic[vacancy_id] ),
        CALCULATE ( [Vacancy Days] ) > 48
    )
)
```

```DAX
Pct <= 21 Days =
DIVIDE ( [Vacancies <= 21 Days], [Vacancy Count] )
```

```DAX
Pct <= 48 Days =
DIVIDE ( [Vacancies <= 48 Days], [Vacancy Count] )
```

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

- `vacancy_id`
- `vacancy_origin`
- `vacancy_reason`
- `vacancy_start_date`
- `vacancy_end_exclusive`
- `full_vacancy_days`
- `full_tenantable_days`
- `full_untenantable_days`
- `full_other_days`
- `meets_21_day_benchmark`
- `meets_48_day_benchmark`

From `dim_active_vacancy_rule_parameters`:

- `rule_name`
- `offset_days`
- `effective_from`
- `comment`
- `updated_by`
- `updated_at`

Hide technical columns such as codes, join keys that users do not need, and intermediate fields.

## Important Modeling Notes

- Use measures from `fact_vacancy_day_vic` on any page that must respect the selected date range.
- Treat the `full_*` columns in `fact_vacancy_interval_vic` as lifetime interval totals, not selected-period totals.
- Label `vacancy_end_exclusive` clearly in the report so users do not mistake it for a plain inclusive end date.
- Keep `dim_active_vacancy_rule_parameters` disconnected and visible for governance only.

## Filter Mapping

Use these filters:

- `Entity` = `dim_property_vic[entity]`
- `From Date` / `To Date` = `Dim Date[Date]`
- `Ownership` = `dim_property_vic[ownership]`
- `CAH Program` = `dim_property_vic[housing_program]`
- `Property Source` = `dim_property_vic[property_source]`
