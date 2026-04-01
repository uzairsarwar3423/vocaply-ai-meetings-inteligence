"use client";

import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User, MessageSquare } from "lucide-react";

interface TranscriptChunk {
    speaker: string;
    text: string;
    start_time: number;
    is_final: boolean;
}

interface LiveTranscriptProps {
    items: TranscriptChunk[];
}

export default function LiveTranscript({ items }: LiveTranscriptProps) {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [items]);

    if (items.length === 0) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-neutral-300 space-y-3">
                <MessageSquare size={48} strokeWidth={1} />
                <p className="font-medium text-sm">Waiting for transcription to start...</p>
            </div>
        );
    }

    return (
        <div className="space-y-6 pb-20">
            {items.map((item, idx) => (
                <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex gap-4 group"
                >
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-neutral-100 flex items-center justify-center text-neutral-400 mt-1 group-hover:bg-primary/10 group-hover:text-primary transition-all">
                        <User size={14} />
                    </div>

                    <div className="flex-1 space-y-1">
                        <div className="flex items-center gap-2">
                            <span className="text-xs font-black text-neutral-900 tracking-tight">{item.speaker}</span>
                            <span className="text-[10px] text-neutral-400 font-medium">
                                {new Date(item.start_time * 1000).toISOString().substr(14, 5)}
                            </span>
                        </div>
                        <p className={`text-sm leading-relaxed ${item.is_final ? 'text-neutral-600' : 'text-neutral-300 italic animate-pulse'}`}>
                            {item.text}
                        </p>
                    </div>
                </motion.div>
            ))}
            <div ref={bottomRef} />
        </div>
    );
}
