import React, { useState, useEffect } from "react";
import { useGameStore } from "../store/gameStore";
import {
  useHealthCheck,
  usePlayerState,
  useOnboarding,
  useMakeDecision,
} from "../api/gameApi";
import Onboarding from "../components/Onboarding";
import TopBar from "../components/TopBar";
import SceneView from "../components/SceneView";
import MetricsBar from "../components/MetricsBar";
import StatsDrawer from "../components/StatsDrawer";
import "./GamePage.css";

function GamePage() {
  // ===================================
  // LOCAL UI STATE
  // ===================================
  const [isStatsOpen, setIsStatsOpen] = useState(false);
  const [background, setBackground] = useState("sunny");

  // ===================================
  // ZUSTAND: Client state
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
  // RANDOMLY CHANGE BACKGROUND FOR VARIETY
  // ===================================
  useEffect(() => {
    const backgrounds = ["sunny", "rainy", "sunset", "cloudy", "indoor"];
    const randomBg =
      backgrounds[Math.floor(Math.random() * backgrounds.length)];
    setBackground(randomBg);
  }, [playerState?.current_step]);

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
  const handleChooseOption = async (chosenOption, optionIndex) => {
    try {
      const result = await decisionMutation.mutateAsync({
        sessionId,
        chosenOption,
        optionIndex,
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
      <div className="game-page-container">
        {onboardingMutation.isError && (
          <div className="game-page-error-banner">
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
    <div className="game-page-container">
      {/* API Status Bar */}
      <div className="game-page-api-status">
        <div className={`game-page-status game-page-status-${apiStatus}`}>
          API: {apiStatus}
        </div>
        <button onClick={handleNewGame} className="game-page-btn-new-game">
          New Game
        </button>
      </div>

      {/* Error Banner for Decision Errors */}
      {decisionMutation.isError && (
        <div className="game-page-error-banner">
          <p>
            {decisionMutation.error?.response?.data?.detail ||
              "Failed to process decision. Please try again."}
          </p>
          <button onClick={() => decisionMutation.reset()}>✕</button>
        </div>
      )}

      {/* Loading State */}
      {isLoadingPlayerState && (
        <div className="game-page-loading-overlay">
          <div className="game-page-loading-spinner">Loading game...</div>
        </div>
      )}

      {/* Game UI */}
      {playerState && (
        <>
          {/* Top Bar */}
          <TopBar
            playerName={playerState.name}
            money={playerState.money}
            fiScore={playerState.fi_score}
            onViewStats={() => setIsStatsOpen(true)}
          />

          {/* Game Content */}
          <div className="game-content">
            <div className="game-top-section">
              <div className="game-time-display">
                <span className="time-label">
                  Turn {playerState.current_step || 0}
                </span>
                {playerState.game_status && (
                  <span className="status-label">
                    Status: {playerState.game_status}
                  </span>
                )}
              </div>
              <button
                onClick={handleMakeDecision}
                className="game-page-btn-make-decision"
              >
                📝 Make Decision
              </button>
            </div>

            <div className="game-main">
              <div className="game-left">
                <SceneView
                  background={background}
                  character={playerState.avatar_key}
                  assets={Object.entries(playerState.assets || {})
                    .filter(([_, owned]) => owned)
                    .map(([name]) => ({ name, image: `${name}.png` }))}
                />
                <div className="metrics-container">
                  <MetricsBar
                    metrics={{
                      energy: playerState.energy,
                      motivation: playerState.motivation,
                      social_life: playerState.social_life,
                      financial_knowledge: playerState.financial_knowledge,
                    }}
                  />
                </div>
              </div>

              <div className="game-right">
                <div className="game-page-financial-summary">
                  <h3>💰 Financial Status</h3>
                  <div className="game-page-financial-grid">
                    <div className="game-page-financial-item">
                      <span className="game-page-label">Income:</span>
                      <span className="game-page-value">
                        €{playerState.monthly_income?.toLocaleString() || 0}
                      </span>
                    </div>
                    <div className="game-page-financial-item">
                      <span className="game-page-label">Expenses:</span>
                      <span className="game-page-value">
                        €{playerState.monthly_expenses?.toLocaleString() || 0}
                      </span>
                    </div>
                    <div className="game-page-financial-item">
                      <span className="game-page-label">Investments:</span>
                      <span className="game-page-value">
                        €{playerState.investments?.toLocaleString() || 0}
                      </span>
                    </div>
                    <div className="game-page-financial-item">
                      <span className="game-page-label">Passive Income:</span>
                      <span className="game-page-value">
                        €{playerState.passive_income?.toLocaleString() || 0}
                      </span>
                    </div>
                    <div className="game-page-financial-item">
                      <span className="game-page-label">Debts:</span>
                      <span className="game-page-value game-page-debt">
                        €{playerState.debts?.toLocaleString() || 0}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Stats Drawer */}
          <StatsDrawer
            isOpen={isStatsOpen}
            onClose={() => setIsStatsOpen(false)}
            playerState={playerState}
          />

          {/* Decision Modal */}
          {showDecisionModal && !showConsequenceModal && (
            <div
              className="game-page-modal-overlay"
              onClick={closeDecisionModal}
            >
              <div
                className="game-page-modal-content"
                onClick={(e) => e.stopPropagation()}
              >
                <button
                  className="game-page-modal-close"
                  onClick={closeDecisionModal}
                >
                  ×
                </button>

                <div className="game-page-narrative-section">
                  <h2>📖 Your Story</h2>
                  <p className="game-page-narrative-text">{currentNarrative}</p>
                </div>

                <div className="game-page-options-section">
                  <h3>What will you do?</h3>
                  <div className="game-page-options-grid">
                    {currentOptions.map((option, index) => (
                      <button
                        key={index}
                        className="game-page-option-button"
                        onClick={() => handleChooseOption(option, index)}
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
            <div
              className="game-page-modal-overlay"
              onClick={handleCloseConsequence}
            >
              <div
                className="game-page-modal-content"
                onClick={(e) => e.stopPropagation()}
              >
                <button
                  className="game-page-modal-close"
                  onClick={handleCloseConsequence}
                >
                  ×
                </button>

                <div className="game-page-consequence-section">
                  <h2>📊 Result</h2>
                  <p className="game-page-consequence-text">
                    {consequenceData.consequence}
                  </p>

                  {consequenceData.learningMoment && (
                    <div className="game-page-learning-moment">
                      <h3>💡 Learning Moment</h3>
                      <p>{consequenceData.learningMoment}</p>
                    </div>
                  )}

                  <button
                    className="game-page-btn-continue"
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

export default GamePage;
