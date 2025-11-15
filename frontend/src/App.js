import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { QueryProvider } from "./providers/QueryProvider";
import { useGameStore } from "./store/gameStore";
import LandingPage from "./routes/LandingPage";
import OnboardingPage from "./routes/OnboardingPage";
import StartGamePage from "./routes/StartGamePage";
import GamePage from "./routes/GamePage";
import SettingsPage from "./routes/SettingsPage";
import "./styles/App.css";

function AppRoutes() {
  const sessionId = useGameStore((state) => state.sessionId);

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/onboarding" element={<OnboardingPage />} />
      <Route path="/start-game" element={<StartGamePage />} />
      <Route path="/settings" element={<SettingsPage />} />
      <Route
        path="/game"
        element={
          sessionId ? (
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