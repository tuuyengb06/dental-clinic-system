import React, { useCallback, useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, CalendarDays, ChevronDown, CircleDollarSign, ClipboardPlus, FileImage, LayoutDashboard, Menu, MessageCircle, Pencil, Plus, Search, Send, ShieldCheck, Stethoscope, Trash2, UserRound, Users, X } from 'lucide-react';
import './styles.css';
import './app.css';

const API = import.meta.env.DEV ? '/api/v1' : (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1');
const AI_CHAT_API = API.replace(/\/v1\/?$/, '/ai/chat');
const teethAdult = Array.from({ length: 32 }, (_, i) => ({ id: i + 1, code: `A${String(i + 1).padStart(2, '0')}`, state: i === 6 || i === 18 ? 'Needs care' : 'Healthy' }));
const teethChild = Array.from({ length: 20 }, (_, i) => ({ id: i + 1, code: `C${String(i + 1).padStart(2, '0')}`, state: i === 3 ? 'Monitor' : 'Healthy' }));
const navigationByRole = {
  ADMIN: [
    ['Overview', LayoutDashboard], ['Patients', Users], ['Appointments', CalendarDays], ['Tooth chart', Stethoscope],
    ['Billing', CircleDollarSign], ['Radiographs', FileImage], ['Services', ClipboardPlus], ['Doctors', UserRound], ['Reception', UserRound]
  ],
  DENTIST: [
    ['Overview', LayoutDashboard], ['Patients', Users], ['Appointments', CalendarDays],
    ['Tooth chart', Stethoscope], ['Radiographs', FileImage], ['EMR', ClipboardPlus]
  ],
  RECEPTIONIST: [
    ['Overview', LayoutDashboard], ['Reception', UserRound], ['Appointments', CalendarDays], ['Patients', Users], ['Billing', CircleDollarSign]
  ]
};

const TOKEN_STORAGE_KEY = 'dms.auth.tokens';

async function apiRequest(path, { tokens, onTokens, method = 'GET', body } = {}) {
  const send = (accessToken) => fetch(`${API}${path}`, {
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
    throw new Error(detail);
  }
  return payload;
}

function App() {
  const [section, setSection] = useState('Overview');
  const [patients, setPatients] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [services, setServices] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [teeth, setTeeth] = useState([]);
  const [medicalRecords, setMedicalRecords] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [invoiceSources, setInvoiceSources] = useState([]);
  const [tokens, setTokens] = useState(null);
  const [profile, setProfile] = useState(null);
  const [authReady, setAuthReady] = useState(false);
  const [authError, setAuthError] = useState('');
  const [query, setQuery] = useState('');
  const [dentition, setDentition] = useState('ADULT');
  const [selectedTooth, setSelectedTooth] = useState(null);
  const [apiLive, setApiLive] = useState(false);
  const [apiError, setApiError] = useState('');
  const [apiLoading, setApiLoading] = useState(false);
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
    setApiLoading(true);
    const currentRole = String(profile.role || '').toUpperCase();
    const recordRequest = currentRole === 'DENTIST' || currentRole === 'ADMIN'
      ? apiRequest('/medical-records/', { tokens, onTokens: updateTokens })
      : Promise.resolve([]);
    const billingRequest = currentRole === 'ADMIN' || currentRole === 'RECEPTIONIST'
      ? Promise.all([
        apiRequest('/invoices/', { tokens, onTokens: updateTokens }),
        apiRequest('/invoices/available-records/', { tokens, onTokens: updateTokens })
      ])
      : Promise.resolve([[], []]);
    Promise.all([
      apiRequest('/patients/', { tokens, onTokens: updateTokens }),
      apiRequest('/appointments/', { tokens, onTokens: updateTokens }),
      apiRequest('/doctors/', { tokens, onTokens: updateTokens }),
      apiRequest('/services/', { tokens, onTokens: updateTokens }),
      apiRequest('/schedules/', { tokens, onTokens: updateTokens }),
      apiRequest('/teeth/', { tokens, onTokens: updateTokens }),
      recordRequest,
      billingRequest
    ]).then(([patientData, appointmentData, doctorData, serviceData, scheduleData, toothData, recordData, billingData]) => {
      setPatients(patientData);
      setAppointments(appointmentData);
      setDoctors(doctorData);
      setServices(serviceData.filter((service) => service.is_active));
      setSchedules(scheduleData);
      setTeeth(toothData);
      setMedicalRecords(recordData);
      setInvoices(billingData[0]);
      setInvoiceSources(billingData[1]);
      setApiLive(true);
      setApiError('');
    }).catch((error) => {
      setApiLive(false);
      setApiError(error.message);
    }).finally(() => {
      setApiLoading(false);
    });
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

  async function createPatient(patient) {
    const createdPatient = await apiRequest('/patients/', {
      tokens,
      onTokens: updateTokens,
      method: 'POST',
      body: patient
    });
    setPatients((currentPatients) => [createdPatient, ...currentPatients]);
    return createdPatient;
  }

  async function createAppointment(appointment) {
    const created = await apiRequest('/appointments/', {
      tokens, onTokens: updateTokens, method: 'POST', body: appointment
    });
    setAppointments((current) => [...current, created]);
    return created;
  }

  async function cancelAppointment(appointmentId) {
    const cancelled = await apiRequest(`/appointments/${appointmentId}/cancel/`, {
      tokens, onTokens: updateTokens, method: 'POST'
    });
    setAppointments((current) => current.map((item) => item.id === cancelled.id ? cancelled : item));
    return cancelled;
  }

  async function createSchedule(schedule) {
    const created = await apiRequest('/schedules/', {
      tokens, onTokens: updateTokens, method: 'POST', body: schedule
    });
    setSchedules((current) => [...current, created]);
    return created;
  }

  async function saveMedicalRecord(record, id) {
    const saved = await apiRequest(id ? `/medical-records/${id}/` : '/medical-records/', {
      tokens,
      onTokens: updateTokens,
      method: id ? 'PATCH' : 'POST',
      body: record
    });
    setMedicalRecords((current) => id
      ? current.map((item) => item.id === id ? saved : item)
      : [...current, saved]);
    return saved;
  }

  async function createInvoice(invoice) {
    const created = await apiRequest('/invoices/', {
      tokens, onTokens: updateTokens, method: 'POST', body: invoice
    });
    setInvoices((current) => [created, ...current]);
    setInvoiceSources((current) => current.filter((record) => record.id !== created.medical_record));
    return created;
  }

  async function payInvoiceCash(invoiceId) {
    const paid = await apiRequest(`/invoices/${invoiceId}/pay-cash/`, {
      tokens, onTokens: updateTokens, method: 'POST', body: { method: 'CASH' }
    });
    setInvoices((current) => current.map((invoice) => invoice.id === paid.id ? paid : invoice));
    return paid;
  }

  async function createInvoiceQr(invoiceId) {
    const result = await apiRequest(`/invoices/${invoiceId}/pay-qr/`, {
      tokens, onTokens: updateTokens, method: 'POST'
    });
    setInvoices((current) => current.map((invoice) => invoice.id === result.invoice.id ? result.invoice : invoice));
    return result;
  }

  async function reconcileInvoiceQr(invoiceId, verification) {
    const invoice = await apiRequest(`/invoices/${invoiceId}/reconcile-qr/`, {
      tokens, onTokens: updateTokens, method: 'POST', body: verification
    });
    setInvoices((current) => current.map((item) => item.id === invoice.id ? invoice : item));
    return invoice;
  }

  async function cancelInvoiceQr(invoiceId) {
    const invoice = await apiRequest(`/invoices/${invoiceId}/cancel-qr/`, {
      tokens, onTokens: updateTokens, method: 'POST', body: { checked_no_payment: true }
    });
    setInvoices((current) => current.map((item) => item.id === invoice.id ? invoice : item));
    return invoice;
  }

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

  if (!authReady) return <><div className="auth-loading">Checking your session…</div><ChatWidget /></>;
  if (!profile) return <><LoginPage onLogin={login} initialError={authError} /><ChatWidget /></>;

  const visiblePatients = patients.filter((patient) => `${patient.full_name} ${patient.patient_code} ${patient.phone}`.toLowerCase().includes(query.toLowerCase()));
  const role = String(profile.role || '').toUpperCase() === 'DOCTOR' ? 'DENTIST' : String(profile.role || '').toUpperCase();
  const nav = navigationByRole[role] || navigationByRole.RECEPTIONIST;
  return <div className="app-shell">
    <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
      <div className="brand"><div className="brand-mark">D</div><div><strong>DMS</strong><span>Dental management</span></div><button className="icon-button close-menu" onClick={() => setMobileOpen(false)}><X size={18} /></button></div>
      <div className="workspace"><span className="eyebrow">Workspace</span><button className="workspace-button">Lotus Dental Clinic <ChevronDown size={15} /></button></div>
      <nav aria-label="Main navigation">{nav.map(([name, Icon]) => <button key={name} className={section === name ? 'nav-item active' : 'nav-item'} aria-current={section === name ? 'page' : undefined} onClick={() => { setSection(name); setMobileOpen(false); }}><Icon size={18} /><span>{name}</span>{name === 'Appointments' && <b>3</b>}</button>)}</nav>
    </aside>
    <main className="main-content">
      <header className="topbar"><button className="icon-button menu-button" onClick={() => setMobileOpen(true)}><Menu size={20} /></button><div><span className="eyebrow">Tuesday, 08 September 2026</span><h1>{section === 'Overview' ? `Good morning, ${profile.display_name}` : section}</h1></div><div className="topbar-actions"><span className={`api-status ${apiLive ? 'live' : ''}`}><span />{apiLive ? 'Live API' : 'Connecting'}</span><button className="icon-button"><Activity size={19} /></button><div className="user-card"><div className="avatar">{profile.display_name.split(' ').map((part) => part[0]).slice(-2).join('')}</div><div><strong>{profile.display_name}</strong><span>{role}</span></div><button className="secondary-button" onClick={logout}>Log out</button></div></div></header>
      {apiError && section !== 'Appointments' && <div className="api-error" role="alert">{apiError}</div>}
      {section === 'Overview' && (role === 'ADMIN'
        ? <RevenueDashboard tokens={tokens} onTokensChanged={updateTokens} />
        : <Overview appointments={appointments} patients={patients} setSection={setSection} />)}
      {section === 'Patients' && <Patients patients={visiblePatients} query={query} setQuery={setQuery} onCreatePatient={createPatient} canCreate={role === 'ADMIN' || role === 'RECEPTIONIST'} />}
      {section === 'Reception' && (role === 'ADMIN' || role === 'RECEPTIONIST') && <Reception tokens={tokens} onTokensChanged={updateTokens} appointments={appointments} setSection={setSection} />}
      {section === 'Appointments' && <Appointments appointments={appointments} patients={patients} doctors={doctors} services={services} schedules={schedules} role={role} loading={apiLoading} loadError={apiError} onCreateAppointment={createAppointment} onCreateSchedule={createSchedule} onCancelAppointment={cancelAppointment} />}
      {section === 'EMR' && (role === 'DENTIST' || role === 'ADMIN') && <MedicalRecords appointments={appointments} patients={patients} services={services} teeth={teeth} records={medicalRecords} loading={apiLoading} loadError={apiError} onSave={saveMedicalRecord} />}
      {section === 'Tooth chart' && <ToothChart dentition={dentition} setDentition={setDentition} selectedTooth={selectedTooth} setSelectedTooth={setSelectedTooth} />}
      {section === 'Billing' && (role === 'ADMIN' || role === 'RECEPTIONIST') && <Billing invoices={invoices} records={invoiceSources} loading={apiLoading} onCreateInvoice={createInvoice} onPayCash={payInvoiceCash} onCreateQr={createInvoiceQr} onReconcileQr={reconcileInvoiceQr} onCancelQr={cancelInvoiceQr} />}
      {section === 'Radiographs' && <Radiographs />}
      {section === 'Services' && role === 'ADMIN' && <ServiceManagement tokens={tokens} onTokensChanged={updateTokens} />}
      {section === 'Doctors' && role === 'ADMIN' && <DoctorDirectory tokens={tokens} onTokensChanged={updateTokens} />}
    </main>
    <ChatWidget />
  </div>;
}

function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Xin chào! Bạn có thể hỏi giá dịch vụ hoặc giờ khám còn trống. Khi hỏi lịch, vui lòng ghi ngày và tên dịch vụ.'
    }
  ]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (open) messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, open]);

  async function sendQuestion(event) {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || loading) return;

    setQuestion('');
    setMessages((current) => [...current, { role: 'user', text: trimmedQuestion }].slice(-21));
    setLoading(true);
    try {
      const response = await fetch(AI_CHAT_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: trimmedQuestion })
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        const message = payload?.answer || payload?.detail || 'Hiện chatbot chưa trả lời được. Bạn vui lòng thử lại hoặc liên hệ lễ tân.';
        throw new Error(message);
      }
      setMessages((current) => [...current, { role: 'assistant', text: payload.answer }].slice(-21));
    } catch (error) {
      setMessages((current) => [
        ...current,
        { role: 'assistant', text: `${error.message || 'Không kết nối được chatbot.'} Nếu cần hỗ trợ gấp, vui lòng liên hệ lễ tân.` }
      ].slice(-21));
    } finally {
      setLoading(false);
    }
  }

  return <div className="chatbot-widget">
    {open && <section className="chatbot-panel" role="dialog" aria-modal="false" aria-labelledby="chatbot-title">
      <header className="chatbot-header">
        <div><strong id="chatbot-title">Tư vấn dịch vụ & lịch khám</strong><span>Dựa trên dữ liệu phòng khám</span></div>
        <button type="button" className="chatbot-close" aria-label="Đóng chatbot" onClick={() => setOpen(false)}><X size={18} /></button>
      </header>
      <div className="chatbot-scope-note">Chỉ tra cứu giá và lịch hiện có; không tư vấn y tế hoặc đặt lịch trong hội thoại.</div>
      <div className="chatbot-messages" aria-live="polite" aria-relevant="additions text">
        {messages.map((message, index) => <div key={`${index}-${message.role}`} className={`chatbot-message ${message.role}`}><p>{message.text}</p></div>)}
        {loading && <div className="chatbot-message assistant"><p role="status">Đang tra cứu…</p></div>}
        <div ref={messagesEndRef} />
      </div>
      <form className="chatbot-form" onSubmit={sendQuestion}>
        <label className="sr-only" htmlFor="chatbot-question">Câu hỏi</label>
        <input id="chatbot-question" maxLength={500} value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Hỏi giá hoặc lịch khám…" disabled={loading} />
        <button type="submit" aria-label="Gửi câu hỏi" disabled={loading || !question.trim()}><Send size={17} /></button>
      </form>
    </section>}
    <button type="button" className="chatbot-launcher" aria-label={open ? 'Đóng tư vấn' : 'Mở chatbot tư vấn'} aria-expanded={open} onClick={() => setOpen((current) => !current)}>
      {open ? <X size={21} /> : <MessageCircle size={21} />}
      <span>{open ? 'Đóng' : 'Tư vấn'}</span>
    </button>
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

function localDateInputValue(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatDashboardPeriod(period, groupBy) {
  if (groupBy === 'month') {
    const [year, month] = period.split('-');
    return `${month}/${year}`;
  }
  const [, month, day] = period.split('-');
  return `${day}/${month}`;
}

function RevenueDashboard({ tokens, onTokensChanged }) {
  const today = localDateInputValue(new Date());
  const [startDate, setStartDate] = useState(`${today.slice(0, 7)}-01`);
  const [endDate, setEndDate] = useState(today);
  const [requestedGroup, setRequestedGroup] = useState('auto');
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!startDate || !endDate) return undefined;
    if (endDate < startDate) {
      setDashboard(null);
      setError('Ngày kết thúc phải từ ngày bắt đầu trở đi.');
      return undefined;
    }

    let active = true;
    const query = new URLSearchParams({
      start_date: startDate,
      end_date: endDate,
      group_by: requestedGroup
    });
    setLoading(true);
    setError('');
    setDashboard(null);
    apiRequest(`/dashboard/analytics/?${query.toString()}`, { tokens, onTokens: onTokensChanged })
      .then((result) => {
        if (active) setDashboard(result);
      })
      .catch((requestError) => {
        if (active) setError(requestError.message || 'Không tải được thống kê. Vui lòng thử lại.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => { active = false; };
  }, [startDate, endDate, requestedGroup, tokens, onTokensChanged]);

  const revenue = Number(dashboard?.total_revenue || 0);
  const visits = Number(dashboard?.total_visits || 0);
  const series = dashboard?.series || [];

  return <section className="page-section management-page revenue-dashboard">
    <div className="section-toolbar">
      <div><span className="eyebrow">FINANCE & CLINICAL ACTIVITY</span><h2>Revenue and visits</h2></div>
      <span className="dashboard-timezone">Asia/Ho_Chi_Minh</span>
    </div>
    <section className="panel dashboard-filter-panel" aria-label="Statistics date filters">
      <label>From<input type="date" value={startDate} max={endDate || today} onChange={(event) => setStartDate(event.target.value)} /></label>
      <label>To<input type="date" value={endDate} min={startDate} max={today} onChange={(event) => setEndDate(event.target.value)} /></label>
      <label>Chart interval<select value={requestedGroup} onChange={(event) => setRequestedGroup(event.target.value)}>
        <option value="auto">Automatic</option>
        <option value="day">Daily</option>
        <option value="month">Monthly</option>
      </select></label>
      {dashboard && <p className="dashboard-filter-summary">{dashboard.group_by === 'day' ? 'Daily' : 'Monthly'} totals · both selected dates included</p>}
    </section>
    {error && <div className="form-error" role="alert">{error}</div>}
    {loading && <p className="management-state" role="status">Loading revenue and visit statistics…</p>}
    <section className="metric-grid dashboard-metrics" aria-label="Statistics summary" aria-busy={loading}>
      <Metric label="Revenue from paid invoices" value={`${revenue.toLocaleString('vi-VN', { maximumFractionDigits: 2 })} ₫`} detail="Paid invoice total, grouped by issue date" accent="sage" icon={CircleDollarSign} />
      <Metric label="Completed visits" value={visits.toLocaleString('vi-VN')} detail="Completed appointments, grouped by appointment date" accent="blue" icon={CalendarDays} />
    </section>
    {!loading && !error && dashboard && <>
      <TrendChart title="Revenue by period" series={series} valueKey="revenue" groupBy={dashboard.group_by} formatValue={(value) => `${Number(value).toLocaleString('vi-VN', { maximumFractionDigits: 2 })} ₫`} color="revenue" />
      <TrendChart title="Completed visits by period" series={series} valueKey="visits" groupBy={dashboard.group_by} formatValue={(value) => Number(value).toLocaleString('vi-VN')} color="visits" />
      <p className="dashboard-definition">Revenue counts each <code>PAID</code> invoice’s total once using its issue date; pending transfers and unpaid invoices are excluded. Visits count <code>Completed</code> appointments, not invoices. Empty dates/periods are shown as zero.</p>
    </>}
  </section>;
}

function TrendChart({ title, series, valueKey, groupBy, formatValue, color }) {
  const values = series.map((point) => Number(point[valueKey]));
  const maximum = Math.max(...values, 0);
  const labelEvery = series.length > 24 ? Math.ceil(series.length / 12) : 1;

  return <section className="panel dashboard-chart-panel">
    <div className="panel-heading"><div><span className="eyebrow">{valueKey === 'revenue' ? 'IN VND' : 'APPOINTMENTS'}</span><h3>{title}</h3></div></div>
    {!series.length ? <p className="management-state">No periods are available for this date range.</p> : maximum === 0
      ? <p className="dashboard-empty-chart">No {valueKey === 'revenue' ? 'revenue' : 'completed visits'} in this period.</p>
      : <div className="dashboard-chart-scroll"><div className="dashboard-bars" role="img" aria-label={`${title} from ${formatDashboardPeriod(series[0].period, groupBy)} to ${formatDashboardPeriod(series.at(-1).period, groupBy)}`}>
        {series.map((point, index) => {
          const value = Number(point[valueKey]);
          const height = maximum ? (value / maximum) * 100 : 0;
          return <div className="dashboard-bar-column" key={point.period} title={`${formatDashboardPeriod(point.period, groupBy)}: ${formatValue(value)}`}>
            <span className="dashboard-bar-value">{formatValue(value)}</span>
            <div className="dashboard-bar-track"><div className={`dashboard-bar ${color}`} style={{ height: `${height}%` }} /></div>
            {(index % labelEvery === 0 || index === series.length - 1) && <span className="dashboard-bar-label">{formatDashboardPeriod(point.period, groupBy)}</span>}
          </div>;
        })}
      </div></div>}
  </section>;
}

function AppointmentRow({ item, canCancel = false, onCancel, cancelling = false }) {
  const appointmentDate = item.appointment_date || item.start_at;
  const time = appointmentDate && appointmentDate.includes('T')
    ? new Date(appointmentDate).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    : appointmentDate;
  const status = String(item.status || '').toLowerCase();
  return <div className="appointment-row">
    <div className="time">{time}</div>
    <div className="appointment-avatar">{(item.patient_name || 'Patient').split(' ').map((part) => part[0]).slice(-2).join('')}</div>
    <div className="appointment-info"><strong>{item.patient_name}</strong><span>{item.service_name || item.type || 'Dental consultation'} · {item.dentist_name}</span></div>
    <span className={`status ${status === 'confirmed' ? 'confirmed' : status === 'completed' ? 'paid' : status === 'cancelled' ? 'inactive' : 'scheduled'}`}>{item.status}</span>
    {canCancel && ['pending', 'confirmed'].includes(status) && <button className="secondary-button cancel-appointment-button" type="button" disabled={cancelling} onClick={() => onCancel?.(item)}>{cancelling ? 'Cancelling…' : 'Cancel appointment'}</button>}
  </div>;
}
const emptyPatient = {
  patient_code: '',
  full_name: '',
  phone: '',
  date_of_birth: '',
  dentition_type: 'ADULT',
  medical_history: '',
  allergies: ''
};

function Patients({ patients, query, setQuery, onCreatePatient, canCreate }) {
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyPatient);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  async function savePatient(event) {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      const patient = await onCreatePatient({
        ...form,
        date_of_birth: form.date_of_birth || null
      });
      setSelectedPatient(patient);
      setForm(emptyPatient);
      setShowForm(false);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return <section className="page-section management-page">
    <div className="section-toolbar">
      <div><span className="eyebrow">PATIENT DIRECTORY</span><h2>Patient records</h2></div>
      {canCreate && <button className="primary-button" onClick={() => { setShowForm(!showForm); setError(''); }}>
        <UserRound size={17} /> {showForm ? 'Cancel' : 'New patient'}
      </button>}
    </div>
    {error && <div className="form-error" role="alert">{error}</div>}
    {showForm && <form className="panel management-form" onSubmit={savePatient}>
      <h3>New patient profile</h3>
      <div className="form-grid">
        <label>Patient code<input required maxLength="20" value={form.patient_code} onChange={(event) => setForm({ ...form, patient_code: event.target.value.trim().toUpperCase() })} /></label>
        <label>Full name<input required maxLength="160" value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} /></label>
        <label>Phone<input maxLength="30" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} /></label>
        <label>Date of birth<input type="date" value={form.date_of_birth} onChange={(event) => setForm({ ...form, date_of_birth: event.target.value })} /></label>
        <label>Dental profile<select value={form.dentition_type} onChange={(event) => setForm({ ...form, dentition_type: event.target.value })}><option value="ADULT">Adult · 32 teeth</option><option value="CHILD">Child · 20 teeth</option></select></label>
        <label>Allergies<textarea value={form.allergies} onChange={(event) => setForm({ ...form, allergies: event.target.value })} /></label>
        <label className="form-wide">Medical history<textarea value={form.medical_history} onChange={(event) => setForm({ ...form, medical_history: event.target.value })} /></label>
      </div>
      <div className="form-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Saving…' : 'Create patient'}</button></div>
    </form>}
    {selectedPatient && <section className="panel patient-profile">
      <div className="panel-heading"><div><span className="eyebrow">PATIENT PROFILE</span><h3>{selectedPatient.full_name}</h3></div><button className="secondary-button" onClick={() => setSelectedPatient(null)}>Close</button></div>
      <div className="patient-profile-grid">
        <div><span>Patient code</span><strong>{selectedPatient.patient_code}</strong></div>
        <div><span>Phone</span><strong>{selectedPatient.phone || '—'}</strong></div>
        <div><span>Date of birth</span><strong>{selectedPatient.date_of_birth || '—'}</strong></div>
        <div><span>Dental profile</span><strong>{selectedPatient.dentition_type === 'CHILD' ? 'Child · 20 teeth' : 'Adult · 32 teeth'}</strong></div>
        <div><span>Allergies</span><p>{selectedPatient.allergies || 'No known allergies recorded'}</p></div>
        <div><span>Medical history</span><p>{selectedPatient.medical_history || 'No medical history recorded'}</p></div>
      </div>
    </section>}
    <div className="search-field"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search name, patient code or phone" /></div>
    <div className="panel table-panel">
      {patients.length === 0 ? <p className="management-state">{query ? 'No matching patients.' : 'No patient records found.'}</p> :
        <table><thead><tr><th>Patient</th><th>Code</th><th>Phone</th><th>Dental profile</th><th>Allergy note</th><th>Profile</th></tr></thead>
          <tbody>{patients.map((patient) => <tr key={patient.id}>
            <td><div className="table-person"><div className="small-avatar">{patient.full_name.split(' ').map((part) => part[0]).slice(-2).join('')}</div><strong>{patient.full_name}</strong></div></td>
            <td><code>{patient.patient_code}</code></td><td>{patient.phone || '—'}</td>
            <td><span className="pill">{patient.dentition_type === 'CHILD' ? '20 teeth · child' : '32 teeth · adult'}</span></td>
            <td>{patient.allergies || 'No known allergies'}</td>
            <td><button className="text-button" onClick={() => setSelectedPatient(patient)}>View profile</button></td>
          </tr>)}</tbody>
        </table>}
    </div>
  </section>;
}
function dateKey(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}

function Appointments({ appointments, patients, doctors, services, schedules, role, loading, loadError, onCreateAppointment, onCreateSchedule, onCancelAppointment }) {
  const [calendarDate, setCalendarDate] = useState(() => new Date());
  const [calendarMode, setCalendarMode] = useState('week');
  const [doctorFilter, setDoctorFilter] = useState('');
  const [bookingOpen, setBookingOpen] = useState(false);
  const [scheduleOpen, setScheduleOpen] = useState(false);
  const [booking, setBooking] = useState({ patient: '', doctor: '', service: '', date: dateKey(new Date()), time: '09:00', notes: '' });
  const [schedule, setSchedule] = useState({ doctor: '', work_date: dateKey(new Date()), start_time: '09:00', end_time: '17:00' });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [cancellationTarget, setCancellationTarget] = useState(null);
  const [cancelling, setCancelling] = useState(false);
  const [cancellationError, setCancellationError] = useState('');
  const monday = new Date(calendarDate);
  monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7));
  const days = Array.from({ length: calendarMode === 'day' ? 1 : 7 }, (_, index) => {
    const date = new Date(calendarMode === 'day' ? calendarDate : monday);
    date.setDate(date.getDate() + index);
    return date;
  });
  const visibleDateKeys = new Set(days.map(dateKey));
  const visibleSchedules = schedules.filter((item) =>
    visibleDateKeys.has(item.work_date) && (!doctorFilter || String(item.doctor) === doctorFilter)
  );
  const visibleAppointments = appointments.filter((item) => {
    const start = new Date(item.appointment_date || item.start_at);
    return !Number.isNaN(start.getTime())
      && visibleDateKeys.has(dateKey(start))
      && (!doctorFilter || String(item.doctor) === doctorFilter);
  });
  const scheduleMinutes = visibleSchedules.flatMap((item) => [
    Number(item.start_time.slice(0, 2)) * 60 + Number(item.start_time.slice(3, 5)),
    Number(item.end_time.slice(0, 2)) * 60 + Number(item.end_time.slice(3, 5))
  ]);
  const appointmentMinutes = visibleAppointments.flatMap((item) => {
    const start = new Date(item.appointment_date || item.start_at);
    const end = new Date(item.end_at || start);
    return [start.getHours() * 60 + start.getMinutes(), end.getHours() * 60 + end.getMinutes()];
  });
  const allMinutes = [...scheduleMinutes, ...appointmentMinutes];
  const firstSlot = Math.max(0, Math.min(8 * 60, ...allMinutes.map((minutes) => Math.floor(minutes / 30) * 30)));
  const lastSlot = Math.min(24 * 60, Math.max(18 * 60, ...allMinutes.map((minutes) => Math.ceil(minutes / 30) * 30)));
  const slots = Array.from({ length: Math.max(1, (lastSlot - firstSlot) / 30) }, (_, index) => {
    const minutes = firstSlot + index * 30;
    return `${String(Math.floor(minutes / 60)).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}`;
  });
  const isReceptionRole = role === 'ADMIN' || role === 'RECEPTIONIST';

  async function submitBooking(event) {
    event.preventDefault();
    const reason = booking.notes.trim();
    if (!booking.patient || !booking.doctor || !booking.service || !booking.date || !booking.time || !reason) {
      setError('Complete all required fields, including the reason for the visit.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const created = await onCreateAppointment({
        patient: Number(booking.patient),
        doctor: Number(booking.doctor),
        service: Number(booking.service),
        appointment_date: new Date(`${booking.date}T${booking.time}:00`).toISOString(),
        notes: reason
      });
      setBookingOpen(false);
      setCalendarDate(new Date(`${booking.date}T12:00:00`));
      setCalendarMode('day');
      const patientName = patients.find((patient) => patient.id === created.patient)?.full_name;
      setSuccess(`Appointment request submitted${patientName ? ` for ${patientName}` : ''}. The updated visit is shown on the selected day.`);
      setBooking((current) => ({ ...current, patient: '', notes: '' }));
    } catch (saveError) {
      setError(saveError.message === 'Failed to fetch'
        ? 'Could not connect to the clinic API. Check your connection and try again.'
        : saveError.message || 'Could not submit the appointment request. Try again.');
    } finally {
      setSaving(false);
    }
  }

  async function submitSchedule(event) {
    event.preventDefault();
    setSaving(true);
    setError('');
    try {
      await onCreateSchedule({
        doctor: Number(schedule.doctor),
        work_date: schedule.work_date,
        start_time: schedule.start_time,
        end_time: schedule.end_time
      });
      setScheduleOpen(false);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  async function confirmCancellation() {
    if (!cancellationTarget) return;
    setCancelling(true);
    setCancellationError('');
    try {
      await onCancelAppointment(cancellationTarget.id);
      setSuccess(`Appointment for ${cancellationTarget.patient_name} was cancelled.`);
      setCancellationTarget(null);
    } catch (cancelError) {
      setCancellationError(cancelError.message === 'Failed to fetch'
        ? 'Could not connect to the clinic API. Check your connection and try again.'
        : cancelError.message || 'Could not cancel this appointment. Try again.');
    } finally {
      setCancelling(false);
    }
  }

  function openBooking(date, time) {
    setBooking((current) => ({
      ...current,
      date: dateKey(date),
      time,
      doctor: doctorFilter || current.doctor || String(doctors[0]?.id || ''),
      patient: current.patient || String(patients[0]?.id || ''),
      service: current.service || String(services[0]?.id || '')
    }));
    setBookingOpen(true);
    setError('');
    setSuccess('');
  }

  return <section className="page-section management-page">
    <div className="section-toolbar">
      <div><span className="eyebrow">CLINIC TIMETABLE</span><h2>Appointments & work shifts</h2></div>
      <div className="calendar-actions">
        {isReceptionRole && <button className="secondary-button" onClick={() => { setScheduleOpen(!scheduleOpen); setError(''); }}>{scheduleOpen ? 'Close shift form' : 'Add work shift'}</button>}
        {isReceptionRole && <button className="primary-button" onClick={() => openBooking(calendarDate, '09:00')}><CalendarDays size={17} /> Book appointment</button>}
      </div>
    </div>
    {success && <div className="form-success" role="status">{success}</div>}
    {error && <div className="form-error" role="alert">{error}</div>}
    {cancellationTarget && <div className="confirmation-backdrop">
      <section className="panel cancellation-dialog" role="dialog" aria-modal="true" aria-labelledby="cancel-dialog-title">
        <h3 id="cancel-dialog-title">Cancel this appointment?</h3>
        <p>{cancellationTarget.patient_name} · {new Date(cancellationTarget.appointment_date || cancellationTarget.start_at).toLocaleString()}</p>
        <p className="management-hint">Only pending or confirmed appointments can be cancelled.</p>
        {cancellationError && <div className="form-error" role="alert">{cancellationError}</div>}
        <div className="form-actions">
          <button className="danger-button secondary-button" type="button" disabled={cancelling} onClick={confirmCancellation}>{cancelling ? 'Cancelling…' : 'Confirm cancellation'}</button>
          <button className="secondary-button" type="button" disabled={cancelling} onClick={() => { setCancellationTarget(null); setCancellationError(''); }}>Keep appointment</button>
        </div>
      </section>
    </div>}
    {scheduleOpen && <form className="panel management-form" onSubmit={submitSchedule}>
      <h3>Set dentist working hours</h3>
      <div className="form-grid">
        <label>Dentist<select required value={schedule.doctor} onChange={(event) => setSchedule({ ...schedule, doctor: event.target.value })}><option value="">Select dentist</option>{doctors.map((doctor) => <option key={doctor.id} value={doctor.id}>{doctor.full_name}</option>)}</select></label>
        <label>Date<input required type="date" value={schedule.work_date} onChange={(event) => setSchedule({ ...schedule, work_date: event.target.value })} /></label>
        <label>Start time<input required type="time" value={schedule.start_time} onChange={(event) => setSchedule({ ...schedule, start_time: event.target.value })} /></label>
        <label>End time<input required type="time" value={schedule.end_time} onChange={(event) => setSchedule({ ...schedule, end_time: event.target.value })} /></label>
      </div>
      <div className="form-actions"><button className="primary-button" disabled={saving}>{saving ? 'Saving…' : 'Save work shift'}</button></div>
    </form>}
    {bookingOpen && <form className="panel management-form" onSubmit={submitBooking}>
      <h3>Request an appointment</h3>
      <div className="form-grid">
        <label>Patient<select required value={booking.patient} onChange={(event) => setBooking({ ...booking, patient: event.target.value })}><option value="">Select patient</option>{patients.map((patient) => <option key={patient.id} value={patient.id}>{patient.full_name} · {patient.patient_code}</option>)}</select></label>
        <label>Dentist<select required value={booking.doctor} onChange={(event) => setBooking({ ...booking, doctor: event.target.value })}><option value="">Select dentist</option>{doctors.map((doctor) => <option key={doctor.id} value={doctor.id}>{doctor.full_name}</option>)}</select></label>
        <label>Service<select required value={booking.service} onChange={(event) => setBooking({ ...booking, service: event.target.value })}><option value="">Select service</option>{services.map((service) => <option key={service.id} value={service.id}>{service.name} · {service.duration_minutes} min</option>)}</select></label>
        <label>Date<input required type="date" value={booking.date} onChange={(event) => setBooking({ ...booking, date: event.target.value })} /></label>
        <label>Start time<input required type="time" value={booking.time} onChange={(event) => setBooking({ ...booking, time: event.target.value })} /></label>
        <label className="booking-reason">Reason for visit<textarea required maxLength={1000} value={booking.notes} onChange={(event) => setBooking({ ...booking, notes: event.target.value })} /></label>
      </div>
      <p className="management-hint">The selected dentist must be scheduled for the full service duration. Overlapping appointments are rejected by the API.</p>
      <div className="form-actions"><button className="primary-button" disabled={saving}>{saving ? 'Booking…' : 'Confirm booking'}</button><button className="secondary-button" type="button" onClick={() => setBookingOpen(false)}>Cancel</button></div>
    </form>}
    <div className="calendar-toolbar panel">
      <div className="calendar-navigation">
        <button className="secondary-button" onClick={() => setCalendarDate(new Date(calendarDate.getFullYear(), calendarDate.getMonth(), calendarDate.getDate() - (calendarMode === 'day' ? 1 : 7), 12))}>Previous {calendarMode}</button>
        <button className="secondary-button" onClick={() => setCalendarDate(new Date())}>Today</button>
        <button className="secondary-button" onClick={() => setCalendarDate(new Date(calendarDate.getFullYear(), calendarDate.getMonth(), calendarDate.getDate() + (calendarMode === 'day' ? 1 : 7), 12))}>Next {calendarMode}</button>
      </div>
      <strong>{calendarMode === 'day'
        ? calendarDate.toLocaleDateString('en', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' })
        : `${days[0].toLocaleDateString('en', { month: 'short', day: 'numeric' })} – ${days[6].toLocaleDateString('en', { month: 'short', day: 'numeric', year: 'numeric' })}`}</strong>
      <label className="calendar-filter">Dentist
        <select aria-label="Filter by dentist" value={doctorFilter} onChange={(event) => setDoctorFilter(event.target.value)}>
          <option value="">All dentists</option>
          {doctors.map((doctor) => <option key={doctor.id} value={doctor.id}>{doctor.full_name}</option>)}
        </select>
      </label>
      <div className="calendar-view-switch" role="group" aria-label="Calendar view">
        {['day', 'week'].map((mode) => <button key={mode} type="button" className={calendarMode === mode ? 'secondary-button active' : 'secondary-button'} aria-pressed={calendarMode === mode} onClick={() => setCalendarMode(mode)}>{mode === 'day' ? 'Day' : 'Week'}</button>)}
      </div>
      <input aria-label="Go to date" type="date" value={dateKey(calendarDate)} onChange={(event) => { if (event.target.value) setCalendarDate(new Date(`${event.target.value}T12:00:00`)); }} />
    </div>
    {loadError && <div className="form-error" role="alert">Could not load the calendar: {loadError}</div>}
    {doctors.length === 0 && !loading && !loadError && <div className="management-state" role="status">No dentist profiles are available.</div>}
    {loading ? <div className="panel management-state" role="status">Loading appointments and work shifts…</div> :
      loadError ? <div className="panel management-state">Calendar data is unavailable. Check the connection and try again.</div> :
      <>
        {!visibleSchedules.length && !visibleAppointments.length && <div className="panel management-state" role="status">No work shifts or appointments for this {calendarMode}.</div>}
        <div className="calendar-legend" aria-label="Calendar legend">
          <span><i className="legend-shift" /> Doctor working hours</span>
          <span><i className="legend-unavailable" /> Outside working hours</span>
          <span><i className="legend-appointment" /> Appointment</span>
        </div>
        <div className="panel timetable-panel">
          <div className={`timetable-grid ${calendarMode === 'day' ? 'day-view' : ''}`} style={{ '--calendar-day-count': days.length }}>
            <div className="timetable-head timetable-time">Time</div>
            {days.map((date) => <div className="timetable-head" key={dateKey(date)}><strong>{date.toLocaleDateString('en', { weekday: 'short' })}</strong><span>{date.toLocaleDateString('en', { month: 'short', day: 'numeric' })}</span></div>)}
            {slots.map((time) => <div className="timetable-row" key={time}>
              <div className="timetable-time">{time}</div>
              {days.map((date) => {
                const key = dateKey(date);
                const minute = Number(time.slice(0, 2)) * 60 + Number(time.slice(3));
                const shifts = visibleSchedules.filter((item) => item.work_date === key
                  && Number(item.start_time.slice(0, 2)) * 60 + Number(item.start_time.slice(3, 5)) <= minute
                  && Number(item.end_time.slice(0, 2)) * 60 + Number(item.end_time.slice(3, 5)) > minute);
                const events = visibleAppointments.filter((item) => {
                  const start = new Date(item.appointment_date || item.start_at);
                  return dateKey(start) === key
                    && Math.floor((start.getHours() * 60 + start.getMinutes()) / 30) * 30 === minute;
                });
                const selectedService = services.find((service) => String(service.id) === booking.service);
                const proposedStart = new Date(`${key}T${time}:00`);
                const proposedEnd = new Date(proposedStart.getTime() + (selectedService?.duration_minutes || 30) * 60_000);
                const slotBusy = visibleAppointments.some((item) => {
                  if (String(item.status || '').toLowerCase() === 'cancelled') return false;
                  const start = new Date(item.appointment_date || item.start_at);
                  const end = item.end_at ? new Date(item.end_at) : new Date(start.getTime() + 30 * 60_000);
                  return start < proposedEnd && proposedStart < end;
                });
                return <div className={`timetable-cell ${shifts.length ? 'shift-available' : ''}`} key={`${key}-${time}`}>
                  {events.map((item) => {
                    const start = new Date(item.appointment_date || item.start_at);
                    const end = item.end_at ? new Date(item.end_at) : null;
                    const statusClass = String(item.status || 'scheduled').toLowerCase().replace(/[^a-z0-9]+/g, '-');
                    return <div className={`calendar-event status-${statusClass}`} key={item.id}>
                      <strong>{start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}{end && !Number.isNaN(end.getTime()) ? `–${end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : ''} · {item.patient_name}</strong>
                      <span>{item.service_name || item.type || 'Dental visit'} · {item.dentist_name}</span>
                      <small>{item.status || 'Scheduled'}</small>
                      {item.notes && <small className="calendar-event-reason">Reason: {item.notes}</small>}
                    </div>;
                  })}
                  {!events.length && !slotBusy && isReceptionRole && shifts.length > 0 && <button aria-label={`Book ${key} at ${time}`} className="empty-slot" onClick={() => openBooking(date, time)} title="Request an appointment for this available slot">+</button>}
                </div>;
              })}
            </div>)}
          </div>
        </div>
        <div className="panel appointment-list-panel"><div className="panel-heading"><div><span className="eyebrow">SELECTED {calendarMode.toUpperCase()}</span><h3>Appointments in this view</h3></div></div>
          {visibleAppointments.length ? <div className="appointment-list">{[...visibleAppointments].sort((a, b) => new Date(a.appointment_date || a.start_at) - new Date(b.appointment_date || b.start_at)).map((item) => <AppointmentRow key={item.id} item={item} canCancel={isReceptionRole} onCancel={(target) => { setCancellationTarget(target); setCancellationError(''); setSuccess(''); }} />)}</div> : <p className="management-state">No appointments in this {calendarMode}.</p>}
        </div>
      </>}
  </section>;
}

function Reception({ tokens, onTokensChanged, appointments, setSection }) {
  const [term, setTerm] = useState('');
  const [patients, setPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const selectedPatient = patients.find((patient) => patient.id === selectedPatientId);
  const patientAppointments = selectedPatient
    ? appointments
      .filter((appointment) => appointment.patient === selectedPatient.id)
      .sort((left, right) => new Date(left.appointment_date || left.start_at) - new Date(right.appointment_date || right.start_at))
    : [];

  async function searchPatients(event) {
    event.preventDefault();
    const searchTerm = term.trim();
    setPatients([]);
    setSelectedPatientId(null);
    setError('');
    setSearched(Boolean(searchTerm));
    if (!searchTerm) return;
    if (searchTerm.length > 100 || !/^[\p{L}\p{N}\s._+'()\-]+$/u.test(searchTerm)) {
      setError('Enter a patient code, name, or phone using letters, numbers, spaces, and common separators.');
      return;
    }

    setLoading(true);
    try {
      const result = await apiRequest(`/patients/?search=${encodeURIComponent(searchTerm)}`, {
        tokens,
        onTokens: onTokensChanged
      });
      if (!Array.isArray(result)) {
        throw new Error('The patient search returned an unexpected response.');
      }
      setPatients(result);
      setSelectedPatientId(result.length === 1 ? result[0].id : null);
    } catch (searchError) {
      setError(searchError.message || 'Could not search patients. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function formatDate(value) {
    if (!value) return 'Not recorded';
    const date = new Date(`${value}T00:00:00`);
    return Number.isNaN(date.getTime()) ? 'Not recorded' : date.toLocaleDateString();
  }

  function patientAge(value) {
    if (!value) return null;
    const birthDate = new Date(`${value}T00:00:00`);
    if (Number.isNaN(birthDate.getTime())) return null;
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    if (today.getMonth() < birthDate.getMonth() || (today.getMonth() === birthDate.getMonth() && today.getDate() < birthDate.getDate())) age -= 1;
    return age >= 0 ? age : null;
  }

  return <section className="page-section management-page reception-page">
    <div className="section-toolbar">
      <div><span className="eyebrow">FRONT DESK</span><h2>Patient reception</h2></div>
      {selectedPatient && <button className="primary-button" onClick={() => setSection('Appointments')}><CalendarDays size={17} /> Continue to scheduling</button>}
    </div>
    <form className="panel reception-search" onSubmit={searchPatients} noValidate>
      <label htmlFor="reception-search">Find an existing patient</label>
      <p>Search by patient code, full or partial name, or phone number.</p>
      <div className="reception-search-controls">
        <Search size={18} aria-hidden="true" />
        <input
          id="reception-search"
          type="search"
          maxLength={120}
          value={term}
          onChange={(event) => {
            setTerm(event.target.value);
            setPatients([]);
            setSelectedPatientId(null);
            setSearched(false);
            setError('');
          }}
          disabled={loading}
          placeholder="e.g. DMS-0001, Nguyen Minh Anh, or phone"
          autoComplete="off"
        />
        <button className="primary-button" type="submit" disabled={loading}>{loading ? 'Searching…' : 'Search'}</button>
      </div>
      {error && <div className="form-error" role="alert">{error}</div>}
    </form>

    {loading && <div className="panel reception-state" role="status">Searching patient records…</div>}
    {!loading && !error && !term.trim() && <div className="panel reception-state">Enter a patient code, name, or phone number to begin.</div>}
    {!loading && !error && term.trim() && !searched && <div className="panel reception-state">Press Search to look up this patient.</div>}
    {!loading && !error && searched && patients.length === 0 && <div className="panel reception-state" role="status">No patient found. Check the details and search again.</div>}
    {!loading && !error && patients.length > 0 && <div className="reception-results-layout">
      <section className="panel reception-results" aria-label="Patient search results">
        <div className="panel-heading"><div><span className="eyebrow">SEARCH RESULTS</span><h3>{patients.length} {patients.length === 1 ? 'patient' : 'patients'} found</h3></div></div>
        {patients.map((patient) => <button
          type="button"
          key={patient.id}
          className={`reception-result ${selectedPatientId === patient.id ? 'selected' : ''}`}
          onClick={() => setSelectedPatientId(patient.id)}
        >
          <span className="small-avatar">{patient.full_name.split(' ').map((part) => part[0]).slice(-2).join('')}</span>
          <span className="reception-result-info"><strong>{patient.full_name}</strong><small>{patient.patient_code} · {patient.phone || 'No phone recorded'}</small></span>
          <span className="reception-result-arrow">›</span>
        </button>)}
      </section>
      {selectedPatient && <section className="panel reception-profile">
        <div className="panel-heading"><div><span className="eyebrow">PATIENT PROFILE</span><h3>{selectedPatient.full_name}</h3></div><span className="pill">{selectedPatient.patient_code}</span></div>
        <dl className="reception-profile-grid">
          <div><dt>Phone</dt><dd>{selectedPatient.phone || 'Not recorded'}</dd></div>
          <div><dt>Date of birth</dt><dd>{formatDate(selectedPatient.date_of_birth)}{patientAge(selectedPatient.date_of_birth) !== null ? ` · ${patientAge(selectedPatient.date_of_birth)} years old` : ''}</dd></div>
          <div><dt>Dental profile</dt><dd>{selectedPatient.dentition_type === 'CHILD' ? 'Child · 20 teeth' : 'Adult · 32 teeth'}</dd></div>
          <div className="reception-medical-alert"><dt>Allergies</dt><dd>{selectedPatient.allergies || 'None recorded'}</dd></div>
          <div className="profile-wide"><dt>Medical history</dt><dd>{selectedPatient.medical_history || 'None recorded'}</dd></div>
        </dl>
        <div className="reception-visit-history">
          <span className="eyebrow">APPOINTMENT HISTORY</span>
          {patientAppointments.length
            ? patientAppointments.map((appointment) => <div key={appointment.id}><strong>{new Date(appointment.appointment_date || appointment.start_at).toLocaleString()}</strong><span>{appointment.service_name || appointment.type || 'Dental visit'} · {appointment.status}</span></div>)
            : <p>No appointments recorded.</p>}
        </div>
      </section>}
      {!selectedPatient && <div className="panel reception-state">Select a patient from the results to review their reception details.</div>}
    </div>}
  </section>;
}

function MedicalRecords({ appointments, patients, services, teeth, records, loading, loadError, onSave }) {
  const eligibleAppointments = appointments.filter((item) => item.status !== 'Cancelled' && item.status !== 'CANCELLED');
  const [appointmentId, setAppointmentId] = useState('');
  const [form, setForm] = useState({ diagnosis: '', treatment_plan: '', prescription: '', notes: '', teeth: [], services: [] });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const selectedAppointment = eligibleAppointments.find((item) => String(item.id) === appointmentId);
  const selectedPatient = patients.find((patient) => String(patient.id) === String(selectedAppointment?.patient));
  const record = records.find((item) => String(item.appointment) === appointmentId);
  const patientTeeth = teeth.filter((tooth) => tooth.dentition_type === (selectedPatient?.dentition_type || 'ADULT'));
  const midpoint = Math.ceil(patientTeeth.length / 2);

  useEffect(() => {
    if (!appointmentId && eligibleAppointments.length) setAppointmentId(String(eligibleAppointments[0].id));
  }, [appointments, appointmentId]);

  useEffect(() => {
    setForm(record ? {
      diagnosis: record.diagnosis,
      treatment_plan: record.treatment_plan,
      prescription: record.prescription || '',
      notes: record.notes || '',
      teeth: record.teeth || [],
      services: record.services || []
    } : { diagnosis: '', treatment_plan: '', prescription: '', notes: '', teeth: [], services: [] });
    setError('');
  }, [appointmentId, record?.id]);

  function toggleSelection(field, id) {
    setForm((current) => ({
      ...current,
      [field]: current[field].includes(id)
        ? current[field].filter((value) => value !== id)
        : [...current[field], id]
    }));
  }

  async function saveRecord(event) {
    event.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await onSave({ ...form, appointment: Number(appointmentId) }, record?.id);
      setSuccess('Medical record saved.');
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return <section className="page-section management-page">
    <div className="section-toolbar"><div><span className="eyebrow">CLINICAL WORKSPACE</span><h2>Electronic medical record</h2></div></div>
    {loading && <div className="panel management-state" role="status">Loading appointments, records, teeth and services…</div>}
    {loadError && <div className="form-error" role="alert">EMR data could not be loaded: {loadError}</div>}
    {error && <div className="form-error" role="alert">{error}</div>}
    {success && <div className="form-success" role="status">{success}</div>}
    {!loading && !loadError && !eligibleAppointments.length && <div className="panel management-state">No appointments are available for clinical documentation.</div>}
    {!loading && !loadError && eligibleAppointments.length > 0 && selectedAppointment && <form className="panel management-form emr-form" onSubmit={saveRecord}>
      <label className="emr-appointment">Appointment being examined
        <select value={appointmentId} onChange={(event) => { setAppointmentId(event.target.value); setSuccess(''); }}>
          {eligibleAppointments.map((item) => <option key={item.id} value={item.id}>{new Date(item.appointment_date || item.start_at).toLocaleString()} · {item.patient_name} · {item.dentist_name}</option>)}
        </select>
      </label>
      {selectedPatient && <div className="emr-patient-alert">
        <div className="emr-patient-heading"><strong>{selectedPatient.full_name}</strong><span>{selectedPatient.patient_code} · {selectedPatient.phone || 'No phone recorded'}</span></div>
        <div className="emr-appointment-details">
          <span><strong>Appointment:</strong> {new Date(selectedAppointment.appointment_date || selectedAppointment.start_at).toLocaleString()}</span>
          <span><strong>Dentist:</strong> {selectedAppointment.dentist_name || 'Not recorded'}</span>
          <span><strong>Status:</strong> {selectedAppointment.status}</span>
        </div>
        <p><strong>Allergies:</strong> {selectedPatient.allergies || 'None recorded'} · <strong>Medical history:</strong> {selectedPatient.medical_history || 'None recorded'}</p>
      </div>}
      <label>Diagnosis<textarea required rows="3" value={form.diagnosis} onChange={(event) => setForm({ ...form, diagnosis: event.target.value })} /></label>
      <label>Treatment plan<textarea required rows="3" value={form.treatment_plan} onChange={(event) => setForm({ ...form, treatment_plan: event.target.value })} /></label>
      <div className="emr-selection-grid">
        <fieldset className="emr-teeth-fieldset">
          <legend>Teeth examined or treated ({form.teeth.length} selected)</legend>
          {!patientTeeth.length ? <p className="emr-empty-options">No tooth chart data is available for this patient's dentition.</p> : <div className="emr-tooth-chart">
            <span className="emr-arch-label">UPPER ARCH</span>
            <div className="emr-tooth-row">{patientTeeth.slice(0, midpoint).map((tooth) => <button key={tooth.id} type="button" aria-pressed={form.teeth.includes(tooth.id)} className={`emr-tooth ${form.teeth.includes(tooth.id) ? 'selected' : ''}`} onClick={() => toggleSelection('teeth', tooth.id)}>{tooth.code}</button>)}</div>
            <div className="emr-mouth-line" />
            <div className="emr-tooth-row lower">{patientTeeth.slice(midpoint).reverse().map((tooth) => <button key={tooth.id} type="button" aria-pressed={form.teeth.includes(tooth.id)} className={`emr-tooth ${form.teeth.includes(tooth.id) ? 'selected' : ''}`} onClick={() => toggleSelection('teeth', tooth.id)}>{tooth.code}</button>)}</div>
            <span className="emr-arch-label lower">LOWER ARCH</span>
          </div>}
        </fieldset>
        <fieldset>
          <legend>Treatment services ({form.services.length} selected)</legend>
          {!services.length ? <p className="emr-empty-options">No active services are available.</p> : <div className="service-options">
            {services.map((service) => <label key={service.id}>
              <input type="checkbox" checked={form.services.includes(service.id)} onChange={() => toggleSelection('services', service.id)} />
              <span><strong>{service.name}</strong><small>{service.description || 'No service description'} · {service.duration_minutes} min</small></span>
              <small>{Number(service.price).toLocaleString('vi-VN')} ₫</small>
            </label>)}
          </div>}
        </fieldset>
      </div>
      <label>Prescription<textarea rows="2" value={form.prescription} onChange={(event) => setForm({ ...form, prescription: event.target.value })} /></label>
      <label>Clinical notes<textarea rows="2" value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} /></label>
      <div className="form-actions"><button className="primary-button" disabled={saving || !appointmentId}>{saving ? 'Saving…' : record ? 'Update medical record' : 'Save medical record'}</button></div>
    </form>}
  </section>;
}
function ToothChart({ dentition, setDentition, selectedTooth, setSelectedTooth }) { const teeth = dentition === 'ADULT' ? teethAdult : teethChild; return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">CLINICAL RECORD</span><h2>Interactive tooth chart</h2></div><div className="segmented"><button className={dentition === 'ADULT' ? 'selected' : ''} onClick={() => setDentition('ADULT')}>Adult · 32</button><button className={dentition === 'CHILD' ? 'selected' : ''} onClick={() => setDentition('CHILD')}>Child · 20</button></div></div><div className="chart-layout"><div className="panel tooth-panel"><div className="chart-header"><div><strong>Nguyen Minh Anh</strong><span>DMS-0001 · {dentition === 'ADULT' ? 'Permanent dentition' : 'Primary dentition'}</span></div><span className="status confirmed">In treatment</span></div><div className="mouth-label">UPPER ARCH</div><div className={`teeth-grid ${dentition.toLowerCase()}`}>{teeth.slice(0, Math.ceil(teeth.length / 2)).map((tooth) => <Tooth key={tooth.id} tooth={tooth} selected={selectedTooth === tooth.id} onClick={() => setSelectedTooth(tooth.id)} />)}</div><div className="mouth-line" /><div className={`teeth-grid lower ${dentition.toLowerCase()}`}>{teeth.slice(Math.ceil(teeth.length / 2)).reverse().map((tooth) => <Tooth key={tooth.id} tooth={tooth} selected={selectedTooth === tooth.id} onClick={() => setSelectedTooth(tooth.id)} />)}</div><div className="mouth-label lower-label">LOWER ARCH</div><div className="chart-legend"><span><i className="dot healthy" />Healthy</span><span><i className="dot care" />Needs care</span><span><i className="dot monitor" />Monitor</span></div></div><aside className="panel tooth-detail"><span className="eyebrow">SELECTED TOOTH</span>{selectedTooth ? <><div className="tooth-number">{teeth.find((tooth) => tooth.id === selectedTooth)?.code}</div><h3>Clinical condition</h3><p>Update this tooth’s condition and add a treatment note for the patient record.</p><select defaultValue="Healthy"><option>Healthy</option><option>Needs care</option><option>Monitor</option><option>Restored</option></select><textarea placeholder="Add a clinical note..." /><button className="primary-button full">Save condition</button></> : <div className="empty-detail"><Stethoscope size={28} /><p>Select a tooth to inspect its clinical record.</p></div>}</aside></div></section>; }
function Tooth({ tooth, selected, onClick }) { return <button onClick={onClick} className={`tooth ${tooth.state.toLowerCase().replace(' ', '-')} ${selected ? 'selected' : ''}`}><span>{tooth.code.slice(1)}</span><div className="tooth-shape" /></button>; }
function Billing({ invoices, records, loading, onCreateInvoice, onPayCash, onCreateQr, onReconcileQr, onCancelQr }) {
  const [recordId, setRecordId] = useState('');
  const [quantities, setQuantities] = useState({});
  const [selectedInvoiceId, setSelectedInvoiceId] = useState('');
  const [cashConfirmOpen, setCashConfirmOpen] = useState(false);
  const [qrDialogOpen, setQrDialogOpen] = useState(false);
  const [qrTransfer, setQrTransfer] = useState(null);
  const [qrImageError, setQrImageError] = useState(false);
  const [bankReference, setBankReference] = useState('');
  const [qrVerified, setQrVerified] = useState(false);
  const [qrCancellationChecked, setQrCancellationChecked] = useState(false);
  const [cashMethod, setCashMethod] = useState('CASH');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [cashError, setCashError] = useState('');
  const [qrError, setQrError] = useState('');
  const [success, setSuccess] = useState('');
  const selectedRecord = records.find((record) => String(record.id) === recordId);
  const selectedInvoice = invoices.find((invoice) => String(invoice.id) === selectedInvoiceId);
  const hasPendingQr = selectedInvoice?.payments?.some((payment) => payment.method === 'BANK_TRANSFER' && payment.status === 'PENDING') || false;
  const total = selectedRecord?.services.reduce((sum, service) => {
    const quantity = Number(quantities[service.id] || 1);
    return sum + Number(service.price) * quantity;
  }, 0) || 0;

  useEffect(() => {
    if (records.length && !records.some((record) => String(record.id) === recordId)) {
      setRecordId(String(records[0].id));
    }
  }, [records, recordId]);

  useEffect(() => {
    if (selectedRecord) {
      setQuantities(Object.fromEntries(selectedRecord.services.map((service) => [service.id, 1])));
    }
  }, [selectedRecord?.id]);

  async function createInvoice(event) {
    event.preventDefault();
    if (!selectedRecord) return;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const invoice = await onCreateInvoice({
        medical_record: selectedRecord.id,
        items: selectedRecord.services.map((service) => ({
          service: service.id,
          quantity: Number(quantities[service.id] || 1)
        }))
      });
      setSelectedInvoiceId(String(invoice.id));
      setSuccess(`Invoice ${invoice.invoice_number} created successfully.`);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  async function confirmCashPayment() {
    if (!selectedInvoice || cashMethod !== 'CASH') return;
    setSaving(true);
    setCashError('');
    setError('');
    setSuccess('');
    try {
      const paid = await onPayCash(selectedInvoice.id);
      setCashConfirmOpen(false);
      setSuccess(`Cash payment of ${Number(paid.paid_amount).toLocaleString('vi-VN')} ₫ recorded.`);
    } catch (paymentError) {
      setCashError(paymentError.message);
    } finally {
      setSaving(false);
    }
  }

  async function showQrPayment() {
    if (!selectedInvoice) return;
    setSaving(true);
    setQrError('');
    setError('');
    setSuccess('');
    try {
      const result = await onCreateQr(selectedInvoice.id);
      setQrTransfer(result.transfer);
      setQrImageError(false);
      setBankReference('');
      setQrVerified(false);
      setQrCancellationChecked(false);
      setQrDialogOpen(true);
      setSuccess('Transfer QR is ready. The invoice remains unpaid until a bank transaction is verified.');
    } catch (paymentError) {
      setQrError(paymentError.message);
    } finally {
      setSaving(false);
    }
  }

  async function confirmQrPayment(event) {
    event.preventDefault();
    if (!selectedInvoice || !bankReference.trim() || !qrVerified) return;
    setSaving(true);
    setQrError('');
    try {
      const paid = await onReconcileQr(selectedInvoice.id, {
        bank_reference: bankReference.trim(),
        verified_amount: qrTransfer.amount,
        verified: true
      });
      setQrDialogOpen(false);
      setBankReference('');
      setQrVerified(false);
      setSuccess(`Bank transfer for invoice ${paid.invoice_number} was recorded as verified.`);
    } catch (verificationError) {
      setQrError(verificationError.message);
    } finally {
      setSaving(false);
    }
  }

  async function cancelPendingQr() {
    if (!selectedInvoice || !qrCancellationChecked) return;
    setSaving(true);
    setQrError('');
    try {
      const updatedInvoice = await onCancelQr(selectedInvoice.id);
      setQrDialogOpen(false);
      setQrCancellationChecked(false);
      setSuccess(`Pending transfer for invoice ${updatedInvoice.invoice_number} was cancelled after the account check.`);
    } catch (cancellationError) {
      setQrError(cancellationError.message);
    } finally {
      setSaving(false);
    }
  }

  return <section className="page-section management-page">
    <div className="section-toolbar"><div><span className="eyebrow">FINANCE</span><h2>Invoices</h2></div></div>
    {error && <div className="form-error" role="alert">{error}</div>}
    {success && <div className="form-success" role="status">{success}</div>}
    <section className="panel invoice-create-panel">
      <div className="panel-heading"><div><span className="eyebrow">FROM PRESCRIBED SERVICES</span><h3>Create invoice</h3></div></div>
      {loading ? <p className="management-state" role="status">Loading invoices and prescribed services…</p> : !records.length ? <p className="management-state">No examination records with uninvoiced prescribed services are available.</p> : <form className="invoice-form" onSubmit={createInvoice}>
        <label>Examination record
          <select required value={recordId} onChange={(event) => { setRecordId(event.target.value); setSuccess(''); }}>
            {records.map((record) => <option key={record.id} value={record.id}>{record.patient_name} · {record.patient_code} · {new Date(record.appointment_date).toLocaleString()}</option>)}
          </select>
        </label>
        {selectedRecord && <>
          <div className="invoice-patient-summary"><strong>{selectedRecord.patient_name}</strong><span>{selectedRecord.patient_code} · Examined {new Date(selectedRecord.appointment_date).toLocaleString()}</span></div>
          <p className="invoice-source-meta">Prescribed services are loaded from EMR. Prices are determined and validated by the server when the invoice is created.</p>
          <div className="invoice-lines">
            <div className="invoice-line invoice-line-heading"><span>Service</span><span>Unit price</span><span>Quantity</span><span>Amount</span></div>
            {selectedRecord.services.map((service) => {
              const quantity = Number(quantities[service.id] || 1);
              const lineTotal = Number(service.price) * quantity;
              return <div className="invoice-line" key={service.id}>
                <strong>{service.name}</strong>
                <span>{Number(service.price).toLocaleString('vi-VN')} ₫</span>
                <input aria-label={`Quantity for ${service.name}`} type="number" min="1" max="32767" step="1" required value={quantities[service.id] ?? 1} onChange={(event) => setQuantities((current) => ({ ...current, [service.id]: event.target.value }))} />
                <strong>{lineTotal.toLocaleString('vi-VN')} ₫</strong>
              </div>;
            })}
          </div>
          <div className="invoice-total invoice-grand-total"><span>Total due</span><strong>{total.toLocaleString('vi-VN')} ₫</strong></div>
          <p className="invoice-payment-note">New invoices are issued unpaid. Cash and QR transfer options are available from invoice details.</p>
          <div className="form-actions"><button className="primary-button" type="submit" disabled={saving || !selectedRecord.services.length}>{saving ? 'Creating invoice…' : 'Create invoice'}</button></div>
        </>}
      </form>}
    </section>
    <section className="panel table-panel management-table invoice-history-panel">
      <div className="panel-heading"><div><span className="eyebrow">BILLING HISTORY</span><h3>Invoices ({invoices.length})</h3></div></div>
      {loading ? <p className="management-state" role="status">Loading invoice history…</p> : !invoices.length ? <p className="management-state">No invoices have been created yet.</p> : <div className="invoice-table-scroll"><table>
        <thead><tr><th>Invoice</th><th>Patient</th><th>Issued</th><th>Total</th><th>Paid</th><th>Balance</th><th>Status</th></tr></thead>
        <tbody>{invoices.map((invoice) => <tr key={invoice.id} className={selectedInvoiceId === String(invoice.id) ? 'invoice-row-selected' : ''} onClick={() => setSelectedInvoiceId(String(invoice.id))}>
          <td><button type="button" className="invoice-number-button" aria-label={`View invoice ${invoice.invoice_number}`} onClick={() => setSelectedInvoiceId(String(invoice.id))}>{invoice.invoice_number}</button></td>
          <td>{invoice.patient_name}</td><td>{new Date(invoice.issued_at).toLocaleDateString()}</td>
          <td>{Number(invoice.total_amount).toLocaleString('vi-VN')} ₫</td><td>{Number(invoice.paid_amount).toLocaleString('vi-VN')} ₫</td>
          <td>{Number(invoice.balance).toLocaleString('vi-VN')} ₫</td><td><span className={`pill invoice-status ${invoice.status.toLowerCase()}`}>{invoice.status}</span></td>
        </tr>)}</tbody>
      </table></div>}
    </section>
    {selectedInvoice && <section className="panel invoice-detail-panel">
      <div className="panel-heading"><div><span className="eyebrow">INVOICE DETAILS</span><h3>{selectedInvoice.invoice_number} · {selectedInvoice.patient_name}</h3></div><div className="invoice-detail-actions"><span className={`pill invoice-status ${selectedInvoice.status.toLowerCase()}`}>{selectedInvoice.status}</span>{selectedInvoice.status === 'ISSUED' && Number(selectedInvoice.balance) > 0 && <><button type="button" className="primary-button" disabled={saving || hasPendingQr} title={hasPendingQr ? 'A bank transfer is pending; do not record another payment.' : undefined} onClick={() => { setCashError(''); setCashMethod('CASH'); setCashConfirmOpen(true); }}>Pay by cash</button><button type="button" className="secondary-button" disabled={saving} onClick={showQrPayment}>{hasPendingQr ? 'Show transfer QR' : 'Pay by QR'}</button></>}</div></div>
      {hasPendingQr && <div className="qr-pending-note" role="status">Bank transfer pending confirmation. The invoice is not paid yet; do not treat this QR or a patient's transfer claim as payment confirmation.</div>}
      {qrError && <div className="form-error" role="alert">{qrError}</div>}
      <div className="invoice-lines">
        <div className="invoice-line invoice-line-heading"><span>Service</span><span>Unit price</span><span>Quantity</span><span>Amount</span></div>
        {selectedInvoice.items.map((item) => <div className="invoice-line" key={item.id}>
          <strong>{item.description}</strong><span>{Number(item.unit_price).toLocaleString('vi-VN')} ₫</span><span>{item.quantity}</span><strong>{Number(item.amount).toLocaleString('vi-VN')} ₫</strong>
        </div>)}
      </div>
      <div className="invoice-total"><span>Total · Balance</span><strong>{Number(selectedInvoice.total_amount).toLocaleString('vi-VN')} ₫ · {Number(selectedInvoice.balance).toLocaleString('vi-VN')} ₫</strong></div>
      {!!selectedInvoice.payments.length && <div className="invoice-payments">
        <h4>Payment transactions</h4>
        {selectedInvoice.payments.map((payment) => <div className="invoice-payment-row" key={payment.id}>
          <strong>{Number(payment.amount).toLocaleString('vi-VN')} ₫ · {payment.method}</strong>
          <span>{payment.status === 'COMPLETED' && payment.paid_at ? `Paid ${new Date(payment.paid_at).toLocaleString()}` : `Created ${new Date(payment.created_at).toLocaleString()} · ${payment.status === 'PENDING' ? 'Awaiting verification' : payment.status}`}</span>
          {payment.bank_reference && <span>Bank reference: {payment.bank_reference}</span>}
          {payment.verified_at && <span>Manually verified {new Date(payment.verified_at).toLocaleString()}</span>}
          {payment.verified_by_name && <span>Manually verified by {payment.verified_by_name}</span>}
          {payment.cancelled_at && <span>Cancelled {new Date(payment.cancelled_at).toLocaleString()} by {payment.cancelled_by_name || 'staff'}</span>}
          {payment.received_by_name && <span>Received by {payment.received_by_name}</span>}
        </div>)}
      </div>}
    </section>}
    {qrDialogOpen && qrTransfer && <div className="confirmation-backdrop" role="presentation">
      <section className="panel cancellation-dialog qr-payment-dialog" role="dialog" aria-modal="true" aria-labelledby="qr-payment-title">
        <h3 id="qr-payment-title">Bank transfer QR</h3>
        <p>Scan this code to transfer the exact amount. The invoice will stay <strong>unpaid</strong> until a bank transaction is verified.</p>
        <div className="qr-image-frame">
          {qrImageError ? <p role="alert">The QR image could not be loaded. Use the bank details below to make the transfer.</p> : <img src={qrTransfer.qr_url} alt={`VietQR for invoice ${qrTransfer.description}`} onError={() => setQrImageError(true)} />}
        </div>
        <dl className="qr-transfer-details">
          <div><dt>Amount</dt><dd>{Number(qrTransfer.amount).toLocaleString('vi-VN')} ₫</dd></div>
          <div><dt>Bank</dt><dd>{qrTransfer.bank_id}</dd></div>
          <div><dt>Account number</dt><dd>{qrTransfer.account_number}</dd></div>
          <div><dt>Account name</dt><dd>{qrTransfer.account_name}</dd></div>
          <div><dt>Transfer content</dt><dd>{qrTransfer.description}</dd></div>
          <div><dt>Status</dt><dd>Pending verification</dd></div>
        </dl>
        <p className="qr-pending-note">Do not confirm from the QR code or a patient's report. Check the receiving bank account and match both the exact amount and transaction reference first. This action records a staff manual reconciliation; it does not connect to a bank or webhook.</p>
        {qrTransfer.status === 'PENDING' && <form className="qr-reconciliation-form" onSubmit={confirmQrPayment}>
          <label>Bank transaction reference<input type="text" required maxLength={100} value={bankReference} onChange={(event) => setBankReference(event.target.value)} /></label>
          <label className="qr-verification-check"><input type="checkbox" checked={qrVerified} onChange={(event) => setQrVerified(event.target.checked)} /> I checked the receiving bank account and confirmed the transaction reference and amount match this invoice.</label>
          {qrError && <div className="form-error" role="alert">{qrError}</div>}
          <div className="form-actions"><button type="button" className="secondary-button" disabled={saving} onClick={() => setQrDialogOpen(false)}>Close</button><button type="submit" className="primary-button" disabled={saving || !bankReference.trim() || !qrVerified}>{saving ? 'Recording…' : 'Record verified transfer'}</button></div>
        </form>}
        {qrTransfer.status === 'PENDING' && <div className="qr-cancellation-form">
          <label className="qr-verification-check"><input type="checkbox" checked={qrCancellationChecked} onChange={(event) => setQrCancellationChecked(event.target.checked)} /> I checked the receiving account and confirmed that this transfer has not arrived.</label>
          <button type="button" className="secondary-button" disabled={saving || !qrCancellationChecked} onClick={cancelPendingQr}>{saving ? 'Cancelling…' : 'Cancel pending transfer'}</button>
        </div>}
        {qrTransfer.status !== 'PENDING' && <div className="form-actions"><button type="button" className="secondary-button" onClick={() => setQrDialogOpen(false)}>Close</button></div>}
      </section>
    </div>}
    {cashConfirmOpen && selectedInvoice && <div className="confirmation-backdrop" role="presentation">
      <section className="panel cancellation-dialog cash-payment-dialog" role="dialog" aria-modal="true" aria-labelledby="cash-payment-title">
        <h3 id="cash-payment-title">Confirm cash payment</h3>
        <p>Confirm that you received the full balance for invoice <strong>{selectedInvoice.invoice_number}</strong>.</p>
        <p className="cash-payment-due">Amount received: <strong>{Number(selectedInvoice.balance).toLocaleString('vi-VN')} ₫</strong></p>
        <fieldset className="cash-method-options"><legend>Payment method</legend>
          <label><input type="radio" name="payment-method" value="CASH" checked={cashMethod === 'CASH'} onChange={() => setCashMethod('CASH')} /> Cash</label>
        </fieldset>
        {cashError && <div className="form-error" role="alert">{cashError}</div>}
        <div className="form-actions"><button type="button" className="secondary-button" disabled={saving} onClick={() => setCashConfirmOpen(false)}>Cancel</button><button type="button" className="primary-button" disabled={saving || cashMethod !== 'CASH'} onClick={confirmCashPayment}>{saving ? 'Recording payment…' : 'Confirm cash received'}</button></div>
      </section>
    </div>}
  </section>;
}
function Radiographs() { return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">IMAGING</span><h2>Radiograph gallery</h2></div><button className="primary-button"><FileImage size={17} /> Upload image</button></div><div className="upload-placeholder"><FileImage size={30} /><h3>No radiographs uploaded yet</h3><p>Attach X-ray images to a patient record from the clinical visit.</p><button className="secondary-button">Choose file</button></div></section>; }

createRoot(document.getElementById('root')).render(<App />);
