import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGame } from '../context/GameContext';
import * as api from '../api/lifesim';
import TopBar from '../components/TopBar';
import './SettingsPage.css';

function SettingsPage() {
  const navigate = useNavigate();
  const { playerState, resetGameState } = useGame();
  const [settings, setSettings] = useState({
    soundEffects: true,
    showTooltips: true,
    language: 'English',
    theme: 'Light',
    sessionLength: 'Medium'
  });
  const [saving, setSaving] = useState(false);
  const [resetConfirm, setResetConfirm] = useState(false);

  // Load settings on mount
  useEffect(() => {
    const loadSettings = async () => {
      const savedSettings = await api.getSettings();
      setSettings(savedSettings);
    };
    loadSettings();
  }, []);

  // Apply theme to body
  useEffect(() => {
    document.body.className = `theme-${settings.theme.toLowerCase()}`;
  }, [settings.theme]);

  const handleSettingChange = async (key, value) => {
    const newSettings = { ...settings, [key]: value };
    setSettings(newSettings);
    
    setSaving(true);
    await api.updateSettings(newSettings);
    setTimeout(() => setSaving(false), 500);
  };

  const handleResetGame = async () => {
    if (!resetConfirm) {
      setResetConfirm(true);
      setTimeout(() => setResetConfirm(false), 5000);
      return;
    }
    
    await resetGameState();
    navigate('/');
  };

  return (
    <div className="settings-page">
      <TopBar
        playerName={playerState?.name}
        money={playerState?.metrics?.money}
        fiScore={playerState?.metrics?.fiScore}
      />

      <div className="settings-content">
        <div className="settings-container">
          <div className="settings-header">
            <h1>⚙️ Settings</h1>
            {saving && <span className="saving-indicator">Saving...</span>}
          </div>

          {/* General Settings */}
          <div className="settings-section">
            <h2 className="section-title">General</h2>
            <div className="settings-grid">
              <div className="setting-item">
                <div className="setting-info">
                  <label>Sound Effects</label>
                  <p className="setting-description">Play sound effects during gameplay</p>
                </div>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={settings.soundEffects}
                    onChange={(e) => handleSettingChange('soundEffects', e.target.checked)}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>

              <div className="setting-item">
                <div className="setting-info">
                  <label>Show Tooltips / Hints</label>
                  <p className="setting-description">Display helpful hints during the game</p>
                </div>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={settings.showTooltips}
                    onChange={(e) => handleSettingChange('showTooltips', e.target.checked)}
                  />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>

          {/* Display Settings */}
          <div className="settings-section">
            <h2 className="section-title">Display</h2>
            <div className="settings-grid">
              <div className="setting-item">
                <div className="setting-info">
                  <label>Language</label>
                  <p className="setting-description">Choose your preferred language</p>
                </div>
                <select
                  className="setting-select"
                  value={settings.language}
                  onChange={(e) => handleSettingChange('language', e.target.value)}
                >
                  <option value="English">English</option>
                  <option value="Finnish">Finnish</option>
                  <option value="Swedish">Swedish</option>
                </select>
              </div>

              <div className="setting-item">
                <div className="setting-info">
                  <label>Theme</label>
                  <p className="setting-description">Change the visual theme</p>
                </div>
                <select
                  className="setting-select"
                  value={settings.theme}
                  onChange={(e) => handleSettingChange('theme', e.target.value)}
                >
                  <option value="Light">Light</option>
                  <option value="Dark">Dark</option>
                  <option value="High Contrast">High Contrast</option>
                </select>
              </div>
            </div>
          </div>

          {/* Gameplay Settings */}
          <div className="settings-section">
            <h2 className="section-title">Gameplay</h2>
            <div className="settings-grid">
              <div className="setting-item">
                <div className="setting-info">
                  <label>Session Length</label>
                  <p className="setting-description">Recommended game session duration</p>
                </div>
                <select
                  className="setting-select"
                  value={settings.sessionLength}
                  onChange={(e) => handleSettingChange('sessionLength', e.target.value)}
                >
                  <option value="Short">Short (15 min)</option>
                  <option value="Medium">Medium (30 min)</option>
                  <option value="Long">Long (1 hour)</option>
                </select>
              </div>

              <div className="setting-item">
                <div className="setting-info">
                  <label>Reset Game Progress</label>
                  <p className="setting-description">Start over from the beginning</p>
                </div>
                <button
                  className={`btn-reset ${resetConfirm ? 'confirm' : ''}`}
                  onClick={handleResetGame}
                >
                  {resetConfirm ? '⚠️ Click Again to Confirm' : '🔄 Reset Game'}
                </button>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="settings-actions">
            <button className="btn btn-primary" onClick={() => navigate('/game')}>
              ← Back to Game
            </button>
            <button className="btn btn-secondary" onClick={() => navigate('/')}>
              Main Menu
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;

