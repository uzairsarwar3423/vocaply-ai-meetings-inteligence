import axios from "axios";
import { useAuthStore } from "../../store/authStore";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Request Interceptor: Add Authorization header rre
apiClient.interceptors.request.use(
    (config) => {
        const tokens = useAuthStore.getState().tokens;
        if (tokens?.access_token && !config.headers.Authorization) {
            config.headers.Authorization = `Bearer ${tokens.access_token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response Interceptor: Handle token refresh on 401 gff
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refresh_token = useAuthStore.getState().tokens?.refresh_token;

                if (!refresh_token) {
                    useAuthStore.getState().logout();
                    return Promise.reject(error);
                }

                const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                    refresh_token,
                });

                const newTokens = response.data;
                useAuthStore.getState().setTokens(newTokens);

                originalRequest.headers.Authorization = `Bearer ${newTokens.access_token}`;
                return apiClient(originalRequest);
            } catch (err) {
                useAuthStore.getState().logout();
                return Promise.reject(err);
            }
        }

        return Promise.reject(error);
    }
);
