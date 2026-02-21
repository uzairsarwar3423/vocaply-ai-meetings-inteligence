"use client";

import React from "react";
import { Button } from "./ui/button";
import { motion } from "framer-motion";
import { Play, ArrowRight, Zap, Shield, Users } from "lucide-react";
import Image from "next/image";

const Hero = () => {
    return (
        <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
            {/* Background Decor */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10 pointer-events-none">
                <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-primary/5 rounded-full blur-3xl" />
                <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-secondary/5 rounded-full blur-3xl" />
            </div>

            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center max-w-4xl mx-auto">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-light text-primary font-semibold text-sm mb-8"
                    >
                        <Zap size={16} fill="currentColor" />
                        <span>Turn Meeting Talk into Real Action</span>
                    </motion.div>

                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.1 }}
                        className="text-5xl lg:text-7xl font-outfit font-bold text-gray-900 leading-[1.1] mb-8"
                    >
                        Your Meetings, <br />
                        <span className="text-transparent bg-clip-text bg-hero">Fully Automated.</span>
                    </motion.h1>

                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                        className="text-xl text-gray-600 mb-12 leading-relaxed max-w-2xl mx-auto font-inter"
                    >
                        Vocaply joins your calls, identifies commitments, assigns owners, and tracks completion. Stop wasting time on follow-ups—start making progress.
                    </motion.p>

                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.5, delay: 0.3 }}
                        className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
                    >
                        <Button size="lg" className="h-16 px-10 text-lg group">
                            Start Your Free Trial
                            <ArrowRight className="ml-2 group-hover:translate-x-1 transition-transform" />
                        </Button>
                        <Button variant="ghost" size="lg" className="h-16 px-10 text-lg gap-2">
                            <div className="w-10 h-10 rounded-full bg-white shadow-md flex items-center justify-center text-primary border border-gray-100">
                                <Play fill="currentColor" size={16} className="ml-1" />
                            </div>
                            Watch Demo
                        </Button>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, delay: 0.4 }}
                        className="relative mx-auto max-w-5xl group"
                    >
                        <div className="absolute -inset-1 bg-gradient-to-r from-primary via-secondary to-primary rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-1000 group-hover:duration-200 animate-gradient-xy"></div>
                        <div className="relative bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden aspect-video flex items-center justify-center">
                            <Image
                                src="/images/platform_dashboard_preview.png"
                                alt="Vocaply Meeting Intelligence Dashboard"
                                fill
                                className="object-cover"
                                priority
                                quality={100}
                            />
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
};

export default Hero;
