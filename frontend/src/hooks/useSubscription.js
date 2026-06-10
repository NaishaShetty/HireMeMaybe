/**
 * useSubscription — thin hook that exposes plan-level capabilities.
 *
 * Free tier can:   analyze, view history, generate cover letters
 * Pro tier adds:   AI resume rewrite, interview prep, company intelligence
 *
 * In a full implementation you'd verify the plan server-side before
 * calling gated endpoints. For now, the gate lives client-side — enough
 * for an MVP and trivially upgradeable to a backend check.
 */

import { useAuth } from '../context/AuthContext';

export const PRO_FEATURES = {
  REWRITE:        { key: 'rewrite',        label: 'AI Resume Rewrite' },
  INTERVIEW_PREP: { key: 'interview_prep', label: 'Interview Prep' },
  COMPANY_INTEL:  { key: 'company_intel',  label: 'Company Intelligence' },
};

export function useSubscription() {
  const { plan, isPro, isAuthenticated } = useAuth();

  /**
   * Returns true if the current user can access the given feature key.
   * Always returns true for anonymous / free users on non-gated features.
   */
  const canAccess = (featureKey) => {
    const gated = Object.values(PRO_FEATURES).map(f => f.key);
    if (!gated.includes(featureKey)) return true; // not a gated feature
    return isPro;
  };

  /**
   * Returns the label for a pro feature (for display in PaywallModal).
   */
  const featureLabel = (featureKey) => {
    return Object.values(PRO_FEATURES).find(f => f.key === featureKey)?.label ?? featureKey;
  };

  return { plan, isPro, isAuthenticated, canAccess, featureLabel };
}
