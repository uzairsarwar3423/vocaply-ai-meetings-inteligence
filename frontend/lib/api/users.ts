import { apiClient } from "./client";
import { User } from "@/types/auth";

export interface UpdateProfilePayload {
    full_name?: string;
    avatar_url?: string;
}

export interface UpdatePreferencesPayload {
    theme?: "light" | "dark" | "system";
    language?: string;
    auto_join_meetings?: boolean;
}

export interface UpdateNotificationsPayload {
    email_alerts?: boolean;
    push_notifications?: boolean;
    meeting_reminders?: boolean;
}

export interface ChangePasswordPayload {
    current_password: string;
    new_password: string;
}

export const usersApi = {
    /** GET /users/me */
    getMe: async (): Promise<User> => {
        const { data } = await apiClient.get<User>("/users/me");
        return data;
    },

    /** PATCH /users/me — update name/avatar */
    updateProfile: async (payload: UpdateProfilePayload): Promise<User> => {
        const { data } = await apiClient.patch<User>("/users/me", payload);
        return data;
    },

    /** PATCH /users/me/preferences — theme, language, etc. */
    updatePreferences: async (payload: UpdatePreferencesPayload): Promise<User> => {
        const { data } = await apiClient.patch<User>("/users/me/preferences", payload);
        return data;
    },

    /** PATCH /users/me/notifications */
    updateNotifications: async (payload: UpdateNotificationsPayload): Promise<User> => {
        const { data } = await apiClient.patch<User>("/users/me/notifications", payload);
        return data;
    },

    /** POST /users/me/change-password */
    changePassword: async (payload: ChangePasswordPayload): Promise<{ message: string }> => {
        const { data } = await apiClient.post<{ message: string }>(
            "/users/me/change-password",
            payload
        );
        return data;
    },
};
