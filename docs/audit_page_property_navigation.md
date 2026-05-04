# Audit Page Property Navigation

## Purpose

This guide explains how to make the `Vacancy Detail` table open the existing `Audit` page for the `property_id` on the selected row.

Target behavior:

- user is on `Vacancy Detail`,
- user selects or right-clicks a row,
- Power BI opens the `Audit` page,
- the `Audit` page is filtered to that row's `property_id`,
- the page shows all relevant audit detail for that property.

## Important Limitation

Power BI native table visuals do not support a true one-click row hyperlink action inside the row itself.

The two practical patterns are:

1. right-click the row and use `Drillthrough`
2. click the row once, then click a drillthrough button

If you want the cleanest user experience, use both:

- keep right-click drillthrough enabled
- add a visible button above the table such as `Open Audit`

## Recommended Design Decision

Your current `Audit` page is already a drillthrough-style page.

If you want the current `Audit` page to open by `property_id`, you have two choices:

1. Replace the current `vacancy_id` drillthrough behavior with `property_id`
2. Duplicate the current `Audit` page first, then keep:
   - `Audit` for `vacancy_id`
   - `Audit By Property` for `property_id`

Recommended option:

- duplicate the current page first if you still need vacancy-level audit

If you do not need the old vacancy-level drillthrough anymore, you can reuse the current `Audit` page directly.

## Best Drillthrough Field

Use:

- `dim_property_vic[property_id]`

Why:

- it filters the audit tables cleanly through the model relationships
- it is the shared property hub for:
  - `fact_vacancy_interval_vic`
  - `fact_vacancy_day_vic`
  - `audit_property_vic`
  - `audit_tenancy_vic`
  - `audit_void_vic`
  - `audit_keys_vic`
  - `audit_exceptions_vic`

## Step 1: Prepare The Audit Page

Open the destination page in Power BI.

If you are reusing the current `Audit` page:

1. Click the `Audit` page.
2. Open the `Drillthrough` pane.
3. Remove `fact_vacancy_interval_vic[vacancy_id]` if you want property-level navigation only.
4. Add `dim_property_vic[property_id]` to the `Drillthrough` well.
5. Keep `Keep all filters` on if you want the current report context, such as date or entity filters, to continue to the Audit page.

If you are duplicating the page:

1. Duplicate `Audit`.
2. Rename the copy to something clear such as `Audit By Property`.
3. On the copied page, remove `fact_vacancy_interval_vic[vacancy_id]` from the `Drillthrough` well.
4. Add `dim_property_vic[property_id]` to the `Drillthrough` well.
5. Keep `Keep all filters` on unless you specifically want a clean property-only landing page.

## Step 2: Check The Audit Page Visuals

The current Audit page can work with property drillthrough because the visuals already use tables that are tied to property or vacancy.

Expected behavior after property drillthrough:

- vacancy day table shows all vacancy-day rows for vacancies under that property
- void interval table shows all void rows for that property
- keys audit table shows keys rows for that property

If you want the page title to reflect the selected property, add a title measure such as:

```DAX
Selected Property Title =
"Audit - Property ID: " & COALESCE ( SELECTEDVALUE ( dim_property_vic[property_id] ), "No Property Selected" )
```

Then use conditional formatting or a card visual to display it.

## Step 3: Make Sure The Source Table Has Property ID

On the `Vacancy Detail` page, the source table must contain a property field.

Recommended field:

- `dim_property_vic[property_id]`

If your table currently uses:

- `fact_vacancy_interval_vic[property_id]`

that may still work, but the safest setup is to display the `dim_property_vic[property_id]` version in the table so the drillthrough source and destination use the same field.

Recommended action:

1. In the `Vacancy Detail` table, replace the displayed property column with `dim_property_vic[property_id]`, or
2. keep the existing property column visible, but also include `dim_property_vic[property_id]` in the visual if needed for reliable drillthrough

## Step 4: Use Right-Click Drillthrough

This is the simplest working setup.

User flow:

1. go to `Vacancy Detail`
2. right-click the selected row
3. choose `Drillthrough`
4. choose `Audit` or `Audit By Property`

Result:

- the page opens filtered to the selected `property_id`

## Step 5: Add A Drillthrough Button

If you want a cleaner workflow than right-click:

1. stay on `Vacancy Detail`
2. insert a `Button`
3. label it `Open Audit`
4. turn `Action` on
5. set `Type` = `Drillthrough`
6. set `Destination` = `Audit` or `Audit By Property`

User flow:

1. click a row in the `Vacancy Detail` table
2. click `Open Audit`

Result:

- the Audit page opens for that selected property

This is usually the best compromise because it feels close to a row-click action while staying within normal Power BI behavior.

## Step 6: Add A Back Button

On the Audit page:

1. insert a `Back` button
2. keep it in the page header area

This makes the navigation much easier for report users.

## Recommended Final UX

Best user experience for this report:

- source page: `Vacancy Detail`
- destination page: `Audit By Property` or `Audit`
- drillthrough field: `dim_property_vic[property_id]`
- user action:
  - select row
  - click `Open Audit`

Keep right-click drillthrough available as a secondary option.

## Validation Checklist

Test these cases after setup:

1. select one vacancy row and open the Audit page
2. confirm the Audit page only shows the chosen property
3. confirm the void table only shows rows for that property
4. confirm the keys table only shows rows for that property
5. confirm the vacancy-day table only shows vacancy-day rows for that property
6. confirm the Back button returns to `Vacancy Detail`

## Troubleshooting

### The drillthrough option does not appear

Check:

- the source visual contains `property_id`
- the destination page has `dim_property_vic[property_id]` in the `Drillthrough` well

### The button is disabled

Check:

- a row is actually selected in the source table
- the destination page drillthrough field is configured

### The Audit page still shows all properties

Check:

- `dim_property_vic[property_id]` relationships are active
- the page is using the correct drillthrough field
- the source table is passing the property field you configured

### The Audit page only shows one vacancy, not the whole property

This usually means:

- `fact_vacancy_interval_vic[vacancy_id]` is still in the `Drillthrough` well

Remove it if you want the page to filter by property only.

### The current Audit page must stay vacancy-specific

Do not overload it.

Instead:

1. duplicate the page
2. rename it `Audit By Property`
3. configure the duplicate for `property_id` drillthrough

That is the cleanest long-term design.

## Recommendation

For your current report, the safest implementation is:

1. duplicate the current `Audit` page
2. create `Audit By Property`
3. use `dim_property_vic[property_id]` as the drillthrough field
4. add an `Open Audit` drillthrough button on `Vacancy Detail`

That gives you property-level navigation without breaking any existing vacancy-level audit behavior.
