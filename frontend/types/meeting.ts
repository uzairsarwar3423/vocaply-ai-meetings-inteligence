
export type MeetingStatus = 'scheduled' | 'completed' | 'processing' | 'live' | 'failed' | 'cancelled';
export type MeetingPlatform = 'google_meet' | 'zoom' | 'teams' | 'other';

export interface Meeting {
    id: string;
    title: string;
    description?: string;
    startTime: string; // ISO String
    endTime?: string; // ISO String
    duration?: number; // in seconds
    platform: MeetingPlatform;
    status: MeetingStatus;
    attendees: (string | { name?: string; email: string })[]; // List of emails, names, or attendee objects
    createdAt: string;
    updatedAt: string;
    recordingUrl?: string; // Optional
    transcriptionId?: string; // Optional
    organizerId: string;
}

export interface MeetingFilters {
    status?: MeetingStatus | 'all';
    search: string;
    dateRange: 'all' | 'today' | 'week' | 'month';
    platform?: MeetingPlatform | 'all';
}

export interface CreateMeetingDTO {
    title: string;
    description?: string;
    startTime: string;
    platform: MeetingPlatform;
    attendees?: (string | { name?: string; email: string })[]; // Optional array of strings
}

export interface CreateMeetingInput {
    // For form inputs if different from DTO
    title: string;
    description?: string;
    startTime: string;
    platform: MeetingPlatform;
    attendeeEmails: string; // Comma separated string
}
