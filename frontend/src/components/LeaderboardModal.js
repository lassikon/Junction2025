import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './LeaderboardModal.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function LeaderboardModal({ isOpen, onClose }) {
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      fetchLeaderboard();
    }
  }, [isOpen]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await axios.get(`${API_URL}/api/leaderboard?limit=10`);
      setLeaderboard(response.data);
    } catch (err) {
      console.error('Failed to load leaderboard:', err);
      setError('Failed to load leaderboard');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const getRankEmoji = (rank) => {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return `#${rank}`;
    }
  };

  const formatEducation = (education) => {
    const educationMap = {
      vocational: 'Vocational',
      university: 'University',
      high_school: 'High School',
      working: 'Working',
    };
    return educationMap[education] || education;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  return (
    <>
      <div className="modal-overlay" onClick={onClose} />
      <div className="leaderboard-modal">
        <div className="modal-header">
          <h2>🏆 Leaderboard</h2>
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-content">
          {loading && (
            <div className="loading-state">
              <p>Loading leaderboard...</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <p>{error}</p>
              <button onClick={fetchLeaderboard} className="btn-retry">
                Try Again
              </button>
            </div>
          )}

          {!loading && !error && leaderboard.length === 0 && (
            <div className="empty-state">
              <p>🎮 No scores yet!</p>
              <p className="empty-hint">Be the first to complete a game!</p>
            </div>
          )}

          {!loading && !error && leaderboard.length > 0 && (
            <div className="leaderboard-table">
              <div className="table-header">
                <div className="col-rank">Rank</div>
                <div className="col-player">Player</div>
                <div className="col-score">FI Score</div>
                <div className="col-balance">Balance</div>
                <div className="col-age">Age</div>
                <div className="col-date">Date</div>
              </div>

              {leaderboard.map((entry) => (
                <div 
                  key={entry.rank} 
                  className={`leaderboard-row ${entry.rank <= 3 ? 'top-three' : ''}`}
                >
                  <div className="col-rank rank-badge">
                    {getRankEmoji(entry.rank)}
                  </div>
                  <div className="col-player">
                    <div className="player-name">{entry.player_name}</div>
                    <div className="player-education">
                      {formatEducation(entry.education_path)}
                    </div>
                  </div>
                  <div className="col-score">
                    <div className="score-value">{entry.final_fi_score.toFixed(1)}%</div>
                    <div className="score-label">FI Score</div>
                  </div>
                  <div className="col-balance">
                    <div className="score-value">{entry.balance_score.toFixed(1)}</div>
                    <div className="score-label">Balance</div>
                  </div>
                  <div className="col-age">{entry.age}</div>
                  <div className="col-date">{formatDate(entry.completed_at)}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="modal-footer">
          <p className="footer-note">
            💡 Only completed games from registered accounts are shown
          </p>
        </div>
      </div>
    </>
  );
}

export default LeaderboardModal;

