import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, CalendarDays, ChevronDown, CircleDollarSign, ClipboardPlus, FileImage, LayoutDashboard, Menu, Search, Settings2, ShieldCheck, Stethoscope, UserRound, Users, X } from 'lucide-react';
import './styles.css';

const API = 'http://127.0.0.1:8000/api/v1';
const fallbackPatients = [
  { id: 1, patient_code: 'DMS-0001', full_name: 'Nguyen Minh Anh', phone: '090 123 4567', dentition_type: 'ADULT', allergies: 'Penicillin' },
  { id: 2, patient_code: 'DMS-0002', full_name: 'Tran Gia Bao', phone: '091 234 5678', dentition_type: 'CHILD', allergies: '' },
  { id: 3, patient_code: 'DMS-0003', full_name: 'Le Thu Phuong', phone: '098 555 2026', dentition_type: 'ADULT', allergies: 'None recorded' }
];
const fallbackAppointments = [
  { id: 1, patient_name: 'Nguyen Minh Anh', dentist_name: 'Dr. Le Thu Ha', start_at: '09:00', room: 'Room 01', status: 'CONFIRMED', type: 'Implant consultation' },
  { id: 2, patient_name: 'Tran Gia Bao', dentist_name: 'Dr. Pham Quoc', start_at: '10:30', room: 'Room 02', status: 'SCHEDULED', type: 'Child check-up' },
  { id: 3, patient_name: 'Le Thu Phuong', dentist_name: 'Dr. Le Thu Ha', start_at: '13:30', room: 'Room 01', status: 'SCHEDULED', type: 'Cleaning & scan' }
];
const teethAdult = Array.from({ length: 32 }, (_, i) => ({ id: i + 1, code: `A${String(i + 1).padStart(2, '0')}`, state: i === 6 || i === 18 ? 'Needs care' : 'Healthy' }));
const teethChild = Array.from({ length: 20 }, (_, i) => ({ id: i + 1, code: `C${String(i + 1).padStart(2, '0')}`, state: i === 3 ? 'Monitor' : 'Healthy' }));

async function fetchApi(path) { const response = await fetch(`${API}${path}`); if (!response.ok) throw new Error('API unavailable'); return response.json(); }

function App() {
  const [section, setSection] = useState('Overview');
  const [patients, setPatients] = useState(fallbackPatients);
  const [appointments, setAppointments] = useState(fallbackAppointments);
  const [query, setQuery] = useState('');
  const [dentition, setDentition] = useState('ADULT');
  const [selectedTooth, setSelectedTooth] = useState(null);
  const [apiLive, setApiLive] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    Promise.all([fetchApi('/patients/'), fetchApi('/appointments/')]).then(([p, a]) => { setPatients(p); setAppointments(a); setApiLive(true); }).catch(() => setApiLive(false));
  }, []);

  const visiblePatients = patients.filter((patient) => `${patient.full_name} ${patient.patient_code} ${patient.phone}`.toLowerCase().includes(query.toLowerCase()));
  const nav = [
    ['Overview', LayoutDashboard], ['Patients', Users], ['Appointments', CalendarDays], ['Tooth chart', Stethoscope], ['Billing', CircleDollarSign], ['Radiographs', FileImage]
  ];
  return <div className="app-shell">
    <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
      <div className="brand"><div className="brand-mark">D</div><div><strong>DMS</strong><span>Dental management</span></div><button className="icon-button close-menu" onClick={() => setMobileOpen(false)}><X size={18} /></button></div>
      <div className="workspace"><span className="eyebrow">Workspace</span><button className="workspace-button">Lotus Dental Clinic <ChevronDown size={15} /></button></div>
      <nav>{nav.map(([name, Icon]) => <button key={name} className={section === name ? 'nav-item active' : 'nav-item'} onClick={() => { setSection(name); setMobileOpen(false); }}><Icon size={18} /><span>{name}</span>{name === 'Appointments' && <b>3</b>}</button>)}</nav>
      <div className="sidebar-bottom"><button className="nav-item"><Settings2 size={18} /><span>Settings</span></button><div className="user-card"><div className="avatar">LH</div><div><strong>Le Thu Ha</strong><span>Clinic manager</span></div><ChevronDown size={15} /></div></div>
    </aside>
    <main className="main-content">
      <header className="topbar"><button className="icon-button menu-button" onClick={() => setMobileOpen(true)}><Menu size={20} /></button><div><span className="eyebrow">Tuesday, 08 September 2026</span><h1>{section === 'Overview' ? 'Good morning, Ha' : section}</h1></div><div className="topbar-actions"><span className={`api-status ${apiLive ? 'live' : ''}`}><span />{apiLive ? 'Live API' : 'Demo data'}</span><button className="icon-button"><Activity size={19} /></button><div className="avatar">LH</div></div></header>
      {section === 'Overview' && <Overview appointments={appointments} patients={patients} setSection={setSection} />}
      {section === 'Patients' && <Patients patients={visiblePatients} query={query} setQuery={setQuery} />}
      {section === 'Appointments' && <Appointments appointments={appointments} />}
      {section === 'Tooth chart' && <ToothChart dentition={dentition} setDentition={setDentition} selectedTooth={selectedTooth} setSelectedTooth={setSelectedTooth} />}
      {section === 'Billing' && <Billing patients={patients} />}
      {section === 'Radiographs' && <Radiographs />}
    </main>
  </div>;
}

function Overview({ appointments, patients, setSection }) { return <>
  <section className="hero-band"><div><span className="eyebrow warm">TODAY AT A GLANCE</span><h2>Care that keeps moving.</h2><p>Your clinic is ready for a focused day. Three appointments are on deck.</p></div><button className="primary-button" onClick={() => setSection('Appointments')}><CalendarDays size={17} /> View schedule</button></section>
  <section className="metric-grid"><Metric label="Today's appointments" value="12" detail="3 waiting now" accent="blue" icon={CalendarDays} /><Metric label="Active patients" value="248" detail="+18 this month" accent="sage" icon={Users} /><Metric label="Outstanding balance" value="₫42.8m" detail="7 payment plans" accent="gold" icon={CircleDollarSign} /><Metric label="Care plans" value="36" detail="8 need review" accent="coral" icon={ClipboardPlus} /></section>
  <div className="content-grid"><section className="panel schedule-panel"><div className="panel-heading"><div><span className="eyebrow">APPOINTMENTS</span><h3>Today’s schedule</h3></div><button className="text-button" onClick={() => setSection('Appointments')}>View calendar <span>→</span></button></div><div className="appointment-list">{appointments.map((item) => <AppointmentRow key={item.id} item={item} />)}</div></section><section className="panel focus-panel"><div className="panel-heading"><div><span className="eyebrow">CLINIC FOCUS</span><h3>At a glance</h3></div><ShieldCheck size={19} color="#1d6857" /></div><div className="focus-stat"><span className="focus-icon green"><UserRound size={18} /></span><div><strong>{patients.length} patient records</strong><span>Digitized and searchable</span></div></div><div className="focus-stat"><span className="focus-icon peach"><Stethoscope size={18} /></span><div><strong>2 care alerts</strong><span>Need dentist review</span></div></div><div className="alert-box"><strong>Medication check</strong><p>One prescription needs allergy confirmation before signing.</p><button onClick={() => setSection('Patients')}>Review record →</button></div></section></div>
</>; }
function Metric({ label, value, detail, accent, icon: Icon }) { return <div className={`metric-card ${accent}`}><div className="metric-icon"><Icon size={18} /></div><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>; }
function AppointmentRow({ item }) { return <div className="appointment-row"><div className="time">{item.start_at}</div><div className="appointment-avatar">{item.patient_name.split(' ').map((v) => v[0]).slice(-2).join('')}</div><div className="appointment-info"><strong>{item.patient_name}</strong><span>{item.type || 'Dental consultation'} · {item.dentist_name}</span></div><span className={`status ${item.status.toLowerCase()}`}>{item.status === 'CONFIRMED' ? 'Confirmed' : 'Scheduled'}</span></div>; }
function Patients({ patients, query, setQuery }) { return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">PATIENT DIRECTORY</span><h2>Patient records</h2></div><button className="primary-button"><UserRound size={17} /> New patient</button></div><div className="search-field"><Search size={17} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search name, patient code or phone" /></div><div className="panel table-panel"><table><thead><tr><th>Patient</th><th>Code</th><th>Phone</th><th>Dental profile</th><th>Allergy note</th></tr></thead><tbody>{patients.map((p) => <tr key={p.id}><td><div className="table-person"><div className="small-avatar">{p.full_name.split(' ').map((v) => v[0]).slice(-2).join('')}</div><strong>{p.full_name}</strong></div></td><td><code>{p.patient_code}</code></td><td>{p.phone || '—'}</td><td><span className="pill">{p.dentition_type === 'CHILD' ? '20 teeth · child' : '32 teeth · adult'}</span></td><td>{p.allergies || 'No known allergies'}</td></tr>)}</tbody></table></div></section>; }
function Appointments({ appointments }) { return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">LIVE CALENDAR</span><h2>Appointment schedule</h2></div><button className="primary-button"><CalendarDays size={17} /> Book appointment</button></div><div className="calendar-strip"><strong>Tue<br /><b>08</b></strong><span>Wed<br /><b>09</b></span><span>Thu<br /><b>10</b></span><span>Fri<br /><b>11</b></span><span>Sat<br /><b>12</b></span></div><div className="panel schedule-panel"><div className="appointment-list">{appointments.concat(appointments).map((item, index) => <AppointmentRow item={{ ...item, id: `${item.id}-${index}`, start_at: index > 2 ? ['14:30', '15:15', '16:00'][index - 3] : item.start_at }} key={`${item.id}-${index}`} />)}</div></div></section>; }
function ToothChart({ dentition, setDentition, selectedTooth, setSelectedTooth }) { const teeth = dentition === 'ADULT' ? teethAdult : teethChild; return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">CLINICAL RECORD</span><h2>Interactive tooth chart</h2></div><div className="segmented"><button className={dentition === 'ADULT' ? 'selected' : ''} onClick={() => setDentition('ADULT')}>Adult · 32</button><button className={dentition === 'CHILD' ? 'selected' : ''} onClick={() => setDentition('CHILD')}>Child · 20</button></div></div><div className="chart-layout"><div className="panel tooth-panel"><div className="chart-header"><div><strong>Nguyen Minh Anh</strong><span>DMS-0001 · {dentition === 'ADULT' ? 'Permanent dentition' : 'Primary dentition'}</span></div><span className="status confirmed">In treatment</span></div><div className="mouth-label">UPPER ARCH</div><div className={`teeth-grid ${dentition.toLowerCase()}`}>{teeth.slice(0, Math.ceil(teeth.length / 2)).map((tooth) => <Tooth key={tooth.id} tooth={tooth} selected={selectedTooth === tooth.id} onClick={() => setSelectedTooth(tooth.id)} />)}</div><div className="mouth-line" /><div className={`teeth-grid lower ${dentition.toLowerCase()}`}>{teeth.slice(Math.ceil(teeth.length / 2)).reverse().map((tooth) => <Tooth key={tooth.id} tooth={tooth} selected={selectedTooth === tooth.id} onClick={() => setSelectedTooth(tooth.id)} />)}</div><div className="mouth-label lower-label">LOWER ARCH</div><div className="chart-legend"><span><i className="dot healthy" />Healthy</span><span><i className="dot care" />Needs care</span><span><i className="dot monitor" />Monitor</span></div></div><aside className="panel tooth-detail"><span className="eyebrow">SELECTED TOOTH</span>{selectedTooth ? <><div className="tooth-number">{teeth.find((tooth) => tooth.id === selectedTooth)?.code}</div><h3>Clinical condition</h3><p>Update this tooth’s condition and add a treatment note for the patient record.</p><select defaultValue="Healthy"><option>Healthy</option><option>Needs care</option><option>Monitor</option><option>Restored</option></select><textarea placeholder="Add a clinical note..." /><button className="primary-button full">Save condition</button></> : <div className="empty-detail"><Stethoscope size={28} /><p>Select a tooth to inspect its clinical record.</p></div>}</aside></div></section>; }
function Tooth({ tooth, selected, onClick }) { return <button onClick={onClick} className={`tooth ${tooth.state.toLowerCase().replace(' ', '-')} ${selected ? 'selected' : ''}`}><span>{tooth.code.slice(1)}</span><div className="tooth-shape" /></button>; }
function Billing({ patients }) { return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">FINANCE</span><h2>Billing & installment plans</h2></div><button className="primary-button"><CircleDollarSign size={17} /> New invoice</button></div><div className="metric-grid compact"><Metric label="Outstanding" value="₫42.8m" detail="Across 18 invoices" accent="gold" icon={CircleDollarSign} /><Metric label="Due this week" value="₫8.4m" detail="6 installments" accent="coral" icon={CalendarDays} /><Metric label="Collected today" value="₫5.2m" detail="11 payments" accent="sage" icon={ShieldCheck} /></div><div className="panel table-panel"><table><thead><tr><th>Invoice</th><th>Patient</th><th>Total</th><th>Paid</th><th>Status</th></tr></thead><tbody>{patients.slice(0, 3).map((p, i) => <tr key={p.id}><td><code>INV-000{i + 1}</code></td><td><strong>{p.full_name}</strong></td><td>₫{['3,500,000', '1,200,000', '850,000'][i]}</td><td>₫{['1,500,000', '1,200,000', '350,000'][i]}</td><td><span className={`status ${i === 1 ? 'paid' : 'scheduled'}`}>{i === 1 ? 'Paid' : 'Installment'}</span></td></tr>)}</tbody></table></div></section>; }
function Radiographs() { return <section className="page-section"><div className="section-toolbar"><div><span className="eyebrow">IMAGING</span><h2>Radiograph gallery</h2></div><button className="primary-button"><FileImage size={17} /> Upload image</button></div><div className="upload-placeholder"><FileImage size={30} /><h3>No radiographs uploaded yet</h3><p>Attach X-ray images to a patient record from the clinical visit.</p><button className="secondary-button">Choose file</button></div></section>; }

createRoot(document.getElementById('root')).render(<App />);
