import React, { createContext, useContext, useState, useEffect } from 'react';
import * as api from '../api/lifesim';

const GameContext = createContext();

export function useGame() {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error('useGame must be used within GameProvider');
  }
  return context;
}

export function GameProvider({ children }) {
  const [playerState, setPlayerState] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const startGame = async (name, avatarKey) => {
    try {
      setLoading(true);
      setError(null);
      const state = await api.login(name, avatarKey);
      setPlayerState(state);
      return state;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const makeChoice = async (choiceId) => {
    try {
      setLoading(true);
      setError(null);
      const newState = await api.submitChoice(choiceId);
      setPlayerState(newState);
      return newState;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const refreshState = async () => {
    try {
      setLoading(true);
      const state = await api.getPlayerState();
      setPlayerState(state);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetGameState = async () => {
    try {
      setLoading(true);
      await api.resetGame();
      setPlayerState(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const value = {
    playerState,
    loading,
    error,
    startGame,
    makeChoice,
    refreshState,
    resetGameState
  };

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}

