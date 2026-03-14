import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { LoadingOverlay, EmptyState } from "../components/UI";
import { fmt } from "../theme";

export default function AnomalyScreen({ statement, onBack }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const currency = statement?.currency;

  const run = async () => {
    setLoading(true); setError(null);
    try {
      const data = await api.detectAnomalies(statement.transactions);
      setResult(data);
    } catch (e) { setError("Detection failed. Please try again."); }
    finally { setLoading(false); }
  };

  useEffect(() => { run(); }, []);

  return (
    <div className="app">
      {loading && <LoadingOverlay message="Scanning for unusual spending..." />}
      <div className="topbar">
        <button className="back-btn" onClick={onBack}>← Back</button>
        <span className="topbar-title">Anomaly Detection</span>
        <button className="back-btn" onClick={run} style={{ fontSize: 20 }}>↻</button>
      </div>

      <div className="screen-scroll">
        <div className="screen-content">
          {error && <div className="error-box"><p className="error-text">⚠️ {error}</p></div>}

          {result && (
            <>
              <div className="card" style={{
                textAlign: "center", padding: 40, marginBottom: 20,
                borderColor: result.total_flagged > 0 ? "rgba(245,158,11,0.3)" : "rgba(16,185,129,0.3)"
              }}>
                <div style={{ fontSize: 48, marginBottom: 12 }}>{result.total_flagged > 0 ? "🚨" : "✅"}</div>
                <div style={{ fontSize: 20, fontWeight: 800, marginBottom: 8 }}>
                  {result.total_flagged} unusual transaction{result.total_flagged !== 1 ? "s" : ""} found
                </div>
                <div style={{ fontSize: 14, color: "var(--muted2)" }}>{result.summary}</div>
              </div>

              {result.anomalies.length === 0 ? (
                <EmptyState icon="✅" title="All Clear" subtitle="Your spending looks consistent." />
              ) : (
                result.anomalies.map((a, i) => (
                  <div key={i} className="card anomaly-card" style={{
                    borderColor: a.action_needed ? "rgba(239,68,68,0.3)" : "rgba(245,158,11,0.2)"
                  }}>
                    <div className="anomaly-header">
                      <div className="anomaly-left">
                        <span style={{ fontSize: 20 }}>{a.is_duplicate ? "🔁" : a.action_needed ? "🚨" : "⚠️"}</span>
                        <div>
                          <div className="anomaly-desc">{a.description}</div>
                          <div className="anomaly-meta">{a.date} · {a.category}</div>
                        </div>
                      </div>
                      <div className="anomaly-right">
                        <div className="anomaly-amount">{fmt(a.amount, currency)}</div>
                        <div className="anomaly-dev" style={{ color: a.deviation_percent > 100 ? "var(--danger)" : "var(--warning)" }}>
                          {a.deviation_percent > 0 ? `+${a.deviation_percent}%` : "Duplicate"}
                        </div>
                      </div>
                    </div>
                    <div className="anomaly-body">
                      <p className="anomaly-reason">{a.reason}</p>
                      {a.suggestion && (
                        <div className="suggestion-box">
                          <p className="suggestion-text">💡 {a.suggestion}</p>
                        </div>
                      )}
                      <p className="anomaly-avg">
                        Your avg for {a.category}: {fmt(a.category_average, currency)}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
