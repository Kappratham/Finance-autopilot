const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";

async function handleResponse(res) {
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "API error");
  return data;
}

export const api = {
  async uploadStatement(file) {
    const formData = new FormData();
    formData.append("file", file, file.name);
    const res = await fetch(`${BASE_URL}/upload`, { method: "POST", body: formData });
    return handleResponse(res);
  },
  async getSummary(transactions) {
    const res = await fetch(`${BASE_URL}/transactions/summary`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(transactions),
    });
    return handleResponse(res);
  },
  async generateReport(transactions, month = null) {
    const res = await fetch(`${BASE_URL}/report/generate`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transactions, month }),
    });
    return handleResponse(res);
  },
  async detectAnomalies(transactions) {
    const res = await fetch(`${BASE_URL}/anomaly/detect`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transactions }),
    });
    return handleResponse(res);
  },
  async indexForChat(transactions) {
    const res = await fetch(`${BASE_URL}/chat/index`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transactions }),
    });
    return handleResponse(res);
  },
  async sendChatMessage(question, transactions, chatHistory = []) {
    const res = await fetch(`${BASE_URL}/chat/message`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, transactions, chat_history: chatHistory }),
    });
    return handleResponse(res);
  },
};
