
import React from 'react';
import { CalendarX2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface MeetingEmptyProps {
    onCreate: () => void;
    hasFilters: boolean;
    clearFilters: () => void;
}

export const MeetingEmpty: React.FC<MeetingEmptyProps> = ({ onCreate, hasFilters, clearFilters }) => {
    return (
        <div className="flex flex-col items-center justify-center p-12 text-center rounded-2xl border border-dashed border-neutral-200 bg-neutral-50/50">
            <div className="w-16 h-16 rounded-full bg-neutral-100 flex items-center justify-center mb-6">
                <CalendarX2 className="w-8 h-8 text-neutral-400" />
            </div>
            <h3 className="text-xl font-bold text-neutral-900 mb-2">
                {hasFilters ? 'No meetings found' : 'No meetings scheduled'}
            </h3>
            <p className="text-neutral-500 max-w-md mb-8">
                {hasFilters
                    ? "We couldn't find any meetings matching your filters. Try adjusting your search criteria."
                    : "Get started by scheduling your first meeting. Vocaply will join automatically to transcribe and take notes."}
            </p>
            {hasFilters ? (
                <Button variant="secondary" onClick={clearFilters}>
                    Clear Filters
                </Button>
            ) : (
                <Button onClick={onCreate}>
                    Schedule Meeting
                </Button>
            )}
        </div>
    );
};
