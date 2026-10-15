import React, { useCallback, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, ArrowLeft, CalendarDays, ChevronDown, CircleDollarSign, ClipboardPlus, FileImage, LayoutDashboard, Menu, Pencil, Plus, Search, ShieldCheck, Stethoscope, Trash2, UserRound, Users, X } from 'lucide-react';
import './styles.css';
import './app.css';

const API = import.meta.env.DEV ? '/api/v1' : (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1');
const API_ROOT = API.replace(/\/api\/v1\/?$/, '');
const CLINIC_API = `${API_ROOT}/api/clinic`;
const fallbackPatients = [
  { id: 1, patient_code: 'DMS-0001', full_name: 'Nguyen Minh Anh', phone: '090 123 4567', dentition_type: 'ADULT', allergies: 'Penicillin' },
  { id: 2, patient_code: 'DMS-0002', full_name: 'Tran Gia Bao', phone: '091 234 5678', dentition_type: 'CHILD', allergies: '' },
  { id: 3, patient_code: 'DMS-0003', full_name: 'Le Thu Phuong', phone: '098 555 2026', dentition_type: 'ADULT', allergies: 'None recorded' }
];
const teethAdult = Array.from({ length: 32 }, (_, i) => ({ id: i + 1, code: `A${String(i + 1).padStart(2, '0')}`, state: i === 6 || i === 18 ? 'Needs care' : 'Healthy' }));
const teethChild = Array.from({ length: 20 }, (_, i) => ({ id: i + 1, code: `C${String(i + 1).padStart(2, '0')}`, state: i === 3 ? 'Monitor' : 'Healthy' }));
const navigationByRole = {
  ADMIN: [
    ['Overview', LayoutDashboard], ['Patients', Users], ['Appointments', CalendarDays], ['Tooth chart', Stethoscope],
    ['Billing', CircleDollarSign], ['Radiographs', FileImage], ['Services', ClipboardPlus], ['Doctors', UserRound]
  ],
  DENTIST: [
    ['Overview', LayoutDashboard], ['Patients', Users], ['Appointments', CalendarDays],
    ['Tooth chart', Stethoscope], ['Radiographs', FileImage]
  ],
  RECEPTIONIST: [
    ['Overview', LayoutDashboard], ['Patients', Users], ['Appointments', CalendarDays], ['Billing', CircleDollarSign]
  ]
};

const TOKEN_STORAGE_KEY = 'dms.auth.tokens';

async function apiRequest(path, { tokens, onTokens, method = 'GET', body, apiBase = API } = {}) {
  const send = (accessToken) => fetch(`${apiBase}${path}`, {
    method,
    headers: {
      ...(body ? { 'Content-Type': 'application/json' } : {}),
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
    },
    ...(body ? { body: JSON.stringify(body) } : {})
  });

  let response = await send(tokens?.access);
  if (response.status === 401 && tokens?.refresh && onTokens) {
    const refreshed = await fetch(`${API}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: tokens.refresh })
    });
    if (!refreshed.ok) {
      onTokens(null);
      throw new Error('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
    }
    const nextTokens = { ...tokens, ...(await refreshed.json()) };
    onTokens(nextTokens);
    response = await send(nextTokens.access);
  }

  const payload = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload?.detail || Object.values(payload || {}).flat().join(' ') || `Yêu cầu thất bại (${response.status}).`;
    const error = new Error(detail);
    error.status = response.status;
    error.code = payload?.code;
    throw error;
  }
  return payload;
}

function App() {
  const [section, setSection] = useState('Overview');
  const [patients, setPatients] = useState(fallbackPatients);
  const [appointments, setAppointments] = useState([]);
  const [appointmentsLoading, setAppointmentsLoading] = useState(false);
  const [appointmentsError, setAppointmentsError] = useState('');
  const [tokens, setTokens] = useState(null);
  const [profile, setProfile] = useState(null);
  const [authReady, setAuthReady] = useState(false);
  const [authError, setAuthError] = useState('');
  const [query, setQuery] = useState('');
  const [dentition, setDentition] = useState('ADULT');
  const [selectedTooth, setSelectedTooth] = useState(null);
  const [apiLive, setApiLive] = useState(false);
  const [apiError, setApiError] = useState('');
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    let active = true;
    async function restoreSession() {
      try {
        const stored = localStorage.getItem(TOKEN_STORAGE_KEY);
        if (!stored) return;
        let savedTokens;
        try {
          savedTokens = JSON.parse(stored);
        } catch {
          localStorage.removeItem(TOKEN_STORAGE_KEY);
          return;
        }
        if (!savedTokens?.access || !savedTokens?.refresh) {
          localStorage.removeItem(TOKEN_STORAGE_KEY);
          return;
        }
        let currentTokens = savedTokens;
        const currentUser = await apiRequest('/auth/me/', {
          tokens: savedTokens,
          onTokens: (nextTokens) => {
            if (!nextTokens) {
              localStorage.removeItem(TOKEN_STORAGE_KEY);
              return;
            }
            currentTokens = nextTokens;
            localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(nextTokens));
            if (active) setTokens(nextTokens);
          }
        });
        if (active) {
          setTokens(currentTokens);
          setProfile(currentUser);
        }
      } catch (error) {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        if (active) setAuthError(error.message);
      } finally {
        if (active) setAuthReady(true);
      }
    }
    restoreSession();
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!tokens || !profile) return;
    let active = true;
    setAppointmentsLoading(true);
    setAppointmentsError('');

    apiRequest('/patients/', { tokens, onTokens: updateTokens })
      .then((patientData) => {
        if (!active) return;
        setPatients(patientData);
        setApiError('');
      })
      .catch((error) => {
        if (!active) return;
        setApiError(error.message);
      });

    apiRequest('/appointments/', { tokens, onTokens: updateTokens })
      .then((appointmentData) => {
        if (!active) return;
        setAppointments(appointmentData);
        setApiLive(true);
        setAppointmentsError('');
      })
      .catch((error) => {
        if (!active) return;
        setApiLive(false);
        setAppointmentsError(error.message);
      })
      .finally(() => {
        if (active) setAppointmentsLoading(false);
      });

    return () => { active = false; };
  }, [tokens, profile]);

  const updateTokens = useCallback((nextTokens) => {
    if (!nextTokens) {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      setTokens(null);
      setProfile(null);
      setAuthError('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
      return;
    }
    localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(nextTokens));
    setTokens(nextTokens);
  }, []);

  async function login(username, password) {
    const nextTokens = await apiRequest('/auth/token/', { method: 'POST', body: { username, password } });
    const currentUser = await apiRequest('/auth/me/', { tokens: nextTokens });
    localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(nextTokens));
    setTokens(nextTokens);
    setProfile(currentUser);
    setAuthError('');
  }

  function logout() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setTokens(null);
    setProfile(null);
    setSection('Overview');
    setAuthError('');
  }

  if (!authReady) return <div className="auth-loading">Checking your session…</div>;
  if (!profile) return <LoginPage onLogin={login} initialError={authError} />;

  const visiblePatients = patients.filter((patient) => `${patient.full_name} ${patient.patient_code} ${patient.phone}`.toLowerCase().includes(query.toLowerCase()));
  const nav = navigationByRole[profile.role] || navigationByRole.RECEPTIONIST;
  return <div className="app-shell">
    <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
      <div className="brand"><div className="brand-mark">D</div><div><strong>DMS</strong><span>Dental management</span></div><button className="icon-button close-menu" onClick={() => setMobileOpen(false)}><X size={18} /></button></div>
      <div className="workspace"><span className="eyebrow">Workspace</span><button className="workspace-button">Lotus Dental Clinic <ChevronDown size={15} /></button></div>
      <nav aria-label="Main navigation">{nav.map(([name, Icon]) => <button key={name} className={section === name ? 'nav-item active' : 'nav-item'} aria-current={section === name ? 'page' : undefined} onClick={() => { setSection(name); setMobileOpen(false); }}><Icon size={18} /><span>{name}</span>{name === 'Appointments' && <b>{appointments.length}</b>}</button>)}</nav>
    </aside>
    <main className="main-content">
      <header className="topbar"><button className="icon-button menu-button" onClick={() => setMobileOpen(true)}><Menu size={20} /></button><div><span className="eyebrow">Tuesday, 08 September 2026</span><h1>{section === 'Overview' ? `Good morning, ${profile.display_name}` : section}</h1></div><div className="topbar-actions"><span className={`api-status ${apiLive ? 'live' : ''}`}><span />{apiLive ? 'Live API' : 'Connecting'}</span><button className="icon-button"><Activity size={19} /></button><div className="user-card"><div className="avatar">{profile.display_name.split(' ').map((part) => part[0]).slice(-2).join('')}</div><div><strong>{profile.display_name}</strong><span>{profile.role}</span></div><button className="secondary-button" onClick={logout}>Log out</button></div></div></header>
      {apiError && <div className="api-error" role="alert">{apiError}</div>}
      {section === 'Overview' && <Overview appointments={appointments} patients={patients} setSection={setSection} />}
      {section === 'Patients' && <Patients patients={visiblePatients} query={query} setQuery={setQuery} />}
      {section === 'Appointments' && <Appointments appointments={appointments} loading={appointmentsLoading} error={appointmentsError} tokens={tokens} onTokensChanged={updateTokens} onAppointmentCreated={(created) => setAppointments((current) => [created, ...current])} onAppointmentUpdated={(updated) => setAppointments((current) => current.map((appointment) => appointment.id === updated.id ? updated : appointment))} onAppointmentsReloaded={setAppointments} />}
      {section === 'Tooth chart' && <ToothChart dentition={dentition} setDentition={setDentition} selectedTooth={selectedTooth} setSelectedTooth={setSelectedTooth} />}
      {section === 'Billing' && <Billing patients={patients} />}
      {section === 'Radiographs' && <Radiographs />}
      {section === 'Services' && profile.role === 'ADMIN' && <ServiceManagement tokens={tokens} onTokensChanged={updateTokens} />}
      {section === 'Doctors' && profile.role === 'ADMIN' && <DoctorDirectory tokens={tokens} onTokensChanged={updateTokens} />}
    </main>
  </div>;
}

function LoginPage({ onLogin, initialError }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(initialError);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      await onLogin(username.trim(), password);
    } catch (loginError) {
      setError(loginError.message);
    } finally {
      setSubmitting(false);
    }
  }

  return <main className="login-screen">
    <form className="login-card" onSubmit={handleSubmit}>
      <div className="brand-mark">D</div>
      <span className="eyebrow">LOTUS DENTAL CLINIC</span>
      <h1>Sign in to your clinic</h1>
      <p>Use your clinic account to continue.</p>
      <label htmlFor="login-username">Username</label>
      <input id="login-username" autoComplete="username" required value={username} onChange={(event) => setUsername(event.target.value)} />
      <label htmlFor="login-password">Password</label>
      <input id="login-password" type="password" autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} />
      {error && <div className="form-error" role="alert">{error}</div>}
      <button className="primary-button login-submit" type="submit" disabled={submitting}>{submitting ? 'Signing in…' : 'Sign in'}</button>
    </form>
  </main>;
}

const emptyService = { code: '', name: '', description: '', price: '', duration_minutes: 30, is_active: true };

function ServiceManagement({ tokens, onTokensChanged }) {
  const [services, setServices] = useState([]);
  const [form, setForm] = useState(emptyService);
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  async function loadServices() {
    setLoading(true);
    try {
      setServices(await apiRequest('/services/', { tokens, onTokens: onTokensChanged }));
      setError('');
    } catch (loadError) {
      setError(loadError.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadServices(); }, [tokens, onTokensChanged]);

  function startCreate() {
    setEditingId(null);
    setForm(emptyService);
    setShowForm(true);
    setError('');
  }

  function startEdit(service) {
    setEditingId(service.id);
    setForm({
      code: service.code,
      name: service.name,
      description: service.description,
      price: service.price,
      duration_minutes: service.duration_minutes,
      is_active: service.is_active
    });
    setShowForm(true);
    setError('');
  }

  async function saveService(event) {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      await apiRequest(editingId ? `/services/${editingId}/` : '/services/', {
        tokens,
        onTokens: onTokensChanged,
        method: editingId ? 'PATCH' : 'POST',
        body: { ...form, duration_minutes: Number(form.duration_minutes) }
      });
      setShowForm(false);
      await loadServices();
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  async function deleteService(service) {
    if (!window.confirm(`Deactivate service "${service.name}"?`)) return;
    setError('');
    try {
      await apiRequest(`/services/${service.id}/`, { tokens, onTokens: onTokensChanged, method: 'DELETE' });
      await loadServices();
    } catch (deleteError) {
      setError(deleteError.message);
    }
  }

  return <section className="page-section management-page">
    <div className="section-toolbar">
      <div><span className="eyebrow">CLINIC CATALOG</span><h2>Service catalog</h2></div>
      {!showForm && <button className="primary-button" onClick={startCreate}><Plus size={16} /> Add service</button>}
    </div>
    {error && <div className="form-error" role="alert">{error}</div>}
    {showForm && <form className="panel management-form" onSubmit={saveService}>
      <h3>{editingId ? 'Edit service' : 'New service'}</h3>
      <div className="form-grid">
        <label>Service code<input required maxLength="30" value={form.code} onChange={(event) => setForm({ ...form, code: event.target.value.toUpperCase() })} /></label>
        <label>Service name<input required maxLength="160" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label>
        <label>Price (VND)<input required type="number" min="0" step="1000" value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} /></label>
        <label>Duration (minutes)<input required type="number" min="1" value={form.duration_minutes} onChange={(event) => setForm({ ...form, duration_minutes: event.target.value })} /></label>
        <label className="form-wide">Description<textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} /></label>
        <label className="checkbox-field"><input type="checkbox" checked={form.is_active} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} /> Available for booking</label>
      </div>
      <div className="form-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Saving…' : 'Save service'}</button><button className="secondary-button" type="button" onClick={() => setShowForm(false)}>Cancel</button></div>
    </form>}
    <div className="panel table-panel management-table">
      {loading ? <p className="management-state">Loading services…</p> : services.length === 0 ? <p className="management-state">No services found. Add a service to get started.</p> :
        <table><thead><tr><th>Code</th><th>Service</th><th>Price</th><th>Duration</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>{services.map((service) => <tr key={service.id}>
            <td><code>{service.code}</code></td><td><strong>{service.name}</strong><small className="table-description">{service.description || '—'}</small></td>
            <td>{Number(service.price).toLocaleString('vi-VN')} ₫</td><td>{service.duration_minutes} min</td>
            <td><span className={`pill ${service.is_active ? '' : 'inactive'}`}>{service.is_active ? 'Active' : 'Inactive'}</span></td>
            <td><div className="row-actions"><button className="icon-button" aria-label={`Edit ${service.name}`} onClick={() => startEdit(service)}><Pencil size={16} /></button>{service.is_active && <button className="icon-button danger-button" aria-label={`Deactivate ${service.name}`} onClick={() => deleteService(service)}><Trash2 size={16} /></button>}</div></td>
          </tr>)}</tbody>
        </table>}
    </div>
  </section>;
}

function DoctorDirectory({ tokens, onTokensChanged }) {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    apiRequest('/doctors/', { tokens, onTokens: onTokensChanged })
      .then((data) => { if (active) setDoctors(data); })
      .catch((loadError) => { if (active) setError(loadError.message); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [tokens, onTokensChanged]);

  return <section className="page-section management-page">
    <div className="section-toolbar"><div><span className="eyebrow">CLINIC TEAM</span><h2>Dentist directory</h2></div><span className="pill">{doctors.length} dentists</span></div>
    {error && <div className="form-error" role="alert">{error}</div>}
    <div className="panel table-panel management-table">
      {loading ? <p className="management-state">Loading dentist directory…</p> : doctors.length === 0 ? <p className="management-state">No dentists found.</p> :
        <table><thead><tr><th>Dentist</th><th>License</th><th>Specialization</th><th>Phone</th><th>Role</th></tr></thead>
          <tbody>{doctors.map((doctor) => <tr key={doctor.id}>
            <td><div className="table-person"><div className="small-avatar">{doctor.full_name.split(' ').map((part) => part[0]).slice(-2).join('')}</div><strong>{doctor.full_name}</strong></div></td>
            <td><code>{doctor.license_number}</code></td><td>{doctor.specialization || '—'}</td><td>{doctor.phone || '—'}</td><td><span className="pill">{doctor.role}</span></td>
          </tr>)}</tbody>
        </table>}
    </div>
  </section>;
}

function Overview({ appointments, patients, setSection }) { return <>
  <section className="hero-band"><div><span className="eyebrow warm">TODAY AT A GLANCE</span><h2>Care that keeps moving.</h2><p>Your clinic is ready for a focused day. Three appointments are on deck.</p></div><button className="primary-button" onClick={() => setSection('Appointments')}><CalendarDays size={17} /> View schedule</button></section>
  <section className="metric-grid"><Metric label="Today's appointments" value="12" detail="3 waiting now" accent="blue" icon={CalendarDays} /><Metric label="Active patients" value="248" detail="+18 this month" accent="sage" icon={Users} /><Metric label="Outstanding balance" value="₫42.8m" detail="7 payment plans" accent="gold" icon={CircleDollarSign} /><Metric label="Care plans" value="36" detail="8 need review" accent="coral" icon={ClipboardPlus} /></section>
  <div className="content-grid"><section className="panel schedule-panel"><div className="panel-heading"><div><span className="eyebrow">APPOINTMENTS</span><h3>Today’s schedule</h3></div><button className="text-button" onClick={() => setSection('Appointments')}>View calendar <span>→</span></button></div><div className="appointment-list">{appointments.map((item) => <AppointmentRow key={item.id} item={item} />)}</div></section><section className="panel focus-panel"><div className="panel-heading"><div><span className="eyebrow">CLINIC FOCUS</span><h3>At a glance</h3></div><ShieldCheck size={19} color="#1d6857" /></div><div className="focus-stat"><span className="focus-icon green"><UserRound size={18} /></span><div><strong>{patients.length} patient records</strong><span>Digitized and searchable</span></div></div><div className="focus-stat"><span className="focus-icon peach"><Stethoscope size={18} /></span><div><strong>2 care alerts</strong><span>Need dentist review</span></div></div><div className="alert-box"><strong>Medication check</strong><p>One prescription needs allergy confirmation before signing.</p><button onClick={() => setSection('Patients')}>Review record →</button></div></section></div>
</>; }
function Metric({ label, value, detail, accent, icon: Icon }) { return <div className={`metric-card ${accent}`}><div className="metric-icon"><Icon size={18} /></div><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>; }
function appointmentDate(value) {
  if (!value) return 'Not provided';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function appointmentStatus(status = '') {
  const normalized = status.toLowerCase();
  const labels = { pending: 'Pending', confirmed: 'Confirmed', completed: 'Completed', cancelled: 'Cancelled' };
  const classes = { pending: 'scheduled', confirmed: 'confirmed', completed: 'paid', cancelled: 'cancelled' };
  return { label: labels[normalized] || status || 'Unknown', className: classes[normalized] || 'scheduled' };
}

function AppointmentRow({ item, onSelect }) {
  const initials = (item.patient_name || 'Patient').split(' ').map((part) => part[0]).slice(-2).join('');
  const status = appointmentStatus(item.status);
  return <div className="appointment-row">
    <div className="time">{appointmentDate(item.appointment_date)}</div>
    <div className="appointment-avatar">{initials}</div>
    <div className="appointment-info"><strong>{item.patient_name || 'Patient information unavailable'}</strong><span>{item.service_name || 'Service not specified'} · {item.dentist_name || 'Dentist not specified'}</span></div>
    <span className={`status ${status.className}`}>{status.label}</span>
    {onSelect && <button className="text-button appointment-view" onClick={() => onSelect(item.id)}>View details</button>}
  </div>;
}
function Patients({ patients, query, setQuery }) { return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">PATIENT DIRECTORY</span><h2>Patient records</h2></div><button className="primary-button"><UserRound size={17} /> New patient</button></div><div className="search-field"><Search size={17} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search name, patient code or phone" /></div><div className="panel table-panel"><table><thead><tr><th>Patient</th><th>Code</th><th>Phone</th><th>Dental profile</th><th>Allergy note</th></tr></thead><tbody>{patients.map((p) => <tr key={p.id}><td><div className="table-person"><div className="small-avatar">{p.full_name.split(' ').map((v) => v[0]).slice(-2).join('')}</div><strong>{p.full_name}</strong></div></td><td><code>{p.patient_code}</code></td><td>{p.phone || '—'}</td><td><span className="pill">{p.dentition_type === 'CHILD' ? '20 teeth · child' : '32 teeth · adult'}</span></td><td>{p.allergies || 'No known allergies'}</td></tr>)}</tbody></table></div></section>; }
function Appointments({ appointments, loading, error, tokens, onTokensChanged, onAppointmentCreated, onAppointmentUpdated, onAppointmentsReloaded }) {
  const [selectedId, setSelectedId] = useState(null);
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState('');
  const [bookingOpen, setBookingOpen] = useState(false);
  const [booking, setBooking] = useState({ patient: '', doctor: '', service: '', appointment_date: '', notes: '' });
  const [services, setServices] = useState([]);
  const [servicesLoading, setServicesLoading] = useState(false);
  const [servicesError, setServicesError] = useState('');
  const [bookingError, setBookingError] = useState('');
  const [bookingSuccess, setBookingSuccess] = useState('');
  const [bookingSaving, setBookingSaving] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  const [cancellationError, setCancellationError] = useState('');
  const [cancellationSuccess, setCancellationSuccess] = useState('');
  const [medicalRecordOpen, setMedicalRecordOpen] = useState(false);
  const [medicalRecord, setMedicalRecord] = useState(null);
  const [medicalRecordLoading, setMedicalRecordLoading] = useState(false);
  const [medicalRecordError, setMedicalRecordError] = useState('');
  const [medicalRecordMissing, setMedicalRecordMissing] = useState(false);
  const [medicalRecordSaving, setMedicalRecordSaving] = useState(false);
  const [medicalRecordUpdating, setMedicalRecordUpdating] = useState(false);
  const [medicalRecordEditing, setMedicalRecordEditing] = useState(false);
  const [medicalRecordCreated, setMedicalRecordCreated] = useState(false);
  const [medicalRecordForm, setMedicalRecordForm] = useState({ diagnosis: '', treatment_plan: '', prescription: '', notes: '' });

  useEffect(() => {
    if (selectedId === null) {
      setSelectedAppointment(null);
      setDetailError('');
      return undefined;
    }
    let active = true;
    setDetailLoading(true);
    setDetailError('');
    apiRequest(`/appointments/${selectedId}/`, { tokens, onTokens: onTokensChanged })
      .then((appointment) => { if (active) setSelectedAppointment(appointment); })
      .catch((requestError) => {
        if (!active) return;
        setDetailError(requestError.status === 404 ? 'This appointment was not found.' : requestError.message);
      })
      .finally(() => { if (active) setDetailLoading(false); });
    return () => { active = false; };
  }, [selectedId, tokens, onTokensChanged]);

  useEffect(() => {
    if (!bookingOpen) return undefined;
    let active = true;
    setServicesLoading(true);
    setServicesError('');
    apiRequest('/services/', { tokens, onTokens: onTokensChanged, apiBase: CLINIC_API })
      .then((data) => { if (active) setServices(data.filter((service) => service.is_active)); })
      .catch((requestError) => { if (active) setServicesError(requestError.message); })
      .finally(() => { if (active) setServicesLoading(false); });
    return () => { active = false; };
  }, [bookingOpen, tokens, onTokensChanged]);

  async function submitBooking(event) {
    event.preventDefault();
    setBookingSaving(true);
    setBookingError('');
    setBookingSuccess('');
    try {
      const created = await apiRequest('/appointments/', {
        tokens,
        onTokens: onTokensChanged,
        method: 'POST',
        body: {
          patient: Number(booking.patient),
          doctor: Number(booking.doctor),
          service: Number(booking.service),
          appointment_date: new Date(booking.appointment_date).toISOString(),
          notes: booking.notes.trim()
        }
      });
      onAppointmentCreated(created);
      setBookingOpen(false);
      setBooking({ patient: '', doctor: '', service: '', appointment_date: '', notes: '' });
      setBookingSuccess(`Appointment #${created.id} was booked successfully.`);
    } catch (requestError) {
      setBookingError(requestError.message || 'Could not reach the appointment service. Please try again.');
    } finally {
      setBookingSaving(false);
    }
  }

  async function reloadAppointment(appointmentId) {
    try {
      const refreshed = await apiRequest(`/appointments/${appointmentId}/`, { tokens, onTokens: onTokensChanged });
      setSelectedAppointment(refreshed);
      onAppointmentUpdated(refreshed);
      return refreshed;
    } catch (requestError) {
      if (requestError.status === 404) {
        const refreshedList = await apiRequest('/appointments/', { tokens, onTokens: onTokensChanged });
        onAppointmentsReloaded(refreshedList);
        setSelectedAppointment(null);
        setDetailError('This appointment was not found. The list has been refreshed.');
      }
      throw requestError;
    }
  }

  async function cancelAppointment(appointment) {
    const patientName = appointment.patient_name || 'this patient';
    const confirmed = window.confirm(`Cancel appointment #${appointment.id} for ${patientName}? Its status will change to Cancelled.`);
    if (!confirmed) return;

    setCancelling(true);
    setCancellationError('');
    setCancellationSuccess('');
    try {
      const cancelled = await apiRequest(`/appointments/${appointment.id}/cancel/`, {
        tokens,
        onTokens: onTokensChanged,
        method: 'POST'
      });
      setSelectedAppointment(cancelled);
      onAppointmentUpdated(cancelled);
      setCancellationSuccess(`Appointment #${cancelled.id} was cancelled.`);
    } catch (requestError) {
      setCancellationError(requestError.message || 'Could not cancel this appointment. Please try again.');
      if (requestError.status === 404 || requestError.status === 400) {
        try {
          await reloadAppointment(appointment.id);
        } catch {
          // The cancellation error remains visible while the list or detail refreshes.
        }
      }
    } finally {
      setCancelling(false);
    }
  }

  async function openMedicalRecord() {
    setMedicalRecordOpen(true);
    setMedicalRecord(null);
    setMedicalRecordError('');
    setMedicalRecordMissing(false);
    setMedicalRecordCreated(false);
    setMedicalRecordEditing(false);
    setMedicalRecordLoading(true);
    try {
      const record = await apiRequest(`/appointments/${selectedId}/medical-record/`, { tokens, onTokens: onTokensChanged });
      setMedicalRecord(record);
    } catch (requestError) {
      if (requestError.code === 'medical_record_not_found') {
        setMedicalRecordError('This appointment does not have a medical record yet.');
        setMedicalRecordMissing(true);
      } else if (requestError.status === 403) {
        setMedicalRecordError('You do not have permission to view this medical record.');
      } else if (requestError.status === 404) {
        setMedicalRecordError('The appointment or medical record could not be found.');
      } else {
        setMedicalRecordError(requestError.message || 'Could not load this medical record. Please try again.');
      }
    } finally {
      setMedicalRecordLoading(false);
    }
  }

  async function submitMedicalRecord(event) {
    event.preventDefault();
    setMedicalRecordSaving(true);
    setMedicalRecordError('');
    setMedicalRecordCreated(false);
    try {
      const created = await apiRequest(`/appointments/${selectedId}/medical-record/`, {
        tokens,
        onTokens: onTokensChanged,
        method: 'POST',
        body: {
          diagnosis: medicalRecordForm.diagnosis.trim(),
          treatment_plan: medicalRecordForm.treatment_plan.trim(),
          prescription: medicalRecordForm.prescription.trim(),
          notes: medicalRecordForm.notes.trim()
        }
      });
      setMedicalRecord(created);
      setMedicalRecordMissing(false);
      setMedicalRecordForm({ diagnosis: '', treatment_plan: '', prescription: '', notes: '' });
      setMedicalRecordCreated(true);
    } catch (requestError) {
      if (requestError.code === 'medical_record_exists') {
        setMedicalRecordError('A record already exists. Loading the existing record…');
        try {
          const existing = await apiRequest(`/appointments/${selectedId}/medical-record/`, { tokens, onTokens: onTokensChanged });
          setMedicalRecord(existing);
          setMedicalRecordMissing(false);
        } catch (loadError) {
          setMedicalRecordError(loadError.message || requestError.message);
        }
      } else {
        setMedicalRecordError(requestError.message || 'Could not create the medical record. Please try again.');
      }
    } finally {
      setMedicalRecordSaving(false);
    }
  }

  function beginMedicalRecordEdit() {
    setMedicalRecordForm({
      diagnosis: medicalRecord.diagnosis || '',
      treatment_plan: medicalRecord.treatment_plan || '',
      prescription: medicalRecord.prescription || '',
      notes: medicalRecord.notes || ''
    });
    setMedicalRecordError('');
    setMedicalRecordCreated(false);
    setMedicalRecordEditing(true);
  }

  async function submitMedicalRecordUpdate(event) {
    event.preventDefault();
    setMedicalRecordUpdating(true);
    setMedicalRecordError('');
    setMedicalRecordCreated(false);
    try {
      const updated = await apiRequest(`/appointments/${selectedId}/medical-record/`, {
        tokens,
        onTokens: onTokensChanged,
        method: 'PATCH',
        body: {
          diagnosis: medicalRecordForm.diagnosis.trim(),
          treatment_plan: medicalRecordForm.treatment_plan.trim(),
          prescription: medicalRecordForm.prescription.trim(),
          notes: medicalRecordForm.notes.trim()
        }
      });
      setMedicalRecord(updated);
      setMedicalRecordEditing(false);
      setMedicalRecordCreated(true);
    } catch (requestError) {
      setMedicalRecordError(requestError.message || 'Could not update the medical record. Please try again.');
    } finally {
      setMedicalRecordUpdating(false);
    }
  }

  if (selectedId !== null && medicalRecordOpen) {
    return <section className="page-section appointment-page">
      <div className="section-toolbar"><div><span className="eyebrow">MEDICAL RECORD</span><h2>Appointment #{selectedId}</h2></div><button className="secondary-button" onClick={() => setMedicalRecordOpen(false)}><ArrowLeft size={16} /> Back to appointment</button></div>
      {medicalRecordLoading && <div className="panel management-state" role="status">Loading medical record…</div>}
      {medicalRecordError && <div className="api-error" role="alert">{medicalRecordError}</div>}
      {medicalRecordCreated && <div className="form-success" role="status">Medical record saved successfully.</div>}
      {medicalRecord && !medicalRecordLoading && !medicalRecordEditing && <div className="panel medical-record-view">
        <div className="medical-record-patient"><span className="eyebrow">PATIENT</span><h3>{medicalRecord.patient_name || 'Patient information unavailable'}</h3><span>{medicalRecord.patient_code || 'Patient code unavailable'}</span></div>
        {selectedAppointment?.can_open_medical_record && <div className="form-actions"><button className="secondary-button" type="button" onClick={beginMedicalRecordEdit}>Edit medical record</button></div>}
        <dl className="appointment-detail-grid medical-record-grid">
          <div><dt>Diagnosis</dt><dd>{medicalRecord.diagnosis || 'No diagnosis recorded.'}</dd></div>
          <div><dt>Treatment plan</dt><dd>{medicalRecord.treatment_plan || 'No treatment plan recorded.'}</dd></div>
          <div><dt>Prescription</dt><dd>{medicalRecord.prescription || 'No prescription recorded.'}</dd></div>
          <div><dt>Clinical notes</dt><dd>{medicalRecord.notes || 'No clinical notes recorded.'}</dd></div>
          <div><dt>Record created</dt><dd>{appointmentDate(medicalRecord.created_at)}</dd></div>
        </dl>
      </div>}
      {medicalRecord && medicalRecordEditing && <form className="panel management-form medical-record-form" onSubmit={submitMedicalRecordUpdate}>
        <h3>Update examination record</h3>
        <label>Diagnosis <span aria-hidden="true">*</span><textarea required value={medicalRecordForm.diagnosis} onChange={(event) => setMedicalRecordForm({ ...medicalRecordForm, diagnosis: event.target.value })} /></label>
        <label>Treatment plan <span aria-hidden="true">*</span><textarea required value={medicalRecordForm.treatment_plan} onChange={(event) => setMedicalRecordForm({ ...medicalRecordForm, treatment_plan: event.target.value })} /></label>
        <label>Prescription<textarea value={medicalRecordForm.prescription} onChange={(event) => setMedicalRecordForm({ ...medicalRecordForm, prescription: event.target.value })} /></label>
        <label>Clinical notes<textarea value={medicalRecordForm.notes} onChange={(event) => setMedicalRecordForm({ ...medicalRecordForm, notes: event.target.value })} /></label>
        <div className="form-actions"><button className="primary-button" type="submit" disabled={medicalRecordUpdating}>{medicalRecordUpdating ? 'Saving…' : 'Save changes'}</button><button className="secondary-button" type="button" disabled={medicalRecordUpdating} onClick={() => setMedicalRecordEditing(false)}>Cancel</button></div>
      </form>}
      {medicalRecordMissing && selectedAppointment?.can_open_medical_record && <form className="panel management-form medical-record-form" onSubmit={submitMedicalRecord}>
        <h3>Create examination record</h3>
        <p className="booking-hint">Appointment #{selectedAppointment.id} · {selectedAppointment.patient_name || 'Patient information unavailable'} · {appointmentDate(selectedAppointment.appointment_date)}</p>
        <label>Diagnosis <span aria-hidden="true">*</span><textarea required value={medicalRecordForm.diagnosis} onChange={(event) => setMedicalRecordForm({ ...medicalRecordForm, diagnosis: event.target.value })} /></label>
        <label>Treatment plan <span aria-hidden="true">*</span><textarea required value={medicalRecordForm.treatment_plan} onChange={(event) => setMedicalRecordForm({ ...medicalRecordForm, treatment_plan: event.target.value })} /></label>
        <label>Prescription<textarea value={medicalRecordForm.prescription} onChange={(event) => setMedicalRecordForm({ ...medicalRecordForm, prescription: event.target.value })} /></label>
        <label>Clinical notes<textarea value={medicalRecordForm.notes} onChange={(event) => setMedicalRecordForm({ ...medicalRecordForm, notes: event.target.value })} /></label>
        <div className="form-actions"><button className="primary-button" type="submit" disabled={medicalRecordSaving}>{medicalRecordSaving ? 'Saving…' : 'Create medical record'}</button></div>
      </form>}
    </section>;
  }

  if (selectedId !== null) {
    const appointment = selectedAppointment;
    const status = appointmentStatus(appointment?.status);
    return <section className="page-section appointment-page">
      <div className="section-toolbar"><div><span className="eyebrow">APPOINTMENT DETAILS</span><h2>Appointment #{selectedId}</h2></div><button className="secondary-button" onClick={() => setSelectedId(null)}><ArrowLeft size={16} /> Back to list</button></div>
      {detailLoading && <div className="panel management-state" role="status">Loading appointment details…</div>}
      {detailError && <div className="api-error" role="alert">{detailError}</div>}
      {appointment && !detailLoading && <div className="panel appointment-detail">
        <div className="appointment-detail-heading"><div><span className="eyebrow">PATIENT</span><h3>{appointment.patient_name || 'Patient information unavailable'}</h3><span>{appointment.patient_code || 'Patient code unavailable'}</span></div><span className={`status ${status.className}`}>{status.label}</span></div>
        {cancellationSuccess && <div className="form-success" role="status">{cancellationSuccess}</div>}
        {cancellationError && <div className="form-error" role="alert">{cancellationError}</div>}
        {appointment.can_open_medical_record && <div className="form-actions"><button className="secondary-button" type="button" onClick={openMedicalRecord}>Open medical record</button></div>}
        {['Pending', 'Confirmed'].includes(appointment.status) && <div className="form-actions"><button className="secondary-button danger-button" type="button" disabled={cancelling} onClick={() => cancelAppointment(appointment)}>{cancelling ? 'Cancelling…' : 'Cancel appointment'}</button></div>}
        <dl className="appointment-detail-grid">
          <div><dt>Appointment ID</dt><dd>{appointment.id}</dd></div>
          <div><dt>Dentist</dt><dd>{appointment.dentist_name || 'Not specified'}</dd></div>
          <div><dt>Date and time</dt><dd>{appointmentDate(appointment.appointment_date)}</dd></div>
          <div><dt>Service / reason</dt><dd>{appointment.service_name || 'Not specified'}</dd></div>
          <div className="appointment-detail-notes"><dt>Notes</dt><dd>{appointment.notes || 'No notes recorded.'}</dd></div>
        </dl>
      </div>}
    </section>;
  }

  return <section className="page-section appointment-page">
    <div className="section-toolbar"><div><span className="eyebrow">APPOINTMENTS</span><h2>Appointment schedule</h2></div><button className="primary-button" onClick={() => { setBookingOpen(true); setBookingError(''); setBookingSuccess(''); }}><CalendarDays size={17} /> Book appointment</button></div>
    {bookingSuccess && <div className="form-success" role="status">{bookingSuccess}</div>}
    {error && <div className="api-error" role="alert">{error}</div>}
    {bookingOpen && <form className="panel management-form appointment-booking-form" onSubmit={submitBooking}>
      <h3>Book an appointment</h3>
      <p className="booking-hint">Enter the patient and dentist record IDs. The server checks that both records exist and that the dentist is working at the requested time.</p>
      <div className="form-grid">
        <label>Patient ID<input required type="number" min="1" step="1" value={booking.patient} onChange={(event) => setBooking({ ...booking, patient: event.target.value })} /></label>
        <label>Dentist ID<input required type="number" min="1" step="1" value={booking.doctor} onChange={(event) => setBooking({ ...booking, doctor: event.target.value })} /></label>
        <label>Service<select required value={booking.service} onChange={(event) => setBooking({ ...booking, service: event.target.value })} disabled={servicesLoading || services.length === 0}><option value="">{servicesLoading ? 'Loading services…' : 'Select a service'}</option>{services.map((service) => <option key={service.id} value={service.id}>{service.name} · {service.duration_minutes} min</option>)}</select></label>
        <label>Date and time<input required type="datetime-local" value={booking.appointment_date} onChange={(event) => setBooking({ ...booking, appointment_date: event.target.value })} /></label>
        <label className="form-wide">Reason / notes<textarea value={booking.notes} onChange={(event) => setBooking({ ...booking, notes: event.target.value })} /></label>
      </div>
      {servicesError && <div className="form-error" role="alert">Could not load services: {servicesError}</div>}
      {bookingError && <div className="form-error" role="alert">{bookingError}</div>}
      <div className="form-actions"><button className="primary-button" type="submit" disabled={bookingSaving || servicesLoading || services.length === 0}>{bookingSaving ? 'Booking…' : 'Confirm booking'}</button><button className="secondary-button" type="button" disabled={bookingSaving} onClick={() => setBookingOpen(false)}>Close</button></div>
    </form>}
    <div className="panel schedule-panel">
      {loading ? <p className="management-state" role="status">Loading appointments…</p> : appointments.length === 0 ? <p className="management-state">No appointments found.</p> :
        <div className="appointment-list">{appointments.map((item) => <AppointmentRow item={item} key={item.id} onSelect={(id) => { setMedicalRecordOpen(false); setMedicalRecordForm({ diagnosis: '', treatment_plan: '', prescription: '', notes: '' }); setMedicalRecordMissing(false); setSelectedId(id); }} />)}</div>}
    </div>
  </section>;
}
function ToothChart({ dentition, setDentition, selectedTooth, setSelectedTooth }) { const teeth = dentition === 'ADULT' ? teethAdult : teethChild; return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">CLINICAL RECORD</span><h2>Interactive tooth chart</h2></div><div className="segmented"><button className={dentition === 'ADULT' ? 'selected' : ''} onClick={() => setDentition('ADULT')}>Adult · 32</button><button className={dentition === 'CHILD' ? 'selected' : ''} onClick={() => setDentition('CHILD')}>Child · 20</button></div></div><div className="chart-layout"><div className="panel tooth-panel"><div className="chart-header"><div><strong>Nguyen Minh Anh</strong><span>DMS-0001 · {dentition === 'ADULT' ? 'Permanent dentition' : 'Primary dentition'}</span></div><span className="status confirmed">In treatment</span></div><div className="mouth-label">UPPER ARCH</div><div className={`teeth-grid ${dentition.toLowerCase()}`}>{teeth.slice(0, Math.ceil(teeth.length / 2)).map((tooth) => <Tooth key={tooth.id} tooth={tooth} selected={selectedTooth === tooth.id} onClick={() => setSelectedTooth(tooth.id)} />)}</div><div className="mouth-line" /><div className={`teeth-grid lower ${dentition.toLowerCase()}`}>{teeth.slice(Math.ceil(teeth.length / 2)).reverse().map((tooth) => <Tooth key={tooth.id} tooth={tooth} selected={selectedTooth === tooth.id} onClick={() => setSelectedTooth(tooth.id)} />)}</div><div className="mouth-label lower-label">LOWER ARCH</div><div className="chart-legend"><span><i className="dot healthy" />Healthy</span><span><i className="dot care" />Needs care</span><span><i className="dot monitor" />Monitor</span></div></div><aside className="panel tooth-detail"><span className="eyebrow">SELECTED TOOTH</span>{selectedTooth ? <><div className="tooth-number">{teeth.find((tooth) => tooth.id === selectedTooth)?.code}</div><h3>Clinical condition</h3><p>Update this tooth’s condition and add a treatment note for the patient record.</p><select defaultValue="Healthy"><option>Healthy</option><option>Needs care</option><option>Monitor</option><option>Restored</option></select><textarea placeholder="Add a clinical note..." /><button className="primary-button full">Save condition</button></> : <div className="empty-detail"><Stethoscope size={28} /><p>Select a tooth to inspect its clinical record.</p></div>}</aside></div></section>; }
function Tooth({ tooth, selected, onClick }) { return <button onClick={onClick} className={`tooth ${tooth.state.toLowerCase().replace(' ', '-')} ${selected ? 'selected' : ''}`}><span>{tooth.code.slice(1)}</span><div className="tooth-shape" /></button>; }
function Billing({ patients }) { return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">FINANCE</span><h2>Billing & installment plans</h2></div><button className="primary-button"><CircleDollarSign size={17} /> New invoice</button></div><div className="metric-grid compact"><Metric label="Outstanding" value="₫42.8m" detail="Across 18 invoices" accent="gold" icon={CircleDollarSign} /><Metric label="Due this week" value="₫8.4m" detail="6 installments" accent="coral" icon={CalendarDays} /><Metric label="Collected today" value="₫5.2m" detail="11 payments" accent="sage" icon={ShieldCheck} /></div><div className="panel table-panel"><table><thead><tr><th>Invoice</th><th>Patient</th><th>Total</th><th>Paid</th><th>Status</th></tr></thead><tbody>{patients.slice(0, 3).map((p, i) => <tr key={p.id}><td><code>INV-000{i + 1}</code></td><td><strong>{p.full_name}</strong></td><td>₫{['3,500,000', '1,200,000', '850,000'][i]}</td><td>₫{['1,500,000', '1,200,000', '350,000'][i]}</td><td><span className={`status ${i === 1 ? 'paid' : 'scheduled'}`}>{i === 1 ? 'Paid' : 'Installment'}</span></td></tr>)}</tbody></table></div></section>; }
function Radiographs() { return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">IMAGING</span><h2>Radiograph gallery</h2></div><button className="primary-button"><FileImage size={17} /> Upload image</button></div><div className="upload-placeholder"><FileImage size={30} /><h3>No radiographs uploaded yet</h3><p>Attach X-ray images to a patient record from the clinical visit.</p><button className="secondary-button">Choose file</button></div></section>; }

createRoot(document.getElementById('root')).render(<App />);
