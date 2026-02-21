export interface User {
    id: string;
    email: string;
    full_name: string | null;
    company_id: string;
    role: "owner" | "admin" | "manager" | "member";
    is_active: boolean;
    is_email_verified: boolean;
    avatar_url: string | null;
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
