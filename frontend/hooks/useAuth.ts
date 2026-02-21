import { useAuthStore } from "../store/authStore";
import { authService } from "../lib/auth/auth";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

export const useAuth = () => {
    const router = useRouter();
    const { user, isAuthenticated, isLoading, tokens, logout: clearAuth } = useAuthStore();

    const logout = async () => {
        try {
            await authService.logout();
            toast.success("Logged out successfully");
            router.push("/login");
        } catch (error) {
            clearAuth();
            router.push("/login");
        }
    };

    return {
        user,
        isAuthenticated,
        isLoading,
        tokens,
        logout,
    };
};
