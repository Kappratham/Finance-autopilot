import React, { useState } from "react";
import UploadScreen from "./screens/UploadScreen";
import DashboardScreen from "./screens/DashboardScreen";
import ReportScreen from "./screens/ReportScreen";
import AnomalyScreen from "./screens/AnomalyScreen";
import ChatScreen from "./screens/ChatScreen";

export default function App() {
  const [screen, setScreen] = useState("upload");
  const [statement, setStatement] = useState(null);

  const handleLoaded = (data) => { setStatement(data); setScreen("dashboard"); };
  const navigate = (s) => setScreen(s);

  return (
    <>
      {screen === "upload" && <UploadScreen onStatementLoaded={handleLoaded} />}
      {screen === "dashboard" && statement && <DashboardScreen statement={statement} onNavigate={navigate} />}
      {screen === "report" && statement && <ReportScreen statement={statement} onBack={() => navigate("dashboard")} />}
      {screen === "anomaly" && statement && <AnomalyScreen statement={statement} onBack={() => navigate("dashboard")} />}
      {screen === "chat" && statement && <ChatScreen statement={statement} onBack={() => navigate("dashboard")} />}
    </>
  );
}
