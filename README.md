# Community Health Data Collection & Analysis

A comprehensive, full-stack public health informatics web application designed for academic evaluation, capstone presentation, and healthcare internship projects.

---

## 📌 Project Overview

* **Project Title:** Community Health Data Collection & Analysis
* **Domain:** Healthcare Informatics / Public Health Epidemiology
* **Tech Stack:** Python (Flask), SQLite3, HTML5, CSS3, Vanilla JavaScript, Chart.js

### Problem Statement
Community health insights are often fragmented and delayed because health indicators are recorded manually or scattered across disparate spreadsheets and local clinics. This fragmentation creates significant hurdles for municipal health officers and epidemiological planners attempting to allocate preventative resources, monitor chronic diseases (e.g., hypertension, diabetes), and address regional healthcare inequities.

### Project Objective
To engineer a responsive, centralized full-stack web application that allows healthcare coordinators, clinicians, and researchers to:
1. **Digitally Collect** standardized, non-personally identifiable community health records with real-time biometric validation.
2. **Derive Clinical Metrics** (BMI, Blood Pressure stages, Glucose status, and comorbidity risk tiers) automatically upon data entry.
3. **Manage & Query** community data with multi-attribute filtering, debounce search, sorting, and pagination.
4. **Visualize Epidemiology Trends** using interactive Chart.js visualizations (diabetes, hypertension, age distribution, BMI, and location disparities).
5. **Generate & Export** executive public health assessment reports (printable to PDF) and raw datasets (CSV and JSON formats).

---

## 🚀 Key Features

* **Interactive Executive Dashboard:**
  * Real-time KPI summary cards (Sample size, Average Age, Average BMI, Diabetes prevalence, Hypertension prevalence, Zero-comorbidity rate).
  * Automated public health surveillance alerts.
  * Six responsive Chart.js visual graphs + full-width location comparison chart.
  * Live filter to isolate charts by specific community/ward.
  * Recent screening activity table.

* **Health Records Data Management:**
  * Fast, real-time client-side search across Record IDs, locations, and observational notes.
  * Multi-filter toolbar: Location, Gender, Diabetes Status, Hypertension Status, BMI Category, Risk Tier.
  * Click-to-sort column headers with ascending/descending indicators.
  * Dynamic pagination with selectable page sizes (15, 25, 50).
  * Patient Profile View Modal and Delete Confirmation Modal.

* **Biometric Data Entry with Live Classifier:**
  * Auto-generated sequential record IDs (e.g. `CHD-1086`).
  * Live dynamic BMI calculator with WHO category pill badges.
  * Real-time Blood Pressure categorization (AHA/ACC criteria) with cross-validation (detects when Diastolic &ge; Systolic).
  * Fasting Blood Glucose status classification (ADA guidelines).
  * Weighted Comorbidity Health Risk Tier Score (Low, Moderate, High) with dynamic color-shifting gauge.
  * Robust dual-layer validation (client-side feedback + server-side validation).

* **Epidemiological Analytics:**
  * Physical Activity level vs Chronic Disease burden cross-tabulation.
  * Age cohort susceptibility curve.
  * Adiposity (BMI) vs Diabetes correlation.
  * Tri-tier clinical risk stratification (Polar Area chart).
  * Evidence-based community health intervention recommendations.

* **Printable Executive Health Report & Export Portal:**
  * Professional formatted Community Health Assessment Report.
  * CSS Print Stylesheet (`@media print`) enabling 1-click **Print / Save as PDF**.
  * Complete CSV and JSON dataset export endpoints.

* **Academic Presentation & Viva Guide:**
  * Dedicated "About Project" section with architectural diagrams, ethical de-identification compliance statements, and examiner viva Q&A answers.

---

## 🛠️ Technology Stack

| Layer | Technology | Rationale for College Evaluation |
|---|---|---|
| **Backend** | Python Flask 3.x | Lightweight, explicit routing, clean Jinja2 integration, easy to explain during code walkthroughs. |
| **Database** | SQLite3 | Embedded, zero-configuration relational database with zero setup requirements; standard SQL syntax. |
| **Frontend** | HTML5, CSS3, ES6+ JavaScript | Fast, native browser performance without bulky Node/npm build steps; responsive grid and flexbox layout. |
| **Visualizations** | Chart.js 4.4 | Crisp, interactive HTML5 canvas charts with responsive resizing and custom tooltips. |
| **Icons & Fonts** | FontAwesome 6, Inter font | Clean, modern medical and dashboard UI aesthetic. |
| **Flask** | A Flask-based web application for community health data collection, analysis, and visualization. |

---

## 📂 Project Architecture

```
Community_Health_Data_Analysis/
├── app.py                     # Main Flask web application, routing, REST APIs & exports
├── database.py                # SQLite schema, indexing, seed data generator & query helpers
├── requirements.txt           # Python library dependencies
├── test_app.py                # Automated unittest suite (13 comprehensive tests)
├── README.md                  # Project documentation & presentation guide
├── community_health.db        # SQLite relational database (created automatically)
│
├── static/
│   ├── css/
│   │   └── style.css          # Modern medical theme, responsive grid, badges, print CSS
│   └── js/
│       ├── main.js            # Global utilities, toast alerts, mobile drawer navigation
│       ├── dashboard.js       # Chart.js initialization and dynamic location filtering
│       ├── records.js         # Records table search, multi-filter, pagination, view & delete
│       ├── add_record.js      # Live real-time BMI, BP, glucose and risk meter calculators
│       └── analytics.js       # Advanced epidemiological cross-tabulations and charts
│
└── templates/
    ├── base.html              # Master layout with responsive sidebar, header, flash alerts
    ├── dashboard.html         # Main overview dashboard with KPI cards and charts
    ├── records.html           # Filterable data table with detail and delete modals
    ├── add_record.html        # Data entry form with live biometric classifier
    ├── analytics.html         # In-depth statistical analysis & correlation matrix
    ├── reports.html           # Official printable assessment report & export center
    └── about.html             # Project background, architecture, ethics & viva Q&A
```

---

## 🩺 Clinical Classifications & Standards Used

1. **Body Mass Index (BMI) — World Health Organization (WHO):**
   * $\text{BMI} < 18.5$: Underweight
   * $18.5 \le \text{BMI} < 25.0$: Normal weight
   * $25.0 \le \text{BMI} < 30.0$: Overweight
   * $\text{BMI} \ge 30.0$: Obese

2. **Blood Pressure (BP) — American Heart Association (AHA / ACC):**
   * Systolic $< 120$ AND Diastolic $< 80$: Normal
   * Systolic $120–129$ AND Diastolic $< 80$: Elevated
   * Systolic $130–139$ OR Diastolic $80–89$: Hypertension Stage 1
   * Systolic $140–179$ OR Diastolic $90–119$: Hypertension Stage 2
   * Systolic $\ge 180$ OR Diastolic $\ge 120$: Hypertensive Crisis

3. **Fasting Blood Glucose — American Diabetes Association (ADA):**
   * $< 100 \text{ mg/dL}$: Normal (Euglycemic)
   * $100 – 125 \text{ mg/dL}$: Prediabetic (Impaired Fasting Glucose)
   * $\ge 126 \text{ mg/dL}$: Diabetic

4. **Weighted Public Health Risk Tier:**
   * Calculated dynamically based on age ($\ge 55, \ge 65$), obesity, hypertension stages, diabetic fasting levels, smoking status, and physical inactivity.
   * Tiers: **Low Risk** (0–2 points), **Moderate Risk** (3–5 points), **High Risk** (6+ points).

---

## ⚡ Installation & Execution Guide

### Prerequisites
* Python 3.8 or newer (Python 3.10+ recommended)
* `pip` package manager

### 1. Clone or Open Project Folder
Open your terminal / command prompt in the project root:
```bash
cd Community_Health_Data_Analysis
```

### 2. (Optional) Create & Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

### 5. Access the Web Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

> **Note on Initial Startup:**
> The application will automatically initialize `community_health.db` and populate it with 85 diverse, realistic, anonymized community records across 7 distinct areas. You can re-seed or reset this data anytime using the **Reset Data** button in the top navigation bar.

---

## 🧪 Running the Automated Test Suite

The project includes an automated test suite verifying all routes, CRUD operations, database queries, calculators, and exports:

```bash
python -m unittest test_app.py
```

Expected Output:
```
.............
----------------------------------------------------------------------
Ran 13 tests in 0.15s

OK
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/stats` | Returns aggregate summary KPIs (mean age, BMI, cases, rates). |
| `GET` | `/api/charts/data?location=...` | Returns dataset structured for Chart.js (optional location filter). |
| `GET` | `/api/records?...` | Returns filterable, searchable, sorted, paginated records list. |
| `GET` | `/api/records/<id>` | Returns full details for a single record. |
| `POST` | `/api/records` | Validates and creates a new community health record. |
| `PUT` | `/api/records/<id>` | Updates an existing health record and recalculates indicators. |
| `DELETE` | `/api/records/<id>` | Permanently removes a health record. |
| `POST` | `/api/calculate-metrics` | Live endpoint providing instantaneous BMI, BP, glucose and risk ratings. |
| `POST` | `/api/reset-sample-data` | Re-seeds the database with 85 realistic sample records. |
| `GET` | `/export/csv` | Streams downloadable CSV file with all records. |
| `GET` | `/export/json` | Streams downloadable formatted JSON export file. |

---

## 🎓 College Review & Viva Talking Points

When presenting this project to examiners or review panels, emphasize the following points:

1. **Architecture Decisions:**
   * *Why Flask over Django?* Flask provides a lightweight, transparent micro-architecture with minimal boilerplate, allowing complete control over SQL queries, data flow, and front-end rendering.
   * *Why SQLite?* SQLite is an ACID-compliant, serverless relational database engine stored as a single file, eliminating complex external database installation while demonstrating relational normalization, primary keys, and index optimization.

2. **Epidemiological Value:**
   * Instead of merely collecting raw text, this application implements standardized WHO, AHA, and ADA guidelines directly into the data pipeline.
   * Healthcare planners can pinpoint geographic disease hot-spots (e.g. higher hypertension in specific wards) and target mobile screening units accordingly.

3. **Data Privacy & Ethics:**
   * No personally identifiable information (PII) such as patient names, phone numbers, or government IDs are accepted or stored, adhering strictly to HIPAA de-identification standards.

---

## 📄 License
Academic Project — Free for learning, modification, and educational distribution.
## Live Demo 
 [Open Live Project] https://community-health-data-analysis.onrender.com

