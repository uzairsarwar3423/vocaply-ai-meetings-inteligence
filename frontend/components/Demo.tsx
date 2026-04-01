"use client";

import React from "react";
import { motion } from "framer-motion";
import { Play, Sparkles, Zap, Shield, CheckCircle2, Globe, Lock, Cpu } from "lucide-react";
import Image from "next/image";

const Demo = () => {
    const features = [
        {
            icon: <Cpu className="text-primary" size={22} />,
            title: "Real-time Processing",
            desc: "Extract strategic commitments as they happen, with sub-second latency.",
            bg: "bg-primary/5"
        },
        {
            icon: <Sparkles className="text-secondary" size={22} />,
            title: "AI-Powered Intelligence",
            desc: "Smart synopses that highlight the true intent behind every statement.",
            bg: "bg-secondary/5"
        },
        {
            icon: <Lock className="text-amber-600" size={22} />,
            title: "Enterprise Encryption",
            desc: "SOC2 compliant recording with end-to-end metadata protection.",
            bg: "bg-amber-50"
        }
    ];

    return (
        <section id="demo" className="py-32 md:py-48 bg-neutral-50/50 relative overflow-hidden">
            {/* Premium Background Decoration */}
            <div className="absolute top-0 right-[-10%] w-[800px] h-[800px] bg-primary/5 rounded-full blur-[160px] -z-10 animate-pulse" />
            <div className="absolute bottom-0 left-[-10%] w-[800px] h-[800px] bg-secondary/5 rounded-full blur-[160px] -z-10" />

            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center mb-24 lg:mb-32">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-flex items-center gap-2.5 px-5 py-2 rounded-full bg-primary/10 text-primary text-[10px] font-black uppercase tracking-[0.2em] mb-8 border border-primary/20"
                    >
                        <Play size={14} className="fill-primary" />
                        <span>Product Showcase</span>
                    </motion.div>

                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-5xl md:text-7xl font-black font-outfit text-neutral-900 mb-8 tracking-tighter"
                    >
                        Experience Meeting <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-teal-500 to-secondary relative">
                            Intelligence.
                            <div className="absolute -bottom-4 left-0 w-full h-2 bg-primary/10 rounded-full blur-xl" />
                        </span>
                    </motion.h2>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                        className="text-xl text-neutral-500 max-w-2xl mx-auto font-medium tracking-tight leading-relaxed"
                    >
                        Don't just record your meetings. Turn them into data-driven decisions with our fully automated workflow engine.
                    </motion.p>
                </div>

                <div className="grid lg:grid-cols-12 gap-16 lg:gap-24 items-center">
                    {/* Left: Interactive Frame */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 1, ease: "circOut" }}
                        className="lg:col-span-8 relative group"
                    >
                        {/* Browser Frame Decoration */}
                        <div className="relative rounded-[2.5rem] overflow-hidden shadow-[0_50px_100px_rgba(0,0,0,0.12)] border border-white/40 bg-white/20 backdrop-blur-3xl group-hover:shadow-primary/20 transition-all duration-700 p-2">
                            <div className="relative rounded-[2rem] overflow-hidden bg-neutral-950 border border-neutral-800 shadow-inner">
                                {/* Browser Header */}
                                <div className="bg-neutral-900 border-b border-neutral-800 px-6 py-4 flex items-center justify-between">
                                    <div className="flex gap-2">
                                        <div className="w-3 h-3 rounded-full bg-rose-500 shadow-lg shadow-rose-500/20" />
                                        <div className="w-3 h-3 rounded-full bg-amber-500 shadow-lg shadow-amber-500/20" />
                                        <div className="w-3 h-3 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/20" />
                                    </div>
                                    <div className="bg-neutral-800/50 border border-neutral-700 rounded-lg px-8 py-1.5 text-[10px] text-neutral-400 font-bold tracking-tight flex items-center gap-2">
                                        <Globe size={10} /> app.vocaply.ai/meeting/q3-strategy-review
                                    </div>
                                    <div className="w-10" />
                                </div>

                                {/* Dashboard Image / Visual */}
                                <div className="aspect-[16/10] relative bg-neutral-900 overflow-hidden">
                                    <img
                                        src="/images/platform_dashboard_preview.png"
                                        alt="Vocaply Dashboard"
                                        className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-1000 opacity-80"
                                    />

                                    {/* Play Overlay */}
                                    <div className="absolute inset-0 bg-neutral-950/40 group-hover:bg-neutral-950/20 transition-all flex items-center justify-center z-20">
                                        <motion.button
                                            whileHover={{ scale: 1.1 }}
                                            whileTap={{ scale: 0.95 }}
                                            className="w-24 h-24 rounded-[2rem] bg-white text-primary flex items-center justify-center shadow-2xl backdrop-blur-sm bg-white/90 border border-white"
                                        >
                                            <Play fill="currentColor" size={32} className="ml-1" />
                                        </motion.button>
                                    </div>

                                    {/* Floating AI Badge */}
                                    <motion.div
                                        animate={{ y: [0, -10, 0] }}
                                        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                                        className="absolute top-10 right-10 glass-panel px-6 py-4 rounded-2xl border-white/20 shadow-2xl z-30 hidden md:block"
                                    >
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-500">
                                                <div className="relative">
                                                    <Sparkles size={24} />
                                                    <motion.div
                                                        animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
                                                        transition={{ duration: 2, repeat: Infinity }}
                                                        className="absolute inset-0 bg-emerald-400 rounded-full blur-sm"
                                                    />
                                                </div>
                                            </div>
                                            <div>
                                                <p className="text-[10px] font-black text-neutral-400 uppercase tracking-widest leading-tight">Action Items</p>
                                                <p className="text-sm font-black text-neutral-900 leading-tight mt-0.5">3 Strategic Tasks Extracted</p>
                                            </div>
                                        </div>
                                    </motion.div>
                                </div>
                            </div>
                        </div>
                    </motion.div>

                    {/* Right: Feature Highlights */}
                    <div className="lg:col-span-4 flex flex-col gap-6">
                        {features.map((f, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: 30 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: 0.3 + (i * 0.1) }}
                                whileHover={{ x: 10 }}
                                className="p-8 rounded-[2rem] glass-panel border-white/40 bg-white/40 hover:bg-white transition-all group/card shadow-sm hover:shadow-xl"
                            >
                                <div className={`w-14 h-14 rounded-2xl ${f.bg} shadow-soft flex items-center justify-center mb-6 group-hover/card:scale-110 transition-transform duration-500`}>
                                    {f.icon}
                                </div>
                                <h4 className="text-2xl font-black font-outfit text-neutral-900 mb-3 tracking-tight">{f.title}</h4>
                                <p className="text-neutral-500 font-medium leading-relaxed tracking-tight">{f.desc}</p>
                            </motion.div>
                        ))}

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.7 }}
                            className="mt-6"
                        >
                            <button className="w-full h-20 bg-primary text-white font-black uppercase tracking-widest text-[11px] rounded-3xl shadow-2xl shadow-primary/20 hover:bg-neutral-900 transition-all active:scale-95 group overflow-hidden relative">
                                <span className="relative z-10 flex items-center justify-center gap-3">
                                    Explore Full Capabilities <Zap size={18} className="group-hover:rotate-12 transition-transform" />
                                </span>
                                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                            </button>
                        </motion.div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Demo;
