"use client";

import React from "react";
import { motion } from "framer-motion";
import { Video, Sparkles, CheckCircle2, ArrowRight } from "lucide-react";


const steps = [
    {
        title: "Connect Your Calendar",
        description: "Vocaply automatically syncs with your Google or Outlook calendar to join scheduled meetings.",
        icon: Video,
        image: "/images/how_it_works_calendar.png",
        color: "text-primary",
        bg: "bg-primary/10",
    },
    {
        title: "Meeting Magic Happens",
        description: "Our AI attends the call, transcribes everything, and identifies action items in real-time.",
        icon: Sparkles,
        image: "/images/how_it_works_transcription.png",
        color: "text-secondary",
        bg: "bg-secondary/10",
    },
    {
        title: "Action Items Sync",
        description: "Tasks are automatically assigned to owners and synced with your favorite project tools.",
        icon: CheckCircle2,
        image: "/images/how_it_works_action_items.png",
        color: "text-emerald-600",
        bg: "bg-emerald-50",
    },
];

const HowItWorks = () => {
    return (
        <section id="how-it-works" className="py-32 bg-neutral-50/30 relative overflow-hidden">
            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center max-w-3xl mx-auto mb-28">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-secondary/10 text-secondary border border-secondary/20 mb-8"
                    >
                        <span className="text-[10px] font-black uppercase tracking-[0.2em]">The Workflow</span>
                    </motion.div>

                    <motion.h3
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-5xl lg:text-6xl font-black font-outfit text-neutral-900 mb-8 tracking-tighter"
                    >
                        Three Steps to <br />
                        <span className="text-secondary">Meeting Excellence.</span>
                    </motion.h3>
                </div>

                <div className="space-y-40">
                    {steps.map((step, index) => (
                        <motion.div
                            key={step.title}
                            initial={{ opacity: 0, y: 40 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.8, ease: "easeOut" }}
                            className={`flex flex-col ${index % 2 === 0 ? "lg:flex-row" : "lg:flex-row-reverse"} items-center gap-16 lg:gap-32`}
                        >
                            <div className="flex-1 text-center lg:text-left">
                                <motion.div
                                    whileHover={{ scale: 1.1, rotate: 5 }}
                                    className={`w-20 h-20 rounded-[1.5rem] ${step.bg} ${step.color} shadow-lg flex items-center justify-center mb-10 border border-white mx-auto lg:mx-0`}
                                >
                                    <step.icon size={36} strokeWidth={2.5} />
                                </motion.div>

                                <h4 className="text-4xl font-black font-outfit text-neutral-900 mb-6 tracking-tight flex items-center justify-center lg:justify-start gap-4">
                                    <span className="text-neutral-200 text-5xl">0{index + 1}</span>
                                    {step.title}
                                </h4>

                                <p className="text-xl text-neutral-500 leading-relaxed font-medium mb-10 tracking-tight">
                                    {step.description}
                                </p>

                                <div className="flex items-center justify-center lg:justify-start gap-3 text-[11px] font-black uppercase tracking-widest text-primary cursor-pointer group">
                                    System deep-dive <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                </div>
                            </div>

                            <div className="flex-1 w-full relative">
                                <div className={`absolute -inset-10 ${step.bg} rounded-full blur-[100px] opacity-30 -z-10 animate-pulse`} />
                                <motion.div
                                    whileHover={{ scale: 1.02 }}
                                    className="glass-card p-4 rounded-[3rem] border-white/50 bg-white/40 shadow-2xl relative overflow-hidden group"
                                >
                                    <div className="aspect-[4/3] rounded-[2rem] overflow-hidden bg-neutral-100 flex items-center justify-center relative">
                                        <div className="absolute inset-0 bg-gradient-to-tr from-black/5 to-transparent z-10" />
                                        <img
                                            src={step.image}
                                            alt={step.title}
                                            className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-110"
                                        />
                                    </div>

                                    {/* Floating stats card for "WOW" effect */}
                                    <motion.div
                                        animate={{ y: [0, -10, 0] }}
                                        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                                        className="absolute -bottom-6 -right-6 glass-panel px-6 py-4 rounded-2xl border-white/40 shadow-2xl hidden md:block z-20"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-600">
                                                <CheckCircle2 size={18} />
                                            </div>
                                            <span className="text-[10px] font-black uppercase tracking-widest text-neutral-700">Automation Active</span>
                                        </div>
                                    </motion.div>
                                </motion.div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default HowItWorks;
