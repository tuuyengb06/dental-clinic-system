import React, { useCallback, useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, CalendarDays, ChevronDown, CircleDollarSign, ClipboardPlus, Copy, FileImage, LayoutDashboard, Menu, MessageCircle, Pencil, Plus, Search, Send, ShieldCheck, Stethoscope, Trash2, UserRound, Users, X } from 'lucide-react';
import './styles.css';
import './app.css';

const API = import.meta.env.DEV ? '/api/v1' : (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1');
const API_ROOT = API.replace(/\/v1\/?$/, '');
const AI_CHAT_API = `${API_ROOT}/ai/chat`;
const navigationByRole = {
  ADMIN: [
    ['Overview', LayoutDashboard], ['Patients', Users], ['Appointments', CalendarDays], ['Tooth chart', Stethoscope],
    ['Follow-up reminders', MessageCircle], ['Billing', CircleDollarSign], ['Radiographs', FileImage], ['Services', ClipboardPlus], ['Doctors', UserRound], ['Reception', UserRound], ['EMR', ClipboardPlus], ['Treatment plans', ClipboardPlus]
  ],
  DENTIST: [
    ['Overview', LayoutDashboard], ['Patients', Users], ['Appointments', CalendarDays],
    ['Tooth chart', Stethoscope], ['Radiographs', FileImage], ['EMR', ClipboardPlus], ['Treatment plans', ClipboardPlus]
  ],
  RECEPTIONIST: [
    ['Overview', LayoutDashboard], ['Reception', UserRound], ['Appointments', CalendarDays], ['Follow-up reminders', MessageCircle], ['Patients', Users], ['Billing', CircleDollarSign]
  ],
  PATIENT: [['Portal', LayoutDashboard]]
};

const navigationLabels = {
  Overview: 'Tổng quan', Patients: 'Bệnh nhân', Appointments: 'Lịch hẹn',
  'Tooth chart': 'Sơ đồ răng', 'Follow-up reminders': 'Nhắc tái khám',
  Billing: 'Thanh toán', Radiographs: 'Ảnh X-quang', Services: 'Dịch vụ',
  Doctors: 'Bác sĩ', Reception: 'Lễ tân', EMR: 'Hồ sơ khám',
  'Treatment plans': 'Kế hoạch điều trị', Portal: 'Cổng bệnh nhân'
};
const sectionPaths = {
  Overview: '/tong-quan',
  Patients: '/benh-nhan',
  Appointments: '/lich-hen',
  'Tooth chart': '/so-do-rang',
  'Follow-up reminders': '/nhac-tai-kham',
  Billing: '/thanh-toan',
  Radiographs: '/anh-x-quang',
  Services: '/dich-vu',
  Doctors: '/bac-si',
  Reception: '/le-tan',
  EMR: '/ho-so-kham',
  'Treatment plans': '/ke-hoach-dieu-tri',
  Portal: '/cong-benh-nhan'
};
const sectionByPath = Object.fromEntries(
  Object.entries(sectionPaths).map(([section, path]) => [path, section])
);
const roleLabels = {
  ADMIN: 'Quản trị viên', DENTIST: 'Bác sĩ',
  RECEPTIONIST: 'Lễ tân', PATIENT: 'Bệnh nhân'
};
const catalogTranslations = {
  'Dental consultation': 'Tư vấn nha khoa',
  'Scaling and polishing': 'Cạo vôi và đánh bóng răng',
  'Tooth filling': 'Trám răng',
  'Simple extraction': 'Nhổ răng đơn giản',
  'Dental X-ray': 'Chụp X-quang răng',
  'General dentistry': 'Nha khoa tổng quát',
  'Routine dental check-up': 'Khám răng định kỳ',
  'Routine dental care': 'Chăm sóc răng miệng định kỳ'
};

function localizeCatalogText(value) {
  return Object.entries(catalogTranslations).reduce(
    (text, [source, translation]) => text.replaceAll(source, translation),
    String(value || '')
  );
}

const TOKEN_STORAGE_KEY = 'dms.auth.tokens';

function defaultSectionForRole(role) {
  return String(role || '').toUpperCase() === 'PATIENT' ? 'Portal' : 'Overview';
}

function sectionForPath(pathname) {
  return sectionByPath[pathname.replace(/\/+$/, '') || '/'] || null;
}

function sectionAllowedForRole(section, role) {
  const normalizedRole = String(role || '').toUpperCase();
  const navigationRole = normalizedRole === 'DOCTOR' ? 'DENTIST' : normalizedRole;
  return (navigationByRole[navigationRole] || []).some(([name]) => name === section);
}

function localizeApiMessage(message, responseStatus) {
  if (/[à-ỹ]/i.test(message || '')) return message;
  if (responseStatus === 400) {
    const passwordTranslations = [
      [/This password is too short\. It must contain at least (\d+) characters\./gi, (_, length) => `Mật khẩu phải có ít nhất ${length} ký tự.`],
      [/This password is too common\./gi, () => 'Mật khẩu quá phổ biến. Hãy chọn mật khẩu khác.'],
      [/This password is entirely numeric\./gi, () => 'Mật khẩu không được chỉ gồm chữ số.'],
      [/This password is too similar to the .*?\./gi, () => 'Mật khẩu quá giống thông tin tài khoản. Hãy chọn mật khẩu khác.']
    ];
    let translated = String(message || '');
    for (const [pattern, replacement] of passwordTranslations) {
      translated = translated.replace(pattern, replacement);
    }
    if (translated !== message) return translated;
  }
  const messages = {
    400: 'Thông tin chưa hợp lệ. Vui lòng kiểm tra lại nội dung đã nhập.',
    401: 'Tên đăng nhập, mật khẩu không chính xác hoặc phiên đăng nhập đã hết hạn.',
    403: 'Bạn không có quyền thực hiện thao tác này.',
    404: 'Không tìm thấy dữ liệu được yêu cầu.',
    409: 'Dữ liệu bị trùng hoặc xung đột. Vui lòng tải lại và thử lại.',
    413: 'Tệp tải lên vượt quá dung lượng cho phép.',
    429: 'Bạn thao tác quá nhanh. Vui lòng chờ một chút rồi thử lại.',
    500: 'Máy chủ gặp sự cố. Vui lòng thử lại sau.',
    502: 'Dịch vụ đang tạm thời gián đoạn. Vui lòng thử lại sau.',
    503: 'Tính năng hiện chưa được cấu hình hoặc đang tạm thời không khả dụng.'
  };
  return messages[responseStatus] || 'Đã xảy ra lỗi. Vui lòng thử lại.';
}

async function apiRequest(path, { tokens, onTokens, method = 'GET', body, baseUrl = API, responseType = 'json' } = {}) {
  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;
  const sendToBase = (accessToken) => fetch(`${baseUrl}${path}`, {
    method,
    headers: {
      ...(body && !isFormData ? { 'Content-Type': 'application/json' } : {}),
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {})
    },
    ...(body ? { body: isFormData ? body : JSON.stringify(body) } : {})
  });
  const sendRequest = async (request) => {
    try {
      return await request();
    } catch (requestError) {
      if (!(requestError instanceof TypeError)) throw requestError;
      const error = new Error('Không thể kết nối máy chủ. Vui lòng kiểm tra kết nối và thử lại.');
      error.code = 'network_error';
      error.retryable = true;
      throw error;
    }
  };

  let response = await sendRequest(() => sendToBase(tokens?.access));
  if (response.status === 401 && tokens?.refresh && onTokens) {
    const refreshed = await sendRequest(() => fetch(`${API}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: tokens.refresh })
    }));
    if (!refreshed.ok) {
      onTokens(null);
      throw new Error('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
    }
    const nextTokens = { ...tokens, ...(await refreshed.json()) };
    onTokens(nextTokens);
    response = await sendRequest(() => sendToBase(nextTokens.access));
  }

  const payload = response.status === 204
    ? null
    : response.ok && responseType === 'blob'
      ? await response.blob()
      : await response.json().catch(() => null);
  if (!response.ok) {
    const detail = payload?.detail || Object.values(payload || {}).flat().join(' ') || `Yêu cầu thất bại (${response.status}).`;
    const error = new Error(localizeApiMessage(detail, response.status));
    error.code = payload?.code || (response.status === 429 ? 'rate_limited' : undefined);
    error.retryable = payload?.retryable === true || response.status === 429;
    error.status = response.status;
    throw error;
  }
  return payload;
}

function App() {
  const [section, setSection] = useState(
    () => sectionForPath(window.location.pathname) || 'Overview'
  );
  const [patients, setPatients] = useState([]);
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [services, setServices] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [teeth, setTeeth] = useState([]);
  const [medicalRecords, setMedicalRecords] = useState([]);
  const [treatmentPlans, setTreatmentPlans] = useState([]);
  const [followUpAppointments, setFollowUpAppointments] = useState([]);
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
  const [accountSettingsOpen, setAccountSettingsOpen] = useState(false);

  useEffect(() => {
    document.title = 'DMS | Hệ thống quản lý nha khoa';
  }, []);

  const navigateToSection = useCallback((nextSection, { replace = false } = {}) => {
    setSection(nextSection);
    const nextPath = sectionPaths[nextSection];
    if (!nextPath || window.location.pathname === nextPath) return;
    window.history[replace ? 'replaceState' : 'pushState']({}, '', nextPath);
  }, []);

  useEffect(() => {
    function handlePopState() {
      const requestedSection = sectionForPath(window.location.pathname);
      if (!profile) {
        setSection('Overview');
        return;
      }
      navigateToSection(
        requestedSection && sectionAllowedForRole(requestedSection, profile.role)
          ? requestedSection
          : defaultSectionForRole(profile.role),
        { replace: true }
      );
    }

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [navigateToSection, profile]);

  useEffect(() => {
    if (!authReady) return;
    if (!profile) {
      if (window.location.pathname !== '/dang-nhap') {
        window.history.replaceState({}, '', '/dang-nhap');
      }
      return;
    }
    const requestedSection = sectionForPath(window.location.pathname);
    const resolvedSection = requestedSection
      && sectionAllowedForRole(requestedSection, profile.role)
      ? requestedSection
      : defaultSectionForRole(profile.role);
    if (resolvedSection !== section) {
      navigateToSection(resolvedSection, { replace: true });
    } else if (window.location.pathname !== sectionPaths[section]) {
      window.history.replaceState({}, '', sectionPaths[section]);
    }
  }, [authReady, navigateToSection, profile, section]);

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
          const requestedSection = sectionForPath(window.location.pathname);
          navigateToSection(
            requestedSection && sectionAllowedForRole(requestedSection, currentUser.role)
              ? requestedSection
              : defaultSectionForRole(currentUser.role),
            { replace: true }
          );
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
  }, [navigateToSection]);

  useEffect(() => {
    if (!tokens || !profile) return;
    setApiLoading(true);
    const currentRole = String(profile.role || '').toUpperCase();
    const recordRequest = currentRole === 'DENTIST' || currentRole === 'ADMIN'
      ? apiRequest('/medical-records/', { tokens, onTokens: updateTokens })
      : currentRole === 'PATIENT'
        ? apiRequest('/medical-records/', { tokens, onTokens: updateTokens })
      : Promise.resolve([]);
    const billingRequest = currentRole === 'ADMIN' || currentRole === 'RECEPTIONIST'
      ? Promise.all([
        apiRequest('/invoices/', { tokens, onTokens: updateTokens }),
        apiRequest('/invoices/available-records/', { tokens, onTokens: updateTokens })
      ])
      : currentRole === 'PATIENT'
        ? apiRequest('/invoices/', { tokens, onTokens: updateTokens }).then((items) => [items, []])
      : Promise.resolve([[], []]);
    const followUpRequest = currentRole === 'ADMIN' || currentRole === 'RECEPTIONIST'
      ? apiRequest('/follow-up-appointments/', { tokens, onTokens: updateTokens })
      : Promise.resolve([]);
    const treatmentPlanRequest = ['ADMIN', 'DENTIST', 'PATIENT'].includes(currentRole)
      ? apiRequest('/treatment-plans/', { tokens, onTokens: updateTokens })
      : Promise.resolve([]);
    Promise.all([
      apiRequest('/patients/', { tokens, onTokens: updateTokens }),
      apiRequest('/appointments/', { tokens, onTokens: updateTokens }),
      apiRequest('/doctors/', { tokens, onTokens: updateTokens }),
      apiRequest('/services/', { tokens, onTokens: updateTokens }),
      apiRequest('/schedules/', { tokens, onTokens: updateTokens }),
      apiRequest('/teeth/', { tokens, onTokens: updateTokens }),
      recordRequest,
      billingRequest,
      followUpRequest,
      treatmentPlanRequest
    ]).then(([patientData, appointmentData, doctorData, serviceData, scheduleData, toothData, recordData, billingData, followUpData, planData]) => {
      setPatients(patientData);
      setAppointments(appointmentData);
      setDoctors(doctorData);
      setServices(serviceData.filter((service) => service.is_active));
      setSchedules(scheduleData);
      setTeeth(toothData);
      setMedicalRecords(recordData);
      setTreatmentPlans(planData);
      setFollowUpAppointments(followUpData);
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

  async function updatePatient(patientId, updates) {
    const updated = await apiRequest(`/patients/${patientId}/`, {
      tokens,
      onTokens: updateTokens,
      method: 'PATCH',
      body: updates
    });
    setPatients((current) => current.map((patient) => patient.id === updated.id ? updated : patient));
    return updated;
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

  async function createTreatmentPlan(plan) {
    const created = await apiRequest('/treatment-plans/', {
      tokens, onTokens: updateTokens, method: 'POST', body: plan
    });
    setTreatmentPlans((current) => [created, ...current]);
    return created;
  }

  async function updateTreatmentPlan(planId, changes) {
    const updated = await apiRequest(`/treatment-plans/${planId}/`, {
      tokens, onTokens: updateTokens, method: 'PATCH', body: changes
    });
    setTreatmentPlans((current) => current.map((plan) => plan.id === updated.id ? updated : plan));
    return updated;
  }

  async function createTreatmentItem(item) {
    const created = await apiRequest('/treatment-items/', {
      tokens, onTokens: updateTokens, method: 'POST', body: item
    });
    setTreatmentPlans((current) => current.map((plan) => plan.id === created.plan
      ? { ...plan, items: [...plan.items, created] }
      : plan));
    return created;
  }

  async function updateTreatmentItem(itemId, changes) {
    const updated = await apiRequest(`/treatment-items/${itemId}/`, {
      tokens, onTokens: updateTokens, method: 'PATCH', body: changes
    });
    setTreatmentPlans((current) => current.map((plan) => ({
      ...plan,
      items: plan.items.map((item) => item.id === updated.id ? updated : item)
    })));
    return updated;
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

  async function generateAiSummary(recordId) {
    return apiRequest(`/medical-records/${recordId}/ai-summary/`, {
      tokens,
      onTokens: updateTokens,
      method: 'POST',
      body: {}
    });
  }

  async function generateFollowUpReminder(recordId) {
    return apiRequest('/ai/generate-reminder', {
      tokens,
      onTokens: updateTokens,
      method: 'POST',
      body: { medical_record_id: recordId },
      baseUrl: API_ROOT
    });
  }

  async function login(username, password) {
    const nextTokens = await apiRequest('/auth/token/', { method: 'POST', body: { username, password } });
    const currentUser = await apiRequest('/auth/me/', { tokens: nextTokens });
    localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(nextTokens));
    setTokens(nextTokens);
    setProfile(currentUser);
    navigateToSection(defaultSectionForRole(currentUser.role), { replace: true });
    setAuthError('');
  }

  async function updateAccount(account) {
    const updatedProfile = await apiRequest('/auth/account/', {
      tokens,
      onTokens: updateTokens,
      method: 'PATCH',
      body: account
    });
    setProfile(updatedProfile);
    return updatedProfile;
  }

  async function resetAccountPassword(accountType, profileId, newPassword) {
    return apiRequest(`/auth/users/${accountType}/${profileId}/reset-password/`, {
      tokens,
      onTokens: updateTokens,
      method: 'POST',
      body: { new_password: newPassword }
    });
  }

  async function registerPatient(registration) {
    await apiRequest('/auth/register/', { method: 'POST', body: registration });
    await login(registration.username, registration.password);
  }

  function logout() {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setTokens(null);
    setProfile(null);
    window.history.replaceState({}, '', '/dang-nhap');
    setSection('Overview');
    setAuthError('');
  }

  if (!authReady) return <><div className="auth-loading">Đang kiểm tra phiên đăng nhập…</div><ChatWidget /></>;
  if (!profile) return <><LoginPage onLogin={login} onRegister={registerPatient} initialError={authError} /><ChatWidget /></>;

  const visiblePatients = patients.filter((patient) => `${patient.full_name} ${patient.patient_code} ${patient.phone}`.toLowerCase().includes(query.toLowerCase()));
  const role = String(profile.role || '').toUpperCase() === 'DOCTOR' ? 'DENTIST' : String(profile.role || '').toUpperCase();
  const nav = navigationByRole[role] || [];
  const todayLabel = new Intl.DateTimeFormat('vi-VN', {
    weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric'
  }).format(new Date());
  return <div className="app-shell">
    {mobileOpen && <button type="button" className="sidebar-backdrop" aria-label="Đóng menu điều hướng" onClick={() => setMobileOpen(false)} />}
    <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
      <div className="brand"><div className="brand-mark">D</div><div><strong>DMS</strong><span>Quản lý nha khoa</span></div><button type="button" className="icon-button close-menu" aria-label="Đóng menu điều hướng" onClick={() => setMobileOpen(false)}><X size={18} /></button></div>
      <div className="workspace"><span className="eyebrow">Không gian làm việc</span><button className="workspace-button">Phòng khám nha khoa Lotus <ChevronDown size={15} /></button></div>
      <nav aria-label="Điều hướng chính">{nav.map(([name, Icon]) => <button key={name} className={section === name ? 'nav-item active' : 'nav-item'} aria-current={section === name ? 'page' : undefined} onClick={() => { navigateToSection(name); setMobileOpen(false); }}><Icon size={18} /><span>{navigationLabels[name]}</span>{name === 'Appointments' && appointments.filter((item) => ['Pending', 'PENDING'].includes(item.status)).length > 0 && <b>{appointments.filter((item) => ['Pending', 'PENDING'].includes(item.status)).length}</b>}</button>)}</nav>
    </aside>
    <main className="main-content">
      <header className="topbar"><button type="button" className="icon-button menu-button" aria-label="Mở menu điều hướng" aria-expanded={mobileOpen} onClick={() => setMobileOpen(true)}><Menu size={20} /></button><div><span className="eyebrow">{todayLabel}</span><h1>{section === 'Overview' || section === 'Portal' ? `Xin chào, ${profile.display_name}` : navigationLabels[section] || section}</h1></div><div className="topbar-actions"><span className={`api-status ${apiLive ? 'live' : ''}`}><span />{apiLive ? 'Đã kết nối' : 'Đang kết nối'}</span><button className="icon-button" aria-label="Trạng thái hoạt động"><Activity size={19} /></button><div className="user-card"><div className="avatar">{profile.display_name.split(' ').map((part) => part[0]).slice(-2).join('')}</div><div><strong>{profile.display_name}</strong><span>{roleLabels[role] || 'Tài khoản'}</span></div><button className="secondary-button" onClick={() => setAccountSettingsOpen(true)}>Tài khoản</button><button className="secondary-button" onClick={logout}>Đăng xuất</button></div></div></header>
      {accountSettingsOpen && <AccountSettingsDialog
        username={profile.username}
        onSave={updateAccount}
        onClose={() => setAccountSettingsOpen(false)}
      />}
      {apiError && section !== 'Appointments' && <div className="api-error" role="alert">{apiError}</div>}
      {section === 'Overview' && (role === 'ADMIN'
        ? <RevenueDashboard tokens={tokens} onTokensChanged={updateTokens} />
        : <Overview appointments={appointments} patients={patients} setSection={navigateToSection} role={role} />)}
      {section === 'Portal' && role === 'PATIENT' && <PatientPortal
        patient={patients[0]}
        appointments={appointments}
        records={medicalRecords}
        invoices={invoices}
        plans={treatmentPlans}
        doctors={doctors}
        services={services}
        onCreateAppointment={createAppointment}
      />}
      {section === 'Patients' && <Patients patients={visiblePatients} query={query} setQuery={setQuery} onCreatePatient={createPatient} onUpdatePatient={updatePatient} onResetPassword={resetAccountPassword} canResetPasswords={role === 'ADMIN'} canCreate={role === 'ADMIN' || role === 'RECEPTIONIST'} loading={apiLoading} />}
      {section === 'Reception' && (role === 'ADMIN' || role === 'RECEPTIONIST') && <Reception tokens={tokens} onTokensChanged={updateTokens} appointments={appointments} setSection={navigateToSection} />}
      {section === 'Appointments' && <Appointments appointments={appointments} patients={patients} doctors={doctors} services={services} schedules={schedules} role={role} loading={apiLoading} loadError={apiError} onCreateAppointment={createAppointment} onCreateSchedule={createSchedule} onCancelAppointment={cancelAppointment} />}
      {section === 'Follow-up reminders' && (role === 'ADMIN' || role === 'RECEPTIONIST') && <FollowUpReminders records={followUpAppointments} loading={apiLoading} loadError={apiError} onGenerate={generateFollowUpReminder} />}
      {section === 'EMR' && (role === 'DENTIST' || role === 'ADMIN') && <MedicalRecords appointments={appointments} patients={patients} services={services} teeth={teeth} records={medicalRecords} loading={apiLoading} loadError={apiError} onSave={saveMedicalRecord} onGenerateSummary={generateAiSummary} />}
      {section === 'Treatment plans' && (role === 'DENTIST' || role === 'ADMIN') && <TreatmentPlans plans={treatmentPlans} patients={patients} doctors={role === 'DENTIST' ? doctors.filter((doctor) => doctor.username === profile.username) : doctors} services={services} teeth={teeth} onCreatePlan={createTreatmentPlan} onUpdatePlan={updateTreatmentPlan} onCreateItem={createTreatmentItem} onUpdateItem={updateTreatmentItem} />}
      {section === 'Tooth chart' && <ToothChart
        dentition={dentition}
        setDentition={setDentition}
        selectedTooth={selectedTooth}
        setSelectedTooth={setSelectedTooth}
        patients={patients}
        teeth={teeth}
        tokens={tokens}
        onTokensChanged={updateTokens}
      />}
      {section === 'Billing' && (role === 'ADMIN' || role === 'RECEPTIONIST') && <Billing invoices={invoices} records={invoiceSources} loading={apiLoading} onCreateInvoice={createInvoice} onPayCash={payInvoiceCash} onCreateQr={createInvoiceQr} onReconcileQr={reconcileInvoiceQr} onCancelQr={cancelInvoiceQr} />}
      {section === 'Radiographs' && <Radiographs
        patients={patients}
        tokens={tokens}
        onTokensChanged={updateTokens}
      />}
      {section === 'Services' && role === 'ADMIN' && <ServiceManagement tokens={tokens} onTokensChanged={updateTokens} />}
      {section === 'Doctors' && role === 'ADMIN' && <DoctorDirectory tokens={tokens} onTokensChanged={updateTokens} onResetPassword={resetAccountPassword} />}
    </main>
    <ChatWidget />
  </div>;
}

function FollowUpReminders({ records, loading, loadError, onGenerate }) {
  const [selectedRecordId, setSelectedRecordId] = useState('');
  const [preview, setPreview] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [retryable, setRetryable] = useState(false);
  const [copyStatus, setCopyStatus] = useState('');
  const generationInFlight = useRef(false);
  const selectedRecord = records.find((record) => String(record.id) === selectedRecordId);

  function selectRecord(record) {
    if (generationInFlight.current) return;
    setSelectedRecordId(String(record.id));
    setPreview(null);
    setError('');
    setRetryable(false);
    setCopyStatus('');
  }

  async function generatePreview() {
    if (!selectedRecord || !selectedRecord.sms_reminder_consent || generationInFlight.current) return;
    generationInFlight.current = true;
    setGenerating(true);
    setError('');
    setRetryable(false);
    setCopyStatus('');
    setPreview(null);
    try {
      setPreview(await onGenerate(selectedRecord.id));
    } catch (requestError) {
      setError(requestError.message || 'Không tạo được tin nhắn nhắc tái khám.');
      setRetryable(requestError.retryable === true);
    } finally {
      generationInFlight.current = false;
      setGenerating(false);
    }
  }

  async function copyPreview() {
    if (!preview?.message) return;
    try {
      if (!navigator.clipboard?.writeText) {
        throw new Error('Trình duyệt không hỗ trợ sao chép tự động. Hãy chọn nội dung để sao chép.');
      }
      await navigator.clipboard.writeText(preview.message);
      setCopyStatus('Đã sao chép tin nhắn.');
    } catch (copyError) {
      setCopyStatus(copyError.message || 'Không thể sao chép tin nhắn.');
    }
  }

  function formatDate(value) {
    return value ? new Date(`${value}T00:00:00`).toLocaleDateString('vi-VN') : '—';
  }

  return <section className="page-section management-page">
    <div className="section-toolbar">
      <div><span className="eyebrow">LỊCH TÁI KHÁM</span><h2>Nhắc tái khám</h2></div>
      <span className="pill">{records.length} hồ sơ</span>
    </div>
    <p className="management-hint follow-up-intro">Chọn hồ sơ có ngày tái khám để tạo bản nháp. Chỉ hồ sơ đã đồng ý nhận tin nhắn mới được dùng; nội dung không tự gửi qua SMS/Zalo.</p>
    {loadError && <div className="form-error" role="alert">{loadError}</div>}
    {loading ? <p className="management-state" role="status">Đang tải lịch tái khám…</p> : !records.length
      ? <div className="panel management-state">Chưa có hồ sơ nào được ghi ngày tái khám.</div>
      : <div className="follow-up-layout">
        <section className="panel table-panel management-table follow-up-list-panel">
          <div className="panel-heading"><div><span className="eyebrow">NGÀY TÁI KHÁM TRONG HỒ SƠ</span><h3>Danh sách lịch tái khám</h3></div></div>
          <div className="follow-up-table-scroll"><table aria-label="Danh sách lịch tái khám">
            <thead><tr><th>Bệnh nhân</th><th>Lịch khám</th><th>Ngày tái khám</th><th>Đồng ý nhận tin</th></tr></thead>
            <tbody>{records.map((record) => <tr
              key={record.id}
              className={String(record.id) === selectedRecordId ? 'follow-up-row-selected' : ''}
              aria-selected={String(record.id) === selectedRecordId}
              onClick={() => !generating && selectRecord(record)}
            >
              <td><button className="follow-up-select" type="button" disabled={generating} onClick={() => selectRecord(record)}>{record.patient_name}</button><small>{record.patient_code}</small></td>
              <td>{new Date(record.appointment_date).toLocaleString('vi-VN')}<small>{record.dentist_name}</small></td>
              <td>{formatDate(record.follow_up_date)}</td>
              <td><span className={`pill ${record.sms_reminder_consent ? 'follow-up-consent-on' : 'inactive'}`}>{record.sms_reminder_consent ? 'Đã đồng ý' : 'Chưa đồng ý'}</span></td>
            </tr>)}</tbody>
          </table></div>
        </section>
        <section className="panel follow-up-preview-panel">
          <div className="panel-heading"><div><span className="eyebrow">XEM TRƯỚC TIN NHẮN AI</span><h3>Tạo tin nhắn</h3></div></div>
          <p className="management-hint">AI chỉ tạo lời mời chung. Không gửi tên, mã bệnh nhân, số điện thoại, ngày tái khám hoặc dữ liệu bệnh án cho Gemini; ngày được ghép từ hồ sơ trong hệ thống. Bản nháp chỉ để xem/sao chép, không tự gửi SMS/Zalo. Giới hạn: 10 lần tạo mỗi người dùng mỗi giờ.</p>
          {selectedRecord && <div className="follow-up-selected">
            <strong>{selectedRecord.patient_name}</strong>
            <span>Tái khám: {formatDate(selectedRecord.follow_up_date)}</span>
          </div>}
          {selectedRecord && !selectedRecord.sms_reminder_consent && <div className="form-error" role="alert">Chưa ghi nhận bệnh nhân đồng ý nhận tin nhắn. Hãy xác nhận trước khi tạo bản nháp.</div>}
          <button className="primary-button" type="button" disabled={!selectedRecord?.sms_reminder_consent || generating || Boolean(error && !retryable)} onClick={generatePreview}>
            <MessageCircle size={16} />{generating ? 'Đang xử lý AI…' : retryable ? 'Thử lại' : 'Tạo tin nhắn bằng AI'}
          </button>
          {generating && <p className="management-state" role="status">Đang chờ dịch vụ AI phản hồi…</p>}
          {error && <div className="form-error" role="alert">{error}</div>}
          {preview && <div className="follow-up-generated">
            <label htmlFor="follow-up-message">Nội dung xem trước</label>
            <textarea id="follow-up-message" readOnly value={preview.message} rows={3} />
            <div className="follow-up-preview-actions">
              <span>{preview.message.length}/70 ký tự · Chưa gửi</span>
              <button className="secondary-button" type="button" onClick={copyPreview}><Copy size={15} />Sao chép</button>
            </div>
          </div>}
          {copyStatus && <div className={copyStatus.startsWith('Đã') ? 'form-success' : 'form-error'} role="status">{copyStatus}</div>}
        </section>
      </div>}
  </section>;
}

function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Xin chào! Bạn có thể hỏi giá, giờ khám, giải thích dịch vụ hoặc hỏi về phân tích và thiết kế đề tài. Hãy nhập câu hỏi của bạn.'
    }
  ]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const requestInFlight = useRef(false);

  useEffect(() => {
    if (open) messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading, open]);

  async function sendQuestion(event, selectedQuestion = question) {
    event?.preventDefault();
    const trimmedQuestion = selectedQuestion.trim();
    if (!trimmedQuestion || requestInFlight.current) return;

    requestInFlight.current = true;
    setQuestion(trimmedQuestion);
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
        const detail = payload?.answer || payload?.detail || '';
        const message = /[à-ỹ]/i.test(detail)
          ? detail
          : localizeApiMessage(detail, response.status);
        throw new Error(message);
      }
      if (typeof payload?.answer !== 'string' || !payload.answer.trim()) {
        throw new Error('Trợ lý tư vấn chưa trả được câu trả lời hợp lệ. Câu hỏi vẫn được giữ lại để bạn thử lại.');
      }
      setMessages((current) => [...current, { role: 'assistant', text: localizeCatalogText(payload.answer) }].slice(-21));
      setQuestion('');
    } catch (error) {
      setMessages((current) => [
        ...current,
        { role: 'assistant', text: `${error.message || 'Không kết nối được trợ lý tư vấn.'} Nếu cần hỗ trợ gấp, vui lòng liên hệ lễ tân.` }
      ].slice(-21));
    } finally {
      requestInFlight.current = false;
      setLoading(false);
    }
  }

  return <div className="chatbot-widget">
    {open && <section className="chatbot-panel" role="dialog" aria-modal="false" aria-labelledby="chatbot-title">
      <header className="chatbot-header">
        <div><strong id="chatbot-title">Trợ lý tư vấn AI</strong><span>Đề tài, dịch vụ và lịch khám</span></div>
        <button type="button" className="chatbot-close" aria-label="Đóng trợ lý tư vấn" onClick={() => setOpen(false)}><X size={18} /></button>
      </header>
      <div className="chatbot-scope-note">Có thể hỏi về phân tích yêu cầu, cơ sở dữ liệu, kiến trúc, prompt AI, giá và lịch khám. Không chẩn đoán hoặc tư vấn điều trị; không nhập thông tin bệnh nhân hay khóa bí mật.</div>
      <div className="chatbot-messages" aria-live="polite" aria-relevant="additions text" aria-busy={loading}>
        {messages.map((message, index) => <div key={`${index}-${message.role}`} className={`chatbot-message ${message.role}`}><p>{message.text}</p></div>)}
        {loading && <div className="chatbot-message assistant"><p role="status">Đang tra cứu…</p></div>}
        <div ref={messagesEndRef} />
      </div>
      <form className="chatbot-form" onSubmit={sendQuestion}>
        <label className="sr-only" htmlFor="chatbot-question">Câu hỏi</label>
        <textarea id="chatbot-question" maxLength={4000} rows={2} value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Nhập câu hỏi về đề tài, giá hoặc lịch khám…" disabled={loading} />
        <button type="submit" aria-label="Gửi câu hỏi" disabled={loading || !question.trim()}><Send size={17} /></button>
      </form>
    </section>}
    <button type="button" className="chatbot-launcher" aria-label={open ? 'Đóng tư vấn' : 'Mở trợ lý tư vấn'} aria-expanded={open} onClick={() => setOpen((current) => !current)}>
      {open ? <X size={21} /> : <MessageCircle size={21} />}
      <span>{open ? 'Đóng' : 'Tư vấn'}</span>
    </button>
  </div>;
}

function AccountSettingsDialog({ username, onSave, onClose }) {
  const [nextUsername, setNextUsername] = useState(username);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await onSave({
        username: nextUsername.trim(),
        current_password: currentPassword,
        new_password: newPassword
      });
      setCurrentPassword('');
      setNewPassword('');
      setSuccess('Đã cập nhật thông tin tài khoản.');
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return <div className="account-dialog-backdrop">
    <section className="account-dialog" role="dialog" aria-modal="true" aria-labelledby="account-dialog-title">
      <div className="account-dialog-heading">
        <div><span className="eyebrow">THÔNG TIN ĐĂNG NHẬP</span><h2 id="account-dialog-title">Tài khoản</h2></div>
        <button className="icon-button" type="button" aria-label="Đóng" onClick={onClose}><X size={18} /></button>
      </div>
      <form className="management-form" onSubmit={submit}>
        <label>Tên đăng nhập<input autoComplete="username" required maxLength={150} value={nextUsername} onChange={(event) => setNextUsername(event.target.value)} /></label>
        <label>Mật khẩu hiện tại<input type="password" autoComplete="current-password" required value={currentPassword} onChange={(event) => setCurrentPassword(event.target.value)} /></label>
        <label>Mật khẩu mới<input type="password" autoComplete="new-password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)} /></label>
        <p className="account-dialog-hint">Để trống mật khẩu mới nếu bạn chỉ muốn đổi tên đăng nhập.</p>
        {error && <div className="form-error" role="alert">{error}</div>}
        {success && <div className="form-success" role="status">{success}</div>}
        <div className="form-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Đang lưu…' : 'Lưu thay đổi'}</button><button className="secondary-button" type="button" disabled={saving} onClick={onClose}>Đóng</button></div>
      </form>
    </section>
  </div>;
}

function AdminPasswordResetDialog({ target, onSave, onClose }) {
  const [newPassword, setNewPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);

  async function submit(event) {
    event.preventDefault();
    if (newPassword !== confirmation) {
      setError('Mật khẩu xác nhận không khớp.');
      return;
    }

    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await onSave(newPassword);
      setNewPassword('');
      setConfirmation('');
      setSuccess(`Đã cập nhật mật khẩu cho tài khoản ${target.username}. Hãy chuyển mật khẩu mới qua kênh riêng.`);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      setSaving(false);
    }
  }

  return <div className="account-dialog-backdrop">
    <section className="account-dialog" role="dialog" aria-modal="true" aria-labelledby="password-reset-title">
      <div className="account-dialog-heading">
        <div><span className="eyebrow">THÔNG TIN ĐĂNG NHẬP</span><h2 id="password-reset-title">Tài khoản</h2></div>
        <button className="icon-button" type="button" aria-label="Đóng" onClick={onClose}><X size={18} /></button>
      </div>
      <form className="management-form" onSubmit={submit}>
        <label>Tên đăng nhập<input value={target.username || 'Chưa liên kết'} readOnly /></label>
        <label>Mật khẩu mới<input type="password" autoComplete="new-password" required value={newPassword} onChange={(event) => setNewPassword(event.target.value)} /></label>
        <label>Xác nhận mật khẩu mới<input type="password" autoComplete="new-password" required value={confirmation} onChange={(event) => setConfirmation(event.target.value)} /></label>
        <p className="account-dialog-hint">Mật khẩu phải đáp ứng chính sách bảo mật. Mật khẩu sẽ không được lưu hoặc hiển thị lại sau khi đặt.</p>
        {error && <div className="form-error" role="alert">{error}</div>}
        {success && <div className="form-success" role="status">{success}</div>}
        <div className="form-actions">
          <button className="primary-button" type="submit" disabled={saving}>{saving ? 'Đang lưu…' : 'Lưu mật khẩu mới'}</button>
          <button className="secondary-button" type="button" disabled={saving} onClick={onClose}>Đóng</button>
        </div>
      </form>
    </section>
  </div>;
}

function LoginPage({ onLogin, onRegister, initialError }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [registering, setRegistering] = useState(false);
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [error, setError] = useState(initialError);
  const [submitting, setSubmitting] = useState(false);
  const submittingRef = useRef(false);

  async function handleSubmit(event) {
    event.preventDefault();
    if (submittingRef.current) return;
    submittingRef.current = true;
    setSubmitting(true);
    setError('');
    try {
      if (registering) {
        await onRegister({
          username: username.trim(),
          password,
          full_name: fullName.trim(),
          phone: phone.trim(),
          date_of_birth: dateOfBirth || null
        });
      } else {
        await onLogin(username.trim(), password);
      }
    } catch (loginError) {
      setError(loginError.message);
    } finally {
      submittingRef.current = false;
      setSubmitting(false);
    }
  }

  return <main className="login-screen">
    <form className="login-card" onSubmit={handleSubmit}>
      <div className="brand-mark">D</div>
      <span className="eyebrow">PHÒNG KHÁM NHA KHOA LOTUS</span>
      <h1>{registering ? 'Tạo tài khoản' : 'Đăng nhập'}</h1>
      {registering && <>
        <label htmlFor="register-full-name">Họ và tên</label>
        <input id="register-full-name" autoComplete="name" required maxLength={160} value={fullName} onChange={(event) => setFullName(event.target.value)} />
        <label htmlFor="register-phone">Số điện thoại</label>
        <input id="register-phone" autoComplete="tel" value={phone} onChange={(event) => setPhone(event.target.value)} />
        <label htmlFor="register-date-of-birth">Ngày sinh</label>
        <input id="register-date-of-birth" type="date" value={dateOfBirth} onChange={(event) => setDateOfBirth(event.target.value)} />
      </>}
      <label htmlFor="login-username">Tên đăng nhập</label>
      <input id="login-username" autoComplete="username" required value={username} onChange={(event) => setUsername(event.target.value)} />
      <label htmlFor="login-password">Mật khẩu</label>
      <input id="login-password" type="password" autoComplete="current-password" required value={password} onChange={(event) => setPassword(event.target.value)} />
      {error && <div className="form-error" role="alert">{error}</div>}
      <button className="primary-button login-submit" type="submit" disabled={submitting}>{submitting ? 'Đang xử lý…' : registering ? 'Tạo tài khoản' : 'Đăng nhập'}</button>
      <button className="text-button login-mode-toggle" type="button" disabled={submitting} onClick={() => { setRegistering(!registering); setError(''); }}>{registering ? 'Đã có tài khoản? Đăng nhập' : 'Tạo tài khoản mới'}</button>
    </form>
  </main>;
}

function statusLabel(value) {
  const labels = {
    Pending: 'Chờ xác nhận', PENDING: 'Chờ xác nhận',
    SCHEDULED: 'Đã lên lịch',
    Confirmed: 'Đã xác nhận', CONFIRMED: 'Đã xác nhận',
    Completed: 'Đã hoàn thành', COMPLETED: 'Đã hoàn thành',
    Cancelled: 'Đã hủy', CANCELLED: 'Đã hủy',
    DRAFT: 'Bản nháp', ACTIVE: 'Đang thực hiện',
    IN_PROGRESS: 'Đang thực hiện',
    DONE: 'Hoàn thành', PLANNED: 'Dự kiến',
    PAID: 'Đã thanh toán', ISSUED: 'Chưa thanh toán',
    PARTIALLY_PAID: 'Thanh toán một phần',
    FAILED: 'Thất bại', UNKNOWN: 'Chưa xác định',
    REFUNDED: 'Đã hoàn tiền', VOID: 'Đã hủy'
  };
  return labels[value] || 'Chưa cập nhật';
}

function paymentMethodLabel(value) {
  const labels = {
    CASH: 'Tiền mặt',
    BANK_TRANSFER: 'Chuyển khoản',
    CARD: 'Thẻ ngân hàng'
  };
  return labels[value] || 'Phương thức khác';
}

function PatientPortal({ patient, appointments, records, invoices, plans, doctors, services, onCreateAppointment }) {
  const [bookingOpen, setBookingOpen] = useState(false);
  const [booking, setBooking] = useState({
    doctor: '', service: '', date: '', time: '09:00', notes: ''
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const inFlight = useRef(false);

  async function submitBooking(event) {
    event.preventDefault();
    if (!patient || inFlight.current) return;
    inFlight.current = true;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await onCreateAppointment({
        patient: patient.id,
        doctor: Number(booking.doctor),
        service: Number(booking.service),
        appointment_date: new Date(`${booking.date}T${booking.time}:00`).toISOString(),
        notes: booking.notes.trim()
      });
      setBookingOpen(false);
      setSuccess('Đã gửi yêu cầu đặt lịch. Phòng khám sẽ xác nhận lịch hẹn của bạn.');
      setBooking((current) => ({ ...current, notes: '' }));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      inFlight.current = false;
      setSaving(false);
    }
  }

  if (!patient) return <div className="panel management-state">Đang tải hồ sơ bệnh nhân…</div>;

  return <section className="page-section management-page patient-portal">
    <section className="hero-band">
      <div><span className="eyebrow warm">CỔNG BỆNH NHÂN</span><h2>Chăm sóc sức khỏe răng miệng của bạn</h2><p>Mã bệnh nhân: {patient.patient_code}</p></div>
      <button className="primary-button" type="button" onClick={() => { setBookingOpen((open) => !open); setError(''); setSuccess(''); }}>Đặt lịch khám</button>
    </section>
    <nav className="patient-portal-nav" aria-label="Điều hướng trong cổng bệnh nhân">
      <a href="#patient-profile">Hồ sơ cá nhân</a>
      <a href="#patient-appointments">Lịch hẹn</a>
      <a href="#patient-records">Kết quả khám</a>
      <a href="#patient-plans">Tiến độ điều trị</a>
      <a href="#patient-invoices">Hóa đơn</a>
    </nav>
    {error && <div className="form-error" role="alert">{error}</div>}
    {success && <div className="form-success" role="status">{success}</div>}
    {bookingOpen && <form className="panel management-form patient-portal-booking" onSubmit={submitBooking}>
      <h3>Gửi yêu cầu đặt lịch</h3>
      <div className="form-grid">
        <label>Bác sĩ<select required value={booking.doctor} onChange={(event) => setBooking({ ...booking, doctor: event.target.value })}><option value="">Chọn bác sĩ</option>{doctors.map((doctor) => <option key={doctor.id} value={doctor.id}>{doctor.full_name}</option>)}</select></label>
        <label>Dịch vụ<select required value={booking.service} onChange={(event) => setBooking({ ...booking, service: event.target.value })}><option value="">Chọn dịch vụ</option>{services.map((service) => <option key={service.id} value={service.id}>{localizeCatalogText(service.name)} · {service.duration_minutes} phút</option>)}</select></label>
        <label>Ngày khám<input required type="date" min={localDateInputValue(new Date())} value={booking.date} onChange={(event) => setBooking({ ...booking, date: event.target.value })} /></label>
        <label>Giờ bắt đầu<input required type="time" value={booking.time} onChange={(event) => setBooking({ ...booking, time: event.target.value })} /></label>
        <label className="form-wide">Lý do khám<textarea required maxLength={1000} value={booking.notes} onChange={(event) => setBooking({ ...booking, notes: event.target.value })} /></label>
      </div>
      <p className="management-hint">Yêu cầu chỉ được xác nhận khi phòng khám kiểm tra ca làm và lịch của bác sĩ.</p>
      <div className="form-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Đang gửi…' : 'Gửi yêu cầu'}</button><button className="secondary-button" type="button" disabled={saving} onClick={() => setBookingOpen(false)}>Đóng</button></div>
    </form>}
    <section className="panel patient-profile patient-portal-profile" id="patient-profile">
      <div className="panel-heading"><div><span className="eyebrow">HỒ SƠ CỦA BẠN</span><h3>{patient.full_name}</h3></div></div>
      <div className="patient-profile-grid">
        <div><span>Mã bệnh nhân</span><strong>{patient.patient_code}</strong></div>
        <div><span>Số điện thoại</span><strong>{patient.phone || 'Chưa cập nhật'}</strong></div>
        <div><span>Ngày sinh</span><strong>{patient.date_of_birth ? new Date(`${patient.date_of_birth}T00:00:00`).toLocaleDateString('vi-VN') : 'Chưa cập nhật'}</strong></div>
        <div><span>Tiền sử dị ứng</span><p>{patient.allergies || 'Chưa ghi nhận'}</p></div>
        <div><span>Tiền sử bệnh</span><p>{patient.medical_history || 'Chưa ghi nhận'}</p></div>
      </div>
    </section>
    <section className="panel table-panel management-table patient-portal-appointments" id="patient-appointments">
      <div className="panel-heading"><div><span className="eyebrow">LỊCH KHÁM</span><h3>Lịch hẹn của tôi</h3></div></div>
      {!appointments.length ? <p className="management-state">Bạn chưa có lịch hẹn.</p> : <div className="invoice-table-scroll"><table><thead><tr><th>Ngày giờ</th><th>Bác sĩ</th><th>Dịch vụ</th><th>Trạng thái</th></tr></thead><tbody>{appointments.map((item) => <tr key={item.id}><td>{new Date(item.appointment_date).toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</td><td>{item.dentist_name}</td><td>{localizeCatalogText(item.service_name || 'Chưa xác định')}</td><td><span className="pill">{statusLabel(item.status)}</span></td></tr>)}</tbody></table></div>}
    </section>
    <section className="panel table-panel management-table patient-portal-records" id="patient-records">
      <div className="panel-heading"><div><span className="eyebrow">HỒ SƠ KHÁM</span><h3>Kết quả điều trị</h3></div></div>
      {!records.length ? <p className="management-state">Chưa có hồ sơ khám được ghi nhận.</p> : <div className="patient-record-list">{records.map((record) => <article key={record.id} className="patient-record-card"><strong>Ngày khám: {new Date(record.appointment_date).toLocaleString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</strong><p><b>Chẩn đoán:</b> {localizeCatalogText(record.diagnosis)}</p><p><b>Kế hoạch điều trị:</b> {localizeCatalogText(record.treatment_plan)}</p>{record.prescription && <p><b>Đơn thuốc:</b> {localizeCatalogText(record.prescription)}</p>}</article>)}</div>}
    </section>
    <section className="panel table-panel management-table patient-portal-plans" id="patient-plans">
      <div className="panel-heading"><div><span className="eyebrow">KẾ HOẠCH</span><h3>Tiến độ điều trị</h3></div></div>
      {!plans.length ? <p className="management-state">Chưa có kế hoạch điều trị.</p> : plans.map((plan) => <article className="patient-record-card" key={plan.id}><strong>{localizeCatalogText(plan.title)} · {statusLabel(plan.status)}</strong><ul>{plan.items.map((item) => <li key={item.id}>{localizeCatalogText(item.procedure_name)} · {statusLabel(item.status)}</li>)}</ul></article>)}
    </section>
    <section className="panel table-panel management-table patient-portal-invoices" id="patient-invoices">
      <div className="panel-heading"><div><span className="eyebrow">THANH TOÁN</span><h3>Hóa đơn của tôi</h3></div></div>
      {!invoices.length ? <p className="management-state">Bạn chưa có hóa đơn.</p> : <div className="invoice-table-scroll"><table><thead><tr><th>Số hóa đơn</th><th>Tổng tiền</th><th>Đã thanh toán</th><th>Trạng thái</th></tr></thead><tbody>{invoices.map((invoice) => <tr key={invoice.id}><td>{invoice.invoice_number}</td><td>{Number(invoice.total_amount).toLocaleString('vi-VN')} ₫</td><td>{Number(invoice.paid_amount).toLocaleString('vi-VN')} ₫</td><td><span className="pill">{statusLabel(invoice.status)}</span></td></tr>)}</tbody></table></div>}
    </section>
  </section>;
}

function TreatmentPlans({ plans, patients, doctors, services, teeth, onCreatePlan, onUpdatePlan, onCreateItem, onUpdateItem }) {
  const [planForm, setPlanForm] = useState({ patient: '', dentist: '', title: '', status: 'ACTIVE', start_date: '', end_date: '' });
  const [itemForm, setItemForm] = useState({ plan: '', service: '', procedure_name: '', tooth: '', cost: '', status: 'PLANNED' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
  const inFlight = useRef(false);

  async function submitPlan(event) {
    event.preventDefault();
    if (inFlight.current) return;
    inFlight.current = true;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await onCreatePlan({
        ...planForm,
        patient: Number(planForm.patient),
        dentist: Number(planForm.dentist),
        start_date: planForm.start_date || null,
        end_date: planForm.end_date || null
      });
      setPlanForm({ patient: '', dentist: '', title: '', status: 'ACTIVE', start_date: '', end_date: '' });
      setSuccess('Đã tạo kế hoạch điều trị.');
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      inFlight.current = false;
      setSaving(false);
    }
  }

  async function submitItem(event) {
    event.preventDefault();
    if (inFlight.current) return;
    inFlight.current = true;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await onCreateItem({
        plan: Number(itemForm.plan),
        service: itemForm.service ? Number(itemForm.service) : null,
        procedure_name: itemForm.procedure_name.trim(),
        tooth: itemForm.tooth ? Number(itemForm.tooth) : null,
        cost: itemForm.cost,
        status: itemForm.status
      });
      setItemForm({ plan: '', service: '', procedure_name: '', tooth: '', cost: '', status: 'PLANNED' });
      setSuccess('Đã thêm bước điều trị.');
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      inFlight.current = false;
      setSaving(false);
    }
  }

  async function updatePlanStatus(plan, status) {
    try {
      await onUpdatePlan(plan.id, { status });
      setSuccess('Đã cập nhật trạng thái kế hoạch.');
      setError('');
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function updateItemStatus(item, status) {
    try {
      await onUpdateItem(item.id, { status });
      setSuccess('Đã cập nhật tiến độ bước điều trị.');
      setError('');
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  return <section className="page-section management-page">
    <div className="section-toolbar"><div><span className="eyebrow">ĐIỀU TRỊ</span><h2>Kế hoạch điều trị</h2></div></div>
    {error && <div className="form-error" role="alert">{error}</div>}
    {success && <div className="form-success" role="status">{success}</div>}
    <form className="panel management-form" onSubmit={submitPlan}>
      <h3>Tạo kế hoạch điều trị</h3>
      <div className="form-grid">
        <label>Bệnh nhân<select required value={planForm.patient} onChange={(event) => setPlanForm({ ...planForm, patient: event.target.value })}><option value="">Chọn bệnh nhân</option>{patients.map((patient) => <option key={patient.id} value={patient.id}>{patient.full_name} · {patient.patient_code}</option>)}</select></label>
        <label>Bác sĩ phụ trách<select required value={planForm.dentist} onChange={(event) => setPlanForm({ ...planForm, dentist: event.target.value })}><option value="">Chọn bác sĩ</option>{doctors.map((doctor) => <option key={doctor.id} value={doctor.id}>{doctor.full_name}</option>)}</select></label>
        <label className="form-wide">Tên kế hoạch<input required maxLength={180} value={planForm.title} onChange={(event) => setPlanForm({ ...planForm, title: event.target.value })} /></label>
        <label>Ngày bắt đầu<input type="date" value={planForm.start_date} onChange={(event) => setPlanForm({ ...planForm, start_date: event.target.value })} /></label>
        <label>Ngày kết thúc dự kiến<input type="date" value={planForm.end_date} onChange={(event) => setPlanForm({ ...planForm, end_date: event.target.value })} /></label>
      </div>
      <div className="form-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Đang lưu…' : 'Tạo kế hoạch'}</button></div>
    </form>
    {!!plans.length && <form className="panel management-form" onSubmit={submitItem}>
      <h3>Thêm bước điều trị</h3>
      <div className="form-grid">
        <label>Kế hoạch<select required value={itemForm.plan} onChange={(event) => setItemForm({ ...itemForm, plan: event.target.value })}>        <option value="">Chọn kế hoạch</option>{plans.map((plan) => <option key={plan.id} value={plan.id}>{localizeCatalogText(plan.title)} · {plan.patient_name}</option>)}</select></label>
        <label>Dịch vụ<select value={itemForm.service} onChange={(event) => { const service = services.find((item) => String(item.id) === event.target.value); setItemForm({ ...itemForm, service: event.target.value, procedure_name: service?.name || itemForm.procedure_name, cost: service?.price || itemForm.cost }); }}><option value="">Không chọn dịch vụ</option>{services.map((service) => <option key={service.id} value={service.id}>{localizeCatalogText(service.name)}</option>)}</select></label>
        <label>Tên bước điều trị<input required maxLength={180} value={itemForm.procedure_name} onChange={(event) => setItemForm({ ...itemForm, procedure_name: event.target.value })} /></label>
        <label>Răng liên quan<select value={itemForm.tooth} onChange={(event) => setItemForm({ ...itemForm, tooth: event.target.value })}><option value="">Không chỉ định răng</option>{teeth.map((tooth) => <option key={tooth.id} value={tooth.id}>{tooth.code}</option>)}</select></label>
        <label>Chi phí dự kiến<input required type="number" min="0" step="1" value={itemForm.cost} onChange={(event) => setItemForm({ ...itemForm, cost: event.target.value })} /></label>
      </div>
      <div className="form-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Đang lưu…' : 'Thêm bước điều trị'}</button></div>
    </form>}
    {!plans.length ? <div className="panel management-state">Chưa có kế hoạch điều trị.</div> : plans.map((plan) => <section className="panel patient-profile treatment-plan-card" key={plan.id}>
      <div className="panel-heading"><div><span className="eyebrow">{plan.patient_name} · {plan.dentist_name}</span><h3>{localizeCatalogText(plan.title)}</h3></div><label className="treatment-status-label">Trạng thái<select value={plan.status} onChange={(event) => updatePlanStatus(plan, event.target.value)}><option value="DRAFT">Bản nháp</option><option value="ACTIVE">Đang thực hiện</option><option value="COMPLETED">Hoàn thành</option><option value="CANCELLED">Đã hủy</option></select></label></div>
      <p className="management-hint">Thời gian: {plan.start_date ? new Date(`${plan.start_date}T00:00:00`).toLocaleDateString('vi-VN') : 'Chưa đặt'} – {plan.end_date ? new Date(`${plan.end_date}T00:00:00`).toLocaleDateString('vi-VN') : 'Chưa đặt'}</p>
      {!plan.items.length ? <p className="management-state">Chưa có bước điều trị trong kế hoạch.</p> : <div className="invoice-table-scroll"><table><thead><tr><th>Bước điều trị</th><th>Răng</th><th>Chi phí dự kiến</th><th>Tiến độ</th></tr></thead><tbody>{plan.items.map((item) => <tr key={item.id}><td>{localizeCatalogText(item.procedure_name)}</td><td>{item.tooth_code || '—'}</td><td>{Number(item.cost).toLocaleString('vi-VN')} ₫</td><td><select value={item.status} onChange={(event) => updateItemStatus(item, event.target.value)}><option value="PLANNED">Dự kiến</option><option value="IN_PROGRESS">Đang thực hiện</option><option value="DONE">Hoàn thành</option><option value="CANCELLED">Đã hủy</option></select></td></tr>)}</tbody></table></div>}
    </section>)}
  </section>;
}

const emptyService = { code: '', name: '', description: '', price: '', duration_minutes: 30, is_active: true };

function ServiceManagement({ tokens, onTokensChanged }) {
  const [services, setServices] = useState([]);
  const [form, setForm] = useState(emptyService);
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState('');
  const mutationInFlight = useRef(false);

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
    if (mutationInFlight.current) return;
    mutationInFlight.current = true;
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
      mutationInFlight.current = false;
      setSaving(false);
    }
  }

  async function deleteService(service) {
    if (mutationInFlight.current) return;
    if (!window.confirm(`Ngừng cung cấp dịch vụ "${localizeCatalogText(service.name)}"?`)) return;
    mutationInFlight.current = true;
    setDeletingId(service.id);
    setError('');
    try {
      await apiRequest(`/services/${service.id}/`, { tokens, onTokens: onTokensChanged, method: 'DELETE' });
      await loadServices();
    } catch (deleteError) {
      setError(deleteError.message);
    } finally {
      mutationInFlight.current = false;
      setDeletingId(null);
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
        <label>Giá (đồng)<input required type="number" min="0" step="1000" value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} /></label>
        <label>Thời lượng (phút)<input required type="number" min="1" value={form.duration_minutes} onChange={(event) => setForm({ ...form, duration_minutes: event.target.value })} /></label>
        <label className="form-wide">Mô tả<textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} /></label>
        <label className="checkbox-field"><input type="checkbox" checked={form.is_active} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} /> Cho phép đặt lịch</label>
      </div>
      <div className="form-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Đang lưu…' : 'Lưu dịch vụ'}</button><button className="secondary-button" type="button" onClick={() => setShowForm(false)}>Hủy</button></div>
    </form>}
    <div className="panel table-panel management-table">
      {loading ? <p className="management-state">Đang tải dịch vụ…</p> : services.length === 0 ? <p className="management-state">Chưa có dịch vụ. Hãy thêm dịch vụ để bắt đầu.</p> :
        <table><thead><tr><th>Mã</th><th>Dịch vụ</th><th>Giá</th><th>Thời lượng</th><th>Trạng thái</th><th>Thao tác</th></tr></thead>
          <tbody>{services.map((service) => <tr key={service.id}>
            <td><code>{service.code}</code></td><td><strong>{localizeCatalogText(service.name)}</strong><small className="table-description">{service.description || '—'}</small></td>
            <td>{Number(service.price).toLocaleString('vi-VN')} ₫</td><td>{service.duration_minutes} phút</td>
            <td><span className={`pill ${service.is_active ? '' : 'inactive'}`}>{service.is_active ? 'Đang hoạt động' : 'Đã ngừng'}</span></td>
            <td><div className="row-actions"><button className="icon-button" aria-label={`Chỉnh sửa ${localizeCatalogText(service.name)}`} disabled={saving || deletingId !== null} onClick={() => startEdit(service)}><Pencil size={16} /></button>{service.is_active && <button className="icon-button danger-button" aria-label={`Ngừng ${localizeCatalogText(service.name)}`} disabled={saving || deletingId !== null} onClick={() => deleteService(service)}><Trash2 size={16} /></button>}</div></td>
          </tr>)}</tbody>
        </table>}
    </div>
  </section>;
}

function DoctorDirectory({ tokens, onTokensChanged, onResetPassword }) {
  const [doctors, setDoctors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [resetTarget, setResetTarget] = useState(null);

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
    {resetTarget && <AdminPasswordResetDialog
      target={resetTarget}
      onSave={(newPassword) => onResetPassword('doctor', resetTarget.id, newPassword)}
      onClose={() => setResetTarget(null)}
    />}
    <div className="panel table-panel management-table">
      {loading ? <p className="management-state">Đang tải danh sách bác sĩ…</p> : doctors.length === 0 ? <p className="management-state">Chưa có thông tin bác sĩ.</p> :
        <table className="doctor-directory-table"><thead><tr><th>Bác sĩ</th><th>Số giấy phép</th><th>Chuyên môn</th><th>Điện thoại</th><th>Vai trò</th><th>Tài khoản</th></tr></thead>
          <tbody>{doctors.map((doctor) => <tr key={doctor.id}>
            <td data-label="Bác sĩ"><div className="table-person"><div className="small-avatar">{doctor.full_name.split(' ').map((part) => part[0]).slice(-2).join('')}</div><strong>{doctor.full_name}</strong></div></td>
            <td data-label="Số giấy phép"><code>{doctor.license_number}</code></td><td data-label="Chuyên môn">{localizeCatalogText(doctor.specialization) || '—'}</td><td data-label="Điện thoại">{doctor.phone || '—'}</td><td data-label="Vai trò"><span className="pill">{roleLabels[doctor.role] || 'Bác sĩ'}</span></td>
            <td data-label="Tài khoản"><button className="text-button" type="button" onClick={() => setResetTarget(doctor)}>Tài khoản</button></td>
          </tr>)}</tbody>
        </table>}
    </div>
  </section>;
}

function Overview({ appointments, patients, setSection, role }) {
  const today = dateKey(new Date());
  const todayAppointments = appointments.filter((item) => {
    const appointmentDate = new Date(item.appointment_date || item.start_at);
    return !Number.isNaN(appointmentDate.getTime()) && dateKey(appointmentDate) === today;
  });
  const waiting = appointments.filter((item) =>
    ['PENDING', 'Pending', 'SCHEDULED'].includes(item.status)
  ).length;
  const completed = appointments.filter((item) =>
    ['COMPLETED', 'Completed'].includes(item.status)
  ).length;
  const heading = role === 'DENTIST' ? 'Lịch khám và công việc của bạn' : 'Hoạt động phòng khám';

  return <section className={`page-section management-page overview-page ${role === 'DENTIST' ? 'dentist-overview' : ''}`}>
    <section className="hero-band">
      <div><span className="eyebrow warm">TỔNG QUAN HÔM NAY</span><h2>{heading}</h2><p>Thông tin được cập nhật từ dữ liệu lịch hẹn và hồ sơ hiện có.</p></div>
      <button className="primary-button" onClick={() => setSection('Appointments')}><CalendarDays size={17} /> Xem lịch hẹn</button>
    </section>
    <section className="metric-grid">
      <Metric label="Lịch hẹn hôm nay" value={todayAppointments.length} detail={`${waiting} lịch đang chờ xác nhận`} accent="blue" icon={CalendarDays} />
      <Metric label="Hồ sơ bệnh nhân" value={patients.length} detail="Trong phạm vi được phân quyền" accent="sage" icon={Users} />
      <Metric label="Lịch đã hoàn thành" value={completed} detail="Tổng số lịch đã hoàn tất" accent="gold" icon={ClipboardPlus} />
    </section>
    <div className="content-grid">
      <section className="panel schedule-panel">
        <div className="panel-heading"><div><span className="eyebrow">LỊCH HẸN</span><h3>Lịch khám hôm nay</h3></div><button className="text-button" onClick={() => setSection('Appointments')}>Mở lịch <span>→</span></button></div>
        <div className="appointment-list">{todayAppointments.length
          ? todayAppointments.map((item) => <AppointmentRow key={item.id} item={item} />)
          : <p className="management-state">Hôm nay chưa có lịch hẹn.</p>}</div>
      </section>
      <section className="panel focus-panel">
        <div className="panel-heading"><div><span className="eyebrow">TÌNH HÌNH</span><h3>Thông tin nhanh</h3></div><ShieldCheck size={19} color="#1d6857" /></div>
        <div className="focus-stat"><span className="focus-icon green"><UserRound size={18} /></span><div><strong>{patients.length} hồ sơ bệnh nhân</strong><span>Được hiển thị theo quyền tài khoản</span></div></div>
        <div className="focus-stat"><span className="focus-icon peach"><CalendarDays size={18} /></span><div><strong>{waiting} lịch cần xác nhận</strong><span>Kiểm tra lịch để cập nhật tình trạng</span></div></div>
        <div className="alert-box"><strong>Cần xem lịch?</strong><p>Mở danh sách lịch hẹn để xem chi tiết và tình trạng từng cuộc hẹn.</p><button onClick={() => setSection('Appointments')}>Xem lịch hẹn →</button></div>
      </section>
    </div>
  </section>;
}
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
    <div><span className="eyebrow">TÀI CHÍNH VÀ HOẠT ĐỘNG KHÁM</span><h2>Doanh thu và lượt khám</h2></div>
    <span className="dashboard-timezone">Múi giờ Việt Nam</span>
    </div>
    <section className="panel dashboard-filter-panel" aria-label="Bộ lọc ngày thống kê">
    <label>Từ ngày<input type="date" value={startDate} max={endDate || today} onChange={(event) => setStartDate(event.target.value)} /></label>
    <label>Đến ngày<input type="date" value={endDate} min={startDate} max={today} onChange={(event) => setEndDate(event.target.value)} /></label>
    <label>Khoảng thời gian biểu đồ<select value={requestedGroup} onChange={(event) => setRequestedGroup(event.target.value)}>
      <option value="auto">Tự động</option>
      <option value="day">Theo ngày</option>
      <option value="month">Theo tháng</option>
      </select></label>
    {dashboard && <p className="dashboard-filter-summary">Tổng {dashboard.group_by === 'day' ? 'theo ngày' : 'theo tháng'} · bao gồm cả hai ngày đã chọn</p>}
    </section>
    {error && <div className="form-error" role="alert">{error}</div>}
    {loading && <p className="management-state" role="status">Đang tải thống kê doanh thu và lượt khám…</p>}
    <section className="metric-grid dashboard-metrics" aria-label="Tóm tắt thống kê" aria-busy={loading}>
      <Metric label="Doanh thu từ hóa đơn đã thanh toán" value={`${revenue.toLocaleString('vi-VN', { maximumFractionDigits: 2 })} ₫`} detail="Tổng hóa đơn đã thanh toán, tính theo ngày lập" accent="sage" icon={CircleDollarSign} />
      <Metric label="Lượt khám đã hoàn thành" value={visits.toLocaleString('vi-VN')} detail="Lịch khám đã hoàn thành, tính theo ngày khám" accent="blue" icon={CalendarDays} />
    </section>
    {!loading && !error && dashboard && <>
      <TrendChart title="Doanh thu theo thời gian" series={series} valueKey="revenue" groupBy={dashboard.group_by} formatValue={(value) => `${Number(value).toLocaleString('vi-VN', { maximumFractionDigits: 2 })} ₫`} color="revenue" />
      <TrendChart title="Lượt khám hoàn thành theo thời gian" series={series} valueKey="visits" groupBy={dashboard.group_by} formatValue={(value) => Number(value).toLocaleString('vi-VN')} color="visits" />
      <p className="dashboard-definition">Doanh thu tính tổng giá trị mỗi hóa đơn đã thanh toán một lần theo ngày lập; không tính giao dịch đang chờ hoặc hóa đơn chưa thanh toán. Lượt khám tính các lịch đã hoàn thành, không tính hóa đơn. Ngày/kỳ không có dữ liệu được hiển thị bằng 0.</p>
    </>}
  </section>;
}

function TrendChart({ title, series, valueKey, groupBy, formatValue, color }) {
  const values = series.map((point) => Number(point[valueKey]));
  const maximum = Math.max(...values, 0);
  const labelEvery = series.length > 24 ? Math.ceil(series.length / 12) : 1;

  return <section className="panel dashboard-chart-panel">
    <div className="panel-heading"><div><span className="eyebrow">{valueKey === 'revenue' ? 'ĐỒNG VIỆT NAM' : 'LỊCH HẸN'}</span><h3>{title}</h3></div></div>
    {!series.length ? <p className="management-state">Không có kỳ thống kê trong khoảng ngày này.</p> : maximum === 0
      ? <p className="dashboard-empty-chart">Không có {valueKey === 'revenue' ? 'doanh thu' : 'lượt khám hoàn thành'} trong kỳ này.</p>
      : <div className="dashboard-chart-scroll"><div className="dashboard-bars" role="img" aria-label={`${title} từ ${formatDashboardPeriod(series[0].period, groupBy)} đến ${formatDashboardPeriod(series.at(-1).period, groupBy)}`}>
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
    ? new Date(appointmentDate).toLocaleString('vi-VN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    : appointmentDate;
  const status = String(item.status || '').toLowerCase();
  return <div className="appointment-row">
    <div className="time">{time}</div>
    <div className="appointment-avatar">{(item.patient_name || 'Bệnh nhân').split(' ').map((part) => part[0]).slice(-2).join('')}</div>
    <div className="appointment-info"><strong>{item.patient_name}</strong><span>{localizeCatalogText(item.service_name || item.type || 'Khám răng')} · {item.dentist_name}</span></div>
    <span className={`status ${status === 'confirmed' ? 'confirmed' : status === 'completed' ? 'paid' : status === 'cancelled' ? 'inactive' : 'scheduled'}`}>{statusLabel(item.status)}</span>
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
  allergies: '',
  ai_processing_consent: false,
  sms_reminder_consent: false
};

function Patients({ patients, query, setQuery, onCreatePatient, onUpdatePatient, onResetPassword, canResetPasswords, canCreate, loading }) {
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyPatient);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [passwordResetTarget, setPasswordResetTarget] = useState(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [consentForm, setConsentForm] = useState({ ai_processing_consent: false, sms_reminder_consent: false });
  const [consentSaving, setConsentSaving] = useState(false);
  const savingRef = useRef(false);
  const consentSavingRef = useRef(false);

  useEffect(() => {
    setConsentForm({
      ai_processing_consent: Boolean(selectedPatient?.ai_processing_consent),
      sms_reminder_consent: Boolean(selectedPatient?.sms_reminder_consent)
    });
  }, [selectedPatient?.id, selectedPatient?.ai_processing_consent, selectedPatient?.sms_reminder_consent]);

  async function savePatient(event) {
    event.preventDefault();
    if (savingRef.current) return;
    savingRef.current = true;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const patient = await onCreatePatient({
        ...form,
        date_of_birth: form.date_of_birth || null
      });
      setSelectedPatient(patient);
      setForm(emptyPatient);
      setShowForm(false);
      setSuccess(`Đã tạo hồ sơ bệnh nhân ${patient.full_name}.`);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }

  async function saveConsents(event) {
    event.preventDefault();
    if (!selectedPatient || consentSavingRef.current) return;
    consentSavingRef.current = true;
    setConsentSaving(true);
    setError('');
    setSuccess('');
    try {
      setSelectedPatient(await onUpdatePatient(selectedPatient.id, consentForm));
      setSuccess('Đã lưu xác nhận đồng ý.');
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      consentSavingRef.current = false;
      setConsentSaving(false);
    }
  }

  return <section className="page-section management-page">
    <div className="section-toolbar">
      <div><span className="eyebrow">DANH SÁCH BỆNH NHÂN</span><h2>Hồ sơ bệnh nhân</h2></div>
      {canCreate && <button className="primary-button" onClick={() => { setShowForm(!showForm); setError(''); setSuccess(''); }}>
        <UserRound size={17} /> {showForm ? 'Hủy' : 'Thêm bệnh nhân'}
      </button>}
    </div>
    {success && <div className="form-success" role="status">{success}</div>}
    {error && <div className="form-error" role="alert">{error}</div>}
    {passwordResetTarget && <AdminPasswordResetDialog
      target={passwordResetTarget}
      onSave={(newPassword) => onResetPassword('patient', passwordResetTarget.id, newPassword)}
      onClose={() => setPasswordResetTarget(null)}
    />}
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
        <label className="checkbox-field form-wide"><input type="checkbox" checked={form.ai_processing_consent} onChange={(event) => setForm({ ...form, ai_processing_consent: event.target.checked })} /> Bệnh nhân đồng ý gửi nội dung lâm sàng đã loại bỏ thông tin nhận dạng đến Gemini để tạo bản tóm tắt bằng AI.</label>
        <label className="checkbox-field form-wide"><input type="checkbox" checked={form.sms_reminder_consent} onChange={(event) => setForm({ ...form, sms_reminder_consent: event.target.checked })} /> Bệnh nhân đồng ý nhận tin nhắn nhắc tái khám.</label>
      </div>
      <div className="form-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Đang lưu…' : 'Tạo hồ sơ'}</button></div>
    </form>}
    {selectedPatient && <section className="panel patient-profile">
      <div className="panel-heading"><div><span className="eyebrow">HỒ SƠ BỆNH NHÂN</span><h3>{selectedPatient.full_name}</h3></div><div className="row-actions">
        {canResetPasswords && selectedPatient.has_login_account && <button className="secondary-button" type="button" onClick={() => setPasswordResetTarget(selectedPatient)}>Tài khoản</button>}
        <button className="secondary-button" type="button" onClick={() => setSelectedPatient(null)}>Đóng</button>
      </div></div>
      {canResetPasswords && !selectedPatient.has_login_account && <p className="account-dialog-hint">Hồ sơ này chưa liên kết tài khoản đăng nhập nên không thể đặt lại mật khẩu.</p>}
      <div className="patient-profile-grid">
        <div><span>Mã bệnh nhân</span><strong>{selectedPatient.patient_code}</strong></div>
        <div><span>Số điện thoại</span><strong>{selectedPatient.phone || '—'}</strong></div>
        <div><span>Ngày sinh</span><strong>{selectedPatient.date_of_birth ? new Date(`${selectedPatient.date_of_birth}T00:00:00`).toLocaleDateString('vi-VN') : '—'}</strong></div>
        <div><span>Bộ răng</span><strong>{selectedPatient.dentition_type === 'CHILD' ? 'Trẻ em · 20 răng' : 'Người lớn · 32 răng'}</strong></div>
        <div><span>Dị ứng</span><p>{selectedPatient.allergies || 'Chưa ghi nhận dị ứng'}</p></div>
        <div><span>Tiền sử bệnh</span><p>{selectedPatient.medical_history || 'Chưa ghi nhận tiền sử bệnh'}</p></div>
      </div>
      {canCreate && <form className="management-form" onSubmit={saveConsents}>
        <h4>Thông tin đồng ý liên lạc và xử lý bằng AI</h4>
        <label className="checkbox-field"><input type="checkbox" checked={consentForm.ai_processing_consent} onChange={(event) => setConsentForm({ ...consentForm, ai_processing_consent: event.target.checked })} /> Bệnh nhân đồng ý gửi nội dung lâm sàng đã loại bỏ thông tin nhận dạng đến Gemini để tạo bản tóm tắt bằng AI.</label>
        <label className="checkbox-field"><input type="checkbox" checked={consentForm.sms_reminder_consent} onChange={(event) => setConsentForm({ ...consentForm, sms_reminder_consent: event.target.checked })} /> Bệnh nhân đồng ý nhận tin nhắn nhắc tái khám.</label>
        <div className="form-actions"><button className="secondary-button" type="submit" disabled={consentSaving}>{consentSaving ? 'Đang lưu…' : 'Lưu thông tin đồng ý'}</button></div>
      </form>}
    </section>}
    <div className="search-field"><Search size={17} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Tìm theo tên, mã bệnh nhân hoặc số điện thoại" /></div>
    <div className="panel table-panel" aria-busy={loading}>
      {loading ? <p className="management-state" role="status">Đang tải hồ sơ bệnh nhân…</p> : patients.length === 0 ? <p className="management-state">{query ? 'Không tìm thấy bệnh nhân phù hợp.' : 'Chưa có hồ sơ bệnh nhân.'}</p> :
        <table><thead><tr><th>Bệnh nhân</th><th>Mã</th><th>Điện thoại</th><th>Bộ răng</th><th>Thông tin dị ứng</th><th>Hồ sơ</th></tr></thead>
          <tbody>{patients.map((patient) => <tr key={patient.id}>
            <td><div className="table-person"><div className="small-avatar">{patient.full_name.split(' ').map((part) => part[0]).slice(-2).join('')}</div><strong>{patient.full_name}</strong></div></td>
            <td><code>{patient.patient_code}</code></td><td>{patient.phone || '—'}</td>
            <td><span className="pill">{patient.dentition_type === 'CHILD' ? '20 răng · trẻ em' : '32 răng · người lớn'}</span></td>
            <td>{patient.allergies || 'Chưa ghi nhận dị ứng'}</td>
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
  const savingRef = useRef(false);
  const cancellationRef = useRef(false);
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
    if (savingRef.current) return;
    const reason = booking.notes.trim();
    if (!booking.patient || !booking.doctor || !booking.service || !booking.date || !booking.time || !reason) {
      setError('Vui lòng điền đầy đủ các mục bắt buộc, gồm cả lý do khám.');
      return;
    }
    savingRef.current = true;
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
      setSuccess(`Đã gửi yêu cầu đặt lịch${patientName ? ` cho ${patientName}` : ''}. Lịch mới được hiển thị trong ngày đã chọn.`);
      setBooking((current) => ({ ...current, patient: '', notes: '' }));
    } catch (saveError) {
      setError(saveError.message || 'Không thể gửi yêu cầu đặt lịch. Vui lòng thử lại.');
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }

  async function submitSchedule(event) {
    event.preventDefault();
    if (savingRef.current) return;
    savingRef.current = true;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await onCreateSchedule({
        doctor: Number(schedule.doctor),
        work_date: schedule.work_date,
        start_time: schedule.start_time,
        end_time: schedule.end_time
      });
      setScheduleOpen(false);
      setSuccess('Đã lưu ca làm việc của bác sĩ.');
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }

  async function confirmCancellation() {
    if (!cancellationTarget || cancellationRef.current) return;
    cancellationRef.current = true;
    setCancelling(true);
    setCancellationError('');
    try {
      await onCancelAppointment(cancellationTarget.id);
      setSuccess(`Đã hủy lịch hẹn của ${cancellationTarget.patient_name}.`);
      setCancellationTarget(null);
    } catch (cancelError) {
      setCancellationError(cancelError.message || 'Không thể hủy lịch hẹn. Vui lòng thử lại.');
    } finally {
      cancellationRef.current = false;
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
      <div><span className="eyebrow">THỜI KHÓA BIỂU PHÒNG KHÁM</span><h2>Lịch hẹn và ca làm việc</h2></div>
      <div className="calendar-actions">
        {isReceptionRole && <button className="secondary-button" disabled={saving} onClick={() => { setScheduleOpen(!scheduleOpen); setError(''); setSuccess(''); }}>{scheduleOpen ? 'Đóng biểu mẫu ca làm' : 'Thêm ca làm việc'}</button>}
        {isReceptionRole && <button className="primary-button" disabled={saving} onClick={() => openBooking(calendarDate, '09:00')}><CalendarDays size={17} /> Đặt lịch hẹn</button>}
      </div>
    </div>
    {success && <div className="form-success" role="status">{success}</div>}
    {error && <div className="form-error" role="alert">{error}</div>}
    {cancellationTarget && <div className="confirmation-backdrop">
      <section className="panel cancellation-dialog" role="dialog" aria-modal="true" aria-labelledby="cancel-dialog-title">
        <h3 id="cancel-dialog-title">Bạn muốn hủy lịch hẹn này?</h3>
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
      <div className="form-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Đang lưu…' : 'Lưu ca làm việc'}</button><button className="secondary-button" type="button" disabled={saving} onClick={() => setScheduleOpen(false)}>Hủy</button></div>
    </form>}
    {bookingOpen && <form className="panel management-form" onSubmit={submitBooking}>
      <h3>Đặt lịch hẹn</h3>
      <div className="form-grid">
        <label>Bệnh nhân<select required value={booking.patient} onChange={(event) => setBooking({ ...booking, patient: event.target.value })}><option value="">Chọn bệnh nhân</option>{patients.map((patient) => <option key={patient.id} value={patient.id}>{patient.full_name} · {patient.patient_code}</option>)}</select></label>
        <label>Bác sĩ<select required value={booking.doctor} onChange={(event) => setBooking({ ...booking, doctor: event.target.value })}><option value="">Chọn bác sĩ</option>{doctors.map((doctor) => <option key={doctor.id} value={doctor.id}>{doctor.full_name}</option>)}</select></label>
        <label>Dịch vụ<select required value={booking.service} onChange={(event) => setBooking({ ...booking, service: event.target.value })}><option value="">Chọn dịch vụ</option>{services.map((service) => <option key={service.id} value={service.id}>{localizeCatalogText(service.name)} · {service.duration_minutes} phút</option>)}</select></label>
        <label>Ngày<input required type="date" value={booking.date} onChange={(event) => setBooking({ ...booking, date: event.target.value })} /></label>
        <label>Giờ bắt đầu<input required type="time" value={booking.time} onChange={(event) => setBooking({ ...booking, time: event.target.value })} /></label>
        <label className="booking-reason">Lý do khám<textarea required maxLength={1000} value={booking.notes} onChange={(event) => setBooking({ ...booking, notes: event.target.value })} /></label>
      </div>
      <p className="management-hint">Bác sĩ được chọn cần có ca làm bao trọn thời lượng dịch vụ. Hệ thống sẽ từ chối các lịch bị trùng.</p>
      <div className="form-actions"><button className="primary-button" type="submit" disabled={saving}>{saving ? 'Đang đặt lịch…' : 'Xác nhận đặt lịch'}</button><button className="secondary-button" type="button" disabled={saving} onClick={() => setBookingOpen(false)}>Hủy</button></div>
    </form>}
    <div className="calendar-toolbar panel">
      <div className="calendar-navigation">
        <button className="secondary-button" onClick={() => setCalendarDate(new Date(calendarDate.getFullYear(), calendarDate.getMonth(), calendarDate.getDate() - (calendarMode === 'day' ? 1 : 7), 12))}>{calendarMode === 'day' ? 'Ngày trước' : 'Tuần trước'}</button>
        <button className="secondary-button" onClick={() => setCalendarDate(new Date())}>Hôm nay</button>
        <button className="secondary-button" onClick={() => setCalendarDate(new Date(calendarDate.getFullYear(), calendarDate.getMonth(), calendarDate.getDate() + (calendarMode === 'day' ? 1 : 7), 12))}>{calendarMode === 'day' ? 'Ngày sau' : 'Tuần sau'}</button>
      </div>
      <strong>{calendarMode === 'day'
        ? calendarDate.toLocaleDateString('vi-VN', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' })
        : `${days[0].toLocaleDateString('vi-VN', { month: 'short', day: 'numeric' })} – ${days[6].toLocaleDateString('vi-VN', { month: 'short', day: 'numeric', year: 'numeric' })}`}</strong>
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
    {loadError && <div className="form-error" role="alert">Không tải được lịch: {loadError}</div>}
    {doctors.length === 0 && !loading && !loadError && <div className="management-state" role="status">Chưa có hồ sơ bác sĩ.</div>}
    {loading ? <div className="panel management-state" role="status">Đang tải lịch hẹn và ca làm…</div> :
      loadError ? <div className="panel management-state">Không có dữ liệu lịch. Vui lòng kiểm tra kết nối và thử lại.</div> :
      <>
        {!visibleSchedules.length && !visibleAppointments.length && <div className="panel management-state" role="status">Không có ca làm hoặc lịch hẹn trong {calendarMode === 'day' ? 'ngày này' : 'tuần này'}.</div>}
        <div className="calendar-legend" aria-label="Chú thích lịch">
          <span><i className="legend-shift" /> Giờ làm việc của bác sĩ</span>
          <span><i className="legend-unavailable" /> Ngoài giờ làm việc</span>
          <span><i className="legend-appointment" /> Lịch hẹn</span>
        </div>
        <div className="panel timetable-panel">
          <div className={`timetable-grid ${calendarMode === 'day' ? 'day-view' : ''}`} style={{ '--calendar-day-count': days.length }}>
            <div className="timetable-row timetable-header-row">
              <div className="timetable-head timetable-time">Giờ</div>
              {days.map((date) => <div className="timetable-head" key={dateKey(date)}><strong>{date.toLocaleDateString('vi-VN', { weekday: 'short' })}</strong><span>{date.toLocaleDateString('vi-VN', { month: 'short', day: 'numeric' })}</span></div>)}
            </div>
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
                      <span>{localizeCatalogText(item.service_name || item.type || 'Khám răng')} · {item.dentist_name}</span>
                      <small>{statusLabel(item.status)}</small>
                      {item.notes && <small className="calendar-event-reason">Lý do: {item.notes}</small>}
                    </div>;
                  })}
                  {!events.length && !slotBusy && isReceptionRole && shifts.length > 0 && <button aria-label={`Đặt lịch ngày ${key} lúc ${time}`} className="empty-slot" onClick={() => openBooking(date, time)} title="Đặt lịch trong khung giờ còn trống này">+</button>}
                </div>;
              })}
            </div>)}
          </div>
        </div>
        <div className="panel appointment-list-panel"><div className="panel-heading"><div><span className="eyebrow">{calendarMode === 'day' ? 'NGÀY ĐANG CHỌN' : 'TUẦN ĐANG CHỌN'}</span><h3>Lịch hẹn trong khoảng thời gian này</h3></div></div>
          {visibleAppointments.length ? <div className="appointment-list">{[...visibleAppointments].sort((a, b) => new Date(a.appointment_date || a.start_at) - new Date(b.appointment_date || b.start_at)).map((item) => <AppointmentRow key={item.id} item={item} canCancel={isReceptionRole} cancelling={cancelling} onCancel={(target) => { setCancellationTarget(target); setCancellationError(''); setSuccess(''); }} />)}</div> : <p className="management-state">{calendarMode === 'day' ? 'Ngày này chưa có lịch hẹn.' : 'Tuần này chưa có lịch hẹn.'}</p>}
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
      setError('Hãy nhập mã bệnh nhân, họ tên hoặc số điện thoại bằng chữ cái, chữ số, khoảng trắng và dấu câu thông dụng.');
      return;
    }

    setLoading(true);
    try {
      const result = await apiRequest(`/patients/?search=${encodeURIComponent(searchTerm)}`, {
        tokens,
        onTokens: onTokensChanged
      });
      if (!Array.isArray(result)) {
        throw new Error('Kết quả tìm kiếm bệnh nhân không đúng định dạng.');
      }
      setPatients(result);
      setSelectedPatientId(result.length === 1 ? result[0].id : null);
    } catch (searchError) {
      setError(searchError.message || 'Không thể tìm bệnh nhân. Vui lòng thử lại.');
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
      <div><span className="eyebrow">QUẦY TIẾP ĐÓN</span><h2>Tiếp nhận bệnh nhân</h2></div>
      {selectedPatient && <button className="primary-button" onClick={() => setSection('Appointments')}><CalendarDays size={17} /> Tiếp tục đặt lịch</button>}
    </div>
    <form className="panel reception-search" onSubmit={searchPatients} noValidate>
      <label htmlFor="reception-search">Tìm bệnh nhân đã có hồ sơ</label>
      <p>Tìm theo mã bệnh nhân, toàn bộ hoặc một phần họ tên, hay số điện thoại.</p>
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
    {!loading && !error && !term.trim() && <div className="panel reception-state">Nhập mã bệnh nhân, họ tên hoặc số điện thoại để bắt đầu.</div>}
    {!loading && !error && term.trim() && !searched && <div className="panel reception-state">Nhấn Tìm kiếm để tra cứu bệnh nhân.</div>}
    {!loading && !error && searched && patients.length === 0 && <div className="panel reception-state" role="status">Không tìm thấy bệnh nhân. Hãy kiểm tra thông tin và tìm lại.</div>}
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
          <div><dt>Số điện thoại</dt><dd>{selectedPatient.phone || 'Chưa ghi nhận'}</dd></div>
          <div><dt>Ngày sinh</dt><dd>{formatDate(selectedPatient.date_of_birth)}{patientAge(selectedPatient.date_of_birth) !== null ? ` · ${patientAge(selectedPatient.date_of_birth)} tuổi` : ''}</dd></div>
          <div><dt>Bộ răng</dt><dd>{selectedPatient.dentition_type === 'CHILD' ? 'Trẻ em · 20 răng' : 'Người lớn · 32 răng'}</dd></div>
          <div className="reception-medical-alert"><dt>Dị ứng</dt><dd>{selectedPatient.allergies || 'Chưa ghi nhận'}</dd></div>
          <div className="profile-wide"><dt>Tiền sử bệnh</dt><dd>{selectedPatient.medical_history || 'Chưa ghi nhận'}</dd></div>
        </dl>
        <div className="reception-visit-history">
          <span className="eyebrow">LỊCH SỬ KHÁM</span>
          {patientAppointments.length
            ? patientAppointments.map((appointment) => <div key={appointment.id}><strong>{new Date(appointment.appointment_date || appointment.start_at).toLocaleString('vi-VN')}</strong><span>{localizeCatalogText(appointment.service_name || appointment.type || 'Khám răng')} · {statusLabel(appointment.status)}</span></div>)
            : <p>Chưa có lịch hẹn.</p>}
        </div>
      </section>}
      {!selectedPatient && <div className="panel reception-state">Chọn bệnh nhân trong kết quả để xem thông tin tiếp nhận.</div>}
    </div>}
  </section>;
}

function MedicalRecords({ appointments, patients, services, teeth, records, loading, loadError, onSave, onGenerateSummary }) {
  const eligibleAppointments = appointments.filter((item) => item.status !== 'Cancelled' && item.status !== 'CANCELLED');
  const [appointmentId, setAppointmentId] = useState('');
  const [form, setForm] = useState({ diagnosis: '', treatment_plan: '', prescription: '', notes: '', teeth: [], services: [], follow_up_date: '' });
  const [saving, setSaving] = useState(false);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summary, setSummary] = useState('');
  const [summaryRetryable, setSummaryRetryable] = useState(false);
  const [summaryError, setSummaryError] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const summaryInFlight = useRef(false);
  const savingRef = useRef(false);
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
      services: record.services || [],
      follow_up_date: record.follow_up_date || ''
    } : { diagnosis: '', treatment_plan: '', prescription: '', notes: '', teeth: [], services: [], follow_up_date: '' });
    setError('');
    setSummary('');
    setSummaryRetryable(false);
    setSummaryError('');
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
    if (savingRef.current) return;
    savingRef.current = true;
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      await onSave({
        ...form,
        appointment: Number(appointmentId),
        follow_up_date: form.follow_up_date || null
      }, record?.id);
      setSuccess('Đã lưu hồ sơ khám.');
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }

  async function requestSummary() {
    if (!record || summaryInFlight.current) return;
    summaryInFlight.current = true;
    setSummaryLoading(true);
    setSummaryError('');
    setSummaryRetryable(false);
    try {
      const result = await onGenerateSummary(record.id);
      setSummary(result.summary);
    } catch (requestError) {
      setSummaryError(requestError.message);
      setSummaryRetryable(requestError.retryable === true);
    } finally {
      summaryInFlight.current = false;
      setSummaryLoading(false);
    }
  }

  return <section className="page-section management-page">
    <div className="section-toolbar"><div><span className="eyebrow">HỒ SƠ LÂM SÀNG</span><h2>Hồ sơ bệnh án điện tử</h2></div></div>
    {loading && <div className="panel management-state" role="status">Đang tải lịch hẹn, hồ sơ, sơ đồ răng và dịch vụ…</div>}
    {loadError && <div className="form-error" role="alert">Không tải được dữ liệu hồ sơ khám: {loadError}</div>}
    {error && <div className="form-error" role="alert">{error}</div>}
    {success && <div className="form-success" role="status">{success}</div>}
    {!loading && !loadError && !eligibleAppointments.length && <div className="panel management-state">Chưa có lịch hẹn để ghi nhận hồ sơ khám.</div>}
    {!loading && !loadError && eligibleAppointments.length > 0 && selectedAppointment && <form className="panel management-form emr-form" onSubmit={saveRecord}>
      <label className="emr-appointment">Lịch hẹn đang được khám
        <select value={appointmentId} disabled={summaryLoading || saving} onChange={(event) => { setAppointmentId(event.target.value); setSuccess(''); }}>
          {eligibleAppointments.map((item) => <option key={item.id} value={item.id}>{new Date(item.appointment_date || item.start_at).toLocaleString('vi-VN')} · {item.patient_name} · {item.dentist_name}</option>)}
        </select>
      </label>
      {selectedPatient && <div className="emr-patient-alert">
        <div className="emr-patient-heading"><strong>{selectedPatient.full_name}</strong><span>{selectedPatient.patient_code} · {selectedPatient.phone || 'Chưa có số điện thoại'}</span></div>
        <div className="emr-appointment-details">
          <span><strong>Lịch hẹn:</strong> {new Date(selectedAppointment.appointment_date || selectedAppointment.start_at).toLocaleString('vi-VN')}</span>
          <span><strong>Bác sĩ:</strong> {selectedAppointment.dentist_name || 'Chưa ghi nhận'}</span>
          <span><strong>Trạng thái:</strong> {statusLabel(selectedAppointment.status)}</span>
        </div>
        <p><strong>Dị ứng:</strong> {selectedPatient.allergies || 'Chưa ghi nhận'} · <strong>Tiền sử bệnh:</strong> {selectedPatient.medical_history || 'Chưa ghi nhận'}</p>
      </div>}
      <label>Chẩn đoán<textarea required rows="3" value={form.diagnosis} onChange={(event) => setForm({ ...form, diagnosis: event.target.value })} /></label>
      <label>Kế hoạch điều trị<textarea required rows="3" value={form.treatment_plan} onChange={(event) => setForm({ ...form, treatment_plan: event.target.value })} /></label>
      <div className="emr-selection-grid">
        <fieldset className="emr-teeth-fieldset">
          <legend>Răng được khám hoặc điều trị ({form.teeth.length} răng đã chọn)</legend>
          {!patientTeeth.length ? <p className="emr-empty-options">Chưa có sơ đồ răng phù hợp với bộ răng của bệnh nhân này.</p> : <div className="emr-tooth-chart">
            <span className="emr-arch-label">HÀM TRÊN</span>
            <div className="emr-tooth-row">{patientTeeth.slice(0, midpoint).map((tooth) => <button key={tooth.id} type="button" aria-pressed={form.teeth.includes(tooth.id)} className={`emr-tooth ${form.teeth.includes(tooth.id) ? 'selected' : ''}`} onClick={() => toggleSelection('teeth', tooth.id)}>{tooth.code}</button>)}</div>
            <div className="emr-mouth-line" />
            <div className="emr-tooth-row lower">{patientTeeth.slice(midpoint).reverse().map((tooth) => <button key={tooth.id} type="button" aria-pressed={form.teeth.includes(tooth.id)} className={`emr-tooth ${form.teeth.includes(tooth.id) ? 'selected' : ''}`} onClick={() => toggleSelection('teeth', tooth.id)}>{tooth.code}</button>)}</div>
            <span className="emr-arch-label lower">HÀM DƯỚI</span>
          </div>}
        </fieldset>
        <fieldset>
          <legend>Dịch vụ điều trị ({form.services.length} dịch vụ đã chọn)</legend>
          {!services.length ? <p className="emr-empty-options">Hiện không có dịch vụ nào đang hoạt động.</p> : <div className="service-options">
            {services.map((service) => <label key={service.id}>
              <input type="checkbox" checked={form.services.includes(service.id)} onChange={() => toggleSelection('services', service.id)} />
              <span><strong>{localizeCatalogText(service.name)}</strong><small>{service.description || 'Chưa có mô tả dịch vụ'} · {service.duration_minutes} phút</small></span>
              <small>{Number(service.price).toLocaleString('vi-VN')} ₫</small>
            </label>)}
          </div>}
        </fieldset>
      </div>
      <label>Đơn thuốc<textarea rows="2" value={form.prescription} onChange={(event) => setForm({ ...form, prescription: event.target.value })} /></label>
      <label>Ghi chú lâm sàng<textarea rows="2" value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} /></label>
      <label>Ngày tái khám<input type="date" value={form.follow_up_date} onChange={(event) => setForm({ ...form, follow_up_date: event.target.value })} /></label>
      <p>Tin nhắn nhắc tái khám chỉ được gửi khi bệnh nhân đã đồng ý nhận tin nhắn, có số điện thoại hợp lệ và tác vụ gửi nhắc hằng ngày đã được cấu hình.</p>
      <div className="form-actions"><button className="primary-button" disabled={saving || !appointmentId}>{saving ? 'Đang lưu…' : record ? 'Cập nhật hồ sơ khám' : 'Lưu hồ sơ khám'}</button></div>
    </form>}
    {!loading && record && <section className="panel management-form">
      <h3>Tóm tắt bằng AI · Gemini</h3>
      <p className="management-hint">Sau khi bệnh nhân đồng ý, Gemini nhận chẩn đoán, kế hoạch điều trị, đơn thuốc, ghi chú, tên dịch vụ và mã răng. Hệ thống lọc tên, mã bệnh nhân, điện thoại, email và các định dạng ngày phổ biến khi phát hiện; không gửi ngày sinh, dị ứng hay tiền sử riêng từ hồ sơ bệnh nhân. Đây là lọc theo mẫu, không bảo đảm ẩn danh hoàn toàn. Bác sĩ cần rà soát kết quả; AI không tự sửa hồ sơ và không thay thế đánh giá chuyên môn.</p>
      {!selectedPatient?.ai_processing_consent && <p role="status">Chưa ghi nhận bệnh nhân đồng ý xử lý hồ sơ bằng AI.</p>}
      <button className="secondary-button" type="button" disabled={!selectedPatient?.ai_processing_consent || summaryLoading || Boolean(summaryError && !summaryRetryable)} onClick={requestSummary}>{summaryLoading ? 'Đang xử lý AI…' : summaryRetryable ? 'Thử lại' : 'Tạo tóm tắt AI'}</button>
      {summaryLoading && <p className="management-state" role="status">Đang chờ dịch vụ AI phản hồi…</p>}
      {summaryError && <div className="form-error" role="alert">{summaryError}</div>}
      {summary && <div className="panel" role="status"><strong>Bản nháp do AI tạo — bác sĩ cần kiểm tra</strong><p>{summary}</p></div>}
    </section>}
  </section>;
}
function ToothChart({
  dentition,
  setDentition,
  selectedTooth,
  setSelectedTooth,
  patients,
  teeth,
  tokens,
  onTokensChanged
}) {
  const [patientId, setPatientId] = useState('');
  const [conditions, setConditions] = useState([]);
  const [condition, setCondition] = useState('Healthy');
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [saved, setSaved] = useState('');
  const saveInFlight = useRef(false);
  const eligiblePatients = patients.filter((patient) => patient.dentition_type === dentition);
  const selectedPatient = eligiblePatients.find((patient) => String(patient.id) === patientId);
  const chartTeeth = teeth
    .filter((tooth) => tooth.dentition_type === dentition)
    .sort((left, right) => left.display_order - right.display_order);
  const selectedCondition = conditions.find(
    (item) => item.tooth === selectedTooth
  );

  useEffect(() => {
    if (!eligiblePatients.some((patient) => String(patient.id) === patientId)) {
      setPatientId(eligiblePatients.length ? String(eligiblePatients[0].id) : '');
      setSelectedTooth(null);
    }
  }, [dentition, patients, patientId, setSelectedTooth]);

  useEffect(() => {
    if (!selectedPatient) {
      setConditions([]);
      setLoading(false);
      return undefined;
    }

    let active = true;
    setLoading(true);
    setError('');
    apiRequest(`/tooth-conditions/?patient=${encodeURIComponent(selectedPatient.id)}`, {
      tokens,
      onTokens: onTokensChanged
    }).then((items) => {
      if (active) setConditions(items);
    }).catch((loadError) => {
      if (active) setError(loadError.message);
    }).finally(() => {
      if (active) setLoading(false);
    });
    return () => { active = false; };
  }, [selectedPatient?.id, tokens, onTokensChanged]);

  useEffect(() => {
    setCondition(selectedCondition?.condition || 'Healthy');
    setNote(selectedCondition?.note || '');
    setSaved('');
  }, [selectedTooth, selectedCondition?.condition, selectedCondition?.note]);

  async function saveCondition(event) {
    event.preventDefault();
    if (!selectedPatient || !selectedTooth || saveInFlight.current) return;

    saveInFlight.current = true;
    setSaving(true);
    setError('');
    setSaved('');
    try {
      const result = await apiRequest('/tooth-conditions/', {
        tokens,
        onTokens: onTokensChanged,
        method: 'POST',
        body: {
          patient: selectedPatient.id,
          tooth: selectedTooth,
          condition,
          note
        }
      });
      setConditions((current) => [
        ...current.filter((item) => item.tooth !== result.tooth),
        result
      ]);
      setSaved(`Đã lưu tình trạng răng ${result.tooth_code}.`);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      saveInFlight.current = false;
      setSaving(false);
    }
  }

  function changeDentition(value) {
    setDentition(value);
    setSelectedTooth(null);
  }

  function renderArch(items, lower = false) {
    const archTeeth = lower ? items.slice(Math.ceil(items.length / 2)).reverse() : items.slice(0, Math.ceil(items.length / 2));
    return <div className={`teeth-grid ${lower ? 'lower ' : ''}${dentition.toLowerCase()}`}>
      {archTeeth.map((tooth) => {
        const savedCondition = conditions.find((item) => item.tooth === tooth.id);
        const toothState = (savedCondition?.condition || 'Healthy').toLowerCase().replace(/\s+/g, '-');
        return <Tooth
          key={tooth.id}
          tooth={{ ...tooth, state: toothState }}
          selected={selectedTooth === tooth.id}
          onClick={() => setSelectedTooth(tooth.id)}
        />;
      })}
    </div>;
  }

  return <section className="page-section">
    <div className="section-toolbar">
      <div><span className="eyebrow">HỒ SƠ LÂM SÀNG</span><h2>Sơ đồ răng tương tác</h2></div>
      <div className="segmented">
        <button type="button" className={dentition === 'ADULT' ? 'selected' : ''} onClick={() => changeDentition('ADULT')}>Người lớn · 32 răng</button>
        <button type="button" className={dentition === 'CHILD' ? 'selected' : ''} onClick={() => changeDentition('CHILD')}>Trẻ em · 20 răng</button>
      </div>
    </div>
    {patients.length > 0 && <label className="tooth-patient-select">Bệnh nhân
      <select value={patientId} onChange={(event) => { setPatientId(event.target.value); setSelectedTooth(null); }}>
        {eligiblePatients.map((patient) => <option key={patient.id} value={patient.id}>{patient.patient_code} · {patient.full_name}</option>)}
      </select>
    </label>}
    {error && <div className="form-error" role="alert">{error}</div>}
    {loading && <div className="management-state" role="status">Đang tải tình trạng răng đã lưu…</div>}
    {!selectedPatient && <div className="panel reception-state">Không có bệnh nhân thuộc bộ răng này.</div>}
    {selectedPatient && <div className="chart-layout">
      <div className="panel tooth-panel">
        <div className="chart-header">
          <div><strong>{selectedPatient.full_name}</strong><span>{selectedPatient.patient_code} · {dentition === 'ADULT' ? 'Răng vĩnh viễn' : 'Răng sữa'}</span></div>
        </div>
        <div className="mouth-label">HÀM TRÊN</div>
        {renderArch(chartTeeth)}
        <div className="mouth-line" />
        {renderArch(chartTeeth, true)}
        <div className="mouth-label lower-label">HÀM DƯỚI</div>
        <div className="chart-legend"><span><i className="dot healthy" />Khỏe mạnh</span><span><i className="dot care" />Cần điều trị</span><span><i className="dot monitor" />Theo dõi</span><span><i className="dot restored" />Đã phục hồi</span></div>
      </div>
      <aside className="panel tooth-detail">
        <span className="eyebrow">RĂNG ĐANG CHỌN</span>
        {selectedTooth ? <form onSubmit={saveCondition}>
          <div className="tooth-number">{chartTeeth.find((tooth) => tooth.id === selectedTooth)?.code}</div>
          <label>Tình trạng lâm sàng
            <select value={condition} onChange={(event) => setCondition(event.target.value)} disabled={loading || saving}>
              <option value="Healthy">Khỏe mạnh</option><option value="Needs care">Cần điều trị</option><option value="Monitor">Theo dõi</option><option value="Restored">Đã phục hồi</option>
            </select>
          </label>
          <label>Ghi chú lâm sàng<textarea rows="4" maxLength={2000} value={note} onChange={(event) => setNote(event.target.value)} disabled={loading || saving} /></label>
          <button className="primary-button full" type="submit" disabled={loading || saving}>{saving ? 'Đang lưu…' : 'Lưu tình trạng'}</button>
          {saved && <p role="status">{saved}</p>}
        </form> : <div className="empty-detail"><Stethoscope size={28} /><p>Chọn một chiếc răng để xem hoặc cập nhật tình trạng lâm sàng đã lưu.</p></div>}
      </aside>
    </div>}
  </section>;
}

function Tooth({ tooth, selected, onClick }) {
  const conditionLabels = {
    healthy: 'khỏe mạnh',
    'needs-care': 'cần điều trị',
    monitor: 'theo dõi',
    restored: 'đã phục hồi'
  };
  return <button type="button" onClick={onClick} className={`tooth ${tooth.state} ${selected ? 'selected' : ''}`} aria-pressed={selected} aria-label={`${tooth.code}, ${conditionLabels[tooth.state] || 'chưa cập nhật'}`}>
    <span>{tooth.code.slice(1)}</span><div className="tooth-shape" />
  </button>;
}
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
  const savingRef = useRef(false);
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
    if (!selectedRecord || savingRef.current) return;
    savingRef.current = true;
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
      setSuccess(`Đã tạo hóa đơn ${invoice.invoice_number}.`);
    } catch (saveError) {
      setError(saveError.message);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }

  async function confirmCashPayment() {
    if (!selectedInvoice || cashMethod !== 'CASH' || savingRef.current) return;
    savingRef.current = true;
    setSaving(true);
    setCashError('');
    setError('');
    setSuccess('');
    try {
      const paid = await onPayCash(selectedInvoice.id);
      setCashConfirmOpen(false);
      setSuccess(`Đã ghi nhận thanh toán tiền mặt ${Number(paid.paid_amount).toLocaleString('vi-VN')} ₫.`);
    } catch (paymentError) {
      setCashError(paymentError.message);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }

  async function showQrPayment() {
    if (!selectedInvoice || savingRef.current) return;
    savingRef.current = true;
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
      setSuccess('Mã QR chuyển khoản đã sẵn sàng. Hóa đơn vẫn chưa được thanh toán cho đến khi giao dịch ngân hàng được xác minh.');
    } catch (paymentError) {
      setQrError(paymentError.message);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }

  async function confirmQrPayment(event) {
    event.preventDefault();
    if (!selectedInvoice || !bankReference.trim() || !qrVerified || savingRef.current) return;
    savingRef.current = true;
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
      setSuccess(`Đã ghi nhận giao dịch chuyển khoản cho hóa đơn ${paid.invoice_number} sau khi xác minh.`);
    } catch (verificationError) {
      setQrError(verificationError.message);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }

  async function cancelPendingQr() {
    if (!selectedInvoice || !qrCancellationChecked || savingRef.current) return;
    savingRef.current = true;
    setSaving(true);
    setQrError('');
    try {
      const updatedInvoice = await onCancelQr(selectedInvoice.id);
      setQrDialogOpen(false);
      setQrCancellationChecked(false);
      setSuccess(`Đã hủy giao dịch chuyển khoản đang chờ của hóa đơn ${updatedInvoice.invoice_number} sau khi kiểm tra tài khoản.`);
    } catch (cancellationError) {
      setQrError(cancellationError.message);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  }

  return <section className="page-section management-page">
    <div className="section-toolbar"><div><span className="eyebrow">TÀI CHÍNH</span><h2>Hóa đơn</h2></div></div>
    {error && <div className="form-error" role="alert">{error}</div>}
    {success && <div className="form-success" role="status">{success}</div>}
    <section className="panel invoice-create-panel">
      <div className="panel-heading"><div><span className="eyebrow">TỪ DỊCH VỤ ĐƯỢC CHỈ ĐỊNH</span><h3>Tạo hóa đơn</h3></div></div>
      {loading ? <p className="management-state" role="status">Đang tải hóa đơn và dịch vụ được chỉ định…</p> : !records.length ? <p className="management-state">Không có hồ sơ khám nào còn dịch vụ được chỉ định chưa lập hóa đơn.</p> : <form className="invoice-form" onSubmit={createInvoice}>
        <label>Hồ sơ khám
          <select required value={recordId} onChange={(event) => { setRecordId(event.target.value); setSuccess(''); }}>
            {records.map((record) => <option key={record.id} value={record.id}>{record.patient_name} · {record.patient_code} · {new Date(record.appointment_date).toLocaleString('vi-VN')}</option>)}
          </select>
        </label>
        {selectedRecord && <>
          <div className="invoice-patient-summary"><strong>{selectedRecord.patient_name}</strong><span>{selectedRecord.patient_code} · Khám lúc {new Date(selectedRecord.appointment_date).toLocaleString('vi-VN')}</span></div>
          <p className="invoice-source-meta">Dịch vụ được lấy từ hồ sơ khám. Giá được máy chủ xác định và kiểm tra khi tạo hóa đơn.</p>
          <div className="invoice-lines">
            <div className="invoice-line invoice-line-heading"><span>Dịch vụ</span><span>Đơn giá</span><span>Số lượng</span><span>Thành tiền</span></div>
            {selectedRecord.services.map((service) => {
              const quantity = Number(quantities[service.id] || 1);
              const lineTotal = Number(service.price) * quantity;
              return <div className="invoice-line" key={service.id}>
                <strong>{localizeCatalogText(service.name)}</strong>
                <span>{Number(service.price).toLocaleString('vi-VN')} ₫</span>
                <input aria-label={`Số lượng ${localizeCatalogText(service.name)}`} type="number" min="1" max="32767" step="1" required value={quantities[service.id] ?? 1} onChange={(event) => setQuantities((current) => ({ ...current, [service.id]: event.target.value }))} />
                <strong>{lineTotal.toLocaleString('vi-VN')} ₫</strong>
              </div>;
            })}
          </div>
          <div className="invoice-total invoice-grand-total"><span>Tổng cần thanh toán</span><strong>{total.toLocaleString('vi-VN')} ₫</strong></div>
          <p className="invoice-payment-note">Hóa đơn mới được tạo ở trạng thái chưa thanh toán. Có thể thanh toán bằng tiền mặt hoặc chuyển khoản QR trong phần chi tiết hóa đơn.</p>
          <div className="form-actions"><button className="primary-button" type="submit" disabled={saving || !selectedRecord.services.length}>{saving ? 'Đang tạo hóa đơn…' : 'Tạo hóa đơn'}</button></div>
        </>}
      </form>}
    </section>
    <section className="panel table-panel management-table invoice-history-panel">
      <div className="panel-heading"><div><span className="eyebrow">LỊCH SỬ THANH TOÁN</span><h3>Hóa đơn ({invoices.length})</h3></div></div>
      {loading ? <p className="management-state" role="status">Đang tải lịch sử hóa đơn…</p> : !invoices.length ? <p className="management-state">Chưa có hóa đơn nào.</p> : <div className="invoice-table-scroll"><table>
        <thead><tr><th>Hóa đơn</th><th>Bệnh nhân</th><th>Ngày lập</th><th>Tổng tiền</th><th>Đã thanh toán</th><th>Còn nợ</th><th>Trạng thái</th></tr></thead>
        <tbody>{invoices.map((invoice) => <tr key={invoice.id} className={selectedInvoiceId === String(invoice.id) ? 'invoice-row-selected' : ''} onClick={() => setSelectedInvoiceId(String(invoice.id))}>
          <td><button type="button" className="invoice-number-button" aria-label={`Xem hóa đơn ${invoice.invoice_number}`} onClick={() => setSelectedInvoiceId(String(invoice.id))}>{invoice.invoice_number}</button></td>
          <td>{invoice.patient_name}</td><td>{new Date(invoice.issued_at).toLocaleDateString('vi-VN')}</td>
          <td>{Number(invoice.total_amount).toLocaleString('vi-VN')} ₫</td><td>{Number(invoice.paid_amount).toLocaleString('vi-VN')} ₫</td>
          <td>{Number(invoice.balance).toLocaleString('vi-VN')} ₫</td><td><span className={`pill invoice-status ${invoice.status.toLowerCase()}`}>{statusLabel(invoice.status)}</span></td>
        </tr>)}</tbody>
      </table></div>}
    </section>
    {selectedInvoice && <section className="panel invoice-detail-panel">
      <div className="panel-heading"><div><span className="eyebrow">CHI TIẾT HÓA ĐƠN</span><h3>{selectedInvoice.invoice_number} · {selectedInvoice.patient_name}</h3></div><div className="invoice-detail-actions"><span className={`pill invoice-status ${selectedInvoice.status.toLowerCase()}`}>{statusLabel(selectedInvoice.status)}</span>{selectedInvoice.status === 'ISSUED' && Number(selectedInvoice.balance) > 0 && <><button type="button" className="primary-button" disabled={saving || hasPendingQr} title={hasPendingQr ? 'Đang có giao dịch chuyển khoản chờ xác nhận; không ghi nhận thêm giao dịch.' : undefined} onClick={() => { setCashError(''); setCashMethod('CASH'); setCashConfirmOpen(true); }}>Thanh toán tiền mặt</button><button type="button" className="secondary-button" disabled={saving} onClick={showQrPayment}>{hasPendingQr ? 'Hiện mã QR chuyển khoản' : 'Thanh toán bằng QR'}</button></>}</div></div>
      {hasPendingQr && <div className="qr-pending-note" role="status">Giao dịch chuyển khoản đang chờ xác nhận. Hóa đơn chưa được thanh toán; không xem mã QR hoặc thông báo chuyển khoản của bệnh nhân là xác nhận thanh toán.</div>}
      {qrError && <div className="form-error" role="alert">{qrError}</div>}
      <div className="invoice-lines">
        <div className="invoice-line invoice-line-heading"><span>Dịch vụ</span><span>Đơn giá</span><span>Số lượng</span><span>Thành tiền</span></div>
        {selectedInvoice.items.map((item) => <div className="invoice-line" key={item.id}>
          <strong>{localizeCatalogText(item.description)}</strong><span>{Number(item.unit_price).toLocaleString('vi-VN')} ₫</span><span>{item.quantity}</span><strong>{Number(item.amount).toLocaleString('vi-VN')} ₫</strong>
        </div>)}
      </div>
      <div className="invoice-total"><span>Tổng tiền · Còn nợ</span><strong>{Number(selectedInvoice.total_amount).toLocaleString('vi-VN')} ₫ · {Number(selectedInvoice.balance).toLocaleString('vi-VN')} ₫</strong></div>
      {!!selectedInvoice.payments.length && <div className="invoice-payments">
        <h4>Giao dịch thanh toán</h4>
        {selectedInvoice.payments.map((payment) => <div className="invoice-payment-row" key={payment.id}>
          <strong>{Number(payment.amount).toLocaleString('vi-VN')} ₫ · {paymentMethodLabel(payment.method)}</strong>
          <span>{payment.status === 'COMPLETED' && payment.paid_at ? `Đã thanh toán lúc ${new Date(payment.paid_at).toLocaleString('vi-VN')}` : `Tạo lúc ${new Date(payment.created_at).toLocaleString('vi-VN')} · ${statusLabel(payment.status)}`}</span>
          {payment.bank_reference && <span>Mã giao dịch ngân hàng: {payment.bank_reference}</span>}
          {payment.verified_at && <span>Đã xác minh thủ công lúc {new Date(payment.verified_at).toLocaleString('vi-VN')}</span>}
          {payment.verified_by_name && <span>Người xác minh: {payment.verified_by_name}</span>}
          {payment.cancelled_at && <span>Đã hủy lúc {new Date(payment.cancelled_at).toLocaleString('vi-VN')} bởi {payment.cancelled_by_name || 'nhân viên'}</span>}
          {payment.received_by_name && <span>Người nhận: {payment.received_by_name}</span>}
        </div>)}
      </div>}
    </section>}
    {qrDialogOpen && qrTransfer && <div className="confirmation-backdrop" role="presentation">
      <section className="panel cancellation-dialog qr-payment-dialog" role="dialog" aria-modal="true" aria-labelledby="qr-payment-title">
        <h3 id="qr-payment-title">Mã QR chuyển khoản</h3>
        <p>Quét mã này để chuyển đúng số tiền. Hóa đơn sẽ vẫn <strong>chưa thanh toán</strong> cho đến khi giao dịch ngân hàng được xác minh.</p>
        <div className="qr-image-frame">
          {qrImageError ? <p role="alert">Không tải được ảnh mã QR. Hãy dùng thông tin ngân hàng bên dưới để chuyển khoản.</p> : <img src={qrTransfer.qr_url} alt={`Mã VietQR cho hóa đơn ${qrTransfer.description}`} onError={() => setQrImageError(true)} />}
        </div>
        <dl className="qr-transfer-details">
          <div><dt>Số tiền</dt><dd>{Number(qrTransfer.amount).toLocaleString('vi-VN')} ₫</dd></div>
          <div><dt>Ngân hàng</dt><dd>{qrTransfer.bank_id}</dd></div>
          <div><dt>Số tài khoản</dt><dd>{qrTransfer.account_number}</dd></div>
          <div><dt>Tên tài khoản</dt><dd>{qrTransfer.account_name}</dd></div>
          <div><dt>Nội dung chuyển khoản</dt><dd>{qrTransfer.description}</dd></div>
          <div><dt>Trạng thái</dt><dd>Chờ xác minh</dd></div>
        </dl>
        <p className="qr-pending-note">Không xác nhận chỉ dựa trên mã QR hoặc thông báo của bệnh nhân. Hãy kiểm tra tài khoản nhận và đối chiếu chính xác số tiền cùng mã giao dịch. Thao tác này do nhân viên xác minh thủ công, không kết nối trực tiếp với ngân hàng.</p>
        {qrTransfer.status === 'PENDING' && <form className="qr-reconciliation-form" onSubmit={confirmQrPayment}>
          <label>Mã giao dịch ngân hàng<input type="text" required maxLength={100} value={bankReference} onChange={(event) => setBankReference(event.target.value)} /></label>
          <label className="qr-verification-check"><input type="checkbox" checked={qrVerified} onChange={(event) => setQrVerified(event.target.checked)} /> Tôi đã kiểm tra tài khoản nhận và xác nhận mã giao dịch cùng số tiền khớp với hóa đơn này.</label>
          {qrError && <div className="form-error" role="alert">{qrError}</div>}
          <div className="form-actions"><button type="button" className="secondary-button" disabled={saving} onClick={() => setQrDialogOpen(false)}>Đóng</button><button type="submit" className="primary-button" disabled={saving || !bankReference.trim() || !qrVerified}>{saving ? 'Đang ghi nhận…' : 'Ghi nhận giao dịch đã xác minh'}</button></div>
        </form>}
        {qrTransfer.status === 'PENDING' && <div className="qr-cancellation-form">
          <label className="qr-verification-check"><input type="checkbox" checked={qrCancellationChecked} onChange={(event) => setQrCancellationChecked(event.target.checked)} /> Tôi đã kiểm tra tài khoản nhận và xác nhận chưa nhận được khoản chuyển này.</label>
          <button type="button" className="secondary-button" disabled={saving || !qrCancellationChecked} onClick={cancelPendingQr}>{saving ? 'Đang hủy…' : 'Hủy giao dịch đang chờ'}</button>
        </div>}
        {qrTransfer.status !== 'PENDING' && <div className="form-actions"><button type="button" className="secondary-button" onClick={() => setQrDialogOpen(false)}>Đóng</button></div>}
      </section>
    </div>}
    {cashConfirmOpen && selectedInvoice && <div className="confirmation-backdrop" role="presentation">
      <section className="panel cancellation-dialog cash-payment-dialog" role="dialog" aria-modal="true" aria-labelledby="cash-payment-title">
        <h3 id="cash-payment-title">Xác nhận thanh toán tiền mặt</h3>
        <p>Xác nhận đã nhận đủ số tiền còn lại của hóa đơn <strong>{selectedInvoice.invoice_number}</strong>.</p>
        <p className="cash-payment-due">Số tiền đã nhận: <strong>{Number(selectedInvoice.balance).toLocaleString('vi-VN')} ₫</strong></p>
        <fieldset className="cash-method-options"><legend>Phương thức thanh toán</legend>
          <label><input type="radio" name="payment-method" value="CASH" checked={cashMethod === 'CASH'} onChange={() => setCashMethod('CASH')} /> Tiền mặt</label>
        </fieldset>
        {cashError && <div className="form-error" role="alert">{cashError}</div>}
        <div className="form-actions"><button type="button" className="secondary-button" disabled={saving} onClick={() => setCashConfirmOpen(false)}>Hủy</button><button type="button" className="primary-button" disabled={saving || cashMethod !== 'CASH'} onClick={confirmCashPayment}>{saving ? 'Đang ghi nhận thanh toán…' : 'Xác nhận đã nhận tiền'}</button></div>
      </section>
    </div>}
  </section>;
}
function Radiographs({ patients, tokens, onTokensChanged }) {
  const [patientId, setPatientId] = useState('');
  const [radiographs, setRadiographs] = useState([]);
  const [imageUrls, setImageUrls] = useState({});
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const uploadInFlight = useRef(false);

  useEffect(() => {
    if (!patients.some((patient) => String(patient.id) === patientId)) {
      setPatientId(patients.length ? String(patients[0].id) : '');
    }
  }, [patients, patientId]);

  useEffect(() => {
    if (!patientId) {
      setRadiographs([]);
      setLoading(false);
      return undefined;
    }

    let active = true;
    setLoading(true);
    setError('');
    setRadiographs([]);
    apiRequest(`/radiographs/?patient=${encodeURIComponent(patientId)}`, {
      tokens,
      onTokens: onTokensChanged
    }).then((items) => {
      if (active) setRadiographs(items);
    }).catch((loadError) => {
      if (active) setError(loadError.message);
    }).finally(() => {
      if (active) setLoading(false);
    });
    return () => { active = false; };
  }, [patientId, tokens, onTokensChanged]);

  useEffect(() => {
    let active = true;
    const createdUrls = [];
    setImageUrls({});
    Promise.all(radiographs.map(async (radiograph) => {
      const image = await apiRequest(
        `/radiographs/${radiograph.id}/image/`,
        { tokens, onTokens: onTokensChanged, responseType: 'blob' }
      );
      const url = URL.createObjectURL(image);
      createdUrls.push(url);
      return [radiograph.id, url];
    })).then((entries) => {
      if (active) setImageUrls(Object.fromEntries(entries));
    }).catch((loadError) => {
      if (active) setError(loadError.message);
    });
    return () => {
      active = false;
      createdUrls.forEach((url) => URL.revokeObjectURL(url));
    };
  }, [radiographs, tokens, onTokensChanged]);

  async function uploadRadiograph(event) {
    event.preventDefault();
    if (!patientId || !file || uploadInFlight.current) return;

    const form = event.currentTarget;
    uploadInFlight.current = true;
    setUploading(true);
    setError('');
    setNotice('');
    const formData = new FormData();
    formData.append('patient', patientId);
    formData.append('image', file);
    try {
      const created = await apiRequest('/radiographs/', {
        tokens,
        onTokens: onTokensChanged,
        method: 'POST',
        body: formData
      });
      setRadiographs((current) => [created, ...current]);
      setFile(null);
      form.reset();
      setNotice('Đã tải ảnh X-quang lên và lưu vào hồ sơ bệnh nhân.');
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      uploadInFlight.current = false;
      setUploading(false);
    }
  }

  const selectedPatient = patients.find((patient) => String(patient.id) === patientId);
  return <section className="page-section">
    <div className="section-toolbar">
    <div><span className="eyebrow">CHẨN ĐOÁN HÌNH ẢNH</span><h2>Thư viện ảnh X-quang</h2></div>
    </div>
    <section className="panel radiograph-upload-panel">
      <h3>Tải ảnh X-quang của bệnh nhân</h3>
      <p>Chỉ chấp nhận ảnh JPG, JPEG hoặc PNG có dung lượng tối đa 10 MB. Ảnh được bảo mật và chỉ bác sĩ phụ trách cùng quản trị viên mới xem được.</p>
      <form onSubmit={uploadRadiograph}>
        <label>Bệnh nhân
          <select value={patientId} onChange={(event) => setPatientId(event.target.value)} disabled={uploading || patients.length === 0}>
            {patients.map((patient) => <option key={patient.id} value={patient.id}>{patient.patient_code} · {patient.full_name}</option>)}
          </select>
        </label>
        <label>Ảnh X-quang
          <input
            type="file"
            accept="image/jpeg,image/png,.jpg,.jpeg,.png"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
            disabled={uploading || patients.length === 0}
          />
        </label>
        {file && <p className="management-hint">{file.name} · {(file.size / (1024 * 1024)).toFixed(2)} MB</p>}
        <button className="primary-button" type="submit" disabled={!selectedPatient || !file || uploading}>
          <FileImage size={17} />{uploading ? 'Đang tải lên…' : 'Tải ảnh lên'}
        </button>
      </form>
    </section>
    {error && <div className="form-error" role="alert">{error}</div>}
    {notice && <div className="form-success" role="status">{notice}</div>}
    {loading && <div className="management-state" role="status">Đang tải ảnh X-quang…</div>}
    {!loading && selectedPatient && radiographs.length === 0 && !error && <div className="upload-placeholder">
      <FileImage size={30} /><h3>Chưa có ảnh X-quang</h3><p>Ảnh đã tải lên của bệnh nhân {selectedPatient.full_name} sẽ hiển thị tại đây.</p>
    </div>}
    {radiographs.length > 0 && <div className="radiograph-grid">
      {radiographs.map((radiograph) => <article className="panel radiograph-card" key={radiograph.id}>
        {imageUrls[radiograph.id]
          ? <img src={imageUrls[radiograph.id]} alt={`Ảnh X-quang của ${selectedPatient?.full_name}`} />
          : <div className="radiograph-image-loading" role="status">Đang tải ảnh…</div>}
        <div><strong>{radiograph.original_filename}</strong><span>{new Date(radiograph.uploaded_at).toLocaleString('vi-VN')}</span></div>
      </article>)}
    </div>}
  </section>;
}

createRoot(document.getElementById('root')).render(<App />);
