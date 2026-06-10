const BASE = 'http://localhost:8000';

export async function parseResume(file) {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${BASE}/parse-resume`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function parseJD(text) {
  const res = await fetch(`${BASE}/parse-jd`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getInterviewScore({ resume, jd, resume_text, jd_text }) {
  const res = await fetch(`${BASE}/interview-score`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume, jd, resume_text, jd_text }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function rewriteResume({ resume, jd, resume_text, jd_text, max_passes = 2, num_candidates = 3 }) {
  const res = await fetch(`${BASE}/rewrite-resume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume, jd, resume_text, jd_text, max_passes, num_candidates }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getInterviewPrep({ resume_text, jd_text, matched_skills = [], missing_skills = [] }) {
  const res = await fetch(`${BASE}/interview-prep`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_text, jd_text, matched_skills, missing_skills }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getCompanyIntel({ company, role = 'Software Engineer' }) {
  const res = await fetch(`${BASE}/company-intel`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ company, role }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function generateCoverLetter({ resume_text, jd_text, role, company }) {
  const res = await fetch(`${BASE}/generate-cover-letter`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_text, jd_text, role, company }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function exportCoverLetterPdf({ cover_letter, company = '' }) {
  const res = await fetch(`${BASE}/export-cover-letter-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cover_letter, company }),
  });
  if (!res.ok) throw new Error(await res.text());
  const blob = await res.blob();
  const safe = company.replace(/[^a-zA-Z0-9 _-]/g, '').trim().replace(/\s+/g, '_');
  const filename = safe ? `Cover_Letter_${safe}.pdf` : 'Cover_Letter.pdf';
  return { blob, filename };
}

export async function exportResume({ resume_text, format }) {
  const res = await fetch(`${BASE}/export-resume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_text, format }),
  });
  if (!res.ok) throw new Error(await res.text());
  const blob = await res.blob();
  const disposition = res.headers.get('Content-Disposition') || '';
  const match = disposition.match(/filename="([^"]+)"/);
  const filename = match ? match[1] : `optimized_resume.${format}`;
  return { blob, filename };
}
