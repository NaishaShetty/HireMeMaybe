import { useState } from 'react';
import ScoreRing from '../components/ScoreRing.jsx';
import { exportResume } from '../api.js';

const CopyIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
  </svg>
);

const DownloadIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
  </svg>
);

const CheckIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const BackIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
  </svg>
);

const TrendUpIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>
  </svg>
);

const StarIcon = () => (
  <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" stroke="none">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
  </svg>
);

function ImprovementBadge({ before, after, label }) {
  const diff = after - before;
  const pct = before > 0 ? ((diff / before) * 100).toFixed(0) : 0;
  const improved = diff > 0;
  return (
    <div style={{
      display:'flex', flexDirection:'column', alignItems:'center', gap:8,
      padding:'20px 24px', borderRadius:16,
      background: improved ? 'rgba(16,185,129,0.08)' : 'rgba(239,68,68,0.08)',
      border:`1px solid ${improved ? 'rgba(16,185,129,0.25)' : 'rgba(239,68,68,0.25)'}`,
    }}>
      <span style={{ fontSize:12, fontWeight:600, color:'var(--text-3)', textTransform:'uppercase', letterSpacing:'0.06em' }}>{label}</span>
      <div style={{ display:'flex', alignItems:'center', gap:12 }}>
        <span style={{ fontSize:28, fontWeight:800, color:'var(--text-3)' }}>{Math.round(before)}</span>
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:2 }}>
          <div style={{ display:'flex', gap:4, color: improved ? 'var(--green)' : 'var(--red)' }}>
            {improved ? '→' : '↘'}
          </div>
          <span style={{ fontSize:11, fontWeight:700, color: improved ? 'var(--green)' : 'var(--red)' }}>
            {improved ? `+${pct}%` : `${pct}%`}
          </span>
        </div>
        <span style={{ fontSize:28, fontWeight:800, color: improved ? 'var(--green)' : 'var(--red)' }}>{Math.round(after)}</span>
      </div>
    </div>
  );
}

export default function RewritePage({ data, originalText, onBack, onNewAnalysis }) {
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState('optimized');
  const [downloading, setDownloading] = useState(null); // 'pdf' | 'docx' | null

  const {
    before_score = 0,
    after_score = 0,
    improvement = 0,
    accepted = false,
    optimized_resume = '',
    changes = [],
    analysis = {},
    recommendations = {},
  } = data;

  const improved = improvement > 0;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(optimized_resume).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  const downloadFormatted = async (format) => {
    if (downloading) return;
    setDownloading(format);
    try {
      const { blob, filename } = await exportResume({ resume_text: optimized_resume, format });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Export failed: ${err.message}`);
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div className="page" style={{ background:'var(--bg)', padding:'0 0 80px' }}>
      {/* Ambient */}
      <div style={{ position:'fixed', top:-200, right:-200, width:600, height:600,
        background:'radial-gradient(circle, rgba(16,185,129,0.08) 0%, transparent 70%)', pointerEvents:'none', zIndex:0 }} />

      <div style={{ position:'relative', zIndex:1, maxWidth:1100, margin:'0 auto', padding:'0 24px' }}>
        {/* Header */}
        <div style={{
          display:'flex', alignItems:'center', justifyContent:'space-between',
          padding:'24px 0', borderBottom:'1px solid var(--border)', marginBottom:36,
        }}>
          <button className="btn-ghost" onClick={onBack}><BackIcon /> Back to Analysis</button>
          <div style={{ textAlign:'center' }}>
            <h2 style={{ fontSize:20, fontWeight:800, letterSpacing:'-0.5px' }}>Optimized Resume</h2>
            <p style={{ color:'var(--text-3)', fontSize:13, marginTop:2 }}>AI-powered rewrite · Anti-hallucination safeguards active</p>
          </div>
          <div className={`badge ${accepted ? 'badge-green' : 'badge-amber'}`}>
            {accepted ? '✓ Score Improved' : '~ Minimal Change'}
          </div>
        </div>

        {/* Score improvement banner */}
        <div className="card" style={{
          padding:28, marginBottom:28,
          background: improved ? 'rgba(16,185,129,0.04)' : 'var(--card)',
          border: improved ? '1px solid rgba(16,185,129,0.2)' : '1px solid var(--border)',
          animation:'fadeUp 0.5s ease both',
        }}>
          <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', flexWrap:'wrap', gap:20 }}>
            {/* Left: celebration text */}
            <div>
              {improved ? (
                <>
                  <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:6 }}>
                    <TrendUpIcon style={{ color:'var(--green)' }} />
                    <span style={{ fontSize:22, fontWeight:800, color:'var(--green)' }}>
                      ATS Score improved by {Math.round(improvement)} points!
                    </span>
                  </div>
                  <p style={{ color:'var(--text-2)', fontSize:14 }}>
                    Your resume is now significantly more likely to pass ATS screening for this role.
                  </p>
                </>
              ) : (
                <>
                  <div style={{ fontSize:20, fontWeight:700, marginBottom:6 }}>Resume rewritten</div>
                  <p style={{ color:'var(--text-2)', fontSize:14 }}>
                    The AI has optimized your resume. ATS improvements may vary by system.
                  </p>
                </>
              )}
            </div>
            {/* Right: score comparison */}
            <div style={{ display:'flex', gap:16, flexWrap:'wrap' }}>
              <ImprovementBadge before={before_score} after={after_score} label="ATS Score" />
              {analysis.ats_score && analysis.skill_match_score && (
                <div style={{
                  display:'flex', flexDirection:'column', alignItems:'center', gap:8, padding:'20px 24px',
                  borderRadius:16, background:'var(--purple-dim)', border:'1px solid rgba(139,92,246,0.2)',
                }}>
                  <span style={{ fontSize:12, fontWeight:600, color:'var(--text-3)', textTransform:'uppercase', letterSpacing:'0.06em' }}>Skill Match</span>
                  <div style={{ display:'flex', alignItems:'center', gap:6 }}>
                    <StarIcon style={{ color:'var(--purple)' }} />
                    <span style={{ fontSize:26, fontWeight:800, color:'var(--purple)' }}>{Math.round(analysis.skill_match_score)}%</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main content: tabs + resume */}
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:24, marginBottom:24,
          animation:'fadeUp 0.5s 0.1s ease both', opacity:0, animationFillMode:'forwards' }}>

          {/* Original */}
          <div className="card" style={{ padding:0, display:'flex', flexDirection:'column', overflow:'hidden' }}>
            <div style={{
              padding:'16px 20px', borderBottom:'1px solid var(--border)',
              display:'flex', alignItems:'center', justifyContent:'space-between',
            }}>
              <div>
                <span style={{ fontWeight:700, fontSize:14 }}>Original Resume</span>
                <span className="badge badge-amber" style={{ marginLeft:10, fontSize:11 }}>Before</span>
              </div>
              <span style={{ fontSize:12, color:'var(--text-3)' }}>ATS: {Math.round(before_score)}</span>
            </div>
            <pre style={{
              padding:'20px', flex:1, overflow:'auto', maxHeight:520,
              fontSize:12.5, lineHeight:1.7, color:'var(--text-2)',
              fontFamily:"'JetBrains Mono', 'Consolas', monospace",
              whiteSpace:'pre-wrap', wordBreak:'break-word', margin:0,
            }}>
              {originalText || '(Original resume text not available)'}
            </pre>
          </div>

          {/* Optimized */}
          <div className="card" style={{ padding:0, display:'flex', flexDirection:'column', overflow:'hidden',
            border:'1px solid rgba(16,185,129,0.25)' }}>
            <div style={{
              padding:'16px 20px', borderBottom:'1px solid rgba(16,185,129,0.2)',
              background:'rgba(16,185,129,0.04)',
              display:'flex', alignItems:'center', justifyContent:'space-between',
            }}>
              <div>
                <span style={{ fontWeight:700, fontSize:14 }}>Optimized Resume</span>
                <span className="badge badge-green" style={{ marginLeft:10, fontSize:11 }}>After</span>
              </div>
              <div style={{ display:'flex', gap:8 }}>
                <button className="btn-ghost" style={{ padding:'6px 12px', fontSize:12 }} onClick={copyToClipboard}>
                  {copied ? <><CheckIcon /> Copied!</> : <><CopyIcon /> Copy</>}
                </button>
                <button
                  className="btn-ghost"
                  style={{ padding:'6px 12px', fontSize:12, opacity: downloading === 'pdf' ? 0.6 : 1 }}
                  onClick={() => downloadFormatted('pdf')}
                  disabled={!!downloading}
                >
                  <DownloadIcon /> {downloading === 'pdf' ? 'Generating…' : 'PDF'}
                </button>
                <button
                  className="btn-ghost"
                  style={{ padding:'6px 12px', fontSize:12, opacity: downloading === 'docx' ? 0.6 : 1 }}
                  onClick={() => downloadFormatted('docx')}
                  disabled={!!downloading}
                >
                  <DownloadIcon /> {downloading === 'docx' ? 'Generating…' : 'Word'}
                </button>
              </div>
            </div>
            <pre style={{
              padding:'20px', flex:1, overflow:'auto', maxHeight:520,
              fontSize:12.5, lineHeight:1.7, color:'var(--text)',
              fontFamily:"'JetBrains Mono', 'Consolas', monospace",
              whiteSpace:'pre-wrap', wordBreak:'break-word', margin:0,
            }}>
              {optimized_resume || '(No optimized content returned)'}
            </pre>
          </div>
        </div>

        {/* Changes summary */}
        {changes?.length > 0 && (
          <div className="card" style={{ padding:28, marginBottom:28,
            animation:'fadeUp 0.5s 0.2s ease both', opacity:0, animationFillMode:'forwards' }}>
            <div style={{ fontWeight:700, fontSize:15, marginBottom:16 }}>
              What Changed ({changes.length} improvements)
            </div>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(280px,1fr))', gap:10 }}>
              {changes.slice(0, 12).map((c, i) => (
                <div key={i} style={{
                  padding:'10px 14px', borderRadius:10,
                  background:'rgba(16,185,129,0.06)', border:'1px solid rgba(16,185,129,0.15)',
                  display:'flex', gap:10, alignItems:'flex-start',
                }}>
                  <span style={{ color:'var(--green)', flexShrink:0, marginTop:1 }}>+</span>
                  <span style={{ fontSize:13, color:'var(--text-2)', lineHeight:1.4 }}>
                    {typeof c === 'string' ? c : c.description || JSON.stringify(c)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations from analysis */}
        {recommendations?.recommendations?.length > 0 && (
          <div className="card" style={{ padding:28, marginBottom:32,
            animation:'fadeUp 0.5s 0.3s ease both', opacity:0, animationFillMode:'forwards' }}>
            <div style={{ fontWeight:700, fontSize:15, marginBottom:16 }}>Further Recommendations</div>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
              {recommendations.recommendations.map((r, i) => (
                <div key={i} style={{
                  padding:'10px 14px', borderRadius:10,
                  background:'var(--purple-dim)', border:'1px solid rgba(139,92,246,0.2)',
                  display:'flex', gap:10, alignItems:'flex-start',
                }}>
                  <span style={{ color:'var(--purple)', flexShrink:0 }}>→</span>
                  <span style={{ fontSize:13, color:'var(--text-2)', lineHeight:1.4 }}>{r}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Bottom CTA */}
        <div style={{
          textAlign:'center',
          animation:'fadeUp 0.5s 0.4s ease both', opacity:0, animationFillMode:'forwards',
        }}>
          <button className="btn-primary" onClick={onNewAnalysis} style={{ fontSize:15, padding:'14px 32px' }}>
            Analyze Another Resume
          </button>
          <p style={{ color:'var(--text-3)', fontSize:13, marginTop:12 }}>
            Each analysis is unique — try different job descriptions to maximize your match rate.
          </p>
        </div>
      </div>
    </div>
  );
}
