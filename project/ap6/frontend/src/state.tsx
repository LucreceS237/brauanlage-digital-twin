// File: state.tsx
// Responsible Engineer: Engineer E (Web Dashboard)
// Purpose: Provides a shared, polled view of the backend status to the whole
// app via React context. One interval polls /api/status (~1.5s) so every page
// (dashboard, timeline, alarms) renders the same live snapshot without each
// page opening its own polling loop.

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { api } from "./api";
import type { StatusResponse } from "./types";

interface StatusContextValue {
  status: StatusResponse | null;
  error: string | null;
  refresh: () => Promise<void>;
}

const StatusContext = createContext<StatusContextValue>({
  status: null,
  error: null,
  refresh: async () => {},
});

export function StatusProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<StatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const mounted = useRef(true);

  const refresh = async () => {
    try {
      const data = await api.status();
      if (mounted.current) {
        setStatus(data);
        setError(null);
      }
    } catch (e) {
      if (mounted.current) setError((e as Error).message);
    }
  };

  useEffect(() => {
    mounted.current = true;
    refresh();
    const id = setInterval(refresh, 1500);
    return () => {
      mounted.current = false;
      clearInterval(id);
    };
  }, []);

  return (
    <StatusContext.Provider value={{ status, error, refresh }}>
      {children}
    </StatusContext.Provider>
  );
}

export function useStatus() {
  return useContext(StatusContext);
}
