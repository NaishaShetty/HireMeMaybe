import { useState } from 'react';
import UploadPage from './pages/UploadPage.jsx';
import AnalysisPage from './pages/AnalysisPage.jsx';
import RewritePage from './pages/RewritePage.jsx';
import InterviewPrepPage from './pages/InterviewPrepPage.jsx';
import CompanyIntelPage from './pages/CompanyIntelPage.jsx';
import LoadingScreen from './components/LoadingScreen.jsx';
import { parseResume, parseJD, getInterviewScore, rewriteResume, getInterviewPrep, getCompanyIntel } from './api.js';

// Steps:
// 'upload' → 'loading-analysis' → 'analysis'
//   → 'loading-rewrite'     → 'rewrite'
//   → 'loading-interview'   → 'interview-prep'
//   → 'company-intel'  (search form + results, no loading screen needed — handled in-page)

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

export default function App() {
  const [step, setStep] = useState('upload');
  const [error, setError] = useState(null);

  // Core data
  const [resumeData, setResumeData]     = useState(null);
  const [jdData,     setJdData]         = useState(null);
  const [resumeText, setResumeText]     = useState('');
  const [jdText,     setJdText]         = useState('');
  const [analysis,   setAnalysis]       = useState(null);
  const [rewrite,    setRewrite]        = useState(null);

  // New feature data
  const [interviewPrep, setInterviewPrep] = useState(null);
  const [companyIntel,  setCompanyIntel]  = useState(null);
  const [companyLoading, setCompanyLoading] = useState(false);

  // ── Step 1 → 2: Upload & Analyze ────────────────────────────────────────
  const handleSubmit = async ({ file, jd }) => {
    setError(null);
    setStep('loading-analysis');
    setJdText(jd);
    try {
      const [parsedResume, parsedJD] = await Promise.all([
        parseResume(file),
        parseJD(jd),
      ]);
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
        jobTitle: parsedJD?.job_title || 'Unknown Role',
        company: parsedJD?.company || '',
        atsScore: Math.round(score.ats_score || 0),
        interviewScore: Math.round(score.interview_probability_score || 0),
        semanticScore: Math.round((score.semantic_similarity || 0) * 100),
        skillScore: Math.round(score.skill_match_score || 0),
        resumeData: resumeJson, jdData: parsedJD,
        resumeText: rawText, jdText: jd, analysis: score,
      });
    } catch (e) {
      setError(`Analysis failed: ${e.message}`);
      setStep('upload');
    }
  };

  // ── Step 2 → 3: Rewrite ─────────────────────────────────────────────────
  const handleRewrite = async ({ resumeData, jdData, resumeText, jdText }) => {
    setError(null);
    setStep('loading-rewrite');
    try {
      const result = await rewriteResume({
        resume: resumeData, jd: jdData,
        resume_text: resumeText, jd_text: jdText,
        max_passes: 2, num_candidates: 3,
      });
      setRewrite(result);
      setStep('rewrite');
    } catch (e) {
      setError(`Rewrite failed: ${e.message}`);
      setStep('analysis');
    }
  };

  // ── Step 2 → Interview Prep ─────────────────────────────────────────────
  const handleInterviewPrep = async () => {
    setError(null);
    setStep('loading-interview');
    try {
      const result = await getInterviewPrep({
        resume_text: resumeText,
        jd_text: jdText,
        matched_skills: analysis?.matched_skills || [],
        missing_skills: analysis?.missing_skills || [],
      });
      setInterviewPrep(result);
      setStep('interview-prep');
    } catch (e) {
      setError(`Interview prep failed: ${e.message}`);
      setStep('analysis');
    }
  };

  // ── Company Intel ────────────────────────────────────────────────────────
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
    setCompanyIntel(null); // clear previous so search form shows
    setStep('company-intel');
  };

  // ── Reset ────────────────────────────────────────────────────────────────
  const handleReset = () => {
    setStep('upload');
    setError(null);
    setResumeData(null); setJdData(null);
    setResumeText(''); setJdText('');
    setAnalysis(null); setRewrite(null);
    setInterviewPrep(null); setCompanyIntel(null);
  };

  const handleRestoreHistory = (entry) => {
    setError(null);
    setResumeData(entry.resumeData);
    setJdData(entry.jdData);
    setResumeText(entry.resumeText);
    setJdText(entry.jdText);
    setAnalysis(entry.analysis);
    setRewrite(null); setInterviewPrep(null); setCompanyIntel(null);
    setStep('analysis');
  };

  return (
    <>
      {/* Global error toast */}
      {error && (
        <div style={{
          position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)',
          background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)',
          borderRadius: 12, padding: '12px 20px', zIndex: 9999,
          display: 'flex', alignItems: 'center', gap: 12, minWidth: 320, maxWidth: '90vw',
          backdropFilter: 'blur(12px)', animation: 'fadeUp 0.3s ease',
        }}>
          <span style={{ color: '#ef4444', fontSize: 18 }}>⚠</span>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 600, fontSize: 14, color: '#ef4444' }}>Something went wrong</div>
            <div style={{ fontSize: 13, color: 'var(--text-2)', marginTop: 2 }}>{error}</div>
          </div>
          <button
            onClick={() => setError(null)}
            style={{ background: 'none', border: 'none', color: 'var(--text-3)', cursor: 'pointer', fontSize: 18, padding: 4 }}
          >×</button>
        </div>
      )}

      {step === 'upload' && (
        <UploadPage
          onSubmit={handleSubmit}
          history={loadHistory()}
          onRestoreHistory={handleRestoreHistory}
        />
      )}

      {step === 'loading-analysis' && (
        <LoadingScreen message="Analyzing Your Resume" rewrite={false} />
      )}

      {step === 'analysis' && analysis && (
        <AnalysisPage
          data={analysis}
          resumeData={resumeData}
          jdData={jdData}
          resumeText={resumeText}
          jdText={jdText}
          onRewrite={handleRewrite}
          onInterviewPrep={handleInterviewPrep}
          onCompanyIntel={handleOpenCompanyIntel}
          onBack={handleReset}
        />
      )}

      {step === 'loading-rewrite' && (
        <LoadingScreen message="Optimizing Your Resume" rewrite={true} />
      )}

      {step === 'rewrite' && rewrite && (
        <RewritePage
          data={rewrite}
          originalText={resumeText}
          onBack={() => setStep('analysis')}
          onNewAnalysis={handleReset}
        />
      )}

      {step === 'loading-interview' && (
        <LoadingScreen message="Generating Interview Questions" rewrite={false} />
      )}

      {step === 'interview-prep' && interviewPrep && (
        <InterviewPrepPage
          data={interviewPrep}
          jdData={jdData}
          onBack={() => setStep('analysis')}
        />
      )}

      {step === 'company-intel' && (
        <CompanyIntelPage
          data={companyIntel}
          defaultCompany={jdData?.company || ''}
          defaultRole={jdData?.job_title || 'Software Engineer'}
          onSearch={handleCompanyIntel}
          loading={companyLoading}
          onBack={() => setStep(analysis ? 'analysis' : 'upload')}
        />
      )}
    </>
  );
}
