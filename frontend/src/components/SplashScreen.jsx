/**
 * SplashScreen — 15-second mascot animation:
 *   0–2s   : mascot appears, cute wink
 *   2–5s   : mascot folds/morphs into a paper airplane
 *   5–11s  : paper airplane flies across screen leaving purple sparkle trail
 *   11–13s : airplane turns back into the document mascot, lands center
 *   13–15s : HireMeMaybe logo + tagline fade in, call to proceed
 */
import { useEffect, useState } from 'react';

export default function SplashScreen({ onDone }) {
  const [phase, setPhase] = useState(0);
  // 0=mascot  1=wink  2=folding  3=flying  4=landing  5=logo

  useEffect(() => {
    const timers = [
      setTimeout(() => setPhase(1), 900),   // wink
      setTimeout(() => setPhase(2), 2200),  // fold
      setTimeout(() => setPhase(3), 4200),  // fly
      setTimeout(() => setPhase(4), 10800), // land
      setTimeout(() => setPhase(5), 12600), // logo reveal
      setTimeout(() => onDone?.(), 15000),  // done
    ];
    return () => timers.forEach(clearTimeout);
  }, [onDone]);

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      background: '#F5F0FF',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      overflow: 'hidden',
      fontFamily: "'Inter', system-ui, sans-serif",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

        @keyframes splashFadeIn   { from { opacity:0; transform:translateY(24px) scale(0.9) } to { opacity:1; transform:none } }
        @keyframes splashFloat    { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
        @keyframes splashWink     { 0%,80%,100%{transform:scaleY(1)} 40%{transform:scaleY(0.1)} }
        @keyframes splashFold     { 0%{transform:scale(1) rotate(0deg); border-radius:18px} 100%{transform:scale(0.55) rotate(-20deg); border-radius:50%} }
        @keyframes splashFly      {
          0%   { left:50%; top:50%; transform:translate(-50%,-50%) rotate(0deg) scale(0.55); opacity:1; }
          15%  { left:80%; top:22%; transform:translate(-50%,-50%) rotate(25deg) scale(0.65); }
          35%  { left:92%; top:55%; transform:translate(-50%,-50%) rotate(-15deg) scale(0.7); }
          55%  { left:15%; top:72%; transform:translate(-50%,-50%) rotate(30deg) scale(0.65); }
          78%  { left:5%;  top:30%; transform:translate(-50%,-50%) rotate(-10deg) scale(0.6); }
          100% { left:50%; top:50%; transform:translate(-50%,-50%) rotate(0deg) scale(1); }
        }
        @keyframes splashLand     { from{transform:scale(1.2) rotate(-5deg)} to{transform:scale(1) rotate(0)} }
        @keyframes splashLogoIn   { from{opacity:0;transform:translateY(30px) scale(0.85)} to{opacity:1;transform:none} }
        @keyframes splashTagIn    { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:none} }
        @keyframes splashBtnIn    { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:none} }
        @keyframes trailFade      { 0%{opacity:0.85;transform:scale(1)} 100%{opacity:0;transform:scale(0.3)} }
        @keyframes starPop        { 0%{opacity:0;transform:scale(0) rotate(0deg)} 30%{opacity:1;transform:scale(1.3) rotate(180deg)} 100%{opacity:0;transform:scale(0.2) rotate(360deg)} }
        @keyframes bgPulse        { 0%,100%{background:#F5F0FF} 50%{background:#EDE8FF} }
        @keyframes orbFloat       { 0%,100%{transform:translate(0,0) scale(1)} 33%{transform:translate(30px,-20px) scale(1.05)} 66%{transform:translate(-20px,15px) scale(0.97)} }
        @keyframes progressGrow   { from{width:0} to{width:100%} }
        @keyframes eyeBlink       { 0%,45%,55%,100%{transform:scaleY(1)} 50%{transform:scaleY(0.05)} }
        @keyframes eyeWink        { 0%,100%{transform:scaleY(1)} 40%,60%{transform:scaleY(0.08)} }

        .splash-bg { animation: bgPulse 4s ease-in-out infinite; }

        .mascot-idle { animation: splashFadeIn 0.7s ease both, splashFloat 3s ease-in-out 0.7s infinite; }
        .mascot-wink .eye-left  { animation: eyeBlink 0.35s ease 0.1s; }
        .mascot-wink .eye-right { animation: eyeWink  0.35s ease; }
        .mascot-fold { animation: splashFold 1.8s cubic-bezier(0.4,0,0.2,1) forwards; }
        .mascot-fly  {
          position: fixed !important;
          animation: splashFly 7s cubic-bezier(0.25,0.46,0.45,0.94) forwards !important;
        }
        .mascot-land { animation: splashLand 0.6s cubic-bezier(0.34,1.56,0.64,1) both; }

        .logo-reveal { animation: splashLogoIn 1s cubic-bezier(0.34,1.56,0.64,1) both; }
        .tag-reveal  { animation: splashTagIn  0.7s ease 0.25s both; }
        .btn-reveal  { animation: splashBtnIn  0.6s ease 0.5s both; }

        .trail-dot { animation: trailFade 1.4s ease forwards; }
        .star-pop  { animation: starPop  1.2s ease forwards; }
      `}</style>

      {/* Ambient background orbs */}
      <div style={{ position:'absolute', inset:0, overflow:'hidden', pointerEvents:'none' }}>
        <div style={{
          position:'absolute', width:520, height:520,
          borderRadius:'50%',
          background:'radial-gradient(circle, rgba(139,92,246,0.18) 0%, transparent 70%)',
          top:'-140px', left:'-140px',
          animation:'orbFloat 8s ease-in-out infinite',
        }} />
        <div style={{
          position:'absolute', width:400, height:400,
          borderRadius:'50%',
          background:'radial-gradient(circle, rgba(99,102,241,0.14) 0%, transparent 70%)',
          bottom:'-100px', right:'-80px',
          animation:'orbFloat 10s ease-in-out 2s infinite reverse',
        }} />
        <div style={{
          position:'absolute', width:260, height:260,
          borderRadius:'50%',
          background:'radial-gradient(circle, rgba(167,139,250,0.12) 0%, transparent 70%)',
          top:'55%', left:'60%',
          animation:'orbFloat 7s ease-in-out 1s infinite',
        }} />
      </div>

      {/* Trail dots during flight */}
      {phase === 3 && <TrailDots />}

      {/* ── PHASES 0-4: Mascot ── */}
      {phase < 5 && (
        <div
          className={
            phase <= 1 ? 'mascot-idle' + (phase === 1 ? ' mascot-wink' : '') :
            phase === 2 ? 'mascot-fold' :
            phase === 3 ? 'mascot-fly' :
            'mascot-land'
          }
          style={{
            position: phase === 3 ? 'fixed' : 'relative',
            left:      phase === 3 ? '50%' : undefined,
            top:       phase === 3 ? '50%' : undefined,
            zIndex: 10,
          }}
        >
          <MascotSVG phase={phase} />
        </div>
      )}

      {/* ── PHASE 5: Logo reveal ── */}
      {phase === 5 && (
        <div style={{ textAlign:'center', zIndex:10 }}>
          {/* Mascot still visible small at top */}
          <div className="logo-reveal" style={{ marginBottom:24 }}>
            <MascotSVG phase={4} small />
          </div>

          {/* Logo */}
          <div className="logo-reveal" style={{ marginBottom:12 }}>
            <span style={{
              fontSize: 52, fontWeight: 900, letterSpacing: '-2px',
              color: '#1A1032',
              fontFamily: "'Inter', sans-serif",
            }}>
              Hire<span style={{
                background: 'linear-gradient(135deg, #7C3AED, #4F46E5)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}>Me</span>Maybe<span style={{ color:'#7C3AED' }}>?</span>
            </span>
          </div>

          {/* Tagline */}
          <p className="tag-reveal" style={{
            fontSize: 18, color: '#6B7280', fontWeight: 500,
            marginBottom: 10, letterSpacing: '0.01em',
          }}>
            Maybe? <span style={{ color:'#7C3AED', fontWeight:700 }}>Let's Fix That.</span> 💜
          </p>
          <p className="tag-reveal" style={{
            fontSize: 14, color: '#9CA3AF', marginBottom: 40,
          }}>
            Crunching keywords · Boosting confidence · Getting you closer to{' '}
            <span style={{ color:'#7C3AED', fontWeight:600 }}>"YOU'RE HIRED!"</span>
          </p>

          {/* Progress bar */}
          <div className="btn-reveal" style={{ width:320, maxWidth:'80vw', margin:'0 auto 32px' }}>
            <div style={{
              height: 6, borderRadius: 999,
              background: 'rgba(124,58,237,0.15)',
              overflow: 'hidden',
            }}>
              <div style={{
                height:'100%', borderRadius:999,
                background: 'linear-gradient(90deg, #7C3AED, #4F46E5, #7C3AED)',
                backgroundSize: '200% 100%',
                animation: 'progressGrow 1.8s ease forwards, shimmer 2s linear infinite',
              }} />
            </div>
          </div>
        </div>
      )}

      {/* ── PHASES 0-4: Caption ── */}
      {phase < 5 && (
        <div style={{
          marginTop: 40, textAlign:'center',
          opacity: phase >= 3 ? 0 : 1,
          transition: 'opacity 0.5s',
        }}>
          <p style={{ fontSize:15, color:'#7C3AED', fontWeight:600, marginBottom:4 }}>
            {phase <= 1 ? 'Making your next opportunity happen.' :
             phase === 2 ? 'Folding your future…' :
             'Flying towards your dream job! ✈️'}
          </p>
          {phase <= 1 && (
            <p style={{ fontSize:13, color:'#9CA3AF' }}>
              HireMeMaybe is loading
              <Dots />
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// ── Mascot SVG ────────────────────────────────────────────────────────────────

function MascotSVG({ phase, small = false }) {
  const size = small ? 72 : 140;
  const isFlying = phase === 3;
  const isFolding = phase === 2;

  if (isFlying || isFolding) {
    // Paper airplane shape
    return (
      <svg width={size} height={size} viewBox="0 0 100 100" fill="none">
        {/* Airplane body */}
        <polygon points="10,50 90,20 70,50 90,80" fill="#7C3AED" opacity="0.9"/>
        <polygon points="10,50 70,50 50,70"        fill="#4F46E5" opacity="0.85"/>
        <polygon points="70,50 90,20 80,52"        fill="#A78BFA" opacity="0.7"/>
        {/* Sparkle on nose */}
        <circle cx="88" cy="22" r="3" fill="#FCD34D" opacity="0.9"/>
        <line x1="88" y1="16" x2="88" y2="12" stroke="#FCD34D" strokeWidth="1.5" strokeLinecap="round"/>
        <line x1="82" y1="22" x2="78" y2="22" stroke="#FCD34D" strokeWidth="1.5" strokeLinecap="round"/>
        <line x1="84" y1="17" x2="81" y2="14" stroke="#FCD34D" strokeWidth="1.5" strokeLinecap="round"/>
      </svg>
    );
  }

  // Document mascot (default / landing)
  return (
    <svg width={size} height={size} viewBox="0 0 120 140" fill="none">
      {/* Shadow */}
      <ellipse cx="60" cy="134" rx="38" ry="6" fill="rgba(124,58,237,0.12)"/>

      {/* Document body */}
      <rect x="16" y="8" width="88" height="112" rx="14" fill="white"
        stroke="#E9D5FF" strokeWidth="2"/>
      {/* Folded corner */}
      <path d="M84 8 L104 28 L84 28 Z" fill="#EDE9FE"/>
      <path d="M84 8 L104 28" stroke="#DDD6FE" strokeWidth="1.5"/>

      {/* Lines on document */}
      <rect x="28" y="42" width="44" height="5" rx="2.5" fill="#DDD6FE" opacity="0.8"/>
      <rect x="28" y="54" width="60" height="4" rx="2" fill="#EDE9FE" opacity="0.9"/>
      <rect x="28" y="64" width="52" height="4" rx="2" fill="#EDE9FE" opacity="0.9"/>
      <rect x="28" y="74" width="58" height="4" rx="2" fill="#EDE9FE" opacity="0.9"/>
      <rect x="28" y="84" width="40" height="4" rx="2" fill="#EDE9FE" opacity="0.7"/>

      {/* Face */}
      {/* Left eye */}
      <ellipse
        cx="44" cy="28" rx="5" ry="5.5"
        fill="#1A1032"
        className={phase === 1 ? 'eye-left' : undefined}
        style={phase === 1 ? { transformOrigin:'44px 28px' } : undefined}
      />
      <circle cx="46" cy="26" r="1.5" fill="white" opacity="0.7"/>

      {/* Right eye — winks */}
      {phase === 1 ? (
        <path d="M58 25 Q63 22 68 25" stroke="#1A1032" strokeWidth="2.5" strokeLinecap="round" fill="none"
          className="eye-right" style={{ transformOrigin:'63px 25px' }}/>
      ) : (
        <ellipse cx="63" cy="28" rx="5" ry="5.5" fill="#1A1032"/>
      )}
      {phase !== 1 && <circle cx="65" cy="26" r="1.5" fill="white" opacity="0.7"/>}

      {/* Smile */}
      <path d="M46 36 Q54 43 66 36" stroke="#7C3AED" strokeWidth="2.5"
        strokeLinecap="round" fill="none"/>

      {/* Rosy cheeks */}
      <circle cx="38" cy="33" r="5" fill="#FCA5A5" opacity="0.35"/>
      <circle cx="74" cy="33" r="5" fill="#FCA5A5" opacity="0.35"/>

      {/* Stars / sparkles around doc */}
      <text x="6"  y="24" fontSize="12" opacity="0.7">✦</text>
      <text x="98" y="18" fontSize="10" opacity="0.6">✦</text>
      <text x="2"  y="90" fontSize="9"  opacity="0.5">·</text>
    </svg>
  );
}

// ── Trail dots that follow the airplane ───────────────────────────────────────

const TRAIL_POSITIONS = [
  { x:'50%', y:'50%', delay:0 },
  { x:'65%', y:'34%', delay:0.5 },
  { x:'80%', y:'26%', delay:1.1 },
  { x:'88%', y:'50%', delay:1.9 },
  { x:'75%', y:'68%', delay:2.8 },
  { x:'40%', y:'74%', delay:3.7 },
  { x:'18%', y:'62%', delay:4.5 },
  { x:'10%', y:'38%', delay:5.3 },
  { x:'28%', y:'22%', delay:5.9 },
];

const COLORS = ['#7C3AED','#A78BFA','#4F46E5','#C4B5FD','#6D28D9'];

function TrailDots() {
  return (
    <>
      {TRAIL_POSITIONS.map((pos, i) => (
        <div key={i} className="trail-dot" style={{
          position: 'fixed',
          left: pos.x, top: pos.y,
          transform: 'translate(-50%,-50%)',
          animationDelay: `${pos.delay}s`,
          zIndex: 8,
          display: 'flex', gap: 6,
        }}>
          {[0,1,2].map(j => (
            <div key={j} style={{
              width:  8 - j * 2,
              height: 8 - j * 2,
              borderRadius: '50%',
              background: COLORS[(i + j) % COLORS.length],
              opacity: 1 - j * 0.25,
              animationDelay: `${pos.delay + j * 0.08}s`,
            }} className="trail-dot" />
          ))}
        </div>
      ))}
      {/* Star pops */}
      {TRAIL_POSITIONS.filter((_,i) => i % 2 === 0).map((pos, i) => (
        <div key={`star-${i}`} className="star-pop" style={{
          position: 'fixed',
          left: `calc(${pos.x} + 24px)`,
          top:  `calc(${pos.y} - 20px)`,
          fontSize: 14,
          zIndex: 9,
          animationDelay: `${pos.delay + 0.15}s`,
        }}>
          {['✨','💜','⭐','✦'][i % 4]}
        </div>
      ))}
    </>
  );
}

// ── Animated dots ─────────────────────────────────────────────────────────────

function Dots() {
  const [n, setN] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setN(x => (x + 1) % 4), 500);
    return () => clearInterval(t);
  }, []);
  return <span>{'...'.slice(0, n)}</span>;
}
