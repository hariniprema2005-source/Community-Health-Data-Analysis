"""
Comprehensive Automated Test Suite for Community Health Web Application
Validates all page routes, API endpoints, CRUD operations, calculators, and exports.
"""

import unittest
import json
from app import app
import database


class CommunityHealthTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure test client
        app.config["TESTING"] = True
        cls.client = app.test_client()
        # Initialize test database and seed
        database.init_db()
        database.seed_sample_data(force=True)

    def test_01_dashboard_page(self):
        """Test GET / and /dashboard returns 200 with dashboard elements"""
        res1 = self.client.get("/")
        self.assertEqual(res1.status_code, 200)
        self.assertIn(b"Community Health Overview", res1.data)
        self.assertIn(b"Total Sample Size", res1.data)

        res2 = self.client.get("/dashboard")
        self.assertEqual(res2.status_code, 200)

    def test_02_records_page(self):
        """Test GET /records returns 200"""
        res = self.client.get("/records")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Community Health Records", res.data)
        self.assertIn(b"records-table-body", res.data)

    def test_03_add_record_page(self):
        """Test GET /add-record returns 200 with input form"""
        res = self.client.get("/add-record")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Participant Health Screening Form", res.data)
        self.assertIn(b"Live Health Classifier", res.data)

    def test_04_analytics_page(self):
        """Test GET /analytics returns 200"""
        res = self.client.get("/analytics")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Epidemiological Insights & Analytics", res.data)

    def test_05_reports_page(self):
        """Test GET /reports returns 200 with printable paper"""
        res = self.client.get("/reports")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Community Health Status Report", res.data)
        self.assertIn(b"Priority Public Health Interventions", res.data)

    def test_06_about_page(self):
        """Test GET /about returns 200 with project review notes"""
        res = self.client.get("/about")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"About the Project", res.data)
        self.assertIn(b"College Project Review / Viva Q&A Guide", res.data)

    def test_07_api_dashboard_stats(self):
        """Test GET /api/dashboard/stats returns correct JSON schema"""
        res = self.client.get("/api/dashboard/stats")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("total_records", data)
        self.assertGreater(data["total_records"], 0)
        self.assertIn("avg_bmi", data)
        self.assertIn("diabetes_cases", data)
        self.assertIn("hypertension_cases", data)

    def test_08_api_charts_data(self):
        """Test GET /api/charts/data returns Chart.js datasets"""
        res = self.client.get("/api/charts/data")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("diabetes", data)
        self.assertIn("hypertension", data)
        self.assertIn("age_groups", data)
        self.assertIn("bmi_categories", data)
        self.assertIn("location_stats", data)

    def test_09_api_records_pagination_and_search(self):
        """Test GET /api/records pagination and search"""
        res = self.client.get("/api/records?page=1&per_page=10")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data["records"]), 10)
        self.assertGreaterEqual(data["total"], 80)
        self.assertIn("total_pages", data)

        # Test search
        res2 = self.client.get("/api/records?search=CHD-1001")
        self.assertEqual(res2.status_code, 200)
        data2 = json.loads(res2.data)
        self.assertGreaterEqual(data2["total"], 1)

    def test_10_crud_operations(self):
        """Test Create, Read, Update, Delete of health record"""
        # 1. Create Record via API
        payload = {
            "record_code": "CHD-9999",
            "age": 48,
            "gender": "Female",
            "location": "North District",
            "height_cm": 165.0,
            "weight_kg": 72.5,
            "systolic_bp": 136,
            "diastolic_bp": 88,
            "blood_glucose": 110.0,
            "diabetes": "Pre-diabetic",
            "hypertension": "Yes",
            "smoking_status": "Never",
            "physical_activity": "Moderate",
            "alcohol_intake": "None",
            "general_health": "Good",
            "healthcare_access": "Yes",
            "notes": "Automated test screening participant"
        }
        create_res = self.client.post(
            "/api/records",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(create_res.status_code, 201)
        create_data = json.loads(create_res.data)
        self.assertTrue(create_data["success"])
        new_record = create_data["record"]
        record_id = new_record["id"]
        self.assertEqual(new_record["record_code"], "CHD-9999")
        self.assertEqual(new_record["bmi_category"], "Overweight")
        self.assertEqual(new_record["bp_category"], "Hypertension Stage 1")

        # 2. Read Single Record
        get_res = self.client.get(f"/api/records/{record_id}")
        self.assertEqual(get_res.status_code, 200)
        get_data = json.loads(get_res.data)
        self.assertEqual(get_data["record"]["age"], 48)

        # 3. Update Record
        update_payload = {
            "age": 49,
            "gender": "Female",
            "location": "North District",
            "height_cm": 165.0,
            "weight_kg": 62.0,
            "systolic_bp": 122,
            "diastolic_bp": 78,
            "blood_glucose": 95.0,
            "diabetes": "No",
            "hypertension": "No",
            "smoking_status": "Never",
            "physical_activity": "Active",
            "alcohol_intake": "None",
            "general_health": "Excellent",
            "healthcare_access": "Yes",
            "notes": "Follow-up update - weight reduced and vitals normalized"
        }
        put_res = self.client.put(
            f"/api/records/{record_id}",
            data=json.dumps(update_payload),
            content_type="application/json"
        )
        self.assertEqual(put_res.status_code, 200)
        put_data = json.loads(put_res.data)
        self.assertTrue(put_data["success"])
        self.assertEqual(put_data["record"]["bmi_category"], "Normal")
        self.assertEqual(put_data["record"]["bp_category"], "Elevated")

        # 4. Delete Record
        del_res = self.client.delete(f"/api/records/{record_id}")
        self.assertEqual(del_res.status_code, 200)
        del_data = json.loads(del_res.data)
        self.assertTrue(del_data["success"])

        # Verify record no longer exists
        verify_res = self.client.get(f"/api/records/{record_id}")
        self.assertEqual(verify_res.status_code, 404)

    def test_11_live_calculator_endpoint(self):
        """Test POST /api/calculate-metrics live preview"""
        calc_payload = {
            "height_cm": 175.0,
            "weight_kg": 85.0,
            "systolic_bp": 142,
            "diastolic_bp": 92,
            "blood_glucose": 130.0,
            "age": 58,
            "diabetes": "Yes",
            "hypertension": "Yes"
        }
        res = self.client.post(
            "/api/calculate-metrics",
            data=json.dumps(calc_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["metrics"]["bmi_category"], "Overweight")
        self.assertEqual(data["metrics"]["bp_category"], "Hypertension Stage 2")
        self.assertEqual(data["metrics"]["glucose_status"], "Diabetic")
        self.assertEqual(data["risk_score"], "High")

    def test_12_exports(self):
        """Test CSV and JSON exports generate proper responses"""
        # CSV Export
        csv_res = self.client.get("/export/csv")
        self.assertEqual(csv_res.status_code, 200)
        self.assertEqual(csv_res.mimetype, "text/csv")
        self.assertIn(b"Record ID,Age,Gender", csv_res.data)

        # JSON Export
        json_res = self.client.get("/export/json")
        self.assertEqual(json_res.status_code, 200)
        self.assertEqual(json_res.mimetype, "application/json")
        export_data = json.loads(json_res.data)
        self.assertIn("dataset_name", export_data)
        self.assertGreater(export_data["record_count"], 0)

    def test_13_validation_errors(self):
        """Test server-side rejection of invalid clinical inputs"""
        bad_payload = {
            "record_code": "CHD-BAD",
            "age": 150,  # Invalid age > 120
            "gender": "InvalidGender",
            "location": "",
            "height_cm": 300,
            "weight_kg": 500,
            "systolic_bp": 110,
            "diastolic_bp": 130,  # diastolic > systolic error!
            "blood_glucose": 750
        }
        res = self.client.post(
            "/api/records",
            data=json.dumps(bad_payload),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertFalse(data["success"])
        self.assertIn("age", data["errors"])
        self.assertIn("gender", data["errors"])
        self.assertIn("location", data["errors"])
        self.assertIn("diastolic_bp", data["errors"])


if __name__ == "__main__":
    unittest.main()
