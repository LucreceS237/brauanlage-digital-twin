// File: api.ts
// Responsible Engineer: Engineer E (API integration)
// Purpose: Single typed client for the backend REST API. All network access in
// the GUI goes through here so the base URL and error handling live in one
// place. The base URL comes from VITE_API_BASE_URL (build/dev) and falls back
// to the host-exposed backend port for the local Docker demo.

import type { Scenario, StatusResponse } from "./types";

const BASE =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new Error(detail);
  }
  // 204 / empty bodies.
  const text = await res.text();
  return (text ? JSON.parse(text) : {}) as T;
}

export const api = {
  base: BASE,

  // Connection workflow
  connect: (mode: "real" | "simulation", opcuaEndpoint?: string, scenario?: string) =>
    request<{ success: boolean; message: string }>("/api/connect", {
      method: "POST",
      body: JSON.stringify({ mode, opcuaEndpoint, scenario }),
    }),
  connectionStatus: () => request<StatusResponse["connection"]>("/api/connection-status"),
  disconnectRequest: () => request<{ warning: string }>("/api/disconnect/request", { method: "POST" }),
  disconnectConfirm: () => request<{ message: string }>("/api/disconnect/confirm", { method: "POST" }),

  // Status / dashboard
  status: () => request<StatusResponse>("/api/status"),
  measurementHistory: (name: string, limit = 120) =>
    request<{ name: string; points: Array<{ timestamp: string; value: number }> }>(
      `/api/measurements/history?name=${encodeURIComponent(name)}&limit=${limit}`,
    ),

  // FSM
  fsmAcknowledge: () => request<{ message: string }>("/api/fsm/acknowledge", { method: "POST" }),

  // Alarms
  activeAlarms: () => request<import("./types").Alarm[]>("/api/alarms/active"),
  alarmHistory: () => request<import("./types").Alarm[]>("/api/alarms/history"),
  acknowledgeAlarm: (id: string) =>
    request<{ message: string }>(`/api/alarms/${id}/acknowledge`, { method: "POST" }),

  // Simulation
  scenarios: () => request<Scenario[]>("/api/simulation/scenarios"),
  startScenario: (scenario: string) =>
    request<{ message: string }>("/api/simulation/scenario", {
      method: "POST",
      body: JSON.stringify({ scenario }),
    }),
  resetConfirm: (scenario: string) =>
    request<{ message: string }>("/api/simulation/reset/confirm", {
      method: "POST",
      body: JSON.stringify({ scenario }),
    }),

  // Logbook
  logbookPreview: () =>
    request<{
      columns: string[];
      reducedColumns: string[];
      totalRows: number;
      rows: Array<Record<string, unknown>>;
    }>("/api/logbook/preview"),
  logbookCsvUrl: () => `${BASE}/api/logbook/export/csv`,
};
