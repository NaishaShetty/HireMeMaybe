import { createClient } from '@supabase/supabase-js';

const supabaseUrl  = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnon = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnon) {
  console.warn(
    '[HireMeMaybe] Missing VITE_SUPABASE_URL or VITE_SUPABASE_ANON_KEY. ' +
    'Auth features will be disabled. Add them to frontend/.env.local'
  );
}

// createClient is safe to call with empty strings — it just won't reach Supabase
export const supabase = createClient(supabaseUrl ?? '', supabaseAnon ?? '');
