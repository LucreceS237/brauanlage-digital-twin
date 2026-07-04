// File: pages/DashboardPage.tsx
// Responsible Engineer: Engineer E (Web Dashboard)
// Purpose: FR-07 live dashboard. Shows the current FSM phase, process step,
// time-in-state and latest snapshot timestamp, a process timeline, the active
// alarms panel, a MULTI-VARIABLE trend chart (follow >= 3 signals at once) and
// the event log. All data comes from the shared polled status context.

import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { api } from "../api";
import { useStatus } from "../state";
import { Badge, Card, Stat, SEVERITY_COLORS, STATE_COLORS } from "../components/ui";
import type { FsmState } from "../types";

// Variables that can be plotted, with axis assignment + line colour.
const TREND_VARS: Record<string, { label: string; color: string; axis: "temp" | "flow" }> = {
  K1_Temperatur: { label: "K1 °C", color: "#f0a500", axis: "temp" },
  K2_Temperatur: { label: "K2 °C", color: "#39d0d8", axis: "temp" },
  K3_Temperatur: { label: "K3 °C", color: "#f97316", axis: "temp" },
  MobilerSensor_Temperatur: { label: "K4 °C", color: "#34d399", axis: "temp" },
  Durchfluss_NachgussMaische: { label: "Flow l/min", color: "#a78bfa", axis: "flow" },
};

function num(v: unknown, digits = 1): string {
  return typeof v === "number" ? v.toFixed(digits) : "—";
}

export default function DashboardPage() {
  const { status } = useStatus();
  const m = status?.measurements ?? {};
  const fsm = status?.fsm;
  const state = (fsm?.current_state ?? "IDLE") as FsmState;

  if (!status?.connected) {
    return <Card>Not connected. Start a connection or simulation on the Connection page.</Card>;
  }

  return (
    <div className="space-y-6">
      {/* Top row: phase, step, time-in-state, timestamp */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card title="Current Phase">
          <span className={`inline-block px-3 py-1 rounded text-white font-bold ${STATE_COLORS[state]}`}>
            {state}
          </span>
          <div className="text-xs text-slate-400 mt-2">Main vessel: {status.mainVessel}</div>
        </Card>
        <Card title="Process Step"><Stat label="aktueller_schritt" value={String(m["aktueller_schritt"] ?? "—")} /></Card>
        <Card title="Time in State"><Stat label="seconds" value={num(fsm?.time_in_state, 0)} unit="s" /></Card>
        <Card title="Last Snapshot">
          <div className="text-sm text-slate-200">
            {String(status.snapshot?.["receivedAt"] ?? "—").slice(11, 19)}
          </div>
          <div className="text-xs text-slate-400 mt-1">source: {String(status.snapshot?.["source"] ?? "—")}</div>
        </Card>
      </div>

      {/* Multi-variable trend + active alarms */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Trends" className="lg:col-span-2">
          <MultiTrend connected={!!status.connected} />
        </Card>

        <Card title={`Active Alarms (${status.alarmCount ?? 0})`}>
          {(status.activeAlarms?.length ?? 0) === 0 ? (
            <p className="text-sm text-slate-400">No active alarms.</p>
          ) : (
            <ul className="space-y-2 max-h-72 overflow-auto">
              {status.activeAlarms!.map((a) => (
                <li key={a.id} className="bg-panel rounded-lg p-2 border border-edge">
                  <div className="flex items-center gap-2">
                    <Badge text={a.severity} color={SEVERITY_COLORS[a.severity]} />
                    <span className="text-xs text-slate-400">{a.code}</span>
                  </div>
                  <div className="text-sm mt-1">{a.message}</div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      {/* Process timeline */}
      <Card title="Process Timeline">
        <div className="flex flex-wrap gap-2">
          {status.timeline?.map((step) => (
            <div
              key={step.state}
              className={`px-3 py-1.5 rounded text-xs font-semibold ${
                step.current ? `${STATE_COLORS[step.state]} text-white ring-2 ring-accent` : "bg-panel text-slate-400 border border-edge"
              }`}
            >
              {step.state}
            </div>
          ))}
        </div>
      </Card>

      {/* Event log */}
      <Card title="Event Log">
        <ul className="space-y-1 text-xs max-h-52 overflow-auto">
          {status.events?.map((e) => (
            <li key={e.id} className="flex gap-2">
              <span className="text-slate-500">{e.createdAt.slice(11, 19)}</span>
              <span className={e.level === "WARNING" ? "text-amber-400" : "text-slate-300"}>
                {e.eventType}: {e.message}
              </span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}

// Trend chart that plots several variables at once. Temperatures share the left
// °C axis; flow uses the right l/min axis. Histories are fetched per variable
// and merged by sample index (all variables come from the same snapshot cycle).
function MultiTrend({ connected }: { connected: boolean }) {
  const allVars = Object.keys(TREND_VARS);
  const [selected, setSelected] = useState<string[]>([
    "K1_Temperatur", "K2_Temperatur", "K3_Temperatur",
  ]);
  const [data, setData] = useState<Array<Record<string, number | string>>>([]);

  const selectedKey = useMemo(() => selected.join(","), [selected]);
  const hasFlow = selected.some((v) => TREND_VARS[v].axis === "flow");

  useEffect(() => {
    if (!connected || selected.length === 0) {
      setData([]);
      return;
    }
    let on = true;
    const load = async () => {
      try {
        const results = await Promise.all(selected.map((v) => api.measurementHistory(v, 60)));
        if (!on) return;
        const minLen = Math.min(...results.map((r) => r.points.length));
        const merged: Array<Record<string, number | string>> = [];
        for (let i = 0; i < minLen; i++) {
          const row: Record<string, number | string> = {
            t: results[0].points[i].timestamp.slice(11, 19),
          };
          selected.forEach((v, idx) => {
            row[v] = Number(results[idx].points[i].value);
          });
          merged.push(row);
        }
        setData(merged);
      } catch {
        /* ignore transient errors */
      }
    };
    load();
    const id = setInterval(load, 1500);
    return () => {
      on = false;
      clearInterval(id);
    };
  }, [selectedKey, connected]);

  function toggle(v: string) {
    setSelected((cur) => (cur.includes(v) ? cur.filter((x) => x !== v) : [...cur, v]));
  }

  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-3">
        {allVars.map((v) => {
          const on = selected.includes(v);
          return (
            <button
              key={v}
              onClick={() => toggle(v)}
              className={`text-xs px-2 py-1 rounded border ${
                on ? "border-transparent text-black font-semibold" : "border-edge text-slate-400 bg-panel"
              }`}
              style={on ? { background: TREND_VARS[v].color } : undefined}
            >
              {TREND_VARS[v].label}
            </button>
          );
        })}
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a323d" />
          <XAxis dataKey="t" stroke="#64748b" fontSize={10} minTickGap={24} />
          <YAxis yAxisId="temp" stroke="#64748b" fontSize={10} domain={["auto", "auto"]} unit="°C" width={48} />
          {hasFlow && (
            <YAxis yAxisId="flow" orientation="right" stroke="#a78bfa" fontSize={10} domain={[0, "auto"]} unit=" l/min" width={56} />
          )}
          <Tooltip contentStyle={{ background: "#1a212b", border: "1px solid #2a323d" }} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          {selected.map((v) => (
            <Line
              key={v}
              yAxisId={TREND_VARS[v].axis}
              type="monotone"
              dataKey={v}
              name={TREND_VARS[v].label}
              stroke={TREND_VARS[v].color}
              dot={false}
              isAnimationActive={false}
              strokeWidth={2}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
