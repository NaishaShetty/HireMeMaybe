import { useState } from 'react';

// ── Icons ──────────────────────────────────────────────────────────────────

const BackIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
  </svg>
);
const BrainIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.46 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.14Z"/>
    <path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.46 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.14Z"/>
  </svg>
);
const AlertIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
  </svg>
);
const StarIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
  </svg>
);
const ChevronDown = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="6 9 12 15 18 9"/>
  </svg>
);
const ChevronUp = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="18 15 12 9 6 15"/>
  </svg>
);

// ── Sub-components ─────────────────────────────────────────────────────────

function SectionTitle({ icon, title, color = 'var(--text)', count }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20 }}>
      <div style={{ color, display: 'flex' }}>{icon}</div>
      <span style={{ fontWeight: 700, fontSize: 16, color }}>{title}</span>
      {count !== undefined && (
        <span style={{ marginLeft: 4, fontSize: 13, color: 'var(--text-3)', fontWeight: 500 }}>({count})</span>
      )}
    </div>
  );
}

function CategoryBadge({ category }) {
  const map = {
    technical:   { bg: 'rgba(59,130,246,0.15)',  color: '#3b82f6', label: 'Technical' },
    behavioural: { bg: 'rgba(16,185,129,0.15)',  color: '#10b981', label: 'Behavioural' },
    situational: { bg: 'rgba(245,158,11,0.15)',  color: '#f59e0b', label: 'Situational' },
    values:      { bg: 'rgba(139,92,246,0.15)',  color: '#8b5cf6', label: 'Values' },
  };
  const style = map[category?.toLowerCase()] || map.technical;
  return (
    <span style={{
      fontSize: 11, fontWeight: 600, padding: '2px 8px', borderRadius: 6,
      background: style.bg, color: style.color, textTransform: 'uppercase', letterSpacing: '0.05em',
    }}>{style.label}</span>
  );
}

function QuestionCard({ item, accent }) {
  return (
    <div style={{
      padding: '16px 20px', borderRadius: 12,
      background: 'rgba(255,255,255,0.03)', border: `1px solid ${accent}30`,
      display: 'flex', flexDirection: 'column', gap: 10,
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
        <p style={{ fontSize: 15, fontWeight: 600, color: 'var(--text)', lineHeight: 1.5 }}>
          {item.question}
        </p>
        {item.category && <CategoryBadge category={item.category} />}
      </div>
      <p style={{ fontSize: 13, color: 'var(--text-3)', lineHeight: 1.5 }}>
        💡 {item.reason || item.how_to_handle}
      </p>
    </div>
  );
}

function StarCard({ item }) {
  const [open, setOpen] = useState(false);
  const fields = [
    { key: 'situation', label: 'S — Situation', color: '#3b82f6' },
    { key: 'task',      label: 'T — Task',      color: '#8b5cf6' },
    { key: 'action',    label: 'A — Action',    color: '#10b981' },
    { key: 'result',    label: 'R — Result',    color: '#f59e0b' },
  ];

  return (
    <div style={{
      borderRadius: 12, border: '1px solid rgba(139,92,246,0.2)',
      background: 'rgba(139,92,246,0.05)', overflow: 'hidden',
    }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: '100%', padding: '16px 20px', background: 'none', border: 'none',
          cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12,
          textAlign: 'left',
        }}
      >
        <div>
          <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--text)', lineHeight: 1.5 }}>{item.question}</p>
          {item.source && (
            <p style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 4 }}>Source: {item.source}</p>
          )}
        </div>
        <div style={{ color: 'var(--purple)', flexShrink: 0 }}>
          {open ? <ChevronUp /> : <ChevronDown />}
        </div>
      </button>

      {open && (
        <div style={{ padding: '0 20px 20px', display: 'flex', flexDirection: 'column', gap: 12 }}>
          {fields.map(({ key, label, color }) => item[key] ? (
            <div key={key} style={{
              padding: '12px 14px', borderRadius: 10,
              borderLeft: `3px solid ${color}`, background: 'rgba(255,255,255,0.03)',
            }}>
              <div style={{ fontSize: 11, fontWeight: 700, color, textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6 }}>
                {label}
              </div>
              <p style={{ fontSize: 14, color: 'var(--text-2)', lineHeight: 1.6 }}>{item[key]}</p>
            </div>
          ) : null)}
        </div>
      )}
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────

export default function InterviewPrepPage({ data, jdData, onBack }) {
  const {
    likely_questions = [],
    weakness_questions = [],
    star_answers = [],
    matched_skills = [],
    missing_skills = [],
  } = data;

  const [activeTab, setActiveTab] = useState('likely');

  const tabs = [
    { id: 'likely',    label: 'Likely Questions',   count: likely_questions.length,   color: 'var(--green)' },
    { id: 'weakness',  label: 'Gap Questions',       count: weakness_questions.length, color: 'var(--amber)' },
    { id: 'star',      label: 'STAR Answers',        count: star_answers.length,       color: 'var(--purple)' },
  ];

  return (
    <div className="page" style={{ background: 'var(--bg)', padding: '0 0 80px' }}>
      {/* Ambient glow */}
      <div style={{
        position: 'fixed', top: -200, right: -200, width: 600, height: 600,
        background: 'radial-gradient(circle, rgba(16,185,129,0.07) 0%, transparent 70%)',
        pointerEvents: 'none', zIndex: 0,
      }} />

      <div style={{ position: 'relative', zIndex: 1, maxWidth: 900, margin: '0 auto', padding: '0 24px' }}>
        {/* Header */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '24px 0', borderBottom: '1px solid var(--border)', marginBottom: 36,
        }}>
          <button className="btn-ghost" onClick={onBack}><BackIcon /> Back to Analysis</button>
          <div style={{ textAlign: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center' }}>
              <span style={{ color: 'var(--green)' }}><BrainIcon /></span>
              <h2 style={{ fontSize: 20, fontWeight: 800, letterSpacing: '-0.5px' }}>Interview Preparation</h2>
            </div>
            <p style={{ color: 'var(--text-3)', fontSize: 13, marginTop: 4 }}>
              {jdData?.job_title || 'Target Role'}{jdData?.company ? ` · ${jdData.company}` : ''}
            </p>
          </div>
          <div style={{ width: 120 }} />
        </div>

        {/* Stats row */}
        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 32,
          animation: 'fadeUp 0.4s ease both',
        }}>
          {[
            { label: 'Expected Questions', value: likely_questions.length, color: 'var(--green)' },
            { label: 'Gap Questions', value: weakness_questions.length, color: 'var(--amber)' },
            { label: 'STAR Answers Ready', value: star_answers.length, color: 'var(--purple)' },
          ].map((s, i) => (
            <div key={i} className="card" style={{ padding: '20px 24px', textAlign: 'center' }}>
              <div style={{ fontSize: 32, fontWeight: 800, color: s.color }}>{s.value}</div>
              <div style={{ fontSize: 13, color: 'var(--text-3)', marginTop: 4 }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div style={{
          display: 'flex', gap: 8, marginBottom: 24, padding: '6px',
          background: 'rgba(255,255,255,0.04)', borderRadius: 14, border: '1px solid var(--border)',
          animation: 'fadeUp 0.4s 0.1s ease both', opacity: 0, animationFillMode: 'forwards',
        }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                flex: 1, padding: '10px 16px', borderRadius: 10, border: 'none', cursor: 'pointer',
                fontWeight: 600, fontSize: 14, transition: 'all 0.2s',
                background: activeTab === tab.id ? 'rgba(255,255,255,0.08)' : 'transparent',
                color: activeTab === tab.id ? tab.color : 'var(--text-3)',
                boxShadow: activeTab === tab.id ? '0 2px 8px rgba(0,0,0,0.2)' : 'none',
              }}
            >
              {tab.label}
              <span style={{
                marginLeft: 6, fontSize: 12, padding: '1px 7px', borderRadius: 10,
                background: activeTab === tab.id ? `${tab.color}20` : 'rgba(255,255,255,0.06)',
                color: activeTab === tab.id ? tab.color : 'var(--text-3)',
              }}>{tab.count}</span>
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div style={{ animation: 'fadeUp 0.35s ease both' }} key={activeTab}>

          {activeTab === 'likely' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {likely_questions.length > 0 ? (
                likely_questions.map((q, i) => <QuestionCard key={i} item={q} accent="var(--green)" />)
              ) : (
                <div className="card" style={{ padding: 40, textAlign: 'center', color: 'var(--text-3)' }}>
                  No questions generated yet.
                </div>
              )}
            </div>
          )}

          {activeTab === 'weakness' && (
            <div>
              {weakness_questions.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {weakness_questions.map((q, i) => <QuestionCard key={i} item={q} accent="var(--amber)" />)}
                </div>
              ) : (
                <div className="card" style={{ padding: 40, textAlign: 'center', color: 'var(--text-3)' }}>
                  No skill gaps found — great position!
                </div>
              )}

              {missing_skills.length > 0 && (
                <div className="card" style={{ padding: 24, marginTop: 24 }}>
                  <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 12, color: 'var(--amber)', display: 'flex', alignItems: 'center', gap: 8 }}>
                    <AlertIcon /> Skills to address in answers
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    {missing_skills.map((s, i) => (
                      <span key={i} className="badge badge-amber" style={{ fontSize: 13 }}>{s}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'star' && (
            <div>
              {star_answers.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  <p style={{ fontSize: 13, color: 'var(--text-3)', marginBottom: 4 }}>
                    Click any question to reveal the STAR answer draft. All content is drawn directly from your resume.
                  </p>
                  {star_answers.map((s, i) => <StarCard key={i} item={s} />)}
                </div>
              ) : (
                <div className="card" style={{ padding: 40, textAlign: 'center', color: 'var(--text-3)' }}>
                  No STAR answers generated. Make sure your resume has detailed experience descriptions.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
