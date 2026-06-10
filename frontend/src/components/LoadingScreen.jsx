import { useEffect, useState } from 'react';

const STEPS = [
  { icon: '📄', text: 'Parsing your resume...' },
  { icon: '🔍', text: 'Analyzing job description...' },
  { icon: '⚙️', text: 'Running ATS compatibility check...' },
  { icon: '🧠', text: 'Computing semantic similarity...' },
  { icon: '📊', text: 'Calculating interview probability...' },
  { icon: '✨', text: 'Compiling your intelligence report...' },
];

const REWRITE_STEPS = [
  { icon: '🔬', text: 'Identifying optimization opportunities...' },
  { icon: '✍️', text: 'Rewriting with AI precision...' },
  { icon: '📈', text: 'Evaluating ATS score improvement...' },
  { icon: '🔄', text: 'Running optimization loop...' },
  { icon: '🛡️', text: 'Verifying factual accuracy...' },
  { icon: '✅', text: 'Finalizing your optimized resume...' },
];

export default function LoadingScreen({ message = 'Analyzing', rewrite = false }) {
  const steps = rewrite ? REWRITE_STEPS : STEPS;
  const [step, setStep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setStep(s => (s + 1) % steps.length), rewrite ? 2200 : 1600);
    return () => clearInterval(interval);
  }, [steps.length, rewrite]);

  useEffect(() => {
    const t = setInterval(() => setProgress(p => Math.min(p + (rewrite ? 0.4 : 0.6), 92)), 80);
    return () => clearInterval(t);
  }, [rewrite]);

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg)', padding: 40,
      fontFamily: "'Inter', system-ui, sans-serif",
    }}>
      <style>{`
        @keyframes ls-float  { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
        @keyframes ls-blob   { 0%,100%{border-radius:60% 40% 70% 30%/60% 30% 70% 40%} 50%{border-radius:30% 60% 40% 70%/40% 70% 30% 60%} }
        @keyframes ls-bounce { 0%,80%,100%{transform:scale(0.6);opacity:0.35} 40%{transform:scale(1);opacity:1} }
        @keyframes ls-shine  { 0%{background-position:-200% center} 100%{background-position:200% center} }
      `}</style>

      <div style={{ position: 'relative', marginBottom: 40 }}>
        <div style={{
          width: 110, height: 110, borderRadius: '50%',
          background: 'linear-gradient(135deg, rgba(124,58,237,0.18), rgba(79,70,229,0.12))',
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%,-50%)',
          animation: 'ls-blob 3s ease-in-out infinite', filter: 'blur(16px)',
        }} />
        <div style={{
          width: 76, height: 76, borderRadius: '50%',
          background: 'linear-gradient(135deg, #7C3AED, #4F46E5)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 30, boxShadow: '0 0 32px rgba(124,58,237,0.4)',
          animation: 'ls-float 2.2s ease-in-out infinite', position: 'relative',
        }}>
          {steps[step].icon}
        </div>
      </div>

      <h2 style={{ fontSize: 26, fontWeight: 800, marginBottom: 8, letterSpacing: '-0.5px', color: 'var(--text)' }}>
        {message}
      </h2>
      <p style={{ color: 'var(--text-2)', marginBottom: 36, fontSize: 15, minHeight: 22, textAlign: 'center' }}>
        {steps[step].text}
      </p>

      <div style={{ width: 300, maxWidth: '85vw' }}>
        <div style={{ height: 7, borderRadius: 999, overflow: 'hidden', background: 'var(--purple-dim)' }}>
          <div style={{
            height: '100%', borderRadius: 999,
            background: 'linear-gradient(90deg, #7C3AED, #4F46E5, #7C3AED)',
            backgroundSize: '200% 100%',
            width: `${progress}%`, transition: 'width 0.1s linear',
            animation: 'ls-shine 2s linear infinite',
          }} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
          <span style={{ fontSize: 12, color: 'var(--text-3)' }}>Processing</span>
          <span style={{ fontSize: 12, color: 'var(--purple)', fontWeight: 600 }}>{Math.round(progress)}%</span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 8, marginTop: 36 }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{
            width: 9, height: 9, borderRadius: '50%', background: 'var(--purple)',
            animation: `ls-bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
          }} />
        ))}
      </div>

      <div style={{
        marginTop: 40, maxWidth: 340, textAlign: 'center',
        background: 'rgba(124,58,237,0.07)', border: '1px solid var(--border)',
        borderRadius: 14, padding: '14px 20px',
      }}>
        <span style={{ fontSize: 13, color: 'var(--text-2)' }}>
          {'💡 '}
          <strong style={{ color: 'var(--purple)' }}>Pro tip:</strong>{' '}
          {rewrite
            ? 'Every rewrite is fact-checked against your original resume.'
            : 'Tailoring your resume to each job can 3x your interview rate.'}
        </span>
      </div>
    </div>
  );
}
