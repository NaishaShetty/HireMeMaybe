/**
 * CoverLetterPage — displays and allows editing/exporting the generated cover letter.
 *
 * Props:
 *   data         { cover_letter, role, company, word_count }
 *   jdData       parsed JD (for role/company display)
 *   onBack       fn
 *   onNewAnalysis fn
 */

import { useState } from 'react';
import { exportCoverLetterPdf } from '../api.js';

// ── Icons ────────────────────────────────────────────────────────────────────

const BackIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
  </svg>
);

const CopyIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
  </svg>
);

const CheckIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const DownloadIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
  </svg>
);

const PenIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
  </svg>
);

// ── Helpers ──────────────────────────────────────────────────────────────────

function downloadTxt(text, filename) {
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function CoverLetterPage({ data, jdData, onBack, onNewAnalysis }) {
  const {
    cover_letter = '',
    role         = jdData?.job_title || 'the role',
    company      = jdData?.company   || 'the company',
    word_count   = 0,
  } = data;

  const [copied,      setCopied]      = useState(false);
  const [editing,     setEditing]     = useState(false);
  const [text,        setText]        = useState(cover_letter);
  const [downloading, setDownloading] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const handleDownloadPdf = async () => {
    if (downloading) return;
    setDownloading(true);
    try {
      const { blob, filename } = await exportCoverLetterPdf({ cover_letter: text, company });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = filename; a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(`PDF export failed: ${err.message}`);
    } finally {
      setDownloading(false);
    }
  };

  const handleDownloadTxt = () => {
    const filename = `Cover_Letter_${company.replace(/\s+/g, '_') || 'draft'}.txt`;
    downloadTxt(text, filename);
  };

  const displayWordCount = text.trim().split(/\s+/).filter(Boolean).length;

  return (
    <div className="page" style={{ background:'var(--bg)', padding:'0 0 80px' }}>
      {/* Ambient */}
      <div style={{ position:'fixed', top:-200, right:-200, width:600, height:600,
        background:'radial-gradient(circle, rgba(59,130,246,0.07) 0%, transparent 70%)', pointerEvents:'none', zIndex:0 }} />

      <div style={{ position:'relative', zIndex:1, maxWidth:860, margin:'0 auto', padding:'0 24px' }}>

        {/* Header */}
        <div style={{
          display:'flex', alignItems:'center', justifyContent:'space-between',
          padding:'24px 0', borderBottom:'1px solid var(--border)', marginBottom:32,
        }}>
          <button className="btn-ghost" onClick={onBack}><BackIcon /> Back to Analysis</button>
          <div style={{ textAlign:'center' }}>
            <h2 style={{ fontSize:20, fontWeight:800, letterSpacing:'-0.5px' }}>Cover Letter</h2>
            <p style={{ color:'var(--text-3)', fontSize:13, marginTop:2 }}>
              {role}{company !== 'the company' ? ` · ${company}` : ''}
            </p>
          </div>
          <div style={{ display:'flex', gap:8 }}>
            <span style={{
              padding:'4px 10px', borderRadius:20, fontSize:12, fontWeight:600,
              background:'var(--blue-dim)', color:'var(--blue)',
            }}>
              {displayWordCount} words
            </span>
          </div>
        </div>

        {/* Letter card */}
        <div
          className="card"
          style={{
            padding:0, overflow:'hidden',
            border:'1px solid rgba(59,130,246,0.2)',
            animation:'fadeUp 0.4s ease both',
          }}
        >
          {/* Toolbar */}
          <div style={{
            display:'flex', alignItems:'center', justifyContent:'space-between',
            padding:'14px 20px', borderBottom:'1px solid rgba(59,130,246,0.15)',
            background:'rgba(59,130,246,0.03)',
          }}>
            <span style={{ fontSize:14, fontWeight:600 }}>
              {editing ? 'Editing — changes apply to copy & download' : 'AI-generated cover letter'}
            </span>
            <div style={{ display:'flex', gap:8 }}>
              <button
                className="btn-ghost"
                style={{ padding:'6px 12px', fontSize:12, color: editing ? 'var(--green)' : 'inherit' }}
                onClick={() => setEditing(e => !e)}
              >
                {editing ? <><CheckIcon /> Done</> : <><PenIcon /> Edit</>}
              </button>
              <button className="btn-ghost" style={{ padding:'6px 12px', fontSize:12 }} onClick={handleCopy}>
                {copied ? <><CheckIcon /> Copied!</> : <><CopyIcon /> Copy</>}
              </button>
              <button
                className="btn-ghost"
                style={{ padding:'6px 12px', fontSize:12, opacity: downloading ? 0.6 : 1 }}
                onClick={handleDownloadPdf}
                disabled={downloading}
              >
                <DownloadIcon /> {downloading ? 'Generating…' : 'PDF'}
              </button>
              <button className="btn-ghost" style={{ padding:'6px 12px', fontSize:12 }} onClick={handleDownloadTxt}>
                <DownloadIcon /> .txt
              </button>
            </div>
          </div>

          {/* Content */}
          {editing ? (
            <textarea
              value={text}
              onChange={e => setText(e.target.value)}
              style={{
                width:'100%', minHeight:520, padding:'28px 32px',
                background:'transparent', border:'none', outline:'none', resize:'vertical',
                fontSize:14.5, lineHeight:1.8, color:'var(--text)',
                fontFamily:"'Inter', system-ui, sans-serif",
              }}
            />
          ) : (
            <div style={{
              padding:'28px 32px', whiteSpace:'pre-wrap', lineHeight:1.8,
              fontSize:14.5, color:'var(--text-2)', fontFamily:"'Inter', system-ui, sans-serif",
            }}>
              {text}
            </div>
          )}
        </div>

        {/* Tips */}
        <div className="card" style={{
          padding:20, marginTop:20,
          animation:'fadeUp 0.4s 0.15s ease both', opacity:0, animationFillMode:'forwards',
        }}>
          <div style={{ fontSize:13, fontWeight:700, color:'var(--text-2)', marginBottom:10 }}>Before you send</div>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8 }}>
            {[
              'Replace [Candidate Name] with your actual name',
              'Add a specific hiring manager name if you know it',
              'Verify all company/role details are accurate',
              'Read aloud to check for natural flow',
            ].map(tip => (
              <div key={tip} style={{
                display:'flex', gap:8, alignItems:'flex-start',
                padding:'8px 12px', borderRadius:8,
                background:'var(--amber-dim)', border:'1px solid rgba(245,158,11,0.15)',
              }}>
                <span style={{ color:'var(--amber)', flexShrink:0 }}>→</span>
                <span style={{ fontSize:12.5, color:'var(--text-2)', lineHeight:1.5 }}>{tip}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom CTA */}
        <div style={{
          textAlign:'center', marginTop:32,
          animation:'fadeUp 0.4s 0.25s ease both', opacity:0, animationFillMode:'forwards',
        }}>
          <button className="btn-primary" onClick={onNewAnalysis} style={{ fontSize:15, padding:'13px 32px' }}>
            Analyze Another Resume
          </button>
        </div>
      </div>
    </div>
  );
}
