# LifeSim: Financial Independence Quest – Project Plan

## 1. Overview

**LifeSim: Financial Independence Quest** is an AI-driven life simulation game that helps young people understand financial decision-making and long-term consequences in an engaging, narrative way. Players progress through life events (e.g., first paycheck, moving out, buying a vehicle, taking a loan), make choices, and see how these decisions affect their financial independence, energy, motivation, and social life.

The core learning goal is to build intuition for budgeting, saving, investing, managing risk, and balancing well-being with financial goals. The game uses AI to generate personalized storylines, choices, and feedback based on each player's starting situation and play style.

## 2. Target Users & Learning Goals

### Target users:

- Upper secondary students, vocational students, and young adults at early stages of independence
- Youth getting their first bank card, first paycheck, or moving away from home

### Learning goals:

- Understand the trade-offs between spending, saving, and investing
- Experience the consequences of debt, interest, and overspending via safe simulation
- Build confidence in making financial decisions (especially for girls)
- Increase risk awareness and long-term thinking (especially for boys)
- Practice balancing money, energy, social life, and motivation like in real life

## 3. Core Game Design

The player controls a simplified "life timeline" where time progresses in steps (e.g., months or years). At each step, the AI generates a short narrative scene and 3–5 decision options. The player chooses an option, and the system updates their state across multiple metrics.

### Key elements of the game loop:

- Narrative event is generated (e.g., "You receive your first paycheck")
- 3–5 realistic choices are presented (buy new moped, fix old one, invest, save, etc.)
- Player chooses; the simulation engine updates metrics (money, energy, social, motivation, etc.)
- AI generates a consequence narrative explaining what happened and why
- Occasionally, curveball events occur (vet bills, car repairs, rent increase, etc.)

## 4. Player Metrics & Financial Independence Model

The player state is tracked via several metrics:

- **Money / Net Worth**: savings, investments, income, and debts
- **FI Score**: (Passive income / Monthly cost of living) × 100%
- **Energy**: affected by overtime, work–life balance, and stress
- **Motivation**: drives the willingness to take on new goals; low motivation can lead to poor choices
- **Social Life**: impacted by how much time and money is spent on friends, hobbies, and experiences
- **Financial Knowledge**: increases through "learning moments" and good decisions; improves future advice

The main objective is to increase FI Score towards 100%. However, the player is also encouraged to keep energy, motivation, and social life in a healthy range. Maximizing money while burning out or losing all social connection is possible but considered a "bad ending" from an educational perspective.

## 5. Curveballs & Life Events

Curveballs are unexpected events that make the simulation feel realistic and teach risk management. They are partly random and partly triggered by past choices (e.g., owning a cat increases the chance of vet bills).

### Example curveballs:

- Your cat suddenly needs urgent veterinary care (€1500)
- Your car breaks down and needs a €1200 repair
- Your landlord increases rent by 10%
- You receive a tax refund or unexpected bonus
- A friend invites you on an expensive trip abroad

## 6. Onboarding & Personalisation

At the start, the player completes a short onboarding questionnaire that sets their initial profile and starting conditions. This makes the simulation feel personal and more realistic.

### Onboarding questions may include:

- Age and city / cost-of-living level
- Current or future education path (e.g., vocational, university)
- Attitude towards risk (risk-averse, balanced, risk-seeking)
- Financial starting point (no savings / some savings / small debt)
- Future aspirations (own a car, travel, own a pet, etc.)

The backend uses this information to set starting income, cost levels, and specific life goals. AI can also adapt the tone of feedback: for example, encouraging and confidence-building for users with lower self-reported confidence.

## 7. Game Flow

### High-level flow:

1. **Onboarding**: user profile and initial state are created
2. **Intro narrative**: AI introduces the first situation (e.g., first summer job paycheck)
3. **Decision screen**: 3–5 options are presented
4. **Simulation**: the engine updates metrics based on the chosen option
5. **Consequence narrative**: AI explains what happened and what the player learned
6. **Next step**: more events, decisions, and occasional curveballs
7. **End state**: FI Score, burnout risk, and overall life balance summarized
8. **Leaderboard**: player sees how their FI Score compares to others

## 8. Technical Architecture (High-Level)

The system is split into a frontend (player-facing UI) and a backend (game logic, AI orchestration, and storage). Two team members focus on backend, and two on frontend. The architecture is intentionally simple so it can be implemented quickly during the hackathon and later expanded.

### Frontend – key responsibilities:

- Render onboarding form and send data to backend
- Display narrative events and decision options
- Show metric bars (money, FI%, energy, motivation, social, knowledge)
- Handle game loop UI (select option → loading state → show consequences)
- Render leaderboard and end-of-game summary

### Backend – key responsibilities:

- Store and update player state (in memory or simple database for hackathon)
- Implement deterministic parts of the simulation (metric updates, FI Score calculation)
- Call the AI model to generate narratives, decision options, and explanations
- Define event templates and curveball triggers
- Manage sessions and simple authentication if needed
- Aggregate and store scores for the leaderboard

## 9. Backend Plan & Milestones

**Assumed tech**: Node.js/TypeScript or Python (FastAPI/Flask), using an LLM API and simple storage (e.g., in-memory or SQLite).

### Milestone B1 – Core project setup (Backend Dev 1)

- Initialize backend project (framework, linting, basic folder structure)
- Implement health check endpoint (`/health`)
- Decide simple session handling (e.g., session ID in headers or cookies)

### Milestone B2 – Player state model & onboarding endpoint (Backend Dev 2)

- Define PlayerState data model (metrics, profile, current step)
- Implement `/api/onboarding` to receive questionnaire data and create initial PlayerState
- Return initial state and the first narrative request stub to frontend

### Milestone B3 – Simulation engine & event logic (Backend Dev 1)

- Implement pure functions to update metrics based on decisions
- Define a small set of event types (paycheck, rent, unexpected expense, etc.)
- Implement curveball logic (probabilities + triggers based on state)

### Milestone B4 – AI integration & narrative generation (Backend Dev 2)

- Implement an `/api/step` endpoint that:
  - Receives current PlayerState and chosen option
  - Runs the simulation engine to update metrics
  - Calls the AI model to generate a consequence narrative
  - Calls the AI model (or a ruleset) to generate the next set of options
  - Returns updated PlayerState, narrative, and options to the frontend

### Milestone B5 – Leaderboard & basic persistence (Backend Dev 1 & 2)

- Implement a minimal storage layer for final scores and FI Scores (e.g., SQLite / in-memory)
- Add `/api/finish` endpoint to store end results
- Add `/api/leaderboard` endpoint to fetch top FI Scores and basic stats

Each backend dev can pick one milestone at a time; if blocked on AI integration, they can focus on pure simulation logic and fake data responses so frontend can continue development.

## 10. Frontend Plan & Milestones

**Assumed tech**: React with TypeScript (or similar), using a simple component-based architecture.

### Milestone F1 – Skeleton layout & routing (Frontend Dev 1)

- Set up base React app and global styles
- Create basic pages: Onboarding, Game, Results, Leaderboard
- Implement simple navigation between pages (no real data yet)

### Milestone F2 – Onboarding UI (Frontend Dev 2)

- Implement a clean onboarding form with key questions (age, goals, risk attitude, etc.)
- Integrate with `/api/onboarding` to send data and receive initial state
- On success, navigate to Game screen

### Milestone F3 – Game screen: narrative + options (Frontend Dev 1)

- Design the main game view with:
  - Story/narrative text area
  - List of decision buttons/options
- Implement interaction with `/api/step` to send chosen option and receive the next state
- Add loading states and basic error handling

### Milestone F4 – Metrics HUD (Frontend Dev 2)

- Create visual components for metrics: money, FI%, energy, motivation, social, knowledge
- Use progress bars or simple icons + numbers to keep it readable for youth
- Update metrics on each step based on the PlayerState from backend

### Milestone F5 – End-of-game screen & leaderboard (Frontend Dev 1 & 2)

- Implement a results screen summarizing:
  - Final FI Score
  - Key best decisions and mistakes
  - Short AI-generated feedback (what the player learned)
- Implement a simple leaderboard view consuming `/api/leaderboard`

Frontend devs can work in parallel: while one builds the game loop, the other focuses on metrics UI and polishing the onboarding and results screens. Fake/mock backend responses can be used early on.

## 11. Stretch Goals (If Time Allows)

- Teacher mode: a view where an educator can see aggregated class results and discussion prompts
- Multiple difficulty modes (short session vs. deep simulation)
- Localization (Finnish + English)
- More detailed personas (e.g., different starting family backgrounds)
- More sophisticated AI feedback tailored to gender, confidence level, and risk profile

## 12. Alignment With Judging Criteria

- **User Experience (25%)**: intuitive UI, visual metrics, simple choices, fast feedback loops, and a motivational leaderboard
- **Innovation & Feasibility (25%)**: AI-driven personalization and narrative make each run unique; architecture is simple enough to be built during the hackathon and extended later
- **Research-Informed Design (25%)**: supports confidence-building for girls, risk-awareness for boys, and long-term financial thinking based on typical youth financial challenges
- **Educational Effectiveness (25%)**: focuses on learning-by-doing, surfacing the long-term consequences of everyday decisions, and reinforcing good habits through immediate feedback
