import React from 'react';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Avatar } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import NotificationBell from '@/components/notifications/NotificationBell';

export interface DashboardHeaderProps {
    title: string;
    description?: string;
    className?: string;
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({
    title,
    description,
    className,
}) => {
    return (
        <header className={cn(
            "h-20 bg-white/80 backdrop-blur-md border-b border-neutral-100 px-8 flex items-center justify-between sticky top-0 z-30",
            className
        )}>
            <div className="flex flex-col">
                <h1 className="text-xl font-bold text-neutral-900">{title}</h1>
                {description && <p className="text-sm text-neutral-500">{description}</p>}
            </div>

            <div className="flex items-center gap-6">
                <div className="hidden md:block w-80">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 pointer-events-none" />
                        <Input
                            placeholder="Search meetings, transcripts, AI notes..."
                            className="h-10 bg-neutral-50 border-none rounded-xl pl-9"
                        />
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <NotificationBell />

                    <div className="h-8 w-px bg-neutral-200 mx-2" />

                    <button className="flex items-center gap-3 pl-2 pr-1 py-1 rounded-2xl hover:bg-neutral-50 transition-colors">
                        <div className="flex flex-col items-end hidden sm:flex">
                            <span className="text-sm font-bold text-neutral-900 leading-none">Uzair Ahmad</span>
                            <span className="text-[10px] font-semibold text-primary uppercase mt-1">Pro Plan</span>
                        </div>
                        <Avatar fallback="UA" size="md" />
                    </button>
                </div>
            </div>
        </header>
    );
};

export default DashboardHeader;
