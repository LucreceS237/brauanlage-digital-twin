// File: pages/SimulationPage.tsx
// Responsible Engineer: Engineer E (Web Dashboard)
// Purpose: Simulation Control (section 22, Page 5 / FR-08, FR-10). Lists the
// demo scenarios. Starting a scenario while one is already running uses the
// guarded warn -> (optional logbook) -> confirm flow so previous runtime data
// is deleted only after confirmation.

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useStatus } from "../state";
import { Card, Modal } from "../components/ui";
import type { Scenario } from "../types";

export default function SimulationPage() {
  const { status, refresh } = useStatus();
  const navigate = useNavigate();
  const active = status?.connection?.active;
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [pending, setPending] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    api.scenarios().then(setScenarios).catch(() => undefined);
  }, []);

  // Choose a scenario: if a run is active, confirm (delete previous) first.
  function choose(name: string) {
    if (active) setPending(name);
    else void start(name, false);
  }

  async function start(name: string, reset: boolean) {
    setBusy(true);
    setMessage(null);
    try {
      if (reset) await api.resetConfirm(name);
      else await api.startScenario(name);
      setMessage(`Scenario '${name}' started.`);
      setPending(null);
      await refresh();
      // Jump straight to the live dashboard once the scenario is running.
      navigate("/dashboard");
    } catch (e) {
      setMessage(`Error: ${(e as Error).message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <Card title="Simulation Scenarios">
        <p className="text-sm text-slate-400 mb-4">
          Each scenario starts a fresh session with a clean runtime state. Fault scenarios drive the
          process into the matching anomaly alarm so the detection rules can be demonstrated.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {scenarios.map((s) => (
            <button
              key={s.name}
              disabled={busy}
              onClick={() => choose(s.name)}
              className="text-left bg-panel border border-edge rounded-lg p-4 hover:border-accent transition-colors"
            >
              <div className="font-semibold text-slate-100">{s.name}</div>
              <div className="text-xs text-slate-400 mt-1">{s.description}</div>
              <div className="text-[11px] text-slate-500 mt-2">
                target: {s.targetState}
                {s.expectedAlarm && <> · alarm: {s.expectedAlarm}</>}
              </div>
            </button>
          ))}
        </div>
        {message && <p className="mt-4 text-sm text-accent">{message}</p>}
      </Card>

      {pending && (
        <Modal onClose={() => setPending(null)}>
          <h3 className="text-lg font-semibold mb-2">Start a new scenario?</h3>
          <p className="text-sm text-slate-300 mb-4">
            Starting <b>{pending}</b> will delete the previous simulation runtime data. Download a
            CSV logbook first if you want to keep it.
          </p>
          <div className="flex flex-col gap-2">
            <button
              className="btn-primary"
              disabled={busy}
              onClick={() => {
                window.open(api.logbookCsvUrl(), "_blank");
                void start(pending, true);
              }}
            >
              Download logbook and start new scenario
            </button>
            <button className="btn-danger" disabled={busy} onClick={() => start(pending, true)}>
              Start new scenario without logbook
            </button>
            <button className="btn-ghost" disabled={busy} onClick={() => setPending(null)}>
              Cancel
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}
