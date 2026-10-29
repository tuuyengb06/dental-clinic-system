import React, { useCallback, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, CalendarDays, ChevronDown, CircleDollarSign, ClipboardPlus, FileImage, LayoutDashboard, Menu, Pencil, Plus, Search, ShieldCheck, Stethoscope, Trash2, UserRound, Users, X } from 'lucide-react';
import './styles.css';
import './app.css';

const API = import.meta.env.DEV ? '/api/v1' : (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1');
const AUTH_API_ROOT = API.replace(/\/v1\/?$/, '');
const teethAdult = Array.from({ length: 32 }, (_, i) => ({ id: i + 1, code: `A${String(i + 1).padStart(2, '0')}`, state: i === 6 || i === 18 ? 'Needs care' : 'Healthy' }));
const teethChild = Array.from({ length: 20 }, (_, i) => ({ id: i + 1, code: `C${String(i + 1).padStart(2, '0')}`, state: i === 3 ? 'Monitor' : 'Healthy' }));
const navigationByRole = {
  ADMIN: [
    ['Tổng quan', LayoutDashboard], ['Bệnh nhân', Users], ['Lịch hẹn', CalendarDays], ['Sơ đồ răng', Stethoscope],
    ['Thanh toán', CircleDollarSign], ['X-quang', FileImage], ['Dịch vụ', ClipboardPlus], ['Bác sĩ', UserRound], ['Lễ tân', UserRound]
  ],
  DENTIST: [
    ['Tổng quan', LayoutDashboard], ['Bệnh nhân', Users], ['Lịch hẹn', CalendarDays],
    ['Sơ đồ răng', Stethoscope], ['X-quang', FileImage], ['Bệnh án điện tử', ClipboardPlus]
  ],
  RECEPTIONIST: [
    ['Tổng quan', LayoutDashboard], ['Lễ tân', UserRound], ['Lịch hẹn', CalendarDays], ['Bệnh nhân', Users], ['Thanh toán', CircleDollarSign]
  ]
};

const TOKEN_STORAGE_KEY = 'dms.auth.tokens';
const roleLabels = {
  ADMIN: 'Quản trị viên',
  DENTIST: 'Bác sĩ',
  DOCTOR: 'Bác sĩ',
  RECEPTIONIST: 'Lễ tân',
  PATIENT: 'Bệnh nhân'
};

function displayRole(role) {
  const normalizedRole = String(role || '').toUpperCase();
  return roleLabels[normalizedRole] || role || 'Chưa xác định';
}

function displayAppointmentStatus(status) {
  const labels = {
    pending: 'Chờ xác nhận',
    confirmed: 'Đã xác nhận',
    completed: 'Đã hoàn thành',
    cancelled: 'Đã hủy',
    scheduled: 'Đã lên lịch',
    draft: 'Bản nháp',
    active: 'Đang thực hiện',
    issued: 'Đã phát hành',
    paid: 'Đã thanh toán',
    unpaid: 'Chưa thanh toán',
    partially_paid: 'Đã thanh toán một phần',
    in_progress: 'Đang thực hiện',
    planned: 'Đã lên kế hoạch',
    done: 'Hoàn tất'
  };
  const normalizedStatus = String(status || '').toLowerCase().replace(/[\s-]+/g, '_');
  return labels[normalizedStatus] || status || 'Chưa xác định';
}

function displayToothState(state) {
  return ({
    Healthy: 'Khỏe mạnh',
    'Needs care': 'Cần điều trị',
    Monitor: 'Cần theo dõi',
    Restored: 'Đã phục hồi'
  })[state] || state;
}

function displayDentition(type) {
  return type === 'CHILD' ? 'Răng trẻ em · 20 răng' : 'Răng người lớn · 32 răng';
}

async function fetchApi(url, options) {
  try {
    return await fetch(url, options);
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error('Không thể kết nối đến hệ thống phòng khám. Vui lòng kiểm tra kết nối.');
    }
    throw error;
  }
}

async function apiRequest(path, { tokens, onTokens, method = 'GET', body } = {}, baseUrl = API) {
  const send = (accessToken) => fetchApi(`${baseUrl}${path}`, {
    method,
    headers: {
      ...(body ? { 'Content-Type': 'application/json' } : {}),
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
    },
    ...(body ? { body: JSON.stringify(body) } : {})
  });

  let response = await send(tokens?.access);
  if (response.status === 401 && tokens?.refresh && onTokens) {
    const refreshed = await fetchApi(`${AUTH_API_ROOT}/auth/token/refresh/`, {
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
  const [section, setSection] = useState('Tổng quan');
  const [patients, setPatients] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [services, setServices] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [teeth, setTeeth] = useState([]);
  const [medicalRecords, setMedicalRecords] = useState([]);
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
        }, AUTH_API_ROOT);
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
    Promise.all([
      apiRequest('/patients/', { tokens, onTokens: updateTokens }),
      apiRequest('/appointments/', { tokens, onTokens: updateTokens }),
      apiRequest('/doctors/', { tokens, onTokens: updateTokens }),
      apiRequest('/services/', { tokens, onTokens: updateTokens }),
      apiRequest('/schedules/', { tokens, onTokens: updateTokens }),
      apiRequest('/teeth/', { tokens, onTokens: updateTokens }),
      recordRequest
    ]).then(([patientData, appointmentData, doctorData, serviceData, scheduleData, toothData, recordData]) => {
      setPatients(patientData);
      setAppointments(appointmentData);
      setDoctors(doctorData);
      setServices(serviceData.filter((service) => service.is_active));
      setSchedules(scheduleData);
      setTeeth(toothData);
      setMedicalRecords(recordData);
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

  async function login(username, password) {
    const nextTokens = await apiRequest('/auth/login/', { method: 'POST', body: { username, password } }, AUTH_API_ROOT);
    const currentUser = await apiRequest('/auth/me/', { tokens: nextTokens }, AUTH_API_ROOT);
    localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(nextTokens));
    setTokens(nextTokens);
    setProfile(currentUser);
    setAuthError('');
  }

  async function register(account) {
    await apiRequest('/auth/register/', { method: 'POST', body: account }, AUTH_API_ROOT);
    await login(account.username, account.password);
  }

  function logout() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setTokens(null);
    setProfile(null);
    setSection('Tổng quan');
    setAuthError('');
  }

  if (!authReady) return <div className="auth-loading">Đang kiểm tra phiên đăng nhập…</div>;
  if (!profile) return <LoginPage onLogin={login} onRegister={register} initialError={authError} />;

  const visiblePatients = patients.filter((patient) => `${patient.full_name} ${patient.patient_code} ${patient.phone}`.toLowerCase().includes(query.toLowerCase()));
  const role = String(profile.role || '').toUpperCase() === 'DOCTOR' ? 'DENTIST' : String(profile.role || '').toUpperCase();
  const nav = navigationByRole[role] || navigationByRole.RECEPTIONIST;
  return <div className="app-shell">
    <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
      <div className="brand"><div className="brand-mark">D</div><div><strong>DMS</strong><span>Quản lý nha khoa</span></div><button className="icon-button close-menu" aria-label="Đóng menu" onClick={() => setMobileOpen(false)}><X size={18} /></button></div>
      <div className="workspace"><span className="eyebrow">Không gian làm việc</span><button className="workspace-button">Phòng khám nha khoa Lotus <ChevronDown size={15} /></button></div>
      <nav aria-label="Điều hướng chính">{nav.map(([name, Icon]) => <button key={name} className={section === name ? 'nav-item active' : 'nav-item'} aria-current={section === name ? 'page' : undefined} onClick={() => { setSection(name); setMobileOpen(false); }}><Icon size={18} /><span>{name}</span>{name === 'Lịch hẹn' && <b>3</b>}</button>)}</nav>
    </aside>
    <main className="main-content">
      <header className="topbar"><button className="icon-button menu-button" aria-label="Mở menu" onClick={() => setMobileOpen(true)}><Menu size={20} /></button><div><span className="eyebrow">{new Date().toLocaleDateString('vi-VN', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })}</span><h1>{section === 'Tổng quan' ? `Xin chào, ${profile.display_name}` : section}</h1></div><div className="topbar-actions"><span className={`api-status ${apiLive ? 'live' : ''}`}><span />{apiLive ? 'Đã kết nối' : 'Đang kết nối'}</span><button className="icon-button" aria-label="Hoạt động"><Activity size={19} /></button><div className="user-card"><div className="avatar">{profile.display_name.split(' ').map((part) => part[0]).slice(-2).join('')}</div><div><strong>{profile.display_name}</strong><span>{displayRole(role)}</span></div><button className="secondary-button" onClick={logout}>Đăng xuất</button></div></div></header>
      {apiError && section !== 'Lịch hẹn' && <div className="api-error" role="alert">{apiError}</div>}
      {section === 'Tổng quan' && <Overview appointments={appointments} patients={patients} setSection={setSection} />}
      {section === 'Bệnh nhân' && <Patients patients={visiblePatients} query={query} setQuery={setQuery} onCreatePatient={createPatient} canCreate={role === 'ADMIN' || role === 'RECEPTIONIST'} />}
      {section === 'Lễ tân' && (role === 'ADMIN' || role === 'RECEPTIONIST') && <Reception tokens={tokens} onTokensChanged={updateTokens} appointments={appointments} setSection={setSection} />}
      {section === 'Lịch hẹn' && <Appointments appointments={appointments} patients={patients} doctors={doctors} services={services} schedules={schedules} role={role} loading={apiLoading} loadError={apiError} onCreateAppointment={createAppointment} onCreateSchedule={createSchedule} onCancelAppointment={cancelAppointment} />}
      {section === 'Bệnh án điện tử' && (role === 'DENTIST' || role === 'ADMIN') && <MedicalRecords appointments={appointments} patients={patients} services={services} teeth={teeth} records={medicalRecords} loading={apiLoading} loadError={apiError} onSave={saveMedicalRecord} />}
      {section === 'Sơ đồ răng' && <ToothChart dentition={dentition} setDentition={setDentition} selectedTooth={selectedTooth} setSelectedTooth={setSelectedTooth} />}
      {section === 'Thanh toán' && <Billing patients={patients} />}
      {section === 'X-quang' && <Radiographs />}
      {section === 'Dịch vụ' && role === 'ADMIN' && <ServiceManagement tokens={tokens} onTokensChanged={updateTokens} />}
      {section === 'Bác sĩ' && role === 'ADMIN' && <DoctorDirectory tokens={tokens} onTokensChanged={updateTokens} />}
    </main>
  </div>;
}

function LoginPage({ onLogin, onRegister, initialError }) {
  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirmation, setPasswordConfirmation] = useState('');
  const [error, setError] = useState(initialError);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    if (mode === 'register' && password !== passwordConfirmation) {
      setError('Mật khẩu xác nhận chưa khớp.');
      return;
    }
    setSubmitting(true);
    try {
      if (mode === 'register') {
        await onRegister({
          username: username.trim(),
          email: email.trim(),
          first_name: firstName.trim(),
          last_name: lastName.trim(),
          password,
          role: 'Patient'
        });
      } else {
        await onLogin(username.trim(), password);
      }
    } catch (authError) {
      setError(authError.message);
    } finally {
      setSubmitting(false);
    }
  }

  return <main className="login-screen">
    <form className="login-card" onSubmit={handleSubmit}>
      <div className="brand-mark">D</div>
      <span className="eyebrow">PHÒNG KHÁM NHA KHOA LOTUS</span>
      <h1>{mode === 'login' ? 'Chào mừng bạn trở lại' : 'Tạo tài khoản bệnh nhân'}</h1>
      <p>{mode === 'login' ? 'Đăng nhập để tiếp tục chăm sóc sức khỏe răng miệng.' : 'Đăng ký tài khoản để thuận tiện theo dõi và đặt lịch khám.'}</p>
      <div className="auth-tabs" role="tablist" aria-label="Chọn hình thức xác thực">
        <button type="button" role="tab" aria-selected={mode === 'login'} className={mode === 'login' ? 'active' : ''} onClick={() => { setMode('login'); setError(''); }}>Đăng nhập</button>
        <button type="button" role="tab" aria-selected={mode === 'register'} className={mode === 'register' ? 'active' : ''} onClick={() => { setMode('register'); setError(''); }}>Đăng ký</button>
      </div>
      {mode === 'register' && <>
        <label htmlFor="register-first-name">Họ và tên đệm</label>
        <input id="register-first-name" autoComplete="family-name" required value={firstName} onChange={(event) => setFirstName(event.target.value)} />
        <label htmlFor="register-last-name">Tên</label>
        <input id="register-last-name" autoComplete="given-name" required value={lastName} onChange={(event) => setLastName(event.target.value)} />
        <label htmlFor="register-email">Địa chỉ email</label>
        <input id="register-email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} />
      </>}
      <label htmlFor="login-username">Tên đăng nhập</label>
      <input id="login-username" autoComplete="username" required value={username} onChange={(event) => setUsername(event.target.value)} />
      <label htmlFor="login-password">Mật khẩu</label>
      <input id="login-password" type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} minLength={mode === 'register' ? 8 : undefined} required value={password} onChange={(event) => setPassword(event.target.value)} />
      {mode === 'register' && <>
        <label htmlFor="register-password-confirmation">Xác nhận mật khẩu</label>
        <input id="register-password-confirmation" type="password" autoComplete="new-password" minLength={8} required value={passwordConfirmation} onChange={(event) => setPasswordConfirmation(event.target.value)} />
      </>}
      {error && <div className="form-error" role="alert">{error}</div>}
      <button className="primary-button login-submit" type="submit" disabled={submitting}>{submitting ? 'Đang xử lý…' : mode === 'login' ? 'Đăng nhập' : 'Đăng ký tài khoản'}</button>
      <span className="auth-note">Chăm sóc nụ cười khỏe mạnh bắt đầu từ hôm nay.</span>
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
    if (!window.confirm(`Bạn có chắc muốn ngừng cung cấp dịch vụ "${service.name}" không?`)) return;
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
      <div><span className="eyebrow">DANH MỤC PHÒNG KHÁM</span><h2>Danh mục dịch vụ</h2></div>
      {!showForm && <button className="primary-button" onClick={startCreate}><Plus size={16} /> Thêm dịch vụ</button>}
    </div>
    {error && <div className="form-error" role="alert">{error}</div>}
    {showForm && <form className="panel management-form" onSubmit={saveService}>
      <h3>{editingId ? 'Chỉnh sửa dịch vụ' : 'Dịch vụ mới'}</h3>
      <div className="form-grid">
        <label>Mã dịch vụ<input required maxLength="30" value={form.code} onChange={(event) => setForm({ ...form, code: event.target.value.toUpperCase() })} /></label>
        <label>Tên dịch vụ<input required maxLength="160" value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label>
        <label>Giá (VNĐ)<input required type="number" min="0" step="1000" value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} /></label>
        <label>Thời lượng (phút)<input required type="number" min="1" value={form.duration_minutes} onChange={(event) => setForm({ ...form, duration_minutes: event.target.value })} /></label>
        <label className="form-wide">Mô tả<textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} /></label>
        <label className="checkbox-field"><input type="checkbox" checked={form.is_active} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} /> Cho phép đặt lịch</label>
      </div>
      <div className="form-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Đang lưu…' : 'Lưu dịch vụ'}</button><button className="secondary-button" type="button" onClick={() => setShowForm(false)}>Hủy</button></div>
    </form>}
    <div className="panel table-panel management-table">
      {loading ? <p className="management-state">Đang tải dịch vụ…</p> : services.length === 0 ? <p className="management-state">Chưa có dịch vụ nào. Hãy thêm dịch vụ để bắt đầu.</p> :
        <table><thead><tr><th>Mã</th><th>Dịch vụ</th><th>Giá</th><th>Thời lượng</th><th>Trạng thái</th><th>Thao tác</th></tr></thead>
          <tbody>{services.map((service) => <tr key={service.id}>
            <td><code>{service.code}</code></td><td><strong>{service.name}</strong><small className="table-description">{service.description || '—'}</small></td>
            <td>{Number(service.price).toLocaleString('vi-VN')} ₫</td><td>{service.duration_minutes} phút</td>
            <td><span className={`pill ${service.is_active ? '' : 'inactive'}`}>{service.is_active ? 'Đang hoạt động' : 'Ngừng hoạt động'}</span></td>
            <td><div className="row-actions"><button className="icon-button" aria-label={`Sửa ${service.name}`} onClick={() => startEdit(service)}><Pencil size={16} /></button>{service.is_active && <button className="icon-button danger-button" aria-label={`Ngừng dịch vụ ${service.name}`} onClick={() => deleteService(service)}><Trash2 size={16} /></button>}</div></td>
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
    <div className="section-toolbar"><div><span className="eyebrow">ĐỘI NGŨ PHÒNG KHÁM</span><h2>Danh sách bác sĩ</h2></div><span className="pill">{doctors.length} bác sĩ</span></div>
    {error && <div className="form-error" role="alert">{error}</div>}
    <div className="panel table-panel management-table">
      {loading ? <p className="management-state">Đang tải danh sách bác sĩ…</p> : doctors.length === 0 ? <p className="management-state">Không tìm thấy bác sĩ.</p> :
        <table><thead><tr><th>Bác sĩ</th><th>Số giấy phép</th><th>Chuyên môn</th><th>Điện thoại</th><th>Vai trò</th></tr></thead>
          <tbody>{doctors.map((doctor) => <tr key={doctor.id}>
            <td><div className="table-person"><div className="small-avatar">{doctor.full_name.split(' ').map((part) => part[0]).slice(-2).join('')}</div><strong>{doctor.full_name}</strong></div></td>
            <td><code>{doctor.license_number}</code></td><td>{doctor.specialization || '—'}</td><td>{doctor.phone || '—'}</td><td><span className="pill">{displayRole(doctor.role)}</span></td>
          </tr>)}</tbody>
        </table>}
    </div>
  </section>;
}

function Overview({ appointments, patients, setSection }) { return <>
  <section className="hero-band"><div><span className="eyebrow warm">TỔNG QUAN HÔM NAY</span><h2>Chăm sóc tận tâm, mỗi ngày.</h2><p>Phòng khám đã sẵn sàng cho một ngày làm việc hiệu quả. Hôm nay có ba lịch hẹn.</p></div><button className="primary-button" onClick={() => setSection('Lịch hẹn')}><CalendarDays size={17} /> Xem lịch làm việc</button></section>
  <section className="metric-grid"><Metric label="Lịch hẹn hôm nay" value="12" detail="3 bệnh nhân đang chờ" accent="blue" icon={CalendarDays} /><Metric label="Bệnh nhân đang theo dõi" value="248" detail="+18 trong tháng này" accent="sage" icon={Users} /><Metric label="Số dư chưa thanh toán" value="₫42,8 triệu" detail="7 kế hoạch thanh toán" accent="gold" icon={CircleDollarSign} /><Metric label="Kế hoạch điều trị" value="36" detail="8 cần xem xét" accent="coral" icon={ClipboardPlus} /></section>
  <div className="content-grid"><section className="panel schedule-panel"><div className="panel-heading"><div><span className="eyebrow">LỊCH HẸN</span><h3>Lịch khám hôm nay</h3></div><button className="text-button" onClick={() => setSection('Lịch hẹn')}>Xem lịch <span>→</span></button></div><div className="appointment-list">{appointments.map((item) => <AppointmentRow key={item.id} item={item} />)}</div></section><section className="panel focus-panel"><div className="panel-heading"><div><span className="eyebrow">HOẠT ĐỘNG PHÒNG KHÁM</span><h3>Tình hình chung</h3></div><ShieldCheck size={19} color="#1d6857" /></div><div className="focus-stat"><span className="focus-icon green"><UserRound size={18} /></span><div><strong>{patients.length} hồ sơ bệnh nhân</strong><span>Đã số hóa và có thể tra cứu</span></div></div><div className="focus-stat"><span className="focus-icon peach"><Stethoscope size={18} /></span><div><strong>2 cảnh báo điều trị</strong><span>Cần bác sĩ xem xét</span></div></div><div className="alert-box"><strong>Kiểm tra thuốc</strong><p>Cần xác nhận dị ứng trước khi kê một đơn thuốc.</p><button onClick={() => setSection('Bệnh nhân')}>Xem hồ sơ →</button></div></section></div>
</>; }
function Metric({ label, value, detail, accent, icon: Icon }) { return <div className={`metric-card ${accent}`}><div className="metric-icon"><Icon size={18} /></div><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>; }
function AppointmentRow({ item, canCancel = false, onCancel, cancelling = false }) {
  const appointmentDate = item.appointment_date || item.start_at;
  const time = appointmentDate && appointmentDate.includes('T')
    ? new Date(appointmentDate).toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
    : appointmentDate;
  const status = String(item.status || '').toLowerCase();
  return <div className="appointment-row">
    <div className="time">{time}</div>
    <div className="appointment-avatar">{(item.patient_name || 'Bệnh nhân').split(' ').map((part) => part[0]).slice(-2).join('')}</div>
    <div className="appointment-info"><strong>{item.patient_name}</strong><span>{item.service_name || item.type || 'Khám răng tổng quát'} · {item.dentist_name}</span></div>
    <span className={`status ${status === 'confirmed' ? 'confirmed' : status === 'completed' ? 'paid' : status === 'cancelled' ? 'inactive' : 'scheduled'}`}>{displayAppointmentStatus(item.status)}</span>
    {canCancel && ['pending', 'confirmed'].includes(status) && <button className="secondary-button cancel-appointment-button" type="button" disabled={cancelling} onClick={() => onCancel?.(item)}>{cancelling ? 'Đang hủy…' : 'Hủy lịch hẹn'}</button>}
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
      <div><span className="eyebrow">DANH SÁCH BỆNH NHÂN</span><h2>Hồ sơ bệnh nhân</h2></div>
      {canCreate && <button className="primary-button" onClick={() => { setShowForm(!showForm); setError(''); }}>
        <UserRound size={17} /> {showForm ? 'Hủy' : 'Thêm bệnh nhân'}
      </button>}
    </div>
    {error && <div className="form-error" role="alert">{error}</div>}
    {showForm && <form className="panel management-form" onSubmit={savePatient}>
      <h3>Tạo hồ sơ bệnh nhân</h3>
      <div className="form-grid">
        <label>Mã bệnh nhân<input required maxLength="20" value={form.patient_code} onChange={(event) => setForm({ ...form, patient_code: event.target.value.trim().toUpperCase() })} /></label>
        <label>Họ và tên<input required maxLength="160" value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} /></label>
        <label>Số điện thoại<input maxLength="30" value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} /></label>
        <label>Ngày sinh<input type="date" value={form.date_of_birth} onChange={(event) => setForm({ ...form, date_of_birth: event.target.value })} /></label>
        <label>Bộ răng<select value={form.dentition_type} onChange={(event) => setForm({ ...form, dentition_type: event.target.value })}><option value="ADULT">Người lớn · 32 răng</option><option value="CHILD">Trẻ em · 20 răng</option></select></label>
        <label>Dị ứng<textarea value={form.allergies} onChange={(event) => setForm({ ...form, allergies: event.target.value })} /></label>
        <label className="form-wide">Tiền sử bệnh<textarea value={form.medical_history} onChange={(event) => setForm({ ...form, medical_history: event.target.value })} /></label>
      </div>
      <div className="form-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Đang lưu…' : 'Tạo hồ sơ bệnh nhân'}</button></div>
    </form>}
    {selectedPatient && <section className="panel patient-profile">
      <div className="panel-heading"><div><span className="eyebrow">HỒ SƠ BỆNH NHÂN</span><h3>{selectedPatient.full_name}</h3></div><button className="secondary-button" onClick={() => setSelectedPatient(null)}>Đóng</button></div>
      <div className="patient-profile-grid">
        <div><span>Mã bệnh nhân</span><strong>{selectedPatient.patient_code}</strong></div>
        <div><span>Số điện thoại</span><strong>{selectedPatient.phone || '—'}</strong></div>
        <div><span>Ngày sinh</span><strong>{selectedPatient.date_of_birth ? new Date(`${selectedPatient.date_of_birth}T00:00:00`).toLocaleDateString('vi-VN') : '—'}</strong></div>
        <div><span>Bộ răng</span><strong>{displayDentition(selectedPatient.dentition_type)}</strong></div>
        <div><span>Dị ứng</span><p>{selectedPatient.allergies || 'Chưa ghi nhận dị ứng'}</p></div>
        <div><span>Tiền sử bệnh</span><p>{selectedPatient.medical_history || 'Chưa ghi nhận tiền sử bệnh'}</p></div>
      </div>
    </section>}
    <div className="search-field"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Tìm theo tên, mã bệnh nhân hoặc số điện thoại" /></div>
    <div className="panel table-panel">
      {patients.length === 0 ? <p className="management-state">{query ? 'Không tìm thấy bệnh nhân phù hợp.' : 'Chưa có hồ sơ bệnh nhân.'}</p> :
        <table><thead><tr><th>Bệnh nhân</th><th>Mã</th><th>Điện thoại</th><th>Bộ răng</th><th>Dị ứng</th><th>Hồ sơ</th></tr></thead>
          <tbody>{patients.map((patient) => <tr key={patient.id}>
            <td><div className="table-person"><div className="small-avatar">{patient.full_name.split(' ').map((part) => part[0]).slice(-2).join('')}</div><strong>{patient.full_name}</strong></div></td>
            <td><code>{patient.patient_code}</code></td><td>{patient.phone || '—'}</td>
            <td><span className="pill">{displayDentition(patient.dentition_type)}</span></td>
            <td>{patient.allergies || 'Không ghi nhận dị ứng'}</td>
            <td><button className="text-button" onClick={() => setSelectedPatient(patient)}>Xem hồ sơ</button></td>
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
      setError('Vui lòng điền đầy đủ các trường bắt buộc, bao gồm cả lý do khám.');
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
      setSuccess(`Đã gửi yêu cầu đặt lịch${patientName ? ` cho bệnh nhân ${patientName}` : ''}. Lịch hẹn mới đã được cập nhật trong ngày đã chọn.`);
      setBooking((current) => ({ ...current, patient: '', notes: '' }));
    } catch (saveError) {
      setError(saveError.message === 'Failed to fetch'
        ? 'Không thể kết nối đến hệ thống phòng khám. Vui lòng kiểm tra kết nối và thử lại.'
        : saveError.message || 'Không thể gửi yêu cầu đặt lịch. Vui lòng thử lại.');
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
      setSuccess(`Đã hủy lịch hẹn của bệnh nhân ${cancellationTarget.patient_name}.`);
      setCancellationTarget(null);
    } catch (cancelError) {
      setCancellationError(cancelError.message === 'Failed to fetch'
        ? 'Không thể kết nối đến hệ thống phòng khám. Vui lòng kiểm tra kết nối và thử lại.'
        : cancelError.message || 'Không thể hủy lịch hẹn này. Vui lòng thử lại.');
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
      <div><span className="eyebrow">LỊCH LÀM VIỆC PHÒNG KHÁM</span><h2>Lịch hẹn và ca làm việc</h2></div>
      <div className="calendar-actions">
        {isReceptionRole && <button className="secondary-button" onClick={() => { setScheduleOpen(!scheduleOpen); setError(''); }}>{scheduleOpen ? 'Đóng biểu mẫu ca làm' : 'Thêm ca làm'}</button>}
        {isReceptionRole && <button className="primary-button" onClick={() => openBooking(calendarDate, '09:00')}><CalendarDays size={17} /> Đặt lịch hẹn</button>}
      </div>
    </div>
    {success && <div className="form-success" role="status">{success}</div>}
    {error && <div className="form-error" role="alert">{error}</div>}
    {cancellationTarget && <div className="confirmation-backdrop">
      <section className="panel cancellation-dialog" role="dialog" aria-modal="true" aria-labelledby="cancel-dialog-title">
        <h3 id="cancel-dialog-title">Bạn có chắc muốn hủy lịch hẹn này?</h3>
        <p>{cancellationTarget.patient_name} · {new Date(cancellationTarget.appointment_date || cancellationTarget.start_at).toLocaleString('vi-VN')}</p>
        <p className="management-hint">Chỉ có thể hủy lịch đang chờ xác nhận hoặc đã xác nhận.</p>
        {cancellationError && <div className="form-error" role="alert">{cancellationError}</div>}
        <div className="form-actions">
          <button className="danger-button secondary-button" type="button" disabled={cancelling} onClick={confirmCancellation}>{cancelling ? 'Đang hủy…' : 'Xác nhận hủy'}</button>
          <button className="secondary-button" type="button" disabled={cancelling} onClick={() => { setCancellationTarget(null); setCancellationError(''); }}>Giữ lịch hẹn</button>
        </div>
      </section>
    </div>}
    {scheduleOpen && <form className="panel management-form" onSubmit={submitSchedule}>
      <h3>Thiết lập ca làm việc của bác sĩ</h3>
      <div className="form-grid">
        <label>Bác sĩ<select required value={schedule.doctor} onChange={(event) => setSchedule({ ...schedule, doctor: event.target.value })}><option value="">Chọn bác sĩ</option>{doctors.map((doctor) => <option key={doctor.id} value={doctor.id}>{doctor.full_name}</option>)}</select></label>
        <label>Ngày<input required type="date" value={schedule.work_date} onChange={(event) => setSchedule({ ...schedule, work_date: event.target.value })} /></label>
        <label>Giờ bắt đầu<input required type="time" value={schedule.start_time} onChange={(event) => setSchedule({ ...schedule, start_time: event.target.value })} /></label>
        <label>Giờ kết thúc<input required type="time" value={schedule.end_time} onChange={(event) => setSchedule({ ...schedule, end_time: event.target.value })} /></label>
      </div>
      <div className="form-actions"><button className="primary-button" disabled={saving}>{saving ? 'Đang lưu…' : 'Lưu ca làm việc'}</button></div>
    </form>}
    {bookingOpen && <form className="panel management-form" onSubmit={submitBooking}>
      <h3>Đặt lịch hẹn</h3>
      <div className="form-grid">
        <label>Bệnh nhân<select required value={booking.patient} onChange={(event) => setBooking({ ...booking, patient: event.target.value })}><option value="">Chọn bệnh nhân</option>{patients.map((patient) => <option key={patient.id} value={patient.id}>{patient.full_name} · {patient.patient_code}</option>)}</select></label>
        <label>Bác sĩ<select required value={booking.doctor} onChange={(event) => setBooking({ ...booking, doctor: event.target.value })}><option value="">Chọn bác sĩ</option>{doctors.map((doctor) => <option key={doctor.id} value={doctor.id}>{doctor.full_name}</option>)}</select></label>
        <label>Dịch vụ<select required value={booking.service} onChange={(event) => setBooking({ ...booking, service: event.target.value })}><option value="">Chọn dịch vụ</option>{services.map((service) => <option key={service.id} value={service.id}>{service.name} · {service.duration_minutes} phút</option>)}</select></label>
        <label>Ngày<input required type="date" value={booking.date} onChange={(event) => setBooking({ ...booking, date: event.target.value })} /></label>
        <label>Giờ bắt đầu<input required type="time" value={booking.time} onChange={(event) => setBooking({ ...booking, time: event.target.value })} /></label>
        <label className="booking-reason">Lý do khám<textarea required maxLength={1000} value={booking.notes} onChange={(event) => setBooking({ ...booking, notes: event.target.value })} /></label>
      </div>
      <p className="management-hint">Bác sĩ được chọn cần có ca làm đủ thời lượng dịch vụ. Hệ thống sẽ từ chối các lịch hẹn bị trùng.</p>
      <div className="form-actions"><button className="primary-button" disabled={saving}>{saving ? 'Đang đặt lịch…' : 'Xác nhận đặt lịch'}</button><button className="secondary-button" type="button" onClick={() => setBookingOpen(false)}>Hủy</button></div>
    </form>}
    <div className="calendar-toolbar panel">
      <div className="calendar-navigation">
        <button className="secondary-button" onClick={() => setCalendarDate(new Date(calendarDate.getFullYear(), calendarDate.getMonth(), calendarDate.getDate() - (calendarMode === 'day' ? 1 : 7), 12))}>{calendarMode === 'day' ? 'Ngày trước' : 'Tuần trước'}</button>
        <button className="secondary-button" onClick={() => setCalendarDate(new Date())}>Hôm nay</button>
        <button className="secondary-button" onClick={() => setCalendarDate(new Date(calendarDate.getFullYear(), calendarDate.getMonth(), calendarDate.getDate() + (calendarMode === 'day' ? 1 : 7), 12))}>{calendarMode === 'day' ? 'Ngày sau' : 'Tuần sau'}</button>
      </div>
      <strong>{calendarMode === 'day'
        ? calendarDate.toLocaleDateString('vi-VN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
        : `${days[0].toLocaleDateString('vi-VN', { day: 'numeric', month: 'short' })} – ${days[6].toLocaleDateString('vi-VN', { day: 'numeric', month: 'short', year: 'numeric' })}`}</strong>
      <label className="calendar-filter">Bác sĩ
        <select aria-label="Lọc theo bác sĩ" value={doctorFilter} onChange={(event) => setDoctorFilter(event.target.value)}>
          <option value="">Tất cả bác sĩ</option>
          {doctors.map((doctor) => <option key={doctor.id} value={doctor.id}>{doctor.full_name}</option>)}
        </select>
      </label>
      <div className="calendar-view-switch" role="group" aria-label="Chế độ xem lịch">
        {['day', 'week'].map((mode) => <button key={mode} type="button" className={calendarMode === mode ? 'secondary-button active' : 'secondary-button'} aria-pressed={calendarMode === mode} onClick={() => setCalendarMode(mode)}>{mode === 'day' ? 'Ngày' : 'Tuần'}</button>)}
      </div>
      <input aria-label="Chọn ngày" type="date" value={dateKey(calendarDate)} onChange={(event) => { if (event.target.value) setCalendarDate(new Date(`${event.target.value}T12:00:00`)); }} />
    </div>
    {loadError && <div className="form-error" role="alert">Không thể tải lịch: {loadError}</div>}
    {doctors.length === 0 && !loading && !loadError && <div className="management-state" role="status">Chưa có hồ sơ bác sĩ.</div>}
    {loading ? <div className="panel management-state" role="status">Đang tải lịch hẹn và ca làm việc…</div> :
      loadError ? <div className="panel management-state">Không có dữ liệu lịch. Vui lòng kiểm tra kết nối và thử lại.</div> :
      <>
        {!visibleSchedules.length && !visibleAppointments.length && <div className="panel management-state" role="status">Không có ca làm hoặc lịch hẹn trong {calendarMode === 'day' ? 'ngày' : 'tuần'} này.</div>}
        <div className="calendar-legend" aria-label="Chú giải lịch">
          <span><i className="legend-shift" /> Giờ làm việc của bác sĩ</span>
          <span><i className="legend-unavailable" /> Ngoài giờ làm việc</span>
          <span><i className="legend-appointment" /> Lịch hẹn</span>
        </div>
        <div className="panel timetable-panel">
          <div className={`timetable-grid ${calendarMode === 'day' ? 'day-view' : ''}`} style={{ '--calendar-day-count': days.length }}>
            <div className="timetable-head timetable-time">Giờ</div>
            {days.map((date) => <div className="timetable-head" key={dateKey(date)}><strong>{date.toLocaleDateString('vi-VN', { weekday: 'short' })}</strong><span>{date.toLocaleDateString('vi-VN', { day: 'numeric', month: 'short' })}</span></div>)}
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
                      <strong>{start.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}{end && !Number.isNaN(end.getTime()) ? `–${end.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}` : ''} · {item.patient_name}</strong>
                      <span>{item.service_name || item.type || 'Khám răng'} · {item.dentist_name}</span>
                      <small>{displayAppointmentStatus(item.status || 'scheduled')}</small>
                      {item.notes && <small className="calendar-event-reason">Lý do: {item.notes}</small>}
                    </div>;
                  })}
                  {!events.length && !slotBusy && isReceptionRole && shifts.length > 0 && <button aria-label={`Đặt lịch ngày ${key} lúc ${time}`} className="empty-slot" onClick={() => openBooking(date, time)} title="Đặt lịch hẹn vào khung giờ còn trống này">+</button>}
                </div>;
              })}
            </div>)}
          </div>
        </div>
        <div className="panel appointment-list-panel"><div className="panel-heading"><div><span className="eyebrow">{calendarMode === 'day' ? 'NGÀY ĐANG CHỌN' : 'TUẦN ĐANG CHỌN'}</span><h3>Lịch hẹn trong chế độ xem này</h3></div></div>
          {visibleAppointments.length ? <div className="appointment-list">{[...visibleAppointments].sort((a, b) => new Date(a.appointment_date || a.start_at) - new Date(b.appointment_date || b.start_at)).map((item) => <AppointmentRow key={item.id} item={item} canCancel={isReceptionRole} onCancel={(target) => { setCancellationTarget(target); setCancellationError(''); setSuccess(''); }} />)}</div> : <p className="management-state">Không có lịch hẹn trong {calendarMode === 'day' ? 'ngày' : 'tuần'} này.</p>}
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
      setError('Vui lòng nhập mã, tên hoặc số điện thoại bệnh nhân bằng chữ cái, chữ số, khoảng trắng và các ký tự phân tách thông dụng.');
      return;
    }

    setLoading(true);
    try {
      const result = await apiRequest(`/patients/?search=${encodeURIComponent(searchTerm)}`, {
        tokens,
        onTokens: onTokensChanged
      });
      if (!Array.isArray(result)) {
        throw new Error('Hệ thống trả về kết quả tra cứu bệnh nhân không hợp lệ.');
      }
      setPatients(result);
      setSelectedPatientId(result.length === 1 ? result[0].id : null);
    } catch (searchError) {
      setError(searchError.message || 'Không thể tìm kiếm bệnh nhân. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  }

  function formatDate(value) {
    if (!value) return 'Chưa ghi nhận';
    const date = new Date(`${value}T00:00:00`);
    return Number.isNaN(date.getTime()) ? 'Chưa ghi nhận' : date.toLocaleDateString('vi-VN');
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
      <div><span className="eyebrow">QUẦY LỄ TÂN</span><h2>Tiếp nhận bệnh nhân</h2></div>
      {selectedPatient && <button className="primary-button" onClick={() => setSection('Lịch hẹn')}><CalendarDays size={17} /> Tiếp tục đặt lịch</button>}
    </div>
    <form className="panel reception-search" onSubmit={searchPatients} noValidate>
      <label htmlFor="reception-search">Tìm bệnh nhân hiện có</label>
      <p>Tìm theo mã bệnh nhân, họ tên đầy đủ hoặc một phần, hay số điện thoại.</p>
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
          placeholder="Ví dụ: DMS-0001, Nguyễn Minh Anh hoặc số điện thoại"
          autoComplete="off"
        />
        <button className="primary-button" type="submit" disabled={loading}>{loading ? 'Đang tìm…' : 'Tìm kiếm'}</button>
      </div>
      {error && <div className="form-error" role="alert">{error}</div>}
    </form>

    {loading && <div className="panel reception-state" role="status">Đang tìm hồ sơ bệnh nhân…</div>}
    {!loading && !error && !term.trim() && <div className="panel reception-state">Nhập mã, tên hoặc số điện thoại bệnh nhân để bắt đầu.</div>}
    {!loading && !error && term.trim() && !searched && <div className="panel reception-state">Nhấn Tìm kiếm để tra cứu bệnh nhân.</div>}
    {!loading && !error && searched && patients.length === 0 && <div className="panel reception-state" role="status">Không tìm thấy bệnh nhân. Vui lòng kiểm tra thông tin và tìm lại.</div>}
    {!loading && !error && patients.length > 0 && <div className="reception-results-layout">
      <section className="panel reception-results" aria-label="Kết quả tìm kiếm bệnh nhân">
        <div className="panel-heading"><div><span className="eyebrow">KẾT QUẢ TÌM KIẾM</span><h3>Tìm thấy {patients.length} bệnh nhân</h3></div></div>
        {patients.map((patient) => <button
          type="button"
          key={patient.id}
          className={`reception-result ${selectedPatientId === patient.id ? 'selected' : ''}`}
          onClick={() => setSelectedPatientId(patient.id)}
        >
          <span className="small-avatar">{patient.full_name.split(' ').map((part) => part[0]).slice(-2).join('')}</span>
          <span className="reception-result-info"><strong>{patient.full_name}</strong><small>{patient.patient_code} · {patient.phone || 'Chưa có số điện thoại'}</small></span>
          <span className="reception-result-arrow">›</span>
        </button>)}
      </section>
      {selectedPatient && <section className="panel reception-profile">
        <div className="panel-heading"><div><span className="eyebrow">HỒ SƠ BỆNH NHÂN</span><h3>{selectedPatient.full_name}</h3></div><span className="pill">{selectedPatient.patient_code}</span></div>
        <dl className="reception-profile-grid">
          <div><dt>Điện thoại</dt><dd>{selectedPatient.phone || 'Chưa ghi nhận'}</dd></div>
          <div><dt>Ngày sinh</dt><dd>{formatDate(selectedPatient.date_of_birth)}{patientAge(selectedPatient.date_of_birth) !== null ? ` · ${patientAge(selectedPatient.date_of_birth)} tuổi` : ''}</dd></div>
          <div><dt>Bộ răng</dt><dd>{displayDentition(selectedPatient.dentition_type)}</dd></div>
          <div className="reception-medical-alert"><dt>Dị ứng</dt><dd>{selectedPatient.allergies || 'Chưa ghi nhận'}</dd></div>
          <div className="profile-wide"><dt>Tiền sử bệnh</dt><dd>{selectedPatient.medical_history || 'Chưa ghi nhận'}</dd></div>
        </dl>
        <div className="reception-visit-history">
          <span className="eyebrow">LỊCH SỬ KHÁM</span>
          {patientAppointments.length
            ? patientAppointments.map((appointment) => <div key={appointment.id}><strong>{new Date(appointment.appointment_date || appointment.start_at).toLocaleString('vi-VN')}</strong><span>{appointment.service_name || appointment.type || 'Khám răng'} · {displayAppointmentStatus(appointment.status)}</span></div>)
            : <p>Chưa có lịch hẹn.</p>}
        </div>
      </section>}
      {!selectedPatient && <div className="panel reception-state">Chọn bệnh nhân trong danh sách để xem thông tin tiếp nhận.</div>}
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
      setSuccess('Đã lưu hồ sơ bệnh án.');
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return <section className="page-section management-page">
    <div className="section-toolbar"><div><span className="eyebrow">KHÔNG GIAN LÂM SÀNG</span><h2>Hồ sơ bệnh án điện tử</h2></div></div>
    {loading && <div className="panel management-state" role="status">Đang tải lịch hẹn, hồ sơ, sơ đồ răng và dịch vụ…</div>}
    {loadError && <div className="form-error" role="alert">Không thể tải dữ liệu bệnh án điện tử: {loadError}</div>}
    {error && <div className="form-error" role="alert">{error}</div>}
    {success && <div className="form-success" role="status">{success}</div>}
    {!loading && !loadError && !eligibleAppointments.length && <div className="panel management-state">Không có lịch hẹn để lập hồ sơ bệnh án.</div>}
    {!loading && !loadError && eligibleAppointments.length > 0 && selectedAppointment && <form className="panel management-form emr-form" onSubmit={saveRecord}>
      <label className="emr-appointment">Lịch hẹn đang khám
        <select value={appointmentId} onChange={(event) => { setAppointmentId(event.target.value); setSuccess(''); }}>
          {eligibleAppointments.map((item) => <option key={item.id} value={item.id}>{new Date(item.appointment_date || item.start_at).toLocaleString('vi-VN')} · {item.patient_name} · {item.dentist_name}</option>)}
        </select>
      </label>
      {selectedPatient && <div className="emr-patient-alert">
        <div className="emr-patient-heading"><strong>{selectedPatient.full_name}</strong><span>{selectedPatient.patient_code} · {selectedPatient.phone || 'Chưa có số điện thoại'}</span></div>
        <div className="emr-appointment-details">
          <span><strong>Lịch hẹn:</strong> {new Date(selectedAppointment.appointment_date || selectedAppointment.start_at).toLocaleString('vi-VN')}</span>
          <span><strong>Bác sĩ:</strong> {selectedAppointment.dentist_name || 'Chưa ghi nhận'}</span>
          <span><strong>Trạng thái:</strong> {displayAppointmentStatus(selectedAppointment.status)}</span>
        </div>
        <p><strong>Dị ứng:</strong> {selectedPatient.allergies || 'Chưa ghi nhận'} · <strong>Tiền sử bệnh:</strong> {selectedPatient.medical_history || 'Chưa ghi nhận'}</p>
      </div>}
      <label>Chẩn đoán<textarea required rows="3" value={form.diagnosis} onChange={(event) => setForm({ ...form, diagnosis: event.target.value })} /></label>
      <label>Phác đồ điều trị<textarea required rows="3" value={form.treatment_plan} onChange={(event) => setForm({ ...form, treatment_plan: event.target.value })} /></label>
      <div className="emr-selection-grid">
        <fieldset className="emr-teeth-fieldset">
          <legend>Răng đã khám hoặc điều trị ({form.teeth.length} đã chọn)</legend>
          {!patientTeeth.length ? <p className="emr-empty-options">Không có dữ liệu sơ đồ răng cho bộ răng của bệnh nhân này.</p> : <div className="emr-tooth-chart">
            <span className="emr-arch-label">HÀM TRÊN</span>
            <div className="emr-tooth-row">{patientTeeth.slice(0, midpoint).map((tooth) => <button key={tooth.id} type="button" aria-pressed={form.teeth.includes(tooth.id)} className={`emr-tooth ${form.teeth.includes(tooth.id) ? 'selected' : ''}`} onClick={() => toggleSelection('teeth', tooth.id)}>{tooth.code}</button>)}</div>
            <div className="emr-mouth-line" />
            <div className="emr-tooth-row lower">{patientTeeth.slice(midpoint).reverse().map((tooth) => <button key={tooth.id} type="button" aria-pressed={form.teeth.includes(tooth.id)} className={`emr-tooth ${form.teeth.includes(tooth.id) ? 'selected' : ''}`} onClick={() => toggleSelection('teeth', tooth.id)}>{tooth.code}</button>)}</div>
            <span className="emr-arch-label lower">HÀM DƯỚI</span>
          </div>}
        </fieldset>
        <fieldset>
          <legend>Dịch vụ điều trị ({form.services.length} đã chọn)</legend>
          {!services.length ? <p className="emr-empty-options">Hiện không có dịch vụ nào đang hoạt động.</p> : <div className="service-options">
            {services.map((service) => <label key={service.id}>
              <input type="checkbox" checked={form.services.includes(service.id)} onChange={() => toggleSelection('services', service.id)} />
              <span><strong>{service.name}</strong><small>{service.description || 'Chưa có mô tả dịch vụ'} · {service.duration_minutes} phút</small></span>
              <small>{Number(service.price).toLocaleString('vi-VN')} ₫</small>
            </label>)}
          </div>}
        </fieldset>
      </div>
      <label>Đơn thuốc<textarea rows="2" value={form.prescription} onChange={(event) => setForm({ ...form, prescription: event.target.value })} /></label>
      <label>Ghi chú lâm sàng<textarea rows="2" value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} /></label>
      <div className="form-actions"><button className="primary-button" disabled={saving || !appointmentId}>{saving ? 'Đang lưu…' : record ? 'Cập nhật bệnh án' : 'Lưu bệnh án'}</button></div>
    </form>}
  </section>;
}
function ToothChart({ dentition, setDentition, selectedTooth, setSelectedTooth }) { const teeth = dentition === 'ADULT' ? teethAdult : teethChild; return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">HỒ SƠ LÂM SÀNG</span><h2>Sơ đồ răng tương tác</h2></div><div className="segmented"><button className={dentition === 'ADULT' ? 'selected' : ''} onClick={() => setDentition('ADULT')}>Người lớn · 32 răng</button><button className={dentition === 'CHILD' ? 'selected' : ''} onClick={() => setDentition('CHILD')}>Trẻ em · 20 răng</button></div></div><div className="chart-layout"><div className="panel tooth-panel"><div className="chart-header"><div><strong>Nguyễn Minh Anh</strong><span>DMS-0001 · {dentition === 'ADULT' ? 'Răng vĩnh viễn' : 'Răng sữa'}</span></div><span className="status confirmed">Đang điều trị</span></div><div className="mouth-label">HÀM TRÊN</div><div className={`teeth-grid ${dentition.toLowerCase()}`}>{teeth.slice(0, Math.ceil(teeth.length / 2)).map((tooth) => <Tooth key={tooth.id} tooth={tooth} selected={selectedTooth === tooth.id} onClick={() => setSelectedTooth(tooth.id)} />)}</div><div className="mouth-line" /><div className={`teeth-grid lower ${dentition.toLowerCase()}`}>{teeth.slice(Math.ceil(teeth.length / 2)).reverse().map((tooth) => <Tooth key={tooth.id} tooth={tooth} selected={selectedTooth === tooth.id} onClick={() => setSelectedTooth(tooth.id)} />)}</div><div className="mouth-label lower-label">HÀM DƯỚI</div><div className="chart-legend"><span><i className="dot healthy" />Khỏe mạnh</span><span><i className="dot care" />Cần điều trị</span><span><i className="dot monitor" />Cần theo dõi</span></div></div><aside className="panel tooth-detail"><span className="eyebrow">RĂNG ĐANG CHỌN</span>{selectedTooth ? <><div className="tooth-number">{teeth.find((tooth) => tooth.id === selectedTooth)?.code}</div><h3>Tình trạng lâm sàng</h3><p>Cập nhật tình trạng răng và thêm ghi chú điều trị vào hồ sơ bệnh nhân.</p><select defaultValue="Healthy"><option value="Healthy">Khỏe mạnh</option><option value="Needs care">Cần điều trị</option><option value="Monitor">Cần theo dõi</option><option value="Restored">Đã phục hồi</option></select><textarea placeholder="Thêm ghi chú lâm sàng..." /><button className="primary-button full">Lưu tình trạng</button></> : <div className="empty-detail"><Stethoscope size={28} /><p>Chọn một chiếc răng để xem hồ sơ lâm sàng.</p></div>}</aside></div></section>; }
function Tooth({ tooth, selected, onClick }) { return <button aria-label={`${tooth.code}: ${displayToothState(tooth.state)}`} onClick={onClick} className={`tooth ${tooth.state.toLowerCase().replace(' ', '-')} ${selected ? 'selected' : ''}`}><span>{tooth.code.slice(1)}</span><div className="tooth-shape" /></button>; }
function Billing({ patients }) { return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">TÀI CHÍNH</span><h2>Thanh toán và trả góp</h2></div><button className="primary-button"><CircleDollarSign size={17} /> Tạo hóa đơn</button></div><div className="metric-grid compact"><Metric label="Còn phải thu" value="42,8 triệu ₫" detail="Trong 18 hóa đơn" accent="gold" icon={CircleDollarSign} /><Metric label="Đến hạn tuần này" value="8,4 triệu ₫" detail="6 đợt thanh toán" accent="coral" icon={CalendarDays} /><Metric label="Đã thu hôm nay" value="5,2 triệu ₫" detail="11 khoản thanh toán" accent="sage" icon={ShieldCheck} /></div><div className="panel table-panel"><table><thead><tr><th>Hóa đơn</th><th>Bệnh nhân</th><th>Tổng cộng</th><th>Đã thanh toán</th><th>Trạng thái</th></tr></thead><tbody>{patients.slice(0, 3).map((p, i) => <tr key={p.id}><td><code>INV-000{i + 1}</code></td><td><strong>{p.full_name}</strong></td><td>{['3.500.000', '1.200.000', '850.000'][i]} ₫</td><td>{['1.500.000', '1.200.000', '350.000'][i]} ₫</td><td><span className={`status ${i === 1 ? 'paid' : 'scheduled'}`}>{i === 1 ? 'Đã thanh toán' : 'Trả góp'}</span></td></tr>)}</tbody></table></div></section>; }
function Radiographs() { return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">CHẨN ĐOÁN HÌNH ẢNH</span><h2>Thư viện ảnh X-quang</h2></div><button className="primary-button"><FileImage size={17} /> Tải ảnh lên</button></div><div className="upload-placeholder"><FileImage size={30} /><h3>Chưa có ảnh X-quang</h3><p>Đính kèm ảnh X-quang vào hồ sơ bệnh nhân trong buổi khám.</p><button className="secondary-button">Chọn tệp</button></div></section>; }

createRoot(document.getElementById('root')).render(<App />);
