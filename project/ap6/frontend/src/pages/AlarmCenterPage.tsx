// File: pages/AlarmCenterPage.tsx
// Responsible Engineer: Engineer E (Web Dashboard)
// Purpose: Alarm Center (section 22, Page 4). Shows active alarms and the full
// alarm history with severity badges, affected component/variable, message and
// per-alarm acknowledge.

import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import { useStatus } from "../state";
import { Badge, Card, SEVERITY_COLORS } from "../components/ui";
import type { Alarm } from "../types";

export default function AlarmCenterPage() {
  const { status } = useStatus();
  const [history, setHistory] = useState<Alarm[]>([]);
  const active = status?.activeAlarms ?? [];

  const loadHistory = useCallback(() => {
    api.alarmHistory().then(setHistory).catch(() => setHistory([]));
  }, []);

  useEffect(() => {
    loadHistory();
    const id = setInterval(loadHistory, 2000);
    return () => clearInterval(id);
  }, [loadHistory]);

  async function ack(id: string) {
    await api.acknowledgeAlarm(id);
    loadHistory();
  }

  const Table = ({ rows, showAck }: { rows: Alarm[]; showAck?: boolean }) => (
    <table className="w-full text-sm">
      <thead className="text-slate-400 text-xs">
        <tr className="text-left border-b border-edge">
          <th className="py-2">Severity</th>
          <th>Code</th>
          <th>State</th>
          <th>Component</th>
          <th>Variable</th>
          <th>Message</th>
          <th>Status</th>
          {showAck && <th></th>}
        </tr>
      </thead>
      <tbody>
        {rows.map((a) => (
          <tr key={a.id} className="border-b border-edge/40">
            <td className="py-1.5"><Badge text={a.severity} color={SEVERITY_COLORS[a.severity]} /></td>
            <td className="text-slate-300">{a.code}</td>
            <td className="text-slate-400">{a.state}</td>
            <td className="text-slate-400">{a.component}</td>
            <td className="text-slate-400">{a.variable}</td>
            <td className="text-slate-200">{a.message}</td>
            <td className="text-slate-400">{a.status}</td>
            {showAck && (
              <td>
                {a.status === "ACTIVE" && (
                  <button className="btn-ghost text-xs py-1" onClick={() => ack(a.id)}>Acknowledge</button>
                )}
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );

  return (
    <div className="space-y-6">
      <Card title={`Active Alarms (${active.length})`}>
        {active.length === 0 ? <p className="text-sm text-slate-400">No active alarms.</p> : <Table rows={active} showAck />}
      </Card>
      <Card title="Alarm History">
        {history.length === 0 ? <p className="text-sm text-slate-400">No alarms recorded.</p> : <Table rows={history} />}
      </Card>
    </div>
  );
}
