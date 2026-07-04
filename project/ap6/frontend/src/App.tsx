// File: App.tsx
// Responsible Engineer: Engineer E (Web Dashboard)
// Purpose: Application shell. Provides the shared status context, the industrial
// sidebar navigation and the routes for the six GUI pages (section 22). A global
// EMERGENCY/ERROR banner is rendered above all pages when the FSM is in a
// critical state so the operator always sees it.

import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import { api } from "./api";
import { StatusProvider, useStatus } from "./state";
import { STATE_COLORS } from "./components/ui";
import ConnectionPage from "./pages/ConnectionPage";
import DashboardPage from "./pages/DashboardPage";
import TimelinePage from "./pages/TimelinePage";
import AlarmCenterPage from "./pages/AlarmCenterPage";
import SimulationPage from "./pages/SimulationPage";
import LogbookPage from "./pages/LogbookPage";

const NAV = [
  { to: "/connection", label: "Connection" },
  { to: "/dashboard", label: "Live Dashboard" },
  { to: "/timeline", label: "Process Timeline" },
  { to: "/alarms", label: "Alarm Center" },
  { to: "/simulation", label: "Simulation Control" },
  { to: "/logbook", label: "Logbook Export" },
];

function GlobalBanner() {
  const { status, refresh } = useStatus();
  const state = status?.fsm?.current_state;
  if (state !== "ERROR" && state !== "EMERGENCY") return null;
  const critical = state === "EMERGENCY";
  return (
    <div
      className={`px-6 py-3 flex items-center justify-center gap-4 font-bold tracking-wide ${
        critical ? "bg-red-700 animate-pulse" : "bg-red-600"
      }`}
    >
      <span>
        {critical
          ? "EMERGENCY — all outputs disabled. Acknowledge required to resume."
          : "ERROR — process fault detected. Acknowledge required to recover."}
      </span>
      <button
        className="bg-white/90 text-black text-sm px-3 py-1 rounded font-semibold hover:bg-white"
        onClick={async () => {
          await api.fsmAcknowledge();
          await refresh();
        }}
      >
        Acknowledge
      </button>
    </div>
  );
}

function ConnectionPill() {
  const { status } = useStatus();
  const active = status?.connection?.active;
  const state = status?.fsm?.current_state;
  return (
    <div className="flex items-center gap-2 text-sm">
      <span className={`h-2.5 w-2.5 rounded-full ${active ? "bg-emerald-400" : "bg-slate-500"}`} />
      <span className="text-slate-300">{active ? "Connected" : "Disconnected"}</span>
      {state && (
        <span className={`ml-2 text-xs px-2 py-0.5 rounded text-white ${STATE_COLORS[state]}`}>
          {state}
        </span>
      )}
    </div>
  );
}

function Shell() {
  return (
    <div className="min-h-screen flex">
      <aside className="w-60 bg-panel border-r border-edge flex flex-col">
        <div className="p-5 border-b border-edge">
          <div className="text-brew font-bold text-lg leading-tight">Brauanlage</div>
          <div className="text-slate-400 text-xs">Digital Twin MVP</div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                `block px-3 py-2 rounded-lg text-sm ${
                  isActive ? "bg-accent text-black font-semibold" : "text-slate-300 hover:bg-edge"
                }`
              }
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-edge text-[11px] text-slate-500">
          Read-only SPS · MongoDB · FSM · Anomaly Detection
        </div>
      </aside>

      <main className="flex-1 flex flex-col">
        <header className="flex items-center justify-between px-6 py-3 border-b border-edge bg-panel/60">
          <h1 className="text-slate-200 font-semibold">Digital Twin — Automated Brewing System</h1>
          <ConnectionPill />
        </header>
        <GlobalBanner />
        <div className="p-6 flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/connection" replace />} />
            <Route path="/connection" element={<ConnectionPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/timeline" element={<TimelinePage />} />
            <Route path="/alarms" element={<AlarmCenterPage />} />
            <Route path="/simulation" element={<SimulationPage />} />
            <Route path="/logbook" element={<LogbookPage />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <StatusProvider>
      <Shell />
    </StatusProvider>
  );
}
