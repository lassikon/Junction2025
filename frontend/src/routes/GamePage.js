import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGame } from '../context/GameContext';
import TopBar from '../components/TopBar';
import SceneView from '../components/SceneView';
import ChoiceList from '../components/ChoiceList';
import MetricsBar from '../components/MetricsBar';
import StatsDrawer from '../components/StatsDrawer';
import './GamePage.css';

function GamePage() {
  const { playerState, makeChoice, loading } = useGame();
  const navigate = useNavigate();
  const [isStatsOpen, setIsStatsOpen] = useState(false);
  const [background, setBackground] = useState('sunny');

  // Redirect to login if no player state
  useEffect(() => {
    if (!playerState) {
      navigate('/');
    }
  }, [playerState, navigate]);

  // Randomly change background occasionally for variety
  useEffect(() => {
    const backgrounds = ['sunny', 'rainy', 'sunset', 'cloudy', 'indoor'];
    const randomBg = backgrounds[Math.floor(Math.random() * backgrounds.length)];
    setBackground(randomBg);
  }, [playerState?.turn]);

  if (!playerState) {
    return (
      <div className="game-page">
        <div className="loading-screen">
          <p>Loading game...</p>
        </div>
      </div>
    );
  }

  const handleChoiceClick = async (choiceId) => {
    try {
      await makeChoice(choiceId);
    } catch (error) {
      console.error('Failed to submit choice:', error);
    }
  };

  return (
    <div className="game-page">
      <TopBar
        playerName={playerState.name}
        money={playerState.metrics.money}
        fiScore={playerState.metrics.fiScore}
        onViewStats={() => setIsStatsOpen(true)}
      />

      <div className="game-content">
        <div className="game-top-section">
          <div className="game-time-display">
            <span className="time-label">Year {playerState.year} • Month {playerState.month}</span>
            <span className="turn-label">Turn {playerState.turn}</span>
          </div>
        </div>

        <div className="game-main">
          <div className="game-left">
            <SceneView
              background={background}
              character={playerState.avatarKey}
              assets={playerState.assets}
            />
            <div className="metrics-container">
              <MetricsBar metrics={playerState.metrics} />
            </div>
          </div>

          <div className="game-right">
            <ChoiceList
              narrative={playerState.currentNarrative}
              choices={playerState.currentChoices}
              onChoiceClick={handleChoiceClick}
              disabled={loading}
            />
          </div>
        </div>
      </div>

      <StatsDrawer
        isOpen={isStatsOpen}
        onClose={() => setIsStatsOpen(false)}
        playerState={playerState}
      />
    </div>
  );
}

export default GamePage;

