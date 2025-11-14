import React from 'react';
import './ChoiceList.css';

function ChoiceList({ narrative, choices, onChoiceClick, disabled }) {
  return (
    <div className="choice-list">
      <div className="narrative-box">
        <p className="narrative-text">{narrative}</p>
      </div>
      
      <div className="choices-container">
        <h3 className="choices-title">What will you do?</h3>
        <div className="choices">
          {choices.map((choice) => (
            <button
              key={choice.id}
              className="choice-button"
              onClick={() => onChoiceClick(choice.id)}
              disabled={disabled}
            >
              <div className="choice-label">{choice.label}</div>
              {choice.description && (
                <div className="choice-description">{choice.description}</div>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ChoiceList;

