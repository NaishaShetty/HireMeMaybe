import { useState } from 'react';

// ── Icons ──────────────────────────────────────────────────────────────────

const BackIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>
  </svg>
);
const BuildingIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/><path d="M3 9h6"/><path d="M3 15h6"/>
  </svg>
);
const CodeIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>
  </svg>
);
const ClipboardIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
    <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
  </svg>
);
const DollarIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
  </svg>
);
const StarIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
  </svg>
);
const NewsIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a4 4 0 0 1-4 4zm0 0a4 4 0 0 1-4-4V7a2 2 0 0 1 2-2h2"/>
    <line x1="16" y1="8" x2="10" y2="8"/><line x1="16" y1="12" x2="10" y2="12"/><line x1="16" y1="16" x2="10" y2="16"/>
  </svg>
);
const LightbulbIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="9" y1="18" x2="15" y2="18"/><line x1="10" y1="22" x2="14" y2="22"/>
    <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/>
  </svg>
);

// ── Sub-components ─────────────────────────────────────────────────────────

function SectionTitle({ icon, title, color = 'var(--text)' }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
      <div style={{ color, display: 'flex' }}>{icon}</div>
      <span style={{ fontWeight: 700, fontSize: 15, color }}>{title}</span>
    </div>
  );
}

function TagList({ items, color = 'var(--blue)', dim = 'rgba(59,130,246,0.15)' }) {
  if (!items?.length) return <p style={{ color: 'var(--text-3)', fontSize: 14 }}>—</p>;
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
      {items.map((item, i) => (
        <span key={i} style={{
          fontSize: 13, padding: '4px 12px', borderRadius: 8,
          background: dim, color, border: `1px solid ${color}30`, fontWeight: 500,
        }}>{item}</span>
      ))}
    </div>
  );
}

function InfoRow({ label, value }) {
  if (!value) return null;
  return (
    <div style={{ display: 'flex', gap: 12, padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
      <span style={{ fontSize: 13, color: 'var(--text-3)', width: 130, flexShrink: 0 }}>{label}</span>
      <span style={{ fontSize: 13, color: 'var(--text-2)', flex: 1 }}>{value}</span>
    </div>
  );
}

function SalaryBand({ label, value, color }) {
  if (!value) return null;
  return (
    <div style={{
      flex: 1, padding: '16px 20px', borderRadius: 12, textAlign: 'center',
      background: `${color}12`, border: `1px solid ${color}30`,
    }}>
      <div style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-3)', marginBottom: 8 }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 800, color }}>{value}</div>
    </div>
  );
}

// ── Search form (shown before data loads) ─────────────────────────────────

function CompanySearchForm({ defaultCompany = '', defaultRole = '', onSearch, loading }) {
  const [company, setCompany] = useState(defaultCompany);
  const [role, setRole] = useState(defaultRole);

  return (
    <div style={{
      maxWidth: 500, margin: '80px auto 0', padding: '0 24px', textAlign: 'center',
      animation: 'fadeUp 0.5s ease both',
    }}>
      <div style={{ fontSize: 40, marginBottom: 12 }}>🏢</div>
      <h2 style={{ fontSize: 24, fontWeight: 800, marginBottom: 8, letterSpacing: '-0.5px' }}>Company Intelligence</h2>
      <p style={{ color: 'var(--text-3)', fontSize: 15, marginBottom: 32 }}>
        Enter a company name to generate a full intelligence report — tech stack, interview process, salary ranges, and more.
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12, textAlign: 'left' }}>
        <div>
          <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-2)', display: 'block', marginBottom: 6 }}>Company Name</label>
          <input
            type="text"
            value={company}
            onChange={e => setCompany(e.target.value)}
            placeholder="e.g. Google, Microsoft, Stripe..."
            onKeyDown={e => e.key === 'Enter' && company.trim() && onSearch({ company, role })}
            style={{
              width: '100%', padding: '12px 16px', borderRadius: 10, fontSize: 15,
              background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)',
              color: 'var(--text)', outline: 'none',
            }}
          />
        </div>
        <div>
          <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-2)', display: 'block', marginBottom: 6 }}>Target Role</label>
          <input
            type="text"
            value={role}
            onChange={e => setRole(e.target.value)}
            placeholder="e.g. Software Engineer, Product Manager..."
            onKeyDown={e => e.key === 'Enter' && company.trim() && onSearch({ company, role })}
            style={{
              width: '100%', padding: '12px 16px', borderRadius: 10, fontSize: 15,
              background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)',
              color: 'var(--text)', outline: 'none',
            }}
          />
        </div>
        <button
          className="btn-primary"
          onClick={() => company.trim() && onSearch({ company, role: role || 'Software Engineer' })}
          disabled={!company.trim() || loading}
          style={{ marginTop: 8, padding: '14px 24px', fontSize: 15, opacity: !company.trim() ? 0.5 : 1 }}
        >
          {loading ? 'Generating Report…' : '🔍 Generate Intelligence Report'}
        </button>
      </div>
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────

export default function CompanyIntelPage({ data, defaultCompany, defaultRole, onSearch, loading, onBack }) {
  const [activeTab, setActiveTab] = useState('overview');

  if (!data) {
    return (
      <div className="page" style={{ background: 'var(--bg)' }}>
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ padding: '24px', borderBottom: '1px solid var(--border)', maxWidth: 900, margin: '0 auto' }}>
            <button className="btn-ghost" onClick={onBack}><BackIcon /> Back to Analysis</button>
          </div>
          <CompanySearchForm
            defaultCompany={defaultCompany}
            defaultRole={defaultRole}
            onSearch={onSearch}
            loading={loading}
          />
        </div>
      </div>
    );
  }

  const {
    company_overview = {},
    tech_stack = {},
    interview_process = {},
    common_interview_questions = [],
    culture_and_values = {},
    salary_ranges = {},
    recent_news = [],
    preparation_tips = [],
    disclaimer = '',
  } = data;

  const tabs = [
    { id: 'overview',  label: 'Overview'  },
    { id: 'tech',      label: 'Tech Stack' },
    { id: 'interview', label: 'Interview'  },
    { id: 'culture',   label: 'Culture'    },
    { id: 'salary',    label: 'Salary'     },
  ];

  return (
    <div className="page" style={{ background: 'var(--bg)', padding: '0 0 80px' }}>
      <div style={{
        position: 'fixed', top: -200, left: -200, width: 600, height: 600,
        background: 'radial-gradient(circle, rgba(59,130,246,0.07) 0%, transparent 70%)',
        pointerEvents: 'none', zIndex: 0,
      }} />

      <div style={{ position: 'relative', zIndex: 1, maxWidth: 960, margin: '0 auto', padding: '0 24px' }}>
        {/* Header */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '24px 0', borderBottom: '1px solid var(--border)', marginBottom: 32,
        }}>
          <button className="btn-ghost" onClick={onBack}><BackIcon /> Back</button>
          <div style={{ textAlign: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, justifyContent: 'center' }}>
              <span style={{ color: 'var(--blue)' }}><BuildingIcon /></span>
              <h2 style={{ fontSize: 20, fontWeight: 800, letterSpacing: '-0.5px' }}>
                {company_overview.name || data.company_name}
              </h2>
            </div>
            <p style={{ color: 'var(--text-3)', fontSize: 13, marginTop: 4 }}>
              {company_overview.industry || ''}{salary_ranges.role ? ` · ${salary_ranges.role}` : ''}
            </p>
          </div>
          <button
            className="btn-ghost"
            onClick={() => onSearch({ company: data.company_name, role: data.role })}
            style={{ fontSize: 13 }}
          >
            🔄 Refresh
          </button>
        </div>

        {/* Tabs */}
        <div style={{
          display: 'flex', gap: 6, marginBottom: 28, padding: '5px',
          background: 'rgba(255,255,255,0.04)', borderRadius: 14, border: '1px solid var(--border)',
          animation: 'fadeUp 0.4s ease both',
        }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                flex: 1, padding: '9px 14px', borderRadius: 10, border: 'none', cursor: 'pointer',
                fontWeight: 600, fontSize: 13, transition: 'all 0.2s',
                background: activeTab === tab.id ? 'rgba(255,255,255,0.08)' : 'transparent',
                color: activeTab === tab.id ? 'var(--blue)' : 'var(--text-3)',
                boxShadow: activeTab === tab.id ? '0 2px 8px rgba(0,0,0,0.2)' : 'none',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div key={activeTab} style={{ animation: 'fadeUp 0.35s ease both' }}>

          {/* OVERVIEW */}
          {activeTab === 'overview' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
              <div className="card" style={{ padding: 28 }}>
                <SectionTitle icon={<BuildingIcon />} title="Company Overview" color="var(--blue)" />
                <div>
                  <InfoRow label="Founded" value={company_overview.founded} />
                  <InfoRow label="Headquarters" value={company_overview.headquarters} />
                  <InfoRow label="Size" value={company_overview.size} />
                  <InfoRow label="Industry" value={company_overview.industry} />
                  <InfoRow label="Business Model" value={company_overview.business_model} />
                  {company_overview.mission && (
                    <div style={{ marginTop: 16 }}>
                      <div style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-3)', marginBottom: 8 }}>Mission</div>
                      <p style={{ fontSize: 14, color: 'var(--text-2)', lineHeight: 1.6, fontStyle: 'italic' }}>
                        "{company_overview.mission}"
                      </p>
                    </div>
                  )}
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                {company_overview.notable_products_or_services?.length > 0 && (
                  <div className="card" style={{ padding: 24 }}>
                    <SectionTitle icon={<StarIcon />} title="Notable Products / Services" color="var(--purple)" />
                    <TagList items={company_overview.notable_products_or_services} color="var(--purple)" dim="rgba(139,92,246,0.12)" />
                  </div>
                )}

                {recent_news.length > 0 && (
                  <div className="card" style={{ padding: 24 }}>
                    <SectionTitle icon={<NewsIcon />} title="Recent News" color="var(--cyan)" />
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      {recent_news.map((item, i) => (
                        <div key={i} style={{
                          padding: '10px 14px', borderRadius: 10,
                          background: 'rgba(6,182,212,0.06)', border: '1px solid rgba(6,182,212,0.15)',
                          fontSize: 14, color: 'var(--text-2)', lineHeight: 1.5,
                        }}>
                          📰 {item}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TECH STACK */}
          {activeTab === 'tech' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
              {[
                { key: 'languages',    label: 'Languages',      color: '#3b82f6', dim: 'rgba(59,130,246,0.12)' },
                { key: 'frameworks',   label: 'Frameworks',     color: '#8b5cf6', dim: 'rgba(139,92,246,0.12)' },
                { key: 'infrastructure', label: 'Infrastructure', color: '#10b981', dim: 'rgba(16,185,129,0.12)' },
                { key: 'data_tools',   label: 'Data Tools',     color: '#f59e0b', dim: 'rgba(245,158,11,0.12)' },
              ].map(({ key, label, color, dim }) => (
                <div key={key} className="card" style={{ padding: 24 }}>
                  <SectionTitle icon={<CodeIcon />} title={label} color={color} />
                  <TagList items={tech_stack[key]} color={color} dim={dim} />
                </div>
              ))}
              {tech_stack.notes && (
                <div className="card" style={{ padding: 24, gridColumn: '1 / -1' }}>
                  <div style={{ fontSize: 13, color: 'var(--text-3)', fontStyle: 'italic' }}>{tech_stack.notes}</div>
                </div>
              )}
            </div>
          )}

          {/* INTERVIEW */}
          {activeTab === 'interview' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                <div className="card" style={{ padding: 24 }}>
                  <SectionTitle icon={<ClipboardIcon />} title="Interview Process" color="var(--green)" />
                  {interview_process.typical_stages?.length > 0 && (
                    <div style={{ marginBottom: 16 }}>
                      {interview_process.typical_stages.map((stage, i) => (
                        <div key={i} style={{
                          display: 'flex', gap: 12, alignItems: 'flex-start',
                          padding: '10px 0', borderBottom: i < interview_process.typical_stages.length - 1 ? '1px solid var(--border)' : 'none',
                        }}>
                          <div style={{
                            width: 24, height: 24, borderRadius: '50%', flexShrink: 0,
                            background: 'var(--green-dim)', color: 'var(--green)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: 12, fontWeight: 700,
                          }}>{i + 1}</div>
                          <span style={{ fontSize: 14, color: 'var(--text-2)', lineHeight: 1.5 }}>{stage}</span>
                        </div>
                      ))}
                    </div>
                  )}
                  <InfoRow label="Format" value={interview_process.format} />
                  <InfoRow label="Duration" value={interview_process.duration_weeks ? `~${interview_process.duration_weeks} weeks` : null} />
                </div>

                {interview_process.tips?.length > 0 && (
                  <div className="card" style={{ padding: 24 }}>
                    <SectionTitle icon={<LightbulbIcon />} title="Interview Tips" color="var(--amber)" />
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                      {interview_process.tips.map((tip, i) => (
                        <div key={i} style={{
                          padding: '10px 14px', borderRadius: 10,
                          background: 'var(--amber-dim)', border: '1px solid rgba(245,158,11,0.2)',
                          fontSize: 14, color: 'var(--text-2)', lineHeight: 1.5,
                        }}>→ {tip}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="card" style={{ padding: 24 }}>
                <SectionTitle icon={<StarIcon />} title={`Common Questions (${common_interview_questions.length})`} color="var(--purple)" />
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                  {common_interview_questions.map((q, i) => (
                    <div key={i} style={{
                      padding: '12px 14px', borderRadius: 10,
                      background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border)',
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                        <p style={{ fontSize: 14, color: 'var(--text-2)', lineHeight: 1.5 }}>{q.question}</p>
                        {q.type && (
                          <span style={{
                            fontSize: 10, fontWeight: 700, padding: '2px 6px', borderRadius: 5, flexShrink: 0,
                            textTransform: 'uppercase', letterSpacing: '0.05em',
                            background: q.type === 'technical' ? 'rgba(59,130,246,0.15)' : q.type === 'behavioural' ? 'rgba(16,185,129,0.15)' : 'rgba(139,92,246,0.15)',
                            color: q.type === 'technical' ? '#3b82f6' : q.type === 'behavioural' ? '#10b981' : '#8b5cf6',
                          }}>{q.type}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* CULTURE */}
          {activeTab === 'culture' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                <div className="card" style={{ padding: 24 }}>
                  <SectionTitle icon={<StarIcon />} title="Key Principles" color="var(--purple)" />
                  <TagList items={culture_and_values.key_principles} color="var(--purple)" dim="rgba(139,92,246,0.12)" />
                </div>
                {culture_and_values.work_style && (
                  <div className="card" style={{ padding: 24 }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-2)', marginBottom: 10 }}>Work Style</div>
                    <p style={{ fontSize: 14, color: 'var(--text-2)', lineHeight: 1.6 }}>{culture_and_values.work_style}</p>
                  </div>
                )}
                {culture_and_values.known_for && (
                  <div className="card" style={{ padding: 24 }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-2)', marginBottom: 10 }}>Known For</div>
                    <p style={{ fontSize: 14, color: 'var(--text-2)', lineHeight: 1.6 }}>{culture_and_values.known_for}</p>
                  </div>
                )}
              </div>

              {preparation_tips.length > 0 && (
                <div className="card" style={{ padding: 24 }}>
                  <SectionTitle icon={<LightbulbIcon />} title="Preparation Tips" color="var(--green)" />
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {preparation_tips.map((tip, i) => (
                      <div key={i} style={{
                        padding: '12px 14px', borderRadius: 10,
                        background: 'var(--green-dim)', border: '1px solid rgba(16,185,129,0.2)',
                        display: 'flex', gap: 10, alignItems: 'flex-start',
                      }}>
                        <span style={{ color: 'var(--green)', flexShrink: 0, marginTop: 1 }}>✓</span>
                        <span style={{ fontSize: 14, color: 'var(--text-2)', lineHeight: 1.5 }}>{tip}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* SALARY */}
          {activeTab === 'salary' && (
            <div style={{ maxWidth: 640, margin: '0 auto' }}>
              <div className="card" style={{ padding: 32, marginBottom: 20 }}>
                <SectionTitle icon={<DollarIcon />} title={`Salary Ranges · ${salary_ranges.role || 'Software Engineer'}`} color="var(--green)" />
                <div style={{ display: 'flex', gap: 16, marginBottom: 20 }}>
                  <SalaryBand label="Junior" value={salary_ranges.junior} color="#10b981" />
                  <SalaryBand label="Mid-Level" value={salary_ranges.mid} color="#3b82f6" />
                  <SalaryBand label="Senior" value={salary_ranges.senior} color="#8b5cf6" />
                </div>
                <InfoRow label="Currency" value={salary_ranges.currency} />
                {salary_ranges.source_note && (
                  <p style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 16, lineHeight: 1.5 }}>
                    ⚠ {salary_ranges.source_note}
                  </p>
                )}
              </div>
              {disclaimer && (
                <div style={{
                  padding: '14px 18px', borderRadius: 10, fontSize: 13, color: 'var(--text-3)',
                  background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)', lineHeight: 1.5,
                }}>
                  ℹ {disclaimer}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
