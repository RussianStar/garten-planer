import { useEffect, useState } from "react";
import { fetchDemoPlan } from "./api/client";
import type { PlanResult } from "./types/estimates";
import { RangeBar } from "./components/RangeBar";

export default function App() {
  const [sowDate, setSowDate] = useState<string>(todayISO());
  const [riskTolerance, setRiskTolerance] = useState<number>(0.5);
  const [plan, setPlan] = useState<PlanResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchDemoPlan(sowDate, riskTolerance)
      .then(setPlan)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [sowDate, riskTolerance]);

  return (
    <div style={pageStyle}>
      <h1 style={{ marginBottom: 4 }}>Garden Planner</h1>
      <p style={{ color: "#345" }}>
        Arrows + uncertainty → date windows instead of single points.
      </p>

      <div style={cardStyle}>
        <label style={{ display: "block", marginBottom: 6 }}>
          Sow date:
          <input
            type="date"
            value={sowDate}
            onChange={(e) => setSowDate(e.target.value)}
            style={inputStyle}
          />
        </label>
        <label style={{ display: "block", margin: "12px 0" }}>
          Risk tolerance ({riskTolerance.toFixed(2)}):
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={riskTolerance}
            onChange={(e) => setRiskTolerance(Number(e.target.value))}
            style={{ marginLeft: 12, width: 180 }}
          />
          <small style={{ display: "block", color: "#456" }}>
            0 = cautious (use upper bounds), 1 = aggressive (lean on typical)
          </small>
        </label>
        {loading && <p>Loading plan…</p>}
        {error && <p style={{ color: "firebrick" }}>{error}</p>}
        {plan && <PlanView plan={plan} />}
      </div>
    </div>
  );
}

function PlanView({ plan }: { plan: PlanResult }) {
  return (
    <div>
      <h3 style={{ margin: "8px 0" }}>
        Tomato lifecycle starting {plan.sow_date}
      </h3>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {plan.events.map((ev) => (
          <div key={ev.id} style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ minWidth: 110, textTransform: "capitalize" }}>{ev.kind}</span>
            <RangeBar
              earliest={ev.earliest}
              typical={ev.typical}
              latest={ev.latest}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

const pageStyle: React.CSSProperties = {
  fontFamily: "Inter, system-ui, -apple-system, sans-serif",
  background: "linear-gradient(135deg, #f5f8ff 0%, #e6f1ff 100%)",
  minHeight: "100vh",
  padding: "32px 24px",
  color: "#123",
};

const cardStyle: React.CSSProperties = {
  background: "#fff",
  padding: 16,
  borderRadius: 12,
  boxShadow: "0 8px 32px rgba(0,0,0,0.08)",
  maxWidth: 720,
  border: "1px solid #dce6f5",
};

const inputStyle: React.CSSProperties = {
  marginLeft: 12,
  padding: "6px 8px",
  borderRadius: 6,
  border: "1px solid #cfd8ea",
};
