import React, { useState, useEffect, useRef } from "react";
import { api } from "../services/api";
import { LoadingOverlay } from "../components/UI";

const SUGGESTIONS = [
  "How much did I spend on food this month?",
  "What was my biggest expense?",
  "How much did I save?",
  "Which category did I overspend on?",
  "Show me all transactions above ₹5000",
  "How many food delivery orders did I make?",
];

export default function ChatScreen({ statement, onBack }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [indexing, setIndexing] = useState(true);
  const bottomRef = useRef();

  useEffect(() => {
    api.indexForChat(statement.transactions)
      .then(() => setMessages([{
        role: "assistant",
        content: `Hey! I've loaded ${statement.transactions.length} transactions from ${statement.bank_name}. Ask me anything about your finances.`,
        time: new Date().toLocaleTimeString(),
      }]))
      .catch(() => setMessages([{
        role: "assistant",
        content: "Ready! Ask me anything about your transactions.",
        time: new Date().toLocaleTimeString(),
      }]))
      .finally(() => setIndexing(false));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text) => {
    const q = text || input.trim();
    if (!q) return;
    setInput("");
    const userMsg = { role: "user", content: q, time: new Date().toLocaleTimeString() };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      const res = await api.sendChatMessage(q, statement.transactions, history);
      setMessages(prev => [...prev, {
        role: "assistant", content: res.answer,
        time: new Date().toLocaleTimeString(),
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: "assistant", content: "Sorry, something went wrong. Please try again.",
        time: new Date().toLocaleTimeString(), isError: true,
      }]);
    } finally { setLoading(false); }
  };

  const handleKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  };

  return (
    <div className="app">
      {indexing && <LoadingOverlay message="Loading your transaction data..." />}
      <div className="topbar">
        <button className="back-btn" onClick={onBack}>← Back</button>
        <span className="topbar-title">Ask AI <span className="online-dot" /></span>
        <div style={{ width: 60 }} />
      </div>

      <div className="chat-screen">
        <div className="chat-messages">
          {messages.length <= 1 && (
            <div className="suggestions-wrap">
              <div className="suggestions-label">Try asking:</div>
              <div className="chips">
                {SUGGESTIONS.map(s => (
                  <button key={s} className="chip" onClick={() => send(s)}>{s}</button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`msg-wrap ${msg.role}`}>
              {msg.role === "assistant" && <div className="avatar">🤖</div>}
              <div className={`bubble ${msg.role}`} style={msg.isError ? { borderColor: "rgba(239,68,68,0.4)" } : {}}>
                <div className="bubble-text">{msg.content}</div>
                <div className="bubble-time">{msg.time}</div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="msg-wrap assistant">
              <div className="avatar">🤖</div>
              <div className="bubble assistant">
                <div className="typing-dots">● ● ●</div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="chat-input-bar">
          <textarea
            className="chat-input"
            rows={1}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Ask about your finances..."
            maxLength={500}
          />
          <button
            className="send-btn"
            onClick={() => send()}
            disabled={!input.trim() || loading}
          >↑</button>
        </div>
      </div>
    </div>
  );
}
