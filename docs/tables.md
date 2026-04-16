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
- `[DataSet.PROPERTYID],
			[DataSet.ENGAGEMENTID],
			[DataSet.PROPERTYNUMBER],
			[DataSet.CURRENTSTAGE],
			[DataSet.CURRENTSTAGECODE],
			[DataSet.PROPERTYSHORTADDRESS],
			[DataSet.ACTIVECODE],
			[DataSet.INACTIVEDATE],
			[DataSet.NOTES],
			[DataSet.STARTDATE],
			[DataSet.ASSIGNEDUSER],
			[DataSet.LATESTMARKETRENTDATE],
			[DataSet.LATESTMARKETRENT],
			[DataSet.TERMINATIONDATE],
			[DataSet.LOTNUMBER],
			[DataSet.UNITNO],
			[DataSet.STREETNO],
			[DataSet.STREETNAME],
			[DataSet.SUBURB],
			[DataSet.STATE],
			[DataSet.POSTCODE],
			[DataSet.HOUSINGPROGRAM],
			[DataSet.HOUSINGPROGRAMD],
			[DataSet.PROPERTYPROGRAM],
			[DataSet.PROPERTYPROGRAMD],
			[DataSet.PROPERTYSTARTDATE],
			[DataSet.FACSHVPRN],
			[DataSet.FUTUREUSE],
			[DataSet.FUTUREUSED],
			[DataSet.HOLDINGTYPE],
			[DataSet.HOLDINGTYPED],
			[DataSet.FACSDCJLEASEDURATION],
			[DataSet.FACSDCJLEASEDURAD],
			[DataSet.PURPOSE],
			[DataSet.PURPOSED],
			[DataSet.PROPERTYTYPE],
			[DataSet.PROPERTYTYPED],
			[DataSet.ALLOCATIONCATEGORY],
			[DataSet.ALLOCATIONCATEGORYD],
			[DataSet.VESTED],
			[DataSet.USEFOR],
			[DataSet.USEFORD],
			[DataSet.DISABILITYMODIFICATIONS],
			[DataSet.DISABILITYMODIFICAD],
			[DataSet.OTHERFACSPROPERTY],
			[DataSet.PROPERTYLGA],
			[DataSet.PROPERTYLGAD],
			[DataSet.TENANCYMGTRESPONSIB],
			[DataSet.TENANCYMGTRESPONSIBD],
			[DataSet.NOOFTENANCIES],
			[DataSet.NOOFTENANCIESD],
			[DataSet.PARKING],
			[DataSet.PARKINGD],
			[DataSet.COUNTPARKING],
			[DataSet.WATERRECHARGE],
			[DataSet.CARSPACES],
			[DataSet.CONSTRUCTIONTYPE],
			[DataSet.CONSTRUCTIONTYPED],
			[DataSet.RATESSERVICES],
			[DataSet.NEWTOSOCIALHOUSING],
			[DataSet.NUMBEROFBEDROOMS],
			[DataSet.NUMBEROFBEDROOMSD],
			[DataSet.MAXLEASES],
			[DataSet.LOCATIONOFCT],
			[DataSet.LOCATIONOFCTD],
			[DataSet.ORIGINALFUNDINGPROGRAM],
			[DataSet.ORIGINALFUNDINGPROGRAD],
			[DataSet.EQUIPMENTPROVIDED],
			[DataSet.ASSETCLASS],
			[DataSet.ASSETCLASSD],
			[DataSet.YEAROFCONSTRUCTION],
			[DataSet.YEAROFCONSTRUCTIOND],
			[DataSet.FPRCATEGORY],
			[DataSet.FPRCATEGORYD],
			[DataSet.ENTITY],
			[DataSet.ENTITYD],
			[DataSet.MORTGAGELENDER],
			[DataSet.MORTGAGELENDERD],
			[DataSet.SUPPORTPARTNER],
			[DataSet.SUPPORTPARTNERD],
			[DataSet.OWNERSHIP],
			[DataSet.OWNERSHIPD],
			[DataSet.ACHLPROPERTYTRANSFERNO],
			[DataSet.STRATAIFAPPLICABLE],
			[DataSet.STRATAIFAPPLICABLED],
			[DataSet.TITLEHELD],
			[DataSet.TITLEHELDD],
			[DataSet.TRANSFEREBATCHNO],
			[DataSet.TITLEREFERENCE],
			[DataSet.PROPNOTES],
			[DataSet.RESPONSIVEMAINTENANCE],
			[DataSet.RESPONSIVEMAINTENANCED],
			[DataSet.PLANNEDMAINTENANCE],
			[DataSet.PLANNEDMAINTENANCED],
			[DataSet.CAPITALMAINTENANCE],
			[DataSet.CAPITALMAINTENANCED],
			[DataSet.CONTRACTOR],
			[DataSet.PROPERTYASSETREGISTER],
			[DataSet.PROPERTYASSETNUMBER],
			[DataSet.OVER55SBLOCK],
			[DataSet.WHEELACCESSABLE],
			[DataSet.MODIFIED],
			[DataSet.MODIFICATIONSSPECIFY],
			[DataSet.DISTANCETOSHOPS],
			[DataSet.DISTANCETOSHOPSD],
			[DataSet.FLOORING],
			[DataSet.FLOORINGD],
			[DataSet.STAIRSFRONT],
			[DataSet.YARDLEVEL],
			[DataSet.YARDLEVELD],
			[DataSet.BACKYARDSIZE],
			[DataSet.BACKYARDSIZED],
			[DataSet.DISTANCETOTRANSPORT],
			[DataSet.DISTANCETOTRANSPORTD],
			[DataSet.STAIRSBACK],
			[DataSet.BATHROOM],
			[DataSet.BATHROOMD],
			[DataSet.FLOOR],
			[DataSet.FLOORD],
			[DataSet.BACKYARD],
			[DataSet.BACKYARDD],
			[DataSet.BUILTINS],
			[DataSet.BUILTINSD],
			[DataSet.ADDITIONALNOTES],
			[DataSet.NOOFEXTINGUISHERS],
			[DataSet.ABE],
			[DataSet.AIRWATER],
			[DataSet.CO2],
			[DataSet.WETCHEMICAL],
			[DataSet.BLANKETS],
			[DataSet.HOSEREEL],
			[DataSet.HYDRANTS],
			[DataSet.FIREINDICATIONPANEL],
			[DataSet.TYPE],
			[DataSet.NOOFDETECTORS],
			[DataSet.EVACLIGHT],
			[DataSet.SPRINKLER],
			[DataSet.WATERSUPPLY],
			[DataSet.PIPETYPE],
			[DataSet.HEADS],
			[DataSet.KFACTORS],
			[DataSet.SOLIDCOREDOORS],
			[DataSet.FIRERATESDOORS],
			[DataSet.FIREDETECTSYSTEM],
			[DataSet.EVACUATIONDIAGRAM],
			[DataSet.SPRINKLERBLOCKPLAN],
			[DataSet.LASTSERVICEDATE],
			[DataSet.LASTBACKFLOWTESTDATE],
			[DataSet.LASTAFSSDATE],
			[DataSet.REMARKS],
			[DataSet.DATELASTUPLOADED],
			[DataSet.USERLASTUPLOADED],
			[DataSet.FLOORS],
			[DataSet.BRICK],
			[DataSet.CONCRETEPANEL],
			[DataSet.STEELMETALIRON],
			[DataSet.TIMBERFLOORSWALLS],
			[DataSet.TIMBERFRAMED],
			[DataSet.TIMBERMEZZANINE],
			[DataSet.CONCRETEBLOCK],
			[DataSet.CONCRETEFLOOR],
			[DataSet.EPSEXTERNALWALLS],
			[DataSet.TILEDROOF],
			[DataSet.ASBESTOS],
			[DataSet.EPSINTERNALWALLS],
			[DataSet.ACPINTERNALWALLS],
			[DataSet.ACPEXTERNALWALLS],
			[DataSet.OTHERSPECIFY],
			[DataSet.OTHERFLOORSSPECIFY],
			[DataSet.WALLS],
			[DataSet.CONCRETEBLOCK2],
			[DataSet.STEELMETALIRON2],
			[DataSet.TIMBERFLOORSWALLS2],
			[DataSet.TIMBERFRAMED2],
			[DataSet.TIMBERMEZZANINE2],
			[DataSet.BRICK2],
			[DataSet.CONCRETEPANEL2],
			[DataSet.CONCRETEFLOOR2],
			[DataSet.ASBESTOS2],
			[DataSet.EPSINTERNALWALLS2],
			[DataSet.EPSEXTERNALWALLS2],
			[DataSet.ACPINTERNALWALLS2],
			[DataSet.ACPEXTERNALWALLS2],
			[DataSet.TILEDROOF2],
			[DataSet.OTHERSPECIFY2],
			[DataSet.OTHERWALLSSPECIFY],
			[DataSet.ROOFS],
			[DataSet.BRICK3],
			[DataSet.CONCRETEBLOCK3],
			[DataSet.CONCRETEPANEL3],
			[DataSet.CONCRETEFLOOR3],
			[DataSet.STEELMETALIRON3],
			[DataSet.TIMBERFLOORSWALLS3],
			[DataSet.TIMBERFRAMED3],
			[DataSet.TIMBERMEZZANINE3],
			[DataSet.ASBESTOS3],
			[DataSet.EPSINTERNALWALLS3],
			[DataSet.EPSEXTERNALWALLS3],
			[DataSet.ACPINTERNALWALLS3],
			[DataSet.ACPEXTERNALWALLS3],
			[DataSet.TILEDROOF3],
			[DataSet.OTHERSPECIFY3],
			[DataSet.OTHERROOFSPECIFY],
			[DataSet.FIRE],
			[DataSet.SPRINKLERDUALWATER],
			[DataSet.SPRINKLERSINGLEWATER],
			[DataSet.FIREHOSEREELS],
			[DataSet.FIREEXTINGUISHERS],
			[DataSet.HARDWIREDSMOKEDETECTORS],
			[DataSet.THERMALALARMS],
			[DataSet.AUTOMATICFIREDOORS],
			[DataSet.OTHERSPECIFY1],
			[DataSet.OTHERFIRECODESPECIFY],
			[DataSet.SECURITY],
			[DataSet.ALARMMONITORED],
			[DataSet.ALARMLOCAL],
			[DataSet.SECURITYPATROL],
			[DataSet.BARSWINDOWSORDOORS],
			[DataSet.SECURITYCARDACCESS],
			[DataSet.DEADLOCKSONALLOPENINGS],
			[DataSet.LOCKEDGATESAFTERHOURS],
			[DataSet.CARETAKERONPREMISES],
			[DataSet.CANINE],
			[DataSet.FLOORS2],
			[DataSet.FLOORSD],
			[DataSet.WALLSSTRUCTURAL],
			[DataSet.WALLSSTRUCTURALD],
			[DataSet.SMOKEALARMS],
			[DataSet.HYDRANT],
			[DataSet.SWIPEACCESS],
			[DataSet.HEATDETECTOR],
			[DataSet.EXTINGUISHERS],
			[DataSet.HYDRANTBOOSTER],
			[DataSet.FIPPANEL],
			[DataSet.ROOF],
			[DataSet.ROOFD],
			[DataSet.FIRECODE],
			[DataSet.FIRECODED],
			[DataSet.OTHERSECURITYCODESPECI],
			[DataSet.SECURITYCODE],
			[DataSet.SECURITYCODED],
			[DataSet.HOUSINGMANAGER],
			[DataSet.HOUSINGMANAGERD],
			[DataSet.PORTFOLIO],
			[DataSet.PORTFOLIOD],
			[DataSet.WORKORDERPORTFOLIO],
			[DataSet.WORKORDERPORTFOLIOD],
			[DataSet.TECHNICALOFFICER],
			[DataSet.TECHNICALOFFICERD],
			[DataSet.WORKORDERREGION],
			[DataSet.WORKORDERREGIOND],
			[DataSet.NDISDWELLINGNUMBER],
			[DataSet.FIRESPRINKLERSHOUSE],
			[DataSet.FIRESPRINKLERSHOUSED],
			[DataSet.ACTIONS],
			[DataSet.SDAREGION],
			[DataSet.SDAREGIOND],
			[DataSet.SEPARATEBREAKOUTROOM],
			[DataSet.SEPARATEBREAKOUTROOMD],
			[DataSet.TYPEOFSDA],
			[DataSet.TYPEOFSDAD],
			[DataSet.NDIAHOMEMODIFICATION],
			[DataSet.NDIAHOMEMODIFICATIOND],
			[DataSet.DESIGNCATEGORY],
			[DataSet.DESIGNCATEGORYD],
			[DataSet.LANDSHAREDOTHERDWEL],
			[DataSet.LANDSHAREDOTHERDWELD],
			[DataSet.DWELLINGCLAIMINGOOA],
			[DataSet.DWELLINGCLAIMINGOOAD],
			[DataSet.NOOFRESIDENTSHOUSED],
			[DataSet.OOASHAREDWITHOTHDWEL],
			[DataSet.PARTOFINTENTIONALCOMM],
			[DataSet.PARTOFINTENTIONALCOMD],
			[DataSet.CRUSER1],
			[DataSet.CRDATEI1],
			[DataSet.CRTIMEI1],
			[DataSet.LASTMODUSER],
			[DataSet.LASTMODDATEI],
			[DataSet.VERS1],
			[DataSet.STARTDATEFY],
			[DataSet.DISPOSALDATEFY],
			[TotalRecordCount],
			[Key],
			[Messages]

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

Additional confirmed fields available from the sample tenancy extract:

- `DataSet.LATESTRENTREVIEWAMOUNT`
- `DataSet.LATESTCONTRIBUTEDRENT`
- `DataSet.LATESTCRAAMOUNT`
- `DataSet.LATESTRRC25OFDSP`
- `DataSet.LATESTCONTINUITYSUPPORT`
- `DataSet.LATESTVBCAMOUNT`
- `DataSet.STATE`
- `DataSet.STATEDESC`
- `DataSet.SHERIFFEVICTION`
- `DataSet.SHERIFFEVICTIONDESC`
- `DataSet.DATEOFOFFER`
- `DataSet.OFFERACCEPTED`
- `DataSet.INITIALLEASEPERIODDESC`
- `DataSet.TENANCYPAYWAYID`
- `DataSet.PREVIOUSHOUSINGSTATUS`
- `DataSet.PREVHOUSINGSTATUSDESC`
- `DataSet.TENANCYTYPE`
- `DataSet.TENANCYTYPEDESC`
- `DataSet.TOTALASSESSABLEINCOME`
- `DataSet.INCOMESOURCE`
- `DataSet.INCOMESOURCEDESC`
- `DataSet.TOTALNONASSESINCOME`
- `DataSet.RENTREVIEWOFFICER`
- `DataSet.RENTREVIEWOFFICERDESC`
- `DataSet.BATCHTRANSFERNO`
- `DataSet.TRANSFERNO`
- `DataSet.WHERENEXTHOUSED`
- `DataSet.WHERENEXTHOUSEDDESC`
- `DataSet.HOMELESSNESS`
- `DataSet.HOMELESSNESSDESC`
- `DataSet.CONTACTID`
- `DataSet.EMAILCONTACT`
- `DataSet.DATEOFBIRTHCONTACT`
- `DataSet.CLIENTIDPAYWAY`
- `DataSet.TENANCYSUMMARYPROPERTY`
- `DataSet.PROPERTYNUMBERPROPERTY`
- `DataSet.CURRENTSTAGEPROPERTY`
- `DataSet.CURRENTSTAGECODEPROP`
- `DataSet.HOUSINGMANAGERPROPERTY`
- `DataSet.HOUSINGMANAGERPROPDESC`
- `DataSet.HOUSINGPROGRAMPROPERTY`
- `DataSet.HOUSINGPROGRAMPROPDESC`
- `DataSet.PROPERTYPROGRAMPROPERTY`
- `DataSet.PROPPROGRAMPROPDESC`
- `DataSet.CRUSER1`
- `DataSet.CRDATEI1`
- `DataSet.CRTIMEI1`
- `DataSet.CRTERM1`
- `DataSet.CRWINDOW1`
- `DataSet.LASTMODUSER`
- `DataSet.LASTMODDATEI`
- `DataSet.LASTMODTIMEI`
- `DataSet.LASTMODTERM`
- `DataSet.LASTMODWINDOW`
- `DataSet.VERS1`
- `TotalRecordCount`
- `Key`
- `Messages`
- `DataSet.EVICTION_REASON_D`
- `DataSet.EVICTION_REASON`
- `data.EVICTION_REASON`

Recommended future tenancy fields for vacancy detail enrichment:

- `DataSet.TENANCYREFERENCE`
  Useful as a user-facing tenancy identifier alongside `vacancy_start_tenancy_id` and `vacancy_end_tenancy_id`.
- `DataSet.CURRENTSTAGE` and `DataSet.CURRENTSTAGECODE`
  Useful only if operations want to audit tenancy lifecycle status around the vacancy.
- `DataSet.TENANCYTYPEDESC`
  Useful if management wants to analyze vacancy performance by tenancy type.
- `DataSet.WHERENEXTHOUSEDDESC`
  Useful only for operational context after tenancy exit. It is not part of vacancy-day logic.
- `DataSet.OFFERACCEPTED` and `DataSet.DATEOFOFFER`
  Potentially useful for a future reletting workflow view, but not required for the current vacancy calculation.
- `DataSet.EVICTION_REASON_D`
  Only useful if the business wants to separate eviction-related exits from other end-of-tenancy reasons.

Current recommendation for the vacancy detail table:

- keep the current tenancy ID and tenancy date fields,
- add `TENANCYREFERENCE` later if users need a more readable tenancy identifier,
- do not add rent, income, contact, or client fields to the vacancy detail table unless a separate business requirement is approved.

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

This is currently enough to explain how vacancy boundaries were derived. A future enhancement can also carry `vacancy_start_tenancy_reference` and `vacancy_end_tenancy_reference` if the business wants human-readable tenancy references in the detail table.

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
