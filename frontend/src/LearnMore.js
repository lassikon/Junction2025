import React from 'react';
import './LearnMore.css';

function LearnMore({ onClose }) {
  return (
    <div className="learn-container">
      <header className="learn-header">
        <div>
            <h1>About Junction Finance</h1>
            <p className="subtitle">Building money-management skills and preparing for real-life financial challenges through a fun, safe game for teens and young adults</p>
        </div>
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
          We have also added an AI-powered chatbot to the web app to help users with questions about personal finance and in-game choices.
          The chatbot is powered by Google Gemini, which allows it to provide helpful, up-to-date responses across a wide range of financial topics.
          </p>
        </section>

        {/* Close button at bottom for convenience */}
        <div className="learn-cta" style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 16 }}>
          {onClose && (
            <button className="btn btn-secondary" onClick={onClose}>
              Close
            </button>
          )}
        </div>
      </main>
    </div>
  );
}

export default LearnMore;