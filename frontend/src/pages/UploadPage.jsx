import { useRef, useState } from 'react';

const BrainIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"/>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"/>
  </svg>
);

const UploadIcon = () => (
  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/>
    <line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
);

const FileIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
    <line x1="16" y1="13" x2="8" y2="13"/>
    <line x1="16" y1="17" x2="8" y2="17"/>
    <polyline points="10 9 9 9 8 9"/>
  </svg>
);

const CheckIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const ArrowRight = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12"/>
    <polyline points="12 5 19 12 12 19"/>
  </svg>
);

const features = [
  { label: 'ATS Compatibility Score', desc: 'See exactly how automated systems score your resume' },
  { label: 'Semantic Match Analysis', desc: 'Deep AI understanding beyond keyword matching' },
  { label: 'Interview Probability', desc: 'Data-driven estimate of your interview chances' },
  { label: 'AI Resume Rewrite', desc: 'Auto-optimized version tailored to the job' },
];

const HistoryIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.5"/>
  </svg>
);

const TrashIcon = () => (
  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
  </svg>
);

function scoreColor(s) {
  return s >= 75 ? 'var(--green)' : s >= 50 ? 'var(--amber)' : 'var(--red)';
}

function formatDate(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  } catch { return ''; }
}

export default function UploadPage({ onSubmit, history = [], onRestoreHistory }) {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState('');
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  const handleFile = (f) => {
    if (f && f.type === 'application/pdf') setFile(f);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    handleFile(f);
  };

  const canSubmit = file && jd.trim().length > 50;

  return (
    <div className="page" style={{ background: 'var(--bg)', overflow: 'hidden' }}>
      {/* Ambient blobs */}
      <div style={{
        position: 'fixed', top: -200, left: -200,
        width: 600, height: 600,
        background: 'radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%)',
        pointerEvents: 'none', zIndex: 0,
      }} />
      <div style={{
        position: 'fixed', bottom: -200, right: -200,
        width: 700, height: 700,
        background: 'radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 70%)',
        pointerEvents: 'none', zIndex: 0,
      }} />

      <div style={{ position: 'relative', zIndex: 1, maxWidth: 1100, margin: '0 auto', padding: '0 24px' }}>
        {/* Nav */}
        <nav style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '24px 0', borderBottom: '1px solid var(--border)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: 'var(--grad)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 0 20px rgba(139,92,246,0.4)',
            }}>
              <BrainIcon />
            </div>
            <span style={{ fontWeight: 800, fontSize: 18, letterSpacing: '-0.3px' }}>HireMeMaybe</span>
          </div>
          <span className="badge badge-purple">AI-Powered</span>
        </nav>

        {/* Hero */}
        <div style={{ textAlign: 'center', padding: '64px 0 56px', animation: 'fadeUp 0.6s ease both' }}>
          <div className="badge badge-purple" style={{ marginBottom: 20, fontSize: 13 }}>
            ✦ Resume Intelligence Platform
          </div>
          <h1 style={{
            fontSize: 'clamp(36px,6vw,68px)', fontWeight: 900,
            lineHeight: 1.05, letterSpacing: '-2px', marginBottom: 20,
          }}>
            Land More Interviews<br />
            <span className="grad-text">With AI Precision</span>
          </h1>
          <p style={{
            fontSize: 18, color: 'var(--text-2)', maxWidth: 540,
            margin: '0 auto', lineHeight: 1.6,
          }}>
            Upload your resume and paste a job description. Our AI analyzes ATS compatibility,
            semantic match, and generates an optimized resume — in seconds.
          </p>
        </div>

        {/* Main form */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24,
          animation: 'fadeUp 0.6s 0.15s ease both', opacity: 0,
          animationFillMode: 'forwards',
        }}>
          {/* Left: Upload */}
          <div
            className="card"
            onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            onClick={() => !file && inputRef.current?.click()}
            style={{
              padding: 32, cursor: file ? 'default' : 'pointer',
              border: dragging
                ? '2px dashed var(--purple)'
                : file
                ? '1px solid rgba(16,185,129,0.4)'
                : '2px dashed var(--border)',
              background: dragging
                ? 'rgba(139,92,246,0.06)'
                : file
                ? 'rgba(16,185,129,0.04)'
                : 'var(--card)',
              transition: 'all 0.2s',
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              minHeight: 280, textAlign: 'center', gap: 16,
            }}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf"
              style={{ display: 'none' }}
              onChange={(e) => handleFile(e.target.files[0])}
            />
            {file ? (
              <>
                <div style={{
                  width: 72, height: 72, borderRadius: 16,
                  background: 'rgba(16,185,129,0.15)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--green)',
                }}>
                  <FileIcon />
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>{file.name}</div>
                  <div style={{ color: 'var(--text-3)', fontSize: 13 }}>
                    {(file.size / 1024).toFixed(0)} KB · PDF
                  </div>
                </div>
                <div className="badge badge-green" style={{ gap: 6 }}>
                  <CheckIcon /> Ready to analyze
                </div>
                <button className="btn-ghost" style={{ marginTop: 4 }} onClick={(e) => { e.stopPropagation(); setFile(null); inputRef.current?.click(); }}>
                  Replace file
                </button>
              </>
            ) : (
              <>
                <div style={{
                  width: 72, height: 72, borderRadius: 16,
                  background: dragging ? 'var(--purple-dim)' : 'rgba(255,255,255,0.05)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: dragging ? 'var(--purple)' : 'var(--text-3)',
                  transition: 'all 0.2s',
                  animation: dragging ? 'float 1s ease-in-out infinite' : 'none',
                }}>
                  <UploadIcon />
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 6 }}>
                    {dragging ? 'Drop it here!' : 'Upload your resume'}
                  </div>
                  <div style={{ color: 'var(--text-3)', fontSize: 14, lineHeight: 1.5 }}>
                    Drag & drop your PDF, or<br />click to browse your files
                  </div>
                </div>
                <div className="badge badge-purple">PDF only</div>
              </>
            )}
          </div>

          {/* Right: JD */}
          <div className="card" style={{ padding: 32, display: 'flex', flexDirection: 'column' }}>
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>Job Description</div>
              <div style={{ color: 'var(--text-3)', fontSize: 13 }}>
                Paste the full job posting — the more detail, the better the analysis.
              </div>
            </div>
            <textarea
              value={jd}
              onChange={(e) => setJd(e.target.value)}
              placeholder="Paste the job description here…&#10;&#10;e.g. We are looking for a Senior Software Engineer with experience in React, Node.js, and cloud platforms. You will be responsible for building scalable microservices…"
              style={{
                flex: 1, minHeight: 200,
                background: 'rgba(255,255,255,0.03)',
                border: `1px solid ${jd.length > 50 ? 'rgba(16,185,129,0.35)' : 'var(--border)'}`,
                borderRadius: 12, padding: '14px 16px',
                color: 'var(--text)', fontSize: 14, lineHeight: 1.6,
                resize: 'none', outline: 'none', fontFamily: 'inherit',
                transition: 'border-color 0.2s',
              }}
            />
            <div style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 10,
            }}>
              <span style={{ fontSize: 12, color: 'var(--text-3)' }}>
                {jd.length > 0 && (jd.length < 50 ? `${50 - jd.length} more characters needed` : `${jd.length} characters`)}
              </span>
              {jd.length > 50 && <span className="badge badge-green"><CheckIcon /> Good length</span>}
            </div>
          </div>
        </div>

        {/* CTA */}
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          padding: '40px 0 32px', gap: 16,
          animation: 'fadeUp 0.6s 0.3s ease both', opacity: 0, animationFillMode: 'forwards',
        }}>
          <button
            className="btn-primary"
            disabled={!canSubmit}
            onClick={() => onSubmit({ file, jd })}
            style={{ fontSize: 16, padding: '16px 40px', borderRadius: 14 }}
          >
            Analyze My Resume <ArrowRight />
          </button>
          {!canSubmit && (
            <p style={{ fontSize: 13, color: 'var(--text-3)' }}>
              {!file ? 'Upload a PDF resume to continue' : 'Paste a job description (50+ chars) to continue'}
            </p>
          )}
        </div>

        {/* Features row */}
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16,
          padding: '0 0 40px',
          animation: 'fadeUp 0.6s 0.45s ease both', opacity: 0, animationFillMode: 'forwards',
        }}>
          {features.map((f, i) => (
            <div key={i} className="card" style={{ padding: '20px 18px' }}>
              <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 6, color: 'var(--text)' }}>{f.label}</div>
              <div style={{ fontSize: 13, color: 'var(--text-3)', lineHeight: 1.5 }}>{f.desc}</div>
            </div>
          ))}
        </div>

        {/* Analysis History */}
        {history.length > 0 && (
          <div style={{
            paddingBottom: 64,
            animation: 'fadeUp 0.6s 0.55s ease both', opacity: 0, animationFillMode: 'forwards',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
              <div style={{ color: 'var(--purple)', display: 'flex' }}><HistoryIcon /></div>
              <span style={{ fontWeight: 700, fontSize: 15 }}>Recent Analyses</span>
              <span style={{ fontSize: 12, color: 'var(--text-3)', marginLeft: 4 }}>
                {history.length} saved
              </span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {history.slice(0, 5).map((entry) => (
                <div
                  key={entry.id}
                  className="card"
                  style={{
                    padding: '16px 20px',
                    display: 'flex', alignItems: 'center', gap: 20,
                    cursor: 'pointer', transition: 'border-color 0.2s',
                  }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(139,92,246,0.4)'}
                  onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
                  onClick={() => onRestoreHistory(entry)}
                >
                  {/* Role + date */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {entry.jobTitle}
                      {entry.company && <span style={{ fontWeight: 400, color: 'var(--text-3)' }}> · {entry.company}</span>}
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-3)' }}>{formatDate(entry.savedAt)}</div>
                  </div>

                  {/* Score pills */}
                  <div style={{ display: 'flex', gap: 12, flexShrink: 0 }}>
                    {[
                      { label: 'ATS',       val: entry.atsScore },
                      { label: 'Interview', val: entry.interviewScore },
                      { label: 'Skills',    val: entry.skillScore },
                    ].map(({ label, val }) => (
                      <div key={label} style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 16, fontWeight: 800, color: scoreColor(val) }}>{val}</div>
                        <div style={{ fontSize: 11, color: 'var(--text-3)' }}>{label}</div>
                      </div>
                    ))}
                  </div>

                  {/* CTA */}
                  <div style={{
                    fontSize: 12, color: 'var(--purple)', fontWeight: 600,
                    flexShrink: 0, display: 'flex', alignItems: 'center', gap: 4,
                  }}>
                    View →
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
