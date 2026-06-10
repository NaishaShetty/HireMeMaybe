/**
 * HistoryPage — full-screen dashboard of past analyses stored in localStorage.
 *
 * Each card shows: job title, company, ATS score, interview probability,
 * semantic score, skill match, date. Click to restore that analysis.
 * Trash icon to delete individual entries.
 */

const HISTORY_KEY = 'hmm_analysis_history';

function loadHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); }
  catch { return []; }
}

function deleteEntry(id) {
  const history = loadHistory().filter(e => e.id !== id);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}

function clearHistory() {
  localStorage.removeItem(HISTORY_KEY);
}

// ── Icons ───────────────────────────────────────────────────────────────────

const BackIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
  </svg>
);

const TrashIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
    <path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
  </svg>
);

const HistoryIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.5"/>
  </svg>
);

const BriefcaseIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
  </svg>
);

// ── Helpers ──────────────────────────────────────────────────────────────────

function scoreColor(s) {
  return s >= 75 ? 'var(--green)' : s >= 50 ? 'var(--amber)' : 'var(--red)';
}

function scoreBg(s) {
  return s >= 75 ? 'var(--green-dim)' : s >= 50 ? 'var(--amber-dim)' : 'var(--red-dim)';
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
  } catch { return ''; }
}

function ScorePill({ label, value, suffix = '' }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3,
      padding: '10px 14px', borderRadius: 10,
      background: scoreBg(value),
      minWidth: 72,
    }}>
      <span style={{ fontSize: 18, fontWeight: 800, color: scoreColor(value), lineHeight: 1 }}>
        {Math.round(value)}{suffix}
      </span>
      <span style={{ fontSize: 10, fontWeight: 600, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        {label}
      </span>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

import { useState } from 'react';

export default function HistoryPage({ onBack, onRestoreEntry }) {
  const [entries, setEntries] = useState(loadHistory);
  const [confirmClear, setConfirmClear] = useState(false);

  const handleDelete = (id) => {
    deleteEntry(id);
    setEntries(loadHistory());
  };

  const handleClearAll = () => {
    clearHistory();
    setEntries([]);
    setConfirmClear(false);
  };

  return (
    <div className="page" style={{ background: 'var(--bg)', padding: '0 0 80px' }}>
      {/* Ambient */}
      <div style={{ position:'fixed', top:-200, left:-200, width:600, height:600,
        background:'radial-gradient(circle, rgba(139,92,246,0.06) 0%, transparent 70%)', pointerEvents:'none', zIndex:0 }} />

      <div style={{ position:'relative', zIndex:1, maxWidth: 960, margin:'0 auto', padding:'0 24px' }}>

        {/* Header */}
        <div style={{
          display:'flex', alignItems:'center', justifyContent:'space-between',
          padding:'24px 0', borderBottom:'1px solid var(--border)', marginBottom:36,
        }}>
          <button className="btn-ghost" onClick={onBack}><BackIcon /> Back</button>

          <div style={{ display:'flex', alignItems:'center', gap:10 }}>
            <div style={{
              width:36, height:36, borderRadius:10, background:'var(--purple-dim)',
              display:'flex', alignItems:'center', justifyContent:'center', color:'var(--purple)',
            }}>
              <HistoryIcon />
            </div>
            <div>
              <h2 style={{ fontSize:18, fontWeight:800, letterSpacing:'-0.4px' }}>Analysis History</h2>
              <p style={{ fontSize:12, color:'var(--text-3)', marginTop:1 }}>{entries.length} saved {entries.length === 1 ? 'analysis' : 'analyses'}</p>
            </div>
          </div>

          {entries.length > 0 && (
            <div style={{ display:'flex', gap:8 }}>
              {confirmClear ? (
                <>
                  <span style={{ fontSize:13, color:'var(--text-2)', alignSelf:'center' }}>Delete all?</span>
                  <button className="btn-ghost" onClick={() => setConfirmClear(false)} style={{ color:'var(--text-2)', padding:'6px 12px', fontSize:12 }}>Cancel</button>
                  <button
                    onClick={handleClearAll}
                    style={{ padding:'6px 12px', borderRadius:8, border:'1px solid rgba(239,68,68,0.4)',
                      background:'var(--red-dim)', color:'var(--red)', fontSize:12, fontWeight:600, cursor:'pointer' }}
                  >
                    Yes, clear all
                  </button>
                </>
              ) : (
                <button className="btn-ghost" onClick={() => setConfirmClear(true)} style={{ fontSize:12, color:'var(--text-3)' }}>
                  Clear all
                </button>
              )}
            </div>
          )}
        </div>

        {/* Empty state */}
        {entries.length === 0 && (
          <div style={{ textAlign:'center', padding:'80px 0', color:'var(--text-3)' }}>
            <div style={{
              width:72, height:72, borderRadius:20, background:'var(--card)',
              display:'inline-flex', alignItems:'center', justifyContent:'center',
              marginBottom:20, color:'var(--text-3)',
            }}>
              <HistoryIcon />
            </div>
            <p style={{ fontSize:18, fontWeight:700, color:'var(--text-2)', marginBottom:8 }}>No analyses yet</p>
            <p style={{ fontSize:14 }}>Upload a resume and job description to get started.</p>
            <button className="btn-primary" onClick={onBack} style={{ marginTop:24 }}>
              Start New Analysis
            </button>
          </div>
        )}

        {/* Cards grid */}
        {entries.length > 0 && (
          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(420px, 1fr))', gap:16 }}>
            {entries.map((entry, i) => (
              <div
                key={entry.id}
                className="card"
                style={{
                  padding:24, cursor:'pointer', transition:'all 0.2s',
                  animation:`fadeUp 0.4s ${i * 0.05}s ease both`, opacity:0, animationFillMode:'forwards',
                  position:'relative',
                }}
                onClick={() => onRestoreEntry(entry)}
                onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(139,92,246,0.3)'}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
              >
                {/* Delete button */}
                <button
                  onClick={e => { e.stopPropagation(); handleDelete(entry.id); }}
                  style={{
                    position:'absolute', top:12, right:12,
                    background:'none', border:'none', color:'var(--text-3)',
                    cursor:'pointer', padding:6, borderRadius:6, transition:'color 0.2s',
                  }}
                  onMouseEnter={e => e.currentTarget.style.color = 'var(--red)'}
                  onMouseLeave={e => e.currentTarget.style.color = 'var(--text-3)'}
                  title="Delete this entry"
                >
                  <TrashIcon />
                </button>

                {/* Job info */}
                <div style={{ display:'flex', alignItems:'flex-start', gap:12, marginBottom:16, paddingRight:24 }}>
                  <div style={{
                    width:40, height:40, borderRadius:10, background:'var(--purple-dim)',
                    display:'flex', alignItems:'center', justifyContent:'center',
                    color:'var(--purple)', flexShrink:0,
                  }}>
                    <BriefcaseIcon />
                  </div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontWeight:700, fontSize:15, lineHeight:1.3, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                      {entry.jobTitle || 'Unknown Role'}
                    </div>
                    {entry.company && (
                      <div style={{ fontSize:13, color:'var(--text-3)', marginTop:2 }}>{entry.company}</div>
                    )}
                    <div style={{ fontSize:11, color:'var(--text-3)', marginTop:4 }}>{formatDate(entry.savedAt)}</div>
                  </div>
                </div>

                {/* Scores */}
                <div style={{ display:'flex', gap:8, flexWrap:'wrap' }}>
                  <ScorePill label="ATS" value={entry.atsScore ?? 0} />
                  <ScorePill label="Interview" value={entry.interviewScore ?? 0} suffix="%" />
                  <ScorePill label="Semantic" value={entry.semanticScore ?? 0} suffix="%" />
                  <ScorePill label="Skills" value={entry.skillScore ?? 0} suffix="%" />
                </div>

                {/* Restore hint */}
                <div style={{
                  marginTop:14, fontSize:12, color:'var(--text-3)',
                  display:'flex', alignItems:'center', gap:4,
                }}>
                  <span>Click to restore this analysis</span>
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
                  </svg>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
