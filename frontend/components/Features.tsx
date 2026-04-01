"use client";

import React from "react";
import { motion } from "framer-motion";
import { Target, Zap, BarChart3, Bell, Share2, Shield, ArrowRight } from "lucide-react";

const features = [
    {
        title: "AI Action Item Extraction",
        description: "Automatically identify tasks, owners, and deadlines directly from your meeting transcriptions.",
        icon: Target,
        color: "text-primary",
        bg: "bg-primary/10",
    },
    {
        title: "Real-time Transcription",
        description: "Multi-language support with high accuracy for Zoom, Google Meet, and Microsoft Teams.",
        icon: Zap,
        color: "text-secondary",
        bg: "bg-secondary/10",
    },
    {
        title: "Commitment Tracking",
        description: "Monitor progress on every task assigned during meetings without manually checking in.",
        icon: BarChart3,
        color: "text-blue-600",
        bg: "bg-blue-50",
    },
    {
        title: "Smart Notifications",
        description: "Push reminders to Slack or Email when deadlines are approaching or things fall through the cracks.",
        icon: Bell,
        color: "text-orange-600",
        bg: "bg-orange-50",
    },
    {
        title: "Deep Integrations",
        description: "Sync your meeting action items directly with Jira, Linear, Asana, and Notion.",
        icon: Share2,
        color: "text-purple-600",
        bg: "bg-purple-50",
    },
    {
        title: "Enterprise Security",
        description: "SOC2 compliant, end-to-end encryption. Your meeting data is private and secure.",
        icon: Shield,
        color: "text-emerald-600",
        bg: "bg-emerald-50",
    },
];

const Features = () => {
    return (
        <section id="features" className="py-32 bg-neutral-50/50 relative overflow-hidden">
            {/* Premium Background Decoration */}
            <div className="absolute top-[20%] right-[-10%] w-[600px] h-[600px] bg-primary/5 rounded-full blur-[140px] -z-10" />
            <div className="absolute bottom-[20%] left-[-10%] w-[600px] h-[600px] bg-secondary/5 rounded-full blur-[140px] -z-10" />

            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center max-w-3xl mx-auto mb-24">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-neutral-900/5 text-neutral-900 border border-neutral-900/10 mb-8"
                    >
                        <span className="text-[10px] font-black uppercase tracking-[0.2em]">Core Capabilities</span>
                    </motion.div>

                    <motion.h3
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-5xl lg:text-6xl font-black font-outfit text-neutral-900 mb-8 tracking-tighter"
                    >
                        Everything you need to turn <br />
                        <span className="text-primary">Talk into Results.</span>
                    </motion.h3>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                        className="text-xl text-neutral-500 font-medium tracking-tight leading-relaxed"
                    >
                        Stop losing track of meeting outcomes. Vocaply provides a comprehensive suite of tools to ensure every commitment is captured and completed.
                    </motion.p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
                    {features.map((feature, index) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, scale: 0.95 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: index * 0.05 }}
                            whileHover={{ y: -8 }}
                            className="p-10 rounded-[2.5rem] glass-card border-white/40 bg-white/40 hover:bg-white/80 transition-all duration-500 group relative overflow-hidden"
                        >
                            <div className={`w-16 h-16 rounded-[1.25rem] flex items-center justify-center mb-8 group-hover:rotate-12 group-hover:scale-110 transition-all duration-500 shadow-lg ${feature.bg} ${feature.color}`}>
                                <feature.icon size={30} strokeWidth={2.5} />
                            </div>

                            <h4 className="text-2xl font-black font-outfit text-neutral-900 mb-4 tracking-tight group-hover:text-primary transition-colors">{feature.title}</h4>

                            <p className="text-neutral-500 leading-relaxed font-medium mb-8">
                                {feature.description}
                            </p>

                            <div className="flex items-center gap-2 text-[11px] font-black uppercase tracking-widest text-neutral-400 group-hover:text-primary transition-colors cursor-pointer">
                                Learn more <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                            </div>

                            {/* Decorative background number */}
                            <span className="absolute top-10 right-10 text-8xl font-black text-neutral-950/2 tracking-tighter opacity-0 group-hover:opacity-100 transition-opacity">
                                0{index + 1}
                            </span>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Features;
