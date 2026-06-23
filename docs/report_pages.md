# Report Build Guide

## Objective

The report should support four reporting modes:

- management summary,
- exportable operational detail,
- audit and rule transparency.
- property-level source trace and validation.

This is not a presentation dashboard. Build it as a working operational report.

The global date slicer is a free management-selected reporting window. It is not tied to quarter-end logic. Users can choose any `From Date` and `To Date` and the visuals should show the relevant vacancy activity for that exact date range.

## Before You Start

Use these model objects:

- table `dim_date`
- table `dim_property_vic`
- table `fact_vacancy_interval_vic`
- table `fact_vacancy_day_vic`
- table `dim_active_vacancy_rule_parameters`
- table `audit_property_vic`
- table `audit_tenancy_vic`
- table `audit_void_vic`
- table `audit_keys_vic`
- table `audit_exceptions_vic`

Use these measures:

- `[Vacancy Count]`
- `[Vacancy Days]`
- `[Tenantable Days]`
- `[Untenantable Days]`
- `[Other Days]`
- `[Average Vacancy Days]`
- `[Avg Tenantable Days]`
- `[Avg Untenantable Days]`
- `[Avg Other Days]`
- `[Avg Tenantable Days When Present]`
- `[Avg Untenantable Days When Present]`
- `[Avg Other Days When Present]`
- `[Vacancies LE 21 Days]`
- `[Vacancies GT 21 Days]`
- `[Vacancies LE 48 Days]`
- `[Vacancies GT 48 Days]`
- `[Pct LE 21 Days]`
- `[Pct LE 48 Days]`
- `[Exception Count]`

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

Trace page note:

- do not sync the global date slicer to the `Property Trace` page unless you explicitly want raw source rows hidden by the selected reporting window,
- use a dedicated searchable property selector on the `Property Trace` page instead.
- do not sync the global date slicer to the `Exception Monitor` page either.

### Standard address filter

For pages that need to exclude non-standard address records, use a visual, page, or report-level filter:

- `dim_property_vic[is_standard_address]` = `True`

Do not use DAX text-search filters such as `SEARCH`, `FIND`, or `CONTAINSSTRING` against address fields at report runtime.

## Page 1: Summary

Purpose:

- show current performance quickly,
- support annual benchmark review,
- support ad hoc operational review.

### Visual 1: Summary KPI Card Container

Visual type:

- `Card (new)` (The New Card Visual)

Field well (Metrics to load):

- `Data` = `[Vacancy Count]`
- `Data` = `[Vacancy Days]`
- `Data` = `[Tenantable Days]`
- `Data` = `[Untenantable Days]`
- `Data` = `[Pct LE 21 Days]`
- `Data` = `[Pct LE 48 Days]`

Step-by-Step Visual Formatting:

#### 1. Visual Container (General $\rightarrow$ Effects $\rightarrow$ Background)
* **Background:** Toggle to **On**.
  * **Color:** Set to a soft slate/navy (e.g., `#1E293B` for dark mode or `#F8FAFC` for light mode).
  * **Transparency:** Set to **`70%–80%`** to create a translucent glassmorphic look over report page gradients.
* **Visual Border:** Toggle to **On**.
  * **Color:** Muted slate (e.g., `#334155`).
  * **Corners:** Round to **`12px`** or **`16px`** for a sleek, modern visual container.

#### 2. Individual Card backgrounds (Visual $\rightarrow$ Cards $\rightarrow$ Fill / Accent Bar)
By default, Power BI fills each card tile with a **solid white background**. To eliminate this white background and replicate the mockup design, you must choose **one** of these two styling options:

* **Option A: Pure Transparent Glassmorphism (Recommended - No individual tiles):**
  * **Visual $\rightarrow$ Cards $\rightarrow$ Fill:** Toggle this setting to **`OFF`** (or set **Transparency** to **`100%`**). This completely removes the white blocks, letting your outer glassmorphic container background show through beautifully.
  * **Visual $\rightarrow$ Cards $\rightarrow$ Border:** Toggle to **`OFF`**.
* **Option B: Layered Slate Tiles (For solid dark nested tiles):**
  * **Visual $\rightarrow$ Cards $\rightarrow$ Fill:** Toggle to **`ON`**.
    * **Color:** Set to a conformed dark slate color (e.g., Hex `#11161D` or `#0F1216` in dark mode; Hex `#F1F5F9` in light mode). **Do NOT leave it as default `#FFFFFF` white.**
    * **Transparency:** Set to **`0%`** (fully solid).
  * **Visual $\rightarrow$ Cards $\rightarrow$ Border:** Toggle to **`ON`**. Set Color to Hex `#222D37` and Width to `1 px`.
* **Shape settings (Visual $\rightarrow$ Shape):**
  * **Type:** Select **`Rounded Rectangle`**.
  * **Corner Radius:** Set to **`8px`** or **`10px`** to follow the rounded theme of the outer container.
* **Card Padding (Visual $\rightarrow$ Cards $\rightarrow$ Padding):**
  * **Type:** Select **`Custom`**.
  * **Value:** Set spacing to **`12px`** or **`16px`** to ensure the numbers and text have professional breathing room.

#### 3. Callout Value and Labels (Visual $\rightarrow$ Callout values)
* **Callout Values:**
  * **Font:** Set to **`Segoe UI Semibold`** or **`Inter`**.
  * **Color:** High-contrast white (`#FFFFFF`) or dark slate (`#0F172A`) depending on theme.
  * **Display Units:** Set to **`None`**.
  * **Format:** Set percentages (`Pct LE 21 Days`, `Pct LE 48 Days`) to format as percentages (`%`).
* **Card Labels (Label Text):**
  * **Color:** Muted slate grey (e.g., `#94A3B8`) to draw secondary attention.
  * **Position:** Set position to **`Below Value`** for clean vertical metric alignment.
* **Card Layout:**
  * **Orientation:** Set layout to **`Horizontal`**.
  * **Card Spacing:** Set card space to **`12px`** (horizontal gap between metric tiles).

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

- `Vacancy Days` include the vacancy start date itself.

## Page 2: Vacancy Detail

Purpose:

- provide exportable row-level detail,
- support operational follow-up,
- support regulator-ready extracts.

### Layout Hierarchy

The page is built with a high-density, professional vertical layout hierarchy:
1. **Top Row:** Synced Filters/Slicers (Entity, Ownership, CAH Program, Property Source, Date Slicer).
2. **Second Row:** 5 Glowing Glassmorphic KPI Cards with Reference Labels and modern outline icons.
3. **Third Row (Split Screen):**
   * **Left Side (40% width):** Clustered column chart showing **Vacancy Duration Distribution**.
   * **Right Side (60% width):** High-density conformed **Vacancy Detail Table** (reduced in column width, optimized for quick export).

---

### Step-by-Step Styling & Formatting Guide (To Replicate the Premium Mockup)

To achieve the premium, modern SaaS-like aesthetics displayed in the high-fidelity [vacancy_detail_mockup.png](file:///Users/abdulla/Documents/vacant_calc/docs/assets/vacancy_detail_mockup.png), configure your Power BI visual elements exactly as follows:

#### 1. Page Background & Wallpaper

To replicate the premium, modern SaaS-like aesthetics seen in advanced visual dashboards, you can choose between two main styling approaches:

* **Approach A: Unified Canvas Grid Background (Recommended - The YouTube Technique)**
  Instead of configuring backgrounds, borders, and shadows on every visual individually (which can render slowly and frequently drift out of alignment), you apply a single, high-fidelity widescreen grid background to the entire page canvas. 
  
  We have pre-designed and generated a premium conformed background asset for you at [dashboard_grid_bg.png](file:///Users/abdulla/Documents/vacant_calc/docs/assets/dashboard_grid_bg.png). It contains the title header space, 5 pre-aligned glassmorphic KPI card slots with glowing accent strokes, and lower layout plates for your chart and table.
  
  **How to apply Approach A in Power BI:**
  1. Open the **Format Page** pane (the paintbrush icon with no visuals selected).
  2. Expand **Canvas background**:
     * **Image:** Click **Browse** and select [dashboard_grid_bg.png](file:///Users/abdulla/Documents/vacant_calc/docs/assets/dashboard_grid_bg.png).
     * **Image Fit:** Change from *Normal* to **`Fit`** (this is critical to prevent cropping or tiling).
     * **Transparency:** Drag the slider from `100%` down to **`0%`** to make the grid visible.
  3. Expand **Wallpaper**:
     * **Color:** Set to Hex **`#0F1216`** (Deep slate gray) to match the outer padding.
  4. Expand **Canvas settings**:
     * **Type:** Select **`16:9`** Widescreen.
     * **Canvas Margins:** Set to **`16 px`** on all sides.
  5. **Visual Layer Overlays:**
     * Drag and place your metrics, column chart, and detail table over their designated pre-rendered slot containers.
     * Select each visual, navigate to **Format Visual $\rightarrow$ General $\rightarrow$ Effects**, and toggle **`Background = OFF`**, **`Visual Border = OFF`**, and **`Shadow = OFF`**. This lets the pre-rendered glowing glassmorphism of the background show through perfectly!

* **Approach B: Native Glassmorphism Containers (No External Assets)**
  Use this if you prefer using native Power BI shapes and formatting instead of static images.
  1. Set **Canvas Background** to Hex **`#0F1216`**, Transparency = `0%`.
  2. Apply the settings in the *Glassmorphic Card Containers* section below to each visual container individually.

* **Approach C: DIY PowerPoint Shape Backgrounds (The Custom YouTube Method)**
  If you want to design your own custom card shapes or layout grids using Microsoft PowerPoint:
  1. **Slide Setup:** Open PowerPoint $\rightarrow$ Go to **Design** tab $\rightarrow$ **Slide Size** $\rightarrow$ **Custom Slide Size**. Set it to a widescreen 16:9 format (`Width: 13.33 inches` or `33.867 cm`, `Height: 7.5 inches` or `19.05 cm`).
  2. **Slide Background:** Right-click the slide background $\rightarrow$ **Format Background** $\rightarrow$ **Solid Fill** $\rightarrow$ Color Hex **`#0F1216`**.
  3. **Draw Card Container:** Insert $\rightarrow$ Shapes $\rightarrow$ **Rounded Rectangle**. Draw a card shape on the slide.
  4. **Shape Formatting:**
     * **Shape Fill:** Select **Solid Fill** $\rightarrow$ Color Hex **`#171E26`** (Dark slate) with an optional `10%` transparency.
     * **Shape Outline/Border:** Select **Solid Line** $\rightarrow$ Color Hex **`#222D37`** (Subtle slate border) or a glowing accent color (Teal `#319795` or Green `#48BB78`), Width = **`1 pt`** or **`1.5 pt`**.
     * **Drop Shadow:** Go to **Shape Effects** $\rightarrow$ **Shadow** $\rightarrow$ **Shadow Options...**:
       * *Color:* Black (`#000000`)
       * *Transparency:* `75%`
       * *Size:* `102%`
       * *Blur:* `12 pt`
       * *Angle:* `90°`
       * *Distance:* `3 pt`
  5. **Exporting Assets:**
     * *To export the whole grid:* Go to **File $\rightarrow$ Save As $\rightarrow$ PNG**. Choose "Just This One".
     * *To export an individual card:* Right-click the shape you drew $\rightarrow$ **Save as Picture...** $\rightarrow$ Choose **PNG**.
  6. **Importing into Power BI:** Upload the individual card image as a fill for your cards (**Visual $\rightarrow$ Cards $\rightarrow$ Fill $\rightarrow$ Image**). Set Fit to **`Fit`** and Transparency to **`0%`**.

#### 2. Glassmorphic Card Containers (Applies to all visual backgrounds when not using Approach A)
For each KPI Card (the New Card visual container), the Column Chart, and the Table container, configure the **Visual Container Formatting** (located under the **`General`** tab $\rightarrow$ **`Effects`** section of the Format Pane):
* **Background (General $\rightarrow$ Effects $\rightarrow$ Background):** Toggle to **On**, Color = Hex `#171E26` (Dark slate gray), Transparency = `30%` (delivers the frosted glassmorphism effect).
* **Visual Border (General $\rightarrow$ Effects $\rightarrow$ Visual Border):** Toggle to **On**, Style = Solid, Width = `1 px`, Color = Hex `#222D37` (Subtle conformed edge stroke).
  * **Rounded Corners:** Toggle to **On**, Corner Radius = `8 px` (Sleek SaaS border radius).
* **Shadow (General $\rightarrow$ Effects $\rightarrow$ Shadow):** Toggle to **On**, Color = Hex `#000000`, Opacity = `80%`, Size = `10 px`, Angle = `90°`, Distance = `2 px`, Position = `Outer` (creates depth).

#### 3. Power BI "New Card" Visual - Callout Values & Reference Labels
Create a single conformed "New Card" visual containing all 5 metrics, or 5 individual card visuals aligned horizontally:

##### Callout Values (Primary Metrics)
* **Font Family:** `Outfit` or `Inter` (or clean sans-serif equivalent).
* **Font Size:** `45 pt`, Bold, Color = Hex `#FFFFFF` (Pure white).
* **Horizontal Alignment:** Left.
* **Display Units:** None.

##### Reference Labels (Secondary Context Metrics)
For each card series, navigate to **Format pane > Reference labels** and add/configure:
* **Font Family:** `Outfit` or `Inter`, Size = `10 pt`.
* **Label Colors:** Hex `#718096` (Slate gray).
* **Card 1 (Vacancy Count):**
  * *Open Vacancies* Value: Hex `#319795` (Teal).
  * *Closed Vacancies* Value: Hex `#718096` (Gray).
* **Card 2 (Vacancy Days):**
  * *Tenantable %* Value: Hex `#48BB78` (Green).
  * *Untenantable %* Value: Hex `#ED8936` (Orange).
  * *Other %* Value: Hex `#718096` (Gray).
* **Card 3 (Average Duration):**
  * *Tenantable / All* Value: Hex `#319795` (Teal).
  * *Tenantable / >0 Only* Value: Hex `#319795` (Teal).
  * *Untenantable / All* Value: Hex `#ED8936` (Orange).
  * *Untenantable / >0 Only* Value: Hex `#ED8936` (Orange).
  * *Other / All* Value: Hex `#718096` (Gray).
  * *Other / >0 Only* Value: Hex `#718096` (Gray).
  * *VS. Target (21d)* Value: Apply **Conditional Formatting** based on `[Avg Vacancy Variance to 21d]`. Rule: If value > 0, Hex `#F56565` (Red - over target); if value <= 0, Hex `#48BB78` (Green - under target).
* **Card 4 (21-Day Benchmark):**
  * *Volume* Value: Hex `#718096` (Gray).
  * *VS. Target (80%)* Value: Apply **Conditional Formatting** based on `[Benchmark 21d Variance]`. Rule: If value >= 0, Hex `#48BB78` (Green); if value < 0, Hex `#F56565` (Red).
* **Card 5 (48-Day Benchmark):**
  * *Volume* Value: Hex `#718096` (Gray).
  * *VS. Target (95%)* Value: Apply **Conditional Formatting** based on `[Benchmark 48d Variance]`. Rule: If value >= 0, Hex `#48BB78` (Green); if value < 0, Hex `#F56565` (Red).

##### Light Theme KPI Card Styling
Use this styling when the Vacancy Detail page uses the clean white-card layout instead of the dark glassmorphic background.

Card container:

- Background = `#FFFFFF`
- Border = `#E5E7EB`, `1 px`
- Corner radius = `10 px` to `12 px`
- Shadow = On, color `#000000`, transparency `75%` to `85%`, blur `10 px` to `14 px`, distance `3 px`
- Inner padding = `18 px` to `22 px`
- Keep all five KPI cards the same width and height.

Typography:

- Primary value font = `Segoe UI Semibold`, `Inter SemiBold`, or `Aptos Display`, `24 pt` to `30 pt`
- Primary label font = `Segoe UI`, `Inter`, or `Aptos`, `12 pt` to `14 pt`
- Reference label font = same family, `8.5 pt` to `9.5 pt`
- Primary value color = `#111827`
- Primary label color = `#6B7280`
- Divider line color = `#E5E7EB`
- Reference label text color = `#8A8F98`
- Reference value color should use the KPI accent color below.

Recommended KPI accent colors:

- Vacancy Count = `#0F766E` (teal)
- Vacancy Days = `#2563EB` (blue)
- Tenantable Days = `#15803D` (green)
- Untenantable Days = `#C2410C` (orange)
- Other Days = `#6B7280` (neutral gray)

Reference label wording for the current card layout:

- Vacancy Count card:
  * `Has Tenantable`
  * `Has Untenantable`
  * `Has Other`
- Vacancy Days card:
  * `Avg (All)`
- Tenantable, Untenantable, and Other cards:
  * `Avg (All)`
  * `Avg (>0 Only)`

Color the reference values, not the full label text. This keeps the cards readable while still giving each KPI a clear semantic cue.

##### Custom Outline Icon Integration
For each card, navigate to **Format pane > Cards > Image** and upload the conformed separated PNG icons:
1. **Vacancy Count Card:** Browse and select [vacancy_count_icon.png](file:///Users/abdulla/Documents/vacant_calc/docs/assets/vacancy_count_icon.png)
2. **Vacancy Days Card:** Browse and select [vacancy_days_icon.png](file:///Users/abdulla/Documents/vacant_calc/docs/assets/vacancy_days_icon.png)
3. **Average Duration Card:** Browse and select [tenantable_days_icon.png](file:///Users/abdulla/Documents/vacant_calc/docs/assets/tenantable_days_icon.png)
4. **21-Day Card:** Browse and select [untenantable_days_icon.png](file:///Users/abdulla/Documents/vacant_calc/docs/assets/untenantable_days_icon.png)
5. **48-Day Card:** Browse and select [benchmark_achievement_icon.png](file:///Users/abdulla/Documents/vacant_calc/docs/assets/benchmark_achievement_icon.png)
* **Image settings for all cards:**
  * **Position:** Right.
  * **Fit:** Fit.
  * **Size:** `40 px`.
  * **Padding:** `10 px`.
  * **Transparency:** `0%`.

#### 4. Clustered Column Chart (Vacancy Duration Distribution)
* **X-axis & Y-axis Labels:** Font = `Outfit`/`Inter`, Size = `9 pt`, Color = Hex `#A0AEC0` (Conformed gray).
* **Gridlines:** Turn both Horizontal and Vertical Gridlines **Off** to preserve the premium slate background.
* **Column Colors:** Turn **Show All** to **On** under **Format > Columns > Colors** and color-code each category exactly to represent the visual gradient:
  * `0-7 Days`: Hex `#1E3A8A` (Deep navy blue)
  * `8-14 Days`: Hex `#0D9488` (Teal)
  * `15-21 Days (Target 21)`: Hex `#16A34A` (Light green)
  * `22-35 Days`: Hex `#D97706` (Amber/Yellow)
  * `36-48 Days (Target 48)`: Hex `#EA580C` (Warm coral orange)
  * `49+ Days`: Hex `#DC2626` (Vibrant red)
* **Data Labels:** Turn **On**, Color = Hex `#FFFFFF`, Size = `8 pt`, Position = `Auto`.
* **Chart Title:** Font = `Outfit`/`Inter`, Bold, Size = `12 pt`, Color = Hex `#FFFFFF`.

#### 5. High-Density Conformed Detail Table
* **Style Preset:** Set to `None` or `Minimal` to allow total conformed overrides.
* **Values Formatting:** Font = `Outfit`/`Inter`, Size = `9 pt`, Text Color = Hex `#E2E8F0` (Off-white), Alternating row style = Off.
* **Column Headers:** Font = `Outfit`/`Inter`, Bold, Size = `10 pt`, Font Color = Hex `#FFFFFF` (Pure white), Background Color = Hex `#171E26` (frosted container color).
* **Grid Formatting:**
  * **Row Borders:** On, Color = Hex `#222D37` (Edge gray stroke), Thickness = `1 px`.
  * **Column Borders:** Off (maintains high readability).
* **Conditional Formatting (Has Exception):**
  * Navigate to **Conditional formatting > Icons** for `Has Exception`.
  * Set rules: If value is `1` (positive exception flag), show the **Red Warning Icon**. If value is `0`, show **No Icon** (completely hidden). Use icon-only layout for this column.

---

### KPI Card 1: Vacancy Count

Visual type:

- `Card (New)`

Field well:

- `Primary Value` = `[Vacancy Count]`

Reference Labels (Secondary Metrics):

- `Label 1` = `Open Vacancies`
  * Value = `[Open Vacancy Count]`
  * Color = HSL Teal / Green accent
- `Label 2` = `Closed Vacancies`
  * Value = `[Closed Vacancy Count]`
  * Color = Gray

Accent / Icon:
- Glowing outline checkmark and house icon in the upper right.

---

### KPI Card 2: Vacancy Days

Visual type:

- `Card (New)`

Field well:

- `Primary Value` = `[Vacancy Days]`

Reference Labels (Secondary Metrics):

- `Label 1` = `Tenantable %`
  * Value = `[Tenantable Days Pct]` (formatted as %)
  * Color = HSL Green accent
- `Label 2` = `Untenantable %`
  * Value = `[Untenantable Days Pct]` (formatted as %)
  * Color = HSL Orange accent
- `Label 3` = `Other %`
  * Value = `[Other Days Pct]` (formatted as %)
  * Color = Gray

Accent / Icon:
- Glowing calendar outline and clock icon in the upper right.

---

### KPI Card 3: Average Duration

Visual type:

- `Card (New)`

Field well:

- `Primary Value` = `[Average Vacancy Days]`

Reference Labels (Secondary Metrics):

- `Label 1` = `Tenantable / All`
  * Value = `[Avg Tenantable Days]`
  * Color = HSL Teal accent
- `Label 2` = `Tenantable / >0 Only`
  * Value = `[Avg Tenantable Days When Present]`
  * Color = HSL Teal accent
- `Label 3` = `Untenantable / All`
  * Value = `[Avg Untenantable Days]`
  * Color = HSL Orange accent
- `Label 4` = `Untenantable / >0 Only`
  * Value = `[Avg Untenantable Days When Present]`
  * Color = HSL Orange accent
- `Label 5` = `Other / All`
  * Value = `[Avg Other Days]`
  * Color = Gray
- `Label 6` = `Other / >0 Only`
  * Value = `[Avg Other Days When Present]`
  * Color = Gray
- `Label 7` = `VS. Target (21d)`
  * Value = `[Avg Vacancy Variance to 21d]` (formatted as `+0.0;-0.0`)
  * Color = Red if positive (above benchmark), Green if negative (below benchmark)

Accent / Icon:
- Glowing key and shield icon in the upper right.

Tooltip / explanation:

- Add a report tooltip for this card with two short rows:
  * `All` = divides by every visible vacancy.
  * `>0 Only` = divides only by vacancies where that day type is greater than zero.
- Keep this explanation in the tooltip or visual subtitle rather than adding a large text box to the page.

---

### KPI Card 4: 21-Day Benchmark Achievement

Visual type:

- `Card (New)`

Field well:

- `Primary Value` = `[Pct LE 21 Days]` (formatted as %)

Reference Labels (Secondary Metrics):

- `Label 1` = `Volume`
  * Value = `[Vacancies LE 21 Days]`
  * Color = Gray
- `Label 2` = `VS. Target (80%)`
  * Value = `[Benchmark 21d Variance]` (formatted as `%`)
  * Color = Green if positive, Red if negative

Accent / Icon:
- Glowing gear and maintenance outline icon in the upper right.

---

### KPI Card 5: 48-Day Benchmark Achievement

Visual type:

- `Card (New)`

Field well:

- `Primary Value` = `[Pct LE 48 Days]` (formatted as %)

Reference Labels (Secondary Metrics):

- `Label 1` = `Volume`
  * Value = `[Vacancies LE 48 Days]`
  * Color = Gray
- `Label 2` = `VS. Target (95%)`
  * Value = `[Benchmark 48d Variance]` (formatted as `%`)
  * Color = Green if positive, Red if negative

Accent / Icon:
- Glowing target circle outline icon in the upper right.

---

### Visual 1: Vacancy Duration Distribution Chart

Visual type:

- `Clustered column chart`

Field well:

- `X-axis` = `fact_vacancy_interval_vic[Vacancy Duration Bracket]`
- `Y-axis` = `[Vacancy Count]`
- `Tooltips` = `[Vacancy Days]`, `[Average Vacancy Days]`

Sorting and Colors:

- Sort by `fact_vacancy_interval_vic[Vacancy Duration Bracket Sort]` ascending.
- Column colors: Gradient sequence representing operational severity (0-7 Days: deep blue, 8-14 Days: teal, 15-21 Days: light green, 22-35 Days: yellow/orange, 36-48 Days: coral, 49+ Days: vibrant red).

---

### Visual 2: Vacancy detail table

Visual type:

- `Table`

Field well:

- `Columns` = `fact_vacancy_interval_vic[vacancy_id]`
- `Columns` = `fact_vacancy_interval_vic[property_id]`
- `Columns` = `dim_property_vic[property_number]`
- `Columns` = `dim_property_vic[property_short_address]`
- `Columns` = `dim_property_vic[is_standard_address]`
- `Columns` = `dim_property_vic[entity]`
- `Columns` = `dim_property_vic[ownership]`
- `Columns` = `dim_property_vic[housing_program]`
- `Columns` = `dim_property_vic[property_type]`
- `Columns` = `dim_property_vic[property_program]`
- `Columns` = `dim_property_vic[current_stage]`
- `Columns` = `dim_property_vic[property_source]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_origin]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_reason]`
- `Columns` = `fact_vacancy_interval_vic[property_has_exception_flag]`
- `Columns` = `fact_vacancy_interval_vic[has_exception_flag]`
- `Columns` = `dim_property_vic[property_start_date]`
- `Columns` = `dim_property_vic[property_end_date]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_start_tenancy_id]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_start_tenancy_current_stage]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_start_tenancy_end_date]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_start_date]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_end_date_display]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_end_tenancy_id]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_end_tenancy_current_stage]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_end_tenancy_start_date]`
- `Columns` = `fact_vacancy_interval_vic[void_id]`
- `Columns` = `fact_vacancy_interval_vic[void_reference]`
- `Columns` = `fact_vacancy_interval_vic[void_start_date]`
- `Columns` = `fact_vacancy_interval_vic[void_end_date]`
- `Columns` = `fact_vacancy_interval_vic[void_reason]`
- `Columns` = `fact_vacancy_interval_vic[overlap_void_start_date]`
- `Columns` = `fact_vacancy_interval_vic[overlap_void_end_date]`
- `Columns` = `fact_vacancy_interval_vic[exception_count]`
- `Columns` = `fact_vacancy_interval_vic[exception_types]`
- `Columns` = `[Vacancy Days]`
- `Columns` = `[Tenantable Days]`
- `Columns` = `[Untenantable Days]`
- `Columns` = `[Other Days]`
- `Columns` = `fact_vacancy_interval_vic[other_start_date]`
- `Columns` = `fact_vacancy_interval_vic[other_end_date]`
- `Columns` = `fact_vacancy_interval_vic[other_vacancy_type_reasons]`
- `Columns` = `fact_vacancy_interval_vic[other_void_types]`
- `Columns` = `fact_vacancy_interval_vic[other_vacancy_record_count]`
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
- rename `dim_property_vic[is_standard_address]` display label to `Standard Address`
- rename `dim_property_vic[entity]` display label to `Entity`
- rename `dim_property_vic[ownership]` display label to `Ownership`
- rename `dim_property_vic[housing_program]` display label to `Housing Program`
- rename `dim_property_vic[property_type]` display label to `Property Type`
- rename `dim_property_vic[property_program]` display label to `Property Program`
- rename `dim_property_vic[current_stage]` display label to `Property Current Stage`
- rename `dim_property_vic[property_source]` display label to `Property Source`
- rename `fact_vacancy_interval_vic[vacancy_origin]` display label to `Vacancy Origin`
- rename `fact_vacancy_interval_vic[vacancy_reason]` display label to `Vacancy Reason`
- rename `fact_vacancy_interval_vic[property_has_exception_flag]` display label to `Property Has Exception`
- rename `fact_vacancy_interval_vic[has_exception_flag]` display label to `Has Exception`
- rename `fact_vacancy_interval_vic[vacancy_start_tenancy_id]` display label to `Previous Tenancy ID`
- rename `fact_vacancy_interval_vic[vacancy_start_tenancy_current_stage]` display label to `Previous Tenancy Current Stage`
- rename `fact_vacancy_interval_vic[vacancy_start_tenancy_end_date]` display label to `Previous Tenancy End Date`
- rename `fact_vacancy_interval_vic[vacancy_start_date]` display label to `Vacancy Start Date`
- rename `fact_vacancy_interval_vic[vacancy_end_date_display]` display label to `Vacancy End Date`
- rename `fact_vacancy_interval_vic[vacancy_end_tenancy_id]` display label to `Next Tenancy ID`
- rename `fact_vacancy_interval_vic[vacancy_end_tenancy_current_stage]` display label to `Next Tenancy Current Stage`
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
- rename `fact_vacancy_interval_vic[exception_count]` display label to `Exception Count`
- rename `fact_vacancy_interval_vic[exception_types]` display label to `Exception Types`
- rename `[Vacancy Days]` display label to `Vacancy Days`
- rename `[Tenantable Days]` display label to `Tenantable Days`
- rename `[Untenantable Days]` display label to `Untenantable Days`
- rename `[Other Days]` display label to `Other Days`
- rename `fact_vacancy_interval_vic[other_start_date]` display label to `Other Start Date`
- rename `fact_vacancy_interval_vic[other_end_date]` display label to `Other End Date`
- rename `fact_vacancy_interval_vic[other_vacancy_type_reasons]` display label to `Other Vacancy Reason`
- rename `fact_vacancy_interval_vic[other_void_types]` display label to `Other Void Type`
- rename `fact_vacancy_interval_vic[other_vacancy_record_count]` display label to `Other Vacancy Record Count`
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
- apply conditional formatting icons to `Has Exception`
- apply conditional formatting icons to `Property Has Exception`
- icon rules:
- if value is `1`, show red warning icon
- if value is `0`, show no icon or green check based on team preference
- if you do not want to show `0` and `1`, use icon-only formatting for this column

Recommended final column order for management:

- `Vacancy ID`
- `Property Number`
- `Property Address`
- `Standard Address`
- `Entity`
- `Ownership`
- `Housing Program`
- `Property Type`
- `Property Program`
- `Property Current Stage`
- `Property Source`
- `Vacancy Origin`
- `Vacancy Reason`
- `Property Has Exception`
- `Has Exception`
- `Property Start Date`
- `Property End Date`
- `Previous Tenancy ID`
- `Previous Tenancy Current Stage`
- `Previous Tenancy End Date`
- `Vacancy Start Date`
- `Vacancy End Date`
- `Next Tenancy ID`
- `Next Tenancy Current Stage`
- `Next Tenancy Start Date`
- `Vacancy Days`
- `Tenantable Days`
- `Untenantable Days`
- `Other Days`
- `Other Start Date`
- `Other End Date`
- `Other Vacancy Reason`
- `Other Void Type`
- `Void ID`
- `Void Reference`
- `Selected Void Start Date`
- `Selected Void End Date`
- `Void Reason`
- `Overall Void Start Date`
- `Overall Void End Date`
- `Exception Count`
- `Exception Types`
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
- `Other Days` must use the `[Other Days]` measure from `fact_vacancy_day_vic`, so it respects the selected date window.
- `other_start_date` and `other_end_date` are descriptive interval fields and may sit outside the selected date window.

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
- `Columns` = `fact_vacancy_day_vic[other_void_id]`
- `Columns` = `fact_vacancy_day_vic[other_vacancy_type_reason]`
- `Columns` = `fact_vacancy_day_vic[other_void_type]`

Formatting:

- sort by `fact_vacancy_day_vic[vacancy_date]` ascending

### Visual 2: Void audit table

Visual type:

- `Table`

Field well:

- `Columns` = `audit_void_vic[void_id]`
- `Columns` = `audit_void_vic[property_id]`
- `Columns` = `audit_void_vic[void_reference]`
- `Columns` = `audit_void_vic[void_start_date]`
- `Columns` = `audit_void_vic[void_end_date]`
- `Columns` = `audit_void_vic[void_end_exclusive]`
- `Columns` = `audit_void_vic[other_start_date]`
- `Columns` = `audit_void_vic[other_end_date]`
- `Columns` = `audit_void_vic[other_effective_start_date]`
- `Columns` = `audit_void_vic[other_effective_end_date]`
- `Columns` = `audit_void_vic[other_vacancy_outside_void_flag]`
- `Columns` = `audit_void_vic[other_vacancy_type_reason]`
- `Columns` = `audit_void_vic[void_type]`
- `Columns` = `audit_void_vic[void_reason]`
- `Columns` = `audit_void_vic[property_condition]`

Formatting:

- rename `void_end_exclusive` display label to `Void End Exclusive Boundary`
- rename `other_start_date` display label to `Other Start Date`
- rename `other_end_date` display label to `Other End Date`
- rename `other_effective_start_date` display label to `Counted Other Start Date`
- rename `other_effective_end_date` display label to `Counted Other End Date`
- rename `other_vacancy_outside_void_flag` display label to `Other Outside Void`
- rename `other_vacancy_type_reason` display label to `Other Vacancy Reason`
- rename `void_type` display label to `Void Type`

Note:

- `void_end_date` is the inclusive business date. `void_end_exclusive` is the technical boundary used for day counting.

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

## Page 5: Property Trace

Purpose:

- validate derived vacancy rows against source-aligned tables for one property,
- support testing of date offsets and vacancy boundaries,
- give future developers a clean trace page without changing the management pages.

Page behavior:

- do not sync the global `dim_date[date]` slicer to this page,
- keep this page focused on one selected property at a time,
- use a searchable property selector instead of a date selector as the primary filter.

### Visual 1: Property selector

Visual type:

- `Slicer`

Field well:

- `Field` = `dim_property_vic[property_id]`

Settings:

- style = `Dropdown`
- search = `On`
- single select = `On`

### Visual 2: Property snapshot table

Visual type:

- `Table`

Field well:

- `Columns` = `audit_property_vic[property_id]`
- `Columns` = `audit_property_vic[property_number]`
- `Columns` = `audit_property_vic[property_short_address]`
- `Columns` = `audit_property_vic[is_standard_address]`
- `Columns` = `audit_property_vic[entity]`
- `Columns` = `audit_property_vic[ownership]`
- `Columns` = `audit_property_vic[housing_program]`
- `Columns` = `audit_property_vic[property_type]`
- `Columns` = `audit_property_vic[property_program]`
- `Columns` = `audit_property_vic[raw_effective_property_start_date]`
- `Columns` = `audit_property_vic[property_start_date]`
- `Columns` = `audit_property_vic[raw_property_end_date]`
- `Columns` = `audit_property_vic[property_end_date]`
- `Columns` = `audit_property_vic[current_stage]`
- `Columns` = `audit_property_vic[active_code]`
- `Columns` = `audit_property_vic[source_date_offset_days]`

Formatting:

- rename `audit_property_vic[property_id]` display label to `Property ID`
- rename `audit_property_vic[property_number]` display label to `Property Number`
- rename `audit_property_vic[property_short_address]` display label to `Property Address`
- rename `audit_property_vic[is_standard_address]` display label to `Standard Address`
- rename `audit_property_vic[entity]` display label to `Entity`
- rename `audit_property_vic[ownership]` display label to `Ownership`
- rename `audit_property_vic[housing_program]` display label to `Housing Program`
- rename `audit_property_vic[property_type]` display label to `Property Type`
- rename `audit_property_vic[property_program]` display label to `Property Program`
- rename `audit_property_vic[raw_effective_property_start_date]` display label to `Raw Property Start Date`
- rename `audit_property_vic[property_start_date]` display label to `Adjusted Property Start Date`
- rename `audit_property_vic[raw_property_end_date]` display label to `Raw Property End Date`
- rename `audit_property_vic[property_end_date]` display label to `Adjusted Property End Date`
- rename `audit_property_vic[current_stage]` display label to `Property Current Stage`
- rename `audit_property_vic[active_code]` display label to `Property Active Code`
- rename `audit_property_vic[source_date_offset_days]` display label to `Property Source Offset Days`

### Visual 3: Tenancy trace table

Visual type:

- `Table`

Field well:

- `Columns` = `audit_tenancy_vic[property_id]`
- `Columns` = `audit_tenancy_vic[tenancy_id]`
- `Columns` = `audit_tenancy_vic[tenancy_reference]`
- `Columns` = `audit_tenancy_vic[property_type]`
- `Columns` = `audit_tenancy_vic[property_program]`
- `Columns` = `audit_tenancy_vic[property_current_stage]`
- `Columns` = `audit_tenancy_vic[raw_tenancy_start_date]`
- `Columns` = `audit_tenancy_vic[tenancy_start_date]`
- `Columns` = `audit_tenancy_vic[raw_tenancy_end_date]`
- `Columns` = `audit_tenancy_vic[tenancy_end_date]`
- `Columns` = `audit_tenancy_vic[tenancy_end_reason]`
- `Columns` = `audit_tenancy_vic[current_stage]`
- `Columns` = `audit_tenancy_vic[active_code]`
- `Columns` = `audit_tenancy_vic[is_excluded_from_vacancy_logic]`
- `Columns` = `audit_tenancy_vic[source_date_offset_days]`

Formatting:

- sort by `audit_tenancy_vic[tenancy_start_date]` ascending
- rename `audit_tenancy_vic[property_id]` display label to `Property ID`
- rename `audit_tenancy_vic[tenancy_id]` display label to `Tenancy ID`
- rename `audit_tenancy_vic[tenancy_reference]` display label to `Tenancy Reference`
- rename `audit_tenancy_vic[property_type]` display label to `Property Type`
- rename `audit_tenancy_vic[property_program]` display label to `Property Program`
- rename `audit_tenancy_vic[property_current_stage]` display label to `Property Current Stage`
- rename `audit_tenancy_vic[raw_tenancy_start_date]` display label to `Raw Tenancy Start Date`
- rename `audit_tenancy_vic[tenancy_start_date]` display label to `Adjusted Tenancy Start Date`
- rename `audit_tenancy_vic[raw_tenancy_end_date]` display label to `Raw Tenancy End Date`
- rename `audit_tenancy_vic[tenancy_end_date]` display label to `Adjusted Tenancy End Date`
- rename `audit_tenancy_vic[tenancy_end_reason]` display label to `End Of Tenancy Reason`
- rename `audit_tenancy_vic[current_stage]` display label to `Tenancy Stage`
- rename `audit_tenancy_vic[active_code]` display label to `Tenancy Active Code`
- rename `audit_tenancy_vic[is_excluded_from_vacancy_logic]` display label to `Excluded From Vacancy Logic`
- rename `audit_tenancy_vic[source_date_offset_days]` display label to `Tenancy Source Offset Days`

Note:

- `Allocation Cancelled` tenancy rows stay visible in this audit table, but they are excluded from vacancy construction and exception generation.

### Visual 4: Void trace table

Visual type:

- `Table`

Field well:

- `Columns` = `audit_void_vic[property_id]`
- `Columns` = `audit_void_vic[void_id]`
- `Columns` = `audit_void_vic[void_reference]`
- `Columns` = `audit_void_vic[property_type]`
- `Columns` = `audit_void_vic[property_program]`
- `Columns` = `audit_void_vic[property_current_stage]`
- `Columns` = `audit_void_vic[raw_void_start_date]`
- `Columns` = `audit_void_vic[void_start_date]`
- `Columns` = `audit_void_vic[raw_void_end_date]`
- `Columns` = `audit_void_vic[void_end_date]`
- `Columns` = `audit_void_vic[void_end_exclusive]`
- `Columns` = `audit_void_vic[other_vacancy_type_reason]`
- `Columns` = `audit_void_vic[raw_other_start_date]`
- `Columns` = `audit_void_vic[other_start_date]`
- `Columns` = `audit_void_vic[raw_other_end_date]`
- `Columns` = `audit_void_vic[other_end_date]`
- `Columns` = `audit_void_vic[other_end_exclusive]`
- `Columns` = `audit_void_vic[other_start_date_source]`
- `Columns` = `audit_void_vic[other_end_date_source]`
- `Columns` = `audit_void_vic[other_effective_start_date]`
- `Columns` = `audit_void_vic[other_effective_end_date]`
- `Columns` = `audit_void_vic[other_vacancy_outside_void_flag]`
- `Columns` = `audit_void_vic[other_start_date_text]`
- `Columns` = `audit_void_vic[other_end_date_text]`
- `Columns` = `audit_void_vic[void_type]`
- `Columns` = `audit_void_vic[void_reason]`
- `Columns` = `audit_void_vic[property_condition]`
- `Columns` = `audit_void_vic[source_date_offset_days]`

Formatting:

- sort by `audit_void_vic[void_start_date]` ascending
- rename `audit_void_vic[property_id]` display label to `Property ID`
- rename `audit_void_vic[void_id]` display label to `Void ID`
- rename `audit_void_vic[void_reference]` display label to `Void Reference`
- rename `audit_void_vic[property_type]` display label to `Property Type`
- rename `audit_void_vic[property_program]` display label to `Property Program`
- rename `audit_void_vic[property_current_stage]` display label to `Property Current Stage`
- rename `audit_void_vic[raw_void_start_date]` display label to `Raw Void Start Date`
- rename `audit_void_vic[void_start_date]` display label to `Adjusted Void Start Date`
- rename `audit_void_vic[raw_void_end_date]` display label to `Raw Void End Date`
- rename `audit_void_vic[void_end_date]` display label to `Adjusted Void End Date`
- rename `audit_void_vic[void_end_exclusive]` display label to `Void End Exclusive Boundary`
- rename `audit_void_vic[other_vacancy_type_reason]` display label to `Other Vacancy Reason`
- rename `audit_void_vic[raw_other_start_date]` display label to `Raw Other Start Date`
- rename `audit_void_vic[other_start_date]` display label to `Adjusted Other Start Date`
- rename `audit_void_vic[raw_other_end_date]` display label to `Raw Other End Date`
- rename `audit_void_vic[other_end_date]` display label to `Adjusted Other End Date`
- rename `audit_void_vic[other_end_exclusive]` display label to `Other End Exclusive Boundary`
- rename `audit_void_vic[other_start_date_source]` display label to `Other Start Date Source`
- rename `audit_void_vic[other_end_date_source]` display label to `Other End Date Source`
- rename `audit_void_vic[other_effective_start_date]` display label to `Counted Other Start Date`
- rename `audit_void_vic[other_effective_end_date]` display label to `Counted Other End Date`
- rename `audit_void_vic[other_vacancy_outside_void_flag]` display label to `Other Outside Void`
- rename `audit_void_vic[other_start_date_text]` display label to `Other Start Date Text`
- rename `audit_void_vic[other_end_date_text]` display label to `Other End Date Text`
- rename `audit_void_vic[void_type]` display label to `Void Type`
- rename `audit_void_vic[void_reason]` display label to `Void Reason`
- rename `audit_void_vic[property_condition]` display label to `Void Property Condition`
- rename `audit_void_vic[source_date_offset_days]` display label to `Void Source Offset Days`

### Visual 5: Keys trace table

Visual type:

- `Table`

Field well:

- `Columns` = `audit_keys_vic[property_id]`
- `Columns` = `audit_keys_vic[key_id]`
- `Columns` = `audit_keys_vic[key_reference]`
- `Columns` = `audit_keys_vic[property_type]`
- `Columns` = `audit_keys_vic[property_program]`
- `Columns` = `audit_keys_vic[property_current_stage]`
- `Columns` = `audit_keys_vic[raw_date_received_from_tenant]`
- `Columns` = `audit_keys_vic[date_received_from_tenant]`
- `Columns` = `audit_keys_vic[raw_outgoing_inspection_date]`
- `Columns` = `audit_keys_vic[outgoing_inspection_date]`
- `Columns` = `audit_keys_vic[raw_contractor_notified_date]`
- `Columns` = `audit_keys_vic[contractor_notified_date]`
- `Columns` = `audit_keys_vic[raw_contractor_collect_key_date]`
- `Columns` = `audit_keys_vic[contractor_collect_key_date]`
- `Columns` = `audit_keys_vic[raw_contractor_return_key_date]`
- `Columns` = `audit_keys_vic[contractor_return_key_date]`
- `Columns` = `audit_keys_vic[vacancy_exemptions_desc]`
- `Columns` = `audit_keys_vic[property_condition]`
- `Columns` = `audit_keys_vic[source_date_offset_days]`

Formatting:

- sort by `audit_keys_vic[key_anchor_date]` descending
- rename `audit_keys_vic[property_id]` display label to `Property ID`
- rename `audit_keys_vic[key_id]` display label to `Keys Record ID`
- rename `audit_keys_vic[key_reference]` display label to `Keys Reference`
- rename `audit_keys_vic[property_type]` display label to `Property Type`
- rename `audit_keys_vic[property_program]` display label to `Property Program`
- rename `audit_keys_vic[property_current_stage]` display label to `Property Current Stage`
- rename `audit_keys_vic[raw_date_received_from_tenant]` display label to `Raw Date Received From Tenant`
- rename `audit_keys_vic[date_received_from_tenant]` display label to `Adjusted Date Received From Tenant`
- rename `audit_keys_vic[raw_outgoing_inspection_date]` display label to `Raw Outgoing Inspection Date`
- rename `audit_keys_vic[outgoing_inspection_date]` display label to `Adjusted Outgoing Inspection Date`
- rename `audit_keys_vic[raw_contractor_notified_date]` display label to `Raw Contractor Notified Date`
- rename `audit_keys_vic[contractor_notified_date]` display label to `Adjusted Contractor Notified Date`
- rename `audit_keys_vic[raw_contractor_collect_key_date]` display label to `Raw Contractor Collected Key Date`
- rename `audit_keys_vic[contractor_collect_key_date]` display label to `Adjusted Contractor Collected Key Date`
- rename `audit_keys_vic[raw_contractor_return_key_date]` display label to `Raw Contractor Returned Key Date`
- rename `audit_keys_vic[contractor_return_key_date]` display label to `Adjusted Contractor Returned Key Date`
- rename `audit_keys_vic[vacancy_exemptions_desc]` display label to `Vacancy Exemption`
- rename `audit_keys_vic[property_condition]` display label to `Property Condition`
- rename `audit_keys_vic[source_date_offset_days]` display label to `Keys Source Offset Days`

### Visual 6: Derived vacancy trace table

Visual type:

- `Table`

Field well:

- `Columns` = `fact_vacancy_interval_vic[vacancy_id]`
- `Columns` = `fact_vacancy_interval_vic[property_id]`
- `Columns` = `fact_vacancy_interval_vic[property_type]`
- `Columns` = `fact_vacancy_interval_vic[property_program]`
- `Columns` = `fact_vacancy_interval_vic[current_stage]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_origin]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_reason]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_start_tenancy_id]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_start_tenancy_current_stage]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_start_tenancy_end_date]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_start_date]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_end_tenancy_id]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_end_tenancy_current_stage]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_end_tenancy_start_date]`
- `Columns` = `fact_vacancy_interval_vic[vacancy_end_date_display]`
- `Columns` = `fact_vacancy_interval_vic[void_id]`
- `Columns` = `fact_vacancy_interval_vic[void_start_date]`
- `Columns` = `fact_vacancy_interval_vic[void_end_date]`
- `Columns` = `fact_vacancy_interval_vic[key_id]`
- `Columns` = `[Vacancy Days]`
- `Columns` = `[Tenantable Days]`
- `Columns` = `[Untenantable Days]`

Formatting:

- sort by `fact_vacancy_interval_vic[vacancy_start_date]` ascending
- rename `fact_vacancy_interval_vic[vacancy_id]` display label to `Vacancy ID`
- rename `fact_vacancy_interval_vic[property_id]` display label to `Property ID`
- rename `fact_vacancy_interval_vic[property_type]` display label to `Property Type`
- rename `fact_vacancy_interval_vic[property_program]` display label to `Property Program`
- rename `fact_vacancy_interval_vic[current_stage]` display label to `Property Current Stage`
- rename `fact_vacancy_interval_vic[vacancy_origin]` display label to `Vacancy Origin`
- rename `fact_vacancy_interval_vic[vacancy_reason]` display label to `Vacancy Reason`
- rename `fact_vacancy_interval_vic[vacancy_start_tenancy_id]` display label to `Previous Tenancy ID`
- rename `fact_vacancy_interval_vic[vacancy_start_tenancy_current_stage]` display label to `Previous Tenancy Current Stage`
- rename `fact_vacancy_interval_vic[vacancy_start_tenancy_end_date]` display label to `Previous Tenancy End Date`
- rename `fact_vacancy_interval_vic[vacancy_start_date]` display label to `Vacancy Start Date`
- rename `fact_vacancy_interval_vic[vacancy_end_tenancy_id]` display label to `Next Tenancy ID`
- rename `fact_vacancy_interval_vic[vacancy_end_tenancy_current_stage]` display label to `Next Tenancy Current Stage`
- rename `fact_vacancy_interval_vic[vacancy_end_tenancy_start_date]` display label to `Next Tenancy Start Date`
- rename `fact_vacancy_interval_vic[vacancy_end_date_display]` display label to `Vacancy End Date`
- rename `fact_vacancy_interval_vic[void_id]` display label to `Selected Void ID`
- rename `fact_vacancy_interval_vic[void_start_date]` display label to `Selected Void Start Date`
- rename `fact_vacancy_interval_vic[void_end_date]` display label to `Selected Void End Date`
- rename `fact_vacancy_interval_vic[key_id]` display label to `Selected Keys Record ID`

### Visual 7: Vacancy day trace table

Visual type:

- `Table`

Field well:

- `Columns` = `fact_vacancy_day_vic[vacancy_id]`
- `Columns` = `fact_vacancy_day_vic[vacancy_date]`
- `Columns` = `fact_vacancy_day_vic[day_type]`
- `Columns` = `fact_vacancy_day_vic[void_id]`
- `Columns` = `fact_vacancy_day_vic[void_reason]`
- `Columns` = `fact_vacancy_day_vic[other_void_id]`
- `Columns` = `fact_vacancy_day_vic[other_vacancy_type_reason]`
- `Columns` = `fact_vacancy_day_vic[other_void_type]`

Formatting:

- sort by `fact_vacancy_day_vic[vacancy_date]` ascending

Trace usage notes:

- start with one `property_id`
- compare raw and adjusted dates in the audit tables first
- then compare the derived vacancy boundaries
- then use the day trace table only if the interval still looks wrong
- this page is for validation and development, not for management export

## Report Notes

- Use measures, not stored `full_*` columns, when a visual should respect the selected date range.
- Keep the detail page export-friendly.
- Keep the audit page plain and readable.
- Add a tooltip or text note that the vacancy logic follows `Vacant Calc.xlsx`.
- After any parameter change, rerun the main notebook and refresh the semantic model before relying on report output.

## Page 6: Exception Monitor

Purpose:

- expose source records that break expected business logic,
- support rapid data-quality review,
- send the user to the `Property Trace` page for investigation.

Current implemented exception rule:

- `TENANCY_OVERLAPS_VOID`
  A tenancy interval overlaps a void interval for the same property by at least one day.
- `OTHER_VACANCY_OUTSIDE_VOID`
  A Void row's other-vacancy range starts before the void start date or ends after the void end date. Counting is capped to the parent void overlap.

Page behavior:

- do not sync the global `dim_date[date]` slicer to this page,
- allow the entity, ownership, housing program, and property selectors to filter this page,
- use this page as a queue of bad records, not as a management summary page.

### Visual 1: Exception count card

Visual type:

- `Card`

Field well:

- `Data` = `[Exception Count]`

Formatting:

- display units = `None`

### Visual 2: Exception type slicer

Visual type:

- `Slicer`

Field well:

- `Field` = `audit_exceptions_vic[exception_type]`

Settings:

- style = `Dropdown`
- search = `On`

### Visual 3: Exception severity slicer

Visual type:

- `Slicer`

Field well:

- `Field` = `audit_exceptions_vic[exception_severity]`

Settings:

- style = `Dropdown`
- search = `On`

### Visual 4: Exception table

Visual type:

- `Table`

Field well:

- `Columns` = `audit_exceptions_vic[exception_id]`
- `Columns` = `audit_exceptions_vic[exception_type]`
- `Columns` = `audit_exceptions_vic[exception_severity]`
- `Columns` = `audit_exceptions_vic[property_id]`
- `Columns` = `audit_exceptions_vic[property_number]`
- `Columns` = `audit_exceptions_vic[property_short_address]`
- `Columns` = `audit_exceptions_vic[entity]`
- `Columns` = `audit_exceptions_vic[ownership]`
- `Columns` = `audit_exceptions_vic[housing_program]`
- `Columns` = `audit_exceptions_vic[property_type]`
- `Columns` = `audit_exceptions_vic[property_program]`
- `Columns` = `audit_exceptions_vic[current_stage]`
- `Columns` = `audit_exceptions_vic[tenancy_id]`
- `Columns` = `audit_exceptions_vic[tenancy_reference]`
- `Columns` = `audit_exceptions_vic[tenancy_current_stage]`
- `Columns` = `audit_exceptions_vic[raw_tenancy_start_date]`
- `Columns` = `audit_exceptions_vic[tenancy_start_date]`
- `Columns` = `audit_exceptions_vic[raw_tenancy_end_date]`
- `Columns` = `audit_exceptions_vic[tenancy_end_date]`
- `Columns` = `audit_exceptions_vic[void_id]`
- `Columns` = `audit_exceptions_vic[void_reference]`
- `Columns` = `audit_exceptions_vic[raw_void_start_date]`
- `Columns` = `audit_exceptions_vic[void_start_date]`
- `Columns` = `audit_exceptions_vic[raw_void_end_date]`
- `Columns` = `audit_exceptions_vic[void_end_date]`
- `Columns` = `audit_exceptions_vic[overlap_start_date]`
- `Columns` = `audit_exceptions_vic[overlap_end_date]`
- `Columns` = `audit_exceptions_vic[overlap_days]`
- `Columns` = `audit_exceptions_vic[exception_summary]`

Formatting:

- sort by `audit_exceptions_vic[overlap_days]` descending
- rename `audit_exceptions_vic[exception_id]` display label to `Exception ID`
- rename `audit_exceptions_vic[exception_type]` display label to `Exception Type`
- rename `audit_exceptions_vic[exception_severity]` display label to `Severity`
- rename `audit_exceptions_vic[property_id]` display label to `Property ID`
- rename `audit_exceptions_vic[property_number]` display label to `Property Number`
- rename `audit_exceptions_vic[property_short_address]` display label to `Property Address`
- rename `audit_exceptions_vic[entity]` display label to `Entity`
- rename `audit_exceptions_vic[ownership]` display label to `Ownership`
- rename `audit_exceptions_vic[housing_program]` display label to `Housing Program`
- rename `audit_exceptions_vic[property_type]` display label to `Property Type`
- rename `audit_exceptions_vic[property_program]` display label to `Property Program`
- rename `audit_exceptions_vic[current_stage]` display label to `Property Current Stage`
- rename `audit_exceptions_vic[tenancy_id]` display label to `Tenancy ID`
- rename `audit_exceptions_vic[tenancy_reference]` display label to `Tenancy Reference`
- rename `audit_exceptions_vic[tenancy_current_stage]` display label to `Tenancy Current Stage`
- rename `audit_exceptions_vic[raw_tenancy_start_date]` display label to `Raw Tenancy Start Date`
- rename `audit_exceptions_vic[tenancy_start_date]` display label to `Adjusted Tenancy Start Date`
- rename `audit_exceptions_vic[raw_tenancy_end_date]` display label to `Raw Tenancy End Date`
- rename `audit_exceptions_vic[tenancy_end_date]` display label to `Adjusted Tenancy End Date`
- rename `audit_exceptions_vic[void_id]` display label to `Void ID`
- rename `audit_exceptions_vic[void_reference]` display label to `Void Reference`
- rename `audit_exceptions_vic[raw_void_start_date]` display label to `Raw Void Start Date`
- rename `audit_exceptions_vic[void_start_date]` display label to `Adjusted Void Start Date`
- rename `audit_exceptions_vic[raw_void_end_date]` display label to `Raw Void End Date`
- rename `audit_exceptions_vic[void_end_date]` display label to `Adjusted Void End Date`
- rename `audit_exceptions_vic[overlap_start_date]` display label to `Overlap Start Date`
- rename `audit_exceptions_vic[overlap_end_date]` display label to `Overlap End Date`
- rename `audit_exceptions_vic[overlap_days]` display label to `Overlap Days`
- rename `audit_exceptions_vic[exception_summary]` display label to `Exception Summary`
- set column widths manually for readability
- enable export to Excel

Usage notes:

- start with the exception table
- sort by `Overlap Days`
- click a `Property ID` and move to the `Property Trace` page for deeper investigation
- keep this page for invalid-source monitoring, not for daily operational KPIs
