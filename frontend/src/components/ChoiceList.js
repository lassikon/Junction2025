import React from "react";
import "../styles/ChoiceList.css";

/**
 * ChoiceList - Modal displaying narrative and decision options
 */
const ChoiceList = ({
  narrative,
  options,
  onChoose,
  onClose,
  isProcessing,
}) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ×
        </button>

        <div className="narrative-section">
          <h2>📖 Your Story</h2>
          <p className="narrative-text">{narrative}</p>
        </div>

        <div className="options-section">
          <h3>What will you do?</h3>
          <div className="options-grid">
            {options.map((option, index) => {
              // Handle both old format (string) and new format (object with text field)
              const optionText = typeof option === 'string' ? option : option.text;
              return (
                <button
                  key={index}
                  className="option-button"
                  onClick={() => onChoose(optionText, index)}
                  disabled={isProcessing}
                >
                  {isProcessing ? "Processing..." : optionText}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChoiceList;
