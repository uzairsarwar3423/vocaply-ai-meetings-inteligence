import React from 'react';
import { Search, Filter, X, Calendar, Video } from 'lucide-react';
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
        <div className="bg-white p-6 rounded-2xl border border-neutral-100 shadow-sm space-y-6">
            <div className="flex items-center justify-between">
                <h3 className="font-bold text-neutral-800 flex items-center gap-2">
                    <Filter className="w-4 h-4 text-primary" />
                    Filters
                </h3>
                {hasActiveFilters && (
                    <button
                        onClick={clearFilters}
                        className="text-xs text-primary hover:text-primary-600 font-bold flex items-center gap-1 transition-colors"
                    >
                        <X className="w-3 h-3" />
                        Clear
                    </button>
                )}
            </div>

            {/* Search */}
            <div className="space-y-2">
                <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Search</label>
                <div className="relative group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 group-focus-within:text-primary transition-colors" />
                    <input
                        type="text"
                        value={filters.search}
                        onChange={(e) => updateFilter({ search: e.target.value })}
                        placeholder="Search meetings..."
                        className="w-full pl-10 pr-4 py-2 bg-neutral-50 border border-neutral-200 rounded-xl text-sm focus:ring-4 focus:ring-primary/5 focus:border-primary focus:bg-white outline-none transition-all"
                    />
                </div>
            </div>

            {/* Status */}
            <div className="space-y-3">
                <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Status</label>
                <div className="flex flex-wrap gap-2">
                    {statusOptions.map((option) => (
                        <button
                            key={option.value}
                            onClick={() => updateFilter({ status: option.value })}
                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${filters.status === option.value
                                ? 'bg-primary text-white shadow-primary'
                                : 'bg-neutral-50 text-neutral-500 hover:bg-neutral-100'
                                }`}
                        >
                            {option.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Platform */}
            <div className="space-y-3">
                <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Platform</label>
                <div className="grid grid-cols-1 gap-1">
                    {platformOptions.map((option) => (
                        <button
                            key={option.value}
                            onClick={() => updateFilter({ platform: option.value })}
                            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-all ${filters.platform === option.value
                                ? 'bg-primary/5 text-primary'
                                : 'text-neutral-600 hover:bg-neutral-50'
                                }`}
                        >
                            <Video className={`w-4 h-4 ${filters.platform === option.value ? 'text-primary' : 'text-neutral-400'}`} />
                            {option.label}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};
