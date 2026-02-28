'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Bot, Clock, Calendar } from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';

interface ScheduledMeeting {
    id: string;
    title: string;
    start_time: string;
    meeting_url: string;
    auto_join_scheduled_at: string;
}

interface UpcomingMeetingsProps {
    meetings: ScheduledMeeting[];
}

export default function UpcomingMeetings({ meetings }: UpcomingMeetingsProps) {
    if (meetings.length === 0) {
        return null;
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Bot className="h-5 w-5 text-blue-600" />
                    Scheduled Auto-Joins
                </CardTitle>
                <CardDescription>
                    Bots will automatically join these meetings 2 minutes before they start
                </CardDescription>
            </CardHeader>

            <CardContent>
                <div className="space-y-3">
                    {meetings.map((meeting) => {
                        const startTime = new Date(meeting.start_time);
                        const timeUntil = formatDistanceToNow(startTime, { addSuffix: true });
                        const isWithinHour = startTime.getTime() - Date.now() < 3600000;

                        return (
                            <div
                                key={meeting.id}
                                className={`
                  flex items-center justify-between p-3 rounded-lg border
                  ${isWithinHour ? 'bg-blue-50 border-blue-200' : 'bg-gray-50'}
                `}
                            >
                                <div className="flex items-center gap-3">
                                    {/* Bot Icon */}
                                    <div
                                        className={`
                      p-2 rounded-full
                      ${isWithinHour ? 'bg-blue-100' : 'bg-gray-100'}
                    `}
                                    >
                                        <Bot className={`h-4 w-4 ${isWithinHour ? 'text-blue-600' : 'text-gray-600'}`} />
                                    </div>

                                    {/* Meeting Info */}
                                    <div>
                                        <div className="font-medium text-gray-900 flex items-center gap-2">
                                            {meeting.title}
                                            {isWithinHour && (
                                                <Badge variant="primary" className="text-xs">
                                                    Starting Soon
                                                </Badge>
                                            )}
                                        </div>
                                        <div className="flex items-center gap-4 text-sm text-gray-600 mt-1">
                                            <div className="flex items-center gap-1">
                                                <Calendar className="h-3 w-3" />
                                                {format(startTime, 'MMM d, h:mm a')}
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <Clock className="h-3 w-3" />
                                                {timeUntil}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Status Badge */}
                                <Badge variant="neutral" className="gap-1">
                                    <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                                    Ready
                                </Badge>
                            </div>
                        );
                    })}
                </div>
            </CardContent>
        </Card>
    );
}