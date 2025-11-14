import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { QueryProvider } from "./providers/QueryProvider";
import { useSessionCheck } from "./hooks/useSessionCheck";
import OnboardingPage from "./routes/OnboardingPage";
import GamePage from "./routes/GamePage";
import "./styles/App.css";

function AppRoutes() {
  const { sessionId, showOnboarding } = useSessionCheck();

  return (
    <Routes>
      <Route
        path="/"
        element={
          showOnboarding || !sessionId ? (
            <OnboardingPage />
          ) : (
            <Navigate to="/game" replace />
          )
        }
      />
      <Route
        path="/game"
        element={
          sessionId && !showOnboarding ? (
            <GamePage />
          ) : (
            <Navigate to="/" replace />
          )
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <QueryProvider>
      <Router>
        <div className="App">
          <AppRoutes />
        </div>
      </Router>
    </QueryProvider>
  );
}

export default App;
