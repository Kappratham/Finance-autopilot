import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { CategoryBar, Badge, LoadingOverlay } from "../components/UI";
import { categoryColors, fmt } from "../theme";

export default function DashboardScreen({ statement, onNavigate }) {
  const [summary, setSummary] = useState(null);
  const [tab, setTab] = useState("overview");
  const [loading, setLoading] = useState(true);
  const currency = statement?.currency;

  useEffect(() => {
    api.getSummary(statement.transactions)
      .then(setSummary)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingOverlay message="Loading dashboard..." />;

  const totalDebits = summary?.total_debits || 0;
  const categories = summary?.category_breakdown || {};

  return (
    <div className="app">
      {/* Top bar */}
      <div className="topbar">
        <div>
          <div className="topbar-title">{statement.bank_name}</div>
          <div style={{ fontSize: 11, color: "var(--muted2)" }}>{statement.statement_period || "Current Period"}</div>
        </div>
        <span className="badge" style={{ color: "var(--accent)", borderColor: "rgba(0,212,255,0.3)", background: "rgba(0,212,255,0.08)" }}>
          {statement.currency}
        </span>
      </div>

      {/* Tabs */}
      <div className="tabs">
        {["overview", "transactions", "categories"].map(t => (
          <button key={t} className={`tab ${tab === t ? "active" : ""}`} onClick={() => setTab(t)}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      <div className="screen-scroll">
        <div className="screen-content">

          {tab === "overview" && (
            <>
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon">📈</div>
                  <div className="stat-value" style={{ color: "var(--green)" }}>{fmt(summary?.total_credits || 0, currency)}</div>
                  <div className="stat-label">Income</div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">📉</div>
                  <div className="stat-value" style={{ color: "var(--orange)" }}>{fmt(totalDebits, currency)}</div>
                  <div className="stat-label">Spent</div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">{summary?.net >= 0 ? "✅" : "⚠️"}</div>
                  <div className="stat-value" style={{ color: summary?.net >= 0 ? "var(--success)" : "var(--danger)" }}>{fmt(summary?.net || 0, currency)}</div>
                  <div className="stat-label">Net</div>
                </div>
                <div className="stat-card">
                  <div className="stat-icon">🔢</div>
                  <div className="stat-value" style={{ color: "var(--purple)" }}>{summary?.total_transactions || 0}</div>
                  <div className="stat-label">Transactions</div>
                </div>
              </div>

              <div className="action-grid">
                {[
                  { icon: "📊", title: "Monthly Report", sub: "AI-generated insights", screen: "report" },
                  { icon: "🚨", title: "Anomalies", sub: "Unusual spending", screen: "anomaly" },
                  { icon: "💬", title: "Ask AI", sub: "Chat with your data", screen: "chat" },
                  { icon: "📤", title: "New Upload", sub: "Load another statement", screen: "upload" },
                ].map(a => (
                  <div key={a.title} className="action-card" onClick={() => onNavigate(a.screen)}>
                    <div className="action-icon">{a.icon}</div>
                    <div className="action-title">{a.title}</div>
                    <div className="action-sub">{a.sub}</div>
                  </div>
                ))}
              </div>

              <div className="card" style={{ marginTop: 16 }}>
                <div className="section-header">
                  <div className="section-title">Top Spending</div>
                </div>
                {Object.entries(categories).slice(0, 5).map(([cat, amt]) => (
                  <CategoryBar key={cat} category={cat} amount={amt} total={totalDebits} currency={currency} />
                ))}
              </div>
            </>
          )}

          {tab === "transactions" && (
            <>
              <div className="section-header">
                <div className="section-title">All Transactions</div>
                <div className="section-sub">{statement.transactions.length} total</div>
              </div>
              {statement.transactions.map(t => (
                <div key={t.id} className="tx-card">
                  <div className="tx-left">
                    <div className="tx-dot" style={{ backgroundColor: t.type === "credit" ? "var(--green)" : "var(--orange)" }} />
                    <div style={{ minWidth: 0 }}>
                      <div className="tx-desc">{t.description}</div>
                      <div className="tx-date">{t.date}</div>
                    </div>
                  </div>
                  <div className="tx-right">
                    <div className="tx-amount" style={{ color: t.type === "credit" ? "var(--green)" : "var(--text)" }}>
                      {t.type === "credit" ? "+" : "-"}{fmt(t.amount, currency)}
                    </div>
                    {t.category && <Badge label={t.category} color={categoryColors[t.category] || "#94A3B8"} />}
                  </div>
                </div>
              ))}
            </>
          )}

          {tab === "categories" && (
            <>
              <div className="section-header">
                <div className="section-title">Spending by Category</div>
                <div className="section-sub">Debit transactions only</div>
              </div>
              <div className="card">
                {Object.entries(categories).map(([cat, amt]) => (
                  <CategoryBar key={cat} category={cat} amount={amt} total={totalDebits} currency={currency} />
                ))}
              </div>
            </>
          )}

        </div>
      </div>
    </div>
  );
}
