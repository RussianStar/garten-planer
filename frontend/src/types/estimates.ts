export type Estimate = {
  typical: number;
  lower: number | null;
  upper: number | null;
  confidence: number;
  source: "kb" | "user" | "learned" | "sensor";
  updated_at?: string | null;
};

export type ScheduleEvent = {
  id: string;
  planting_id: string;
  kind: "sow" | "transplant" | "harvest_start" | "clear_bed";
  earliest: string; // ISO date
  typical: string;
  latest: string;
};

export type PlanResult = {
  crop_variety_id: string;
  sow_date: string;
  events: ScheduleEvent[];
};
