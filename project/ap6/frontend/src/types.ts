// File: types.ts
// Responsible Engineer: Engineer E (Web Dashboard)
// Purpose: Shared TypeScript types mirroring the backend API payloads so the
// dashboard, alarm center and timeline render type-safe data.

export type FsmState =
  | "IDLE" | "PRECHECK" | "NACHGUSS" | "MASHING" | "LAUTERING" | "BOILING"
  | "COOLING" | "TRANSFER_TO_K4" | "FERMENTING" | "FINISHED" | "ERROR" | "EMERGENCY";

export interface ConnectionStatus {
  active: boolean;
  mode: string | null;
  connectionStatus?: string;
  endpoint: string | null;
  sessionId: string | null;
  scenario: string | null;
  fsmState: FsmState | null;
  displayState?: string | null;
  publisherMode?: string | null;
  source?: string | null;
}

export interface FsmResult {
  current_state: FsmState;
  display_state?: string;
  previous_state: FsmState;
  transition_reason: string;
  time_in_state: number;
  state_valid: boolean;
  active_fault: boolean;
  emergency_stop: boolean;
  acknowledge_required: boolean;
}

export interface Alarm {
  id: string;
  ruleId: string;
  code: string;
  severity: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  state: string;
  component: string;
  variable: string;
  value: unknown;
  threshold: string;
  message: string;
  status: string;
  createdAt: string;
  clearedAt: string | null;
}

export interface TimelineStep {
  state: FsmState;
  current: boolean;
  mainVessel: string;
}

export interface SystemEvent {
  id: string;
  level: string;
  eventType: string;
  message: string;
  createdAt: string;
}

export interface StatusResponse {
  connected: boolean;
  connection: ConnectionStatus;
  session?: { sessionId: string; mode: string; scenario: string | null; startedAt: string };
  fsm?: FsmResult;
  mainVessel?: string;
  snapshot?: Record<string, unknown>;
  measurements?: Record<string, number | boolean>;
  activeAlarms?: Alarm[];
  alarmCount?: number;
  timeline?: TimelineStep[];
  transitions?: Array<Record<string, unknown>>;
  events?: SystemEvent[];
  source?: string;
  publisherMode?: string;
  displayState?: string;
}

export interface Scenario {
  name: string;
  description: string;
  targetState: string;
  expectedAlarm: string | null;
}
