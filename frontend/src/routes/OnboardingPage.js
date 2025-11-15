import React from "react";
import Onboarding from "../components/Onboarding";
import { useOnboarding } from "../api/lifesim";
import { useGameStore } from "../store/gameStore";
import { useNavigate } from "react-router-dom";
import "../styles/OnboardingPage.css";

/**
 * OnboardingPage - Entry point for new players
 * Handles player profile creation and game initialization
 */
const OnboardingPage = () => {
  const navigate = useNavigate();
  const onboardingMutation = useOnboarding();
  const { setSessionId, setNarrativeAndOptions, setShowOnboarding } = useGameStore();

  const handleOnboardingComplete = async (onboardingData) => {
    try {
      const result = await onboardingMutation.mutateAsync(onboardingData);

      // Save session ID to Zustand store (persists to localStorage)
      setSessionId(result.game_state.session_id);

      // Store initial narrative and full option data (with effects)
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
      {onboardingMutation.isError && (
        <div className="error-banner">
          <p>
            {onboardingMutation.error?.response?.data?.detail ||
              "Failed to initialize game. Please try again."}
          </p>
          <button onClick={() => onboardingMutation.reset()}>✕</button>
        </div>
      )}

      <Onboarding
        onComplete={handleOnboardingComplete}
        isLoading={onboardingMutation.isPending}
      />
    </div>
  );
};

export default OnboardingPage;