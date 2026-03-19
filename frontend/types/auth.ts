export interface UserPreferences {
    theme?: "light" | "dark" | "system";
    language?: string;
    auto_join_meetings?: boolean;
}

export interface UserNotificationSettings {
    email_alerts?: boolean;
    push_notifications?: boolean;
    meeting_reminders?: boolean;
}

export interface User {
    id: string;
    email: string;
    full_name: string | null;
    company_id: string;
    role: "owner" | "admin" | "manager" | "member";
    is_active: boolean;
    is_email_verified: boolean;
    avatar_url: string | null;
    preferences: UserPreferences | null;
    notification_settings: UserNotificationSettings | null;
    created_at: string;
    updated_at: string;
}

export interface AuthTokens {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export interface AuthState {
    user: User | null;
    tokens: AuthTokens | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}

export interface ZoomOAuthTokens {
    access_token: string;
    refresh_token: string;
    expires_in: number;
    token_type: string;
    scope: string;
}

export interface ZoomUser {
    user_id: string;
    email: string;
    first_name: string;
    last_name: string;
    company: string;
    profile_picture: string;
    timezone: string;
}

