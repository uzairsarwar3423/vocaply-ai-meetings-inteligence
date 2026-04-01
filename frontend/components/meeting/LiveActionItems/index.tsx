"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckSquare, User, Calendar, Plus, Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api/client";

interface ActionItem {
    id: string;
    description: string;
    assignee: string | null;
    due_date: string | null;
    status: string;
}

export default function LiveActionItems({ meetingId }: { meetingId: string }) {
    const [items, setItems] = useState<ActionItem[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchItems = async () => {
        try {
            const res = await apiClient.get(`/action-items?meeting_id=${meetingId}`);
            setItems(res.data);
            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch action items:", err);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchItems();
        // POLL for new items every 30 seconds as a fallback to WebSocket
        const interval = setInterval(fetchItems, 30000);
        return () => clearInterval(interval);
    }, [meetingId]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-40 space-y-3">
                <Loader2 className="w-6 h-6 text-primary animate-spin" />
                <p className="text-[10px] font-black text-neutral-400 uppercase tracking-widest">Scanning meeting content...</p>
            </div>
        );
    }

    return (
        <div className="space-y-4 pb-10">
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-black text-neutral-900 uppercase tracking-wider flex items-center gap-2">
                    <CheckSquare size={14} className="text-primary" />
                    Intelligent Extraction
                </h3>
            </div>

            {items.length === 0 ? (
                <div className="p-8 border-2 border-dashed border-neutral-100 rounded-2xl flex flex-col items-center text-center">
                    <p className="text-xs text-neutral-400 font-medium leading-relaxed">
                        Vocaply AI is analyzing the conversation. Action items will appear here automatically.
                    </p>
                </div>
            ) : (
                <div className="grid gap-3">
                    {items.map((item, idx) => (
                        <motion.div
                            key={item.id}
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            className="p-4 bg-white border border-neutral-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow group relative overflow-hidden"
                        >
                            <div className="absolute top-0 left-0 w-1 h-full bg-primary/20 group-hover:bg-primary transition-colors" />

                            <p className="text-sm font-bold text-neutral-800 mb-3 leading-snug">
                                {item.description}
                            </p>

                            <div className="flex items-center gap-4">
                                <div className="flex items-center gap-1.5">
                                    <div className="w-5 h-5 rounded-lg bg-neutral-100 flex items-center justify-center text-neutral-400">
                                        <User size={10} />
                                    </div>
                                    <span className="text-[10px] font-black text-neutral-600 uppercase tracking-tight">
                                        {item.assignee || "Unassigned"}
                                    </span>
                                </div>

                                <div className="flex items-center gap-1.5">
                                    <div className="w-5 h-5 rounded-lg bg-neutral-100 flex items-center justify-center text-neutral-400">
                                        <Calendar size={10} />
                                    </div>
                                    <span className="text-[10px] font-black text-neutral-600 uppercase tracking-tight">
                                        {item.due_date ? new Date(item.due_date).toLocaleDateString() : "No Deadline"}
                                    </span>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </div>
    );
}
