"""
LabPulse AI — College Edition V7
Automated Verification Test Suite
"""
import unittest
from fastapi.testclient import TestClient

from backend.main import app
import backend.database as db

client = TestClient(app)

class TestLabPulseV7(unittest.TestCase):
    def test_01_health_and_routes(self):
        """Test API Documentation and Root OpenAPI availability"""
        response = client.get("/openapi.json")
        self.assertEqual(response.status_code, 200, "OpenAPI schema must be valid and 200 OK")
        data = response.json()
        self.assertIn("paths", data)
        self.assertIn("/api/dashboard", data["paths"])
        self.assertIn("/api/live-utilization", data["paths"])
        self.assertIn("/api/conflicts", data["paths"])
        self.assertIn("/api/audit-logs", data["paths"])
        print("[PASS] Test 01 Passed: OpenAPI Schema and Core V7 Routes Verified")

    def test_02_authentication_roles(self):
        """Test Role-Based Authentication (Admin, HOD, Faculty, Student Viewer)"""
        # Admin
        res_admin = client.post("/api/login", json={"login_id": "admin", "password": "admin"})
        self.assertEqual(res_admin.status_code, 200)
        self.assertEqual(res_admin.json()["role"], "Admin")

        # HOD
        res_hod = client.post("/api/login", json={"login_id": "aiml", "password": "hod"})
        self.assertEqual(res_hod.status_code, 200)
        self.assertEqual(res_hod.json()["role"], "HOD")

        # Faculty
        res_fac = client.post("/api/login", json={"login_id": "cse", "password": "faculty"})
        self.assertEqual(res_fac.status_code, 200)
        self.assertEqual(res_fac.json()["role"], "Faculty")

        # Student Viewer
        res_stu = client.post("/api/login", json={"login_id": "student", "password": "student"})
        self.assertEqual(res_stu.status_code, 200)
        self.assertEqual(res_stu.json()["role"], "Student Viewer")

        print("[PASS] Test 02 Passed: Role-Based Authentication (Admin, HOD, Faculty, Student Viewer) Verified")

    def test_03_dashboard_kpis_and_v7_sections(self):
        """Test Section 6 Dashboard: 6 KPIs, Live Lab Utilization (6.5), Upcoming Conflicts (6.6)"""
        response = client.get("/api/dashboard")
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Part 6.1: 6 KPIs
        self.assertIn("total_laboratories", data)
        self.assertIn("available_labs", data)
        self.assertIn("occupied_labs", data)
        self.assertIn("pending_requests", data)
        self.assertIn("active_conflicts", data)
        self.assertIn("utilization_rate", data)

        # Part 6.5: Live Lab Utilization
        self.assertIn("live_utilization", data)
        self.assertIsInstance(data["live_utilization"], list)

        # Part 6.6: Upcoming Conflicts
        self.assertIn("upcoming_conflicts", data)
        self.assertIsInstance(data["upcoming_conflicts"], list)

        # Part 6.4: Recent Activity
        self.assertIn("recent_activity", data)
        print("[PASS] Test 03 Passed: Dashboard 6 KPIs, Section 6.5 Live Utilization, and Section 6.6 Upcoming Conflicts Verified")

    def test_04_conflict_detection_endpoint(self):
        """Test Section 6.6 Upcoming Resource Conflicts detection logic"""
        res = client.get("/api/conflicts")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("conflicts", data)
        self.assertIn("total_conflicts", data)
        print(f"[PASS] Test 04 Passed: Conflicts endpoint returned {data['total_conflicts']} detected conflicts")

    def test_05_live_utilization_endpoint(self):
        """Test Section 6.5 Live Lab Utilization endpoint"""
        res = client.get("/api/live-utilization")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("utilization", data)
        self.assertIn("records", data)
        self.assertIn("summary", data)
        print(f"[PASS] Test 05 Passed: Live utilization returned {len(data['records'])} monitored resources")

    def test_06_laboratory_registration_and_verification(self):
        """Test Laboratory Management: Registration, Listing, and Verification Audit"""
        login_res = client.post("/api/login", json={"login_id": "admin", "password": "admin"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        import time
        test_lab_id = f"V7-TEST-SUITE-{int(time.time()) % 100000}"

        # Register Lab
        payload = {
            "lab_id": test_lab_id,
            "lab_name": "AI Capstone Project Laboratory",
            "location": "Academic Block 4, Floor 2",
            "lab_type": "AI/ML LAB",
            "department": "AIML",
            "capacity": 60,
            "equipment": "60 High-End Workstations"
        }
        reg_res = client.post("/api/laboratories", json=payload, headers=headers)
        self.assertIn(reg_res.status_code, [200, 201])
        reg_data = reg_res.json()
        self.assertEqual(reg_data["active"], 0, "New registered lab must be inactive pending verification")

        # Admin View
        admin_labs_res = client.get("/api/admin/laboratories", headers=headers)
        self.assertEqual(admin_labs_res.status_code, 200)
        lab_ids = [l["lab_id"] for l in admin_labs_res.json()]
        self.assertIn(test_lab_id, lab_ids)

        # Verify Lab
        verify_payload = {
            "verified_by": "Administrator Dr. Reviewer",
            "notes": "Physical audit passed. 60 workstations verified."
        }
        verify_res = client.patch(f"/api/admin/laboratories/{test_lab_id}/verify", json=verify_payload, headers=headers)
        self.assertEqual(verify_res.status_code, 200)
        verified_data = verify_res.json()
        self.assertEqual(verified_data["active"], 1)

        # Active public laboratories list should now include the verified lab
        public_labs = client.get("/api/laboratories").json()
        public_ids = [l["lab_id"] for l in public_labs]
        self.assertIn(test_lab_id, public_ids)

        print("[PASS] Test 06 Passed: Laboratory Registration, Verification Audit, and Activation Workflow Verified")

    def test_07_recommendation_algorithm_and_constraints(self):
        """Test Part 8 Recommendation Algorithm: Hard Constraints & Weighted Suitability Score"""
        req_payload = {
            "request_date": "2026-10-20",
            "time_slot": "10:30 AM - 01:00 PM",
            "department": "Artificial Intelligence & Machine Learning",
            "academic_year": "IV Year",
            "section": "A",
            "students": 45,
            "purpose": "Deep Learning Practicals",
            "preferred_lab_type": "AI / ML"
        }
        rec_res = client.post("/api/requests", json=req_payload)
        self.assertEqual(rec_res.status_code, 200)
        req_data = rec_res.json()
        self.assertIn("recommended_lab", req_data)
        self.assertIsNotNone(req_data["recommended_lab"])
        self.assertIsNotNone(req_data["recommendation_score"])
        self.assertGreaterEqual(req_data["recommendation_score"], 0.0)
        self.assertLessEqual(req_data["recommendation_score"], 100.0)
        print(f"[PASS] Test 07 Passed: Recommendation Engine matched '{req_data['recommended_lab']}' with suitability score {req_data['recommendation_score']}")

    def test_08_request_status_lifecycle_and_audit(self):
        """Test Resource Request status transition (Pending -> Approved) and Audit Logging"""
        login_res = client.post("/api/login", json={"login_id": "aiml", "password": "hod"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get latest request
        requests_list = client.get("/api/requests").json()
        self.assertTrue(len(requests_list) > 0)
        latest_req = requests_list[0]
        req_id = latest_req["id"]

        # Approve request
        patch_res = client.patch(f"/api/requests/{req_id}?status=Approved", headers=headers)
        self.assertEqual(patch_res.status_code, 200)
        updated_req = patch_res.json()
        self.assertEqual(updated_req["status"], "Approved")

        # Check Audit Log
        audit_res = client.get("/api/audit-logs")
        self.assertEqual(audit_res.status_code, 200)
        audit_logs = audit_res.json()
        self.assertTrue(len(audit_logs) > 0)
        print("[PASS] Test 08 Passed: Request Approval Lifecycle & System Audit Logging Verified")

    def test_09_faculty_usage_override(self):
        """Test Section 7.7 Faculty Usage recording & Timetable real-time synchronization"""
        usage_payload = {
            "lab_id": "V7-TEST-SUITE-01",
            "lab_name": "AI Capstone Project Laboratory",
            "usage_date": "2026-10-25",
            "time_slot": "02:00 PM - 04:30 PM",
            "department": "Artificial Intelligence & Machine Learning",
            "academic_year": "IV Year",
            "section": "A",
            "status": "BUSY",
            "faculty": "Prof. AI Tester"
        }
        res = client.post("/api/faculty-usage", json=usage_payload)
        self.assertEqual(res.status_code, 200)

        # Check usage retrieval
        usage_list = client.get("/api/faculty-usage?selected_date=2026-10-25").json()
        matching = [u for u in usage_list if u["lab_id"] == "V7-TEST-SUITE-01" and u["status"] == "BUSY"]
        self.assertTrue(len(matching) > 0)

        # Check availability reflects BUSY
        avail_res = client.get("/api/lab-availability?selected_date=2026-10-25&time_slot=02:00%20PM%20-%2004:30%20PM").json()
        test_lab_avail = next((l for l in avail_res.get("labs", []) if l["lab_id"] == "V7-TEST-SUITE-01"), None)
        if test_lab_avail:
            self.assertEqual(test_lab_avail["status"], "Busy (Faculty)")

        print("[PASS] Test 09 Passed: Faculty Usage Real-time Matrix Override Verified")

    def test_10_analytics_and_metadata(self):
        """Test Analytics endpoint and Academic Metadata (years, departments, settings)"""
        analytics_res = client.get("/api/analytics?selected_date=2026-10-25")
        self.assertEqual(analytics_res.status_code, 200)
        adata = analytics_res.json()
        self.assertIn("total_laboratories", adata)
        self.assertIn("by_lab", adata)
        self.assertIn("by_department", adata)

        years_res = client.get("/api/years")
        self.assertEqual(years_res.status_code, 200)
        self.assertIn("years", years_res.json())

        dept_res = client.get("/api/departments")
        self.assertEqual(dept_res.status_code, 200)
        self.assertIsInstance(dept_res.json(), list)

        print("[PASS] Test 10 Passed: Analytics, Department Breakdown, and Academic Metadata Verified")

if __name__ == "__main__":
    unittest.main()
