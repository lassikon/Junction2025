// ============================================
// QUICK REFERENCE: TanStack Query + Zustand
// ============================================

// ============================================
// 1. ZUSTAND STORE USAGE
// ============================================

import { useGameStore } from "./store/gameStore";

// Get single value
const sessionId = useGameStore((state) => state.sessionId);

// Get multiple values
const { sessionId, openModal, closeModal } = useGameStore();

// Call an action
const setSessionId = useGameStore((state) => state.setSessionId);
setSessionId("new-session-123");

// All available Zustand state & actions:
const {
  // Session
  sessionId,
  setSessionId,
  clearSession,

  // Modals
  showDecisionModal,
  showConsequenceModal,
  showOnboarding,
  openDecisionModal,
  closeDecisionModal,
  openConsequenceModal,
  closeConsequenceModal,
  setShowOnboarding,

  // Consequence data
  consequenceData,
  setConsequenceData,

  // UI preferences
  soundEnabled,
  animationsEnabled,
  toggleSound,
  toggleAnimations,

  // Narrative cache
  currentNarrative,
  currentOptions,
  setNarrativeAndOptions,
  clearNarrativeAndOptions,

  // Reset
  resetGame,
} = useGameStore();

// ============================================
// 2. TANSTACK QUERY HOOKS
// ============================================

import {
  useHealthCheck,
  usePlayerState,
  useOnboarding,
  useMakeDecision,
  useLeaderboard,
  useFinishGame,
} from "./api/gameApi";

// --- QUERIES (GET data) ---

// Health check
const { data, isLoading, isError, error } = useHealthCheck();
// Returns: { status: "healthy" }

// Get player state
const { data: playerState, isLoading } = usePlayerState(sessionId);
// Returns: { session_id, money, fi_score, energy, ... }

// Get leaderboard
const { data: leaderboard } = useLeaderboard(10);
// Returns: [{ rank, player_nickname, final_fi_score, ... }]

// --- MUTATIONS (POST/PUT data) ---

// Onboarding
const onboardingMutation = useOnboarding();
await onboardingMutation.mutateAsync(onboardingData);
// Check state: onboardingMutation.isPending, .isError, .isSuccess

// Make decision
const decisionMutation = useMakeDecision();
await decisionMutation.mutateAsync({ sessionId, chosenOption });
// Check state: decisionMutation.isPending, .isError, .isSuccess

// Finish game
const finishMutation = useFinishGame();
await finishMutation.mutateAsync({ sessionId, nickname });

// ============================================
// 3. COMMON PATTERNS
// ============================================

// --- Pattern 1: Display loading state ---
function MyComponent() {
  const sessionId = useGameStore((state) => state.sessionId);
  const { data, isLoading, isError, error } = usePlayerState(sessionId);

  if (isLoading) return <div>Loading...</div>;
  if (isError) return <div>Error: {error.message}</div>;

  return <div>Money: €{data.money}</div>;
}

// --- Pattern 2: Make API call on button click ---
function DecisionButton() {
  const sessionId = useGameStore((state) => state.sessionId);
  const mutation = useMakeDecision();

  const handleClick = async () => {
    try {
      const result = await mutation.mutateAsync({
        sessionId,
        chosenOption: "Save money",
      });
      console.log("Success!", result);
    } catch (error) {
      console.error("Failed:", error);
    }
  };

  return (
    <button onClick={handleClick} disabled={mutation.isPending}>
      {mutation.isPending ? "Processing..." : "Make Decision"}
    </button>
  );
}

// --- Pattern 3: Reset everything ---
function NewGameButton() {
  const resetGame = useGameStore((state) => state.resetGame);

  return (
    <button
      onClick={() => {
        resetGame(); // Clears Zustand
        window.location.reload(); // Force refresh
      }}
    >
      New Game
    </button>
  );
}

// --- Pattern 4: Open modal with data ---
function GameDashboard() {
  const { openDecisionModal, setNarrativeAndOptions } = useGameStore();

  const handleMakeDecision = () => {
    // Set narrative first
    setNarrativeAndOptions("You received your first paycheck!", [
      "Save it",
      "Invest it",
      "Spend it",
    ]);

    // Then open modal
    openDecisionModal();
  };

  return <button onClick={handleMakeDecision}>Make Decision</button>;
}

// --- Pattern 5: Conditional rendering based on query ---
function GameScreen() {
  const sessionId = useGameStore((state) => state.sessionId);
  const { data: playerState } = usePlayerState(sessionId);

  // playerState is automatically cached and updates on mutations!

  return (
    <div>
      <h1>FI Score: {playerState?.fi_score || 0}%</h1>
      <p>Money: €{playerState?.money || 0}</p>
    </div>
  );
}

// ============================================
// 4. BACKEND API ENDPOINTS (for reference)
// ============================================

// GET /health
// → { status: "healthy" }

// GET /api/game/{session_id}
// → { session_id, current_step, money, fi_score, ... }

// POST /api/onboarding
// Body: { player_name, age, city, education_path, ... }
// → { game_state, initial_narrative, initial_options }

// POST /api/step
// Body: { session_id, chosen_option }
// → { updated_state, consequence_narrative, learning_moment, next_narrative, next_options }

// GET /api/leaderboard?limit=10
// → [{ rank, player_nickname, final_fi_score, ... }]

// POST /api/finish
// Body: { session_id, player_nickname }
// → { success: true }

// ============================================
// 5. DEBUGGING TIPS
// ============================================

// Open React Query DevTools (bottom-left in dev mode)
// - See all active queries
// - Inspect cached data
// - Manually trigger refetch
// - View query timeline

// Check Zustand state
console.log(useGameStore.getState());

// Check localStorage
console.log(localStorage.getItem("lifesim-game-storage"));

// Manually clear cache
import { useQueryClient } from "@tanstack/react-query";
const queryClient = useQueryClient();
queryClient.clear(); // Clear all cached data

// Invalidate specific query
queryClient.invalidateQueries({ queryKey: ["playerState", sessionId] });
