import { apiClient } from "../api/client";
import { useAuthStore } from "../../store/authStore";
import { User, AuthTokens } from "../../types/auth";

export const authService = {
    async login(data: any) {
        const response = await apiClient.post<AuthTokens>("/auth/login", data);
        const tokens = response.data;

        // Fetch user info after login
        const userResponse = await apiClient.get<User>("/auth/me", {
            headers: { Authorization: `Bearer ${tokens.access_token}` }
        });

        useAuthStore.getState().setAuth(userResponse.data, tokens);
        return { user: userResponse.data, tokens };
    },

    async register(data: any) {
        const response = await apiClient.post<User>("/auth/register", data);
        return response.data;
    },

    async logout() {
        try {
            const tokens = useAuthStore.getState().tokens;
            if (tokens?.refresh_token) {
                await apiClient.post("/auth/logout", { refresh_token: tokens.refresh_token });
            }
        } finally {
            useAuthStore.getState().logout();
        }
    },

    async getMe() {
        const response = await apiClient.get<User>("/auth/me");
        return response.data;
    }
};
