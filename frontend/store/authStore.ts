import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { AuthState, User, AuthTokens } from "../types/auth";

interface AuthStore extends AuthState {
    setAuth: (user: User, tokens: AuthTokens) => void;
    setTokens: (tokens: AuthTokens) => void;
    logout: () => void;
    setLoading: (isLoading: boolean) => void;
    _hasHydrated: boolean;
    setHasHydrated: (state: boolean) => void;
}

export const useAuthStore = create<AuthStore>()(
    persist(
        (set) => ({
            user: null,
            tokens: null,
            isAuthenticated: false,
            isLoading: false,
            _hasHydrated: false,

            setAuth: (user, tokens) =>
                set({
                    user,
                    tokens,
                    isAuthenticated: true,
                    isLoading: false,
                }),

            setTokens: (tokens) =>
                set((state) => ({
                    ...state,
                    tokens,
                })),

            logout: () =>
                set({
                    user: null,
                    tokens: null,
                    isAuthenticated: false,
                }),

            setLoading: (isLoading) => set({ isLoading }),
            setHasHydrated: (state) => set({ _hasHydrated: state }),
        }),
        {
            name: "vocaply-auth",
            storage: createJSONStorage(() => localStorage),
            partialize: (state) => ({
                user: state.user,
                tokens: state.tokens,
                isAuthenticated: state.isAuthenticated,
            }),
            onRehydrateStorage: () => (state) => {
                state?.setHasHydrated(true);
            },
        }
    )
);
