import React from "react";
import { categoryColors } from "../theme";

export function LoadingOverlay({ message }) {
  return (
    <div className="loading-overlay">
      <div className="loading-card">
        <div className="loading-spinner" />
        <p className="loading-text">{message || "Processing..."}</p>
      </div>
    </div>
  );
}

export function CategoryBar({ category, amount, total, currency }) {
  const symbol = currency === "INR" ? "₹" : "$";
  const color = categoryColors[category] || "#94A3B8";
  const pct = total > 0 ? (amount / total) * 100 : 0;
  return (
    <div className="cat-bar">
      <div className="cat-bar-header">
        <div className="cat-bar-left">
          <div className="cat-dot" style={{ backgroundColor: color }} />
          <span className="cat-bar-label">{category}</span>
        </div>
        <span className="cat-bar-amount" style={{ color }}>
          {symbol}{Number(amount).toLocaleString("en-IN", { maximumFractionDigits: 0 })}
        </span>
      </div>
      <div className="cat-bar-track">
        <div className="cat-bar-fill" style={{ width: `${Math.min(pct, 100)}%`, backgroundColor: color }} />
      </div>
      <div className="cat-bar-pct">{pct.toFixed(1)}% of total spending</div>
    </div>
  );
}

export function Badge({ label, color }) {
  return (
    <span className="badge" style={{ color, borderColor: color + "40", backgroundColor: color + "15" }}>
      {label}
    </span>
  );
}

export function EmptyState({ icon, title, subtitle }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <div className="empty-title">{title}</div>
      {subtitle && <div className="empty-sub">{subtitle}</div>}
    </div>
  );
}
