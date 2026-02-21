import React from 'react';
import { Meeting } from '../../../types/meeting';
import { MeetingCard } from '../MeetingCard/MeetingCard';
import { MeetingEmpty } from '../MeetingEmpty/MeetingEmpty';
import { MeetingCardSkeleton } from '../MeetingCard/MeetingCardSkeleton';
import { Skeleton } from '@/components/ui/skeleton';
import { clsx } from 'clsx';
import { LayoutGrid, List as ListIcon, ChevronLeft, ChevronRight } from 'lucide-react';

interface MeetingListProps {
    meetings: Meeting[];
    isLoading: boolean;
    viewMode: 'grid' | 'list';
    onViewChange: (mode: 'grid' | 'list') => void;
    onDelete: (id: string) => void;
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
    hasFilters: boolean;
    clearFilters: () => void;
    onCreate: () => void;
}

export const MeetingList: React.FC<MeetingListProps> = ({
    meetings,
    isLoading,
    viewMode,
    onViewChange,
    onDelete,
    currentPage,
    totalPages,
    onPageChange,
    hasFilters,
    clearFilters,
    onCreate,
}) => {
    if (isLoading) {
        return (
            <div className="space-y-6">
                <div className="flex items-center justify-between mb-6">
                    <Skeleton className="h-5 w-32 rounded-lg" />
                    <Skeleton className="h-10 w-24 rounded-xl" />
                </div>
                <div className={clsx(
                    "grid gap-6",
                    viewMode === 'grid' ? "grid-cols-1 md:grid-cols-2 xl:grid-cols-2 2xl:grid-cols-3" : "grid-cols-1"
                )}>
                    {[...Array(6)].map((_, i) => (
                        <MeetingCardSkeleton key={i} viewMode={viewMode} />
                    ))}
                </div>
            </div>
        );
    }

    if (meetings.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-20 px-4 bg-white rounded-3xl border border-neutral-100 shadow-sm text-center">
                <div className="w-20 h-20 bg-primary/5 rounded-full flex items-center justify-center mb-6">
                    <ListIcon className="w-10 h-10 text-primary" />
                </div>
                <h3 className="text-xl font-bold text-neutral-800 mb-2">
                    {hasFilters ? 'No matching meetings found' : 'No meetings scheduled'}
                </h3>
                <p className="text-neutral-500 max-w-sm mb-8 font-medium">
                    {hasFilters
                        ? 'Try adjusting your filters or search terms to find what you are looking for.'
                        : 'Connect your calendar or create a manual meeting to start using Vocaply.'}
                </p>
                <div className="flex gap-4">
                    {hasFilters && (
                        <button
                            onClick={clearFilters}
                            className="px-6 py-2.5 text-neutral-600 font-bold border border-neutral-200 rounded-xl hover:bg-neutral-50 transition-all"
                        >
                            Clear Filters
                        </button>
                    )}
                    <button
                        onClick={onCreate}
                        className="px-6 py-2.5 bg-primary text-white font-bold rounded-xl shadow-primary hover:shadow-lg hover:bg-primary-600 transition-all active:scale-95"
                    >
                        Create Meeting
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* View Toggle & Count */}
            <div className="flex items-center justify-between mb-8">
                <p className="text-sm font-bold text-neutral-500 uppercase tracking-widest">
                    {meetings.length} Meetings Found
                </p>

                <div className="flex bg-neutral-100 p-1 rounded-xl shadow-inner">
                    <button
                        onClick={() => onViewChange('grid')}
                        className={clsx(
                            "p-2 rounded-lg transition-all",
                            viewMode === 'grid' ? "bg-white text-primary shadow-sm" : "text-neutral-400 hover:text-neutral-600"
                        )}
                    >
                        <LayoutGrid className="w-4 h-4" />
                    </button>
                    <button
                        onClick={() => onViewChange('list')}
                        className={clsx(
                            "p-2 rounded-lg transition-all",
                            viewMode === 'list' ? "bg-white text-primary shadow-sm" : "text-neutral-400 hover:text-neutral-600"
                        )}
                    >
                        <ListIcon className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Grid/List Container */}
            <div className={clsx(
                "grid gap-6 transition-all duration-500 animate-in fade-in",
                viewMode === 'grid' ? "grid-cols-1 md:grid-cols-2 xl:grid-cols-2 2xl:grid-cols-3" : "grid-cols-1"
            )}>
                {meetings.map((meeting) => (
                    <MeetingCard
                        key={meeting.id}
                        meeting={meeting}
                        viewMode={viewMode}
                        onDelete={onDelete}
                    />
                ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-center gap-2 pt-10">
                    <button
                        onClick={() => onPageChange(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                        className="p-2 border border-neutral-200 rounded-xl hover:bg-neutral-50 disabled:opacity-30 transition-all"
                    >
                        <ChevronLeft className="w-5 h-5" />
                    </button>
                    {[...Array(totalPages)].map((_, i) => (
                        <button
                            key={i + 1}
                            onClick={() => onPageChange(i + 1)}
                            className={clsx(
                                "w-10 h-10 rounded-xl font-bold transition-all",
                                currentPage === i + 1
                                    ? "bg-primary text-white shadow-primary"
                                    : "text-neutral-500 hover:bg-neutral-100"
                            )}
                        >
                            {i + 1}
                        </button>
                    ))}
                    <button
                        onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
                        disabled={currentPage === totalPages}
                        className="p-2 border border-neutral-200 rounded-xl hover:bg-neutral-50 disabled:opacity-30 transition-all"
                    >
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>
            )}
        </div>
    );
};
