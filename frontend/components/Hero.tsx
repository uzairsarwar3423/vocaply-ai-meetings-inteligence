"use client";

import React from "react";
import { Button } from "./ui/button";
import { motion } from "framer-motion";
import { Play, ArrowRight, Zap, Stars, MousePointer2, Sparkles } from "lucide-react";
import Image from "next/image";

const Hero = () => {
    return (
        <section className="relative pt-32 pb-24 lg:pt-56 lg:pb-40 overflow-hidden bg-white">
            {/* Background Mesh Gradient Decor */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-[120%] -z-10 pointer-events-none opacity-40">
                <div className="absolute top-[-10%] right-[10%] w-[800px] h-[800px] bg-primary/20 rounded-full blur-[120px] mix-blend-multiply animate-pulse" />
                <div className="absolute bottom-[20%] left-[-5%] w-[600px] h-[600px] bg-secondary/20 rounded-full blur-[100px] mix-blend-multiply" />
                <div className="absolute top-[20%] left-[20%] w-[400px] h-[400px] bg-teal-200/20 rounded-full blur-[80px]" />
            </div>

            <div className="max-w-7xl mx-auto px-6 relative">
                {/* Floating Elements */}
                <motion.div
                    animate={{ y: [0, -15, 0] }}
                    transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute top-0 left-10 hidden xl:flex items-center gap-3 glass-card px-4 py-2 rounded-2xl border-white/40 shadow-xl"
                >
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary">
                        <Stars size={14} fill="currentColor" />
                    </div>
                    <span className="text-[10px] font-black uppercase tracking-widest text-neutral-500">AI Transcription</span>
                </motion.div>

                <motion.div
                    animate={{ y: [0, 15, 0] }}
                    transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 1 }}
                    className="absolute top-20 right-10 hidden xl:flex items-center gap-3 glass-card px-4 py-2 rounded-2xl border-white/40 shadow-xl"
                >
                    <div className="w-8 h-8 rounded-full bg-secondary/20 flex items-center justify-center text-secondary">
                        <MousePointer2 size={14} fill="currentColor" />
                    </div>
                    <span className="text-[10px] font-black uppercase tracking-widest text-neutral-500">Smart Tasks</span>
                </motion.div>

                <div className="text-center max-w-5xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="inline-flex items-center gap-2.5 px-5 py-2 rounded-full bg-primary/10 text-primary border border-primary/20 shadow-[0_0_20px_rgba(13,148,136,0.1)] mb-10"
                    >
                        <Zap size={14} className="fill-primary animate-pulse" />
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] py-0.5">Meet Your New AI Assistant</span>
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                        className="text-6xl lg:text-[6.5rem] font-black font-outfit text-neutral-900 leading-[0.9] mb-10 tracking-tighter"
                    >
                        Meetings, <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary via-teal-500 to-secondary relative">
                            Fully Automated
                            <div className="absolute -bottom-4 left-0 w-full h-2 bg-primary/20 rounded-full blur-xl" />
                        </span>
                    </motion.h1>

                    <motion.p
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 1, delay: 0.3 }}
                        className="text-xl text-neutral-500 mb-14 leading-[1.6] max-w-2xl mx-auto font-medium tracking-tight"
                    >
                        Vocaply captures conversation, extracts strategic commitments, and orchestrates completion. <span className="text-neutral-900 font-bold">Zero friction, pure velocity.</span>
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.5 }}
                        className="flex flex-col sm:flex-row items-center justify-center gap-6 mb-24"
                    >
                        <button className="h-20 px-12 bg-neutral-900 text-white font-black uppercase tracking-widest text-[11px] rounded-3xl shadow-2xl shadow-neutral-300 hover:bg-primary hover:shadow-primary/30 transition-all active:scale-95 group relative overflow-hidden">
                            <span className="relative z-10 flex items-center gap-3">
                                Initialize Free Access <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                            </span>
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                        </button>

                        <button className="h-20 px-12 glass-panel border-white/50 text-neutral-900 font-black uppercase tracking-widest text-[11px] rounded-3xl hover:bg-white hover:shadow-xl transition-all active:scale-95 flex items-center gap-4 group">
                            <div className="w-10 h-10 rounded-2xl bg-white shadow-lg flex items-center justify-center text-primary ring-1 ring-neutral-100 group-hover:scale-110 transition-transform">
                                <Play fill="currentColor" size={12} className="ml-0.5" />
                            </div>
                            Playback Showcase
                        </button>
                    </motion.div>

                    {/* App Preview Container */}
                    <motion.div
                        initial={{ opacity: 0, y: 60 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 1, delay: 0.7, ease: "circOut" }}
                        className="relative mx-auto max-w-6xl group p-4 bg-white/50 backdrop-blur-2xl rounded-[3rem] border border-white/40 shadow-3xl perspective-2000"
                    >
                        <div className="absolute -inset-2 bg-gradient-to-tr from-primary/30 to-secondary/30 rounded-[3.5rem] blur-2xl opacity-0 group-hover:opacity-100 transition duration-1000" />

                        <div className="relative bg-neutral-50 rounded-[2rem] shadow-inner border border-white/50 overflow-hidden aspect-[16/9] flex items-center justify-center group-hover:scale-[1.01] transition-transform duration-700">
                            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/5 to-black/20 z-10 pointer-events-none" />
                            <Image
                                src="/images/platform_dashboard_preview.png"
                                alt="Vocaply Meeting Intelligence Dashboard"
                                fill
                                className="object-cover group-hover:scale-105 transition-transform duration-1000"
                                priority
                                quality={100}
                            />

                            {/* Overlay UI elements for "WOW" effect */}
                            <div className="absolute bottom-8 left-8 right-8 z-20 flex justify-between items-end opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                                <div className="glass-card px-6 py-4 rounded-2xl border-white/20 shadow-2xl">
                                    <p className="text-[10px] font-black text-primary uppercase tracking-widest transition-all">Extracting Context...</p>
                                    <div className="h-1 w-32 bg-primary/20 rounded-full mt-2 overflow-hidden">
                                        <motion.div
                                            animate={{ x: [-128, 128] }}
                                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                                            className="h-full w-full bg-primary"
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
};

export default Hero;
