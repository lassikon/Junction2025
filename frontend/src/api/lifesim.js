import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

/**
 * TanStack Query API hooks for LifeSim game
 *
 * These hooks handle ALL server communication:
 * - Automatic loading/error states
 * - Caching and cache invalidation
 * - Retries and background refetching
 * - Optimistic updates
 */

// ===================================
// QUERY: Get Player State
// ===================================
/**
 * Fetch current player state from the server
 * @param {string} sessionId - The player's session ID
 * @returns {UseQueryResult} - Query result with player state data
 */
export function usePlayerState(sessionId) {
  return useQuery({
    queryKey: ["playerState", sessionId],
    queryFn: async () => {
      if (!sessionId) return null;
      const response = await axios.get(`${API_URL}/api/game/${sessionId}`);
      return response.data;
    },
    enabled: !!sessionId, // Only run if sessionId exists
    staleTime: 30000, // Consider data fresh for 30 seconds
    refetchOnWindowFocus: false, // Don't refetch when tab regains focus
    retry: 2, // Retry failed requests twice
  });
}

// ===================================
// MUTATION: Onboarding (Create Player)
// ===================================
/**
 * Create a new player profile and initialize game state
 * @returns {UseMutationResult} - Mutation result for onboarding
 */
export function useOnboarding() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (onboardingData) => {
      const response = await axios.post(
        `${API_URL}/api/onboarding`,
        onboardingData
      );
      return response.data;
    },
    onSuccess: (data) => {
      // Cache the initial player state
      const sessionId = data.game_state.session_id;
      queryClient.setQueryData(["playerState", sessionId], data.game_state);

      console.log("✅ Onboarding successful:", data);
    },
    onError: (error) => {
      console.error("❌ Onboarding failed:", error);
    },
  });
}

// ===================================
// MUTATION: Make a Decision
// ===================================
/**
 * Process a player's decision and update game state
 * @returns {UseMutationResult} - Mutation result for making decisions
 */
export function useMakeDecision() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ sessionId, chosenOption, optionIndex, optionEffects }) => {
      const response = await axios.post(`${API_URL}/api/step`, {
        session_id: sessionId,
        chosen_option: chosenOption,
        option_index: optionIndex,
        option_effects: optionEffects,  // Send full option data with effects
      });
      return response.data;
    },
    onMutate: async ({ sessionId }) => {
      // Cancel any outgoing refetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({ queryKey: ["playerState", sessionId] });

      // Snapshot the previous value for rollback
      const previousState = queryClient.getQueryData([
        "playerState",
        sessionId,
      ]);

      // Optional: Optimistically update UI (uncomment if desired)
      // queryClient.setQueryData(['playerState', sessionId], (old) => ({
      //   ...old,
      //   // Apply optimistic changes here
      // }));

      return { previousState };
    },
    onSuccess: (data, { sessionId }) => {
      // Update the cached player state with new data
      queryClient.setQueryData(["playerState", sessionId], data.updated_state);

      console.log("✅ Decision processed:", data);
    },
    onError: (error, { sessionId }, context) => {
      // Rollback to previous state on error
      if (context?.previousState) {
        queryClient.setQueryData(
          ["playerState", sessionId],
          context.previousState
        );
      }
      console.error("❌ Decision failed:", error);
    },
  });
}

// ===================================
// QUERY: Get Leaderboard
// ===================================
/**
 * Fetch the game leaderboard
 * @param {number} limit - Number of top players to fetch
 * @returns {UseQueryResult} - Query result with leaderboard data
 */
export function useLeaderboard(limit = 10) {
  return useQuery({
    queryKey: ["leaderboard", limit],
    queryFn: async () => {
      const response = await axios.get(
        `${API_URL}/api/leaderboard?limit=${limit}`
      );
      return response.data;
    },
    staleTime: 60000, // Cache for 1 minute
    refetchInterval: 30000, // Auto-refresh every 30 seconds
    retry: 2,
  });
}

// ===================================
// MUTATION: Finish Game (Submit to Leaderboard)
// ===================================
/**
 * Finish the game and submit score to leaderboard
 * @returns {UseMutationResult} - Mutation result for finishing game
 */
export function useFinishGame() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ sessionId, nickname }) => {
      const response = await axios.post(`${API_URL}/api/finish`, {
        session_id: sessionId,
        player_nickname: nickname,
      });
      return response.data;
    },
    onSuccess: () => {
      // Invalidate leaderboard to fetch fresh data
      queryClient.invalidateQueries({ queryKey: ["leaderboard"] });
      console.log("✅ Game finished and submitted to leaderboard");
    },
    onError: (error) => {
      console.error("❌ Failed to finish game:", error);
    },
  });
}

// ===================================
// UTILITY: Health Check
// ===================================
/**
 * Check API health status
 * @returns {UseQueryResult} - Query result with health status
 */
export function useHealthCheck() {
  return useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/health`);
      return response.data;
    },
    staleTime: 60000, // Check every minute
    refetchInterval: 60000,
    retry: 1,
  });
}
