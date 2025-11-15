import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useHealthCheck } from "../api/lifesim";
import { useGameStore } from "../store/gameStore";
import LeaderboardModal from "./LeaderboardModal";
import "../styles/TopBar.css";

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * TopBar - Header with API status and game controls
 */
const TopBar = ({ onShowTransactions, playerState }) => {
  const navigate = useNavigate();
  const { data: healthStatus } = useHealthCheck();
  const { resetGame, authToken, displayName, isTestMode, clearAll } = useGameStore();
  const [showLeaderboard, setShowLeaderboard] = useState(false);

  const apiStatus = healthStatus?.status === "healthy" ? "connected" : "disconnected";

  const handleNewGame = () => {
    // Clear game session but keep auth
    resetGame();

    // If logged in and has completed onboarding, go to start-game page
    // Otherwise go to onboarding
    if (authToken && !isTestMode) {
      navigate("/start-game");
    } else {
      navigate("/onboarding?mode=guest");
    }
  };

  const handleSettings = () => {
    navigate("/settings");
  };

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to logout?')) {
      try {
        await axios.post(
          `${API_URL}/api/auth/logout`,
          {},
          {
            headers: {
              Authorization: `Bearer ${authToken}`,
            },
          }
        );
      } catch (err) {
        console.error('Logout error:', err);
      } finally {
        clearAll();
        navigate('/');
      }
    }
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
        {authToken && displayName && (
          <div className="user-badge">
            👤 {displayName}
            {isTestMode && <span className="test-mode-badge">Guest</span>}
          </div>
        )}
      </div>
      
      <div className="top-bar-right">
        <div className={`api-status status-${apiStatus}`}>
          API: {apiStatus}
        </div>
        <button 
          onClick={() => setShowLeaderboard(true)} 
          className="btn-leaderboard"
        >
          🏆 Leaderboard
        </button>
        {onShowTransactions && (
          <button onClick={onShowTransactions} className="btn-transactions">
            📊 History
          </button>
        )}
        <button onClick={handleNewGame} className="btn-new-game">
          🎮 New Game
        </button>
        {authToken && !isTestMode && (
          <button onClick={handleSettings} className="btn-settings">
            ⚙️ Settings
          </button>
        )}
        {authToken && (
          <button onClick={handleLogout} className="btn-logout">
            🚪 Logout
          </button>
        )}
      </div>
      
      <LeaderboardModal 
        isOpen={showLeaderboard} 
        onClose={() => setShowLeaderboard(false)} 
      />
    </div>
  );
};

export default TopBar;

