import React, { useEffect } from "react";
import "./App.css";
import Onboarding from "./components/Onboarding";
import GameDashboard from "./components/GameDashboard";
import { useGameStore } from "./store/gameStore";
import {
  usePlayerState,
  useOnboarding,
  useMakeDecision,
  useHealthCheck,
} from "./api/gameApi";

function App() {
  // ===================================
  // ZUSTAND: Local UI state
  // ===================================
  const {
    sessionId,
    setSessionId,
    showOnboarding,
    setShowOnboarding,
    showDecisionModal,
    openDecisionModal,
    closeDecisionModal,
    showConsequenceModal,
    closeConsequenceModal,
    consequenceData,
    setConsequenceData,
    currentNarrative,
    currentOptions,
    setNarrativeAndOptions,
    resetGame,
  } = useGameStore();

  // ===================================
  // TANSTACK QUERY: Server state
  // ===================================
  const { data: healthStatus } = useHealthCheck();
  const { data: playerState, isLoading: isLoadingPlayerState } =
    usePlayerState(sessionId);
  const onboardingMutation = useOnboarding();
  const decisionMutation = useMakeDecision();

  // ===================================
  // API STATUS
  // ===================================
  const apiStatus =
    healthStatus?.status === "healthy" ? "connected" : "disconnected";

  // ===================================
  // CHECK FOR EXISTING SESSION ON MOUNT
  // ===================================
  useEffect(() => {
    if (sessionId) {
      setShowOnboarding(false);
    }
  }, [sessionId, setShowOnboarding]);

  // ===================================
  // HANDLERS
  // ===================================

  /**
   * Handle onboarding completion
   */
  const handleOnboardingComplete = async (onboardingData) => {
    try {
      const result = await onboardingMutation.mutateAsync(onboardingData);

      // Save session ID to Zustand store (will persist to localStorage)
      setSessionId(result.game_state.session_id);

      // Store initial narrative and options
      setNarrativeAndOptions(result.initial_narrative, result.initial_options);

      // Hide onboarding
      setShowOnboarding(false);

      console.log("✅ Game initialized successfully");
    } catch (error) {
      console.error("❌ Onboarding failed:", error);
      throw error; // Let Onboarding component handle error display
    }
  };

  /**
   * Open decision modal
   */
  const handleMakeDecision = () => {
    openDecisionModal();
  };

  /**
   * Handle option selection
   */
  const handleChooseOption = async (chosenOption) => {
    try {
      const result = await decisionMutation.mutateAsync({
        sessionId,
        chosenOption,
      });

      // Close decision modal
      closeDecisionModal();

      // Store consequence data and open consequence modal
      setConsequenceData({
        consequence: result.consequence_narrative,
        learningMoment: result.learning_moment,
      });

      // Store next narrative and options
      setNarrativeAndOptions(result.next_narrative, result.next_options);

      console.log("✅ Decision processed successfully");
    } catch (error) {
      console.error("❌ Decision processing failed:", error);
    }
  };

  /**
   * Close consequence modal and continue to next decision
   */
  const handleCloseConsequence = () => {
    closeConsequenceModal();
  };

  /**
   * Start a new game
   */
  const handleNewGame = () => {
    // Clear all state
    resetGame();

    // Force reload to ensure clean slate
    window.location.reload();
  };

  // ===================================
  // RENDER: Onboarding
  // ===================================
  if (showOnboarding) {
    return (
      <div className="App">
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
  }

  // ===================================
  // RENDER: Game Dashboard
  // ===================================
  return (
    <div className="App">
      {/* API Status Bar */}
      <div className="api-status-bar">
        <div className={`status status-${apiStatus}`}>API: {apiStatus}</div>
        <button onClick={handleNewGame} className="btn-new-game">
          New Game
        </button>
      </div>

      {/* Error Banner for Decision Errors */}
      {decisionMutation.isError && (
        <div className="error-banner">
          <p>
            {decisionMutation.error?.response?.data?.detail ||
              "Failed to process decision. Please try again."}
          </p>
          <button onClick={() => decisionMutation.reset()}>✕</button>
        </div>
      )}

      {/* Loading State */}
      {isLoadingPlayerState && (
        <div className="loading-overlay">
          <div className="loading-spinner">Loading game state...</div>
        </div>
      )}

      {/* Game Dashboard */}
      {playerState && (
        <>
          <GameDashboard
            gameState={playerState}
            onMakeDecision={handleMakeDecision}
          />

          {/* Decision Modal */}
          {showDecisionModal && !showConsequenceModal && (
            <div className="modal-overlay" onClick={closeDecisionModal}>
              <div
                className="modal-content"
                onClick={(e) => e.stopPropagation()}
              >
                <button className="modal-close" onClick={closeDecisionModal}>
                  ×
                </button>

                <div className="narrative-section">
                  <h2>📖 Your Story</h2>
                  <p className="narrative-text">{currentNarrative}</p>
                </div>

                <div className="options-section">
                  <h3>What will you do?</h3>
                  <div className="options-grid">
                    {currentOptions.map((option, index) => (
                      <button
                        key={index}
                        className="option-button"
                        onClick={() => handleChooseOption(option)}
                        disabled={decisionMutation.isPending}
                      >
                        {decisionMutation.isPending ? "Processing..." : option}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Consequence Modal */}
          {showConsequenceModal && consequenceData && (
            <div className="modal-overlay" onClick={handleCloseConsequence}>
              <div
                className="modal-content"
                onClick={(e) => e.stopPropagation()}
              >
                <button
                  className="modal-close"
                  onClick={handleCloseConsequence}
                >
                  ×
                </button>

                <div className="consequence-section">
                  <h2>📊 Result</h2>
                  <p className="consequence-text">
                    {consequenceData.consequence}
                  </p>

                  {consequenceData.learningMoment && (
                    <div className="learning-moment">
                      <h3>💡 Learning Moment</h3>
                      <p>{consequenceData.learningMoment}</p>
                    </div>
                  )}

                  <button
                    className="btn-continue"
                    onClick={handleCloseConsequence}
                  >
                    Continue
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;
