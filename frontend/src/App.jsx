import { useState, useCallback } from 'react';
import ErrorBoundary from './components/ErrorBoundary.jsx';

import UploadPage        from './pages/UploadPage.jsx';
import AnalysisPage      from './pages/AnalysisPage.jsx';
import RewritePage       from './pages/RewritePage.jsx';
import InterviewPrepPage from './pages/InterviewPrepPage.jsx';
import CompanyIntelPage  from './pages/CompanyIntelPage.jsx';
import CoverLetterPage   from './pages/CoverLetterPage.jsx';
import HistoryPage       from './pages/HistoryPage.jsx';
import AuthPage          from './pages/AuthPage.jsx';
import LoadingScreen     from './components/LoadingScreen.jsx';
import SplashScreen      from './components/SplashScreen.jsx';
import PaywallModal      from './components/PaywallModal.jsx';

import { AuthProvider, useAuth }         from './context/AuthContext.jsx';
import { useSubscription, PRO_FEATURES } from './hooks/useSubscription.js';

import {
  parseResume, parseJD, getInterviewScore,
  rewriteResume, getInterviewPrep, getCompanyIntel,
  generateCoverLetter,
} from './api.js';

// ── localStorage history ─────────────────────────────────────────────────────

const HISTORY_KEY = 'hmm_analysis_history';
const MAX_HISTORY = 10;

function loadHistory() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); }
  catch { return []; }
}

function saveToHistory(entry) {
  const history = loadHistory();
  history.unshift({ id: Date.now(), savedAt: new Date().toISOString(), ...entry });
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, MAX_HISTORY)));
}

// ── Tiny header with user account status ────────────────────────────────────

function AccountBadge({ onShowAuth, onSignOut, onShowHistory, compact = false }) {
  const { isAuthenticated, user, isPro, isLoading } = useAuth();
  const [open, setOpen] = useState(false);

  if (isLoading) return null;

  if (compact) {
    return (
      <button
        className="sidebar-nav-item"
        onClick={isAuthenticated ? () => setOpen(o => !o) : onShowAuth}
        style={{ width:'100%', position:'relative' }}
      >
        <span style={{ fontSize:16 }}>
          {isAuthenticated ? (isPro ? '✦' : '👤') : '🔑'}
        </span>
        {isAuthenticated ? (user?.email?.split('@')[0] ?? 'Account') : 'Sign in'}
        {open && isAuthenticated && (
          <div style={{
            position:'absolute', bottom:'100%', left:0, width:'100%',
            background:'var(--card)', border:'1px solid var(--border)',
            borderRadius:12, padding:8, zIndex:600,
            boxShadow:'var(--shadow-md)',
          }}>
            <button onClick={onSignOut} style={{
              width:'100%', padding:'8px 10px', border:'none', background:'none',
              color:'var(--red)', fontSize:13, cursor:'pointer', textAlign:'left', borderRadius:8,
              fontFamily:'inherit',
            }}>Sign out</button>
          </div>
        )}
      </button>
    );
  }

  return (
    <div style={{ position:'fixed', top:16, right:20, zIndex:500, display:'flex', gap:8, alignItems:'center' }}>
      <button
        className="btn-ghost"
        onClick={onShowHistory}
        style={{ padding:'6px 12px', fontSize:12, display:'flex', alignItems:'center', gap:6 }}
        title="View analysis history"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.5"/>
        </svg>
        <span className="account-badge-history-label">History</span>
      </button>

      {isAuthenticated ? (
        <div style={{ position:'relative' }}>
          <button
            onClick={() => setOpen(o => !o)}
            style={{
              display:'flex', alignItems:'center', gap:8, padding:'6px 12px',
              borderRadius:10, border:'1px solid var(--border)',
              background:'var(--card)', cursor:'pointer', fontSize:12, color:'var(--text-2)',
              transition:'border-color 0.2s',
            }}
            onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--border-bright)'}
            onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
          >
            <div style={{
              width:20, height:20, borderRadius:6,
              background: isPro ? 'var(--grad)' : 'var(--purple-dim)',
              display:'flex', alignItems:'center', justifyContent:'center',
              fontSize:9, fontWeight:800, color: isPro ? '#fff' : 'var(--purple)',
            }}>
              {isPro ? '✦' : user?.email?.[0]?.toUpperCase() ?? 'U'}
            </div>
            <span className="account-email-label" style={{ maxWidth:120, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
              {user?.email}
            </span>
            {isPro && (
              <span style={{
                padding:'1px 6px', borderRadius:20, fontSize:10, fontWeight:700,
                background:'var(--grad)', color:'#fff',
              }}>PRO</span>
            )}
          </button>

          {open && (
            <div
              style={{
                position:'absolute', top:'calc(100% + 6px)', right:0, minWidth:180,
                background:'var(--card)', border:'1px solid var(--border)', borderRadius:12,
                padding:8, zIndex:600, boxShadow:'var(--shadow-lg)',
              }}
              onMouseLeave={() => setOpen(false)}
            >
              <div style={{ padding:'6px 10px', fontSize:11, color:'var(--text-3)', marginBottom:4 }}>
                {isPro ? '✦ Pro plan' : 'Free plan'}
              </div>
              {!isPro && (
                <button
                  onClick={() => { setOpen(false); alert('Billing integration coming soon!'); }}
                  style={{
                    width:'100%', textAlign:'left', padding:'8px 10px', borderRadius:8,
                    background:'var(--purple-dim)', border:'none', color:'var(--purple)',
                    fontSize:13, fontWeight:600, cursor:'pointer', marginBottom:4, fontFamily:'inherit',
                  }}
                >
                  ✦ Upgrade to Pro
                </button>
              )}
              <button
                onClick={() => { setOpen(false); onSignOut(); }}
                style={{
                  width:'100%', textAlign:'left', padding:'8px 10px', borderRadius:8,
                  background:'none', border:'none', color:'var(--text-2)',
                  fontSize:13, cursor:'pointer', fontFamily:'inherit',
                }}
                onMouseEnter={e => e.currentTarget.style.background = 'var(--card-hover)'}
                onMouseLeave={e => e.currentTarget.style.background = 'none'}
              >
                Sign out
              </button>
            </div>
          )}
        </div>
      ) : (
        <button
          className="btn-ghost"
          onClick={onShowAuth}
          style={{ padding:'6px 14px', fontSize:12, fontWeight:600 }}
        >
          Sign in
        </button>
      )}
    </div>
  );
}

// ── Main app inner (needs AuthContext) ───────────────────────────────────────

function AppInner() {
  const { signOut, isAuthenticated }   = useAuth();
  const { canAccess, featureLabel }    = useSubscription();

  const [step,  setStep]  = useState('upload');
  const [error, setError] = useState(null);

  const [resumeData,    setResumeData]    = useState(null);
  const [jdData,        setJdData]        = useState(null);
  const [resumeText,    setResumeText]    = useState('');
  const [jdText,        setJdText]        = useState('');
  const [analysis,      setAnalysis]      = useState(null);
  const [rewrite,       setRewrite]       = useState(null);
  const [interviewPrep, setInterviewPrep] = useState(null);
  const [companyIntel,  setCompanyIntel]  = useState(null);
  const [coverLetter,   setCoverLetter]   = useState(null);
  const [companyLoading, setCompanyLoading] = useState(false);

  const [paywallFeature, setPaywallFeature] = useState(null);

  // ── Paywall guard ──────────────────────────────────────────────────────────
  const withPaywall = useCallback((featureKey, action) => {
    if (canAccess(featureKey)) {
      action();
    } else {
      setPaywallFeature(featureKey);
    }
  }, [canAccess]);

  // ── Step 1 → 2: Upload & Analyze ─────────────────────────────────────────
  const handleSubmit = async ({ file, jd }) => {
    setError(null);
    setStep('loading-analysis');
    setJdText(jd);
    try {
      const [parsedResume, parsedJD] = await Promise.all([parseResume(file), parseJD(jd)]);
      const rawText = parsedResume.resume_text || '';
      const { resume_text: _rt, ...resumeJson } = parsedResume;
      setResumeData(resumeJson);
      setResumeText(rawText);
      setJdData(parsedJD);

      const score = await getInterviewScore({
        resume: resumeJson, jd: parsedJD,
        resume_text: rawText, jd_text: jd,
      });
      setAnalysis(score);
      setStep('analysis');

      saveToHistory({
        jobTitle:       parsedJD?.job_title || 'Unknown Role',
        company:        parsedJD?.company || '',
        atsScore:       Math.round(score.ats_score || 0),
        interviewScore: Math.round(score.interview_probability_score || 0),
        semanticScore:  Math.round((score.semantic_similarity || 0) * 100),
        skillScore:     Math.round(score.skill_match_score || 0),
        resumeData: resumeJson, jdData: parsedJD,
        resumeText: rawText, jdText: jd, analysis: score,
      });
    } catch (e) {
      setError(`Analysis failed: ${e.message}`);
      setStep('upload');
    }
  };

  // ── Step 2 → 3: Rewrite (Pro) ─────────────────────────────────────────────
  const handleRewrite = ({ resumeData: rd, jdData: jd, resumeText: rt, jdText: jt }) => {
    withPaywall(PRO_FEATURES.REWRITE.key, async () => {
      setError(null);
      setStep('loading-rewrite');
      try {
        const result = await rewriteResume({
          resume: rd, jd, resume_text: rt, jd_text: jt,
          max_passes: 2, num_candidates: 3,
        });
        setRewrite(result);
        setStep('rewrite');
      } catch (e) {
        setError(`Rewrite failed: ${e.message}`);
        setStep('analysis');
      }
    });
  };

  // ── Step 2 → Interview Prep (Pro) ─────────────────────────────────────────
  const handleInterviewPrep = () => {
    withPaywall(PRO_FEATURES.INTERVIEW_PREP.key, async () => {
      setError(null);
      setStep('loading-interview');
      try {
        const result = await getInterviewPrep({
          resume_text: resumeText, jd_text: jdText,
          matched_skills: analysis?.matched_skills || [],
          missing_skills: analysis?.missing_skills || [],
        });
        setInterviewPrep(result);
        setStep('interview-prep');
      } catch (e) {
        setError(`Interview prep failed: ${e.message}`);
        setStep('analysis');
      }
    });
  };

  // ── Cover Letter (free) ───────────────────────────────────────────────────
  const handleCoverLetter = async () => {
    setError(null);
    setStep('loading-cover');
    try {
      const result = await generateCoverLetter({
        resume_text: resumeText,
        jd_text:     jdText,
        role:        jdData?.job_title || 'the role',
        company:     jdData?.company   || 'your company',
      });
      setCoverLetter(result);
      setStep('cover-letter');
    } catch (e) {
      setError(`Cover letter failed: ${e.message}`);
      setStep('analysis');
    }
  };

  // ── Company Intel (Pro) ───────────────────────────────────────────────────
  const handleCompanyIntel = async ({ company, role }) => {
    setError(null);
    setCompanyLoading(true);
    try {
      const result = await getCompanyIntel({ company, role });
      setCompanyIntel(result);
    } catch (e) {
      setError(`Company intel failed: ${e.message}`);
    } finally {
      setCompanyLoading(false);
    }
  };

  const handleOpenCompanyIntel = () => {
    withPaywall(PRO_FEATURES.COMPANY_INTEL.key, () => {
      setCompanyIntel(null);
      setStep('company-intel');
    });
  };

  // ── Reset ──────────────────────────────────────────────────────────────────
  const handleReset = () => {
    setStep('upload');
    setError(null);
    setResumeData(null); setJdData(null);
    setResumeText(''); setJdText('');
    setAnalysis(null); setRewrite(null);
    setInterviewPrep(null); setCompanyIntel(null); setCoverLetter(null);
  };

  const handleRestoreHistory = (entry) => {
    setError(null);
    setResumeData(entry.resumeData);
    setJdData(entry.jdData);
    setResumeText(entry.resumeText);
    setJdText(entry.jdText);
    setAnalysis(entry.analysis);
    setRewrite(null); setInterviewPrep(null); setCompanyIntel(null); setCoverLetter(null);
    setStep('analysis');
  };

  const showSidebar = step !== 'auth';

  return (
    <div className={showSidebar ? 'app-layout' : ''}>

      {/* ── Sidebar nav ── */}
      {showSidebar && (
        <nav className="sidebar">
          <div className="sidebar-logo">
            <div style={{ fontSize:20, fontWeight:900, letterSpacing:'-0.5px', color:'var(--text)' }}>
              Hire<span style={{
                background:'var(--grad)', WebkitBackgroundClip:'text',
                WebkitTextFillColor:'transparent', backgroundClip:'text',
              }}>Me</span>Maybe<span style={{ color:'var(--purple)' }}>?</span>
            </div>
          </div>

          {[
            { icon:'🏠', label:'Home',      key:'upload' },
            { icon:'📄', label:'Resumes',   key:'upload' },
            { icon:'💼', label:'Jobs',      key:'company-intel' },
            { icon:'💡', label:'Resources', key:'history' },
          ].map(({ icon, label, key }) => (
            <button
              key={label}
              className={`sidebar-nav-item${step === key && label !== 'Jobs' && label !== 'Resources' ? ' active' : ''}`}
              onClick={() => setStep(key)}
            >
              <span style={{ fontSize:18, lineHeight:1 }}>{icon}</span>
              {label}
            </button>
          ))}

          <div style={{ marginTop:'auto', padding:'0 10px', borderTop:'1px solid var(--border)', paddingTop:16 }}>
            <button
              className="sidebar-nav-item"
              onClick={() => setStep('history')}
              style={{ width:'100%' }}
            >
              <span style={{ fontSize:16 }}>🕐</span> History
            </button>
            <AccountBadge
              onShowAuth={() => setStep('auth')}
              onSignOut={signOut}
              onShowHistory={() => setStep('history')}
              compact
            />
          </div>
        </nav>
      )}

      {/* ── Main content area ── */}
      <div className={showSidebar ? 'main-content' : ''}>

        {/* Account badge (only when no sidebar) */}
        {!showSidebar && (
          <AccountBadge
            onShowAuth={() => setStep('auth')}
            onSignOut={signOut}
            onShowHistory={() => setStep('history')}
          />
        )}

        {/* Global error toast */}
        {error && (
          <div style={{
            position:'fixed', bottom:24, left:'50%', transform:'translateX(-50%)',
            background:'rgba(239,68,68,0.10)', border:'1px solid rgba(239,68,68,0.25)',
            borderRadius:12, padding:'12px 20px', zIndex:9999,
            display:'flex', alignItems:'center', gap:12, minWidth:320, maxWidth:'90vw',
            animation:'fadeUp 0.3s ease',
          }}>
            <span style={{ color:'#ef4444', fontSize:18 }}>⚠</span>
            <div style={{ flex:1 }}>
              <div style={{ fontWeight:600, fontSize:14, color:'#ef4444' }}>Something went wrong</div>
              <div style={{ fontSize:13, color:'var(--text-2)', marginTop:2 }}>{error}</div>
            </div>
            <button
              onClick={() => setError(null)}
              style={{
                border:'none', background:'none', cursor:'pointer',
                color:'var(--text-3)', fontSize:18, lineHeight:1, padding:4,
              }}
            >✕</button>
          </div>
        )}

        {/* Paywall modal */}
        {paywallFeature && (
          <PaywallModal
            feature={featureLabel(paywallFeature)}
            onClose={() => setPaywallFeature(null)}
            onSignIn={() => { setPaywallFeature(null); setStep('auth'); }}
          />
        )}

        {/* ── Pages ── */}
        <ErrorBoundary>
          {step === 'auth' && (
            <AuthPage onSkip={() => setStep('upload')} />
          )}

          {step === 'history' && (
            <HistoryPage
              history={loadHistory()}
              onRestore={handleRestoreHistory}
              onBack={() => setStep('upload')}
            />
          )}

          {step === 'upload' && (
            <UploadPage onSubmit={handleSubmit} />
          )}

          {step === 'loading-analysis' && (
            <LoadingScreen message="Analyzing your resume" rewrite={false} />
          )}

          {step === 'analysis' && analysis && (
            <AnalysisPage
              analysis={analysis}
              resumeData={resumeData}
              jdData={jdData}
              resumeText={resumeText}
              jdText={jdText}
              onRewrite={handleRewrite}
              onInterviewPrep={handleInterviewPrep}
              onCoverLetter={handleCoverLetter}
              onCompanyIntel={handleOpenCompanyIntel}
              onReset={handleReset}
            />
          )}

          {step === 'loading-rewrite' && (
            <LoadingScreen message="Rewriting your resume" rewrite={true} />
          )}

          {step === 'rewrite' && rewrite && (
            <RewritePage
              result={rewrite}
              onBack={() => setStep('analysis')}
              onReset={handleReset}
            />
          )}

          {step === 'loading-interview' && (
            <LoadingScreen message="Preparing interview questions" rewrite={false} />
          )}

          {step === 'interview-prep' && interviewPrep && (
            <InterviewPrepPage
              result={interviewPrep}
              jdData={jdData}
              onBack={() => setStep('analysis')}
              onReset={handleReset}
            />
          )}

          {step === 'loading-cover' && (
            <LoadingScreen message="Writing your cover letter" rewrite={false} />
          )}

          {step === 'cover-letter' && coverLetter && (
            <CoverLetterPage
              result={coverLetter}
              jdData={jdData}
              onBack={() => setStep('analysis')}
              onReset={handleReset}
            />
          )}

          {step === 'company-intel' && (
            <CompanyIntelPage
              result={companyIntel}
              loading={companyLoading}
              jdData={jdData}
              onFetch={handleCompanyIntel}
              onBack={() => setStep('analysis')}
              onReset={handleReset}
            />
          )}
        </ErrorBoundary>

      </div>
    </div>
  );
}

// ── Splash wrapper ───────────────────────────────────────────────────────────

function AppWithSplash() {
  const [splashDone, setSplashDone] = useState(
    () => sessionStorage.getItem('hmm_splashed') === '1'
  );

  const handleSplashDone = () => {
    sessionStorage.setItem('hmm_splashed', '1');
    setSplashDone(true);
  };

  if (!splashDone) {
    return <SplashScreen onDone={handleSplashDone} />;
  }

  return (
    <AuthProvider>
      <AppInner />
    </AuthProvider>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AppWithSplash />
    </ErrorBoundary>
  );
}
