import React from 'react';
import { useRouter } from 'next/navigation';
import {
    CalendarDays,
    Clock,
    Video,
    Users,
    Trash2,
    ChevronRight,
    ExternalLink
} from 'lucide-react';
import { formatDuration } from '@/utils/formatters';
import { Meeting } from '@/types/meeting';
import { StatusBadge } from '../StatusBadge/StatusBadge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Avatar } from '@/components/ui/avatar';
import { clsx } from 'clsx';

interface MeetingCardProps {
    meeting: Meeting;
    onDelete: (id: string) => void;
    viewMode: 'grid' | 'list';
}

export const MeetingCard: React.FC<MeetingCardProps> = ({ meeting, onDelete, viewMode }) => {
    const router = useRouter();
    const isGrid = viewMode === 'grid';

    const handleCardClick = () => {
        router.push(`/meetings/${meeting.id}`);
    };

    const platformIcon = {
        google_meet: <Video className="w-4 h-4 text-blue-500" />,
        zoom: <Video className="w-4 h-4 text-blue-400" />,
        teams: <Video className="w-4 h-4 text-indigo-500" />,
        other: <Video className="w-4 h-4 text-gray-500" />,
    }[meeting.platform] || <Video className="w-4 h-4" />;

    if (!isGrid) {
        return (
            <div
                onClick={handleCardClick}
                className="bg-white rounded-2xl border border-neutral-100 p-4 hover:shadow-lg transition-all cursor-pointer flex items-center gap-6 group"
            >
                <div className="flex-shrink-0 w-12 h-12 bg-neutral-50 rounded-xl flex items-center justify-center">
                    {platformIcon}
                </div>

                <div className="flex-grow min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                        <h4 className="font-bold text-neutral-800 truncate group-hover:text-primary transition-colors">{meeting.title}</h4>
                        <StatusBadge status={meeting.status} />
                    </div>
                    <div className="flex items-center gap-4 text-xs text-neutral-500 pt-1">
                        <div className="flex items-center gap-1">
                            <CalendarDays className="w-3.5 h-3.5" />
                            <span>{new Date(meeting.startTime).toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5" />
                            <span>{new Date(meeting.startTime).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <Users className="w-3.5 h-3.5" />
                            <span>{meeting.attendees.length} Attendees</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <Button
                        variant="ghost"
                        size="sm"
                        className="h-9 w-9 p-0 text-neutral-400 hover:text-error hover:bg-error/10 opacity-0 group-hover:opacity-100 transition-all rounded-lg"
                        onClick={(e) => {
                            e.stopPropagation();
                            onDelete(meeting.id);
                        }}
                    >
                        <Trash2 className="w-4 h-4" />
                    </Button>
                    <ChevronRight className="w-5 h-5 text-neutral-300 group-hover:text-primary transition-all group-hover:translate-x-1" />
                </div>
            </div>
        );
    }

    return (
        <Card
            className="hover:shadow-2xl transition-all duration-500 cursor-pointer group relative overflow-hidden flex flex-col h-full bg-white border-neutral-100 hover:border-primary/20 hover:-translate-y-2 rounded-3xl"
            onClick={handleCardClick}
        >
            <CardHeader className="pb-4 pt-6 px-6">
                <div className="flex justify-between items-start mb-4">
                    <div className="p-2 bg-neutral-50 rounded-xl">
                        {platformIcon}
                    </div>
                    <StatusBadge status={meeting.status} />
                </div>
                <CardTitle className="text-xl font-bold font-outfit text-neutral-800 line-clamp-2 leading-snug group-hover:text-primary transition-colors">
                    {meeting.title}
                </CardTitle>
            </CardHeader>

            <CardContent className="flex-grow pb-6 px-6">
                {meeting.description && (
                    <p className="text-sm text-neutral-500 line-clamp-2 mb-6 font-medium leading-relaxed">
                        {meeting.description}
                    </p>
                )}

                <div className="space-y-3">
                    <div className="flex items-center gap-3 text-sm font-semibold text-neutral-600">
                        <CalendarDays className="w-4 h-4 text-primary/60" />
                        <span>{new Date(meeting.startTime).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                    </div>
                    <div className="flex items-center gap-3 text-sm font-semibold text-neutral-600">
                        <Clock className="w-4 h-4 text-primary/60" />
                        <span>
                            {new Date(meeting.startTime).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })}
                            {' • '}
                            {formatDuration(meeting.duration || (meeting.endTime ? (new Date(meeting.endTime).getTime() - new Date(meeting.startTime).getTime()) / 1000 : 0))}
                        </span>
                    </div>
                </div>
            </CardContent>

            <CardFooter className="pt-4 border-t border-neutral-50 mt-auto px-6 py-4 flex items-center justify-between bg-neutral-50/30">
                <div className="flex -space-x-2">
                    {meeting.attendees.slice(0, 3).map((attendee, i) => (
                        <Avatar
                            key={i}
                            size="sm"
                            fallback={typeof attendee === 'string' ? attendee[0].toUpperCase() : attendee.name?.[0] || attendee.email[0].toUpperCase()}
                            className="ring-2 ring-white"
                        />
                    ))}
                    {meeting.attendees.length > 3 && (
                        <div className="w-8 h-8 rounded-full bg-neutral-100 border-2 border-white flex items-center justify-center text-[10px] font-bold text-neutral-500">
                            +{meeting.attendees.length - 3}
                        </div>
                    )}
                </div>

                <div className="flex gap-2">
                    <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0 text-neutral-400 hover:text-error hover:bg-error/10 opacity-0 group-hover:opacity-100 transition-all rounded-lg"
                        onClick={(e) => {
                            e.stopPropagation();
                            onDelete(meeting.id);
                        }}
                    >
                        <Trash2 className="w-4 h-4" />
                    </Button>
                    <div className="h-8 w-8 bg-primary/5 rounded-lg flex items-center justify-center text-primary opacity-0 group-hover:opacity-100 transition-all">
                        <ChevronRight className="w-4 h-4" />
                    </div>
                </div>
            </CardFooter>
        </Card>
    );
};
