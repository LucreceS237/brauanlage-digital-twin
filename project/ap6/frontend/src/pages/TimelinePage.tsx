// File: pages/TimelinePage.tsx
// Responsible Engineer: Engineer E (Web Dashboard)
// Purpose: Process timeline page (section 22, Page 3). Visualises the FSM state
// progression with the current state highlighted, lists the special states and
// shows the recorded transition history for the active session.

import { useStatus } from "../state";
import { Card, STATE_COLORS } from "../components/ui";
import type { FsmState } from "../types";

const NORMAL: FsmState[] = [
  "IDLE", "PRECHECK", "NACHGUSS", "MASHING", "LAUTERING", "BOILING",
  "COOLING", "TRANSFER_TO_K4", "FERMENTING", "FINISHED",
];
const SPECIAL: FsmState[] = ["ERROR", "EMERGENCY"];

export default function TimelinePage() {
  const { status } = useStatus();
  const current = status?.fsm?.current_state;
  const transitions = status?.transitions ?? [];

  const node = (s: FsmState) => (
    <div key={s} className="flex flex-col items-center">
      <div
        className={`w-28 text-center px-3 py-3 rounded-lg font-semibold text-white ${
          s === current ? `${STATE_COLORS[s]} ring-2 ring-accent scale-105` : "bg-panel border border-edge text-slate-400"
        } transition-transform`}
      >
        {s}
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <Card title="Normal Process Flow">
        <div className="flex flex-wrap items-center gap-2">
          {NORMAL.map((s, i) => (
            <div key={s} className="flex items-center gap-2">
              {node(s)}
              {i < NORMAL.length - 1 && <span className="text-slate-500">→</span>}
            </div>
          ))}
        </div>
      </Card>

      <Card title="Special States">
        <div className="flex gap-4">{SPECIAL.map(node)}</div>
      </Card>

      <Card title="Transition History">
        {transitions.length === 0 ? (
          <p className="text-sm text-slate-400">No transitions recorded yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="text-slate-400 text-xs">
              <tr className="text-left border-b border-edge">
                <th className="py-2">Time</th>
                <th>From</th>
                <th>To</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {transitions.map((t, i) => (
                <tr key={i} className="border-b border-edge/40">
                  <td className="py-1.5 text-slate-500">{String(t["createdAt"]).slice(11, 19)}</td>
                  <td className="text-slate-400">{String(t["previousState"])}</td>
                  <td className="text-slate-100">{String(t["currentState"])}</td>
                  <td className="text-slate-300">{String(t["transitionReason"])}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </div>
  );
}
