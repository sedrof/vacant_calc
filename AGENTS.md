# Repository Instructions For Future LLM And Coding Agents

This repo is a Fabric delivery pack for the `VACANCY REPORTING - VIC` report.

## Read Order

Before changing anything, read these files in this order:

1. `docs/project_overview.md`
2. `docs/fabric_implementation.md`
3. `docs/semantic_model.md`
4. `docs/report_pages.md`
5. `docs/tables.md`

If the task is about date corrections or source timing issues, also read:

- `vacancy_rule_parameter_maintenance_notebook.py`

If the task is about notebook logic, use:

- `vacancy_reporting_vic_notebook.py`

## Source Of Truth

Use this priority order when requirements conflict:

1. Explicit user instruction in the current conversation
2. Confirmed workbook logic from `Vacant Calc.xlsx`
3. Current implementation in `vacancy_reporting_vic_notebook.py`
4. Documentation in `docs/`
5. Older notes or prose that are not backed by data logic

Do not invent business rules to fill gaps.

## Business Rules That Must Be Preserved

- Vacancy after tenancy end starts from the corrected tenancy end boundary.
- Vacancy before the first tenancy starts from the corrected property start boundary.
- Vacancy ending against the next tenancy uses the corrected next-start boundary.
- Void days are a subset of vacancy days.
- `Tenantable Days` are vacancy days that are not void days.
- `Other Days` must remain `0` unless a real rule and source are confirmed.

## Parameter Governance

- Date correction offsets are governed in Fabric through `vacancy_reporting.cfg_vacancy_rule_parameters`.
- Do not move these controls into report-side writeback or slicer-driven logic for the official report.
- The report may display the active configuration, but should not be the system of record for editing it.

## Modeling Rules

- Keep the daily-grain fact table because it is required for reliable `From Date` / `To Date` filtering.
- Treat `vacancy_end_exclusive` as the technical boundary used for correct day counting.
- If a report needs a user-facing inclusive end date, derive or label it clearly instead of changing the storage logic.
- Do not activate a `Keys` relationship until the engagement mapping is confirmed.

## Documentation Rules

- Any meaningful change to notebook logic must be reflected in `docs/project_overview.md` and `docs/fabric_implementation.md`.
- Any semantic model change must be reflected in `docs/semantic_model.md`.
- Any report/page/filter change must be reflected in `docs/report_pages.md`.
- Keep docs concise, implementation-focused, and readable by a human delivery team.

## Change Checklist

When making future changes, complete this checklist:

1. Update the implementation.
2. Update the affected docs.
3. Verify paths and references.
4. Run at least syntax-level validation where possible.
5. Call out any unresolved assumptions explicitly.

## Things To Avoid

- Do not overwrite user-authored business context without improving it materially.
- Do not add unsupported assumptions for `Other Days`, exemptions, or `Keys` joins.
- Do not convert operational rules into hidden report-layer logic when they belong in the data layer.
- Do not remove auditability to make the model look simpler.
