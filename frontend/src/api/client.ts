import type { PlanResult } from "../types/estimates";

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

export async function fetchDemoPlan(sowDate: string, riskTolerance: number): Promise<PlanResult> {
  const url = new URL("/demo/plan", API_BASE);
  url.searchParams.set("sow_date", sowDate);
  url.searchParams.set("risk_tolerance", riskTolerance.toString());
  const res = await fetch(url.toString());
  if (!res.ok) {
    throw new Error(`Backend error ${res.status}`);
  }
  return res.json();
}
