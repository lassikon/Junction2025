import React, { useState } from "react";
import { useGameStore } from "../store/gameStore";
import { usePlayerState, useMakeDecision } from "../api/lifesim";
import TopBar from "../components/TopBar";
import MetricsBar from "../components/MetricsBar";
import SceneView from "../components/SceneView";
import ChoiceList from "../components/ChoiceList";
import ConsequenceModal from "../components/ConsequenceModal";
import TransactionHistory from "../components/TransactionHistory";
import "../styles/GamePage.css";

/**
 * GamePage - Main game interface
 * Displays player metrics, narrative, and decision choices
 */
const GamePage = () => {
  const [showTransactionHistory, setShowTransactionHistory] = useState(false);
  const [monthlyCashFlow, setMonthlyCashFlow] = useState(null);
  
  const {
    sessionId,
    showDecisionModal,
    openDecisionModal,
    closeDecisionModal,
    showConsequenceModal,
    closeConsequenceModal,
    consequenceData,
    setConsequenceData,
    lastTransaction,
    setLastTransaction,
    currentNarrative,
    currentOptions,
    setNarrativeAndOptions,
  } = useGameStore();

  const { data: playerState, isLoading: isLoadingPlayerState } =
    usePlayerState(sessionId);
  const decisionMutation = useMakeDecision();

  const handleMakeDecision = () => {
    openDecisionModal();
  };

  const handleChooseOption = async (chosenOption, optionIndex) => {
    try {
      const result = await decisionMutation.mutateAsync({
        sessionId,
        chosenOption,
        optionIndex,
      });

      // Close decision modal
      closeDecisionModal();

      // Store transaction summary
      if (result.transaction_summary) {
        setLastTransaction(result.transaction_summary);
      }

      // Store monthly cash flow
      if (result.monthly_cash_flow) {
        setMonthlyCashFlow(result.monthly_cash_flow);
      }
      if (result.monthly_cash_flow) {
        setMonthlyCashFlow(result.monthly_cash_flow);
      }

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
      <TopBar onShowTransactions={() => setShowTransactionHistory(true)} />

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
        <SceneView
          gameState={playerState}
          onMakeDecision={handleMakeDecision}
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
          transactionSummary={lastTransaction}
          monthlyCashFlow={monthlyCashFlow}
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
    </div>
  );
};

export default GamePage;
