/**
 * api.js — Unnati Career Portal Frontend API Helper
 * All fetch calls to the FastAPI backend go through here.
 * Change BASE_URL if your backend runs on a different port/host.
 */

const BASE_URL = '';

/* ── Token helpers ─────────────────────────────────── */
function getToken()  { return sessionStorage.getItem('placeit_token'); }
function setToken(t) { sessionStorage.setItem('placeit_token', t); }
function clearToken(){ sessionStorage.removeItem('placeit_token'); sessionStorage.removeItem('placeit_session'); }

function getSession()  { try { return JSON.parse(sessionStorage.getItem('placeit_session')); } catch { return null; } }
function setSession(d) { sessionStorage.setItem('placeit_session', JSON.stringify(d)); }

/* ── Core fetch wrapper ────────────────────────────── */
async function api(method, path, body = null, isForm = false) {
  const token = getToken();
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (body && !isForm) headers['Content-Type'] = 'application/json';

  const opts = { method, headers };
  if (body) opts.body = isForm ? body : JSON.stringify(body);

  const res = await fetch(BASE_URL + path, opts);
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const msg = data.detail || `Error ${res.status}`;
    throw new Error(Array.isArray(msg) ? msg.map(e => e.msg).join(', ') : msg);
  }
  return data;
}

/* ── AUTH ─────────────────────────────────────────── */
const Auth = {
  studentLogin: (roll_no, dob)  => api('POST', '/api/auth/student/login', { roll_no, dob }),
  adminLogin:   (email, password) => api('POST', '/api/auth/admin/login', { email, password }),
  register:     (data)           => api('POST', '/api/auth/student/register', data),
};

/* ── STUDENTS ─────────────────────────────────────── */
const Students = {
  me:           ()     => api('GET',  '/api/students/me'),
  updateMe:     (data) => api('PUT',  '/api/students/me', data),
  uploadResume: (file) => {
    const fd = new FormData();
    fd.append('file', file);
    return api('POST', '/api/students/me/resume', fd, true);
  },
  uploadPhoto: (file) => {
    const fd = new FormData();
    fd.append('file', file);
    return api('POST', '/api/students/me/photo', fd, true);
  },
  list:    (params = {}) => api('GET', '/api/students/?' + new URLSearchParams(params)),
  getById: (id)          => api('GET', `/api/students/${id}`),
  delete:  (id)          => api('DELETE', `/api/students/${id}`),
};

/* ── COMPANIES ────────────────────────────────────── */
const Companies = {
  list:   (sector = '') => api('GET', '/api/companies/' + (sector ? `?sector=${sector}` : '')),
  create: (data)        => api('POST',   '/api/companies/', data),
  update: (id, data)    => api('PUT',    `/api/companies/${id}`, data),
  delete: (id)          => api('DELETE', `/api/companies/${id}`),
};

/* ── JOBS ─────────────────────────────────────────── */
const Jobs = {
  list:    (params = {}) => api('GET', '/api/jobs/?' + new URLSearchParams(params)),
  listAll: ()            => api('GET', '/api/jobs/all'),
  create:  (data)        => api('POST',   '/api/jobs/', data),
  update:  (id, data)    => api('PUT',    `/api/jobs/${id}`, data),
  delete:  (id)          => api('DELETE', `/api/jobs/${id}`),
};

/* ── APPLICATIONS ─────────────────────────────────── */
const Applications = {
  apply:        (job_id)        => api('POST',  '/api/applications/', { job_id }),
  myApps:       ()              => api('GET',   '/api/applications/my'),
  all:          (params = {})   => api('GET',   '/api/applications/?' + new URLSearchParams(params)),
  updateStatus: (id, status)    => api('PATCH', `/api/applications/${id}/status`, { status }),
  delete:       (id)            => api('DELETE', `/api/applications/${id}`),
};

/* ── NOTIFICATIONS ────────────────────────────────── */
const Notifications = {
  myNotifs:    ()  => api('GET',  '/api/notifications/my'),
  readAll:     ()  => api('POST', '/api/notifications/my/read-all'),
  adminNotifs: ()  => api('GET',  '/api/notifications/admin'),
};

/* ── STATS ────────────────────────────────────────── */
const Stats = {
  overview:       () => api('GET', '/api/stats/overview'),
  placedStudents: () => api('GET', '/api/stats/placed-students'),
  alumni:         () => api('GET', '/api/stats/alumni'),
  addAlumni:      (data) => api('POST', '/api/stats/alumni', data),
  deleteAlumni:   (id)   => api('DELETE', `/api/stats/alumni/${id}`),
  predict:        ()     => api('GET', '/api/stats/predict'),
};

/* ── SCHOLARSHIPS ─────────────────────────────────── */
const Scholarships = {
  list:   ()     => api('GET',  '/api/scholarships'),
  create: (data) => api('POST', '/api/scholarships', data),
  delete: (id)   => api('DELETE', `/api/scholarships/${id}`),
};

/* ── ADMIN ────────────────────────────────────────── */
const Admin = {
  dashboard:      ()     => api('GET', '/api/admin/dashboard'),
  interviewForms: ()     => api('GET', '/api/admin/interview-forms'),
  addForm:        (data) => api('POST', '/api/admin/interview-forms', data),
  deleteForm:     (id)   => api('DELETE', `/api/admin/interview-forms/${id}`),
  broadcast:      (data) => api('POST', '/api/admin/broadcast', data),
  downloadReport: async (formId, jobTitle = 'report') => {
    const token = getToken();
    const res = await fetch(`/api/admin/interview-forms/${formId}/report`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });
    if (!res.ok) { const d = await res.json().catch(()=>({})); throw new Error(d.detail || 'Failed to download report'); }
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `Applicants_${jobTitle.replace(/\s+/g,'_')}.xlsx`;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },
  downloadApplicantsReport: async (params = {}) => {
    const token = getToken();
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`/api/admin/applicants/report?${query}`, {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });
    if (!res.ok) { const d = await res.json().catch(()=>({})); throw new Error(d.detail || 'Failed to download report'); }
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = `Applicants_Report_${today().replace(/-/g,'')}.xlsx`;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },
};

/* ── INSIGHTS & EXTERNAL ─────────────────────────────── */
const External = {
  getNews: (course) => api('GET', `/api/external/news?course=${course}`),
};

/* ── UTILS ────────────────────────────────────────── */
function statusBadge(s) {
  const m = { Applied:'badge-gray', Shortlisted:'badge-blue', Selected:'badge-green', Rejected:'badge-red' };
  return `<span class="badge ${m[s]||'badge-gray'}">${s}</span>`;
}
function today() { return new Date().toISOString().split('T')[0]; }
function initials(name) { return (name||'?').split(' ').map(w=>w[0]).join('').toUpperCase().slice(0,2); }

function stars(rating=4.0) {
  let h = '';
  for(let i=1; i<=5; i++) h += `<span style="color:${i<=Math.round(rating)?'var(--orange-yellow-crayola)':'var(--light-gray70)'};margin-right:1px;">★</span>`;
  return h;
}

function getScholarshipMatch(student, sch) {
  if (!student || !sch) return { score: 0, reasons: [] };
  let score = 50;
  const reasons = [];
  const elig = (sch.eligibility || '').toLowerCase();
  const course = (student.course || '').toLowerCase();
  
  if (elig.includes(course) || elig.includes('all courses') || elig.includes('any')) {
    score += 30;
    reasons.push(`Matches ${student.course}`);
  }
  
  const cgpaMatch = elig.match(/([0-9]\.[0-9]+|[0-9])\s*(cgpa|\+|plus|above)/);
  if (cgpaMatch) {
    const minCgpa = parseFloat(cgpaMatch[1]);
    if (student.cgpa >= minCgpa) {
      score += 20;
      reasons.push(`CGPA ${student.cgpa} meets requirement`);
    } else {
      score -= 40;
      reasons.push(`CGPA ${student.cgpa} below target`);
    }
  }
  return { score, reasons };
}

function getSkillMatch(studentSkills, jobSkills) {
  if (!jobSkills) return { score: 100, gaps: [] };
  const s = (studentSkills||'').toLowerCase().split(',').map(x=>x.trim()).filter(x=>x);
  const j = (jobSkills||'').toLowerCase().split(',').map(x=>x.trim()).filter(x=>x);
  if (j.length === 0) return { score: 100, gaps: [] };
  const gaps = j.filter(need => !s.some(have => have.includes(need) || need.includes(have)));
  const score = Math.round(((j.length - gaps.length) / j.length) * 100);
  return { score, gaps };
}

function toast(msg, type='info') {
  let c = document.getElementById('toastContainer');
  if (!c) { c = document.createElement('div'); c.id='toastContainer'; c.className='toast-container'; document.body.appendChild(c); }
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span>${{success:'✅',error:'❌',info:'ℹ️'}[type]||'📢'}</span><span>${msg}</span>`;
  c.appendChild(t);
  setTimeout(() => { t.style.animation='toastout .3s ease forwards'; setTimeout(()=>t.remove(),300); }, 3200);
}

function showE(id)  { const e=document.getElementById(id); if(e) e.classList.add('show'); }
function hideE(id)  { const e=document.getElementById(id); if(e) e.classList.remove('show'); }
function showGE(id, msg) { const e=document.getElementById(id); if(e){e.textContent=msg; e.classList.add('show');} }
function hideGE(id) { const e=document.getElementById(id); if(e) e.classList.remove('show'); }

/* ── Loading spinner helper ── */
function showLoading(id, msg='Loading...') {
  const el = document.getElementById(id);
  if(el) el.innerHTML = `<div style="text-align:center;padding:40px;color:var(--light-gray70);font-size:var(--fs7);">⏳ ${msg}</div>`;
}
