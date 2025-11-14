import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { GameProvider } from './context/GameContext';
import LoginPage from './routes/LoginPage';
import GamePage from './routes/GamePage';
import SettingsPage from './routes/SettingsPage';
import MockHome from './MockHome';
import Chat from './Chat';
import './App.css';

function App() {
  return (
    <GameProvider>
      <Router>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/game" element={<GamePage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/old-home" element={<MockHome />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </Router>
    </GameProvider>
  );
}

export default App;