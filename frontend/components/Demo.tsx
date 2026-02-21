"use client";

import React from "react";
import { motion } from "framer-motion";
import { Play, Sparkles, Zap, Shield, CheckCircle2 } from "lucide-react";
import Image from "next/image";

const Demo = () => {
    // Importing the generated dashboard image
    const dashboardImage = "/_next/image?url=%2Fhome%2Fuzair%2F.gemini%2Fantigravity%2Fbrain%2F5fe4d10a-d4ed-4bd4-8801-8372bb4bf658%2Fai_meeting_dashboard_demo_1771217753418.png&w=1200&q=75";

    const features = [
        {
            icon: <Zap className="text-secondary-500" size={20} />,
            title: "Real-time Processing",
            desc: "Extract insights as the meeting happens, not hours later."
        },
        {
            icon: <Sparkles className="text-primary-500" size={20} />,
            title: "AI-Powered Summaries",
            desc: "Smart synopses that highlight the 'why' behind the 'what'."
        },
        {
            icon: <Shield className="text-blue-500" size={20} />,
            title: "Enterpise Security",
            desc: "SOC2 compliant recording and metadata encryption."
        }
    ];

    return (
        <section id="demo" className="py-24 md:py-32 bg-white relative overflow-hidden">
            {/* Background Decorative Elements */}
            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary-100/30 rounded-full blur-[120px] -translate-y-1/2 translate-x-1/2 -z-10"></div>
            <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-secondary-100/20 rounded-full blur-[100px] translate-y-1/2 -translate-x-1/2 -z-10"></div>

            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center mb-16 md:mb-24">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-50 text-primary-700 text-sm font-semibold mb-6 border border-primary-100"
                    >
                        <Play size={16} fill="currentColor" />
                        <span>Interactive Product Tour</span>
                    </motion.div>

                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-4xl md:text-6xl font-outfit font-bold text-neutral-900 mb-6 tracking-tight"
                    >
                        Experience Meeting <br />
                        <span className="text-gradient">Intelligence.</span>
                    </motion.h2>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.2 }}
                        className="text-lg md:text-xl text-neutral-500 max-w-2xl mx-auto font-inter"
                    >
                        Dont just record your meetings. Turn them into data-driven decisions with our automated workflow engine.
                    </motion.p>
                </div>

                <div className="grid lg:grid-cols-12 gap-12 items-center">
                    {/* Left: Interactive Frame */}
                    <motion.div
                        initial={{ opacity: 0, x: -30 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        className="lg:col-span-8 relative group"
                    >
                        {/* Browser Frame Decoration */}
                        <div className="relative rounded-2xl overflow-hidden shadow-2xl border border-neutral-200 bg-neutral-900 group-hover:shadow-primary transition-all duration-500">
                            {/* Browser Header */}
                            <div className="bg-neutral-50 border-b border-neutral-200 px-4 py-3 flex items-center justify-between">
                                <div className="flex gap-1.5">
                                    <div className="w-3 h-3 rounded-full bg-red-400"></div>
                                    <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                                    <div className="w-3 h-3 rounded-full bg-green-400"></div>
                                </div>
                                <div className="bg-white border border-neutral-200 rounded-md px-6 py-0.5 text-[10px] text-neutral-400 font-inter">
                                    app.vocaply.ai/meeting/q3-review
                                </div>
                                <div className="w-10"></div>
                            </div>

                            {/* Dashboard Image / Visual */}
                            <div className="aspect-[16/10] relative bg-white overflow-hidden">
                                {/* Placeholder for the dashboard - in production we'd use the actual Image component */}
                                <div className="absolute inset-0 bg-neutral-100 flex items-center justify-center">
                                    <div className="text-neutral-300 flex flex-col items-center gap-4">
                                        <Zap size={48} className="animate-pulse" />
                                        <p className="font-outfit font-semibold text-xl">Loading Experience...</p>
                                    </div>
                                </div>

                                <img
                                    src="/images/dashboard-demo.png"
                                    alt="Vocaply Dashboard"
                                    className="absolute inset-0 w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
                                />

                                {/* Play Overlay */}
                                <div className="absolute inset-0 bg-neutral-900/10 group-hover:bg-neutral-900/0 transition-all flex items-center justify-center z-20">
                                    <motion.button
                                        whileHover={{ scale: 1.1 }}
                                        whileTap={{ scale: 0.95 }}
                                        className="w-20 h-20 rounded-full bg-white text-primary-500 flex items-center justify-center shadow-2xl backdrop-blur-sm bg-white/90"
                                    >
                                        <Play fill="currentColor" size={32} className="ml-1" />
                                    </motion.button>
                                </div>

                                {/* Floating AI Badge */}
                                <motion.div
                                    animate={{ y: [0, -10, 0] }}
                                    transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                                    className="absolute top-10 right-10 bg-white/90 backdrop-blur-md p-4 rounded-xl shadow-xl border border-primary-100 z-30 hidden md:block"
                                >
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-full bg-success/10 flex items-center justify-center text-success">
                                            <CheckCircle2 size={24} />
                                        </div>
                                        <div>
                                            <p className="text-[10px] font-bold text-neutral-400 uppercase tracking-widest leading-tight">AI Status</p>
                                            <p className="text-sm font-bold text-neutral-900 leading-tight">3 Action Items Found</p>
                                        </div>
                                    </div>
                                </motion.div>
                            </div>
                        </div>

                        {/* Corner Accents */}
                        <div className="absolute -bottom-6 -left-6 w-32 h-32 bg-secondary-500/10 rounded-full -z-10 blur-2xl"></div>
                        <div className="absolute -top-6 -right-6 w-32 h-32 bg-primary-500/10 rounded-full -z-10 blur-2xl"></div>
                    </motion.div>

                    {/* Right: Feature Highlights */}
                    <div className="lg:col-span-4 flex flex-col gap-6">
                        {features.map((f, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: 30 }}
                                whileInView={{ opacity: 1, x: 0 }}
                                viewport={{ once: true }}
                                transition={{ delay: 0.2 + (i * 0.1) }}
                                className="p-6 rounded-2xl bg-neutral-50 border border-neutral-100 hover:border-primary-200 transition-all group/card"
                            >
                                <div className="w-12 h-12 rounded-xl bg-white shadow-sm flex items-center justify-center mb-4 group-hover/card:scale-110 transition-transform">
                                    {f.icon}
                                </div>
                                <h4 className="text-lg font-bold text-neutral-900 mb-2 font-outfit">{f.title}</h4>
                                <p className="text-neutral-500 text-sm font-inter leading-relaxed">{f.desc}</p>
                            </motion.div>
                        ))}

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.6 }}
                            className="mt-4"
                        >
                            <button className="w-full btn-primary-enhanced h-14 rounded-2xl flex items-center justify-center gap-2 font-bold group">
                                Learn How It Works
                                <Zap size={18} className="group-hover:rotate-12 transition-transform" />
                            </button>
                        </motion.div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Demo;
