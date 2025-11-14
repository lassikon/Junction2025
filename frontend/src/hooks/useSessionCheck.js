import { useEffect } from "react";
import { useGameStore } from "../store/gameStore";

export const useSessionCheck = () => {
  const { sessionId, showOnboarding, setShowOnboarding } = useGameStore();

  useEffect(() => {
    if (sessionId) {
      setShowOnboarding(false);
    }
  }, [sessionId, setShowOnboarding]);

  return { sessionId, showOnboarding };
};

