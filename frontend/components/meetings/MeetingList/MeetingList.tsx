import React from 'react';
import { Meeting } from '../../../types/meeting';
import { MeetingCard } from '../MeetingCard/MeetingCard';
import { MeetingEmpty } from '../MeetingEmpty/MeetingEmpty';
import { MeetingCardSkeleton } from '../MeetingCard/MeetingCardSkeleton';
import { Skeleton } from '@/components/ui/skeleton';
import { clsx } from 'clsx';
import { LayoutGrid, List as ListIcon, ChevronLeft, ChevronRight, Search } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

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

const container = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1
        }
    }
};

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
            <div className="space-y-8">
                <div className="flex items-center justify-between mb-8 pb-4 border-b border-neutral-100/50">
                    <Skeleton className="h-4 w-40 rounded-full" />
                    <Skeleton className="h-10 w-24 rounded-2xl" />
                </div>
                <div className={clsx(
                    "grid gap-8",
                    viewMode === 'grid' ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-2 2xl:grid-cols-3" : "grid-cols-1"
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
            <div className="flex flex-col items-center justify-center py-24 px-4 glass-card rounded-[3rem] border-white/40 shadow-2xl shadow-neutral-200/20 text-center animate-in zoom-in duration-500">
                <div className="w-24 h-24 bg-primary/5 rounded-[2rem] flex items-center justify-center mb-8 shadow-inner ring-1 ring-primary/10">
                    <Search className="w-10 h-10 text-primary animate-pulse" />
                </div>
                <h3 className="text-2xl font-black text-neutral-900 mb-3 tracking-tight">
                    {hasFilters ? 'No matches found' : 'Workspace is empty'}
                </h3>
                <p className="text-neutral-400 max-w-sm mb-10 font-medium leading-relaxed">
                    {hasFilters
                        ? 'We couldn\'t find any records matching your specific criteria. Try broadening your horizon.'
                        : 'Your digital meeting graveyard is currently vacant. Start by connecting your sources.'}
                </p>
                <div className="flex flex-col sm:flex-row gap-4">
                    {hasFilters && (
                        <button
                            onClick={clearFilters}
                            className="px-8 py-3.5 text-neutral-500 font-black uppercase tracking-widest text-[10px] border border-neutral-200 rounded-2xl hover:bg-neutral-50 hover:text-neutral-900 transition-all active:scale-95"
                        >
                            Reset Pulse
                        </button>
                    )}
                    <button
                        onClick={onCreate}
                        className="px-8 py-3.5 bg-primary text-white font-black uppercase tracking-widest text-[10px] rounded-2xl shadow-xl shadow-primary/20 hover:shadow-primary/40 hover:bg-primary-600 transition-all active:scale-95"
                    >
                        Create Workspace
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* View Toggle & Count */}
            <div className="flex items-center justify-between mb-10 pb-4 border-b border-neutral-100/30">
                <div className="flex items-center gap-3">
                    <p className="text-[10px] font-black text-neutral-400 uppercase tracking-[0.3em]">
                        {meetings.length} Records Found
                    </p>
                    <div className="h-1 w-1 rounded-full bg-neutral-200" />
                    <p className="text-[10px] font-bold text-primary uppercase tracking-widest">Page {currentPage}</p>
                </div>

                <div className="flex glass-panel p-1 rounded-2xl shadow-sm border-white/20">
                    <button
                        onClick={() => onViewChange('grid')}
                        className={clsx(
                            "p-2.5 rounded-xl transition-all duration-300",
                            viewMode === 'grid' ? "bg-white text-primary shadow-md ring-1 ring-neutral-100" : "text-neutral-400 hover:text-neutral-600"
                        )}
                        title="Grid View"
                    >
                        <LayoutGrid className="w-4.5 h-4.5" />
                    </button>
                    <button
                        onClick={() => onViewChange('list')}
                        className={clsx(
                            "p-2.5 rounded-xl transition-all duration-300",
                            viewMode === 'list' ? "bg-white text-primary shadow-md ring-1 ring-neutral-100" : "text-neutral-400 hover:text-neutral-600"
                        )}
                        title="List View"
                    >
                        <ListIcon className="w-4.5 h-4.5" />
                    </button>
                </div>
            </div>

            {/* Grid/List Container */}
            <motion.div
                variants={container}
                initial="hidden"
                animate="show"
                className={clsx(
                    "grid gap-8 pb-10",
                    viewMode === 'grid' ? "grid-cols-1 md:grid-cols-2 lg:grid-cols-2 2xl:grid-cols-3" : "grid-cols-1"
                )}>
                <AnimatePresence mode="popLayout">
                    {meetings.map((meeting) => (
                        <MeetingCard
                            key={meeting.id}
                            meeting={meeting}
                            viewMode={viewMode}
                            onDelete={onDelete}
                        />
                    ))}
                </AnimatePresence>
            </motion.div>

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-center gap-3 pt-10 border-t border-neutral-100/50">
                    <button
                        onClick={() => onPageChange(Math.max(1, currentPage - 1))}
                        disabled={currentPage === 1}
                        className="w-12 h-12 flex items-center justify-center border border-neutral-200 rounded-2xl hover:bg-white hover:border-primary/30 text-neutral-500 hover:text-primary transition-all disabled:opacity-30 shadow-sm"
                    >
                        <ChevronLeft className="w-5 h-5" />
                    </button>
                    <div className="flex items-center gap-2 p-1 bg-neutral-100/50 rounded-2xl backdrop-blur-sm shadow-inner">
                        {[...Array(totalPages)].map((_, i) => (
                            <button
                                key={i + 1}
                                onClick={() => onPageChange(i + 1)}
                                className={clsx(
                                    "w-10 h-10 rounded-xl text-xs font-black transition-all",
                                    currentPage === i + 1
                                        ? "bg-white text-primary shadow-md ring-1 ring-neutral-100"
                                        : "text-neutral-400 hover:text-neutral-600 hover:bg-white/50"
                                )}
                            >
                                {i + 1}
                            </button>
                        ))}
                    </div>
                    <button
                        onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
                        disabled={currentPage === totalPages}
                        className="w-12 h-12 flex items-center justify-center border border-neutral-200 rounded-2xl hover:bg-white hover:border-primary/30 text-neutral-500 hover:text-primary transition-all disabled:opacity-30 shadow-sm"
                    >
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>
            )}
        </div>
    );
};
