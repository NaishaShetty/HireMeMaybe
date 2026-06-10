import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

function MascotDoc() {
  return (
    <svg width="130" height="150" viewBox="0 0 120 140" fill="none">
      <ellipse cx="60" cy="136" rx="38" ry="5" fill="rgba(124,58,237,0.12)"/>
      <rect x="16" y="8" width="88" height="112" rx="14" fill="white" stroke="#E9D5FF" strokeWidth="2"/>
      <path d="M84 8 L104 28 L84 28 Z" fill="#EDE9FE"/>
      <path d="M84 8 L104 28" stroke="#DDD6FE" strokeWidth="1.5"/>
      <rect x="28" y="42" width="44" height="5" rx="2.5" fill="#DDD6FE" opacity="0.8"/>
      <rect x="28" y="54" width="60" height="4" rx="2" fill="#EDE9FE" opacity="0.9"/>
      <rect x="28" y="64" width="52" height="4" rx="2" fill="#EDE9FE" opacity="0.9"/>
      <rect x="28" y="74" width="58" height="4" rx="2" fill="#EDE9FE" opacity="0.9"/>
      <rect x="28" y="84" width="40" height="4" rx="2" fill="#EDE9FE" opacity="0.7"/>
      <ellipse cx="44" cy="28" rx="5" ry="5.5" fill="#1A1032"/>
      <circle cx="46" cy="26" r="1.5" fill="white" opacity="0.7"/>
      <ellipse cx="63" cy="28" rx="5" ry="5.5" fill="#1A1032"/>
      <circle cx="65" cy="26" r="1.5" fill="white" opacity="0.7"/>
      <path d="M46 36 Q54 43 66 36" stroke="#7C3AED" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
      <circle cx="38" cy="33" r="5" fill="#FCA5A5" opacity="0.35"/>
      <circle cx="74" cy="33" r="5" fill="#FCA5A5" opacity="0.35"/>
      <text x="6" y="24" fontSize="12" opacity="0.7">✦</text>
      <text x="98" y="18" fontSize="10" opacity="0.6">✦</text>
    </svg>
  );
}

function Field({ label, type, value, onChange, placeholder, hint }) {
  const [focused, setFocused] = useState(false);
  return (
    <div style={{ marginBottom: 18 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 7 }}>
        <label style={{ fontSize: 14, fontWeight: 600, color: '#374151' }}>{label}</label>
        {hint && <span style={{ fontSize: 13, color: '#7C3AED', cursor: 'pointer', fontWeight: 500 }}>{hint}</span>}
      </div>
      <div style={{
        border: `1.5px solid ${focused ? '#7C3AED' : '#E5E7EB'}`,
        borderRadius: 12, background: '#fff', transition: 'border-color 0.2s, box-shadow 0.2s',
        boxShadow: focused ? '0 0 0 3px rgba(124,58,237,0.12)' : 'none',
        padding: '13px 14px',
      }}>
        <input
          type={type} value={value} onChange={onChange} placeholder={placeholder}
          onFocus={() => setFocused(true)} onBlur={() => setFocused(false)}
          style={{
            width: '100%', border: 'none', outline: 'none',
            fontSize: 15, color: '#1F2937', background: 'transparent',
            fontFamily: "'Inter', sans-serif",
          }}
        />
      </div>
    </div>
  );
}

export default function AuthPage({ onSkip }) {
  const { signIn, signUp } = useAuth();
  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setSuccess('');
    if (!email.trim() || !password.trim()) { setError('Email and password are required.'); return; }
    if (password.length < 6) { setError('Password must be at least 6 characters.'); return; }
    setLoading(true);
    try {
      if (mode === 'signup') {
        await signUp(email.trim(), password);
        setSuccess('Account created! You can now sign in.');
        setMode('login');
      } else {
        await signIn(email.trim(), password);
      }
    } catch (err) {
      setError(err.message || 'Authentication failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#F5F0FF', display: 'flex', fontFamily: "'Inter', system-ui, sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        @keyframes authFadeUp { from{opacity:0;transform:translateY(28px)} to{opacity:1;transform:none} }
        @keyframes authFloat  { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
        @keyframes authOrb    { 0%,100%{transform:translate(0,0)} 50%{transform:translate(20px,-14px)} }
        .auth-mascot { animation: authFloat 3.5s ease-in-out infinite; }
        .auth-card   { animation: authFadeUp 0.5s cubic-bezier(0.34,1.56,0.64,1) both; }
        .auth-btn {
          width:100%; padding:14px; border-radius:14px; border:none; cursor:pointer;
          background:linear-gradient(135deg,#7C3AED,#4F46E5);
          color:#fff; font-size:16px; font-weight:700; font-family:'Inter',sans-serif;
          display:flex; align-items:center; justify-content:center; gap:8px;
          box-shadow:0 4px 20px rgba(124,58,237,0.35);
          transition:transform 0.15s, box-shadow 0.15s, opacity 0.15s;
        }
        .auth-btn:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 8px 28px rgba(124,58,237,0.45);}
        .auth-btn:active:not(:disabled){transform:translateY(0);}
        .auth-btn:disabled{opacity:0.55;cursor:not-allowed;}
        .auth-tab {
          flex:1; padding:10px 0; border:none; cursor:pointer; border-radius:10px;
          font-size:14px; font-weight:600; transition:all 0.2s; font-family:'Inter',sans-serif;
        }
        @keyframes spin { to{transform:rotate(360deg)} }
      `}</style>

      {/* Left panel */}
      <div style={{
        width: '42%', minHeight: '100vh',
        background: 'linear-gradient(160deg, #EDE8FF 0%, #F5F0FF 60%, #EEF2FF 100%)',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        padding: '60px 48px', position: 'relative', overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', width: 380, height: 380, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(124,58,237,0.14) 0%, transparent 70%)',
          top: '-80px', left: '-60px', animation: 'authOrb 9s ease-in-out infinite', pointerEvents: 'none',
        }}/>
        <div style={{
          position: 'absolute', width: 280, height: 280, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 70%)',
          bottom: '-60px', right: '-40px', animation: 'authOrb 11s ease-in-out 2s infinite reverse', pointerEvents: 'none',
        }}/>

        <div style={{ marginBottom: 40, textAlign: 'center' }}>
          <div style={{ fontSize: 36, fontWeight: 900, letterSpacing: '-1px', color: '#1A1032', marginBottom: 2 }}>
            Hire
            <span style={{ background: 'linear-gradient(135deg,#7C3AED,#4F46E5)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>Me</span>
            Maybe
            <span style={{ color: '#7C3AED' }}>?</span>
          </div>
        </div>

        <div className="auth-mascot" style={{ marginBottom: 36 }}>
          <MascotDoc />
        </div>

        <div style={{ textAlign: 'center', maxWidth: 280 }}>
          <p style={{ fontSize: 26, fontWeight: 800, color: '#1A1032', lineHeight: 1.3, marginBottom: 12 }}>
            Maybe?
            <br />
            <span style={{ background: 'linear-gradient(135deg,#7C3AED,#4F46E5)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              {"Let's Fix That."}
            </span>
            {' '}💜
          </p>
          <p style={{ fontSize: 15, color: '#6B7280', lineHeight: 1.6, marginBottom: 28 }}>
            AI-powered tools to help you get past ATS and{' '}
            <span style={{ color: '#7C3AED', fontWeight: 600 }}>land interviews.</span>
          </p>
          <div style={{
            background: '#FEF9C3', border: '1px solid #FDE047', borderRadius: 12,
            padding: '14px 18px', transform: 'rotate(-2deg)',
            boxShadow: '2px 3px 12px rgba(0,0,0,0.08)',
            display: 'inline-block', textAlign: 'left',
            fontSize: 13, color: '#78350F', fontWeight: 500, lineHeight: 1.5,
          }}>
            Dear Recruiter,
            <br />
            <span style={{ fontWeight: 700 }}>{"Let's make it happen."}</span> 💜
          </div>
        </div>
      </div>

      {/* Right panel */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center',
        padding: '40px 32px', background: '#fff',
      }}>
        <div className="auth-card" style={{ width: '100%', maxWidth: 420 }}>
          <h2 style={{ fontSize: 28, fontWeight: 800, color: '#1A1032', marginBottom: 4, textAlign: 'center' }}>
            {mode === 'login' ? 'Welcome back 👋' : 'Create account ✨'}
          </h2>
          <p style={{ fontSize: 14, color: '#9CA3AF', textAlign: 'center', marginBottom: 28 }}>
            {mode === 'login' ? 'Log in to continue your journey' : 'Join thousands optimizing their resumes'}
          </p>

          {/* Tab toggle */}
          <div style={{ display: 'flex', gap: 4, background: '#F3F4F6', borderRadius: 14, padding: 4, marginBottom: 28 }}>
            {[['login', 'Sign In'], ['signup', 'Sign Up']].map(([m, label]) => (
              <button
                key={m}
                className="auth-tab"
                onClick={() => { setMode(m); setError(''); setSuccess(''); }}
                style={{
                  background: mode === m ? 'linear-gradient(135deg,#7C3AED,#4F46E5)' : 'transparent',
                  color: mode === m ? '#fff' : '#6B7280',
                  boxShadow: mode === m ? '0 2px 8px rgba(124,58,237,0.3)' : 'none',
                }}
              >
                {label}
              </button>
            ))}
          </div>

          {error && (
            <div style={{
              background: 'rgba(239,68,68,0.07)', border: '1px solid rgba(239,68,68,0.2)',
              borderRadius: 12, padding: '11px 14px', marginBottom: 18,
              fontSize: 13, color: '#B91C1C', display: 'flex', gap: 8, alignItems: 'center',
            }}>
              ⚠️ {error}
            </div>
          )}
          {success && (
            <div style={{
              background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)',
              borderRadius: 12, padding: '12px 16px', marginBottom: 20, fontSize: 13, color: '#065F46',
            }}>
              ✅ {success}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <Field label="Email address" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" />
            <Field label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••••" hint={mode === 'login' ? 'Forgot password?' : undefined} />
            <button type="submit" className="auth-btn" disabled={loading} style={{ marginTop: 4 }}>
              {loading
                ? (<><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" style={{ animation: 'spin 0.8s linear infinite' }}><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>{mode === 'login' ? 'Signing in...' : 'Creating account...'}</>)
                : (<>{mode === 'login' ? 'Log in' : 'Create account'} →</>)
              }
            </button>
          </form>

          {onSkip && (
            <button
              onClick={onSkip}
              style={{
                width: '100%', marginTop: 14, padding: '11px',
                border: '1.5px solid #E9D5FF', borderRadius: 12,
                background: 'transparent', color: '#7C3AED',
                fontSize: 14, fontWeight: 600, cursor: 'pointer',
                fontFamily: "'Inter',sans-serif", transition: 'background 0.15s',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.06)'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
            >
              Continue without account →
            </button>
          )}

          <p style={{ textAlign: 'center', marginTop: 24, fontSize: 12, color: '#D1D5DB' }}>
            🔒 Your data is safe with us. We never share it with anyone.
          </p>
        </div>
      </div>
    </div>
  );
}
