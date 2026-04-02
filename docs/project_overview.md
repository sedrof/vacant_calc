# Vacancy Reporting VIC

## Purpose

This project delivers a Fabric-based vacancy reporting solution for Victoria that replaces manual vacancy turnaround calculations with a governed, repeatable, and auditable process.

The primary reporting goal is to measure vacancy performance against the required benchmarks of `21 days` and `48 days` using system-generated data from TechOne.

## Audience And Usage

- `GGAL`: annual regulatory reporting
- `Resident Services (VIC)`: ad hoc operational use
- `EH Management`: oversight and performance monitoring

The report must support both formal annual reporting and day-to-day investigation of vacancy performance.

## Source Inputs

This repo currently uses three main source inputs:

1. `Vacant Calc.xlsx`
   This is the key logic reference. It shows the date-boundary behavior used to calculate vacancy periods.
2. `tables.md`
   This lists the available lakehouse or warehouse source tables and the important columns.
3. Business context from the original report brief
   This provides the audience, filter expectations, report purpose, and regulatory framing.

## Confirmed Business Logic

The workbook establishes the most important date rules:

1. If a tenancy ends on `2026-01-01`, the vacancy starts on `2026-01-02`.
2. If the next tenancy starts on `2026-04-05`, the vacancy inclusive end date is `2026-04-04`.
3. A new property vacancy starts from the property start date, not from a tenancy end.
4. Void periods are a subset of the vacancy period.
5. `Tenantable Days` are vacancy days that are not in a void period.

To make the solution stable in Fabric, the notebook stores the end boundary as an exclusive date:

- user-facing inclusive end example: `2026-04-04`
- stored technical end boundary: `2026-04-05`

This is deliberate. It prevents off-by-one errors and makes daily date slicing reliable.

## Configurable Date Corrections

The source data may be one day behind the Australian business date because of server timing. That correction is now governed in Fabric through a config table, not hardcoded in the report.

The active rules are stored in:

- `vacancy_reporting.cfg_vacancy_rule_parameters`

The active values published for reporting are stored in:

- `vacancy_reporting.dim_active_vacancy_rule_parameters`

This allows controlled changes without editing the report each time a date correction rule changes.

## Required Output

The report must provide:

- vacancy counts,
- vacancy days,
- tenantable days,
- untenantable days,
- benchmark performance against `21` and `48` days,
- property-level operational detail,
- an audit trail showing how daily vacancy days were classified.

The report must also support these main filters:

- `Entity`
- `From Date`
- `To Date`
- `Ownership`
- `CAH Program`
- `Property Source`

## Current Solution Design

The implementation uses:

- a Fabric notebook to build the reporting tables,
- a semantic model on top of those tables,
- a Power BI report with summary, detail, audit, and config views.

The main notebook is:

- `../vacancy_reporting_vic_notebook.py`

The notebook creates these reporting tables:

- `vacancy_reporting.dim_property_vic`
- `vacancy_reporting.dim_active_vacancy_rule_parameters`
- `vacancy_reporting.fact_vacancy_day_vic`
- `vacancy_reporting.fact_vacancy_interval_vic`
- `vacancy_reporting.fact_void_interval_vic`
- `vacancy_reporting.stg_keys_vic`

## Scope Decisions

These decisions are intentional and should not be changed without evidence:

- `Resident_Data` is not part of the first vacancy calculation build because it is not needed for the current logic.
- `Keys` is staged only. It is not related into the main model until the engagement mapping is confirmed.
- `Other Days` remains `0` because no valid source rule has been confirmed.
- `Property Program` is currently used as `Property Source`.

## Delivery Sequence

Use this order for implementation:

1. Review this overview and `docs/tables.md`.
2. Run the notebook in Fabric.
3. Validate the config table and active rule values.
4. Build the semantic model.
5. Build the Power BI report pages.
6. Validate benchmark outputs against known workbook scenarios.

## Open Items

These items still require business confirmation before expansion:

- The exact rule for `Other Days`
- Whether any source tables need a permanent raw date shift
- How `Keys.PARENT_ENGAGEMENT_ID` should map to vacancy or property events
- Whether `Property Program` is definitively the right field for `Property Source`

## Success Criteria

The project is successful when:

- the report reproduces the workbook boundary logic,
- the date corrections are governed in Fabric,
- the report is auditable at vacancy-day level,
- the report supports exportable operational detail,
- the process can be rerun without manual recalculation.


but 93 means we exceeded the quartely ? since we have this formula on the excel for Vac days `=MIN(O8,M2)-N8`  O8=`04/04/2026`, M2=`31/03/2026`,
  N8=`02/01/2026` and the Vac days = 88. because we have Report to date 31/03/2026