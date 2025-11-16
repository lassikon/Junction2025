import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useGameStore } from '../store/gameStore';
import './SettingsPage.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const EDUCATION_PATHS = {
  vocational: 'Vocational Training',
  university: 'University',
  high_school: 'High School',
  working: 'Already Working',
};

const RISK_ATTITUDES = {
  risk_averse: 'Risk Averse',
  balanced: 'Balanced',
  risk_seeking: 'Risk Seeking',
};

const CITIES = [
  'Helsinki', 'Espoo', 'Tampere', 'Vantaa', 'Oulu',
  'Turku', 'Jyväskylä', 'Lahti', 'Kuopio', 'Pori',
];

function SettingsPage() {
  const navigate = useNavigate();
  const { authToken, displayName, username, clearAll } = useGameStore();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    age: 25,
    city: 'Helsinki',
    education_path: 'university',
    risk_attitude: 'balanced',
    monthly_income: 2000,
    monthly_expenses: 1000,
    starting_savings: 0,
    starting_debt: 0,
    aspirations: {},
  });

  useEffect(() => {
    if (!authToken) {
      navigate('/');
      return;
    }
    loadSettings();
  }, [authToken, navigate]);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/account/profile`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      const profile = response.data;
      if (profile.default_age) {
        setFormData({
          age: profile.default_age,
          city: profile.default_city,
          education_path: profile.default_education_path,
          risk_attitude: profile.default_risk_attitude,
          monthly_income: profile.default_monthly_income,
          monthly_expenses: profile.default_monthly_expenses,
          starting_savings: profile.default_starting_savings || 0,
          starting_debt: profile.default_starting_debt || 0,
          aspirations: profile.default_aspirations || {},
        });
      }
    } catch (err) {
      console.error('Failed to load settings:', err);
      setError('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');

      await axios.put(
        `${API_URL}/api/account/onboarding`,
        formData,
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
            'Content-Type': 'application/json',
          },
        }
      );

      setSuccess('Settings saved successfully! ✅');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Failed to save settings:', err);
      setError(err.response?.data?.detail || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    try {
      // Call logout endpoint
      await axios.post(
        `${API_URL}/api/auth/logout`,
        {},
        {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
          withCredentials: true,
        }
      );
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      // Clear local state regardless
      clearAll();
      navigate('/');
    }
  };

  if (!authToken) {
    return null;
  }

  if (loading) {
    return (
      <div className="settings-page">
        <div className="settings-container">
          <p>Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="settings-page">
      <div className="settings-container">
        <div className="settings-header">
          <div>
            <h1>⚙️ Account Settings</h1>
            <p className="account-info">
              Logged in as <strong>{displayName || username}</strong>
            </p>
          </div>
          <button className="btn btn-back" onClick={() => navigate('/game')}>
            ← Back to Game
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <div className="settings-card">
          <h2>Default Onboarding Settings</h2>
          <p className="settings-description">
            These settings will be pre-filled when you start a new game
          </p>

          <div className="settings-form">
            <div className="form-group">
              <label>Age</label>
              <input
                type="number"
                min="15"
                max="35"
                value={formData.age}
                onChange={(e) =>
                  setFormData({ ...formData, age: parseInt(e.target.value) })
                }
              />
            </div>

            <div className="form-group">
              <label>City</label>
              <select
                value={formData.city}
                onChange={(e) =>
                  setFormData({ ...formData, city: e.target.value })
                }
              >
                {CITIES.map((city) => (
                  <option key={city} value={city}>
                    {city}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Education Path</label>
              <select
                value={formData.education_path}
                onChange={(e) =>
                  setFormData({ ...formData, education_path: e.target.value })
                }
              >
                {Object.entries(EDUCATION_PATHS).map(([key, label]) => (
                  <option key={key} value={key}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Risk Attitude</label>
              <select
                value={formData.risk_attitude}
                onChange={(e) =>
                  setFormData({ ...formData, risk_attitude: e.target.value })
                }
              >
                {Object.entries(RISK_ATTITUDES).map(([key, label]) => (
                  <option key={key} value={key}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Monthly Income (€)</label>
                <input
                  type="number"
                  min="0"
                  step="100"
                  value={formData.monthly_income}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      monthly_income: parseFloat(e.target.value) || 0,
                    })
                  }
                />
              </div>

              <div className="form-group">
                <label>Monthly Expenses (€)</label>
                <input
                  type="number"
                  min="0"
                  step="100"
                  value={formData.monthly_expenses}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      monthly_expenses: parseFloat(e.target.value) || 0,
                    })
                  }
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Starting Savings (€)</label>
                <input
                  type="number"
                  min="0"
                  step="100"
                  value={formData.starting_savings}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      starting_savings: parseFloat(e.target.value) || 0,
                    })
                  }
                />
              </div>

              <div className="form-group">
                <label>Starting Debt (€)</label>
                <input
                  type="number"
                  min="0"
                  step="100"
                  value={formData.starting_debt}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      starting_debt: parseFloat(e.target.value) || 0,
                    })
                  }
                />
              </div>
            </div>

            <button
              className="btn btn-primary btn-large"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? 'Saving...' : '💾 Save Settings'}
            </button>
          </div>
        </div>

        <div className="settings-card danger-zone">
          <h2>Account Actions</h2>
          
          <div className="action-item">
            <div>
              <h3>Logout</h3>
              <p>Sign out of your account</p>
            </div>
            <button className="btn btn-secondary" onClick={handleLogout}>
              🚪 Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPage;
