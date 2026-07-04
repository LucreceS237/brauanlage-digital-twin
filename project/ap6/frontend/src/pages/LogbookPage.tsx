// File: pages/LogbookPage.tsx
// Responsible Engineer: Engineer E (Web Dashboard)
// Purpose: Logbook Export Workflow (section 22, Page 6 / FR-12). Shows a REDUCED,
// real-time view of the logbook (important columns only, newest first) so the
// demonstrator can watch the run unfold and immediately see which snapshot
// caused an alarm (alarm rows are highlighted). Offers the full CSV download and
// hosts the disconnect confirmation that deletes runtime data after export.

import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import { useStatus } from "../state";
import { Card, Modal } from "../components/ui";

interface Preview {
  columns: string[];
  reducedColumns: string[];
  totalRows: number;
  rows: Array<Record<string, unknown>>;
}

// Friendly short headers for the reduced view.
const HEADERS: Record<string, string> = {
  timestamp: "Time",
  fsm_state: "State",
  aktueller_schritt: "Step",
  K2_Temperatur: "K2 °C",
  K3_Temperatur: "K3 °C",
  MobilerSensor_Temperatur: "K4 °C",
  Durchfluss_NachgussMaische: "Flow",
  alarm_active: "Alarm",
  alarm_codes: "Alarm codes",
  alarm_severities: "Severity",
};

export default function LogbookPage() {
  const { status, refresh } = useStatus();
  const active = status?.connection?.active;
  const [preview, setPreview] = useState<Preview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showDisconnect, setShowDisconnect] = useState(false);
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    if (!active) {
      setPreview(null);
      return;
    }
    api.logbookPreview().then(setPreview).catch((e) => setError((e as Error).message));
  }, [active]);

  // Real-time refresh of the reduced logbook view.
  useEffect(() => {
    load();
    if (!active) return;
    const id = setInterval(load, 1500);
    return () => clearInterval(id);
  }, [load, active]);

  async function confirmDisconnect(downloadFirst: boolean) {
    if (downloadFirst) window.open(api.logbookCsvUrl(), "_blank");
    setBusy(true);
    try {
      await api.disconnectConfirm();
      setShowDisconnect(false);
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (!active) {
    return <Card>No active session. Connect or start a simulation to generate a logbook.</Card>;
  }

  const cols = preview?.reducedColumns ?? [];
  // Newest snapshots first for the live feed.
  const rows = preview ? [...preview.rows].reverse() : [];

  return (
    <div className="space-y-6">
      <Card title="Logbook Export">
        <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
          <div className="text-sm text-slate-300">
            {preview
              ? `${preview.totalRows} snapshots recorded · live view shows the most recent ${preview.rows.length}.`
              : "Loading preview…"}
          </div>
          <div className="flex gap-3">
            <a className="btn-primary" href={api.logbookCsvUrl()} target="_blank" rel="noreferrer">
              Download full CSV
            </a>
            <button className="btn-danger" onClick={() => setShowDisconnect(true)}>
              Disconnect…
            </button>
          </div>
        </div>
        {error && <p className="text-red-400 text-sm mb-2">{error}</p>}

        <p className="text-xs text-slate-400 mb-2">
          Reduced live view — rows highlighted in red are the snapshots that triggered an alarm.
        </p>

        <div className="overflow-auto max-h-[30rem] border border-edge rounded-lg">
          <table className="text-xs w-full">
            <thead className="bg-panel sticky top-0">
              <tr>
                {cols.map((c) => (
                  <th key={c} className="text-left px-2 py-1.5 text-slate-400 border-b border-edge whitespace-nowrap">
                    {HEADERS[c] ?? c}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => {
                const alarm = row["alarm_active"] === true || row["alarm_active"] === "True";
                return (
                  <tr
                    key={i}
                    className={alarm ? "bg-red-900/40 border-b border-red-800/50" : "border-b border-edge/30"}
                  >
                    {cols.map((c) => (
                      <td key={c} className="px-2 py-1 text-slate-300 whitespace-nowrap">
                        {c === "alarm_active"
                          ? (alarm ? "⚠ YES" : "—")
                          : c === "timestamp"
                            ? String(row[c] ?? "").slice(11, 19)
                            : format(row[c])}
                      </td>
                    ))}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {showDisconnect && (
        <Modal onClose={() => setShowDisconnect(false)}>
          <h3 className="text-lg font-semibold mb-2">Disconnect and delete runtime data?</h3>
          <p className="text-sm text-slate-300 mb-4">
            Runtime values for this session will be deleted. Download the CSV logbook first to keep a
            record of the run.
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

function format(v: unknown): string {
  if (v === null || v === undefined || v === "") return "—";
  if (typeof v === "number") return Number.isInteger(v) ? String(v) : v.toFixed(2);
  return String(v);
}
