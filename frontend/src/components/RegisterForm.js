import React, { useState } from 'react';
import axios from 'axios';
import { API_URL } from '../config/api';
import { useGameStore } from '../store/gameStore';
import './AuthForm.css';

function RegisterForm({ onSuccess, onBack }) {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    display_name: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const setAuth = useGameStore((state) => state.setAuth);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    if (formData.username.length < 3) {
      setError('Username must be at least 3 characters');
      return;
    }

    try {
      setLoading(true);
      const response = await axios.post(
        `${API_URL}/api/auth/register`,
        {
          username: formData.username,
          password: formData.password,
          display_name: formData.display_name || formData.username,
        },
        { withCredentials: true }
      );

      // Save auth data to store
      setAuth(response.data);

      console.log('✅ Registration successful:', response.data);
      onSuccess();
    } catch (err) {
      console.error('❌ Registration error:', err);
      setError(
        err.response?.data?.detail || 'Registration failed. Please try again.'
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
          
          <h1 className="auth-title">Create Account</h1>
          <p className="auth-description">
            Join LifeSim and start your financial independence journey!
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
                placeholder="Choose a username"
                required
                minLength={3}
                maxLength={50}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="display_name">Display Name (Optional)</label>
              <input
                id="display_name"
                type="text"
                value={formData.display_name}
                onChange={(e) =>
                  setFormData({ ...formData, display_name: e.target.value })
                }
                placeholder="How should we call you?"
                maxLength={100}
                disabled={loading}
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
                placeholder="Enter password (min 6 characters)"
                required
                minLength={6}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={(e) =>
                  setFormData({ ...formData, confirmPassword: e.target.value })
                }
                placeholder="Re-enter password"
                required
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-large"
              disabled={loading}
            >
              {loading ? 'Creating Account...' : '✨ Create Account'}
            </button>
          </form>

          <p className="auth-footer">
            Already have an account?{' '}
            <button className="link-button" onClick={onBack}>
              Go back
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default RegisterForm;

