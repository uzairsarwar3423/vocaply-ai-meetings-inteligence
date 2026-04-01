"use client";

import React from "react";
import { Button } from "./ui/button";
import { motion } from "framer-motion";
import { Sparkles, ArrowRight, Zap } from "lucide-react";

const CTA = () => {
    return (
        <section className="relative py-40 md:py-60 overflow-hidden w-full flex items-center justify-center bg-[#001A1A]">
            {/* Ultra-Premium Mesh Gradient Background */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <motion.div
                    animate={{
                        scale: [1, 1.2, 1],
                        rotate: [0, 45, 0],
                        x: [0, 100, 0],
                        y: [0, -50, 0]
                    }}
                    transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                    className="absolute top-[-20%] left-[-10%] w-[1000px] h-[1000px] bg-primary/20 rounded-full blur-[160px]"
                />
                <motion.div
                    animate={{
                        scale: [1, 1.3, 1],
                        rotate: [0, -30, 0],
                        x: [0, -150, 0],
                        y: [0, 100, 0]
                    }}
                    transition={{ duration: 18, repeat: Infinity, ease: "linear", delay: 2 }}
                    className="absolute bottom-[-30%] right-[-10%] w-[1000px] h-[1000px] bg-secondary/20 rounded-full blur-[180px]"
                />
                <motion.div
                    animate={{
                        opacity: [0.2, 0.4, 0.2],
                        scale: [1, 1.1, 1]
                    }}
                    transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
                    className="absolute top-[30%] right-[10%] w-[600px] h-[600px] bg-teal-400/10 rounded-full blur-[140px]"
                />

                {/* Dynamic Noise/Texture */}
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-30 mix-blend-overlay" />
            </div>

            <div className="max-w-7xl mx-auto px-6 relative z-10 w-full">
                <motion.div
                    initial={{ opacity: 0, y: 40 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
                    className="glass-panel p-20 md:p-32 rounded-[5rem] border-white/10 bg-white/5 backdrop-blur-[60px] text-center relative overflow-hidden shadow-[0_40px_100px_rgba(0,0,0,0.5)]"
                >
                    {/* Floating Glow Elements */}
                    <div className="absolute -top-20 -left-20 w-80 h-80 bg-primary/20 rounded-full blur-[100px] animate-pulse" />
                    <div className="absolute -bottom-20 -right-20 w-80 h-80 bg-secondary/15 rounded-full blur-[100px] animate-pulse" />

                    <div className="relative z-10">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.8 }}
                            className="inline-flex items-center gap-3 px-8 py-3 rounded-full bg-white/5 border border-white/10 text-primary uppercase text-[11px] font-black tracking-[0.4em] mb-14 hover:border-primary/50 transition-colors cursor-default"
                        >
                            <Sparkles size={18} className="animate-spin-slow" />
                            <span>Transformation Awaits</span>
                        </motion.div>

                        <motion.h2
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.8, delay: 0.1 }}
                            className="text-6xl md:text-9xl font-black font-outfit text-white mb-12 tracking-tighter leading-[0.85] drop-shadow-2xl"
                        >
                            Turn talk <br />
                            <span className="text-secondary italic">into decisions.</span>
                        </motion.h2>

                        <motion.p
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.8, delay: 0.2 }}
                            className="text-2xl md:text-3xl text-neutral-300 max-w-3xl mx-auto mb-20 font-medium tracking-tight leading-relaxed opacity-90"
                        >
                            Stop losing momentum after the call ends. Join 500+ high-performance teams using Vocaply to automate accountability.
                        </motion.p>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.8, delay: 0.3 }}
                            className="flex flex-col sm:flex-row items-center justify-center gap-8"
                        >
                            <button className="h-24 px-16 bg-primary text-white text-[12px] font-black uppercase tracking-[0.3em] rounded-[2.5rem] shadow-[0_25px_50px_-12px_rgba(0,172,172,0.5)] hover:bg-white hover:text-neutral-950 transition-all duration-500 active:scale-95 group relative overflow-hidden">
                                <span className="relative z-10 flex items-center gap-4">
                                    Start for Free Today <ArrowRight size={24} className="group-hover:translate-x-2 transition-transform h-6 w-6" />
                                </span>
                                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-500" />
                            </button>

                            <button className="h-24 px-16 bg-white/5 border-2 border-white/10 text-white text-[12px] font-black uppercase tracking-[0.3em] rounded-[2.5rem] hover:bg-white/10 hover:border-white/20 transition-all duration-500 flex items-center gap-4 backdrop-blur-md">
                                Book a Live Demo <Zap size={22} className="text-secondary fill-secondary" />
                            </button>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0 }}
                            whileInView={{ opacity: 1 }}
                            viewport={{ once: true }}
                            transition={{ duration: 1, delay: 0.6 }}
                            className="mt-16 flex flex-col items-center gap-6"
                        >
                            <p className="text-neutral-500 text-[11px] font-black uppercase tracking-[0.3em]">
                                No credit card required • Unlimited Trial • SOC2 Certified
                            </p>

                            {/* Trust badges placeholder */}
                            <div className="flex gap-8 opacity-30 grayscale hover:grayscale-0 transition-all duration-500">
                                <div className="h-6 w-24 bg-white/20 rounded" />
                                <div className="h-6 w-24 bg-white/20 rounded" />
                                <div className="h-6 w-24 bg-white/20 rounded" />
                            </div>
                        </motion.div>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};

export default CTA;
