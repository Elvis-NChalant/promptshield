import { useState, useEffect } from "react";
import AnalyzeForm from "./components/AnalyzeForm";
import MetricsPanel from "./components/MetricsPanel";
import HistoryTable from "./components/HistoryTable";
import PPADemo from "./components/PPADemo";

const API_BASE = "http://localhost:8000";

function App() {
  const [lastResult, setLastResult] = useState(null);
  const [history, setHistory] = useState([]);

  const refreshHistory = async () => {
    const res = await fetch(`${API_BASE}/history`);
    const data = await res.json();
    setHistory(data.items || []);
  };

  useEffect(() => {
    refreshHistory();
  }, []);

  const handleAnalyze = async (prompt) => {
    const start = performance.now();

    const res = await fetch(`${API_BASE}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });

    const data = await res.json();
    const elapsed = performance.now() - start;

    setLastResult({
      ...data,
      client_ms: elapsed,
    });

    refreshHistory();
  };

  return (
    <div style={{ padding: "1.5rem", fontFamily: "system-ui" }}>
      <h1>PromptShield Dashboard</h1>

      <p style={{ opacity: 0.75 }}>
        Real-time LLM safety gateway
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "2fr 1fr",
          gap: "1rem",
          alignItems: "flex-start",
          marginTop: "1rem",
        }}
      >
        <AnalyzeForm onAnalyze={handleAnalyze} lastResult={lastResult} />
        <MetricsPanel lastResult={lastResult} />
      </div>

      <PPADemo lastResult={lastResult} />

      <HistoryTable history={history} />
    </div>
  );
}

export default App;
