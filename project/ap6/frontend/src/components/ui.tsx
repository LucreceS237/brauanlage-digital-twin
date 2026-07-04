// File: components/ui.tsx
// Responsible Engineer: Engineer E (Web Dashboard)
// Purpose: Small reusable presentational helpers (state colors, badges, cards,
// modal) shared across pages so the visual language stays consistent.

import type { ReactNode } from "react";
import type { FsmState } from "../types";

// Color mapping per FSM state for the timeline and phase cards.
export const STATE_COLORS: Record<FsmState, string> = {
  IDLE: "bg-slate-500",
  PRECHECK: "bg-slate-600",
  NACHGUSS: "bg-blue-600",
  MASHING: "bg-amber-500",
  LAUTERING: "bg-yellow-600",
  BOILING: "bg-orange-600",
  COOLING: "bg-sky-500",
  TRANSFER_TO_K4: "bg-indigo-600",
  FERMENTING: "bg-emerald-600",
  FINISHED: "bg-green-700",
  ERROR: "bg-red-600",
  EMERGENCY: "bg-red-700",
};

export const SEVERITY_COLORS: Record<string, string> = {
  LOW: "bg-slate-600",
  MEDIUM: "bg-amber-600",
  HIGH: "bg-orange-600",
  CRITICAL: "bg-red-600",
};

export function Card({ title, children, className = "" }: { title?: string; children: ReactNode; className?: string }) {
  return (
    <div className={`card ${className}`}>
      {title && <div className="card-title">{title}</div>}
      {children}
    </div>
  );
}

export function Stat({ label, value, unit }: { label: string; value: ReactNode; unit?: string }) {
  return (
    <div className="flex flex-col">
      <span className="text-xs text-slate-400">{label}</span>
      <span className="text-2xl font-semibold text-slate-100">
        {value}
        {unit && <span className="text-sm text-slate-400 ml-1">{unit}</span>}
      </span>
    </div>
  );
}

export function Badge({ text, color }: { text: string; color: string }) {
  return (
    <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded text-white ${color}`}>
      {text}
    </span>
  );
}

export function Modal({ children, onClose }: { children: ReactNode; onClose?: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="card max-w-lg w-full" onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </div>
  );
}
