"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Sparkles, Loader2, MessageCircle } from "lucide-react";

interface Message {
    role: "user" | "assistant";
    content: string;
    id: string;
    timestamp: Date;
}

interface VocaplyChatProps {
    meetingId: string;
    ws: WebSocket | null;
}

export default function VocaplyChat({ meetingId, ws }: VocaplyChatProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputValue, setInputValue] = useState("");
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }, [messages, isTyping]);

    useEffect(() => {
        if (!ws) return;

        const handleMessage = (event: MessageEvent) => {
            const msg = JSON.parse(event.data);
            if (msg.event === "chat_response" && msg.data.meeting_id === meetingId) {
                const newMsg: Message = {
                    role: "assistant",
                    content: msg.data.answer,
                    id: Math.random().toString(36).substr(2, 9),
                    timestamp: new Date()
                };
                setMessages((prev) => [...prev, newMsg]);
                setIsTyping(false);
            }
        };

        ws.addEventListener("message", handleMessage);
        return () => ws.removeEventListener("message", handleMessage);
    }, [ws, meetingId]);

    const sendMessage = () => {
        if (!inputValue.trim() || !ws) return;

        const userMsg: Message = {
            role: "user",
            content: inputValue,
            id: Math.random().toString(36).substr(2, 9),
            timestamp: new Date()
        };

        setMessages((prev) => [...prev, userMsg]);
        setIsTyping(true);

        // Send via WebSocket
        ws.send(JSON.stringify({
            event: "chat_message",
            data: {
                meeting_id: meetingId,
                message: inputValue
            }
        }));

        setInputValue("");
    };

    return (
        <div className="flex-1 flex flex-col min-h-0 bg-neutral-900 overflow-hidden">
            {/* ── Chat Feed ────────────────────────────────────────────── */}
            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-hide"
            >
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-center space-y-4 px-8 mt-10">
                        <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                            <Sparkles size={32} />
                        </div>
                        <h4 className="text-white text-sm font-black">AI Meeting Intelligence</h4>
                        <p className="text-neutral-500 text-xs font-medium leading-relaxed">
                            Ask me about what's being discussed, summarize points, or identify tasks in real-time.
                        </p>
                    </div>
                )}

                <AnimatePresence initial={false}>
                    {messages.map((msg) => (
                        <motion.div
                            key={msg.id}
                            initial={{ opacity: 0, scale: 0.95, y: 10 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                        >
                            <div className={`flex gap-3 max-w-[85%] ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                                <div className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center border ${msg.role === "user" ? "bg-white/5 border-white/10 text-neutral-400" : "bg-primary border-primary/20 text-white"
                                    }`}>
                                    {msg.role === "user" ? <User size={14} /> : <Bot size={14} />}
                                </div>
                                <div className={`p-4 rounded-2xl text-sm font-medium leading-relaxed ${msg.role === "user"
                                        ? "bg-white/5 text-neutral-200 border border-white/5"
                                        : "bg-neutral-800 text-neutral-300 border border-white/5 shadow-xl shadow-black/40"
                                    } shadow-sm`}>
                                    {msg.content}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>

                {isTyping && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex gap-3"
                    >
                        <div className="flex-shrink-0 w-8 h-8 rounded-xl bg-primary flex items-center justify-center text-white">
                            <Bot size={14} />
                        </div>
                        <div className="p-4 rounded-2xl bg-neutral-800 border border-white/5 flex items-center gap-1.5">
                            <div className="w-1 h-1 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]" />
                            <div className="w-1 h-1 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]" />
                            <div className="w-1 h-1 bg-primary rounded-full animate-bounce" />
                        </div>
                    </motion.div>
                )}
            </div>

            {/* ── Input Area ───────────────────────────────────────────── */}
            <div className="p-6 bg-neutral-900 border-t border-white/5 relative">
                <div className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-2xl p-2 pl-4 focus-within:border-primary/50 transition-colors">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={(e) => e.key === "Enter" && sendMessage()}
                        placeholder="Ask Vocaply anything..."
                        className="flex-1 bg-transparent border-none text-sm text-white placeholder-neutral-600 focus:outline-none py-2"
                    />
                    <button
                        onClick={sendMessage}
                        disabled={!inputValue.trim()}
                        className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-white disabled:opacity-30 transition-all hover:scale-105 active:scale-95"
                    >
                        <Send size={18} />
                    </button>
                </div>
                <div className="mt-3 flex items-center justify-center gap-4">
                    <div className="px-2 py-1 rounded bg-white/5 border border-white/5 text-[9px] font-black text-neutral-600 uppercase tracking-widest flex items-center gap-1.5">
                        <Sparkles size={8} />
                        GPT-4o Mini
                    </div>
                    <div className="px-2 py-1 rounded bg-white/5 border border-white/5 text-[9px] font-black text-neutral-600 uppercase tracking-widest flex items-center gap-1.5">
                        <MessageCircle size={8} />
                        Context Injected
                    </div>
                </div>
            </div>
        </div>
    );
}
