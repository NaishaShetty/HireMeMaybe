/**
 * PaywallModal — shown when a free-tier user tries to access a Pro feature.
 *
 * Props:
 *   featureLabel  string   Human-readable name of the gated feature
 *   onClose       fn       Dismiss the modal
 *   onUpgrade     fn       Called when the user clicks "Upgrade to Pro"
 *                          (hook up to Stripe/billing page when ready)
 *   isAuthenticated bool   If false, show "create an account first" copy
 */

const LockIcon = () => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
  </svg>
);

const CheckIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const PRO_PERKS = [
  'Unlimited AI Resume Rewrites',
  'Interview Question Generator + STAR Answers',
  'Company Intelligence Reports',
  'Priority ATS optimization',
  'Export to PDF & Word',
];

export default function PaywallModal({ featureLabel, onClose, onUpgrade, isAuthenticated = true }) {
  return (
    <div
      style={{
        position: 'fixed', inset: 0, zIndex: 10000,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'rgba(7,7,15,0.85)', backdropFilter: 'blur(12px)',
        animation: 'fadeIn 0.2s ease',
        padding: '24px',
      }}
      onClick={e => { if (e.target === e.currentTarget) onClose(); }}
    >
      <div
        className="card"
        style={{
          width: '100%', maxWidth: 480, padding: 40,
          border: '1px solid rgba(139,92,246,0.3)',
          boxShadow: '0 0 60px rgba(139,92,246,0.15)',
          animation: 'fadeUp 0.3s ease',
          position: 'relative',
        }}
      >
        {/* Close */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute', top: 16, right: 16,
            background: 'none', border: 'none', color: 'var(--text-3)',
            cursor: 'pointer', fontSize: 22, lineHeight: 1, padding: 4,
          }}
        >
          ×
        </button>

        {/* Icon */}
        <div style={{
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
          width: 60, height: 60, borderRadius: 18,
          background: 'var(--purple-dim)', marginBottom: 20,
          color: 'var(--purple)',
        }}>
          <LockIcon />
        </div>

        {/* Headline */}
        <h2 style={{ fontSize: 22, fontWeight: 800, letterSpacing: '-0.5px', marginBottom: 8 }}>
          {featureLabel} is a Pro feature
        </h2>
        <p style={{ color: 'var(--text-2)', fontSize: 14, lineHeight: 1.6, marginBottom: 28 }}>
          {isAuthenticated
            ? `Upgrade to HireMeMaybe Pro to unlock ${featureLabel} and the full suite of AI-powered career tools.`
            : `Create a free account, then upgrade to Pro to unlock ${featureLabel} and the full career toolkit.`}
        </p>

        {/* Perks */}
        <div style={{ marginBottom: 28 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12 }}>
            Everything in Pro
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {PRO_PERKS.map(perk => (
              <div key={perk} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{
                  width: 20, height: 20, borderRadius: 6,
                  background: 'var(--green-dim)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  color: 'var(--green)', flexShrink: 0,
                }}>
                  <CheckIcon />
                </div>
                <span style={{ fontSize: 14, color: 'var(--text-2)' }}>{perk}</span>
              </div>
            ))}
          </div>
        </div>

        {/* CTAs */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <button
            className="btn-primary"
            onClick={onUpgrade}
            style={{ fontSize: 15, padding: '13px 0' }}
          >
            Upgrade to Pro
          </button>
          <button
            onClick={onClose}
            style={{
              background: 'none', border: '1px solid var(--border)', borderRadius: 10,
              color: 'var(--text-2)', fontSize: 14, padding: '11px 0',
              cursor: 'pointer', transition: 'border-color 0.2s',
            }}
            onMouseEnter={e => e.target.style.borderColor = 'var(--border-bright)'}
            onMouseLeave={e => e.target.style.borderColor = 'var(--border)'}
          >
            Maybe later
          </button>
        </div>
      </div>
    </div>
  );
}
