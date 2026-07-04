// File: pages/ConnectionPage.tsx
// Responsible Engineer: Engineer E (Web Dashboard)
// Purpose: FR-01 connection page. Lets the user pick real SPS (via MQTT) or
// simulation mode (pick a scenario), connect/disconnect and see the connection
// status + success/error feedback. "Connect to SPS" now means: subscribe to the
// MQTT broker and wait for the first valid live payload. Disconnect uses the
// guarded warn -> (optional logbook) -> confirm flow (FR-11).

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useStatus } from "../state";
import { Card, Modal } from "../components/ui";
import type { Scenario } from "../types";

export default function ConnectionPage() {
  const { status, refresh } = useStatus();
  const navigate = useNavigate();
  const connection = status?.connection;
  const active = connection?.active;

  const [mode, setMode] = useState<"real" | "simulation">("simulation");
  // Real mode connects through the MQTT broker; the endpoint is informational.
  const endpoint = "mqtt://mosquitto:1883/brauanlage/sps/live";
  const [scenario, setScenario] = useState("Normal process");
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [showDisconnect, setShowDisconnect] = useState(false);

  useEffect(() => {
    api.scenarios().then(setScenarios).catch(() => undefined);
  }, []);

  async function handleConnect() {
    setBusy(true);
    setError(null);
    setMessage(null);
    try {
      const res = await api.connect(mode, mode === "real" ? endpoint : undefined, scenario);
      if (!res.success) {
        // Expected failure (e.g. no MQTT data): show message, stay on page.
        setError(res.message);
        return;
      }
      setMessage(res.message);
      await refresh();
      // Jump straight to the live dashboard after a successful connection.
      navigate("/dashboard");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function confirmDisconnect(downloadFirst: boolean) {
    if (downloadFirst) window.open(api.logbookCsvUrl(), "_blank");
    setBusy(true);
    try {
      await api.disconnectConfirm();
      setMessage("Disconnected. Runtime session data deleted.");
      setShowDisconnect(false);
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-5xl">
      <Card title="Connection Mode">
        <div className="flex gap-3 mb-4">
          {(["simulation", "real"] as const).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`btn flex-1 ${mode === m ? "btn-primary" : "btn-ghost"}`}
            >
              {m === "real" ? "Real SPS" : "Simulation"}
            </button>
          ))}
        </div>

        {mode === "real" ? (
          <div className="mb-4 rounded-lg border border-edge bg-panel/60 p-3 text-xs text-slate-400 leading-relaxed">
            Connects via the <span className="text-slate-200">MQTT broker</span> and waits for the
            first valid live SPS payload on topic
            <span className="text-slate-200"> brauanlage/sps/live</span>. The dockerized SPS
            publisher (real or fake) feeds the data — the dashboard never talks to the SPS directly.
          </div>
        ) : (
          <label className="block mb-4">
            <span className="text-xs text-slate-400">Simulation Scenario</span>
            <select
              className="w-full mt-1 bg-panel border border-edge rounded-lg px-3 py-2 text-sm"
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
            >
              {scenarios.map((s) => (
                <option key={s.name} value={s.name}>{s.name}</option>
              ))}
            </select>
          </label>
        )}

        <div className="flex gap-3">
          <button className="btn-primary flex-1" disabled={busy || active} onClick={handleConnect}>
            {mode === "real" ? "Connect" : "Start Simulation"}
          </button>
          <button
            className="btn-danger flex-1"
            disabled={busy || !active}
            onClick={() => setShowDisconnect(true)}
          >
            Disconnect
          </button>
        </div>

        {message && <p className="mt-4 text-emerald-400 text-sm">{message}</p>}
        {error && <p className="mt-4 text-red-400 text-sm">Error: {error}</p>}
      </Card>

      <Card title="Connection Status">
        <dl className="space-y-3 text-sm">
          <Row label="Status" value={active ? "Connected" : "Disconnected"} ok={active} />
          <Row label="Link" value={connection?.connectionStatus ?? "—"} />
          <Row label="Source" value={connection?.source ?? "—"} />
          <Row label="Publisher" value={connection?.publisherMode ?? "—"} />
          <Row label="Mode" value={connection?.mode === "real" ? "Real SPS (MQTT)" : connection?.mode ?? "—"} />
          <Row label="Scenario" value={connection?.scenario ?? "—"} />
          <Row label="Endpoint" value={connection?.endpoint ?? "—"} />
          <Row label="Session" value={connection?.sessionId ?? "—"} />
          <Row label="FSM State" value={connection?.fsmState ?? "—"} />
        </dl>
      </Card>

      {showDisconnect && (
        <Modal onClose={() => setShowDisconnect(false)}>
          <h3 className="text-lg font-semibold mb-2">Disconnect the Anlage?</h3>
          <p className="text-sm text-slate-300 mb-4">
            All runtime values stored during this session will be deleted from the database to
            protect data and avoid conflicts with the next connection. Would you like to download a
            CSV logbook before disconnecting?
          </p>
          <div className="flex flex-col gap-2">
            <button className="btn-primary" disabled={busy} onClick={() => confirmDisconnect(true)}>
              Download logbook and disconnect
            </button>
            <button className="btn-danger" disabled={busy} onClick={() => confirmDisconnect(false)}>
              Disconnect without logbook
            </button>
            <button className="btn-ghost" disabled={busy} onClick={() => setShowDisconnect(false)}>
              Cancel
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}

function Row({ label, value, ok }: { label: string; value: string; ok?: boolean }) {
  return (
    <div className="flex justify-between border-b border-edge/60 pb-2">
      <dt className="text-slate-400">{label}</dt>
      <dd className={ok === undefined ? "text-slate-200" : ok ? "text-emerald-400" : "text-slate-400"}>
        {value}
      </dd>
    </div>
  );
}
