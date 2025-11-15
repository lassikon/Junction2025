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
      // VERSION CONTROL (increment to clear old cached data)
      // ===================================
      _storeVersion: 3, // Increment when store structure changes

      // ===================================
      // AUTHENTICATION STATE
      // ===================================
      authToken: null,
      accountId: null,
      username: null,
      displayName: null,
      hasCompletedOnboarding: false,
      isTestMode: false,

      setAuth: (authData) =>
        set({
          authToken: authData.token,
          accountId: authData.account_id,
          username: authData.username,
          displayName: authData.display_name,
          hasCompletedOnboarding: authData.has_completed_onboarding,
          isTestMode: false,
        }),

      clearAuth: () =>
        set({
          authToken: null,
          accountId: null,
          username: null,
          displayName: null,
          hasCompletedOnboarding: false,
          isTestMode: false,
        }),

      setTestMode: (isTest) => set({ isTestMode: isTest }),

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
      
      // Clear everything (logout)
      clearAll: () => 
        set({
          authToken: null,
          accountId: null,
          username: null,
          displayName: null,
          hasCompletedOnboarding: false,
          isTestMode: false,
          sessionId: null,
          showDecisionModal: false,
          showConsequenceModal: false,
          consequenceData: null,
          transactionHistory: [],
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
      // TRANSACTION HISTORY (rolling log of financial changes)
      // ===================================
      transactionHistory: [],

      addTransaction: (transaction) =>
        set((state) => ({
          transactionHistory: [...state.transactionHistory, transaction],
        })),

      clearTransactionHistory: () =>
        set({
          transactionHistory: [],
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
          transactionHistory: [],
        });
      },
    }),
    {
      name: "lifesim-game-storage", // localStorage key
      version: 2, // Must match _storeVersion - will clear old data automatically
      // Only persist essential data across sessions
      // NOTE: Do NOT persist currentNarrative/currentOptions - they must be fresh from API
      partialize: (state) => ({
        _storeVersion: state._storeVersion,
        sessionId: state.sessionId,
        soundEnabled: state.soundEnabled,
        animationsEnabled: state.animationsEnabled,
      }),
    }
  )
);
