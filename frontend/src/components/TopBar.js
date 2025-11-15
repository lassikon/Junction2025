import React from "react";
import { useNavigate } from "react-router-dom";
import { useHealthCheck } from "../api/lifesim";
import { useGameStore } from "../store/gameStore";
import "../styles/TopBar.css";

/**
 * TopBar - Header with API status and game controls
 */
const TopBar = ({ onShowTransactions }) => {
  const navigate = useNavigate();
  const { data: healthStatus } = useHealthCheck();
  const { resetGame } = useGameStore();

  const apiStatus = healthStatus?.status === "healthy" ? "connected" : "disconnected";

  const handleNewGame = () => {
    // Clear all state
    resetGame();

    // Navigate to onboarding
    navigate("/");

    // Force reload to ensure clean slate
    window.location.reload();
  };

  return (
    <div className="top-bar">
      <div className="top-bar-left">
        <h1 className="game-title">🎮 LifeSim: Financial Independence Quest</h1>
      </div>
      
      <div className="top-bar-right">
        <div className={`api-status status-${apiStatus}`}>
          API: {apiStatus}
        </div>
        {onShowTransactions && (
          <button onClick={onShowTransactions} className="btn-transactions">
            📊 History
          </button>
        )}
        <button onClick={handleNewGame} className="btn-new-game">
          New Game
        </button>
      </div>
    </div>
  );
};

export default TopBar;

