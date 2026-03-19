import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useAuthStore } from "../store/authStore";
import { apiClient } from "../lib/api/client";
import { User, AuthTokens } from "../types/auth";

const ZOOM_OAUTH_URL = process.env.NEXT_PUBLIC_ZOOM_OAUTH_URL || "https://zoom.us/oauth/authorize";
const ZOOM_CLIENT_ID = process.env.NEXT_PUBLIC_ZOOM_CLIENT_ID;
const ZOOM_REDIRECT_URI = process.env.NEXT_PUBLIC_ZOOM_REDIRECT_URI;

export const useZoomAuth = () => {
    const router = useRouter();
    const setAuth = useAuthStore((state) => state.setAuth);

    /**
     * Redirect user to Zoom OAuth authorization URL
     */
    const initiateZoomLogin = useCallback(() => {
        if (!ZOOM_CLIENT_ID || !ZOOM_REDIRECT_URI) {
            toast.error("Zoom OAuth configuration is missing");
            return;
        }

        const params = new URLSearchParams({
            response_type: "code",
            client_id: ZOOM_CLIENT_ID,
            redirect_uri: ZOOM_REDIRECT_URI,
            state: crypto.getRandomValues(new Uint8Array(16)).toString(),
        });

        window.location.href = `${ZOOM_OAUTH_URL}?${params.toString()}`;
    }, []);

    /**
     * Handle Zoom OAuth callback
     * Exchange authorization code for app tokens
     */
    const handleZoomCallback = useCallback(
        async (code: string) => {
            try {
                // Send authorization code to backend
                const response = await apiClient.post<AuthTokens>(
                    "/auth/zoom/callback",
                    { code }
                );

                const tokens = response.data;

                // Fetch user info after successful auth
                const userResponse = await apiClient.get<User>("/auth/me", {
                    headers: { Authorization: `Bearer ${tokens.access_token}` },
                });

                // Store auth state
                setAuth(userResponse.data, tokens);

                toast.success("Successfully authenticated with Zoom!");
                router.push("/dashboard");
            } catch (error: any) {
                const message = error.response?.data?.detail || 
                    "Failed to authenticate with Zoom";
                toast.error(message);
                console.error("Zoom OAuth error:", error);
            }
        },
        [router, setAuth]
    );

    /**
     * Get Zoom OAuth authorization URL
     */
    const getZoomAuthUrl = useCallback(() => {
        if (!ZOOM_CLIENT_ID || !ZOOM_REDIRECT_URI) {
            console.error("Zoom OAuth configuration is missing");
            return null;
        }

        const params = new URLSearchParams({
            response_type: "code",
            client_id: ZOOM_CLIENT_ID,
            redirect_uri: ZOOM_REDIRECT_URI,
        });

        return `${ZOOM_OAUTH_URL}?${params.toString()}`;
    }, []);

    return {
        initiateZoomLogin,
        handleZoomCallback,
        getZoomAuthUrl,
    };
};
