you are the fabric assistant who will translate all the data we have here from different sources. and give clear insutructions of how to implement this to our fabric. 

you will be responsible to create the notebooks.py , semantic models/ relations instructions/ report page.

you will give detailed instructions copy/paste ready for the fabric. 

first you need to understand the Vacant calc.xlsx file
we also have word file `  

Report Overview  

REPORT  
NAME 

VACANCY REPORTING - VIC 

REPORT 
PURPOSE  

To provide regulatory annual vacancy reporting for Housing Registrar Victoria, using system-generated data to accurately calculate vacancy turnaround times. This report will enable Evolve Housing to assess compliance against the required benchmarks of 21 days and 48 days, without the need for manual calculations. 

The report supports consistent, auditable, and timely reporting, ensuring vacancy performance can be reliably measured and demonstrated for regulatory compliance purpose 

REPORT  

BENEFITS 

Automating the vacancy turnaround time calculations will deliver significant efficiency and accuracy benefits. Currently, manual calculations take approximately 5–7 business days to complete. This report will eliminate the need for manual effort by providing real-time, system-generated results.  

The availability of this report will enable Resident Services to regularly monitor vacancy turnaround performance without manual intervention. It will also support proactive identification of properties that are not meeting the required benchmarks, allowing timely action to improve performance and ensure ongoing compliance with regulatory requirements 

AUDIENCE 

GGAL, Resident Services (VIC), EH Management 

FREQUENCY 

GGAL – Annually, Resident Services – ad hoc (real time) 

 

 

 

VERSION 

DATE 

REPORT OWNER / AUTHOR 

0.1  

13/03/2026  

Mona Singh 

 

 

Data Requirements 

DATA SOURCES 

TechOne 

List all the data sources that will be used to compile the report (e.g., databases, systems, spreadsheets, external data). 

DATA COLLECTION METHOD 

No data collection required – obtained from TechOne DB 

Describe how to collect the data (automatically, manually, or via a third-party service). 

DATA UPDATE FREQUENCY 

Overnight Update from TechOne 

Indicate how often to update/refresh the data.  

Content Requirements 

DATA FIELDS 

 

Specify the data output fields required for the report 

 

 

 

Replicate the NSW Vacancy Report (NRSCH) data fields  

In addition, add: 

Each vacancy to be split into their distinct periods: 

Days Vacant (tenantable)- refer calculation 

Days Vacant (untenantable - voids) – refer calculation 

Days Vacant (other) – refer calculation 

Note:  A ‘actual vacancy’ typically passes through a combination of stages prior to being tenanted. 

Property Start Date 

Property End Date 

 

Report must include all new vacant acquisitions and all vacant properties – refer to Appendix for definitions on the 3 days vacant categories. 

ANALYSIS/CALCULATIONS 

 

Specify whether there are any analysis/calculations required and provide details of the analysis 

 

Days vacant – based on the start and end date selected in the parameters, provide the days of each vacancy stage as per above split i.e. tenantable, untenantable, other 

KEY METRICS / INDICATORS 

Not applicable 

List all the metrics or performance indicators that will be included in the report. 

FILTERS AND DATA BREAKDOWNS 

Global Filter for system: 

Entity 

To and From dates 

Ownership  

CAH Program (relating to the entity & ownership selected) 

Property Source (relating to the entity & ownership selected) 

 

Enable multi selection 

Specify whether global filters are required or down the data is to be broken down by categories (e.g., time, department, geography). 

HISTORICAL DATA COMPARISON 

Based on the From and To dates selected in the parameters 

State whether or not the report will compare current data to historical data for trend analysis. 

 

Format and Layout 

REPORT FORMAT 

Excel report output 

Indicate the format you will be using (e.g., PDF, Excel, web-based dashboard). 

LAYOUT 

  Table 

Describe the layout or provide a sketch. (Include charts, tables, text sections, etc.). 

 

 

Delivery Method 

DISTRIBUTION METHOD 

No distribution required, will be run by GAL annually and Resident Services as required 

Indicate how to distribute the report to the audience (e.g., email, online portal, print). 

SECURITY / CONFIDENTIALITY REQUIREMENTS 

 Internal only 

Include any requirements for handling sensitive or confidential information. 

 

 

Implementation Plan 

TIMELINE 

  Next reporting due August 2026 

Include all the key milestones and deadlines required for the development and distribution of the report. 

RESOURCES REQUIRED 

 N/A 

Include any tools, subscriptions, or other resources required to produce the report. 

USER ACCEPTANCE TESTING 

 

Indicate who is responsible for User Acceptance Testing  

Mona Singh 

 

 

Mockup  

 

Mockup of report parameters: 

 

Entity 

From Date: 				To Date: 

Property Program 

Support Partner  

 

Approval and Review Process 

REVIEWERS 

 Suzanne Prabhudesai 

List the individuals or groups responsible for reviewing the report before distribution. 

APPROVAL PROCESS 

Suzanne Prabhudesai 

Melissa Scardino 

Identify who must approve the report before you distribute it. 

 

Revision History 

VERSION  

DATE 

REVISIONS APPLIED 

REVISED BY 

 



Appendix 

 

Days vacant definitions:  

 

Days vacant (tenantable)  

  

Total number of days tenancy units were vacant (tenantable) during the reporting period.  

Vacant (tenantable): A tenancy unit that is ready to be occupied, including:  

units where maintenance has been completed  

units that are difficult to tenant (e.g. geographically isolated, a lack of suitable tenants)  

new tenancy units where a Certificate of Occupancy has been issued  

purchased tenancy units that are ready to be occupied from the date of settlement  

units where a third-party nomination agreement is in place  

  

Days vacant (untenantable) 

  

Total number of days tenancy units were vacant (untenantable) during the reporting period.  

Vacant (untenantable): An unoccupied tenancy unit that requires maintenance to be ready for occupation, including:  

damaged units (including contamination)  

units awaiting insurance evaluation  

newly acquired or newly built tenancy units where maintenance is required prior to occupancy  

vacated maintenance  

units damaged or occupied by squatters  

units where tenants have left goods behind  

  

  

Days vacant (other) 

  

Total number of days tenancy units were vacant (other) during the reporting period.  

Vacant (other): Tenancy units that have been identified prior to vacancy for removal from the usual turnaround cycle. This may include for:  

forthcoming sale  

capital works1 such as: buildings or extensions, alterations, or improvements to a building  

structural improvements such as sealed driveways, fences and retaining walls.  

  

tenant welfare (including public health precautions)  

leaving a unit vacant to accommodate a tenant during capital works at the tenant’s principal residence  

neighbour fatigue  

accommodating a caretaker on site  

 

 

 

 

 `

 so the main goal is to create this new vacancy table. 

 but theres some notes you need to consider before, the current tables we have above which we will use to build the new table/report. needs some changes

 in the `Start Date	End Date ` as you see theres a formula in start +1 and end -1. as the dates recieved from the server is 1 day difference.

 the whole point we want same as this table `                                                                
    Start Date	End Date 	Vac days	Vacancy Reason	void Start Date	Void End Date	Void days	Tenantable days	Untenantable Days	Exemption	PropID	Prop Addrees	Tenancy_End_ID	Tenancy_Start_ID	KeysID	VOID ID
 Vacancy for prop 223344	02/01/2026	04/04/2026	88		22/01/2026	30/01/2026	8	80	8				5678	05/04/2026		
                                                                
                                                                
 Void @ Prop223344	22/01/2026	30/01/2026	8													
                                                                
                                                                
    Tenantable		80													
    Untenantable		8													`
    ofc you can see the formulas from the excel file itself here `vacant calc.xlsx` so we will need to first create notebooks to clean the data etc and create this new table. and ofc the reports/semantic/measures etc. also about the 1 day difference we need to make it a variable that we can change as we want could be cool if can be changed via slicers at the report somehow.