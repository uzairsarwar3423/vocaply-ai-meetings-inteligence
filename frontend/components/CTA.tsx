"use client";

import React from "react";
import { Button } from "./ui/button";
import { motion } from "framer-motion";
import { Sparkles, ArrowRight } from "lucide-react";

const CTA = () => {
    return (
        <section className="relative py-24 md:py-32 overflow-hidden bg-neutral-900 w-full">
            {/* Background Effects */}
            <div className="absolute top-0 left-0 w-full h-full">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-4xl h-[500px] bg-primary-500/20 blur-[120px] rounded-full"></div>
                <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-secondary-500/10 blur-[100px] rounded-full"></div>
                <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/carbon-fibre.png')] opacity-[0.03]"></div>
            </div>

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                <div className="flex flex-col items-center text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-primary-300 text-sm font-medium mb-8"
                    >
                        <Sparkles size={16} />
                        <span>Ready to elevate your meetings?</span>
                    </motion.div>

                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.1 }}
                        className="text-4xl md:text-7xl font-outfit font-bold text-white mb-8 tracking-tight leading-[1.1]"
                    >
                        Turn your talk <br />
                        into <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-secondary-400">decisive action.</span>
                    </motion.h2>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="text-lg md:text-xl text-neutral-400 max-w-2xl mx-auto mb-12 font-inter leading-relaxed"
                    >
                        Stop losing momentum after the call ends. Join 500+ high-performance teams using Vocaply to automate accountability.
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                        className="flex flex-col sm:flex-row items-center gap-4"
                    >
                        <button className="btn-primary-enhanced h-14 px-10 rounded-full text-lg font-bold flex items-center gap-2 group transition-all">
                            Get Started for Free
                            <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                        </button>
                        <button className="h-14 px-10 rounded-full text-lg font-medium text-white bg-white/5 border border-white/10 hover:bg-white/10 transition-all">
                            Book a Live Demo
                        </button>
                    </motion.div>

                    <motion.p
                        initial={{ opacity: 0 }}
                        whileInView={{ opacity: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6, delay: 0.5 }}
                        className="mt-8 text-neutral-500 text-sm font-inter"
                    >
                        No credit card required. Free 14-day trial included.
                    </motion.p>
                </div>
            </div>

            {/* Bottom Glow */}
            <div className="absolute bottom-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-primary-500/50 to-transparent"></div>
        </section>
    );
};

export default CTA;
