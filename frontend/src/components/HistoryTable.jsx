export default function HistoryTable({ history }) {
  return (
    <div style={{ marginTop: "2rem" }}>
      <h3>Attack History (latest)</h3>

      <div style={{ overflowX: "auto" }}>
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            fontSize: ".85rem",
          }}
        >
          <thead>
            <tr>
              <th>ID</th>
              <th>Timestamp</th>
              <th>Action</th>
              <th>Total</th>
              <th>Regex</th>
              <th>Entropy</th>
              <th>Anomaly</th>
              <th>Latency (ms)</th>
              <th>Template</th>
            </tr>
          </thead>

          <tbody>
            {history.map((h) => (
              <tr key={h.id}>
                <td>{h.id}</td>
                <td>{h.timestamp}</td>
                <td>{h.action}</td>
                <td>{h.total_score}</td>
                <td>{h.regex_score}</td>
                <td>{h.entropy_score}</td>
                <td>{h.anomaly_score}</td>
                <td>{h.processing_ms.toFixed(2)}</td>
                <td>{h.ppa_template_id || "-"}</td>
              </tr>
            ))}

            {history.length === 0 && (
              <tr>
                <td colSpan={9} style={{ textAlign: "center" }}>
                  No history yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
