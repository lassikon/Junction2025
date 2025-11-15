import React, { useState } from 'react';
import axios from 'axios';
import { API_URL } from '../config/api';
import { useGameStore } from '../store/gameStore';
import './AuthForm.css';

function LoginForm({ onSuccess, onBack }) {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const setAuth = useGameStore((state) => state.setAuth);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      setLoading(true);
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        username: formData.username,
        password: formData.password,
      });

      // Save auth data to store
      setAuth(response.data);

      console.log('✅ Login successful:', response.data);
      onSuccess(response.data.has_completed_onboarding);
    } catch (err) {
      console.error('❌ Login error:', err);
      setError(
        err.response?.data?.detail || 'Login failed. Please check your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div 
        className="auth-background"
        style={{ backgroundImage: 'url(/images/backgrounds/sunny_background.png)' }}
      />
      
      <div className="auth-container">
        <div className="auth-card">
          <button className="back-button" onClick={onBack}>
            ← Back
          </button>
          
          <h1 className="auth-title">Welcome Back!</h1>
          <p className="auth-description">
            Login to continue your financial independence journey
          </p>

          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                value={formData.username}
                onChange={(e) =>
                  setFormData({ ...formData, username: e.target.value })
                }
                placeholder="Enter your username"
                required
                disabled={loading}
                autoComplete="username"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                placeholder="Enter your password"
                required
                disabled={loading}
                autoComplete="current-password"
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-large"
              disabled={loading}
            >
              {loading ? 'Logging in...' : '🔐 Login'}
            </button>
          </form>

          <p className="auth-footer">
            Don't have an account?{' '}
            <button className="link-button" onClick={onBack}>
              Go back
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default LoginForm;

