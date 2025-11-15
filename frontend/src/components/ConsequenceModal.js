import React from "react";
import TransactionDisplay from "./TransactionDisplay";
import MonthlyCashFlow from "./MonthlyCashFlow";
import "../styles/ConsequenceModal.css";

/**
 * ConsequenceModal - Display decision consequences and learning moments
 */
const ConsequenceModal = ({ consequence, learningMoment, transactionSummary, monthlyCashFlow, onClose }) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content consequence-modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ×
        </button>

        <div className="consequence-section">
          <h2>📊 Result</h2>
          
          {/* Monthly cash flow - shown first */}
          {monthlyCashFlow && (
            <MonthlyCashFlow cashFlow={monthlyCashFlow} />
          )}
          
          <p className="consequence-text">{consequence}</p>

          {/* Transaction summary - decision effects */}
          {transactionSummary && (
            <TransactionDisplay transaction={transactionSummary} />
          )}

          {learningMoment && (
            <div className="learning-moment">
              <h3>💡 Learning Moment</h3>
              <p>{learningMoment}</p>
            </div>
          )}

          <button className="btn-continue" onClick={onClose}>
            Continue
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConsequenceModal;

