"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    Video,
    MessageSquare,
    CheckSquare,
    Users,
    Settings,
    ChevronRight,
    Loader2,
    Zap,
    Send,
    Bot,
    User as UserIcon,
    AlertCircle
} from "lucide-react";

import { apiClient } from "@/lib/api/client";
import { useAuth } from "@/hooks/useAuth";
import LiveTranscript from "@/components/meeting/LiveTranscript";
import LiveActionItems from "@/components/meeting/LiveActionItems";
import VocaplyChat from "@/components/meeting/VocaplyChat";

// ── Types ────────────────────────────────────────────────────────────────────

interface TranscriptChunk {
    speaker: string;
    text: string;
    start_time: number;
    is_final: boolean;
}

interface ActionItemUpdate {
    meeting_id: string;
    count: number;
    message: string;
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function LiveMeetingPage({ params }: { params: { id: string } }) {
    const meetingId = params.id;
    const { user, tokens } = useAuth();
    const token = tokens?.access_token;

    // UI State
    const [meeting, setMeeting] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<"transcript" | "chat" | "tasks">("transcript");

    // Live Data
    const [transcript, setTranscript] = useState<TranscriptChunk[]>([]);
    const [isAILoading, setIsAILoading] = useState(false);

    const wsRef = useRef<WebSocket | null>(null);

    // ── WebSocket Logic ───────────────────────────────────────────────────────

    const connectWS = useCallback(() => {
        if (!token) return;

        // Protocol for WS
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host.includes("localhost") ? "localhost:8000" : window.location.host}/api/v1/ws`;

        console.log("Connecting to WS:", wsUrl);
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log("WS Connected");
            // Authenticate
            ws.send(JSON.stringify({
                event: "authenticate",
                data: { token }
            }));
        };

        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            console.log("WS Message:", msg.event, msg.data);

            switch (msg.event) {
                case "authenticated":
                    // Subscribe to meeting channels
                    ws.send(JSON.stringify({
                        event: "subscribe",
                        data: { channel: "meeting_live", resource_id: meetingId }
                    }));
                    break;

                case "transcript_chunk":
                    setTranscript((prev) => {
                        // If the last chunk is intermediate from same speaker, update it
                        if (prev.length > 0 && !prev[prev.length - 1].is_final && prev[prev.length - 1].speaker === msg.data.speaker) {
                            const updated = [...prev];
                            updated[updated.length - 1] = msg.data;
                            return updated;
                        }
                        return [...prev, msg.data];
                    });
                    break;

                case "live_action_item":
                    // Trigger a re-fetch of action items or just show a notification
                    // We'll broadcast this event to the LiveActionItems component via a shared state or ref
                    break;
            }
        };

        ws.onclose = () => {
            console.log("WS Disconnected, retrying...");
            setTimeout(connectWS, 3000);
        };

        ws.onerror = (err) => {
            console.error("WS Error:", err);
        };
    }, [meetingId, token]);

    useEffect(() => {
        const fetchMeeting = async () => {
            try {
                const res = await apiClient.get(`/meetings/${meetingId}`);
                setMeeting(res.data);
                setLoading(false);
                connectWS();
            } catch (err: any) {
                setError(err.message || "Failed to load meeting details");
                setLoading(false);
            }
        };

        if (meetingId) fetchMeeting();

        return () => {
            if (wsRef.current) wsRef.current.close();
        };
    }, [meetingId, connectWS]);

    // ── Render ──────────────────────────────────────────────────────────────

    if (loading) {
        return (
            <div className="h-[80vh] flex flex-col items-center justify-center space-y-4">
                <Loader2 className="w-12 h-12 text-primary animate-spin" />
                <p className="text-neutral-400 font-bold uppercase tracking-widest text-xs">Initializing Live Intelligence...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="h-[80vh] flex flex-col items-center justify-center space-y-4">
                <AlertCircle className="w-12 h-12 text-rose-500" />
                <h2 className="text-xl font-black text-neutral-900">Oops! Connection Failed</h2>
                <p className="text-neutral-400 font-medium">{error}</p>
                <button
                    onClick={() => window.location.reload()}
                    className="mt-4 px-6 py-2 bg-primary text-white font-bold rounded-xl shadow-lg shadow-primary/20"
                >
                    Retry Connection
                </button>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-[calc(100vh-120px)] space-y-6">
            {/* ── Header ─────────────────────────────────────────────────── */}
            <div className="flex items-center justify-between">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <div className="h-2 w-2 bg-rose-500 rounded-full animate-pulse" />
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-rose-500">
                            Live Session
                        </span>
                    </div>
                    <h1 className="text-3xl font-outfit font-black text-neutral-900 tracking-tight">
                        {meeting?.title || "Project Sync"}
                    </h1>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={() => {
                            // Trigger mock stream for testing
                            apiClient.post(`/meetings/${meetingId}/mock-stream`);
                        }}
                        className="flex items-center gap-2 px-4 py-2 bg-neutral-100 text-neutral-600 font-bold rounded-xl text-xs hover:bg-neutral-200 transition-colors"
                    >
                        <Zap size={14} className="text-amber-500" />
                        Demo Stream
                    </button>
                    <div className="h-10 w-[1px] bg-neutral-100 mx-2" />
                    <button className="p-2.5 rounded-xl border border-neutral-100 text-neutral-400 hover:text-neutral-900 transition-colors">
                        <Settings size={20} />
                    </button>
                </div>
            </div>

            {/* ── Main content layout ────────────────────────────────────── */}
            <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 overflow-hidden">

                {/* ── Left: Live Transcript (8 cols) ────────────────────── */}
                <div className="lg:col-span-8 bg-white rounded-3xl border border-neutral-100 shadow-sm flex flex-col overflow-hidden">
                    <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-50 bg-neutral-50/30">
                        <div className="flex items-center gap-4">
                            <button
                                onClick={() => setActiveTab("transcript")}
                                className={`px-4 py-2 rounded-xl text-xs font-black transition-all ${activeTab === "transcript" ? "bg-white text-primary shadow-sm" : "text-neutral-400 hover:text-neutral-600"
                                    }`}
                            >
                                Live Transcript
                            </button>
                            <button
                                onClick={() => setActiveTab("tasks")}
                                className={`px-4 py-2 rounded-xl text-xs font-black transition-all ${activeTab === "tasks" ? "bg-white text-primary shadow-sm" : "text-neutral-400 hover:text-neutral-600"
                                    }`}
                            >
                                Action Items
                            </button>
                        </div>
                        <div className="flex items-center gap-2 text-[10px] font-bold text-neutral-400 bg-white px-3 py-1.5 rounded-full border border-neutral-100">
                            <Users size={12} />
                            {meeting?.participant_count || 0} participants
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-6 scrollbar-hide">
                        {activeTab === "transcript" ? (
                            <LiveTranscript items={transcript} />
                        ) : (
                            <LiveActionItems meetingId={meetingId} />
                        )}
                    </div>
                </div>

                {/* ── Right: AI Chat Hub (4 cols) ───────────────────────── */}
                <div className="lg:col-span-4 flex flex-col gap-6 overflow-hidden">
                    {/* Vocaply AI Chat Card */}
                    <div className="flex-1 bg-neutral-900 rounded-3xl overflow-hidden shadow-2xl flex flex-col relative border border-white/5">
                        <div className="absolute top-0 inset-x-0 h-32 bg-gradient-to-b from-primary/20 to-transparent pointer-events-none" />

                        <div className="px-6 py-5 border-b border-white/10 flex items-center justify-between relative">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-2xl bg-primary flex items-center justify-center text-white shadow-lg shadow-primary/30">
                                    <Bot size={22} />
                                </div>
                                <div>
                                    <h3 className="text-sm font-black text-white">Vocaply Assistant</h3>
                                    <div className="flex items-center gap-1.5 mt-0.5">
                                        <div className="w-1 h-1 bg-emerald-500 rounded-full" />
                                        <span className="text-[10px] text-emerald-500/80 font-bold uppercase tracking-widest">Always Listening</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <VocaplyChat meetingId={meetingId} ws={wsRef.current} />
                    </div>

                    {/* Compact Live Status Info */}
                    <div className="h-44 bg-white rounded-3xl border border-neutral-100 p-6 flex flex-col justify-between">
                        <div className="flex items-center justify-between">
                            <span className="text-[10px] font-black uppercase text-neutral-400 tracking-widest">AI Extraction</span>
                            <Zap size={16} className="text-primary animate-pulse" />
                        </div>
                        <div className="space-y-4 mt-2">
                            <div className="flex items-center justify-between">
                                <p className="text-xs font-bold text-neutral-600">Tasks Extracted</p>
                                <span className="text-xl font-black text-neutral-900">{transcript.length > 5 ? Math.floor(transcript.length / 3) : 0}</span>
                            </div>
                            <div className="w-full bg-neutral-50 h-2 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-primary"
                                    initial={{ width: "0%" }}
                                    animate={{ width: `${Math.min(100, (transcript.length / 20) * 100)}%` }}
                                />
                            </div>
                            <p className="text-[10px] text-neutral-400 font-medium">Extraction occurs every 150 words of meeting text.</p>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
