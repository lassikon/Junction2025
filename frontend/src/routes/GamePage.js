import React, { useState } from "react";
import { useGameStore } from "../store/gameStore";
import { usePlayerState, useMakeDecision, useNextQuestion } from "../api/lifesim";
import TopBar from "../components/TopBar";
import MetricsBar from "../components/MetricsBar";
import SceneView from "../components/SceneView";
import ChoiceList from "../components/ChoiceList";
import ConsequenceModal from "../components/ConsequenceModal";
import TransactionHistory from "../components/TransactionHistory";
import TransactionLog from "../components/TransactionLog";
import FloatingChatbot from "../components/FloatingChatbot";
import "../styles/GamePage.css";

/**
 * GamePage - Main game interface
 * Displays player metrics, narrative, and decision choices
 */
const GamePage = () => {
  const [showTransactionHistory, setShowTransactionHistory] = useState(false);
  const [monthlyCashFlow, setMonthlyCashFlow] = useState(null);
  const [lifeMetricsChanges, setLifeMetricsChanges] = useState(null);
  const [fetchNextQuestion, setFetchNextQuestion] = useState(false);
  
  const {
    sessionId,
    showDecisionModal,
    openDecisionModal,
    closeDecisionModal,
    showConsequenceModal,
    closeConsequenceModal,
    consequenceData,
    setConsequenceData,
    transactionHistory,
    addTransaction,
    currentNarrative,
    currentOptions,
    setNarrativeAndOptions,
    showChatbot,
    toggleChatbot,
  } = useGameStore();

  const { data: playerState, isLoading: isLoadingPlayerState } =
    usePlayerState(sessionId);
  const decisionMutation = useMakeDecision();
  
  // Fetch next question when consequence is shown
  const { data: nextQuestionData, isLoading: isLoadingNextQuestion } = useNextQuestion(sessionId, fetchNextQuestion);
  
  // When next question data arrives, store it
  React.useEffect(() => {
    if (nextQuestionData && fetchNextQuestion) {
      console.log(nextQuestionData.was_cached ? "✅ Using cached next question" : "⚠️ Generated next question on-demand");
      setNarrativeAndOptions(nextQuestionData.next_narrative, nextQuestionData.next_options);
      setFetchNextQuestion(false); // Reset flag
    }
  }, [nextQuestionData, fetchNextQuestion, setNarrativeAndOptions]);

  const handleMakeDecision = () => {
    openDecisionModal();
  };

  const handleChooseOption = async (chosenOption, optionIndex) => {
    try {
      // Get the full option data to send back to backend
      const optionEffects = currentOptions[optionIndex];
      
      const result = await decisionMutation.mutateAsync({
        sessionId,
        chosenOption,
        optionIndex,
        optionEffects,  // Send full option data including effects
      });

      // Close decision modal
      closeDecisionModal();

      // Add monthly flow transaction first (if present)
      if (result.monthly_flow_transaction) {
        addTransaction(result.monthly_flow_transaction);
      }

      // Add decision transaction to history
      if (result.transaction_summary) {
        addTransaction(result.transaction_summary);
      }

      // Store monthly cash flow
      if (result.monthly_cash_flow) {
        setMonthlyCashFlow(result.monthly_cash_flow);
      }

      // Store life metrics changes
      if (result.life_metrics_changes) {
        setLifeMetricsChanges(result.life_metrics_changes);
      }

      // Store consequence data and open consequence modal
      setConsequenceData({
        consequence: result.consequence_narrative,
        learningMoment: result.learning_moment,
      });

      // If next question is not in response, trigger fetch
      if (!result.next_narrative || !result.next_options) {
        console.log("🔄 Fetching next question...");
        setFetchNextQuestion(true);
      } else {
        // Store next narrative and options if they were returned
        setNarrativeAndOptions(result.next_narrative, result.next_options);
      }

      console.log("✅ Decision processed successfully");
    } catch (error) {
      console.error("❌ Decision processing failed:", error);
    }
  };

  const handleCloseConsequence = () => {
    closeConsequenceModal();
  };

  if (isLoadingPlayerState) {
    return (
      <div className="game-page">
        <div className="loading-overlay">
          <div className="loading-spinner">Loading game state...</div>
        </div>
      </div>
    );
  }

  if (!playerState) {
    return (
      <div className="game-page">
        <div className="error-message">Failed to load game state</div>
      </div>
    );
  }

  return (
    <div className="game-page">
      <TopBar onShowTransactions={() => setShowTransactionHistory(true)} playerState={playerState} />

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

      {/* Main Game Content */}
      <div className="game-content">
        <MetricsBar gameState={playerState} />
        <div className="split-layout">
          <TransactionLog 
            transactions={transactionHistory} 
            currentMonthsPassed={playerState.months_passed}
            currentMonthPhase={playerState.month_phase}
          />
        </div>
        <SceneView
          gameState={playerState}
          onMakeDecision={handleMakeDecision}
          showOnlyBottom={true}
        />
      </div>

      {/* Decision Modal */}
      {showDecisionModal && !showConsequenceModal && (
        <ChoiceList
          narrative={currentNarrative}
          options={currentOptions}
          onChoose={handleChooseOption}
          onClose={closeDecisionModal}
          isProcessing={decisionMutation.isPending}
        />
      )}

      {/* Consequence Modal */}
      {showConsequenceModal && consequenceData && (
        <ConsequenceModal
          consequence={consequenceData.consequence}
          learningMoment={consequenceData.learningMoment}
          monthlyCashFlow={monthlyCashFlow}
          lifeMetricsChanges={lifeMetricsChanges}
          onClose={handleCloseConsequence}
        />
      )}

      {/* Transaction History Modal */}
      {showTransactionHistory && (
        <TransactionHistory
          sessionId={sessionId}
          onClose={() => setShowTransactionHistory(false)}
        />
      )}

      {/* Floating Financial Advisor Chatbot */}
      <FloatingChatbot
        sessionId={sessionId}
        isOpen={showChatbot}
        onToggle={toggleChatbot}
      />
    </div>
  );
};

export default GamePage;
