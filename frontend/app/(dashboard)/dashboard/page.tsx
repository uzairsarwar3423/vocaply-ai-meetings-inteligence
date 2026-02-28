"use client";

import { useAuthStore } from "@/store/authStore";
import { useMeetings } from "@/hooks/useMeetings";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Video, CheckSquare, Users, UploadCloud, ArrowRight } from "lucide-react";
import Link from 'next/link';
import FileUploader from "@/components/meetings/FileUploader/FileUploader";

export default function DashboardPage() {
    const { user } = useAuthStore();
    const { meetings, isLoading, totalMeetings } = useMeetings();
    const [scheduledEvents, setScheduledEvents] = useState([]);

    useEffect(() => {
        const fetchScheduled = async () => {
            try {
                const res = await fetch('/api/v1/calendar/scheduled');
                if (res.ok) {
                    const data = await res.json();
                    setScheduledEvents(data.events || []);
                }
            } catch (error) {
                console.error("Failed to fetch scheduled events", error);
            }
        };
        fetchScheduled();
    }, []);

    // Get the most recent meeting for the Quick Upload widget
    const recentMeeting = meetings && meetings.length > 0 ? meetings[0] : null;

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-outfit font-bold text-gray-900">Dashboard Overview</h1>
                    <p className="text-gray-500 mt-1">
                        Welcome back, {user?.full_name || 'User'}. Ready to turn meetings into action?
                    </p>
                </div>
                <Link href="/meetings/new">
                    <Button className="gap-2">
                        <Plus size={18} />
                        <span>New Meeting</span>
                    </Button>
                </Link>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[
                    { label: "Total Meetings", value: totalMeetings || "0", icon: Video, color: "text-blue-500", bg: "bg-blue-50" },
                    { label: "Tasks Pending", value: "12", icon: CheckSquare, color: "text-amber-500", bg: "bg-amber-50" }, // Placeholder for now
                    { label: "Team Members", value: "8", icon: Users, color: "text-primary", bg: "bg-primary/5" }, // Placeholder
                    { label: "Recording Hours", value: "24h", icon: Video, color: "text-green-500", bg: "bg-green-50" }, // Placeholder
                ].map((stat, i) => (
                    <Card key={i} className="shadow-sm border-gray-100/50">
                        <CardContent className="p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-400 font-inter">{stat.label}</p>
                                    <h3 className="text-2xl font-bold font-outfit mt-1">{stat.value}</h3>
                                </div>
                                <div className={`w-12 h-12 rounded-2xl ${stat.bg} ${stat.color} flex items-center justify-center`}>
                                    <stat.icon size={24} />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Meetings */}
                <div className="lg:col-span-2 space-y-6">
                    <h2 className="text-lg font-bold font-outfit text-gray-900">Recent Meetings</h2>
                    {isLoading ? (
                        <div className="p-12 flex justify-center text-gray-400">Loading...</div>
                    ) : meetings && meetings.length > 0 ? (
                        <div className="grid gap-4">
                            {meetings.slice(0, 3).map((meeting) => (
                                <Link href={`/meetings/${meeting.id}`} key={meeting.id}>
                                    <Card className="hover:shadow-md transition-shadow cursor-pointer border-gray-100/50">
                                        <CardContent className="p-5 flex items-center justify-between">
                                            <div className="flex items-center gap-4">
                                                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                                                    <Video size={18} />
                                                </div>
                                                <div>
                                                    <h4 className="font-bold text-gray-900">{meeting.title}</h4>
                                                    <p className="text-xs text-gray-500">
                                                        {new Date(meeting.startTime).toLocaleDateString()} • {meeting.platform}
                                                    </p>
                                                </div>
                                            </div>
                                            <Button variant="ghost" size="sm" className="text-gray-400 hover:text-primary">
                                                View <ArrowRight size={16} className="ml-1" />
                                            </Button>
                                        </CardContent>
                                    </Card>
                                </Link>
                            ))}
                        </div>
                    ) : (
                        <Card className="border-dashed border-2 border-gray-100 bg-gray-50/30">
                            <CardContent className="p-12 flex flex-col items-center justify-center text-center">
                                <div className="w-16 h-16 bg-white rounded-full shadow-md flex items-center justify-center mb-4 text-gray-300">
                                    <Video size={32} />
                                </div>
                                <h3 className="text-xl font-outfit font-bold text-gray-900">No recent meetings</h3>
                                <p className="text-gray-500 max-w-sm mt-2 font-inter text-sm">
                                    Schedule a new meeting to get started with AI insights.
                                </p>
                                <Link href="/meetings/new" className="mt-6">
                                    <Button variant="outline">Create Meeting</Button>
                                </Link>
                            </CardContent>
                        </Card>
                    )}
                </div>

                {/* Quick Upload & Calendar Widget */}
                <div className="space-y-8">
                    <div className="space-y-6">
                        <div className="flex items-center justify-between">
                            <h2 className="text-lg font-bold font-outfit text-gray-900">Upcoming Schedule</h2>
                            <Link href="/calendar">
                                <Button variant="ghost" size="sm" className="text-primary hover:bg-primary/5 h-8">
                                    View Calendar
                                </Button>
                            </Link>
                        </div>
                        <Card className="border-gray-100/50 shadow-sm">
                            <CardContent className="p-0">
                                <div className="p-4 border-b border-gray-50 bg-gray-50/30">
                                    <div className="flex items-center gap-2">
                                        <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                                        <span className="text-xs font-medium text-gray-600">Auto-join active</span>
                                    </div>
                                </div>
                                <div className="divide-y divide-gray-50 max-h-[300px] overflow-y-auto">
                                    {scheduledEvents.length > 0 ? (
                                        scheduledEvents.map((event: any) => (
                                            <div key={event.id} className="p-4 flex items-center gap-3 hover:bg-gray-50/50 transition-colors">
                                                <div className="w-10 h-10 rounded-xl bg-primary/5 flex items-center justify-center text-primary flex-shrink-0">
                                                    <Video size={18} />
                                                </div>
                                                <div className="min-w-0 flex-1">
                                                    <p className="text-sm font-semibold text-gray-900 truncate">{event.title}</p>
                                                    <p className="text-xs text-gray-500">
                                                        {new Date(event.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • Sync active
                                                    </p>
                                                </div>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="p-8 text-center">
                                            <p className="text-sm text-gray-400">No events scheduled today</p>
                                        </div>
                                    )}
                                </div>
                                <div className="p-4 bg-gray-50/50">
                                    <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wider">
                                        Last checked: Just now
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="space-y-6">
                        <h2 className="text-lg font-bold font-outfit text-gray-900">Quick Upload</h2>
                        <Card className="border-gray-100/50 shadow-sm">
                            <CardContent className="p-6">
                                {recentMeeting ? (
                                    <div className="space-y-4">
                                        <div className="flex items-center gap-2 mb-2">
                                            <UploadCloud className="text-primary w-5 h-5" />
                                            <p className="text-sm font-semibold text-gray-700">
                                                Upload to: <span className="text-primary truncate block max-w-[150px]">{recentMeeting.title}</span>
                                            </p>
                                        </div>
                                        <FileUploader
                                            meetingId={recentMeeting.id}
                                            onSuccess={() => window.location.reload()}
                                        />
                                    </div>
                                ) : (
                                    <div className="text-center py-8">
                                        <p className="text-gray-400 text-sm mb-4">Create a meeting first to upload recordings.</p>
                                        <Link href="/meetings/new">
                                            <Button size="sm" className="w-full">Create Meeting</Button>
                                        </Link>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
