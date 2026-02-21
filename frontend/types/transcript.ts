export interface TranscriptWord {
    word: string;
    start: number;
    end: number;
    confidence: number;
}

export interface TranscriptSegment {
    id: string;
    meeting_id: string;
    company_id: string;
    user_id?: string;
    text: string;
    speaker_id?: string;
    speaker_name?: string;
    speaker_email?: string;
    start_time: number;  // seconds
    end_time: number;    // seconds
    duration: number;
    confidence?: number;
    language: string;
    channel?: number;
    sequence_number: number;
    words?: TranscriptWord[];
    is_edited: boolean;
    original_text?: string;
    edited_by?: string;
    edited_at?: string;
    created_at: string;
    updated_at: string;
}

export interface TranscriptMetadata {
    id: string;
    meeting_id: string;
    total_chunks: number;
    total_words: number;
    total_duration_seconds: number;
    average_confidence?: number;
    speaker_count: number;
    speakers: TranscriptSpeaker[];
    detected_language?: string;
    language_confidence?: number;
    deepgram_model?: string;
}

export interface TranscriptSpeaker {
    id: string;
    name?: string;
    email?: string;
    word_count: number;
    duration: number;
    color?: string; // assigned in frontend
}

export interface TranscriptBookmark {
    id: string;
    segment_id: string;
    time: number;
    label: string;
    note?: string;
    created_at: string;
}

export interface TranscriptFilters {
    search: string;
    speaker?: string;
    minConfidence?: number;
}

export type ExportFormat = 'txt' | 'pdf' | 'docx' | 'srt';
