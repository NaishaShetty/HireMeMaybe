import { useEffect, useState } from 'react';

const STEPS = [
  { icon: '📄', text: 'Parsing your resume…' },
  { icon: '🔍', text: 'Analyzing job description…' },
  { icon: '⚙️',  text: 'Running ATS compatibility check…' },
  { icon: '🧠', text: 'Computing semantic similarity…' },
  { icon: '📊', text: 'Calculating interview probability…' },
  { icon: '✨', text: 'Compiling your intelligence report…' },
];

const REWRITE_STEPS = [
  { icon: '🔬', text: 'Identifying optimization opportunities…' },
  { icon: '✍️',  text: 'Rewriting with AI precision…' },
  { icon: '📈', text: 'Evaluating ATS score improvement…' },
  { icon: '🔄', text: 'Running optimization loop…' },
  { icon: '✅', text: 'Finalizing your optimized resume…' },
];

export default function LoadingScreen({ message = 'Analyzing', rewrite = false }) {
  const steps = rewrite ? REWRITE_STEPS : STEPS;
  const [step, setStep] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStep(s => (s + 1) % steps.length);
    }, rewrite ? 2200 : 1600);
    return () => clearInterval(interval);
  }, [steps.length, rewrite]);

  useEffect(() => {
    const t = setInterval(() => {
      setProgress(p => Math.min(p + (rewrite ? 0.4 : 0.6), 92));
    }, 80);
    return () => clearInterval(t);
  }, [rewrite]);

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      background: 'var(--bg)',
      padding: 40,
      animation: 'fadeIn 0.4s ease',
    }}>
      {/* Orb */}
      <div style={{ position: 'relative', marginBottom: 48 }}>
        <div style={{
          width: 120, height: 120,
          borderRadius: '50%',
          background: 'var(--grad)',
          opacity: 0.15,
          position: 'absolute',
          top: '50%', left: '50%',
          transform: 'translate(-50%,-50%)',
          animation: 'blob 3s ease-in-out infinite',
          filter: 'blur(20px)',
        }} />
        <div style={{
          width: 80, height: 80, borderRadius: '50%',
          background: 'var(--grad)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 32,
          boxShadow: '0 0 40px rgba(139,92,246,0.5)',
          animation: 'float 2s ease-in-out infinite',
          position: 'relative',
        }}>
          {steps[step].icon}
        </div>
      </div>

      {/* Heading */}
      <h2 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8, letterSpacing: '-0.5px' }}>
        {message}
      </h2>
      <p style={{ color: 'var(--text-2)', marginBottom: 40, fontSize: 15, minHeight: 22, transition: 'opacity 0.3s', textAlign:'center' }}>
        {steps[step].text}
      </p>

      {/* Progress bar */}
      <div style={{ width: 320, maxWidth: '90vw' }}>
        <div className="progress-track">
          <div className="progress-fill" style={{
            width: `${progress}%`,
            background: 'var(--grad)',
            transition: 'width 0.1s linear',
          }} />
        </div>
        <div style={{ display:'flex', justifyContent:'space-between', marginTop:8 }}>
          <span style={{ fontSize:12, color:'var(--text-3)' }}>Processing</span>
          <span style={{ fontSize:12, color:'var(--text-3)' }}>{Math.round(progress)}%</span>
        </div>
      </div>

      {/* Dots */}
      <div style={{ display:'flex', gap:8, marginTop:40 }}>
        {[0,1,2].map(i => (
          <div key={i} style={{
            width:8, height:8, borderRadius:'50%',
            background:'var(--purple)',
            animation:`dot-bounce 1.2s ease-in-out ${i*0.2}s infinite`,
          }} />
        ))}
      </div>
    </div>
  );
}
