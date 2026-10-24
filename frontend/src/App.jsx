import React, { useEffect, useMemo, useState } from 'react'
import './App.css'


const getApiBase = () => {
  const apiUrl = import.meta.env.VITE_API_BASE_URL

  if (apiUrl) return apiUrl.replace(/\/$/, '')

  if (typeof window !== 'undefined') {
    if (window.location.hostname === 'localhost') {
      return 'http://localhost:8000'
    }

    if (window.location.hostname === '127.0.0.1') {
      return 'http://127.0.0.1:8000'
    }
  }

  return 'http://127.0.0.1:8000'
}



const FACULTY_USAGE_SLOTS = [
  '9:30 AM - 10:30 AM',
  '10:30 AM - 11:20 AM',
  '11:20 AM - 12:10 PM',
  '12:10 PM - 01:00 PM',
  '02:00 PM - 02:50 PM',
  '02:50 PM - 03:40 PM',
  '03:40 PM - 04:30 PM',
]


const DEFAULT_SLOTS = [
  '9:30 AM - 10:30 AM',
  '10:30 AM - 11:20 AM',
  '11:20 AM - 12:10 PM',
  '12:10 PM - 01:00 PM',
  '02:00 PM - 02:50 PM',
  '02:50 PM - 03:40 PM',
  '03:40 PM - 04:30 PM',
]
const FALLBACK_YEARS = ['I Year', 'II Year', 'III Year', 'IV Year']

const DEPARTMENTS = [
  { name: 'Artificial Intelligence & Machine Learning', code: 'AIML', hod: 'Dr. G. Loshma', email: 'anjalibaluvu5555@gmail.com' },
  { name: 'Computer Science & Engineering', code: 'CSE', hod: 'Dr. D. Jaya Kumari', email: '' },
  { name: 'Electronics & Communication Engineering', code: 'ECE', hod: 'Dr. E. Kusuma Kumari', email: '' },
  { name: 'Electrical & Electronics Engineering', code: 'EEE', hod: 'D. Sudha Rani', email: '' },
  { name: 'Mechanical Engineering', code: 'MECH', hod: 'Dr. M. V. Ramesh', email: '' },
  { name: 'Civil Engineering', code: 'CIVIL', hod: 'Mr. D. Naveen Kumar', email: '' },
  { name: 'Information Technology', code: 'IT', hod: 'IT HOD', email: 'anjalibaluvu5555@gmail.com' },
]

const NAV = [
  ['dashboard', '⌂', 'Dashboard'],
  ['timetable', '▤', 'Timetable View'],
  ['availability', '◫', 'Lab Availability'],
  ['usage', '✓', 'Lab Usage (Faculty)'],
  ['requests', '◇', 'Lab Requests'],
  ['analytics', '◒', 'Analytics'],
  ['activities', '◈', 'Workshops / Activities'],
  ['upload', '⇧', 'Timetable Upload'],
  ['laboratories', '▣', 'Laboratory Management'],
  ['settings', '⚙', 'Settings'],
]

async function api(path, options = {}) {
  let session = null

  try {
    session = JSON.parse(
      localStorage.getItem('labpulse_session') || 'null'
    )
  } catch {
    session = null
  }

  const headers = new Headers(options.headers || {})

  if (!headers.has('Content-Type') && options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  if (session?.access_token) {
    headers.set(
      'Authorization',
      `Bearer ${session.access_token}`
    )
  }

  const baseUrl = getApiBase()
  let response

  try {
    response = await fetch(`${baseUrl}${path}`, {
      ...options,
      headers,
    })
  } catch (err) {
    throw new Error(
      `Backend service unreachable at ${baseUrl}. Please ensure FastAPI is running on port 8000.`
    )
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`

    try {
      const data = await response.json()
      message = data.detail || message
    } catch {
      // Ignore non-JSON error responses.
    }

    throw new Error(message)
  }

  return response.json()
}


const today = () => new Date().toISOString().slice(0, 10)

const formatDate = (value) =>
  value
    ? new Date(`${value}T00:00:00`).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
    : '—'

const dayName = (value) =>
  new Date(`${value}T00:00:00`).toLocaleDateString('en-US', {
    weekday: 'long',
  })

const esc = (value) => encodeURIComponent(value || '')

export default function App() {
  const [session, setSession] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('labpulse_session') || 'null')
    } catch {
      return null
    }
  })

  if (!session) {
    return <Login onLogin={setSession} />
  }

  return (
    <MainApp
      session={session}
      onLogout={() => {
        localStorage.removeItem('labpulse_session')
        setSession(null)
      }}
    />
  )
}

function Login({ onLogin }) {
  const [loginId, setLoginId] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (event) => {
    event.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await api('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          login_id: loginId.trim().toLowerCase(),
          password,
        }),
      })

      localStorage.setItem('labpulse_session', JSON.stringify(result))
      onLogin(result)
    } catch (err) {
      setError(err.message || 'Login failed.')
    } finally {
      setLoading(false)
    }
  }

  const quickLogin = (id, pass) => {
    setLoginId(id)
    setPassword(pass)
    setError('')
  }

  
return (
  <main className="lp-auth-screen">
    <section className="lp-auth-art" aria-label="Sri Vasavi Engineering College and faculty" />
    <section className="lp-auth-side">
      <form className="lp-auth-card" onSubmit={submit}>
        <h1>Faculty Login</h1>
        <label className="lp-auth-field">
          <span>Email ID / Login ID</span>
          <input autoFocus value={loginId} onChange={(event) => setLoginId(event.target.value)}
            placeholder="Enter your email or login ID" autoComplete="username" required />
        </label>
        <label className="lp-auth-field">
          <span>Password</span>
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)}
            placeholder="Enter your password" autoComplete="current-password" required />
        </label>
        {error && <div className="lp-auth-error" role="alert">{error}</div>}
        <button className="lp-auth-button" type="submit" disabled={loading || !loginId || !password}>
          {loading ? 'Signing in…' : 'Login  →'}
        </button>
      </form>
    </section>
  </main>
)

}

function MainApp({ session, onLogout }) {
  const [page, setPage] = useState('dashboard')
  const [sidebar, setSidebar] = useState(true)
  const isAdmin = session?.role === 'Admin'
  const isHod = session?.role === 'HOD'
  const [toast, setToast] = useState('')
  const [error, setError] = useState('')
  const [dash, setDash] = useState(null)
  const [labs, setLabs] = useState([])
  const [adminLabs, setAdminLabs] = useState([])
  const [adminLabsError, setAdminLabsError] = useState('')
  const [adminLabsLoading, setAdminLabsLoading] = useState(false)


  const [labForm, setLabForm] = useState({
    lab_id: '',
    lab_name: '',
    location: '',
    lab_type: 'LABORATORY',
    equipment: '',
    department: '',
    capacity: '',
  })
  const [labFormLoading, setLabFormLoading] = useState(false)

  const [requests, setRequests] = useState([])
  const [activities, setActivities] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [meta, setMeta] = useState({
    years: FALLBACK_YEARS,
    departments: DEPARTMENTS.map((d) => d.name),
    slots: DEFAULT_SLOTS,
  })

  const sessionDeptCode = String(session?.department_code || session?.department || '').toUpperCase()
  const sessionDept = DEPARTMENTS.find((d) => [d.code, ...(d.code === 'AIML' ? ['AIM'] : d.code === 'MECH' ? ['ME'] : d.code === 'CIVIL' ? ['CE'] : [])].includes(sessionDeptCode))
  const [selectedDepartment, setSelectedDepartment] = useState(
    session?.role === 'Admin' ? DEPARTMENTS[0].name : (sessionDept?.name || DEPARTMENTS[0].name)
  )

  const [profileImage, setProfileImage] = useState(
    localStorage.getItem('labpulse_hod_image') || ''
  )

  const refresh = async () => {
    try {
      const [dashboard, laboratoryData, requestData, analyticsData, activityData, settings, years, departments] =
        await Promise.all([
          api('/api/dashboard'),
          api('/api/laboratories'),
          api('/api/requests'),
          api('/api/analytics'),
          api('/api/activities'),
          api('/api/settings'),
          api('/api/years'),
          api('/api/departments'),
        ])

      setDash(dashboard)
      setLabs(Array.isArray(laboratoryData) ? laboratoryData : [])
      setRequests(Array.isArray(requestData) ? requestData : [])
      setAnalytics(analyticsData)
      setActivities(Array.isArray(activityData) ? activityData : [])

      setMeta({
        years: years?.years?.length ? years.years : FALLBACK_YEARS,
        departments:
          departments?.map((item) => item.department_name) ||
          DEPARTMENTS.map((item) => item.name),
        slots:
          settings?.time_slots?.length
            ? settings.time_slots
            : DEFAULT_SLOTS,
      })

      setError('')
    } catch (err) {
      setError(err.message || 'Backend is not available.')
    }
  }


  const loadAdminLabs = async () => {
    if (session?.role !== 'Admin') return

    setAdminLabsLoading(true)
    setAdminLabsError('')

    try {
      const data = await api('/api/admin/laboratories')
      setAdminLabs(Array.isArray(data) ? data : [])
    } catch (err) {
      setAdminLabsError(
        err.message || 'Unable to load laboratory inventory.'
      )
    } finally {
      setAdminLabsLoading(false)
    }
  }


  const registerLaboratory = async (event) => {
    event.preventDefault()
    setAdminLabsError('')
    setToast('')
    setLabFormLoading(true)

    try {
      const payload = {
        ...labForm,
        lab_id: labForm.lab_id.trim(),
        lab_name: labForm.lab_name.trim(),
        location: labForm.location.trim(),
        equipment: labForm.equipment.trim(),
        department: labForm.department.trim(),
        capacity:
          labForm.capacity.trim() === ''
            ? null
            : Number(labForm.capacity),
      }

      await api('/api/laboratories', {
        method: 'POST',
        body: JSON.stringify(payload),
      })

      setToast('Laboratory registered as inactive pending verification.')
      setLabForm({
        lab_id: '',
        lab_name: '',
        location: '',
        lab_type: 'LABORATORY',
        equipment: '',
        department: '',
        capacity: '',
      })

      await loadAdminLabs()
    } catch (err) {
      setAdminLabsError(err.message || 'Laboratory registration failed.')
    } finally {
      setLabFormLoading(false)
    }
  }


  useEffect(() => {
    if (page === 'laboratories' && isAdmin) {
      loadAdminLabs()
    }
  }, [page, isAdmin])


  useEffect(() => {
    refresh()
  }, [])

  useEffect(() => {
    if (!toast) return undefined
    const timer = setTimeout(() => setToast(''), 3500)
    return () => clearTimeout(timer)
  }, [toast])

  const hod =
    DEPARTMENTS.find((department) => department.name === selectedDepartment) ||
    DEPARTMENTS.find((department) => department.code === String(session?.department_code || session?.department || '').toUpperCase()) ||
    DEPARTMENTS[0]

  const pageLabel =
    NAV.find((item) => item[0] === page)?.[2] || 'Dashboard'

  const onImage = (event) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = () => {
      setProfileImage(reader.result)
      localStorage.setItem('labpulse_hod_image', reader.result)
    }
    reader.readAsDataURL(file)
  }



  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebar ? '' : 'collapsed'}`}>
        <div className="brand-block">
          <div className="brand-logo">LP</div>
          {sidebar && (
            <div>
              <strong>LabPulse AI</strong>
              <small>Academic Resource Intelligence</small>
            </div>
          )}
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav>

          {NAV.filter(([id]) => {
            if (session?.role === 'Student' || session?.role === 'Student Viewer') {
              return ['dashboard', 'timetable', 'availability', 'analytics'].includes(id)
            }
            if (id === 'laboratories') return isAdmin
            if (isHod || isAdmin) return true
            return !['upload', 'settings', 'analytics'].includes(id)
          }).map(([id, icon, label]) => (

            <button
              key={id}
              className={`nav-item ${page === id ? 'active' : ''}`}
              onClick={() => setPage(id)}
              title={label}
            >
              <span>{icon}</span>
              {sidebar && label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          {sidebar && (
            <>
              <span className="live-dot" /> Live resource engine
            </>
          )}
        </div>
      </aside>

      <main className="main-shell">
        <header className="topbar">
          <button
            className="menu-btn"
            onClick={() => setSidebar((value) => !value)}
          >
            ☰
          </button>

          <div className="header-title">
            <strong>{pageLabel}</strong>
            <span>Academic Laboratory Resource Intelligence</span>
          </div>

          <div className="profile-controls">
            <label className="department-select">
              <span>Department</span>
              <select
                value={selectedDepartment}
                disabled={!isAdmin}
                onChange={(event) =>
                  setSelectedDepartment(event.target.value)
                }
              >
                {DEPARTMENTS.map((department) => (
                  <option key={department.code} value={department.name}>
                    {department.code} — {department.name}
                  </option>
                ))}
              </select>
            </label>

            <label
              className="profile-upload"
              title="Choose profile image from device"
            >
              {profileImage ? (
                <img src={profileImage} alt="Profile" />
              ) : (
                <span>H</span>
              )}
              <input
                type="file"
                accept="image/*"
                onChange={onImage}
              />
            </label>

            <div className="profile-text">
              <b>
                {isAdmin
                  ? session.display_name || 'Administrator'
                  : session?.role === 'Faculty'
                    ? `${hod.code} Faculty`
                    : hod.hod}
              </b>
              <small>
                {session?.role} • {hod.code} Department
              </small>
            </div>

            <button
              className="logout-btn"
              onClick={onLogout}
              title="Sign out"
            >
              ↪
            </button>
          </div>
        </header>

        <section className="content-area">
          {error && (
            <div className="error-banner">
              <b>Backend:</b> {error}
              <button className="text-button" onClick={refresh}>
                Retry
              </button>
            </div>
          )}

          {page === 'dashboard' && (
            <Dashboard
              dash={dash}
              requests={requests}
              activities={activities}
              go={setPage}
              session={session}
            />
          )}

          {page === 'timetable' && <Timetable meta={meta} />}

          {page === 'availability' && <Availability meta={meta} />}

          {page === 'usage' && (
            <Usage
              labs={labs}
              meta={meta}
              selectedDepartment={selectedDepartment}
              onSaved={async () => {
                await refresh()
                setToast(
                  'Faculty usage updated — timetable marked in real time.'
                )
              }}
            />
          )}

          {page === 'requests' && (
            <Requests
              requests={requests}
              meta={meta}
              selectedDepartment={selectedDepartment}
              onChanged={async (message) => {
                await refresh()
                setToast(message)
              }}
            />
          )}

          {page === 'analytics' && (
            <Analytics meta={meta} initial={analytics} />
          )}

          {page === 'activities' && (
            <Activities
              labs={labs}
              activities={activities}
              departments={DEPARTMENTS}
              onChanged={async (message) => {
                await refresh()
                setToast(message)
              }}
            />
          )}

          {page === 'upload' && (
            <TimetableUpload
              meta={meta}
              onImported={async () => {
                await refresh()
                setPage('timetable')
                setToast('Semester timetable imported successfully.')
              }}
            />
          )}

          {page === 'settings' && (
            <Settings meta={meta} hod={hod} />
          )}



          {page === 'laboratories' && isAdmin && (
            <div className="panel">
              <div className="section-heading">
                <div>
                  <h2>Laboratory Inventory</h2>
                  <p>Review registered physical laboratories and verification records.</p>
                </div>
                <button
                  className="secondary-btn"
                  onClick={loadAdminLabs}
                  disabled={adminLabsLoading}
                >
                  {adminLabsLoading ? 'Loading...' : 'Refresh Inventory'}
                </button>
              </div>

              {adminLabsError && (
                <div className="error-banner">
                  {adminLabsError}
                </div>
              )}

              <div className="lab-registration-card">
                <div className="lab-registration-heading">
                  <div>
                    <h3>Register a Physical Laboratory</h3>
                    <p>New entries remain inactive until an authorized administrator verifies them.</p>
                  </div>
                  <span className="status-pill pending">Verification required</span>
                </div>

                <form
                  className="lab-registration-form"
                  onSubmit={registerLaboratory}
                >
                  <label>
                    Laboratory ID *
                    <input
                      value={labForm.lab_id}
                      onChange={(e) => setLabForm({ ...labForm, lab_id: e.target.value })}
                      placeholder="e.g. AIML-LAB-01"
                      required
                    />
                  </label>

                  <label>
                    Laboratory name *
                    <input
                      value={labForm.lab_name}
                      onChange={(e) => setLabForm({ ...labForm, lab_name: e.target.value })}
                      placeholder="e.g. AI and ML Laboratory"
                      required
                    />
                  </label>

                  <label>
                    Location
                    <input
                      value={labForm.location}
                      onChange={(e) => setLabForm({ ...labForm, location: e.target.value })}
                      placeholder="Block, floor or room"
                    />
                  </label>

                  <label>
                    Laboratory type
                    <select
                      value={labForm.lab_type}
                      onChange={(e) => setLabForm({ ...labForm, lab_type: e.target.value })}
                    >
                      <option value="LABORATORY">Laboratory</option>
                      <option value="COMPUTER LAB">Computer Lab</option>
                      <option value="AI/ML LAB">AI/ML Lab</option>
                      <option value="ELECTRONICS LAB">Electronics Lab</option>
                      <option value="General">General</option>
                    </select>
                  </label>

                  <label>
                    Department
                    <input
                      value={labForm.department}
                      onChange={(e) => setLabForm({ ...labForm, department: e.target.value })}
                      placeholder="e.g. AIML"
                    />
                  </label>

                  <label>
                    Student capacity
                    <input
                      type="number"
                      min="0"
                      step="1"
                      value={labForm.capacity}
                      onChange={(e) => setLabForm({ ...labForm, capacity: e.target.value })}
                      placeholder="Enter known capacity"
                    />
                  </label>

                  <label className="lab-equipment-field">
                    Equipment and facilities
                    <textarea
                      value={labForm.equipment}
                      onChange={(e) => setLabForm({ ...labForm, equipment: e.target.value })}
                      placeholder="Record verified equipment, if known"
                      rows={3}
                    />
                  </label>

                  <div className="lab-registration-actions">
                    <button
                      type="submit"
                      className="primary-btn"
                      disabled={labFormLoading}
                    >
                      {labFormLoading ? 'Registering...' : 'Register Laboratory'}
                    </button>
                  </div>
                </form>
              </div>
              {adminLabsLoading ? (
                <p>Loading laboratory inventory...</p>
              ) : adminLabs.length === 0 ? (
                <p>No laboratories are registered yet.</p>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Lab ID</th>
                        <th>Laboratory</th>
                        <th>Location</th>
                        <th>Type</th>
                        <th>Capacity</th>
                        <th>Inventory Status</th>
                        <th>Last Verification</th>
                      </tr>
                    </thead>
                    <tbody>
                      {adminLabs.map((lab) => (
                        <tr key={lab.id}>
                          <td>{lab.lab_id}</td>
                          <td>{lab.lab_name}</td>
                          <td>{lab.location || 'Not recorded'}</td>
                          <td>{lab.lab_type || 'General'}</td>
                          <td>
                            {Number(lab.capacity) > 0
                              ? lab.capacity
                              : 'Unknown'}
                          </td>
                          <td>
                            {Number(lab.active) === 1
                              ? 'Active'
                              : 'Inactive'}
                          </td>
                          <td>
                            {lab.last_verified == null
                              ? 'Pending'
                              : Number(lab.last_verified) === 1
                                ? 'Verified'
                                : 'Not verified'}
                            {lab.last_verified_by
                              ? ` — ${lab.last_verified_by}`
                              : ''}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              <div className="soft-note">
                <strong>Safety rule</strong>
                <p>
                  Only activate a laboratory after its physical identity,
                  location and capacity have been confirmed by an authorized
                  administrator. An inactive laboratory cannot be recommended
                  as available.
                </p>
              </div>
            </div>
          )}


        </section>

        {toast && <div className="toast">✓ {toast}</div>}
      </main>
    </div>
  )
}

function PageTitle({ eyebrow, title, sub, actions }) {
  return (
    <div className="page-title">
      <div>
        <div className="eyebrow">{eyebrow || 'LABPULSE AI'}</div>
        <h1>{title}</h1>
        <p>{sub}</p>
      </div>
      <div className="title-actions">{actions}</div>
    </div>
  )
}

function Card({ title, children, action, className = '' }) {
  return (
    <section className={`card ${className}`}>
      <div className="card-head">
        <h3>{title}</h3>
        {action}
      </div>
      {children}
    </section>
  )
}

function Stat({ label, value, sub, tone = 'blue', icon = '◈' }) {
  return (
    <div className={`stat-card ${tone}`}>
      <div>
        <span>{label}</span>
        <strong>{value ?? 0}</strong>
        <small>{sub}</small>
      </div>
      <i>{icon}</i>
    </div>
  )
}

function Badge({ text }) {
  const className = String(text || '')
    .toLowerCase()
    .replace(/[^a-z]+/g, '-')

  return (
    <span className={`badge ${className}`}>
      {text || '—'}
    </span>
  )
}

function Empty({ text }) {
  return (
    <div className="empty-state">
      <div>⌁</div>
      <span>{text}</span>
    </div>
  )
}

function InlineError({ text }) {
  return <div className="inline-error">⚠ {text}</div>
}

function Loading() {
  return (
    <div className="loading">
      <span className="spinner" />
      Loading resource intelligence…
    </div>
  )
}

function Field({
  label,
  type = 'text',
  value,
  onChange,
  placeholder = '',
}) {
  return (
    <label className="field">
      <span>{label}</span>
      <input
        type={type}
        value={value ?? ''}
        placeholder={placeholder}
        onChange={onChange}
      />
    </label>
  )
}

function Select({ label, value, set, options = [] }) {
  return (
    <label className="field">
      <span>{label}</span>
      <select
        value={value ?? ''}
        onChange={(event) => set(event.target.value)}
      >
        {options.map((option) => {
          const item =
            typeof option === 'string'
              ? { value: option, label: option }
              : option

          return (
            <option key={item.value} value={item.value}>
              {item.label}
            </option>
          )
        })}
      </select>
    </label>
  )
}

function Modal({ title, children, close }) {
  return (
    <div className="overlay">
      <div className="modal">
        <div className="modal-head">
          <h2>{title}</h2>
          <button onClick={close}>×</button>
        </div>
        {children}
      </div>
    </div>
  )
}

function Dashboard({ dash, requests, activities, go, session }) {
  if (!dash) return <Loading />

  const available = dash.available_today || 0
  const occupied = dash.occupied_today || 0
  const total = dash.laboratories || 1
  const percentage = Math.round((available / total) * 100)
  const labStatus = dash.lab_status || []

  return (
    <>
      <PageTitle
        eyebrow="COLLEGE RESOURCE COMMAND CENTER"
        title={`Good day, ${session?.role || 'User'}`}
        sub="A live overview of academic laboratory availability, usage and reservations."
        actions={
          <button
            className="primary"
            onClick={() => go('requests')}
          >
            ＋ New Lab Request
          </button>
        }
      />

      <div className="stats-grid">
        <Stat
          label="Total Laboratories"
          value={total}
          sub="Active college resources"
          tone="blue"
          icon="▦"
        />
        <Stat
          label="Available Today"
          value={available}
          sub="Currently free resources"
          tone="green"
          icon="✓"
        />
        <Stat
          label="Occupied / Reserved"
          value={occupied}
          sub="Across active lab slots"
          tone="red"
          icon="!"
        />
        <Stat
          label="Pending Requests"
          value={dash.pending_requests ?? dash.requests}
          sub="Awaiting admin review"
          tone="purple"
          icon="◇"
        />
        <Stat
          label="Scheduling Conflicts"
          value={dash.active_conflicts ?? (dash.upcoming_conflicts ? dash.upcoming_conflicts.length : 0)}
          sub="Detected overlaps / unverified"
          tone="orange"
          icon="▲"
        />
        <Stat
          label="Utilization Rate"
          value={dash.utilization_rate != null ? `${dash.utilization_rate}%` : '0%'}
          sub="Confirmed actual vs scheduled"
          tone="blue"
          icon="◈"
        />
      </div>

      <div className="dashboard-grid top-grid">
        <Card
          title="Live Lab Availability"
          action={
            <span className="live-pill">
              <i /> Live
            </span>
          }
        >
          <div className="availability-visual">
            <div
              className="donut"
              style={{ '--p': `${percentage}%` }}
            >
              <b>{percentage}%</b>
              <span>Available</span>
            </div>

            <div className="legend-list">
              <div>
                <i className="dot green" />
                Available <b>{available}</b>
              </div>
              <div>
                <i className="dot red" />
                Occupied / Reserved <b>{occupied}</b>
              </div>
              <div>
                <i className="dot blue" />
                Total <b>{total}</b>
              </div>
            </div>
          </div>

          <div className="hover-labs">
            {labStatus.map((lab) => (
              <div className="hover-lab" key={lab.lab_id}>
                <span
                  className={`mini-status ${lab.status === 'Available' ? 'free' : 'busy'
                    }`}
                />
                <b>{lab.lab_name}</b>
                <em>{lab.status}</em>

                <div className="lab-tooltip">
                  <strong>{lab.lab_name}</strong>
                  <span>
                    {lab.lab_id} • Capacity {lab.capacity}
                  </span>
                  <span>{lab.location}</span>
                  <span>{lab.reason}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Year-wise Timetable Coverage">
          <Bars
            data={dash.years || []}
            empty="Upload the semester timetable to populate coverage."
          />
          <div className="card-foot-note">
            Coverage is derived from the timetable stored in the backend
            database.
          </div>
        </Card>
      </div>

      <div className="dashboard-grid bottom-grid">
        <Card
          title="Recent Lab Requests"
          action={
            <button
              className="text-button"
              onClick={() => go('requests')}
            >
              View all →
            </button>
          }
        >
          <RequestTable requests={requests.slice(0, 5)} compact />
        </Card>

        <Card
          title="Upcoming Academic Activities"
          action={
            <button
              className="text-button"
              onClick={() => go('activities')}
            >
              Manage →
            </button>
          }
        >
          <div className="activity-mini-list">
            {activities.slice(0, 4).map((activity) => (
              <div className="mini-row" key={activity.id}>
                <div className="date-box">
                  <b>
                    {new Date(
                      `${activity.activity_date}T00:00:00`
                    ).getDate()}
                  </b>
                  <small>
                    {new Date(
                      `${activity.activity_date}T00:00:00`
                    ).toLocaleDateString('en-US', {
                      month: 'short',
                    })}
                  </small>
                </div>

                <div>
                  <b>{activity.activity_name}</b>
                  <small>
                    {activity.start_time}–{activity.end_time} •{' '}
                    {activity.laboratory || 'Campus'}
                  </small>
                </div>

                <Badge text={activity.status} />
              </div>
            ))}

            {!activities.length && (
              <Empty text="No activities scheduled." />
            )}
          </div>
        </Card>
      </div>

      {/* SECTION 6.5 — LIVE LAB UTILIZATION */}
      <Card
        title="Section 6.5 • Live Lab Utilization"
        action={
          <button className="text-button" onClick={() => go('availability')}>
            Availability Finder →
          </button>
        }
      >
        {(!dash.live_utilization || !dash.live_utilization.length) ? (
          <Empty text="Usage data not yet recorded for active laboratories." />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Laboratory Identifier</th>
                  <th>Status</th>
                  <th>Session Slot</th>
                  <th>Capacity</th>
                  <th>Occupancy</th>
                  <th>Utilization</th>
                  <th>Data Source</th>
                  <th>Last Update</th>
                </tr>
              </thead>
              <tbody>
                {dash.live_utilization.map((item) => (
                  <tr key={`${item.lab_id}-${item.time_slot}`}>
                    <td>
                      <b>{item.lab_name || item.lab_id}</b>
                      <small style={{ display: 'block', color: 'var(--color-text-secondary)' }}>
                        {item.location || 'College Block'}
                      </small>
                    </td>
                    <td><Badge text={item.status} /></td>
                    <td>{item.time_slot}</td>
                    <td>{item.capacity}</td>
                    <td>{item.recorded_occupancy ?? 0} seats</td>
                    <td>
                      <b>{item.utilization_percentage != null ? `${item.utilization_percentage}%` : '0%'}</b>
                    </td>
                    <td>
                      <small style={{ color: 'var(--color-primary-teal)', fontWeight: 600 }}>
                        {item.data_source}
                      </small>
                    </td>
                    <td>
                      <small>{item.last_updated || 'Live'}</small>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* SECTION 6.6 — UPCOMING RESOURCE CONFLICTS & SECTION 6.4 ACTIVITY */}
      <div className="dashboard-grid bottom-grid" style={{ marginTop: '20px' }}>
        <Card
          title="Section 6.6 • Upcoming Resource Conflicts"
          action={
            <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>
              {(dash.upcoming_conflicts || []).length} Detected
            </span>
          }
        >
          {(!dash.upcoming_conflicts || !dash.upcoming_conflicts.length) ? (
            <Empty text="No scheduling conflicts detected. All scheduled allocations and reservations are consistent." />
          ) : (
            <div className="activity-mini-list">
              {dash.upcoming_conflicts.slice(0, 6).map((c) => (
                <div className="mini-row" key={c.id}>
                  <div className="date-box" style={{ background: c.severity === 'HIGH' ? '#FFECEC' : '#FFF3DB' }}>
                    <b style={{ color: c.severity === 'HIGH' ? '#B54747' : '#B7791F' }}>
                      {c.severity}
                    </b>
                    <small>ALERT</small>
                  </div>
                  <div>
                    <b>{c.laboratory}</b>
                    <small style={{ color: 'var(--color-text-main)' }}>
                      {c.time_interval} • {c.overlapping_items}
                    </small>
                    <small style={{ color: 'var(--color-text-secondary)', display: 'block', marginTop: '2px' }}>
                      {c.conflict_reason} — <em>{c.resolution}</em>
                    </small>
                  </div>
                  <Badge text={c.severity === 'HIGH' ? 'Conflict' : 'Review'} />
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* SECTION 6.4 — RECENT SYSTEM ACTIVITY FEED */}
        <Card title="Section 6.4 • Traceable Activity History">
          {(!dash.recent_activity || !dash.recent_activity.length) ? (
            <Empty text="No system operations logged yet." />
          ) : (
            <div className="activity-mini-list">
              {dash.recent_activity.slice(0, 5).map((log) => (
                <div className="mini-row" key={log.id}>
                  <div>
                    <b>{log.action}</b>
                    <small style={{ color: 'var(--color-text-main)' }}>
                      {log.entity_type} {log.entity_id ? `(#${log.entity_id})` : ''} • By {log.actor}
                    </small>
                    <small style={{ color: 'var(--color-text-secondary)', display: 'block' }}>
                      {log.details || 'System event'}
                    </small>
                  </div>
                  <small style={{ color: 'var(--color-text-secondary)', whiteSpace: 'nowrap' }}>
                    {log.created_at?.slice(11, 16) || '—'}
                  </small>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </>
  )
}

function Bars({ data = [], empty }) {
  if (!data.length) return <Empty text={empty} />

  const max = Math.max(
    ...data.map((item) => Number(item.value) || 0),
    1
  )

  return (
    <div className="bars">
      {data.map((item) => (
        <div className="bar-col" key={item.name}>
          <div
            className="bar"
            style={{
              height: `${Math.max(
                8,
                (Number(item.value) / max) * 100
              )}%`,
            }}
          />
          <b>{Number(item.value) || 0}</b>
          <small>
            {String(item.name).replace(' Year', '')}
          </small>
        </div>
      ))}
    </div>
  )
}

function Timetable({ meta }) {
  const [dateValue, setDateValue] = useState(today())
  const [year, setYear] = useState('All Years')
  const [department, setDepartment] = useState('All Departments')
  const [rows, setRows] = useState([])
  const [labs, setLabs] = useState([])
  const [states, setStates] = useState({})
  const [facultyUsage, setFacultyUsage] = useState([])
  const [venueAssignments, setVenueAssignments] = useState({})
  const [error, setError] = useState('')
  

  const load = async () => {
    try {
      const [timetableData, laboratoryData] = await Promise.all([
        api(
          `/api/timetable?year=${esc(
            year
          )}&department=${esc(
            department
          )}&selected_date=${dateValue}`
        ),
        api('/api/laboratories'),
      ])

      setRows(timetableData || [])
      setLabs(laboratoryData || [])

      const usageRecords = await api(
  `/api/faculty-usage?selected_date=${dateValue}`
)
setFacultyUsage(usageRecords || [])

      const slots = meta.slots?.length
        ? meta.slots
        : DEFAULT_SLOTS

      const [availabilityResults, venueResults] = await Promise.all([
        Promise.all(slots.map((slot) =>
          api(`/api/lab-availability?selected_date=${dateValue}&time_slot=${esc(slot)}&year=${esc(year)}&department=${esc(department)}`)
        )),
        Promise.all(slots.map((slot) =>
          api(`/api/venue-mappings?selected_date=${dateValue}&time_slot=${esc(slot)}&year=${esc(year)}&department=${esc(department)}`)
            .catch(() => ({ mappings: [] }))
        )),
      ])

      const availabilityMap = {}
      availabilityResults.forEach((result, index) => {
        ;(result.labs || []).forEach((lab) => {
          availabilityMap[`${lab.lab_id}|${slots[index]}`] = lab
        })
      })

      const assignmentMap = {}
      venueResults.forEach((result, index) => {
        assignmentMap[slots[index]] = result.mappings || []
      })

      setStates(availabilityMap)
      setVenueAssignments(assignmentMap)
      setError('')
    } catch (err) {
      setError(err.message || 'Unable to load timetable.')
    }
  }

  useEffect(() => {
    load()
  }, [dateValue, year, department, meta.slots.join('|')])

  const slots = meta.slots?.length
    ? meta.slots
    : DEFAULT_SLOTS

  return (
    <>
      <PageTitle
        eyebrow="LIVE SCHEDULE"
        title="Timetable & Availability"
        sub={`${dayName(dateValue)} • ${formatDate(dateValue)} • choose a branch and year to show only matching classes. Past dates show the planned timetable, not confirmed historical occupancy; future dates show the planned schedule. Live availability is shown only when supported by records.`}
      />

      <div className="filter-card">
        <Select
          label="Department"
          value={department}
          set={setDepartment}
          options={['All Departments', ...meta.departments]}
        />

        <Select
          label="Academic Year"
          value={year}
          set={setYear}
          options={['All Years', ...meta.years]}
        />

        <Field
          label="Date"
          type="date"
          value={dateValue}
          onChange={(event) => setDateValue(event.target.value)}
        />
      </div>

      <div className="legend-line">
        <span>
          <i className="legend-box available" />
          Available (recorded)
        </span>

        <span>
          <i className="legend-box red" />
          Faculty Busy / Reserved / Activity
        </span>
        <span>
          <i className="legend-box break" />
          Lunch Break
        </span>
      </div>

      {error && <InlineError text={error} />}

      <Card title={`All timetable predictions — ${dayName(dateValue)} · ${formatDate(dateValue)}`}>
        <div className="slot-prediction-list">
          {slots.map((slot) => {
            const assignments = venueAssignments[slot] || []
            return (
              <section className="slot-prediction" key={`prediction-${slot}`}>
                <div className="slot-prediction-heading">
                  <b>{slot}</b>
                  <span>{assignments.length} scheduled assignment{assignments.length === 1 ? '' : 's'}</span>
                </div>
                {assignments.length ? (
                  <div className="slot-prediction-items">
                    {assignments.map((item, idx) => (
                      <div className="slot-prediction-item" key={`${slot}-${item.lab_venue}-${item.department}-${item.academic_year}-${item.section}-${idx}`}>
                        <b>{item.lab_venue || 'Venue pending verification'}</b>
                        <span>{item.department || 'Branch not recorded'} · Year {item.academic_year || '—'} · Section {item.section || '—'}</span>
                        <small>{item.subject || item.subject_name || 'Subject not recorded'}{item.faculty_name ? ` · ${item.faculty_name}` : ''}</small>
                      </div>
                    ))}
                  </div>
                ) : <p className="slot-prediction-empty">No timetable venue assignment is recorded for this slot.</p>}
              </section>
            )
          })}
        </div>
      </Card>

      <Card
        title={`Laboratory resource board — ${formatDate(
          dateValue
        )}`}
      >
        {!labs.length ? (
          <Empty text="No laboratories configured." />
        ) : (
          <div className="schedule-wrap">
            <div
              className="schedule-grid"
              style={{ '--cols': labs.length }}
            >
              <div className="schedule-corner">
                Time / Lab
              </div>

              {labs.map((lab) => (
                <div
                  className="lab-header"
                  key={lab.lab_id}
                >
                  <b>{lab.lab_name}</b>
                  <small>{lab.lab_id} · {lab.capacity} seats</small>
                  
                </div>
              ))}

              {slots.map((slot, index) => (
                <React.Fragment key={slot}>
                  <div className="time-cell">
                    <b>{slot}</b>
                    <small>Scheduled time</small>
                  </div>

                  {labs.map((lab) => {
                    
const state =
  states[`${lab.lab_id}|${slot}`] || {
    status: 'Availability Unverified',
    reason: 'No conflicting booking is recorded for this slot.',
  }

const normalizeSlot = (value) =>
  String(value || '')
    .replace(/\s*-\s*/g, '-')
    .replace(/\s+/g, ' ')
    .trim()
    .toUpperCase()

const facultyBusy = facultyUsage.find((record) =>
  String(record.lab_id || '').trim().toLowerCase() ===
    String(lab.lab_id || '').trim().toLowerCase() &&
  normalizeSlot(record.time_slot) === normalizeSlot(slot) &&
  String(record.status || '').trim().toUpperCase() === 'BUSY'
)

const effectiveState = facultyBusy
  ? {
      status: 'Busy (Faculty)',
      reason: `Faculty confirmed usage by ${facultyBusy.faculty || 'Faculty'}`,
    }
  : state

                    const assignment = (venueAssignments[slot] || []).find(
                      (item) => String(item.lab_venue || '').trim().toLowerCase() === String(lab.lab_name || lab.lab_id || '').trim().toLowerCase()
                    )
                    const isRed = [
  'Busy (Faculty)',
  'Reserved',
  'Workshop / Activity',
  'Occupied',
].includes(effectiveState.status)
                    const hasScheduledAssignment = Boolean(assignment)
                    const verifiedAssignment = assignment && String(assignment.mapping_status || '').toUpperCase() === 'VERIFIED'
                    const displayedStatus = isRed
  ? effectiveState.status
  : hasScheduledAssignment
    ? 'Occupied / Scheduled'
    : effectiveState.status

                    return (
                      <div
                        className={`resource-cell ${isRed
                            ? 'red-cell'
                            : hasScheduledAssignment
                              ? 'scheduled-cell'
                              : effectiveState.status === 'Available'
                                ? 'available-cell'
                                : 'unverified-cell'
                          }`}
                        key={`${slot}-${lab.lab_id}`}
                        title={effectiveState.reason}
                      >
                        
{isRed ? (
  <>
    <b>{effectiveState.status}</b>
    <small>{effectiveState.reason}</small>
  </>
) : hasScheduledAssignment ? (
  <>
    <b>{displayedStatus}</b>
    <small>{assignment.subject}</small>
    <small>
      {assignment.department} · {assignment.academic_year} · {assignment.section}
    </small>
  </>
) : effectiveState.status === 'Available' ? (
  <b>Available</b>
) : (
  <>
    <b>{effectiveState.status || 'Availability Unverified'}</b>
    <small>
      {effectiveState.reason || 'No verified occupancy record for this time.'}
    </small>
  </>
)}

           </div>
                )
              })}
            </React.Fragment>
          ))}
        </div>
      </div>
    )}
  </Card>
  </>
)
}
function Availability({ meta }) {
  const [dateValue, setDateValue] = useState(today())
  const [slot, setSlot] = useState(meta.slots?.[0] || DEFAULT_SLOTS[0])
  const [selectedSlots, setSelectedSlots] = useState([])
  const [data, setData] = useState([])
  const [venueData, setVenueData] = useState([])
  const [venueError, setVenueError] = useState('')
  const [error, setError] = useState('')


  useEffect(() => {
    if (!meta.slots.includes(slot)) {
      setSlot(meta.slots[0] || DEFAULT_SLOTS[0])
    }
  }, [meta.slots.join('|')])

  useEffect(() => {
    api(
      `/api/lab-availability?selected_date=${dateValue}&time_slot=${esc(
        slot
      )}`
    )
      .then((result) => {
        setData(result.labs || [])
        setError('')
      })
      .catch((err) => setError(err.message))
  }, [dateValue, slot])


  useEffect(() => {
    if (!dateValue || !slot) {
      setVenueData([])
      return
    }

    api(
      `/api/venue-mappings?selected_date=${dateValue}&time_slot=${esc(slot)}`
    )
      .then((result) => {
        setVenueData(result.mappings || [])
        setVenueError('')
      })
      .catch((err) => {
        setVenueData([])
        setVenueError(err.message)
      })
  }, [dateValue, slot])


  const free = data.filter(
    (item) => item.status === 'Available'
  ).length

  return (
    <>
      <PageTitle
        eyebrow="RESOURCE FINDER"
        title="Lab Availability"
        sub="Choose a date and laboratory time slot to inspect resource availability and timetable venue assignments."
      />

      <div className="filter-card">
        <Field
          label="Date"
          type="date"
          value={dateValue}
          onChange={(event) => setDateValue(event.target.value)}
        />

        <Select
          label="Laboratory Session"
          value={slot}
          set={setSlot}
          options={meta.slots}
        />
      </div>

      {error && <InlineError text={error} />}

      <div className="availability-banner">
        <div>
          <span>Selected session</span>
          <b>
            {formatDate(dateValue)} • {slot}
          </b>
        </div>
        <strong>{free} labs available</strong>
      </div>

      <div className="lab-grid">
        {data.map((lab) => (
          <div
            className={`lab-card ${lab.status === 'Available'
                ? 'is-free'
                : 'is-busy'
              }`}
            key={lab.lab_id}
          >
            <div className="lab-card-top">
              <span>{lab.lab_id}</span>
              <Badge text={lab.status} />
            </div>

            <h3>{lab.lab_name}</h3>
            <p>{lab.location}</p>

            <div className="lab-facts">
              <span>
                Capacity <b>{lab.capacity}</b>
              </span>
              <span>{lab.lab_type}</span>
            </div>

            <small>{lab.reason}</small>
          </div>
        ))}

        {!data.length && (
          <Empty text="No availability data returned." />
        )}
      </div>


      <div className="soft-note recommendation-status-note">
        <strong>Recommendation status: Verification pending</strong>
        <p>
          Physical laboratory inventory has not yet been verified.
          Timetable assignments are not proof of availability, so
          no confirmed laboratory recommendation can be provided.
          Verify the physical venue and its actual usage before
          approving a request.
        </p>
      </div>


      <div className="venue-mappings-section">
        <PageTitle
          eyebrow="TIMETABLE INTELLIGENCE"
          title="Timetable Venue Assignments"
          sub="View scheduled lab sessions and their mapped venues. Assignments marked for review are not yet verified."
        />

        {venueError && <InlineError text={venueError} />}

        {!venueError && venueData.length > 0 && (
          <div className="venue-mappings-list">
            {venueData.map((mapping) => (
              <div className="venue-mapping-card" key={mapping.id}>
                <div className="venue-mapping-top">
                  <span>{mapping.department} · {mapping.section}</span>
                  <Badge text={mapping.mapping_status} />
                </div>

                <h3>{mapping.lab_venue}</h3>

                <p>{mapping.subject}</p>

                <div className="lab-facts">
                  <span>
                    Academic year <b>{mapping.academic_year}</b>
                  </span>
                  <span>
                    Day <b>{mapping.day}</b>
                  </span>
                </div>

                <div className="lab-facts">
                  <span>
                    Periods <b>{mapping.start_period}–{mapping.end_period}</b>
                  </span>
                  <span>
                    Venue type <b>{mapping.venue_type}</b>
                  </span>
                </div>

                <small>
                  Verify this timetable assignment before treating the venue
                  as confirmed.
                </small>
              </div>
            ))}
          </div>
        )}

        {!venueError && venueData.length === 0 && (
          <Empty text="No venue assignments found for this date and session." />
        )}
      </div>

    </>
  )
}

function Usage({
  labs,
  meta,
  selectedDepartment,
  onSaved,
}) {
  const [dateValue, setDateValue] = useState(today())
  const [lab, setLab] = useState(labs[0]?.lab_id || '')
  const [selectedSlots, setSelectedSlots] = useState([])
  const [branch, setBranch] = useState('')
  const [year, setYear] = useState(
    meta.years.at(-1) || 'IV Year'
  )
  const [section, setSection] = useState('A')
  const [faculty, setFaculty] = useState('Faculty')
  const [status, setStatus] = useState('BUSY')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [existing, setExisting] = useState([])

  
const departmentCode = String(selectedDepartment || '').toUpperCase()

const branchOptions = departmentCode.includes('ARTIFICIAL')
  || departmentCode === 'AIML'
  || departmentCode === 'AIM'
  ? ['AIML', 'CAI']
  : departmentCode.includes('COMPUTER SCIENCE')
    || departmentCode === 'CSE'
    ? ['CSE', 'CST', 'CDS']
    : departmentCode.includes('ELECTRONICS')
      || departmentCode === 'ECE'
      ? ['ECE', 'ECT']
      : departmentCode.includes('ELECTRICAL')
        || departmentCode === 'EEE'
        ? ['EEE']
        : departmentCode.includes('MECHANICAL')
          || departmentCode === 'MECH'
          || departmentCode === 'ME'
          ? ['Mech']
          : departmentCode.includes('CIVIL')
            || departmentCode === 'CE'
            ? ['Civil']
            : []

  useEffect(() => {
  setBranch((current) =>
    branchOptions.includes(current)
      ? current
      : branchOptions[0] || ''
  )
}, [selectedDepartment])

  useEffect(() => {
    if (!lab && labs[0]) {
      setLab(labs[0].lab_id)
    }
  }, [labs, lab])

  useEffect(() => {
    api(`/api/faculty-usage?selected_date=${dateValue}`)
      .then(setExisting)
      .catch(() => setExisting([]))
  }, [dateValue])

  
  const save = async () => {
    if (selectedSlots.length === 0) {
      setError('Please select at least one time slot.')
      return
    }

    setSaving(true)
    setError('')

    try {
      const selectedLab = labs.find(
        (item) => item.lab_id === lab
      )

      for (const selectedSlot of selectedSlots) {
        await api('/api/faculty-usage', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            lab_id: lab,
            lab_name: selectedLab?.lab_name || '',
            usage_date: dateValue,
            time_slot: selectedSlot,
            department: branch,
            academic_year: year,
            section,
            status,
            faculty,
          }),
        })
      }

      await onSaved()
      setError('')
    } catch (err) {
      setError(
        `Saving stopped: ${err.message}. Some selected slots may already have been saved.`
      )
    } finally {
      setSaving(false)
    }
  }


  return (
    <>
      <PageTitle
        eyebrow="ACTUAL USAGE CONFIRMATION"
        title="Lab Usage (Faculty)"
        sub="The checklist is an operational override: BUSY changes only the selected date + selected 3-hour session."
      />

      <div className="two-col">
        <Card title="Faculty Usage Checklist">
          <div className="form-grid">
            <Select
              label="Laboratory"
              value={lab}
              set={setLab}
              options={labs.map((item) => ({
                value: item.lab_id,
                label: `${item.lab_id} — ${item.lab_name}`,
              }))}
            />

            <Field
              label="Date"
              type="date"
              value={dateValue}
              onChange={(event) =>
                setDateValue(event.target.value)
              }
            />

            
  
<div className="slot-checklist">
  <label>Time Slots</label>

  {FACULTY_USAGE_SLOTS.map((timeSlot) => (
    <label key={timeSlot} className="slot-checkbox">
      <input
        type="checkbox"
        checked={selectedSlots.includes(timeSlot)}
        onChange={(event) => {
          setSelectedSlots((current) =>
            event.target.checked
              ? [...current, timeSlot]
              : current.filter((item) => item !== timeSlot)
          )
        }}
      />
      <span>{timeSlot}</span>
    </label>
  ))}
</div>

<Select
  label="Branch"
  value={branch}
  set={setBranch}
  options={branchOptions}
/>

            <Select
              label="Academic Year"
              value={year}
              set={setYear}
              options={meta.years}
            />

            <Field
              label="Section"
              value={section}
              onChange={(event) =>
                setSection(event.target.value)
              }
            />

            <Field
              label="Faculty Name"
              value={faculty}
              onChange={(event) =>
                setFaculty(event.target.value)
              }
            />
          </div>

          <div className="check-choice">
            <button
              className={status === 'BUSY' ? 'chosen' : ''}
              onClick={() => setStatus('BUSY')}
            >
              <b>●</b> Mark Lab BUSY
            </button>

            <button
              className={
                status === 'FREE'
                  ? 'chosen free-choice'
                  : ''
              }
              onClick={() => setStatus('FREE')}
            >
              <b>○</b> Mark Lab FREE
            </button>
          </div>

          {error && <InlineError text={error} />}

          <div className="actions">
            <button
              className="primary"
              disabled={!lab || saving}
              onClick={save}
            >
              {saving ? 'Saving…' : 'Save Checklist'}
            </button>
          </div>
        </Card>

        <Card title="What happens next">
          <div className="rule-list">
            <div>
              <b>01</b>
              <span>
                BUSY is stored in SQLite for the exact date,
                session, department, year and section.
              </span>
            </div>
            <div>
              <b>02</b>
              <span>
                The timetable board immediately changes that
                laboratory cell to red.
              </span>
            </div>
            <div>
              <b>03</b>
              <span>
                Lab Availability and the recommendation engine
                treat BUSY as a hard constraint.
              </span>
            </div>
            <div>
              <b>04</b>
              <span>
                Previous and future dates remain unchanged.
              </span>
            </div>
          </div>

          <div className="soft-note">
            Tip: use this checklist after a class is actually
            cancelled, moved or occupied unexpectedly.
          </div>
        </Card>
      </div>

      <Card
        title={`Saved confirmations — ${formatDate(dateValue)}`}
        className="mt-card"
      >
        <RequestTable
          requests={existing.map((item) => ({
            ...item,
            id: item.id,
            status: item.status,
            recommended_lab: item.lab_name,
            request_date: item.usage_date,
          }))}
          usage
        />
      </Card>
    </>
  )
}

function Requests({
  requests,
  meta,
  selectedDepartment,
  onChanged,
}) {
  const [open, setOpen] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const [form, setForm] = useState({
    request_date: today(),
    time_slot:
      meta.slots[1] || DEFAULT_SLOTS[1],
    department: selectedDepartment,
    academic_year:
      meta.years.at(-1) || 'IV Year',
    section: 'A',
    students: 40,
    purpose: 'Laboratory practical',
    preferred_lab_type: 'AI / ML',
  })

  useEffect(() => {
    const code = String(selectedDepartment || '').toUpperCase()
    const branch = code.includes('ARTIFICIAL') || code === 'AIM' || code === 'AIML' ? 'AIM'
      : code.includes('COMPUTER SCIENCE') || code === 'CSE' ? 'CSE'
      : code.includes('ELECTRONICS') || code === 'ECE' ? 'ECE'
      : code.includes('ELECTRICAL') || code === 'EEE' ? 'EEE'
      : code.includes('MECHANICAL') || code === 'MECH' || code === 'ME' ? 'ME'
      : code.includes('CIVIL') || code === 'CE' ? 'CE' : selectedDepartment
    setForm((current) => ({ ...current, department: branch }))
  }, [selectedDepartment])

  const change = (key, value) => {
    setForm((current) => ({
      ...current,
      [key]: value,
    }))
  }

  const submit = async () => {
    setError('')

    try {
      const response = await api('/api/requests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          students: Number(form.students),
        }),
      })

      setResult(response)
      setOpen(false)

      await onChanged(
        `Request REQ${String(response.id).padStart(
          3,
          '0'
        )} created • ${response.recommended_lab || 'No suitable lab'
        } recommended.`
      )
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <PageTitle
        eyebrow="ALLOCATION REQUESTS"
        title="Lab Requests"
        sub="Submit a requirement; the backend filters conflicts and capacity before ranking the best available laboratory."
        actions={
          <button
            className="primary"
            onClick={() => setOpen(true)}
          >
            ＋ New Lab Request
          </button>
        }
      />

      {result && (
        <div className="success-panel">
          <div>
            <b>
              REQ{String(result.id).padStart(3, '0')} processed
            </b>
            <span>
              Recommended laboratory:{' '}
              <strong>
                {result.recommended_lab ||
                  'No suitable laboratory'}
              </strong>{' '}
              • Score: {result.recommendation_score ?? '—'}
            </span>
          </div>

          <small>
            {result.notification?.sent
              ? 'Email sent'
              : 'Notification ready for'}{' '}
            {result.notification?.recipient ||
              'selected HOD'}
          </small>
        </div>
      )}

      <Card title="Request Register">
        <RequestTable
          requests={requests}
          onChanged={onChanged}
        />
      </Card>

      {open && (
        <Modal
          title="Create New Lab Request"
          close={() => setOpen(false)}
        >
          <div className="form-grid">
            <Field
              label="Required Date"
              type="date"
              value={form.request_date}
              onChange={(event) =>
                change(
                  'request_date',
                  event.target.value
                )
              }
            />

            <Select
              label="3-hour Session"
              value={form.time_slot}
              set={(value) => change('time_slot', value)}
              options={meta.slots}
            />

            <Select
              label="Branch"
              value={form.department}
              set={(value) => change('department', value)}
              options={(() => {
                const code = String(selectedDepartment || '').toUpperCase()
                if (code.includes('ARTIFICIAL') || code === 'AIM' || code === 'AIML') return ['AIM', 'CAI']
                if (code.includes('COMPUTER SCIENCE') || code === 'CSE') return ['CSE', 'CST', 'CSD']
                if (code.includes('ELECTRONICS') || code === 'ECE') return ['ECE', 'ECT']
                if (code.includes('ELECTRICAL') || code === 'EEE') return ['EEE']
                if (code.includes('MECHANICAL') || code === 'MECH' || code === 'ME') return ['ME']
                if (code.includes('CIVIL') || code === 'CE') return ['CE']
                return [form.department || selectedDepartment]
              })()}
            />

            <Select
              label="Academic Year"
              value={form.academic_year}
              set={(value) =>
                change('academic_year', value)
              }
              options={meta.years}
            />

            <Field
              label="Section"
              value={form.section}
              onChange={(event) =>
                change('section', event.target.value)
              }
            />

            <Field
              label="Students"
              type="number"
              value={form.students}
              onChange={(event) =>
                change('students', event.target.value)
              }
            />

            <Field
              label="Purpose"
              value={form.purpose}
              onChange={(event) =>
                change('purpose', event.target.value)
              }
            />

            <Select
              label="Preferred Lab Type"
              value={form.preferred_lab_type}
              set={(value) =>
                change('preferred_lab_type', value)
              }
              options={[
                'AI / ML',
                'Programming',
                'Database',
                'Networking',
                'Embedded Systems',
                'General',
              ]}
            />
          </div>

          <div className="recipient-preview">
            <span>HOD notification</span>
            <b>
              {DEPARTMENTS.find(
                (department) =>
                  department.name === form.department
              )?.hod || 'HOD'}
            </b>
            <small>
              {DEPARTMENTS.find(
                (department) =>
                  department.name === form.department
              )?.email || '—'}
            </small>
          </div>

          {error && <InlineError text={error} />}

          <div className="actions">
            <button
              className="secondary"
              onClick={() => setOpen(false)}
            >
              Cancel
            </button>

            <button
              className="primary"
              onClick={submit}
            >
              Submit & Recommend Lab
            </button>
          </div>
        </Modal>
      )}
    </>
  )
}

function RequestTable({
  requests = [],
  compact = false,
  onChanged,
  usage = false,
}) {
  return (
    <div
      className={`data-table ${compact ? 'compact' : ''
        }`}
    >
      <div className="data-row head">
        <span>ID</span>
        <span>Date</span>
        <span>Time / Resource</span>
        <span>Department</span>
        <span>Students</span>
        <span>Result</span>
        {!compact && !usage && <span>Action</span>}
      </div>

      {requests.map((request) => (
        <div className="data-row" key={request.id}>
          <span>
            <b>
              {usage ? 'USE' : 'REQ'}
              {String(request.id).padStart(3, '0')}
            </b>
          </span>

          <span>
            {formatDate(
              request.request_date ||
              request.usage_date
            )}
          </span>

          <span>{request.time_slot}</span>
          <span>{request.department}</span>
          <span>{request.students || '—'}</span>

          <span>
            {usage ? (
              <Badge text={request.status} />
            ) : (
              <>
                <b>
                  {request.recommended_lab ||
                    'No match'}
                </b>
                <small>
                  {request.recommendation_score
                    ? `Score ${request.recommendation_score}`
                    : ''}
                </small>
              </>
            )}
          </span>

          {!compact && !usage && (
            <span>
              {request.status === 'Pending' ? (
                <button
                  className="small-button"
                  onClick={async () => {
                    await api(
                      `/api/requests/${request.id}?status=Approved`,
                      { method: 'PATCH' }
                    )
                    await onChanged?.(
                      'Request approved.'
                    )
                  }}
                >
                  Approve
                </button>
              ) : (
                <Badge text={request.status} />
              )}
            </span>
          )}
        </div>
      ))}

      {!requests.length && (
        <Empty text="No records available." />
      )}
    </div>
  )
}

function Analytics({ initial }) {
  const [dateValue, setDateValue] = useState(today())
  const [data, setData] = useState(initial)
  const [error, setError] = useState('')

  const load = () => {
    api(`/api/analytics?selected_date=${dateValue}`)
      .then((result) => {
        setData(result)
        setError('')
      })
      .catch((err) => setError(err.message))
  }

  useEffect(() => {
    load()
  }, [dateValue])

  if (!data) return <Loading />

  const maximumScheduled = Math.max(
    ...(data.by_lab || []).map(
      (item) => item.scheduled || 0
    ),
    1
  )

  return (
    <>
      <PageTitle
        eyebrow="DATA INTELLIGENCE"
        title="Analytics"
        sub="Date-based operational summary connected directly to the backend database."
      />

      <div className="filter-card">
        <Field
          label="Analysis Date"
          type="date"
          value={dateValue}
          onChange={(event) =>
            setDateValue(event.target.value)
          }
        />

        <div className="date-summary">
          <span>Selected day</span>
          <b>{formatDate(dateValue)}</b>
        </div>
      </div>

      {error && <InlineError text={error} />}

      <div className="stats-grid">
        <Stat
          label="Total Laboratories"
          value={data.total_laboratories}
          sub="College resources"
        />
        <Stat
          label="Allocated / Active"
          value={data.allocated_labs}
          sub="Selected first lab session"
          tone="purple"
        />
        <Stat
          label="Free Laboratories"
          value={data.free_labs}
          sub="Selected first lab session"
          tone="green"
        />
        <Stat
          label="Seminar Halls / Activities"
          value={data.seminar_halls}
          sub="Seminars on selected date"
          tone="blue"
        />
      </div>

      <div className="two-col">
        <Card title="Occupied History — Selected Date">
          <div className="history-table">
            {data.occupied_history?.map(
              (item, index) => (
                <div
                  className="history-item"
                  key={`${item.lab_id}-${index}`}
                >
                  <div>
                    <b>
                      {item.lab_name || item.lab_id}
                    </b>
                    <small>
                      {item.time_slot} •{' '}
                      {item.department} •{' '}
                      {item.academic_year} •{' '}
                      {item.section}
                    </small>
                  </div>
                  <Badge text={item.status} />
                </div>
              )
            )}

            {!data.occupied_history?.length && (
              <Empty text="No faculty usage records for this date." />
            )}
          </div>
        </Card>

        <Card title="Laboratory Schedule Volume">
          <div className="analytics-bars">
            {(data.by_lab || [])
              .slice(0, 8)
              .map((item) => (
                <div key={item.lab_id}>
                  <div>
                    <span>{item.lab_name}</span>
                    <b>{item.scheduled}</b>
                  </div>
                  <div className="track">
                    <i
                      style={{
                        width: `${((item.scheduled || 0) /
                            maximumScheduled) *
                          100
                          }%`,
                      }}
                    />
                  </div>
                </div>
              ))}
          </div>
        </Card>
      </div>

      <Card title="Department-wise Timetable Records">
        <div className="dept-chips">
          {(data.by_department || []).map((item) => (
            <div key={item.name}>
              <b>{item.name}</b>
              <span>{item.value} records</span>
            </div>
          ))}
        </div>
      </Card>
    </>
  )
}

function Activities({
  labs,
  activities,
  departments,
  onChanged,
}) {
  const [open, setOpen] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    activity_name: '',
    activity_type: 'Workshop',
    activity_date: today(),
    start_time: '10:30',
    end_time: '13:00',
    organizer: '',
    expected_students: 40,
    laboratory: labs[0]?.lab_name || '',
    department: departments[0]?.name || '',
  })

  useEffect(() => {
    if (!form.laboratory && labs[0]) {
      setForm((current) => ({
        ...current,
        laboratory: labs[0].lab_name,
      }))
    }
  }, [labs, form.laboratory])

  const change = (key, value) => {
    setForm((current) => ({
      ...current,
      [key]: value,
    }))
  }

  const save = async () => {
    setError('')

    try {
      const slotResponse = await api(`/api/venue-mappings?selected_date=${esc(form.activity_date)}&time_slot=${esc(form.start_time)}`).catch(() => ({ mappings: [] }))
      const occupiedMatch = (slotResponse.mappings || []).find((item) =>
        String(item.lab_venue || '').trim().toLowerCase() === String(form.laboratory || '').trim().toLowerCase()
      )
      let permissionConfirmed = false
      if (occupiedMatch) {
        const occupiedFor = `${occupiedMatch.department || 'Unknown branch'} · Year ${occupiedMatch.academic_year || '—'} · Section ${occupiedMatch.section || '—'} · ${occupiedMatch.subject || 'scheduled class'}`
        permissionConfirmed = window.confirm(`This lab is already occupied at ${form.start_time}.\n\nLab: ${form.laboratory}\nExisting timetable: ${occupiedFor}\n\nDo you have permission to request an override? Continue only if the department has approved it.`)
        if (!permissionConfirmed) return
      }
      const result = await api('/api/activities', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          permission_confirmed: permissionConfirmed,
          expected_students: Number(form.expected_students),
        }),
      })

      setOpen(false)

      await onChanged(
        `Activity saved as ${result.status}${result.notification?.sent
          ? ' and HOD email sent.'
          : '.'
        }`
      )
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <>
      <PageTitle
        eyebrow="ACADEMIC ACTIVITIES"
        title="Workshops / Activities"
        sub="A planned activity becomes Scheduled when its start time is reached. Until then it is Upcoming. Its lab is reserved automatically for the overlapping session."
        actions={
          <button
            className="primary"
            onClick={() => setOpen(true)}
          >
            ＋ Add Activity
          </button>
        }
      />

      <div className="status-explain">
        <span>
          <Badge text="Upcoming" /> Future activity
        </span>
        <span>
          <Badge text="Scheduled" /> Currently running
        </span>
        <span>
          <Badge text="Completed" /> Finished
        </span>
      </div>

      <div className="activity-grid">
        {activities.map((activity) => (
          <div
            className="activity-card"
            key={activity.id}
          >
            <div className="activity-top">
              <span className="activity-icon">◈</span>
              <Badge text={activity.status} />
            </div>

            <h3>{activity.activity_name}</h3>
            <p>
              {activity.activity_type} •{' '}
              {formatDate(activity.activity_date)}
            </p>
            <p>
              <b>
                {activity.start_time} –{' '}
                {activity.end_time}
              </b>{' '}
              • {activity.laboratory || 'Campus'}
            </p>
            <small>
              {activity.department ||
                activity.organizer ||
                'College Administration'}{' '}
              • {activity.expected_students} students
            </small>

            <button
              className="danger-link"
              onClick={async () => {
                await api(
                  `/api/activities/${activity.id}`,
                  { method: 'DELETE' }
                )
                await onChanged(
                  'Activity removed; timetable and availability released.'
                )
              }}
            >
              Remove
            </button>
          </div>
        ))}

        {!activities.length && (
          <Empty text="No workshops or activities recorded." />
        )}
      </div>

      {open && (
        <Modal
          title="Plan Workshop / Activity"
          close={() => setOpen(false)}
        >
          <div className="form-grid">
            <Field
              label="Activity Name"
              value={form.activity_name}
              onChange={(event) =>
                change(
                  'activity_name',
                  event.target.value
                )
              }
            />

            <Select
              label="Type"
              value={form.activity_type}
              set={(value) =>
                change('activity_type', value)
              }
              options={[
                'Workshop',
                'Seminar',
                'Training',
                'Event',
                'Maintenance',
              ]}
            />

            <Select
              label="Department"
              value={form.department}
              set={(value) =>
                change('department', value)
              }
              options={departments.map(
                (department) => department.name
              )}
            />

            <Field
              label="Date"
              type="date"
              value={form.activity_date}
              onChange={(event) =>
                change(
                  'activity_date',
                  event.target.value
                )
              }
            />

            <Field
              label="Start Time"
              value={form.start_time}
              onChange={(event) =>
                change(
                  'start_time',
                  event.target.value
                )
              }
            />

            <Field
              label="End Time"
              value={form.end_time}
              onChange={(event) =>
                change(
                  'end_time',
                  event.target.value
                )
              }
            />

            <Select
              label="Laboratory"
              value={form.laboratory}
              set={(value) =>
                change('laboratory', value)
              }
              options={labs.map(
                (lab) => lab.lab_name
              )}
            />

            <Field
              label="Expected Students"
              type="number"
              value={form.expected_students}
              onChange={(event) =>
                change(
                  'expected_students',
                  event.target.value
                )
              }
            />

            <Field
              label="Organizer"
              value={form.organizer}
              onChange={(event) =>
                change(
                  'organizer',
                  event.target.value
                )
              }
            />
          </div>

          <div className="soft-note">
            The system calculates Upcoming / Scheduled
            from the planned date and time. If the activity
            overlaps a lab session, that laboratory appears
            red in Timetable View and is unavailable to
            recommendations.
          </div>

          {error && <InlineError text={error} />}

          <div className="actions">
            <button
              className="secondary"
              onClick={() => setOpen(false)}
            >
              Cancel
            </button>

            <button
              className="primary"
              onClick={save}
            >
              Save & Reserve Laboratory
            </button>
          </div>
        </Modal>
      )}
    </>
  )
}

function TimetableUpload({ meta, onImported }) {
  const [file, setFile] = useState(null)
  const [history, setHistory] = useState([])
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const loadHistory = () => {
    api('/api/timetable/upload-history')
      .then(setHistory)
      .catch(() => setHistory([]))
  }

  useEffect(() => {
    loadHistory()
  }, [])

  const upload = async () => {
    if (!file) {
      setError('Please choose one Excel/CSV workbook first.')
      return
    }

    if (!window.confirm(
      'This replaces the timetable master data with the uploaded workbook. Faculty usage, requests and activities are preserved. Continue?'
    )) return

    setBusy(true)
    setError('')
    setMessage('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const result = await api('/api/timetable/upload', {
        method: 'POST',
        body: formData,
      })

      setMessage(
        `${result.rows_imported} rows imported. Years detected: ${(result.years_detected || []).join(', ') || result.academic_year}. Venue mappings imported: ${result.venue_mappings_imported ?? 0}.`
      )
      setFile(null)
      loadHistory()
      await onImported()
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <PageTitle
        eyebrow="MASTER DATA"
        title="Timetable Upload"
        sub="Upload one Excel workbook. LabPulse detects the timetable headers and academic years from the file."
      />

      <div className="upload-grid">
        <Card title="Import Timetable Workbook">
          <div className="upload-hero">
            <div className="upload-icon">⇧</div>
            <div>
              <h2>Upload one Excel / CSV file</h2>
              <p>
                Select the complete workbook. Academic year and semester
                do not need to be selected separately. The system detects
                supported columns and imports available venue values too.
              </p>
            </div>
          </div>

          <label className="drop-zone">
            <input
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={(event) => {
                setFile(event.target.files?.[0] || null)
                setMessage('')
                setError('')
              }}
            />
            <b>{file ? file.name : 'Choose timetable Excel file'}</b>
            <span>Accepted: .xlsx, .xls, .csv</span>
          </label>

          <div className="required-chips">
            <b>Recognized fields</b>
            <span>Academic Year</span>
            <span>Department</span>
            <span>Section</span>
            <span>Day</span>
            <span>Period / Start Period</span>
            <span>Time Slot / Time</span>
            <span>Subject / Lab Name</span>
            <span>Students</span>
            <span>Lab Venue (if provided)</span>
          </div>

          {message && <div className="success-box">✓ {message}</div>}
          {error && <InlineError text={error} />}

          <div className="actions">
            <button
              className="primary"
              disabled={busy || !file}
              onClick={upload}
            >
              {busy ? 'Importing…' : 'Upload and Extract Data'}
            </button>
          </div>
        </Card>

        <Card title="Upload History">
          <div className="history-table">
            {history.map((item) => (
              <div className="history-item" key={item.id}>
                <div>
                  <b>{item.file_name}</b>
                  <small>{item.academic_year} • {item.semester}</small>
                </div>
                <strong>{item.rows_imported}</strong>
              </div>
            ))}
            {!history.length && <Empty text="No uploads yet." />}
          </div>

          <div className="soft-note">
            <b>Automatic storage</b>
            <br />
            Imported rows are saved in the backend database and load again
            when the page is reopened, provided the deployed database uses
            persistent storage.
          </div>
        </Card>
      </div>
    </>
  )
}

function Settings({ hod }) {
  const [status, setStatus] = useState(null)

  const emailTest = async () => {
    try {
      const result = await api('/api/email/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipient: hod.email,
        }),
      })

      setStatus(result)
    } catch (err) {
      setStatus({
        sent: false,
        reason: err.message,
      })
    }
  }

  return (
    <>
      <PageTitle
        eyebrow="SYSTEM PROFILE"
        title="Settings"
        sub="Professional project configuration, data policy and notification status."
      />

      <div className="settings-grid">
        <Card title="Application Summary">
          <div className="setting-list">
            <div>
              <span>Product name</span>
              <b>LabPulse AI</b>
            </div>
            <div>
              <span>Purpose</span>
              <b>
                Academic laboratory availability &
                intelligent allocation
              </b>
            </div>
            <div>
              <span>Frontend</span>
              <b>React + Vite</b>
            </div>
            <div>
              <span>Backend</span>
              <b>FastAPI + Python</b>
            </div>
            <div>
              <span>Database</span>
              <b>SQLite</b>
            </div>
            <div>
              <span>Analytics</span>
              <b>
                Pandas / SQL-based utilization analysis
              </b>
            </div>
            <div>
              <span>ML layer</span>
              <b>
                Scikit-learn compatible ranking /
                forecasting layer
              </b>
            </div>
            <div>
              <span>Upload formats</span>
              <b>Excel (.xlsx/.xls) and CSV</b>
            </div>
          </div>
        </Card>

        <Card title="Professional Project Controls">
          <div className="control-grid">
            <div>
              <b>✓ Hard constraints</b>
              <span>
                Faculty BUSY, reservations, activities and
                capacity are excluded before ranking.
              </span>
            </div>
            <div>
              <b>✓ Semester master data</b>
              <span>
                Timetable upload is intentionally isolated
                to one tab and preserves operational records.
              </span>
            </div>
            <div>
              <b>✓ Date isolation</b>
              <span>
                Faculty usage applies only to the selected
                date and session.
              </span>
            </div>
            <div>
              <b>✓ Transparent recommendations</b>
              <span>
                Every recommendation has a score and
                human-readable reasons.
              </span>
            </div>
            <div>
              <b>✓ HOD notifications</b>
              <span>
                Requests and activities map to the selected
                department's HOD.
              </span>
            </div>
            <div>
              <b>✓ Audit-friendly UI</b>
              <span>
                Analytics exposes date-based occupied history
                from the backend.
              </span>
            </div>
          </div>
        </Card>

        <Card title="HOD Notification Mapping">
          <div className="hod-table">
            {DEPARTMENTS.map((department) => (
              <div key={department.code}>
                <b>{department.code}</b>
                <span>{department.hod}</span>
                <small>{department.email}</small>
              </div>
            ))}
          </div>

          <div className="email-test">
            <div>
              <b>Current HOD: {hod.hod}</b>
              <small>{hod.email}</small>
            </div>

            <button
              className="secondary"
              onClick={emailTest}
            >
              Test notification
            </button>
          </div>

          {status && (
            <div
              className={
                status.sent
                  ? 'success-box'
                  : 'soft-note'
              }
            >
              {status.sent
                ? `✓ Email sent to ${status.recipient}`
                : `Notification ready for ${status.recipient || hod.email
                }. ${status.reason || ''}`}
            </div>
          )}
        </Card>

        <Card title="Operational Notes">
          <div className="notes-grid">
            <span>
              Lab sessions default to{' '}
              <b>10:30 AM–01:00 PM</b> and{' '}
              <b>02:00 PM–04:30 PM</b>; uploaded timetable
              slots override these defaults.
            </span>
            <span>
              Lunch break is represented between the two
              default sessions.
            </span>
            <span>
              Reports and Recommendations have intentionally
              been removed from navigation; recommendations
              are generated directly when a request is
              submitted.
            </span>
          </div>
        </Card>
      </div>
    </>
  )
}