/**
 * AuthContext — provides the current Supabase session + user, plus a derived
 * `plan` ('free' | 'pro') read from the `profiles` table.
 *
 * Supabase schema expected:
 *
 *   create table profiles (
 *     id   uuid primary key references auth.users(id) on delete cascade,
 *     plan text not null default 'free'        -- 'free' | 'pro'
 *   );
 *
 *   -- auto-create profile on sign-up:
 *   create or replace function handle_new_user()
 *   returns trigger language plpgsql security definer as $$
 *   begin
 *     insert into public.profiles (id, plan) values (new.id, 'free');
 *     return new;
 *   end;
 *   $$;
 *
 *   create trigger on_auth_user_created
 *     after insert on auth.users
 *     for each row execute procedure handle_new_user();
 */

import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { supabase } from '../lib/supabase';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession]   = useState(undefined); // undefined = loading
  const [profile, setProfile]   = useState(null);      // { id, plan }

  // ── Fetch profile from DB ─────────────────────────────────────────────────
  const fetchProfile = useCallback(async (userId) => {
    if (!userId) { setProfile(null); return; }
    const { data, error } = await supabase
      .from('profiles')
      .select('id, plan')
      .eq('id', userId)
      .single();

    if (error) {
      // Profile may not exist yet (race with trigger) — default to free
      console.warn('[AuthContext] fetchProfile error:', error.message);
      setProfile({ id: userId, plan: 'free' });
    } else {
      setProfile(data);
    }
  }, []);

  // ── Bootstrap: get initial session + subscribe to changes ─────────────────
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session: s } }) => {
      setSession(s ?? null);
      fetchProfile(s?.user?.id ?? null);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, s) => {
      setSession(s ?? null);
      fetchProfile(s?.user?.id ?? null);
    });

    return () => subscription.unsubscribe();
  }, [fetchProfile]);

  // ── Auth helpers ───────────────────────────────────────────────────────────
  const signUp = useCallback(async (email, password) => {
    const { data, error } = await supabase.auth.signUp({ email, password });
    if (error) throw error;
    return data;
  }, []);

  const signIn = useCallback(async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    return data;
  }, []);

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
  }, []);

  const value = {
    session,               // null = logged-out, undefined = loading
    user: session?.user ?? null,
    plan: profile?.plan ?? 'free',
    isLoading: session === undefined,
    isAuthenticated: !!session,
    isPro: profile?.plan === 'pro',
    signUp,
    signIn,
    signOut,
    refetchProfile: () => fetchProfile(session?.user?.id ?? null),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
