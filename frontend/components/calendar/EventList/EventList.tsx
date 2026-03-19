'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Calendar, Video, Clock, Users } from 'lucide-react';
import { useToast } from '@/hooks/useToast';
import { format, formatDistanceToNow } from 'date-fns';
import { apiClient } from '@/lib/api/client';

interface CalendarEvent {
    id: string;
    title: string;
    description?: string;
    start_time: string;
    end_time: string;
    has_meeting_url: boolean;
    meeting_url?: string;
    meeting_platform?: 'zoom' | 'google_meet' | 'teams';
    auto_join_enabled: boolean;
    auto_join_scheduled: boolean;
}

interface EventListProps {
    events: CalendarEvent[];
    onAutoJoinToggle?: (eventId: string, enabled: boolean) => void;
}

const platformConfig = {
    zoom: { label: 'Zoom', color: 'bg-blue-100 text-blue-800' },
    google_meet: { label: 'Google Meet', color: 'bg-green-100 text-green-800' },
    teams: { label: 'Teams', color: 'bg-purple-100 text-purple-800' },
};

export default function EventList({ events, onAutoJoinToggle }: EventListProps) {
    const [togglingEvents, setTogglingEvents] = useState<Set<string>>(new Set());
    const { toast } = useToast();

    const handleAutoJoinToggle = async (eventId: string, currentEnabled: boolean) => {
        const newEnabled = !currentEnabled;
        setTogglingEvents(prev => new Set(prev).add(eventId));

        try {
            await apiClient.post('/calendar/enable-auto-join', {
                event_id: eventId,
                enabled: newEnabled,
            });

            toast({
                title: newEnabled ? 'Auto-Join Enabled' : 'Auto-Join Disabled',
                description: newEnabled
                    ? 'Bot will automatically join this meeting'
                    : 'Bot will not join this meeting',
            });

            onAutoJoinToggle?.(eventId, newEnabled);
        } catch (error) {
            console.error('Toggle error:', error);
            toast({
                title: 'Error',
                description: 'Failed to update auto-join setting',
                variant: 'destructive',
            });
        } finally {
            setTogglingEvents(prev => {
                const next = new Set(prev);
                next.delete(eventId);
                return next;
            });
        }
    };

    if (events.length === 0) {
        return (
            <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                    <Calendar className="h-12 w-12 text-gray-400 mb-4" />
                    <div className="text-center">
                        <div className="font-medium text-gray-900 mb-1">No upcoming events</div>
                        <div className="text-sm text-gray-500">
                            Connect your calendar to see upcoming meetings
                        </div>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="space-y-3">
            {events.map((event) => {
                const startTime = new Date(event.start_time);
                const endTime = new Date(event.end_time);
                const isToday = startTime.toDateString() === new Date().toDateString();
                const timeUntil = formatDistanceToNow(startTime, { addSuffix: true });

                return (
                    <Card key={event.id} className={isToday ? 'border-blue-200 bg-blue-50/30' : ''}>
                        <CardContent className="p-4">
                            <div className="flex items-start justify-between gap-4">
                                {/* Event Info */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-2">
                                        <h3 className="font-semibold text-gray-900 truncate">
                                            {event.title}
                                        </h3>
                                        {isToday && (
                                            <Badge variant="primary" className="text-xs">
                                                Today
                                            </Badge>
                                        )}
                                        {event.auto_join_scheduled && (
                                            <Badge variant="neutral" className="text-xs">
                                                Scheduled
                                            </Badge>
                                        )}
                                    </div>

                                    {/* Time */}
                                    <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                                        <div className="flex items-center gap-1.5">
                                            <Clock className="h-4 w-4" />
                                            <span>
                                                {format(startTime, 'h:mm a')} - {format(endTime, 'h:mm a')}
                                            </span>
                                        </div>
                                        <div className="text-gray-500">{timeUntil}</div>
                                    </div>

                                    {/* Meeting Platform */}
                                    {event.has_meeting_url && event.meeting_platform && (
                                        <div className="flex items-center gap-2">
                                            <Video className="h-4 w-4 text-gray-400" />
                                            <Badge
                                                variant="secondary"
                                                className={platformConfig[event.meeting_platform]?.color}
                                            >
                                                {platformConfig[event.meeting_platform]?.label}
                                            </Badge>
                                            {event.meeting_url && (
                                                <a
                                                    href={event.meeting_url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="text-xs text-blue-600 hover:underline"
                                                >
                                                    Join manually
                                                </a>
                                            )}
                                        </div>
                                    )}
                                </div>

                                {/* Auto-Join Toggle */}
                                {event.has_meeting_url && (
                                    <div className="flex items-center gap-3">
                                        <div className="text-right">
                                            <div className="text-sm font-medium text-gray-700">Auto-Join</div>
                                            <div className="text-xs text-gray-500">
                                                {event.auto_join_enabled ? 'Enabled' : 'Disabled'}
                                            </div>
                                        </div>
                                        <Switch
                                            checked={event.auto_join_enabled}
                                            onCheckedChange={() =>
                                                handleAutoJoinToggle(event.id, event.auto_join_enabled)
                                            }
                                            disabled={togglingEvents.has(event.id)}
                                        />
                                    </div>
                                )}
                            </div>

                            {/* Description */}
                            {event.description && (
                                <div className="mt-3 pt-3 border-t">
                                    <p className="text-sm text-gray-600 line-clamp-2">{event.description}</p>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                );
            })}
        </div>
    );
}