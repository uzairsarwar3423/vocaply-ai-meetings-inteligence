import React from 'react';
import { Search, Filter, X, Calendar, Video, Zap } from 'lucide-react';
import { MeetingStatus, MeetingPlatform, MeetingFilters as FilterType } from '../../../types/meeting';

interface MeetingFiltersProps {
    filters: FilterType;
    onFilterChange: (filters: FilterType) => void;
}

const statusOptions: { value: MeetingStatus | 'all'; label: string }[] = [
    { value: 'all', label: 'All Statuses' },
    { value: 'scheduled', label: 'Upcoming' },
    { value: 'live', label: 'Live' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' },
];

const platformOptions: { value: MeetingPlatform | 'all'; label: string }[] = [
    { value: 'all', label: 'All Platforms' },
    { value: 'google_meet', label: 'Google Meet' },
    { value: 'zoom', label: 'Zoom' },
    { value: 'teams', label: 'MS Teams' },
];

export const MeetingFilters: React.FC<MeetingFiltersProps> = ({
    filters,
    onFilterChange,
}) => {
    const hasActiveFilters = filters.status !== 'all' || filters.platform !== 'all' || filters.search.length > 0 || filters.dateRange !== 'all';

    const updateFilter = (updates: Partial<FilterType>) => {
        onFilterChange({ ...filters, ...updates });
    };

    const clearFilters = () => {
        onFilterChange({
            search: '',
            status: 'all',
            dateRange: 'all',
            platform: 'all'
        });
    };

    return (
        <div className="glass-card p-6 rounded-3xl border-white/30 space-y-8 sticky top-24 shadow-xl shadow-neutral-200/20">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-black text-neutral-900 flex items-center gap-2.5 uppercase tracking-widest">
                    <div className="p-1.5 bg-primary/10 rounded-lg text-primary">
                        <Filter className="w-4 h-4" />
                    </div>
                    Filters
                </h3>
                {hasActiveFilters && (
                    <button
                        onClick={clearFilters}
                        className="text-[10px] text-primary hover:text-primary-700 font-black flex items-center gap-1 transition-all uppercase tracking-widest bg-primary/5 px-2 py-1 rounded-full ring-1 ring-primary/10"
                    >
                        <X className="w-3 h-3" />
                        Clear
                    </button>
                )}
            </div>

            {/* Search */}
            <div className="space-y-3">
                <label className="text-[10px] font-black text-neutral-400 uppercase tracking-[0.2em] ml-1">Search Keywords</label>
                <div className="relative group">
                    <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-300 group-focus-within:text-primary transition-all duration-300" />
                    <input
                        type="text"
                        value={filters.search}
                        onChange={(e) => updateFilter({ search: e.target.value })}
                        placeholder="Project name, client..."
                        className="w-full pl-11 pr-4 py-3 bg-white/50 border border-neutral-100 rounded-2xl text-sm font-medium placeholder:text-neutral-300 focus:ring-4 focus:ring-primary/5 focus:border-primary/50 focus:bg-white outline-none transition-all shadow-sm"
                    />
                </div>
            </div>

            {/* Status */}
            <div className="space-y-4">
                <label className="text-[10px] font-black text-neutral-400 uppercase tracking-[0.2em] ml-1">Status Feed</label>
                <div className="flex flex-wrap gap-2">
                    {statusOptions.map((option) => (
                        <button
                            key={option.value}
                            onClick={() => updateFilter({ status: option.value })}
                            className={`px-3 py-2 rounded-xl text-[10px] font-black transition-all uppercase tracking-wider ${filters.status === option.value
                                ? 'bg-primary text-white shadow-lg shadow-primary/20 ring-1 ring-primary'
                                : 'bg-white text-neutral-500 border border-neutral-100 hover:border-primary/30 hover:text-primary shadow-sm'
                                }`}
                        >
                            {option.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Platform */}
            <div className="space-y-4">
                <label className="text-[10px] font-black text-neutral-400 uppercase tracking-[0.2em] ml-1">Connector</label>
                <div className="grid grid-cols-1 gap-2">
                    {platformOptions.map((option) => (
                        <button
                            key={option.value}
                            onClick={() => updateFilter({ platform: option.value })}
                            className={`flex items-center gap-3 px-4 py-3 rounded-2xl text-[13px] font-bold transition-all border ${filters.platform === option.value
                                ? 'bg-primary/5 text-primary border-primary/20 shadow-[inset_0px_0px_12px_rgba(13,148,136,0.05)]'
                                : 'bg-white/50 text-neutral-600 border-neutral-100 hover:bg-white hover:border-primary/20 hover:text-primary shadow-sm'
                                }`}
                        >
                            <Video className={`w-4 h-4 ${filters.platform === option.value ? 'text-primary' : 'text-neutral-400'}`} />
                            <span className="flex-1 text-left">{option.label}</span>
                            {filters.platform === option.value && <div className="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(13,148,136,0.5)]" />}
                        </button>
                    ))}
                </div>
            </div>

            {/* AI Assistant Tip */}
            <div className="pt-4 mt-6 border-t border-neutral-100/50">
                <div className="bg-primary/5 p-4 rounded-2xl border border-primary/10">
                    <p className="text-[10px] font-bold text-primary uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
                        <Zap size={12} className="fill-primary" />
                        AI Summary
                    </p>
                    <p className="text-[11px] text-neutral-500 leading-relaxed font-medium">
                        Meeting extraction is currently processing <span className="text-primary font-bold">2 records</span> in the background.
                    </p>
                </div>
            </div>
        </div>
    );
};
