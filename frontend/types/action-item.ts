// Action Item Types
// Vocaply Platform - Day 11

export type ActionItemStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';
export type ActionItemPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface ActionItem {
    id: string;
    meeting_id: string;
    company_id: string;
    title: string;
    description?: string;
    assignee_name?: string;
    assignee_email?: string;
    assigned_to_id?: string;
    status: ActionItemStatus;
    priority: ActionItemPriority;
    due_date?: string;       // ISO string
    completed_at?: string;
    is_ai_generated: boolean;
    confidence_score?: number;  // 0–1
    transcript_quote?: string;
    transcript_start_time?: number;
    created_at: string;
    updated_at: string;
}

export interface ActionItemFilters {
    search: string;
    status: ActionItemStatus | 'all';
    priority: ActionItemPriority | 'all';
    assignee_id: string | 'all';
    meeting_id: string | 'all';
    is_ai_generated: boolean | 'all';
}

export interface ActionItemUpdate {
    title?: string;
    description?: string;
    assignee_name?: string;
    assignee_email?: string;
    assigned_to_id?: string;
    status?: ActionItemStatus;
    priority?: ActionItemPriority;
    due_date?: string | null;
}

export interface PaginationMeta {
    page: number;
    per_page: number;
    total_items: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
}

export interface ActionItemsResponse {
    data: ActionItem[];
    pagination: PaginationMeta;
}

export interface ActionItemStats {
    total: number;
    by_status: Record<string, number>;
    by_priority: Record<string, number>;
}
