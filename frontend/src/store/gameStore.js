import { create } from "zustand";
import { persist } from "zustand/middleware";

/**
 * Zustand store for LOCAL game UI state and session management
 *
 * This store handles:
 * - Session ID persistence
 * - Modal visibility states
 * - UI preferences (sound, animations, etc.)
 *
 * Does NOT handle:
 * - Player metrics (managed by TanStack Query)
 * - API calls (managed by TanStack Query)
 */
export const useGameStore = create(
  persist(
    (set, get) => ({
      // ===================================
      // SESSION STATE
      // ===================================
      sessionId: null,

      setSessionId: (id) => set({ sessionId: id }),

      clearSession: () =>
        set({
          sessionId: null,
          showDecisionModal: false,
          showConsequenceModal: false,
          consequenceData: null,
        }),

      // ===================================
      // MODAL STATES
      // ===================================
      showDecisionModal: false,
      showConsequenceModal: false,
      showOnboarding: true,

      openDecisionModal: () => set({ showDecisionModal: true }),
      closeDecisionModal: () => set({ showDecisionModal: false }),

      openConsequenceModal: () => set({ showConsequenceModal: true }),
      closeConsequenceModal: () =>
        set({
          showConsequenceModal: false,
          consequenceData: null,
        }),

      setShowOnboarding: (show) => set({ showOnboarding: show }),

      // ===================================
      // CONSEQUENCE DATA (temporary)
      // ===================================
      consequenceData: null,

      setConsequenceData: (data) =>
        set({
          consequenceData: data,
          showConsequenceModal: true,
        }),

      // ===================================
      // UI PREFERENCES
      // ===================================
      soundEnabled: true,
      animationsEnabled: true,

      toggleSound: () =>
        set((state) => ({
          soundEnabled: !state.soundEnabled,
        })),

      toggleAnimations: () =>
        set((state) => ({
          animationsEnabled: !state.animationsEnabled,
        })),

      // ===================================
      // NARRATIVE & OPTIONS (cached from last API response)
      // ===================================
      currentNarrative: "",
      currentOptions: [],

      setNarrativeAndOptions: (narrative, options) =>
        set({
          currentNarrative: narrative,
          currentOptions: options,
        }),

      clearNarrativeAndOptions: () =>
        set({
          currentNarrative: "",
          currentOptions: [],
        }),

      // ===================================
      // RESET ALL
      // ===================================
      resetGame: () => {
        set({
          sessionId: null,
          showDecisionModal: false,
          showConsequenceModal: false,
          showOnboarding: true,
          consequenceData: null,
          currentNarrative: "",
          currentOptions: [],
        });
      },
    }),
    {
      name: "lifesim-game-storage", // localStorage key
      // Only persist essential data across sessions
      partialize: (state) => ({
        sessionId: state.sessionId,
        soundEnabled: state.soundEnabled,
        animationsEnabled: state.animationsEnabled,
        currentNarrative: state.currentNarrative,
        currentOptions: state.currentOptions,
      }),
    }
  )
);
