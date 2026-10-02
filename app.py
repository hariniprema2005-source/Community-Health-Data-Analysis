"""
Community Health Data Collection & Analysis
Main Flask Application Entry Point
"""

import csv
import io
import json
from datetime import datetime
from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, flash, Response, make_response
)
import database

app = Flask(__name__)
app.secret_key = "community-health-secret-key-2026"


# Ensure database and sample data are initialized on startup
with app.app_context():
    database.init_db()
    database.seed_sample_data()


# -------------------------------------------------------------
# Input Validation Helper
# -------------------------------------------------------------

def validate_record_data(data):
    """Validates raw health record inputs. Returns (is_valid, errors_dict)."""
    errors = {}

    # 1. Age
    try:
        age = int(data.get("age", ""))
        if age < 1 or age > 120:
            errors["age"] = "Age must be between 1 and 120 years."
    except (ValueError, TypeError):
        errors["age"] = "Please enter a valid whole number for age."

    # 2. Gender
    gender = data.get("gender", "").strip()
    if gender not in ["Male", "Female", "Other"]:
        errors["gender"] = "Please select a valid gender option."

    # 3. Location
    location = data.get("location", "").strip()
    if not location or len(location) < 2:
        errors["location"] = "Location/Area name must be at least 2 characters."

    # 4. Height (cm)
    try:
        height = float(data.get("height_cm", ""))
        if height < 40 or height > 250:
            errors["height_cm"] = "Height must be between 40 cm and 250 cm."
    except (ValueError, TypeError):
        errors["height_cm"] = "Please enter a valid numerical height in cm."

    # 5. Weight (kg)
    try:
        weight = float(data.get("weight_kg", ""))
        if weight < 2 or weight > 350:
            errors["weight_kg"] = "Weight must be between 2 kg and 350 kg."
    except (ValueError, TypeError):
        errors["weight_kg"] = "Please enter a valid numerical weight in kg."

    # 6. Systolic BP
    try:
        sbp = int(data.get("systolic_bp", ""))
        if sbp < 60 or sbp > 260:
            errors["systolic_bp"] = "Systolic BP must be between 60 and 260 mmHg."
    except (ValueError, TypeError):
        errors["systolic_bp"] = "Please enter a valid systolic blood pressure."

    # 7. Diastolic BP
    try:
        dbp = int(data.get("diastolic_bp", ""))
        if dbp < 40 or dbp > 160:
            errors["diastolic_bp"] = "Diastolic BP must be between 40 and 160 mmHg."
    except (ValueError, TypeError):
        errors["diastolic_bp"] = "Please enter a valid diastolic blood pressure."

    # Cross-check BP logic
    if "systolic_bp" not in errors and "diastolic_bp" not in errors:
        if dbp >= sbp:
            errors["diastolic_bp"] = "Diastolic BP must be lower than Systolic BP."

    # 8. Blood Glucose
    try:
        glucose = float(data.get("blood_glucose", ""))
        if glucose < 30 or glucose > 600:
            errors["blood_glucose"] = "Fasting glucose must be between 30 and 600 mg/dL."
    except (ValueError, TypeError):
        errors["blood_glucose"] = "Please enter a valid blood glucose level."

    return len(errors) == 0, errors


# -------------------------------------------------------------
# Frontend Page Routes
# -------------------------------------------------------------

@app.route("/")
@app.route("/dashboard")
def dashboard():
    """Renders the main public health dashboard with KPIs and visualizations."""
    summary = database.get_dashboard_summary()
    locations = database.get_distinct_locations()
    # Recent 5 records for dashboard activity table
    recent_result = database.get_records(page=1, per_page=6, sort_by="id", sort_order="desc")
    return render_template(
        "dashboard.html",
        active_page="dashboard",
        summary=summary,
        locations=locations,
        recent_records=recent_result["records"]
    )


@app.route("/records")
def records_view():
    """Renders the health data management page with filterable records table."""
    locations = database.get_distinct_locations()
    return render_template(
        "records.html",
        active_page="records",
        locations=locations
    )


@app.route("/add-record", methods=["GET", "POST"])
def add_record_view():
    """Renders the data entry form and handles standard form submissions."""
    locations = database.get_distinct_locations()

    if request.method == "POST":
        form_data = request.form.to_dict()
        is_valid, errors = validate_record_data(form_data)

        if not is_valid:
            return render_template(
                "add_record.html",
                active_page="add_record",
                locations=locations,
                errors=errors,
                form_data=form_data
            )

        try:
            new_id = database.add_record(form_data)
            flash("Health record added successfully!", "success")
            return redirect(url_for("records_view"))
        except Exception as e:
            flash(f"Error adding record: {str(e)}", "danger")
            return render_template(
                "add_record.html",
                active_page="add_record",
                locations=locations,
                errors={"general": str(e)},
                form_data=form_data
            )

    return render_template(
        "add_record.html",
        active_page="add_record",
        locations=locations,
        errors={},
        form_data={}
    )


@app.route("/edit-record/<int:record_id>", methods=["GET", "POST"])
def edit_record_view(record_id):
    """Renders the edit record form and handles updates."""
    record = database.get_record_by_id(record_id)
    if not record:
        flash("Record not found.", "warning")
        return redirect(url_for("records_view"))

    locations = database.get_distinct_locations()

    if request.method == "POST":
        form_data = request.form.to_dict()
        is_valid, errors = validate_record_data(form_data)

        if not is_valid:
            return render_template(
                "add_record.html",
                active_page="records",
                is_edit=True,
                record_id=record_id,
                locations=locations,
                errors=errors,
                form_data=form_data
            )

        try:
            database.update_record(record_id, form_data)
            flash(f"Record {record['record_code']} updated successfully!", "success")
            return redirect(url_for("records_view"))
        except Exception as e:
            flash(f"Error updating record: {str(e)}", "danger")
            return render_template(
                "add_record.html",
                active_page="records",
                is_edit=True,
                record_id=record_id,
                locations=locations,
                errors={"general": str(e)},
                form_data=form_data
            )

    return render_template(
        "add_record.html",
        active_page="records",
        is_edit=True,
        record_id=record_id,
        locations=locations,
        errors={},
        form_data=record
    )


@app.route("/analytics")
def analytics_view():
    """Renders advanced epidemiological correlations and community insights."""
    summary = database.get_dashboard_summary()
    locations = database.get_distinct_locations()
    return render_template(
        "analytics.html",
        active_page="analytics",
        summary=summary,
        locations=locations
    )


@app.route("/reports")
def reports_view():
    """Renders public health assessment reports and export portal."""
    summary = database.get_dashboard_summary()
    charts_data = database.get_charts_data()
    locations = database.get_distinct_locations()
    now_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")

    return render_template(
        "reports.html",
        active_page="reports",
        summary=summary,
        charts_data=charts_data,
        locations=locations,
        generated_date=now_str
    )


@app.route("/about")
def about_view():
    """Renders the project documentation, methodology, and student review guide."""
    return render_template("about.html", active_page="about")


# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------

@app.route("/api/dashboard/stats")
def api_dashboard_stats():
    """API endpoint providing live summary KPIs."""
    summary = database.get_dashboard_summary()
    return jsonify(summary)


@app.route("/api/charts/data")
def api_charts_data():
    """API endpoint providing dataset structured for Chart.js."""
    location = request.args.get("location", "").strip()
    data = database.get_charts_data(location=location)
    return jsonify(data)


@app.route("/api/records")
def api_get_records():
    """API endpoint providing filterable, searchable, sortable paginated records."""
    search = request.args.get("search", "").strip()
    location = request.args.get("location", "").strip()
    gender = request.args.get("gender", "").strip()
    diabetes = request.args.get("diabetes", "").strip()
    hypertension = request.args.get("hypertension", "").strip()
    bmi_cat = request.args.get("bmi_cat", "").strip()
    risk = request.args.get("risk", "").strip()
    sort_by = request.args.get("sort_by", "id").strip()
    sort_order = request.args.get("sort_order", "desc").strip()

    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(100, max(5, int(request.args.get("per_page", 15))))
    except ValueError:
        page = 1
        per_page = 15

    result = database.get_records(
        search=search,
        location=location,
        gender=gender,
        diabetes=diabetes,
        hypertension=hypertension,
        bmi_cat=bmi_cat,
        risk=risk,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )

    return jsonify(result)


@app.route("/api/records/<int:record_id>", methods=["GET"])
def api_get_single_record(record_id):
    """Returns details for a single record."""
    record = database.get_record_by_id(record_id)
    if not record:
        return jsonify({"success": False, "error": "Record not found"}), 404
    return jsonify({"success": True, "record": record})


@app.route("/api/records", methods=["POST"])
def api_create_record():
    """Creates a new record via AJAX JSON."""
    data = request.get_json(silent=True) or request.form.to_dict()
    is_valid, errors = validate_record_data(data)

    if not is_valid:
        return jsonify({"success": False, "errors": errors}), 400

    try:
        new_id = database.add_record(data)
        record = database.get_record_by_id(new_id)
        return jsonify({
            "success": True,
            "message": "Health record created successfully!",
            "record": record
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/records/<int:record_id>", methods=["PUT", "POST"])
def api_update_record(record_id):
    """Updates an existing record via AJAX."""
    record = database.get_record_by_id(record_id)
    if not record:
        return jsonify({"success": False, "error": "Record not found"}), 404

    data = request.get_json(silent=True) or request.form.to_dict()
    is_valid, errors = validate_record_data(data)

    if not is_valid:
        return jsonify({"success": False, "errors": errors}), 400

    try:
        database.update_record(record_id, data)
        updated_record = database.get_record_by_id(record_id)
        return jsonify({
            "success": True,
            "message": f"Record {record['record_code']} updated successfully!",
            "record": updated_record
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def api_delete_record(record_id):
    """Deletes a record by ID."""
    record = database.get_record_by_id(record_id)
    if not record:
        return jsonify({"success": False, "error": "Record not found"}), 404

    success = database.delete_record(record_id)
    if success:
        return jsonify({
            "success": True,
            "message": f"Record {record['record_code']} was successfully deleted."
        })
    return jsonify({"success": False, "error": "Failed to delete record"}), 500


@app.route("/api/calculate-metrics", methods=["POST"])
def api_calculate_metrics():
    """Live metric calculation endpoint for real-time form feedback."""
    data = request.get_json(silent=True) or request.form.to_dict()

    try:
        height_cm = float(data.get("height_cm", 0))
        weight_kg = float(data.get("weight_kg", 0))
        systolic_bp = int(data.get("systolic_bp", 0))
        diastolic_bp = int(data.get("diastolic_bp", 0))
        blood_glucose = float(data.get("blood_glucose", 0))
        age = int(data.get("age", 30))
        diabetes = data.get("diabetes", "No")
        hypertension = data.get("hypertension", "No")
        smoking = data.get("smoking_status", "Never")
        activity = data.get("physical_activity", "Moderate")

        metrics = database.calculate_health_metrics(
            height_cm, weight_kg, systolic_bp, diastolic_bp, blood_glucose
        )
        risk = database.calculate_risk_level(
            age, metrics["bmi_category"], metrics["bp_category"],
            metrics["glucose_status"], diabetes, hypertension,
            smoking, activity
        )

        return jsonify({
            "success": True,
            "metrics": metrics,
            "risk_score": risk
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/reset-sample-data", methods=["POST"])
def api_reset_sample_data():
    """Resets the dataset to fresh realistic sample data."""
    try:
        count = database.seed_sample_data(force=True)
        return jsonify({
            "success": True,
            "message": f"Sample dataset re-initialized with {count} records."
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# -------------------------------------------------------------
# Data Export Endpoints (CSV & JSON)
# -------------------------------------------------------------

@app.route("/export/csv")
def export_csv():
    """Streams a complete CSV download of health records."""
    location = request.args.get("location", "")
    gender = request.args.get("gender", "")
    diabetes = request.args.get("diabetes", "")
    hypertension = request.args.get("hypertension", "")

    records = database.get_all_records_for_export(
        location=location, gender=gender,
        diabetes=diabetes, hypertension=hypertension
    )

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    headers = [
        "Record ID", "Age", "Gender", "Location", "Height (cm)", "Weight (kg)",
        "BMI", "BMI Category", "Systolic BP", "Diastolic BP", "BP Category",
        "Blood Glucose (mg/dL)", "Glucose Status", "Diabetes", "Hypertension",
        "Smoking Status", "Physical Activity", "Alcohol Intake", "General Health",
        "Healthcare Access", "Risk Tier", "Notes", "Date Created"
    ]
    writer.writerow(headers)

    for r in records:
        writer.writerow([
            r["record_code"], r["age"], r["gender"], r["location"],
            r["height_cm"], r["weight_kg"], r["bmi"], r["bmi_category"],
            r["systolic_bp"], r["diastolic_bp"], r["bp_category"],
            r["blood_glucose"], r["glucose_status"], r["diabetes"], r["hypertension"],
            r["smoking_status"], r["physical_activity"], r["alcohol_intake"],
            r["general_health"], r["healthcare_access"], r["risk_score"],
            r["notes"], r["created_at"]
        ])

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"community_health_records_{timestamp}.csv"

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


@app.route("/export/json")
def export_json():
    """Streams a formatted JSON export of health records."""
    location = request.args.get("location", "")
    gender = request.args.get("gender", "")
    diabetes = request.args.get("diabetes", "")
    hypertension = request.args.get("hypertension", "")

    records = database.get_all_records_for_export(
        location=location, gender=gender,
        diabetes=diabetes, hypertension=hypertension
    )

    export_payload = {
        "dataset_name": "Community Health Data Collection & Analysis",
        "exported_at": datetime.now().isoformat(),
        "record_count": len(records),
        "records": records
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"community_health_records_{timestamp}.json"

    response = make_response(json.dumps(export_payload, indent=2))
    response.headers["Content-Type"] = "application/json"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


if __name__ == "__main__":
    print("=" * 65)
    print("  COMMUNITY HEALTH DATA COLLECTION & ANALYSIS SYSTEM")
    print("  Server starting at: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(debug=True, host="127.0.0.1", port=5000)
