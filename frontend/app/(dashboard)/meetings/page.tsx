"use client";

import React, { useState } from 'react';
import { useMeetings } from '@/hooks/useMeetings';
import { MeetingList } from '@/components/meetings/MeetingList/MeetingList';
import { MeetingFilters } from '@/components/meetings/MeetingFilters/MeetingFilters';
import { Button } from '@/components/ui/button';
import { Plus, Layout } from 'lucide-react';
import { CreateMeetingModal } from '@/components/meetings/CreateMeetingModal/CreateMeetingModal';
import { CreateMeetingDTO } from '@/types/meeting';
import { motion } from 'framer-motion';

export default function MeetingsPage() {
    const {
        meetings,
        isLoading,
        filters,
        setFilters,
        currentPage,
        setCurrentPage,
        totalPages,
        deleteMeeting,
        createMeeting,
        totalMeetings
    } = useMeetings();

    const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleCreateMeeting = async (data: CreateMeetingDTO) => {
        setIsSubmitting(true);
        try {
            await createMeeting(data);
            setIsCreateModalOpen(false);
        } catch (error) {
            console.error(error);
        } finally {
            setIsSubmitting(false);
        }
    };

    const hasFilters = filters.search !== '' || filters.status !== 'all' || filters.dateRange !== 'all' || filters.platform !== 'all';

    const clearFilters = () => {
        setFilters({
            search: '',
            status: 'all',
            dateRange: 'all',
            platform: 'all'
        });
    };

    const handleDelete = async (id: string) => {
        if (confirm('Are you sure you want to delete this meeting?')) {
            await deleteMeeting(id);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="container mx-auto px-4 py-8 max-w-7xl pb-32"
        >
            <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-16 gap-8">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <div className="h-1 w-8 bg-primary rounded-full" />
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-primary">Workspace</span>
                    </div>
                    <h1 className="text-5xl font-black font-outfit text-neutral-900 tracking-tighter">My Meetings</h1>
                    <p className="text-neutral-400 mt-2 font-semibold">
                        Access and manage your processed intelligence.
                    </p>
                </div>
                <Button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="w-full md:w-auto px-8 py-7 rounded-[2rem] bg-primary hover:bg-primary-600 shadow-2xl shadow-primary/30 hover:shadow-primary/50 transition-all font-black uppercase tracking-widest text-[11px] group"
                >
                    <Plus className="w-5 h-5 mr-3 group-hover:rotate-90 transition-transform duration-300" />
                    New Workspace
                </Button>
            </div>

            <div className="flex flex-col lg:grid lg:grid-cols-4 gap-12">
                {/* Sidebar Filters */}
                <aside className="lg:col-span-1 space-y-8">
                    <MeetingFilters filters={filters} onFilterChange={setFilters} />

                    {/* Stats Widget */}
                    <div className="glass-card rounded-[2.5rem] p-8 border-white/30 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-20 h-20 bg-primary/5 rounded-bl-full -mr-6 -mt-6 group-hover:scale-110 transition-transform" />
                        <div className="relative z-10">
                            <p className="text-[10px] font-black text-primary uppercase tracking-[0.2em] mb-3">Meeting Index</p>
                            <div className="flex items-baseline gap-2">
                                <p className="text-5xl font-black text-neutral-900 font-outfit tracking-tighter">{totalMeetings}</p>
                                <span className="text-xs font-bold text-neutral-400 uppercase tracking-widest">Total</span>
                            </div>
                            <div className="mt-6 flex items-center gap-2 text-[10px] font-bold text-neutral-400 uppercase tracking-widest">
                                <Layout size={14} className="text-primary" />
                                Updated just now
                            </div>
                        </div>
                    </div>
                </aside>

                {/* Meeting List Content */}
                <div className="lg:col-span-3">
                    <MeetingList
                        meetings={meetings}
                        isLoading={isLoading}
                        viewMode={viewMode}
                        onViewChange={setViewMode}
                        onDelete={handleDelete}
                        currentPage={currentPage}
                        totalPages={totalPages}
                        onPageChange={setCurrentPage}
                        hasFilters={hasFilters}
                        clearFilters={clearFilters}
                        onCreate={() => setIsCreateModalOpen(true)}
                    />
                </div>
            </div>

            <CreateMeetingModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onSubmit={handleCreateMeeting}
                isSubmitting={isSubmitting}
            />
        </motion.div>
    );
}
