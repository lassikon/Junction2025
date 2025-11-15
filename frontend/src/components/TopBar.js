import React from "react";
import { useNavigate } from "react-router-dom";
import { useHealthCheck } from "../api/lifesim";
import { useGameStore } from "../store/gameStore";
import "../styles/TopBar.css";

/**
 * TopBar - Header with API status and game controls
 */
const TopBar = ({ onShowTransactions, playerState }) => {
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

  const handleClearCache = () => {
    // Clear all localStorage
    localStorage.clear();
    
    // Show alert
    alert("Cache cleared! The page will reload with fresh data.");
    
    // Reload page
    window.location.reload();
  };

  // Get month name and phase
  const getMonthName = (monthsPassed) => {
    const months = ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"];
    return months[monthsPassed % 12];
  };

  const getPhaseName = (phase) => {
    return { 1: "Early", 2: "Mid", 3: "Late" }[phase] || "Early";
  };

  const monthDisplay = playerState ? 
    `${getPhaseName(playerState.month_phase)} ${getMonthName(playerState.months_passed)}` : 
    "";

  return (
    <div className="top-bar">
      <div className="top-bar-left">
        <h1 className="game-title">🎮 LifeSim: Financial Independence Quest</h1>
        {monthDisplay && (
          <div className="month-indicator">
            📅 {monthDisplay}
          </div>
        )}
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
        <button 
          onClick={handleClearCache} 
          className="btn-clear-cache"
          title="Clear cache and reload"
        >
          🔄 Clear Cache
        </button>
        <button onClick={handleNewGame} className="btn-new-game">
          New Game
        </button>
      </div>
    </div>
  );
};

export default TopBar;

