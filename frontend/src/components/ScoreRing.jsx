import { useEffect, useRef, useState } from 'react';

const colorForScore = (score, custom) => {
  if (custom) return custom;
  if (score >= 75) return '#10b981';
  if (score >= 50) return '#f59e0b';
  return '#ef4444';
};

export default function ScoreRing({ score = 0, label, sublabel, size = 140, color, animate = true }) {
  const r = 44;
  const circ = 2 * Math.PI * r;
  const [displayed, setDisplayed] = useState(animate ? 0 : score);
  const raf = useRef(null);

  useEffect(() => {
    if (!animate) { setDisplayed(score); return; }
    const start = performance.now();
    const duration = 1400;
    const ease = (t) => t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    const tick = (now) => {
      const t = Math.min((now - start) / duration, 1);
      setDisplayed(Math.round(ease(t) * score));
      if (t < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf.current);
  }, [score, animate]);

  const c = colorForScore(score, color);
  const offset = circ * (1 - displayed / 100);

  return (
    <div style={{ textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
      <div style={{ position: 'relative', width: size, height: size }}>
        <svg viewBox="0 0 100 100" width={size} height={size} style={{ overflow: 'visible' }}>
          {/* Glow */}
          <circle cx="50" cy="50" r={r} fill="none"
            stroke={c} strokeWidth="10"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%', opacity: 0.15, filter: `blur(6px)` }}
          />
          {/* Track */}
          <circle cx="50" cy="50" r={r} fill="none"
            stroke="rgba(255,255,255,0.07)" strokeWidth="7"
          />
          {/* Fill */}
          <circle cx="50" cy="50" r={r} fill="none"
            stroke={c} strokeWidth="7"
            strokeDasharray={circ}
            strokeDashoffset={circ * (1 - displayed / 100)}
            strokeLinecap="round"
            style={{
              transform: 'rotate(-90deg)',
              transformOrigin: '50% 50%',
              transition: animate ? 'none' : undefined,
              filter: `drop-shadow(0 0 6px ${c}99)`,
            }}
          />
        </svg>
        <div style={{
          position: 'absolute', inset: 0,
          display: 'flex', flexDirection: 'column',
          alignItems: 'center', justifyContent: 'center',
        }}>
          <span style={{ fontSize: size * 0.22, fontWeight: 800, lineHeight: 1, color: c, letterSpacing: '-1px' }}>
            {displayed}
          </span>
          {sublabel && (
            <span style={{ fontSize: 10, color: 'var(--text-3)', fontWeight: 500, marginTop: 2 }}>{sublabel}</span>
          )}
        </div>
      </div>
      {label && (
        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-2)', letterSpacing: '0.02em' }}>{label}</span>
      )}
    </div>
  );
}
