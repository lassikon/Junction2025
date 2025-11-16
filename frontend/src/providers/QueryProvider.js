import React, { useEffect } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useGameStore } from "../store/gameStore";
import { refreshAuth } from "../api/auth";

// Create a QueryClient instance
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
      staleTime: 30000,
    },
    mutations: {
      retry: 1,
    },
  },
});

export const QueryProvider = ({ children }) => {
  const setAuth = useGameStore((state) => state.setAuth);

  // On app boot, try to silently rehydrate auth using HttpOnly refresh cookie.
  useEffect(() => {
    let mounted = true;

    async function tryRefresh() {
      try {
        const auth = await refreshAuth();
        if (auth && mounted) {
          // hydrate in-memory auth state
          setAuth(auth);
        }
      } catch (e) {
        // ignore - not authenticated
        // console.debug("refresh failed", e);
      }
    }

    tryRefresh();

    return () => {
      mounted = false;
    };
  }, [setAuth]);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* React Query Devtools removed for production UI cleanliness */}
    </QueryClientProvider>
  );
};

