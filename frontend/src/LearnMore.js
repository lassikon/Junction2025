import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LearnMore.css';

function LearnMore() {
  const navigate = useNavigate();

  return (
    <div className="learn-container">
      <header className="learn-header">
        <h1>About Junction Finance</h1>
        <p className="subtitle">Learning financial control through a fun, safe game for teens & young adults</p>
      </header>

      <main className="learn-main">
        <section className="learn-section">
          <h2>What this site teaches</h2>
          <p>
            Junction Finance is an educational game designed to help teens and young adults build essential
            money-management skills. Players practice budgeting, saving, investing basics, and making real-world
            financial decisions in realistic, risk-free scenarios.
          </p>
        </section>

        <section className="learn-section">
          <h2>How the game works</h2>
          <ul>
            <li>Scenario-based challenges (jobs, expenses, unexpected events)</li>
            <li>Budgeting and saving mechanics with clear feedback</li>
            <li>Interactive chat assistant provides guidance and explanations</li>
            <li>Mini-quizzes and progress tracking to reinforce learning</li>
            <li>Rewards and leveling to keep motivation high</li>
          </ul>
        </section>

        <section className="learn-section">
          <h2>Why it helps</h2>
          <p>
            The game turns abstract financial concepts into hands-on practice. Players learn consequences of choices,
            build confidence managing money, and develop habits that transfer to real life.
          </p>
        </section>

        <section className="learn-section">
          <h2>Chatbot</h2>
          <p>
            We have also added a chatbot to our website to help users with any questions they may have about personal finance. 
            The chatbot is powered by OpenAI's GPT-3.5-turbo model, which allows it to provide accurate and helpful responses to a wide range of financial topics.
          </p>
        </section>

        <div className="learn-cta">
          <button className="btn btn-primary" onClick={() => navigate('/chat')}>
            Start Chatting
          </button>
          <button className="btn btn-secondary" onClick={() => navigate('/')}>
            Back to Home
          </button>
        </div>
      </main>
    </div>
  );
}

export default LearnMore;