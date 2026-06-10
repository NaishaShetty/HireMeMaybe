import ScoreRing from '../components/ScoreRing.jsx';

const BrainIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.14Z"/>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.14Z"/>
  </svg>
);

const BuildingIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="7" width="20" height="15" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
    <line x1="8" y1="11" x2="8" y2="11.01"/><line x1="16" y1="11" x2="16" y2="11.01"/>
    <line x1="12" y1="11" x2="12" y2="11.01"/><line x1="8" y1="15" x2="8" y2="15.01"/>
    <line x1="16" y1="15" x2="16" y2="15.01"/><line x1="12" y1="15" x2="12" y2="15.01"/>
  </svg>
);

const SparklesIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3l1.09 3.26L16 7.5l-3.26 1.09L12 12l-1.09-3.26L8 7.5l3.26-1.09z"/><path d="M5 3l.55 1.64L7 5.5l-1.45.86L5 8l-.55-1.64L3 5.5l1.45-.86z"/><path d="M19 3l.55 1.64L21 5.5l-1.45.86L19 8l-.55-1.64L17 5.5l1.45-.86z"/>
  </svg>
);

const AlertIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
  </svg>
);

const CheckCircle = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><polyline points="9 12 11 14 15 10"/>
  </svg>
);

const XCircle = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
  </svg>
);

const ShieldIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
  </svg>
);

const LightbulbIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="9" y1="18" x2="15" y2="18"/><line x1="10" y1="22" x2="14" y2="22"/>
    <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/>
  </svg>
);

const ArrowRight = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
  </svg>
);

const BackIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
  </svg>
);

function SectionTitle({ icon, title, color = 'var(--text)' }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
      <div style={{ color, display:'flex' }}>{icon}</div>
      <span style={{ fontWeight: 700, fontSize: 15, color }}>{title}</span>
    </div>
  );
}

function InsightCard({ items, icon, color, emptyText = 'None identified.' }) {
  if (!items?.length) return <p style={{ color:'var(--text-3)', fontSize:14 }}>{emptyText}</p>;
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
      {items.map((item, i) => (
        <div key={i} style={{
          display:'flex', gap:10, alignItems:'flex-start',
          padding:'10px 14px', borderRadius:10,
          background:'rgba(255,255,255,0.03)',
          border:'1px solid var(--border)',
        }}>
          <div style={{ color, marginTop:2, flexShrink:0 }}>{icon}</div>
          <span style={{ fontSize:14, lineHeight:1.5, color:'var(--text-2)' }}>{item}</span>
        </div>
      ))}
    </div>
  );
}

function ScoreMeter({ label, score, color }) {
  return (
    <div>
      <div style={{ display:'flex', justifyContent:'space-between', marginBottom:6 }}>
        <span style={{ fontSize:13, color:'var(--text-2)' }}>{label}</span>
        <span style={{ fontSize:13, fontWeight:700, color }}>{Math.round(score)}%</span>
      </div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width:`${score}%`, background:color }} />
      </div>
    </div>
  );
}

export default function AnalysisPage({ data, resumeData, jdData, resumeText, jdText, onRewrite, onInterviewPrep, onCoverLetter, onCompanyIntel, onBack }) {
  const {
    interview_probability_score = 0,
    ats_score = 0,
    semantic_similarity = 0,
    skill_match_score = 0,
    matched_skills = [],
    missing_skills = [],
    strengths = [],
    weaknesses = [],
    risk_factors = [],
    recommendations = [],
  } = data;

  const semanticPct = Math.round(semantic_similarity * 100);
  const scoreColor = (s) => s >= 75 ? 'var(--green)' : s >= 50 ? 'var(--amber)' : 'var(--red)';

  const scoreSummary = (s) => {
    if (s >= 75) return { label: 'Strong', cls: 'badge-green' };
    if (s >= 50) return { label: 'Moderate', cls: 'badge-amber' };
    return { label: 'Needs Work', cls: 'badge-red' };
  };

  const interviewSummary = scoreSummary(interview_probability_score);

  return (
    <div className="page" style={{ background:'var(--bg)', padding:'0 0 80px' }}>
      {/* Ambient */}
      <div style={{ position:'fixed', top:-300, left:-200, width:700, height:700,
        background:'radial-gradient(circle, rgba(139,92,246,0.08) 0%, transparent 70%)', pointerEvents:'none', zIndex:0 }} />

      <div style={{ position:'relative', zIndex:1, maxWidth:1100, margin:'0 auto', padding:'0 24px' }}>
        {/* Header */}
        <div style={{
          display:'flex', alignItems:'center', justifyContent:'space-between',
          padding:'24px 0', borderBottom:'1px solid var(--border)', marginBottom:40,
        }}>
          <button className="btn-ghost" onClick={onBack}><BackIcon /> New Analysis</button>
          <div style={{ textAlign:'center' }}>
            <h2 style={{ fontSize:20, fontWeight:800, letterSpacing:'-0.5px' }}>Resume Intelligence Report</h2>
            <p style={{ color:'var(--text-3)', fontSize:13, marginTop:2 }}>
              {resumeData?.email || 'Your Resume'} · {jdData?.job_title || 'Target Role'}
            </p>
          </div>
          <div className={`badge ${interviewSummary.cls}`}>
            {interviewSummary.label} Match
          </div>
        </div>

        {/* Top score rings */}
        <div style={{
          display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:20, marginBottom:32,
          animation:'fadeUp 0.5s ease both',
        }}>
          {[
            { score:interview_probability_score, label:'Interview Probability', sublabel:'/100', color: scoreColor(interview_probability_score) },
            { score:ats_score,                   label:'ATS Score',             sublabel:'/100', color: scoreColor(ats_score) },
            { score:semanticPct,                 label:'Semantic Match',        sublabel:'%',    color: scoreColor(semanticPct) },
            { score:skill_match_score,           label:'Skill Coverage',        sublabel:'%',    color: scoreColor(skill_match_score) },
          ].map((s, i) => (
            <div key={i} className="card" style={{ padding:'28px 20px', display:'flex', flexDirection:'column', alignItems:'center', gap:4 }}>
              <ScoreRing score={s.score} label={s.label} sublabel={s.sublabel} size={120} color={s.color} />
            </div>
          ))}
        </div>

        {/* Score bars */}
        <div className="card" style={{ padding:28, marginBottom:24, animation:'fadeUp 0.5s 0.1s ease both', opacity:0, animationFillMode:'forwards' }}>
          <div style={{ fontWeight:700, fontSize:15, marginBottom:20 }}>Score Breakdown</div>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'14px 40px' }}>
            <ScoreMeter label="ATS Keyword Alignment" score={ats_score} color={scoreColor(ats_score)} />
            <ScoreMeter label="Semantic Relevance" score={semanticPct} color={scoreColor(semanticPct)} />
            <ScoreMeter label="Skill Match" score={skill_match_score} color={scoreColor(skill_match_score)} />
            <ScoreMeter label="Interview Likelihood" score={interview_probability_score} color={scoreColor(interview_probability_score)} />
          </div>
        </div>

        {/* Skills */}
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:24, marginBottom:24,
          animation:'fadeUp 0.5s 0.2s ease both', opacity:0, animationFillMode:'forwards' }}>
          {/* Matched */}
          <div className="card" style={{ padding:24 }}>
            <SectionTitle icon={<CheckCircle />} title={`Matched Skills (${matched_skills.length})`} color="var(--green)" />
            <div style={{ display:'flex', flexWrap:'wrap', gap:8 }}>
              {matched_skills.length > 0
                ? matched_skills.map((s, i) => (
                  <span key={i} className="badge badge-green" style={{ fontSize:13 }}>{s}</span>
                ))
                : <p style={{ color:'var(--text-3)', fontSize:14 }}>No skills matched</p>
              }
            </div>
          </div>
          {/* Missing */}
          <div className="card" style={{ padding:24 }}>
            <SectionTitle icon={<XCircle />} title={`Missing Skills (${missing_skills.length})`} color="var(--red)" />
            <div style={{ display:'flex', flexWrap:'wrap', gap:8 }}>
              {missing_skills.length > 0
                ? missing_skills.slice(0, 20).map((s, i) => (
                  <span key={i} className="badge badge-red" style={{ fontSize:13 }}>{s}</span>
                ))
                : <p style={{ color:'var(--text-3)', fontSize:14 }}>No critical gaps found!</p>
              }
            </div>
          </div>
        </div>

        {/* Insights */}
        <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:24, marginBottom:32,
          animation:'fadeUp 0.5s 0.3s ease both', opacity:0, animationFillMode:'forwards' }}>
          <div className="card" style={{ padding:24 }}>
            <SectionTitle icon={<CheckCircle />} title="Strengths" color="var(--green)" />
            <InsightCard items={strengths} icon={<CheckCircle />} color="var(--green)" emptyText="Keep working to build strengths." />
          </div>
          <div className="card" style={{ padding:24 }}>
            <SectionTitle icon={<XCircle />} title="Weaknesses" color="var(--red)" />
            <InsightCard items={weaknesses} icon={<XCircle />} color="var(--red)" emptyText="No major weaknesses found!" />
          </div>
          <div className="card" style={{ padding:24 }}>
            <SectionTitle icon={<ShieldIcon />} title="Risk Factors" color="var(--amber)" />
            <InsightCard items={risk_factors} icon={<AlertIcon />} color="var(--amber)" emptyText="No significant risks identified." />
          </div>
        </div>

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="card" style={{ padding:28, marginBottom:40,
            animation:'fadeUp 0.5s 0.4s ease both', opacity:0, animationFillMode:'forwards' }}>
            <SectionTitle icon={<LightbulbIcon />} title="AI Recommendations" color="var(--purple)" />
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
              {recommendations.map((r, i) => (
                <div key={i} style={{
                  display:'flex', gap:10, alignItems:'flex-start',
                  padding:'10px 14px', borderRadius:10,
                  background:'var(--purple-dim)', border:'1px solid rgba(139,92,246,0.2)',
                }}>
                  <span style={{ color:'var(--purple)', flexShrink:0, marginTop:1 }}>→</span>
                  <span style={{ fontSize:14, lineHeight:1.5, color:'var(--text-2)' }}>{r}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CTA */}
        <div style={{
          animation:'fadeUp 0.5s 0.5s ease both', opacity:0, animationFillMode:'forwards',
        }}>
          {/* Main rewrite CTA */}
          <div style={{
            textAlign:'center', padding:'32px 48px', borderRadius:20,
            background:'var(--grad-subtle)', border:'1px solid rgba(139,92,246,0.2)',
            marginBottom: 20,
          }}>
            <div style={{ fontSize:22, fontWeight:800, marginBottom:8, letterSpacing:'-0.5px' }}>
              Ready to optimize?
            </div>
            <p style={{ color:'var(--text-2)', marginBottom:24, fontSize:15 }}>
              Our AI will rewrite your resume to maximize ATS compatibility for this specific role.
            </p>
            <button
              className="btn-primary"
              onClick={() => onRewrite({ resumeData, jdData, resumeText, jdText })}
              style={{ fontSize:16, padding:'16px 40px', borderRadius:14 }}
            >
              <SparklesIcon /> Generate Optimized Resume <ArrowRight />
            </button>
          </div>

          {/* Secondary CTAs */}
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:16 }}>
            <button
              onClick={onInterviewPrep}
              style={{
                display:'flex', alignItems:'center', justifyContent:'center', gap:10,
                padding:'18px 24px', borderRadius:16, border:'1px solid rgba(16,185,129,0.3)',
                background:'rgba(16,185,129,0.07)', cursor:'pointer',
                fontWeight:700, fontSize:14, color:'var(--green)',
                transition:'all 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.background='rgba(16,185,129,0.13)'; e.currentTarget.style.borderColor='rgba(16,185,129,0.5)'; }}
              onMouseLeave={e => { e.currentTarget.style.background='rgba(16,185,129,0.07)'; e.currentTarget.style.borderColor='rgba(16,185,129,0.3)'; }}
            >
              <BrainIcon />
              Interview Prep
              <ArrowRight />
            </button>

            <button
              onClick={onCoverLetter}
              style={{
                display:'flex', alignItems:'center', justifyContent:'center', gap:10,
                padding:'18px 24px', borderRadius:16, border:'1px solid rgba(245,158,11,0.3)',
                background:'rgba(245,158,11,0.07)', cursor:'pointer',
                fontWeight:700, fontSize:14, color:'var(--amber)',
                transition:'all 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.background='rgba(245,158,11,0.13)'; e.currentTarget.style.borderColor='rgba(245,158,11,0.5)'; }}
              onMouseLeave={e => { e.currentTarget.style.background='rgba(245,158,11,0.07)'; e.currentTarget.style.borderColor='rgba(245,158,11,0.3)'; }}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
              Cover Letter
              <ArrowRight />
            </button>

            <button
              onClick={onCompanyIntel}
              style={{
                display:'flex', alignItems:'center', justifyContent:'center', gap:10,
                padding:'18px 24px', borderRadius:16, border:'1px solid rgba(59,130,246,0.3)',
                background:'rgba(59,130,246,0.07)', cursor:'pointer',
                fontWeight:700, fontSize:14, color:'#3b82f6',
                transition:'all 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.background='rgba(59,130,246,0.13)'; e.currentTarget.style.borderColor='rgba(59,130,246,0.5)'; }}
              onMouseLeave={e => { e.currentTarget.style.background='rgba(59,130,246,0.07)'; e.currentTarget.style.borderColor='rgba(59,130,246,0.3)'; }}
            >
              <BuildingIcon />
              Company Intel
              <ArrowRight />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
