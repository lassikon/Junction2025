import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import Onboarding from "./components/Onboarding";
import GameDashboard from "./components/GameDashboard";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState("checking");
  const [gameState, setGameState] = useState(null);
  const [showOnboarding, setShowOnboarding] = useState(true);
  const [error, setError] = useState(null);
  const [currentNarrative, setCurrentNarrative] = useState("");
  const [currentOptions, setCurrentOptions] = useState([]);
  const [showDecisionModal, setShowDecisionModal] = useState(false);
  const [consequenceNarrative, setConsequenceNarrative] = useState("");
  const [learningMoment, setLearningMoment] = useState(null);

  useEffect(() => {
    // Check API health on mount
    axios
      .get(`${API_URL}/health`)
      .then(() => setApiStatus("connected"))
      .catch(() => setApiStatus("disconnected"));

    // Check if there's an existing game session in localStorage
    const savedSessionId = localStorage.getItem("lifesim_session_id");
    const savedGameState = localStorage.getItem("lifesim_game_state");
    const savedNarrative = localStorage.getItem("lifesim_narrative");
    const savedOptions = localStorage.getItem("lifesim_options");
    
    if (savedSessionId && savedGameState) {
      try {
        setGameState(JSON.parse(savedGameState));
        if (savedNarrative) setCurrentNarrative(savedNarrative);
        if (savedOptions) setCurrentOptions(JSON.parse(savedOptions));
        setShowOnboarding(false);
      } catch (e) {
        console.error("Error parsing saved game state:", e);
        localStorage.removeItem("lifesim_session_id");
        localStorage.removeItem("lifesim_game_state");
        localStorage.removeItem("lifesim_narrative");
        localStorage.removeItem("lifesim_options");
      }
    }
  }, []);

  const handleOnboardingComplete = async (onboardingData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/api/onboarding`, onboardingData);
      const onboardingResponse = response.data;
      
      // Extract game_state from the response
      const newGameState = onboardingResponse.game_state;
      
      // Save to state
      setGameState(newGameState);
      setShowOnboarding(false);
      
      // Save to localStorage for persistence
      localStorage.setItem("lifesim_session_id", newGameState.session_id);
      localStorage.setItem("lifesim_game_state", JSON.stringify(newGameState));
      
      // Store narrative and options
      setCurrentNarrative(onboardingResponse.initial_narrative);
      setCurrentOptions(onboardingResponse.initial_options);
      localStorage.setItem("lifesim_narrative", onboardingResponse.initial_narrative);
      localStorage.setItem("lifesim_options", JSON.stringify(onboardingResponse.initial_options));
      
      console.log("Game initialized successfully:", newGameState);
      console.log("Initial narrative:", onboardingResponse.initial_narrative);
      console.log("Initial options:", onboardingResponse.initial_options);
    } catch (error) {
      console.error("Error during onboarding:", error);
      setError(error.response?.data?.detail || "Failed to initialize game. Please try again.");
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleOnboardingError = (error) => {
    setError(error.response?.data?.detail || "An error occurred during onboarding.");
  };

  const handleMakeDecision = () => {
    setShowDecisionModal(true);
  };

  const handleChooseOption = async (chosenOption) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/api/step`, {
        session_id: gameState.session_id,
        chosen_option: chosenOption
      });
      
      const decisionResponse = response.data;
      
      // Update game state
      const updatedState = decisionResponse.updated_state;
      setGameState(updatedState);
      localStorage.setItem("lifesim_game_state", JSON.stringify(updatedState));
      
      // Store consequence and learning moment
      setConsequenceNarrative(decisionResponse.consequence_narrative);
      setLearningMoment(decisionResponse.learning_moment);
      
      // Store next narrative and options
      setCurrentNarrative(decisionResponse.next_narrative);
      setCurrentOptions(decisionResponse.next_options);
      localStorage.setItem("lifesim_narrative", decisionResponse.next_narrative);
      localStorage.setItem("lifesim_options", JSON.stringify(decisionResponse.next_options));
      
      console.log("Decision processed:", decisionResponse);
    } catch (error) {
      console.error("Error processing decision:", error);
      setError(error.response?.data?.detail || "Failed to process decision. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleCloseConsequence = () => {
    setConsequenceNarrative("");
    setLearningMoment(null);
    setShowDecisionModal(false);
  };

  const handleNewGame = () => {
    localStorage.removeItem("lifesim_session_id");
    localStorage.removeItem("lifesim_game_state");
    localStorage.removeItem("lifesim_narrative");
    localStorage.removeItem("lifesim_options");
    setGameState(null);
    setCurrentNarrative("");
    setCurrentOptions([]);
    setShowOnboarding(true);
    setError(null);
    window.location.reload(); // Force reload to clear any cached state
  };

  // Show onboarding if no game state exists
  if (showOnboarding) {
    return (
      <div className="App">
        {error && (
          <div className="error-banner">
            <p>{error}</p>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}
        <Onboarding 
          onComplete={handleOnboardingComplete}
          onError={handleOnboardingError}
        />
      </div>
    );
  }

  // Show game dashboard if game state exists
  return (
    <div className="App">
      <div className="api-status-bar">
        <div className={`status status-${apiStatus}`}>
          API: {apiStatus}
        </div>
        <button onClick={handleNewGame} className="btn-new-game">
          New Game
        </button>
      </div>
      
      {error && (
        <div className="error-banner">
          <p>{error}</p>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}
      
      {gameState && (
        <>
          <GameDashboard 
            gameState={gameState}
            onMakeDecision={handleMakeDecision}
          />
          
          {/* Decision Modal */}
          {showDecisionModal && !consequenceNarrative && (
            <div className="modal-overlay" onClick={() => setShowDecisionModal(false)}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={() => setShowDecisionModal(false)}>×</button>
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
                        disabled={loading}
                      >
                        {option}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Consequence Modal */}
          {consequenceNarrative && (
            <div className="modal-overlay" onClick={handleCloseConsequence}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={handleCloseConsequence}>×</button>
                <div className="consequence-section">
                  <h2>📊 Result</h2>
                  <p className="consequence-text">{consequenceNarrative}</p>
                  
                  {learningMoment && (
                    <div className="learning-moment">
                      <h3>💡 Learning Moment</h3>
                      <p>{learningMoment}</p>
                    </div>
                  )}
                  
                  <button className="btn-continue" onClick={handleCloseConsequence}>
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
