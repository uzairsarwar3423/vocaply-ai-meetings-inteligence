'use client';

import { useState, useEffect } from 'react';
import CalendarSync from '@/components/calendar/CalendarSync/CalendarSync';
import EventList from '@/components/calendar/EventList/EventList';
import AutoJoinSettings from '@/components/calendar/AutoJoinSettings/AutoJoinSettings';
import UpcomingMeetings from '@/components/calendar/UpcomingMeetings/UpcomingMeetings';
import { apiClient } from '@/lib/api/client';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Calendar as CalendarIcon, Settings, ShieldCheck, Clock } from 'lucide-react';

export default function CalendarPage() {
    const [events, setEvents] = useState([]);
    const [scheduledMeetings, setScheduledMeetings] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchCalendarData = async () => {
        setIsLoading(true);
        try {
            // In a real app, these would be API calls
            // Fetch events
            const eventsRes = await apiClient.get('/calendar/events');
            setEvents(eventsRes.data.events || []);

            // Fetch scheduled auto-joins
            const scheduledRes = await apiClient.get('/calendar/scheduled');
            setScheduledMeetings(scheduledRes.data.events || []);
        } catch (error) {
            console.error('Failed to fetch calendar data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchCalendarData();
    }, []);

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-outfit font-bold text-gray-900">Calendar & Automation</h1>
                    <p className="text-gray-500 mt-1">
                        Manage your meeting schedule and bot automation settings.
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column - Main Content */}
                <div className="lg:col-span-2 space-y-6">
                    <Tabs defaultValue="upcoming" className="w-full">
                        <TabsList className="grid w-full grid-cols-2 mb-6">
                            <TabsTrigger value="upcoming" className="flex items-center gap-2">
                                <CalendarIcon className="h-4 w-4" />
                                Upcoming Events
                            </TabsTrigger>
                            <TabsTrigger value="settings" className="flex items-center gap-2">
                                <Settings className="h-4 w-4" />
                                Auto-Join Rules
                            </TabsTrigger>
                        </TabsList>

                        <TabsContent value="upcoming" className="space-y-6">
                            <EventList
                                events={events}
                                onAutoJoinToggle={() => fetchCalendarData()}
                            />
                        </TabsContent>

                        <TabsContent value="settings" className="space-y-6">
                            <AutoJoinSettings />
                        </TabsContent>
                    </Tabs>
                </div>

                {/* Right Column - Status & Config */}
                <div className="space-y-6">
                    <section>
                        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3 px-1 flex items-center gap-2">
                            <ShieldCheck className="h-4 w-4" />
                            Connection
                        </h2>
                        <CalendarSync onSyncComplete={fetchCalendarData} />
                    </section>

                    <section>
                        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3 px-1 flex items-center gap-2">
                            <Clock className="h-4 w-4" />
                            Next Actions
                        </h2>
                        <UpcomingMeetings meetings={scheduledMeetings} />
                    </section>
                </div>
            </div>
        </div>
    );
}
