# Source Table Guide

## Purpose

This document maps the TechOne source tables that are relevant to the VIC vacancy reporting solution.

It is not intended to be a full data dictionary for every column in TechOne. It focuses on the tables and columns that matter for the current implementation.

## Warehouse Prefix

Use this warehouse prefix in Fabric:

```text
`Evolve-TechOne`.Shortcut.ev
```

## Tables In Scope

### 1. `Property`

Purpose:

- supplies property identity and reporting dimensions,
- supplies the property start date used for new-property vacancy logic,
- supplies filter attributes such as entity, ownership, and program.

Columns currently used by the notebook:

- `DataSet.PROPERTYID`
- `DataSet.PROPERTYNUMBER`
- `DataSet.PROPERTYSHORTADDRESS`
- `DataSet.SUBURB`
- `DataSet.STATE`
- `DataSet.POSTCODE`
- `DataSet.ENTITY`
- `DataSet.ENTITYD`
- `DataSet.OWNERSHIP`
- `DataSet.OWNERSHIPD`
- `DataSet.HOUSINGPROGRAM`
- `DataSet.HOUSINGPROGRAMD`
- `DataSet.PROPERTYPROGRAM`
- `DataSet.PROPERTYPROGRAMD`
- `DataSet.PROPERTYSTARTDATE`
- `DataSet.STARTDATE`
- `DataSet.TERMINATIONDATE`
- `DataSet.INACTIVEDATE`
- `DataSet.CURRENTSTAGE`
- `DataSet.CURRENTSTAGECODE`
- `DataSet.ACTIVECODE`

### 2. `Tenancy`

Purpose:

- supplies tenancy start and end boundaries,
- drives vacancy creation between one tenancy and the next,
- supplies tenancy end reason as the initial vacancy reason.

Columns currently used by the notebook:

- `DataSet.TENANCYID`
- `DataSet.TENANCYREFERENCE`
- `DataSet.PROPID`
- `DataSet.TENANCYSTARTDATE`
- `DataSet.TENANCYENDDATE`
- `DataSet.ENDOFTENANCYREASON`
- `DataSet.ENDOFTENANCYREASONDES`
- `DataSet.CURRENTSTAGE`
- `DataSet.CURRENTSTAGECODE`
- `DataSet.ACTIVECODE`
- `DataSet.INACTIVEDATE`

### 3. `Void`

Purpose:

- identifies untenantable periods within a vacancy,
- provides the void date range used to split vacancy days,
- provides reason and property condition context for audit.

Columns currently used by the notebook:

- `DataSet.VOID_ID`
- `DataSet.PROP_ID`
- `DataSet.VOID_REFERENCE`
- `DataSet.VOID_FROM_DATE`
- `DataSet.VOID_TO_DATE`
- `DataSet.VOID_REASON`
- `DataSet.VOID_REASON_D`
- `DataSet.PROPERTY_CONDITION`
- `DataSet.PROPERTY_CONDITION_D`
- `DataSet.KEY_REGISTER_ENG_ID`
### 4. `Keys`

Purpose:

- supports vacancy-related operational context,
- provides vacancy exemptions, property condition, and contractor/key handling dates,
- is matched through `PARENT_ENGAGEMENT_ID = property_id`.

Columns currently used by the notebook:

- `DataSet.KEY_ID`
- `DataSet.PARENT_ENGAGEMENT_ID`
- `DataSet.KEY_REFERENCE`
- `DataSet.DATE_RECEIVED_FROM_TENANT`
- `DataSet.OUTGOING_INSPECTION_DATE`
- `DataSet.CONTRACTOR_NOTIFIED_DATE`
- `DataSet.TO_LOCKBOX_ONSITE`
- `DataSet.CONTRACTOR_COLLECT_K_DATE`
- `DataSet.CONTRACTOR_NAME_COMMENTS`
- `DataSet.CONTRACTOR_RETURN_K_DATE`
- `DataSet.NEW_ACTIVATED_PROPERTY`
- `DataSet.VACANCY_EXEMPTIONS_C`
- `DataSet.VACANCY_EXEMPTIONS_DESC`
- `DataSet.PROPERTY_CONDITION`
- `DataSet.PROPERTY_CONDITION_D`

### 5. `Resident_Data`

Purpose:

- not required for the current vacancy logic,
- available for future reporting extensions if resident context becomes necessary.

It is intentionally not used in the current notebook.

## Current Join Logic

The current implementation uses these keys:

- `Property.PROPERTYID` to `Tenancy.PROPID`
- `Property.PROPERTYID` to `Void.PROP_ID`
- `Property.PROPERTYID` to `Keys.PARENT_ENGAGEMENT_ID`

For report enrichment, the notebook selects one representative keys row per vacancy using:

- matching `property_id`,
- preference for keys dates that fall inside the vacancy interval,
- then nearest keys date to the vacancy start date.

For vacancy detail reporting, the notebook also carries tenancy context into the vacancy interval output using:

- `vacancy_start_tenancy_id`, `vacancy_start_tenancy_start_date`, `vacancy_start_tenancy_end_date`
- `vacancy_end_tenancy_id`, `vacancy_end_tenancy_start_date`, `vacancy_end_tenancy_end_date`

These fields are derived by matching `Property.PROPERTYID` to `Tenancy.PROPID`.

## Important Data Notes

- Date correction offsets are applied in the notebook through governed Fabric parameters.
- Raw source date shifts are controlled separately for `Property`, `Tenancy`, `Void`, and `Keys`.
- If the confirmed TechOne rule is that source dates are one day behind, set `property_source_date_offset`, `tenancy_source_date_offset`, `void_source_date_offset`, and `keys_source_date_offset` to `1`.
- The notebook stores vacancy intervals using an exclusive end boundary for reliable day counting.
- The report uses the daily fact table as the main date-filtering layer.

## Future Extensions

Only extend the current source map after confirming the business rule that needs the new data.

Likely future areas:

- a real definition for `Other Days`,
- resident-level enrichments from `Resident_Data`,
- formal exemption logic if approved by the business.
