import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useHealthCheck } from "../api/lifesim";
import { useGameStore } from "../store/gameStore";
import LeaderboardModal from "./LeaderboardModal";
import LearnMore from "../LearnMore";
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
  const [showLearn, setShowLearn] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef(null);

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

  useEffect(() => {
    function handleDocClick(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setShowMenu(false);
      }
    }

    document.addEventListener('mousedown', handleDocClick);
    return () => document.removeEventListener('mousedown', handleDocClick);
  }, []);

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
        {/* keep user badge if present */}
        {authToken && displayName && (
          <div className="user-badge">
            👤 {displayName}
            {isTestMode && <span className="test-mode-badge">Guest</span>}
          </div>
        )}

        <div className="menu-wrap" ref={menuRef}>
          <button
            className="topbar-menu-btn"
            onClick={() => setShowMenu((s) => !s)}
            aria-haspopup="true"
            aria-expanded={showMenu}
            aria-label="Open menu"
          >
            ☰
          </button>

          {showMenu && (
            <div className="dropdown-menu" role="menu">
              <button className="dropdown-item" onClick={() => { setShowLeaderboard(true); setShowMenu(false); }}>🏆 Leaderboard</button>
              {onShowTransactions && (
                <button className="dropdown-item" onClick={() => { onShowTransactions(); setShowMenu(false); }}>📊 History</button>
              )}
              <button className="dropdown-item" onClick={() => { setShowLearn(true); setShowMenu(false); }}>ℹ️ Learn more</button>
              <button className="dropdown-item" onClick={() => { handleNewGame(); setShowMenu(false); }}>🎮 New Game</button>
              {authToken && !isTestMode && (
                <button className="dropdown-item" onClick={() => { handleSettings(); setShowMenu(false); }}>⚙️ Settings</button>
              )}
              {authToken && (
                <button className="dropdown-item" onClick={() => { handleLogout(); setShowMenu(false); }}>🚪 Logout</button>
              )}
            </div>
          )}
        </div>
      </div>
      
      {showLearn && (
        <div className="modal-overlay" onClick={() => setShowLearn(false)}>
          <div className="modal-content" role="dialog" aria-modal="true" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowLearn(false)} aria-label="Close">×</button>
            <LearnMore onClose={() => setShowLearn(false)} />
          </div>
        </div>
      )}

      <LeaderboardModal 
        isOpen={showLeaderboard} 
        onClose={() => setShowLeaderboard(false)} 
      />
    </div>
  );
};

export default TopBar;

