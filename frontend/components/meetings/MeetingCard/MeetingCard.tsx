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
import { motion } from 'framer-motion';

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
        google_meet: <div className="p-2 bg-blue-50 rounded-lg text-blue-600 ring-1 ring-blue-100/50"><Video size={18} /></div>,
        zoom: <div className="p-2 bg-sky-50 rounded-lg text-sky-500 ring-1 ring-sky-100/50"><Video size={18} /></div>,
        teams: <div className="p-2 bg-indigo-50 rounded-lg text-indigo-500 ring-1 ring-indigo-100/50"><Video size={18} /></div>,
        other: <div className="p-2 bg-neutral-50 rounded-lg text-neutral-500 ring-1 ring-neutral-100/50"><Video size={18} /></div>,
    }[meeting.platform] || <div className="p-2 bg-neutral-50 rounded-lg text-neutral-500"><Video size={18} /></div>;

    if (!isGrid) {
        return (
            <motion.div
                layout
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                onClick={handleCardClick}
                className="glass-card rounded-2xl p-4 flex items-center gap-6 group cursor-pointer border-white/20"
            >
                <div className="flex-shrink-0 transition-transform group-hover:scale-110 duration-300">
                    {platformIcon}
                </div>

                <div className="flex-grow min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                        <h4 className="font-black text-neutral-900 truncate group-hover:text-primary transition-colors text-base tracking-tight">{meeting.title}</h4>
                        <StatusBadge status={meeting.status} />
                    </div>
                    <div className="flex items-center gap-4 text-[10px] font-bold text-neutral-400 pt-1 uppercase tracking-widest">
                        <div className="flex items-center gap-1.5">
                            <CalendarDays className="w-3 h-3 text-primary/50" />
                            <span>{new Date(meeting.startTime).toLocaleDateString()}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <Clock className="w-3 h-3 text-primary/50" />
                            <span>{new Date(meeting.startTime).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <Users className="w-3 h-3 text-primary/50" />
                            <span>{meeting.attendees.length} Attendees</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <Button
                        variant="ghost"
                        size="sm"
                        className="h-9 w-9 p-0 text-neutral-300 hover:text-error hover:bg-error/10 opacity-0 group-hover:opacity-100 transition-all rounded-xl"
                        onClick={(e) => {
                            e.stopPropagation();
                            onDelete(meeting.id);
                        }}
                    >
                        <Trash2 className="w-4 h-4" />
                    </Button>
                    <div className="w-8 h-8 rounded-full bg-primary/5 flex items-center justify-center text-primary group-hover:translate-x-1 transition-all">
                        <ChevronRight className="w-5 h-5" />
                    </div>
                </div>
            </motion.div>
        );
    }

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="h-full"
        >
            <Card
                className="hover:shadow-2xl transition-all duration-500 cursor-pointer group relative overflow-hidden flex flex-col h-full bg-white/70 backdrop-blur-md border-white/30 hover:border-primary/30 rounded-3xl"
                onClick={handleCardClick}
            >
                <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 rounded-bl-full opacity-50 -mr-8 -mt-8 transition-transform group-hover:scale-110" />

                <CardHeader className="pb-4 pt-6 px-6 relative">
                    <div className="flex justify-between items-start mb-4">
                        <div className="transition-transform group-hover:scale-110 duration-300">
                            {platformIcon}
                        </div>
                        <StatusBadge status={meeting.status} />
                    </div>
                    <CardTitle className="text-xl font-black font-outfit text-neutral-900 line-clamp-2 leading-tight group-hover:text-primary transition-colors tracking-tight">
                        {meeting.title}
                    </CardTitle>
                </CardHeader>

                <CardContent className="flex-grow pb-6 px-6">
                    {meeting.description && (
                        <p className="text-sm text-neutral-400 line-clamp-2 mb-6 font-medium leading-relaxed">
                            {meeting.description}
                        </p>
                    )}

                    <div className="space-y-3">
                        <div className="flex items-center gap-3 text-xs font-bold text-neutral-500 uppercase tracking-widest">
                            <CalendarDays className="w-4 h-4 text-primary" />
                            <span>{new Date(meeting.startTime).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                        </div>
                        <div className="flex items-center gap-3 text-xs font-bold text-neutral-500 uppercase tracking-widest">
                            <Clock className="w-4 h-4 text-primary" />
                            <span>
                                {new Date(meeting.startTime).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })}
                                {' • '}
                                {formatDuration(meeting.duration || (meeting.endTime ? (new Date(meeting.endTime).getTime() - new Date(meeting.startTime).getTime()) / 1000 : 0))}
                            </span>
                        </div>
                    </div>
                </CardContent>

                <CardFooter className="pt-4 border-t border-neutral-100/50 mt-auto px-6 py-4 flex items-center justify-between bg-neutral-50/30">
                    <div className="flex -space-x-2.5">
                        {meeting.attendees.slice(0, 3).map((attendee, i) => (
                            <Avatar
                                key={i}
                                size="sm"
                                fallback={typeof attendee === 'string' ? attendee[0].toUpperCase() : attendee.name?.[0] || attendee.email[0].toUpperCase()}
                                className="ring-2 ring-white shadow-sm"
                            />
                        ))}
                        {meeting.attendees.length > 3 && (
                            <div className="w-8 h-8 rounded-full bg-white border-2 border-white flex items-center justify-center text-[10px] font-black text-neutral-400 shadow-sm">
                                +{meeting.attendees.length - 3}
                            </div>
                        )}
                    </div>

                    <div className="flex gap-2">
                        <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0 text-neutral-300 hover:text-error hover:bg-error/10 opacity-0 group-hover:opacity-100 transition-all rounded-xl"
                            onClick={(e) => {
                                e.stopPropagation();
                                onDelete(meeting.id);
                            }}
                        >
                            <Trash2 className="w-4 h-4" />
                        </Button>
                        <div className="h-8 w-8 bg-primary/10 rounded-xl flex items-center justify-center text-primary opacity-0 group-hover:opacity-100 transition-all shadow-inner">
                            <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                        </div>
                    </div>
                </CardFooter>
            </Card>
        </motion.div>
    );
};
