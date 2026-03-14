import React, { useState } from "react";
import { View, StyleSheet, StatusBar } from "react-native";
import { theme } from "./src/theme";
import UploadScreen from "./src/screens/UploadScreen";
import DashboardScreen from "./src/screens/DashboardScreen";
import ReportScreen from "./src/screens/ReportScreen";
import AnomalyScreen from "./src/screens/AnomalyScreen";
import ChatScreen from "./src/screens/ChatScreen";

export default function App() {
  const [screen, setScreen] = useState("upload");
  const [statement, setStatement] = useState(null);

  const handleStatementLoaded = (data) => {
    setStatement(data);
    setScreen("dashboard");
  };

  const navigate = (screenName) => setScreen(screenName);

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor={theme.colors.bg} />

      {screen === "upload" && (
        <UploadScreen onStatementLoaded={handleStatementLoaded} />
      )}
      {screen === "dashboard" && statement && (
        <DashboardScreen
          statement={statement}
          onNavigate={navigate}
        />
      )}
      {screen === "report" && statement && (
        <ReportScreen
          statement={statement}
          onBack={() => navigate("dashboard")}
        />
      )}
      {screen === "anomaly" && statement && (
        <AnomalyScreen
          statement={statement}
          onBack={() => navigate("dashboard")}
        />
      )}
      {screen === "chat" && statement && (
        <ChatScreen
          statement={statement}
          onBack={() => navigate("dashboard")}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: theme.colors.bg },
});
