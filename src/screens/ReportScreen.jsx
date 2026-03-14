import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { LoadingOverlay } from "../components/UI";
import { fmt } from "../theme";

export default function ReportScreen({ statement, onBack }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const currency = statement?.currency;

  const generate = async () => {
    setLoading(true); setError(null);
    try {
      const data = await api.generateReport(statement.transactions, statement.statement_period);
      setReport(data);
    } catch (e) { setError("Failed to generate report. Please try again."); }
    finally { setLoading(false); }
  };

  useEffect(() => { generate(); }, []);

  return (
    <div className="app">
      {loading && <LoadingOverlay message="AI is analyzing your finances..." />}
      <div className="topbar">
        <button className="back-btn" onClick={onBack}>← Back</button>
        <span className="topbar-title">Monthly Report</span>
        <button className="back-btn" onClick={generate} style={{ fontSize: 20 }}>↻</button>
      </div>

      <div className="screen-scroll">
        <div className="screen-content">
          {error && (
            <div className="card" style={{ borderColor: "rgba(239,68,68,0.4)", marginBottom: 16 }}>
              <p style={{ color: "var(--danger)" }}>⚠️ {error}</p>
              <button className="btn btn-ghost" style={{ marginTop: 12 }} onClick={generate}>Retry</button>
            </div>
          )}

          {report && (
            <>
              <div className="summary-row">
                <div className="summary-card" style={{ borderColor: "rgba(0,255,179,0.3)" }}>
                  <div className="summary-label">Income</div>
                  <div className="summary-value" style={{ color: "var(--green)" }}>{fmt(report.summary.total_credits, currency)}</div>
                </div>
                <div className="summary-card" style={{ borderColor: "rgba(255,107,53,0.3)" }}>
                  <div className="summary-label">Spent</div>
                  <div className="summary-value" style={{ color: "var(--orange)" }}>{fmt(report.summary.total_debits, currency)}</div>
                </div>
                <div className="summary-card" style={{ borderColor: report.summary.net >= 0 ? "rgba(16,185,129,0.3)" : "rgba(239,68,68,0.3)" }}>
                  <div className="summary-label">Saved</div>
                  <div className="summary-value" style={{ color: report.summary.net >= 0 ? "var(--success)" : "var(--danger)" }}>
                    {fmt(report.summary.net, currency)}
                  </div>
                </div>
              </div>

              {/* Savings Rate */}
              <div className="card" style={{ marginBottom: 14, borderColor: "rgba(0,255,179,0.2)" }}>
                <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 4 }}>Savings Rate</div>
                <div style={{ fontSize: 36, fontWeight: 800, color: "var(--green)", fontFamily: "var(--mono)" }}>
                  {report.summary.savings_rate}%
                </div>
                <div className="savings-bar-track">
                  <div className="savings-bar-fill" style={{
                    width: `${Math.min(Math.max(report.summary.savings_rate, 0), 100)}%`,
                    backgroundColor: report.summary.savings_rate > 20 ? "var(--green)" : report.summary.savings_rate > 0 ? "var(--warning)" : "var(--danger)"
                  }} />
                </div>
                <div style={{ fontSize: 13, color: "var(--muted2)" }}>
                  {report.summary.savings_rate > 20 ? "🎉 Great savings rate!" : report.summary.savings_rate > 0 ? "📊 Room to improve" : "⚠️ Spending exceeds income"}
                </div>
              </div>

              {/* AI Report */}
              <div className="card accent" style={{ marginBottom: 14 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                  <span style={{ fontSize: 20 }}>🤖</span>
                  <span style={{ fontSize: 16, fontWeight: 700, color: "var(--accent)" }}>AI Analysis</span>
                </div>
                <p className="report-text">{report.report}</p>
              </div>

              {/* Top Expenses */}
              {report.top_expenses?.length > 0 && (
                <div className="card">
                  <div className="section-header">
                    <div className="section-title">Top Expenses</div>
                  </div>
                  {report.top_expenses.map((exp, i) => (
                    <div key={i} className="expense-row">
                      <div className="expense-rank">#{i + 1}</div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div className="expense-desc">{exp.description}</div>
                        <div className="expense-meta">{exp.date} · {exp.category}</div>
                      </div>
                      <div className="expense-amount">{fmt(exp.amount, currency)}</div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
