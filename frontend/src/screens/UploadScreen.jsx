import React, { useState, useRef } from "react";
import { api } from "../services/api";
import { LoadingOverlay } from "../components/UI";

export default function UploadScreen({ onStatementLoaded }) {
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState("");
  const [error, setError] = useState(null);
  const [drag, setDrag] = useState(false);
  const inputRef = useRef();

  const processFile = async (file) => {
    if (!file || !file.name.endsWith(".pdf")) {
      setError("Please upload a PDF file.");
      return;
    }
    setError(null);
    setLoading(true);
    setLoadingMsg("Extracting text from PDF...");
    try {
      setTimeout(() => setLoadingMsg("AI detecting bank format..."), 1500);
      setTimeout(() => setLoadingMsg("Categorizing transactions..."), 4000);
      const result = await api.uploadStatement(file);
      if (result.success) {
        onStatementLoaded(result.statement);
      } else {
        setError(result.error || "Failed to parse statement.");
      }
    } catch (e) {
      setError("Connection failed. Make sure the backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {loading && <LoadingOverlay message={loadingMsg} />}
      <div className="upload-screen">
        <div className="upload-hero">
          <div className="upload-logo">💰 Finance Autopilot</div>
          <div className="upload-tagline">Upload any bank statement. Get instant AI insights.</div>
        </div>

        <div
          className={`upload-zone ${drag ? "drag" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
          onDragLeave={() => setDrag(false)}
          onDrop={(e) => { e.preventDefault(); setDrag(false); processFile(e.dataTransfer.files[0]); }}
          onClick={() => inputRef.current.click()}
        >
          <div className="upload-icon">{drag ? "⬇️" : "📄"}</div>
          <div className="upload-title">{drag ? "Drop it!" : "Drop your bank statement here"}</div>
          <div className="upload-sub">Supports any Indian or US bank · PDF format · Max 10MB</div>
          <button className="btn btn-primary" onClick={(e) => { e.stopPropagation(); inputRef.current.click(); }}>
            📂 &nbsp;Choose PDF File
          </button>
          <input ref={inputRef} type="file" accept=".pdf" style={{ display: "none" }} onChange={(e) => processFile(e.target.files[0])} />
          {error && <div className="error-box"><p className="error-text">⚠️ {error}</p></div>}
        </div>

        <div className="banks">
          <div className="banks-title">Works with any bank</div>
          <div className="banks-list">
            {["HDFC", "SBI", "ICICI", "Axis", "Kotak", "BOB", "Chase", "Wells Fargo", "& more"].map(b => (
              <span key={b} className="bank-chip">{b}</span>
            ))}
          </div>
        </div>

        <div className="features-grid">
          {[
            { icon: "🤖", title: "AI Parsing", desc: "Auto-detects any bank format" },
            { icon: "🏷️", title: "Auto Categories", desc: "9 spending categories" },
            { icon: "📊", title: "Smart Report", desc: "Plain English analysis" },
            { icon: "🚨", title: "Anomaly Detection", desc: "Flags unusual spending" },
            { icon: "💬", title: "Chat with Data", desc: "Ask AI about finances" },
            { icon: "🔒", title: "Private", desc: "Data never stored" },
          ].map(f => (
            <div key={f.title} className="feature-card">
              <div className="feature-icon">{f.icon}</div>
              <div className="feature-title">{f.title}</div>
              <div className="feature-desc">{f.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
