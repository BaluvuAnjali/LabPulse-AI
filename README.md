# LabPulse AI — College Edition V7
## Academic Laboratory Resource Intelligence System
**Final-Year B.Tech Artificial Intelligence and Machine Learning Project**

LabPulse AI is a full-stack, data-driven academic laboratory intelligence platform. It bridges the gap between static curriculum timetables and physical laboratory availability by integrating semester schedules, equipment capacity, actual faculty usage confirmations, temporary event reservations, and constraint-based laboratory recommendation algorithms.

---

## 1. System Architecture & Tech Stack

| Component | Technology | Role |
|---|---|---|
| **Frontend UI** | React 19, Vite 8 | Responsive Single-Page Application |
| **Design System** | Custom Vanilla CSS | Teal-Green (`#176B5B`, `#10483E`) & Warm Biscuit (`#E7D3B0`, `#F6EFE3`) tokens |
| **Backend API** | Python 3.12, FastAPI, Uvicorn | High-performance asynchronous RESTful API |
| **Database** | SQLite3 | Local relational database with foreign keys & transactions |
| **Data Ingestion** | pandas, openpyxl | Multi-sheet Excel (.xlsx, .xls) and CSV timetable parser |
| **Recommendation Engine** | Transparent Multi-Factor Scorer | Hard constraint pruning + weighted suitability ranking |
| **Audit & Governance** | SQLite Audit Trail | Chronological event logs with actors, actions, and timestamps |

---

## 2. Directory Structure

```text
Academic-Lab-Intelligence-ML_Copy/
├── backend/
│   ├── main.py                     # FastAPI backend application & API routes
│   ├── database.py                 # SQLite database schema, connections & audit helpers
│   ├── excel_processor.py          # Timetable Excel/CSV file parser & validator
│   ├── academic_lab.db             # Primary SQLite database (3,564 sessions, 94 venues)
│   └── requirements.txt            # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Main application coordinator & view router
│   │   ├── App.css                 # V7 Design System styles & responsive breakpoints
│   │   ├── main.jsx                # React root mount
│   │   └── index.css               # Global baseline stylesheet
│   ├── index.html                  # HTML entry point with metadata
│   ├── package.json                # Frontend package configuration
│   └── vite.config.js              # Vite server & API proxy configuration
├── backup_before_v7/               # Timestamped SQLite database & code backups
├── test_v7_suite.py                # Automated backend verification test suite (10 tests)
├── backup_db.py                    # Non-destructive SQLite backup utility
├── .env.example                    # Environment variable configuration template
└── README.md                       # Complete documentation & startup guide
```

---

## 3. Quick Startup Instructions

### Prerequisites
- Python 3.10 or higher
- Node.js 18 or higher & npm

### Terminal 1: Backend (FastAPI)
From the project root folder:

```powershell
# 1. (Optional) Activate your existing virtual environment if present:
# .\.venv\Scripts\Activate.ps1

# 2. Install backend dependencies:
pip install -r backend/requirements.txt

# 3. Start FastAPI server on port 8000:
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- API Documentation (Swagger UI): `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/health`

### Terminal 2: Frontend (Vite)
Open a second terminal window in the `frontend` folder:

```powershell
cd frontend
npm install
npm run dev
```
Open your browser to the local URL displayed by Vite, typically:
`http://localhost:5173/`

---

## 4. Role-Based Demo Credentials

For college presentations, demo authentication provides four distinct perspectives:

| Role | User ID | Password | Responsibilities |
|---|---|---|---|
| **Administrator** | `admin` | `admin` | Full control: Laboratory management, timetable upload, verification audits |
| **Department HOD** | `aiml` (or dept code) | `hod` | Request approvals, departmental analytics, notification routing |
| **Faculty Member** | `cse` (or dept code) | `faculty` | Resource search, lab requests, actual usage checklist overrides |
| **Student Viewer** | `student` | `student` | Read-only matrix: Timetable view, lab availability finder, analytics |

*Available department codes:* `aiml`, `cse`, `ece`, `eee`, `mech`, `civil`, `it`.

---

## 5. Core Feature Modules

1. **Dashboard (Command Center)**:
   - **Part 6.1 — 6 Core KPIs**: Total Laboratories, Available Today, Occupied/Reserved, Pending Requests, Scheduling Conflicts, and Recorded Utilization Percentage.
   - **Part 6.5 — Live Lab Utilization**: Real-time table displaying laboratory identifiers, recorded status, session block, capacity, confirmed occupancy, utilization percentage, and data source.
   - **Part 6.6 — Upcoming Resource Conflicts**: Automatically scans and lists timetable overlaps, unverified venue assignments, and faculty schedule clashes with severity levels and resolution actions.
   - **Part 6.4 — Traceable Activity Feed**: Chronological log of recent institutional operations.

2. **Laboratory Management**:
   - Inventory list of registered physical facilities.
   - Registration form with mandatory validation (Lab ID, name, location, department, capacity, equipment).
   - Multi-step administrator verification workflow (new labs remain inactive until verified by an Admin).

3. **Timetable Schedule Matrix**:
   - Interactive schedule matrix filtering by academic year, department, and date.
   - Clearly distinguishes Planned sessions, Faculty Busy (Red), Reserved sessions, and Campus Lunch Break (1:00 PM – 2:00 PM).

4. **Lab Availability Search**:
   - Filter by date, 3-hour session block, minimum seat capacity, and laboratory type.
   - Real-time conflict exclusion and timetable venue assignment details.

5. **Lab Usage Confirmation (Faculty Checklist)**:
   - Faculty can mark a laboratory `BUSY` or `FREE` for a specific session.
   - Acts as an operational override: changes the timetable cell to Red immediately and excludes the laboratory from recommendation candidate pools.

6. **Resource Requests & Recommendation Engine**:
   - Submit student capacity requirements and session blocks.
   - **Hard Constraint Pruning**: Prunes facilities that are occupied by faculty, reserved by prior requests, scheduled for workshops, or lack sufficient capacity (`capacity < students`).
   - **Weighted Scoring**: Evaluates equipment match (35%), capacity fit (25%), department suitability (20%), and historical utilization (20%).
   - Administrator/HOD one-click Approval/Rejection workflow.

7. **Analytics & Utilization**:
   - Date-based operational analytics.
   - Timetable session volume breakdown by laboratory and department distribution.
   - Distinguishes scheduled timetable allocations from confirmed actual usage.

8. **Workshops & Academic Activities**:
   - Schedule technical seminars, workshops, or maintenance blocks.
   - Automatically reserves overlapping laboratories and updates live availability.

9. **Timetable Master Data Ingestion**:
   - Isolated upload point for official semester Excel (.xlsx, .xls) and CSV schedules.
   - Row-level validation and safe replacement of master schedules while preserving operational faculty records.

10. **Settings & Governance**:
    - Application summary, technical specifications, and HOD notification testing.

---

## 6. Automated Testing

The project includes an automated test suite verifying all critical functional flows:

```powershell
python test_v7_suite.py
```

### Verified Test Cases:
- `test_01_health_and_routes`: OpenAPI Schema and Core V7 Routes
- `test_02_authentication_roles`: Role-Based Authentication (Admin, HOD, Faculty, Student Viewer)
- `test_03_dashboard_kpis_and_v7_sections`: 6 KPIs, Section 6.5 Live Utilization, and Section 6.6 Conflicts
- `test_04_conflict_detection_endpoint`: Automated conflict detection logic
- `test_05_live_utilization_endpoint`: Live utilization metrics
- `test_06_laboratory_registration_and_verification`: Registration, audit, and activation workflow
- `test_07_recommendation_algorithm_and_constraints`: Hard constraints & weighted suitability scoring
- `test_08_request_status_lifecycle_and_audit`: Request approval lifecycle and audit logging
- `test_09_faculty_usage_override`: Real-time faculty usage matrix override
- `test_10_analytics_and_metadata`: Analytics aggregation and academic department metadata

### Frontend Production Build Check:
```powershell
cd frontend
npm run build
```
*(Verified: compiles in under 300ms with zero errors).*

---

## 7. Troubleshooting & Common Fixes

### "Failed to fetch" on Login
- **Cause**: Origin mismatch or backend not running on port 8000.
- **Solution**:
  1. Ensure FastAPI is running on `http://127.0.0.1:8000`.
  2. CORS in `backend/main.py` is configured with `allow_origin_regex` to support both `localhost` and `127.0.0.1` on any port.
  3. `frontend/vite.config.js` includes an automatic proxy for `/api` to `http://127.0.0.1:8000`.
  4. The frontend API client automatically matches the current browser hostname.

### Database Safety & Restore
A safe SQLite backup is located at:
`backup_before_v7/academic_lab_backup_20261017_120853.db`
To restore the verified baseline, simply copy the backup file over `backend/academic_lab.db`.

---

## 8. Limitations & Future Scope
- **IoT Hardware Integration**: Live occupancy currently relies on confirmed faculty operational checklists; future versions could integrate RFID badge readers or passive infrared (PIR) occupancy sensors.
- **Forecasting ML Models**: A scikit-learn random forest regressor pipeline is supported in the schema; active inference can be enabled once an institution records 3+ consecutive semesters of confirmed usage history.
- **Production Authentication**: For academic demonstration, role-based demo credentials are used. For institutional production deployment, integration with SAML 2.0 or LDAP/Active Directory is recommended.


## V7 update — timetable filters, evidence-based status, and visual theme

- The timetable page now defaults to **All Departments** and supports department/year filters. The selected filters are sent to both timetable and venue-assignment APIs so only matching academic assignments appear.
- Each scheduled lab cell displays the subject plus branch, academic year, and section.
- Removed the UI fallback that labelled every empty cell “Available”. Empty cells now show **Availability Unverified** unless the backend has a recorded availability status.
- Venue mappings marked `REVIEW_REQUIRED` are displayed as scheduled but needing venue verification; a planned timetable entry is not treated as proof of live physical-lab occupancy.
- The date selector uses the selected date’s weekday to display the recurring timetable. Historical actual occupancy cannot be inferred from the weekly timetable alone; it requires saved usage records.
- Updated the interface styling to a teal-green and biscuit/cream palette with softer cards, readable contrast, and simpler status labels.

### Important data limitation
The bundled database contains 3,564 timetable rows and 94 venue mappings, but the venue mappings are marked `REVIEW_REQUIRED`. Therefore the app can show the matching planned class/lab session, but it must not claim a physical lab is confirmed available until venue assignments and actual usage are verified. This avoids fabricated “Available” predictions.
