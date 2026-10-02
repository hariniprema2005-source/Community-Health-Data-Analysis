"""
Database module for Community Health Data Collection & Analysis
Handles SQLite schema creation, initial realistic anonymized seed data,
and comprehensive query helpers for CRUD, filtering, and public health analytics.
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'community_health.db')


def get_db_connection():
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def calculate_health_metrics(height_cm, weight_kg, systolic_bp, diastolic_bp, blood_glucose):
    """
    Computes standard epidemiological classifications for BMI, Blood Pressure,
    and Fasting Blood Glucose based on WHO, AHA, and ADA clinical thresholds.
    """
    # 1. BMI calculation
    height_m = float(height_cm) / 100.0
    bmi = round(float(weight_kg) / (height_m * height_m), 1) if height_m > 0 else 0.0

    if bmi < 18.5:
        bmi_category = "Underweight"
    elif bmi < 25.0:
        bmi_category = "Normal"
    elif bmi < 30.0:
        bmi_category = "Overweight"
    else:
        bmi_category = "Obese"

    # 2. Blood Pressure classification (AHA/ACC guidelines)
    sbp = int(systolic_bp)
    dbp = int(diastolic_bp)

    if sbp >= 180 or dbp >= 120:
        bp_category = "Hypertensive Crisis"
    elif sbp >= 140 or dbp >= 90:
        bp_category = "Hypertension Stage 2"
    elif (130 <= sbp <= 139) or (80 <= dbp <= 89):
        bp_category = "Hypertension Stage 1"
    elif (120 <= sbp <= 129) and dbp < 80:
        bp_category = "Elevated"
    else:
        bp_category = "Normal"

    # 3. Blood Glucose classification (ADA Fasting guidelines)
    glucose = float(blood_glucose)
    if glucose < 100.0:
        glucose_status = "Normal"
    elif glucose < 126.0:
        glucose_status = "Prediabetic"
    else:
        glucose_status = "Diabetic"

    return {
        "bmi": bmi,
        "bmi_category": bmi_category,
        "bp_category": bp_category,
        "glucose_status": glucose_status
    }


def calculate_risk_level(age, bmi_cat, bp_cat, glucose_stat, diabetes, hypertension, smoking, physical_activity):
    """Calculates an overall community health risk tier based on clinical risk score."""
    score = 0
    if int(age) >= 55:
        score += 1
    if int(age) >= 65:
        score += 1
    if bmi_cat in ["Overweight", "Obese"]:
        score += 1 if bmi_cat == "Overweight" else 2
    if bp_cat in ["Hypertension Stage 1", "Hypertension Stage 2", "Hypertensive Crisis"]:
        score += 2 if bp_cat != "Hypertension Stage 1" else 1
    if glucose_stat == "Diabetic" or diabetes == "Yes":
        score += 2
    elif glucose_stat == "Prediabetic" or diabetes == "Pre-diabetic":
        score += 1
    if hypertension == "Yes":
        score += 1
    if smoking == "Current":
        score += 2
    elif smoking == "Former":
        score += 1
    if physical_activity == "Sedentary":
        score += 1

    if score <= 2:
        return "Low"
    elif score <= 5:
        return "Moderate"
    else:
        return "High"


def init_db():
    """Initializes the database schema and indexes."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS health_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_code TEXT UNIQUE NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        location TEXT NOT NULL,
        height_cm REAL NOT NULL,
        weight_kg REAL NOT NULL,
        bmi REAL NOT NULL,
        bmi_category TEXT NOT NULL,
        systolic_bp INTEGER NOT NULL,
        diastolic_bp INTEGER NOT NULL,
        bp_category TEXT NOT NULL,
        blood_glucose REAL NOT NULL,
        glucose_status TEXT NOT NULL,
        diabetes TEXT NOT NULL,
        hypertension TEXT NOT NULL,
        smoking_status TEXT NOT NULL,
        physical_activity TEXT NOT NULL,
        alcohol_intake TEXT NOT NULL,
        general_health TEXT NOT NULL,
        healthcare_access TEXT NOT NULL,
        risk_score TEXT NOT NULL,
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # Performance indexes for search, filtering, and aggregation
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_location ON health_records(location);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_gender ON health_records(gender);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_diabetes ON health_records(diabetes);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_hypertension ON health_records(hypertension);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_risk ON health_records(risk_score);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_records_bmi_cat ON health_records(bmi_category);")

    conn.commit()
    conn.close()


def generate_record_code(cursor):
    """Generates a sequential human-readable record code like CHD-1045."""
    cursor.execute("SELECT MAX(id) FROM health_records")
    row = cursor.fetchone()
    next_id = (row[0] or 0) + 1
    return f"CHD-{next_id + 1000}"


def seed_sample_data(force=False):
    """
    Populates the database with realistic, diverse, anonymized community health records.
    Only seeds if the table is currently empty, unless force=True.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM health_records")
    count = cursor.fetchone()[0]

    if count > 0 and not force:
        conn.close()
        return count

    if force:
        cursor.execute("DELETE FROM health_records")
        conn.commit()

    # Pre-defined realistic community areas
    locations = [
        "North District",
        "South Ward",
        "East River Basin",
        "West Valley",
        "Central Metro",
        "Highland Colony",
        "Lakeside Suburb"
    ]

    genders = ["Male", "Female", "Other"]
    smoking_options = ["Never", "Former", "Current"]
    activity_options = ["Sedentary", "Moderate", "Active"]
    alcohol_options = ["None", "Occasional", "Regular"]
    health_ratings = ["Excellent", "Good", "Fair", "Poor"]

    # Sample observational notes for realistic clinical/community records
    sample_notes = [
        "Routine community wellness screening.",
        "Referred for nutritional counseling and lifestyle guidance.",
        "Participated in mobile healthcare clinic screening program.",
        "History of borderline hypertension reported during visit.",
        "Active member of community exercise initiative.",
        "Recommended follow-up blood glucose testing in 3 months.",
        "Advised on smoking cessation resources and support groups.",
        "Standard public health baseline demographic survey.",
        "Reports good adherence to prescribed preventative checkups.",
        "Shows elevated blood pressure; encouraged sodium reduction.",
        "High physical activity; excellent cardiovascular baseline.",
        "No prior chronic disease diagnosis on file."
    ]

    # Seed 85 realistic records with realistic correlations
    random.seed(42)  # reproducible seed
    base_date = datetime.now() - timedelta(days=90)

    for i in range(1, 86):
        record_code = f"CHD-{1000 + i}"
        age = random.choices(
            [random.randint(18, 30), random.randint(31, 45), random.randint(46, 60), random.randint(61, 80)],
            weights=[25, 30, 25, 20]
        )[0]

        gender = random.choices(genders, weights=[48, 48, 4])[0]
        location = random.choice(locations)

        # Height & Weight based on gender and age
        if gender == "Male":
            height_cm = round(random.uniform(162.0, 188.0), 1)
            # Older individuals or sedentary more likely higher weight
            base_weight = random.uniform(62.0, 102.0)
            if age > 45:
                base_weight += random.uniform(2.0, 8.0)
            weight_kg = round(base_weight, 1)
        elif gender == "Female":
            height_cm = round(random.uniform(150.0, 172.0), 1)
            base_weight = random.uniform(48.0, 92.0)
            if age > 45:
                base_weight += random.uniform(2.0, 6.0)
            weight_kg = round(base_weight, 1)
        else:
            height_cm = round(random.uniform(155.0, 180.0), 1)
            weight_kg = round(random.uniform(55.0, 90.0), 1)

        # Correlated Blood Pressure
        # Older or higher BMI individuals tend to have higher BP
        is_older = age > 50
        bmi_rough = weight_kg / ((height_cm / 100.0) ** 2)

        if is_older or bmi_rough > 28:
            systolic_bp = random.choices(
                [random.randint(110, 125), random.randint(126, 139), random.randint(140, 168)],
                weights=[25, 40, 35]
            )[0]
            diastolic_bp = random.randint(72, min(105, int(systolic_bp * 0.68 + 10)))
        else:
            systolic_bp = random.choices(
                [random.randint(105, 122), random.randint(123, 134), random.randint(135, 148)],
                weights=[60, 25, 15]
            )[0]
            diastolic_bp = random.randint(65, min(92, int(systolic_bp * 0.65 + 5)))

        # Correlated Fasting Glucose
        if is_older or bmi_rough > 27:
            blood_glucose = round(random.choices(
                [random.uniform(80.0, 99.0), random.uniform(100.0, 125.0), random.uniform(126.0, 180.0)],
                weights=[35, 40, 25]
            )[0], 1)
        else:
            blood_glucose = round(random.choices(
                [random.uniform(75.0, 99.0), random.uniform(100.0, 120.0), random.uniform(121.0, 150.0)],
                weights=[70, 22, 8]
            )[0], 1)

        # Compute derived metrics
        metrics = calculate_health_metrics(height_cm, weight_kg, systolic_bp, diastolic_bp, blood_glucose)

        # Diabetes status aligned with glucose
        if metrics["glucose_status"] == "Diabetic":
            diabetes = random.choices(["Yes", "No"], weights=[85, 15])[0]
        elif metrics["glucose_status"] == "Prediabetic":
            diabetes = random.choices(["Pre-diabetic", "No"], weights=[70, 30])[0]
        else:
            diabetes = "No"

        # Hypertension status aligned with BP
        if metrics["bp_category"] in ["Hypertension Stage 1", "Hypertension Stage 2", "Hypertensive Crisis"]:
            hypertension = random.choices(["Yes", "No"], weights=[80, 20])[0]
        else:
            hypertension = "No"

        smoking = random.choices(smoking_options, weights=[60, 22, 18])[0]
        activity = random.choices(activity_options, weights=[35, 45, 20])[0]
        alcohol = random.choices(alcohol_options, weights=[45, 40, 15])[0]

        # General health
        if metrics["bmi_category"] == "Normal" and hypertension == "No" and diabetes == "No":
            gen_health = random.choices(health_ratings, weights=[45, 40, 12, 3])[0]
        elif metrics["bmi_category"] == "Obese" or hypertension == "Yes" or diabetes == "Yes":
            gen_health = random.choices(health_ratings, weights=[5, 25, 45, 25])[0]
        else:
            gen_health = random.choices(health_ratings, weights=[20, 50, 25, 5])[0]

        # Healthcare access (geographic variation)
        if location in ["North District", "Central Metro", "Lakeside Suburb"]:
            healthcare_access = random.choices(["Yes", "No"], weights=[88, 12])[0]
        else:
            healthcare_access = random.choices(["Yes", "No"], weights=[68, 32])[0]

        risk_score = calculate_risk_level(
            age=age,
            bmi_cat=metrics["bmi_category"],
            bp_cat=metrics["bp_category"],
            glucose_stat=metrics["glucose_status"],
            diabetes=diabetes,
            hypertension=hypertension,
            smoking=smoking,
            physical_activity=activity
        )

        record_date = (base_date + timedelta(days=random.randint(0, 88), hours=random.randint(1, 23))).strftime("%Y-%m-%d %H:%M:%S")
        note = random.choice(sample_notes)

        cursor.execute("""
            INSERT INTO health_records (
                record_code, age, gender, location, height_cm, weight_kg,
                bmi, bmi_category, systolic_bp, diastolic_bp, bp_category,
                blood_glucose, glucose_status, diabetes, hypertension,
                smoking_status, physical_activity, alcohol_intake,
                general_health, healthcare_access, risk_score, notes,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record_code, age, gender, location, height_cm, weight_kg,
            metrics["bmi"], metrics["bmi_category"], systolic_bp, diastolic_bp, metrics["bp_category"],
            blood_glucose, metrics["glucose_status"], diabetes, hypertension,
            smoking, activity, alcohol,
            gen_health, healthcare_access, risk_score, note,
            record_date, record_date
        ))

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM health_records")
    total = cursor.fetchone()[0]
    conn.close()
    return total


# -------------------------------------------------------------
# Record Query & CRUD Functions
# -------------------------------------------------------------

def get_records(search="", location="", gender="", diabetes="", hypertension="",
                bmi_cat="", risk="", sort_by="id", sort_order="desc", page=1, per_page=15):
    """Fetches paginated records with dynamic filtering and sorting."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM health_records WHERE 1=1"
    params = []

    if search:
        query += " AND (record_code LIKE ? OR location LIKE ? OR notes LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])

    if location:
        query += " AND location = ?"
        params.append(location)

    if gender:
        query += " AND gender = ?"
        params.append(gender)

    if diabetes:
        query += " AND diabetes = ?"
        params.append(diabetes)

    if hypertension:
        query += " AND hypertension = ?"
        params.append(hypertension)

    if bmi_cat:
        query += " AND bmi_category = ?"
        params.append(bmi_cat)

    if risk:
        query += " AND risk_score = ?"
        params.append(risk)

    # Count total matching
    count_query = f"SELECT COUNT(*) FROM ({query})"
    cursor.execute(count_query, params)
    total_records = cursor.fetchone()[0]

    # Validate sorting column
    valid_sorts = {
        "id": "id",
        "record_code": "record_code",
        "age": "age",
        "gender": "gender",
        "location": "location",
        "bmi": "bmi",
        "systolic_bp": "systolic_bp",
        "blood_glucose": "blood_glucose",
        "risk_score": "risk_score",
        "created_at": "created_at"
    }
    col = valid_sorts.get(sort_by, "id")
    order = "ASC" if sort_order.lower() == "asc" else "DESC"

    query += f" ORDER BY {col} {order}"

    # Pagination
    offset = (page - 1) * per_page
    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    records = [dict(row) for row in rows]

    total_pages = max(1, (total_records + per_page - 1) // per_page)

    conn.close()
    return {
        "records": records,
        "total": total_records,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }


def get_all_records_for_export(location="", gender="", diabetes="", hypertension=""):
    """Fetches all matching records without pagination for CSV/JSON export."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM health_records WHERE 1=1"
    params = []

    if location:
        query += " AND location = ?"
        params.append(location)
    if gender:
        query += " AND gender = ?"
        params.append(gender)
    if diabetes:
        query += " AND diabetes = ?"
        params.append(diabetes)
    if hypertension:
        query += " AND hypertension = ?"
        params.append(hypertension)

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_record_by_id(record_id):
    """Retrieves a single record by its primary key ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM health_records WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_record(data):
    """
    Validates and inserts a new community health record.
    Calculates all derived medical indicators automatically.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    record_code = data.get("record_code") or generate_record_code(cursor)
    age = int(data["age"])
    gender = data["gender"]
    location = data["location"].strip()
    height_cm = float(data["height_cm"])
    weight_kg = float(data["weight_kg"])
    systolic_bp = int(data["systolic_bp"])
    diastolic_bp = int(data["diastolic_bp"])
    blood_glucose = float(data["blood_glucose"])
    diabetes = data.get("diabetes", "No")
    hypertension = data.get("hypertension", "No")
    smoking_status = data.get("smoking_status", "Never")
    physical_activity = data.get("physical_activity", "Moderate")
    alcohol_intake = data.get("alcohol_intake", "None")
    general_health = data.get("general_health", "Good")
    healthcare_access = data.get("healthcare_access", "Yes")
    notes = data.get("notes", "").strip()

    metrics = calculate_health_metrics(height_cm, weight_kg, systolic_bp, diastolic_bp, blood_glucose)
    risk_score = calculate_risk_level(
        age, metrics["bmi_category"], metrics["bp_category"],
        metrics["glucose_status"], diabetes, hypertension,
        smoking_status, physical_activity
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO health_records (
            record_code, age, gender, location, height_cm, weight_kg,
            bmi, bmi_category, systolic_bp, diastolic_bp, bp_category,
            blood_glucose, glucose_status, diabetes, hypertension,
            smoking_status, physical_activity, alcohol_intake,
            general_health, healthcare_access, risk_score, notes,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record_code, age, gender, location, height_cm, weight_kg,
        metrics["bmi"], metrics["bmi_category"], systolic_bp, diastolic_bp, metrics["bp_category"],
        blood_glucose, metrics["glucose_status"], diabetes, hypertension,
        smoking_status, physical_activity, alcohol_intake,
        general_health, healthcare_access, risk_score, notes,
        now, now
    ))

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_record(record_id, data):
    """Updates an existing health record and recalculates derived clinical metrics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    age = int(data["age"])
    gender = data["gender"]
    location = data["location"].strip()
    height_cm = float(data["height_cm"])
    weight_kg = float(data["weight_kg"])
    systolic_bp = int(data["systolic_bp"])
    diastolic_bp = int(data["diastolic_bp"])
    blood_glucose = float(data["blood_glucose"])
    diabetes = data.get("diabetes", "No")
    hypertension = data.get("hypertension", "No")
    smoking_status = data.get("smoking_status", "Never")
    physical_activity = data.get("physical_activity", "Moderate")
    alcohol_intake = data.get("alcohol_intake", "None")
    general_health = data.get("general_health", "Good")
    healthcare_access = data.get("healthcare_access", "Yes")
    notes = data.get("notes", "").strip()

    metrics = calculate_health_metrics(height_cm, weight_kg, systolic_bp, diastolic_bp, blood_glucose)
    risk_score = calculate_risk_level(
        age, metrics["bmi_category"], metrics["bp_category"],
        metrics["glucose_status"], diabetes, hypertension,
        smoking_status, physical_activity
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE health_records SET
            age = ?, gender = ?, location = ?, height_cm = ?, weight_kg = ?,
            bmi = ?, bmi_category = ?, systolic_bp = ?, diastolic_bp = ?, bp_category = ?,
            blood_glucose = ?, glucose_status = ?, diabetes = ?, hypertension = ?,
            smoking_status = ?, physical_activity = ?, alcohol_intake = ?,
            general_health = ?, healthcare_access = ?, risk_score = ?, notes = ?,
            updated_at = ?
        WHERE id = ?
    """, (
        age, gender, location, height_cm, weight_kg,
        metrics["bmi"], metrics["bmi_category"], systolic_bp, diastolic_bp, metrics["bp_category"],
        blood_glucose, metrics["glucose_status"], diabetes, hypertension,
        smoking_status, physical_activity, alcohol_intake,
        general_health, healthcare_access, risk_score, notes,
        now, record_id
    ))

    conn.commit()
    conn.close()
    return True


def delete_record(record_id):
    """Deletes a record from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM health_records WHERE id = ?", (record_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# -------------------------------------------------------------
# Summary KPIs & Chart Data Aggregations
# -------------------------------------------------------------

def get_dashboard_summary():
    """
    Computes key performance indicators (KPIs) for the primary dashboard:
    - Total records
    - Average age
    - Average BMI
    - Diabetes cases & prevalence rate
    - Hypertension cases & prevalence rate
    - Normal health cases
    - High-risk cases
    - Average blood glucose
    - Average blood pressure
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_records,
            ROUND(AVG(age), 1) AS avg_age,
            ROUND(AVG(bmi), 1) AS avg_bmi,
            ROUND(AVG(blood_glucose), 1) AS avg_glucose,
            ROUND(AVG(systolic_bp), 1) AS avg_systolic,
            ROUND(AVG(diastolic_bp), 1) AS avg_diastolic,
            SUM(CASE WHEN diabetes = 'Yes' THEN 1 ELSE 0 END) AS diabetes_cases,
            SUM(CASE WHEN diabetes = 'Pre-diabetic' THEN 1 ELSE 0 END) AS prediabetes_cases,
            SUM(CASE WHEN hypertension = 'Yes' THEN 1 ELSE 0 END) AS hypertension_cases,
            SUM(CASE WHEN bmi_category = 'Normal' AND diabetes = 'No' AND hypertension = 'No' THEN 1 ELSE 0 END) AS normal_health_cases,
            SUM(CASE WHEN risk_score = 'High' THEN 1 ELSE 0 END) AS high_risk_cases,
            SUM(CASE WHEN healthcare_access = 'Yes' THEN 1 ELSE 0 END) AS healthcare_access_yes
        FROM health_records
    """)
    row = cursor.fetchone()
    conn.close()

    total = row["total_records"] or 0
    diabetes_cases = row["diabetes_cases"] or 0
    hypertension_cases = row["hypertension_cases"] or 0
    normal_health = row["normal_health_cases"] or 0
    high_risk = row["high_risk_cases"] or 0

    diabetes_rate = round((diabetes_cases / total) * 100, 1) if total > 0 else 0
    hypertension_rate = round((hypertension_cases / total) * 100, 1) if total > 0 else 0
    normal_rate = round((normal_health / total) * 100, 1) if total > 0 else 0
    high_risk_rate = round((high_risk / total) * 100, 1) if total > 0 else 0

    return {
        "total_records": total,
        "avg_age": row["avg_age"] or 0,
        "avg_bmi": row["avg_bmi"] or 0,
        "avg_glucose": row["avg_glucose"] or 0,
        "avg_systolic": row["avg_systolic"] or 0,
        "avg_diastolic": row["avg_diastolic"] or 0,
        "diabetes_cases": diabetes_cases,
        "prediabetes_cases": row["prediabetes_cases"] or 0,
        "diabetes_rate": diabetes_rate,
        "hypertension_cases": hypertension_cases,
        "hypertension_rate": hypertension_rate,
        "normal_health_cases": normal_health,
        "normal_health_rate": normal_rate,
        "high_risk_cases": high_risk,
        "high_risk_rate": high_risk_rate,
        "healthcare_access_pct": round(((row["healthcare_access_yes"] or 0) / total) * 100, 1) if total > 0 else 0
    }


def get_charts_data(location=""):
    """
    Returns structured data formatted specifically for Chart.js:
    1. Diabetes Distribution
    2. Hypertension Distribution
    3. Age Group Distribution
    4. Gender Distribution
    5. BMI Category Distribution
    6. Location-wise Health Statistics
    7. Blood Pressure Categories
    8. Risk Score Breakdown
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    where_clause = ""
    params = []
    if location:
        where_clause = "WHERE location = ?"
        params.append(location)

    # 1. Diabetes distribution
    cursor.execute(f"""
        SELECT diabetes, COUNT(*) as count
        FROM health_records {where_clause}
        GROUP BY diabetes
    """, params)
    diabetes_map = {"Yes": 0, "No": 0, "Pre-diabetic": 0}
    for r in cursor.fetchall():
        diabetes_map[r["diabetes"]] = r["count"]

    # 2. Hypertension distribution
    cursor.execute(f"""
        SELECT hypertension, COUNT(*) as count
        FROM health_records {where_clause}
        GROUP BY hypertension
    """, params)
    hypertension_map = {"Yes": 0, "No": 0}
    for r in cursor.fetchall():
        hypertension_map[r["hypertension"]] = r["count"]

    # 3. Age Groups
    cursor.execute(f"""
        SELECT
            CASE
                WHEN age < 18 THEN '<18'
                WHEN age BETWEEN 18 AND 35 THEN '18-35'
                WHEN age BETWEEN 36 AND 50 THEN '36-50'
                WHEN age BETWEEN 51 AND 65 THEN '51-65'
                ELSE '65+'
            END as age_group,
            COUNT(*) as count
        FROM health_records {where_clause}
        GROUP BY age_group
    """, params)
    age_groups = {"<18": 0, "18-35": 0, "36-50": 0, "51-65": 0, "65+": 0}
    for r in cursor.fetchall():
        if r["age_group"] in age_groups:
            age_groups[r["age_group"]] = r["count"]

    # 4. Gender
    cursor.execute(f"""
        SELECT gender, COUNT(*) as count
        FROM health_records {where_clause}
        GROUP BY gender
    """, params)
    genders = {"Male": 0, "Female": 0, "Other": 0}
    for r in cursor.fetchall():
        genders[r["gender"]] = r["count"]

    # 5. BMI Category
    cursor.execute(f"""
        SELECT bmi_category, COUNT(*) as count
        FROM health_records {where_clause}
        GROUP BY bmi_category
    """, params)
    bmi_categories = {"Underweight": 0, "Normal": 0, "Overweight": 0, "Obese": 0}
    for r in cursor.fetchall():
        if r["bmi_category"] in bmi_categories:
            bmi_categories[r["bmi_category"]] = r["count"]

    # 6. Blood pressure categories
    cursor.execute(f"""
        SELECT bp_category, COUNT(*) as count
        FROM health_records {where_clause}
        GROUP BY bp_category
    """, params)
    bp_categories = {
        "Normal": 0,
        "Elevated": 0,
        "Hypertension Stage 1": 0,
        "Hypertension Stage 2": 0,
        "Hypertensive Crisis": 0
    }
    for r in cursor.fetchall():
        if r["bp_category"] in bp_categories:
            bp_categories[r["bp_category"]] = r["count"]

    # 7. Risk level
    cursor.execute(f"""
        SELECT risk_score, COUNT(*) as count
        FROM health_records {where_clause}
        GROUP BY risk_score
    """, params)
    risk_breakdown = {"Low": 0, "Moderate": 0, "High": 0}
    for r in cursor.fetchall():
        if r["risk_score"] in risk_breakdown:
            risk_breakdown[r["risk_score"]] = r["count"]

    # 8. Location-wise statistics (Overall community comparison)
    cursor.execute("""
        SELECT
            location,
            COUNT(*) as total,
            SUM(CASE WHEN diabetes = 'Yes' THEN 1 ELSE 0 END) as diabetes_count,
            SUM(CASE WHEN hypertension = 'Yes' THEN 1 ELSE 0 END) as hypertension_count,
            SUM(CASE WHEN bmi_category = 'Obese' THEN 1 ELSE 0 END) as obese_count,
            ROUND(AVG(bmi), 1) as avg_bmi,
            ROUND(AVG(age), 1) as avg_age
        FROM health_records
        GROUP BY location
        ORDER BY total DESC
    """)
    location_stats = [dict(r) for r in cursor.fetchall()]

    # 9. Lifestyle cross-tabulations (for analytics)
    cursor.execute(f"""
        SELECT
            physical_activity,
            COUNT(*) as total,
            SUM(CASE WHEN hypertension = 'Yes' OR diabetes = 'Yes' THEN 1 ELSE 0 END) as chronic_cases
        FROM health_records {where_clause}
        GROUP BY physical_activity
    """, params)
    activity_impact = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "diabetes": diabetes_map,
        "hypertension": hypertension_map,
        "age_groups": age_groups,
        "genders": genders,
        "bmi_categories": bmi_categories,
        "bp_categories": bp_categories,
        "risk_breakdown": risk_breakdown,
        "location_stats": location_stats,
        "activity_impact": activity_impact
    }


def get_distinct_locations():
    """Returns a list of all distinct community locations in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT location FROM health_records ORDER BY location ASC")
    rows = cursor.fetchall()
    conn.close()
    return [r["location"] for r in rows]
