"use client";

import { useAuthStore } from "@/store/authStore";
import { useMeetings } from "@/hooks/useMeetings";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Video, CheckSquare, Users, UploadCloud, ArrowRight, TrendingUp, Clock, Calendar as CalendarIcon, Zap } from "lucide-react";
import Link from 'next/link';
import FileUploader from "@/components/meetings/FileUploader/FileUploader";
import { apiClient } from "@/lib/api/client";
import { motion, AnimatePresence } from "framer-motion";

const container = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1
        }
    }
};

const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
};

export default function DashboardPage() {
    const { user } = useAuthStore();
    const { meetings, isLoading, totalMeetings } = useMeetings();
    const [scheduledEvents, setScheduledEvents] = useState([]);

    useEffect(() => {
        const fetchScheduled = async () => {
            try {
                const res = await apiClient.get('/calendar/scheduled');
                setScheduledEvents(res.data.events || []);
            } catch (error) {
                console.error("Failed to fetch scheduled events", error);
            }
        };
        fetchScheduled();
    }, []);

    const recentMeeting = meetings && meetings.length > 0 ? meetings[0] : null;

    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-10 pb-20"
        >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <motion.div variants={item}>
                    <div className="flex items-center gap-2 mb-1">
                        <div className="h-1 w-8 bg-primary rounded-full" />
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-primary">Overview</span>
                    </div>
                    <h1 className="text-4xl font-outfit font-black text-neutral-900 tracking-tight">Dashboard Overview</h1>
                    <p className="text-neutral-400 mt-1 font-medium">
                        Welcome back, <span className="text-neutral-900 font-bold">{user?.full_name || 'User'}</span>. Here's what's happening.
                    </p>
                </motion.div>
                <motion.div variants={item}>
                    <Link href="/meetings/new">
                        <Button className="gap-2 px-6 py-6 rounded-2xl bg-primary hover:bg-primary-600 shadow-xl shadow-primary/20 hover:shadow-primary/40 transition-all font-bold group">
                            <Plus size={20} className="group-hover:rotate-90 transition-transform duration-300" />
                            <span>New Meeting</span>
                        </Button>
                    </Link>
                </motion.div>
            </div>

            {/* Stats Grid */}
            <motion.div
                variants={item}
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
            >
                {[
                    { label: "Total Meetings", value: totalMeetings || "0", icon: Video, color: "text-primary", bg: "bg-primary/10", trend: "+12%" },
                    { label: "Tasks Pending", value: "12", icon: CheckSquare, color: "text-amber-500", bg: "bg-amber-50", trend: "Active" },
                    { label: "Team Members", value: "8", icon: Users, color: "text-indigo-500", bg: "bg-indigo-50", trend: "3 New" },
                    { label: "Recording Hours", value: "24h", icon: Clock, color: "text-emerald-500", bg: "bg-emerald-50", trend: "This Month" },
                ].map((stat, i) => (
                    <div key={i} className="group cursor-pointer">
                        <Card className="hover:shadow-2xl transition-all duration-500 border-white/20 overflow-hidden relative">
                            <div className={`absolute top-0 right-0 w-24 h-24 ${stat.bg} rounded-bl-full opacity-30 -mr-8 -mt-8 transition-all group-hover:scale-110`} />
                            <CardContent className="p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div className={`w-12 h-12 rounded-2xl ${stat.bg} ${stat.color} flex items-center justify-center shadow-inner`}>
                                        <stat.icon size={22} className="group-hover:scale-110 transition-transform" />
                                    </div>
                                    <span className={`text-[10px] font-black px-2 py-1 rounded-full ${stat.bg} ${stat.color} uppercase tracking-wider`}>
                                        {stat.trend}
                                    </span>
                                </div>
                                <p className="text-xs font-bold text-neutral-400 uppercase tracking-widest leading-none">{stat.label}</p>
                                <h3 className="text-3xl font-black font-outfit mt-2 text-neutral-900">{stat.value}</h3>
                            </CardContent>
                        </Card>
                    </div>
                ))}
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Meetings */}
                <motion.div variants={item} className="lg:col-span-2 space-y-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <h2 className="text-xl font-black font-outfit text-neutral-900">Recent Meetings</h2>
                            <div className="px-2 py-0.5 rounded-full bg-neutral-100 text-[10px] font-bold text-neutral-500 uppercase">Live Feed</div>
                        </div>
                        <Link href="/meetings" className="text-xs font-bold text-primary hover:underline uppercase tracking-wider">View All</Link>
                    </div>
                    {isLoading ? (
                        <div className="p-12 flex justify-center text-neutral-400 animate-pulse font-medium">Loading intelligence...</div>
                    ) : meetings && meetings.length > 0 ? (
                        <div className="grid gap-4">
                            {meetings.slice(0, 3).map((meeting) => (
                                <Link href={`/meetings/${meeting.id}`} key={meeting.id}>
                                    <Card className="hover:shadow-xl transition-all duration-300 cursor-pointer border-white/20 group overflow-hidden">
                                        <CardContent className="p-5 flex items-center justify-between">
                                            <div className="flex items-center gap-4">
                                                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center text-primary shadow-inner group-hover:bg-primary group-hover:text-white transition-colors duration-300">
                                                    <Video size={20} />
                                                </div>
                                                <div>
                                                    <h4 className="font-black text-neutral-900 group-hover:text-primary transition-colors">{meeting.title}</h4>
                                                    <div className="flex items-center gap-2 mt-1">
                                                        <span className="text-[10px] font-bold text-neutral-400 uppercase">{new Date(meeting.startTime).toLocaleDateString()}</span>
                                                        <span className="w-1 h-1 rounded-full bg-neutral-200" />
                                                        <span className="text-[10px] font-bold text-primary uppercase tracking-wider">{meeting.platform}</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <Button variant="ghost" size="sm" className="text-neutral-400 group-hover:text-primary group-hover:translate-x-1 transition-all">
                                                <ArrowRight size={18} />
                                            </Button>
                                        </CardContent>
                                    </Card>
                                </Link>
                            ))}
                        </div>
                    ) : (
                        <Card className="border-dashed border-2 border-neutral-200 bg-neutral-50/50">
                            <CardContent className="p-12 flex flex-col items-center justify-center text-center">
                                <div className="w-20 h-20 bg-white rounded-3xl shadow-xl flex items-center justify-center mb-6 text-neutral-100 ring-1 ring-neutral-200">
                                    <Video size={36} />
                                </div>
                                <h3 className="text-2xl font-outfit font-black text-neutral-900">No recent meetings</h3>
                                <p className="text-neutral-400 max-w-xs mt-2 font-medium">
                                    Schedule a meeting or upload a recording to see your AI-processed insights here.
                                </p>
                                <Link href="/meetings/new" className="mt-8">
                                    <Button className="rounded-xl px-8 font-bold shadow-lg shadow-primary/20">Get Started</Button>
                                </Link>
                            </CardContent>
                        </Card>
                    )}
                </motion.div>

                {/* Quick Upload & Calendar Widget */}
                <motion.div variants={item} className="space-y-10">
                    <div className="space-y-6">
                        <div className="flex items-center justify-between">
                            <h2 className="text-xl font-black font-outfit text-neutral-900 tracking-tight">Schedule</h2>
                            <Link href="/calendar">
                                <Button variant="ghost" size="sm" className="text-primary hover:bg-primary/10 h-8 rounded-lg font-bold text-xs">
                                    Explore
                                </Button>
                            </Link>
                        </div>
                        <Card className="border-white/20 shadow-xl shadow-neutral-200/20 overflow-hidden">
                            <CardContent className="p-0">
                                <div className="p-4 border-b border-neutral-100/50 bg-neutral-50/30 flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                                        <span className="text-[10px] font-black text-neutral-500 uppercase tracking-widest">Auto-join Active</span>
                                    </div>
                                    <Zap size={14} className="text-amber-500 fill-amber-500" />
                                </div>
                                <div className="divide-y divide-neutral-100/50 max-h-[350px] overflow-y-auto custom-scrollbar">
                                    {scheduledEvents.length > 0 ? (
                                        scheduledEvents.map((event: any) => (
                                            <div key={event.id} className="p-4 flex items-center gap-3 hover:bg-white transition-all cursor-pointer group">
                                                <div className="w-10 h-10 rounded-xl bg-neutral-100 flex items-center justify-center text-neutral-400 group-hover:bg-primary-50 group-hover:text-primary transition-colors">
                                                    <CalendarIcon size={18} />
                                                </div>
                                                <div className="min-w-0 flex-1">
                                                    <p className="text-sm font-bold text-neutral-900 truncate leading-tight">{event.title}</p>
                                                    <p className="text-[10px] text-neutral-400 font-bold uppercase mt-0.5">
                                                        {new Date(event.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} • {event.platform || 'Online'}
                                                    </p>
                                                </div>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="p-12 text-center">
                                            <div className="w-12 h-12 bg-neutral-50 rounded-full flex items-center justify-center mx-auto mb-3">
                                                <Clock className="text-neutral-200" size={20} />
                                            </div>
                                            <p className="text-xs font-bold text-neutral-300 uppercase tracking-widest">Queue Empty</p>
                                        </div>
                                    )}
                                </div>
                                <div className="p-4 bg-neutral-50/50 flex justify-center">
                                    <p className="text-[9px] text-neutral-400 font-black uppercase tracking-[0.2em]">
                                        Last Synced: Just Now
                                    </p>
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    <div className="space-y-6">
                        <h2 className="text-xl font-black font-outfit text-neutral-900 tracking-tight">Quick Action</h2>
                        <Card className="border-white/20 shadow-xl shadow-neutral-200/20 bg-gradient-to-br from-white to-neutral-50/50">
                            <CardContent className="p-6">
                                {recentMeeting ? (
                                    <div className="space-y-5">
                                        <div className="flex items-center gap-3 p-3 bg-white rounded-2xl border border-neutral-100 shadow-sm">
                                            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                                                <UploadCloud size={20} />
                                            </div>
                                            <div className="min-w-0">
                                                <p className="text-[10px] font-black text-neutral-400 uppercase tracking-widest">Uploading to</p>
                                                <p className="text-xs font-bold text-neutral-900 truncate max-w-[140px]">{recentMeeting.title}</p>
                                            </div>
                                        </div>
                                        <FileUploader
                                            meetingId={recentMeeting.id}
                                            onSuccess={() => window.location.reload()}
                                        />
                                    </div>
                                ) : (
                                    <div className="text-center py-6">
                                        <div className="w-14 h-14 bg-white rounded-3xl shadow-lg flex items-center justify-center mx-auto mb-4 border border-neutral-100">
                                            <UploadCloud className="text-neutral-200" size={24} />
                                        </div>
                                        <p className="text-xs font-bold text-neutral-400 leading-relaxed max-w-[180px] mx-auto">Create a meeting workspace to unlock instant uploads.</p>
                                        <Link href="/meetings/new" className="mt-6 block">
                                            <Button size="sm" className="w-full rounded-xl font-bold">New Workspace</Button>
                                        </Link>
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </motion.div>
            </div>
        </motion.div>
    );
}
