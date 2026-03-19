"use client";

import React, { useState } from 'react';
import { useMeetings } from '@/hooks/useMeetings';
import { MeetingList } from '@/components/meetings/MeetingList/MeetingList';
import { MeetingFilters } from '@/components/meetings/MeetingFilters/MeetingFilters';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { CreateMeetingModal } from '@/components/meetings/CreateMeetingModal/CreateMeetingModal';
import { CreateMeetingDTO } from '@/types/meeting';

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
        <div className="container mx-auto px-4 py-8 max-w-7xl animate-in fade-in duration-700">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-6">
                <div>
                    <h1 className="text-4xl font-extrabold font-outfit text-neutral-900 tracking-tight">My Meetings</h1>
                    <p className="text-neutral-500 mt-2 font-medium">
                        Manage your upcoming schedule and review past meeting insights.
                    </p>
                </div>
                <Button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="w-full md:w-auto px-6 py-4 rounded-xl bg-primary hover:bg-primary/90 shadow-md hover:shadow-lg transition-all font-bold"
                >
                    <Plus className="w-5 h-5 mr-2" />
                    New Meeting
                </Button>
            </div>

            <div className="flex flex-col lg:grid lg:grid-cols-4 gap-8">
                {/* Sidebar Filters */}
                <aside className="lg:col-span-1 space-y-6">
                    <MeetingFilters filters={filters} onFilterChange={setFilters} />

                    {/* Stats Widget */}
                    <div className="bg-primary/5 rounded-3xl p-6 border border-primary/10">
                        <p className="text-xs font-bold text-primary uppercase tracking-widest mb-1">Total Meetings</p>
                        <p className="text-3xl font-black text-primary font-outfit">{totalMeetings}</p>
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
        </div>
    );
}
