
import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import * as SecureStore from "expo-secure-store";
import { api, setToken, setUnauthorizedHandler } from "./api";

const KEY = "laundry_pal_token";
const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [token, setTok] = useState(null);
  const [ready, setReady] = useState(false);

  const signOut = useCallback(async () => {
    setToken(null); setTok(null);
    try { await SecureStore.deleteItemAsync(KEY); } catch {}
  }, []);

  const signIn = useCallback(async (t) => {
    setToken(t); setTok(t);
    try { await SecureStore.setItemAsync(KEY, t); } catch {}
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(signOut);
    (async () => {
      try {
        const saved = await SecureStore.getItemAsync(KEY);
        if (saved) { setToken(saved); await api("/me"); setTok(saved); }   // /me confirms the token is still valid
      } catch { setToken(null); }
      setReady(true);
    })();
  }, [signOut]);

  return <Ctx.Provider value={{ token, ready, signIn, signOut }}>{children}</Ctx.Provider>;
}
