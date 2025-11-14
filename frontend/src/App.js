import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MockHome from './MockHome';
import Chat from './Chat'; // Rename your current chat logic to Chat.js
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MockHome />} />
        <Route path="/chat" element={<Chat />} />
      </Routes>
    </Router>
  );
}

export default App;