import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import Onboarding from "../components/Onboarding";
import { useOnboarding } from "../api/lifesim";
import { useGameStore } from "../store/gameStore";
import "../styles/OnboardingPage.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

/**
 * OnboardingPage - Entry point for new players
 * Handles player profile creation and game initialization
 * Supports both authenticated users and guest mode
 */
const OnboardingPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const onboardingMutation = useOnboarding();
  const { 
    setSessionId, 
    setNarrativeAndOptions, 
    setShowOnboarding,
    authToken,
    hasCompletedOnboarding,
    setTestMode
  } = useGameStore();
  
  const [defaultData, setDefaultData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Check if we're in guest mode
  const isGuestMode = location.search.includes('mode=guest');

  useEffect(() => {
    // If authenticated and has completed onboarding, fetch defaults
    if (authToken && hasCompletedOnboarding && !isGuestMode) {
      fetchAccountDefaults();
    }
    
    // Set test mode flag
    if (isGuestMode) {
      setTestMode(true);
    } else {
      setTestMode(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authToken, hasCompletedOnboarding, isGuestMode]);

  const fetchAccountDefaults = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/account/profile`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
      
      const profile = response.data;
      
      // Only set defaults if they exist
      if (profile.default_age) {
        setDefaultData({
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
        console.log('✅ Loaded account defaults');
      }
    } catch (error) {
      console.error('⚠️ Failed to load account defaults:', error);
      // Not critical, continue without defaults
    } finally {
      setLoading(false);
    }
  };

  const handleOnboardingComplete = async (onboardingData) => {
    try {
      const result = await onboardingMutation.mutateAsync(onboardingData);

      // Save session ID to Zustand store (persists to localStorage)
      setSessionId(result.game_state.session_id);

      // Store initial narrative and options
      setNarrativeAndOptions(result.initial_narrative, result.initial_options);

      // Hide onboarding
      setShowOnboarding(false);

      // Navigate to game
      navigate("/game");

      console.log("✅ Game initialized successfully");
    } catch (error) {
      console.error("❌ Onboarding failed:", error);
      throw error; // Let Onboarding component handle error display
    }
  };

  return (
    <div className="onboarding-page">
      {isGuestMode && (
        <div className="guest-mode-banner">
          👤 Playing in Guest Mode - Your progress won't be saved to the leaderboard
        </div>
      )}
      
      {onboardingMutation.isError && (
        <div className="error-banner">
          <p>
            {onboardingMutation.error?.response?.data?.detail ||
              "Failed to initialize game. Please try again."}
          </p>
          <button onClick={() => onboardingMutation.reset()}>✕</button>
        </div>
      )}

      {loading ? (
        <div className="loading-container">
          <p>Loading your profile...</p>
        </div>
      ) : (
        <Onboarding
          onComplete={handleOnboardingComplete}
          isLoading={onboardingMutation.isPending}
          defaultData={defaultData}
        />
      )}
    </div>
  );
};

export default OnboardingPage;

