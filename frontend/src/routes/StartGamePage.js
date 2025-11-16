import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_URL } from '../config/api';
import { useGameStore } from '../store/gameStore';
import './StartGamePage.css';

function StartGamePage() {
  const navigate = useNavigate();
  const { authToken, displayName, setSessionId, setNarrativeAndOptions } = useGameStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    if (!authToken) {
      navigate('/');
      return;
    }
    loadProfile();
  }, [authToken, navigate]);

  const loadProfile = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/account/profile`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
      setProfile(response.data);
      
      // If they haven't completed onboarding, redirect to onboarding
      if (!response.data.has_completed_onboarding) {
        navigate('/onboarding');
      }
    } catch (err) {
      console.error('Failed to load profile:', err);
      setError('Failed to load profile');
    }
  };

  const handleStartGame = async () => {
    try {
      setLoading(true);
      setError('');

      // Use the saved defaults to start a new game
      // Break down monthly_expenses into individual categories
      const totalExpenses = profile.default_monthly_expenses || 0;
      const onboardingData = {
        player_name: displayName || profile.username,
        age: profile.default_age,
        city: profile.default_city,
        education_path: profile.default_education_path,
        risk_attitude: profile.default_risk_attitude,
        monthly_income: profile.default_monthly_income,
        // Individual expense categories (breaking down total expenses)
        expense_housing: Math.round(totalExpenses * 0.4),
        expense_food: Math.round(totalExpenses * 0.25),
        expense_transport: Math.round(totalExpenses * 0.08),
        expense_utilities: Math.round(totalExpenses * 0.12),
        expense_insurance: Math.round(totalExpenses * 0.05),
        expense_subscriptions: 0,
        expense_other: 0,
        active_subscriptions: [],
        starting_savings: profile.default_starting_savings || 0,
        starting_debt: profile.default_starting_debt || 0,
        aspirations: profile.default_aspirations || {},
      };

      const response = await axios.post(
        `${API_URL}/api/onboarding`,
        onboardingData,
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          },
        }
      );

      // Save session ID and navigate to game
      setSessionId(response.data.game_state.session_id);
      setNarrativeAndOptions(
        response.data.initial_narrative,
        response.data.initial_options
      );
      
      navigate('/game');
    } catch (err) {
      console.error('Failed to start game:', err);
      setError(err.response?.data?.detail || 'Failed to start game');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomizeSettings = () => {
    navigate('/settings');
  };

  if (!profile) {
    return (
      <div className="start-game-page">
        <div className="start-game-container">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="start-game-page">
      <div 
        className="start-game-background"
        style={{ backgroundImage: 'url(/images/backgrounds/sunny_background.png)' }}
      />
      
      <div className="start-game-container">
        <div className="start-game-card">
          <h1 className="start-game-title">Welcome back, {displayName}! 👋</h1>
          <p className="start-game-description">
            Ready to start a new financial independence journey?
          </p>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          <div className="game-preview">
            <h3>Your Settings:</h3>
            <div className="settings-grid">
              <div className="setting-item">
                <span className="setting-label">Age:</span>
                <span className="setting-value">{profile.default_age} years</span>
              </div>
              <div className="setting-item">
                <span className="setting-label">City:</span>
                <span className="setting-value">{profile.default_city}</span>
              </div>
              <div className="setting-item">
                <span className="setting-label">Education:</span>
                <span className="setting-value">{profile.default_education_path}</span>
              </div>
              <div className="setting-item">
                <span className="setting-label">Risk Attitude:</span>
                <span className="setting-value">{profile.default_risk_attitude}</span>
              </div>
              <div className="setting-item">
                <span className="setting-label">Monthly Income:</span>
                <span className="setting-value">€{profile.default_monthly_income}</span>
              </div>
              <div className="setting-item">
                <span className="setting-label">Monthly Expenses:</span>
                <span className="setting-value">€{profile.default_monthly_expenses}</span>
              </div>
            </div>
          </div>

          <div className="button-group">
            <button
              className="btn btn-primary btn-large"
              onClick={handleStartGame}
              disabled={loading}
            >
              {loading ? 'Starting Game...' : '🎮 Start New Game'}
            </button>

            <button
              className="btn btn-secondary"
              onClick={handleCustomizeSettings}
              disabled={loading}
            >
              ⚙️ Customize Settings
            </button>
          </div>

          <p className="hint-text">
            💡 Your settings will be used for this game. You can change them anytime in Settings.
          </p>
        </div>
      </div>
    </div>
  );
}

export default StartGamePage;

