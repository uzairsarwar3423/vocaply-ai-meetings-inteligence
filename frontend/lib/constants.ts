export const APP_NAME = "Vocaply AI";
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const ROUTES = {
    HOME: "/",
    DASHBOARD: "/dashboard",
    MEETINGS: "/dashboard/meetings",
    TRANSCRIPTS: "/dashboard/transcripts",
    CALENDAR: "/dashboard/calendar",
    TEAM: "/dashboard/team",
    SETTINGS: "/dashboard/settings",
    LOGIN: "/auth/login",
    SIGNUP: "/auth/signup",
};

export const AUTH_STORAGE_KEY = "vocaply_auth_token";
