import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import Onboarding from "./components/Onboarding";
import GameDashboard from "./components/GameDashboard";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState("checking");
  const [gameState, setGameState] = useState(null);
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check API health on mount
    axios
      .get(`${API_URL}/health`)
      .then(() => setApiStatus("connected"))
      .catch(() => setApiStatus("disconnected"));

    // Check if there's an existing game session in localStorage
    const savedSessionId = localStorage.getItem("lifesim_session_id");
    const savedGameState = localStorage.getItem("lifesim_game_state");

    if (savedSessionId && savedGameState) {
      try {
        setGameState(JSON.parse(savedGameState));
        setShowOnboarding(false);
      } catch (e) {
        console.error("Error parsing saved game state:", e);
        localStorage.removeItem("lifesim_session_id");
        localStorage.removeItem("lifesim_game_state");
      }
    }
  }, []);

  const handleOnboardingComplete = async (onboardingData) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(
        `${API_URL}/api/onboarding`,
        onboardingData
      );
      const newGameState = response.data;

      // Save to state
      setGameState(newGameState);
      setShowOnboarding(false);

      // Save to localStorage for persistence
      localStorage.setItem("lifesim_session_id", newGameState.session_id);
      localStorage.setItem("lifesim_game_state", JSON.stringify(newGameState));

      console.log("Game initialized successfully:", newGameState);
    } catch (error) {
      console.error("Error during onboarding:", error);
      setError(
        error.response?.data?.detail ||
          "Failed to initialize game. Please try again."
      );
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleOnboardingError = (error) => {
    setError(
      error.response?.data?.detail || "An error occurred during onboarding."
    );
  };

  const handleMakeDecision = () => {
    // Placeholder for decision-making functionality
    alert("Decision making feature coming soon!");
  };

  const handleNewGame = () => {
    localStorage.removeItem("lifesim_session_id");
    localStorage.removeItem("lifesim_game_state");
    setGameState(null);
    setShowOnboarding(true);
    setError(null);
  };

  // Show onboarding if no game state exists
  if (showOnboarding) {
    return (
      <div className="App">
        {error && (
          <div className="error-banner">
            <p>{error}</p>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}
        <Onboarding
          onComplete={handleOnboardingComplete}
          onError={handleOnboardingError}
        />
      </div>
    );
  }

  // Show game dashboard if game state exists
  return (
    <div className="App">
      <div className="api-status-bar">
        <div className={`status status-${apiStatus}`}>API: {apiStatus}</div>
        <button onClick={handleNewGame} className="btn-new-game">
          New Game
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {gameState && (
        <GameDashboard
          gameState={gameState}
          onMakeDecision={handleMakeDecision}
        />
      )}
    </div>
  );
}

export default App;
