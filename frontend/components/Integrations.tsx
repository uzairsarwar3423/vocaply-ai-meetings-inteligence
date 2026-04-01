"use client";

import React from "react";
import { motion } from "framer-motion";
import Image from "next/image";
import { Cpu, Zap, Share2 } from "lucide-react";

const integrations = [
    { name: "Slack", src: "/icons/icons8-slack-24.png" },
    { name: "Jira", src: "/icons/jira.png" },
    { name: "Linear", src: "/icons/linear.svg" },
    { name: "Asana", src: "/icons/asana.svg" },
    { name: "Google Calendar", src: "/icons/google-calendar.svg" },
    { name: "Notion", src: "/icons/notion.svg" },
];

const Integrations = () => {
    return (
        <section id="integrations" className="py-32 bg-neutral-50/50 relative overflow-hidden">
            {/* Decoration */}
            <div className="absolute top-[20%] right-[-10%] w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px] -z-10" />

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                <div className="flex flex-col lg:flex-row items-center gap-24 lg:gap-32">
                    <div className="flex-1 text-center lg:text-left">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 text-primary border border-primary/20 mb-8"
                        >
                            <Share2 size={14} />
                            <span className="text-[10px] font-black uppercase tracking-[0.2em]">Universal Ecosystem</span>
                        </motion.div>

                        <motion.h3
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.1 }}
                            className="text-5xl lg:text-6xl font-black font-outfit text-neutral-900 mb-8 tracking-tighter"
                        >
                            Works with the tools <br />
                            <span className="text-primary italic">You already love.</span>
                        </motion.h3>

                        <motion.p
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.2 }}
                            className="text-xl text-neutral-500 font-medium tracking-tight leading-relaxed mb-12 max-w-xl mx-auto lg:mx-0"
                        >
                            Sync action items and meeting insights directly to your workspace. Eliminate manual data entry and keep your team in sync.
                        </motion.p>

                        <div className="grid grid-cols-3 gap-4 mx-auto lg:mx-0 max-w-sm">
                            {integrations.map((item, index) => (
                                <motion.div
                                    key={item.name}
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    whileInView={{ opacity: 1, scale: 1 }}
                                    viewport={{ once: true }}
                                    transition={{ duration: 0.5, delay: 0.3 + index * 0.05 }}
                                    whileHover={{ y: -5, scale: 1.05 }}
                                    className="aspect-square bg-white rounded-2xl shadow-sm border border-neutral-100 flex items-center justify-center cursor-pointer group transition-all"
                                >
                                    <div className="relative w-10 h-10 transform group-hover:rotate-12 transition-transform">
                                        <Image
                                            src={item.src}
                                            alt={item.name}
                                            fill
                                            className="object-contain"
                                        />
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </div>

                    <div className="flex-1 w-full relative">
                        {/* Visual representation of connectivity */}
                        <div className="relative w-full aspect-square max-w-lg mx-auto flex items-center justify-center">
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 50, repeat: Infinity, ease: "linear" }}
                                className="absolute inset-0 border-[3px] border-dashed border-primary/10 rounded-full"
                            />
                            <motion.div
                                animate={{ rotate: -360 }}
                                transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
                                className="absolute inset-16 border-[2px] border-dashed border-secondary/10 rounded-full"
                            />
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
                                className="absolute inset-32 border-[1px] border-dashed border-neutral-200 rounded-full"
                            />

                            <motion.div
                                whileHover={{ scale: 1.05 }}
                                className="w-32 h-32 bg-primary rounded-[2.5rem] shadow-[0_30px_60px_rgba(0,172,172,0.3)] flex items-center justify-center text-white relative z-10 border-4 border-white overflow-hidden group shadow-primary"
                            >
                                <div className="absolute inset-0 bg-gradient-to-tr from-black/20 to-transparent" />
                                <span className="text-5xl font-black relative z-10 group-hover:scale-110 transition-transform">V</span>

                                <motion.div
                                    animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.6, 0.3] }}
                                    transition={{ duration: 3, repeat: Infinity }}
                                    className="absolute inset-0 bg-white blur-xl -z-10"
                                />
                            </motion.div>

                            {/* Floating integration badges */}
                            <motion.div
                                animate={{ y: [0, -15, 0] }}
                                transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
                                className="absolute top-10 left-10 glass-panel p-4 rounded-2xl shadow-xl z-20 border-white/40"
                            >
                                <Zap className="text-primary" size={20} />
                            </motion.div>

                            <motion.div
                                animate={{ y: [0, 15, 0] }}
                                transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
                                className="absolute bottom-10 right-10 glass-panel p-4 rounded-2xl shadow-xl z-20 border-white/40"
                            >
                                <Cpu className="text-secondary" size={20} />
                            </motion.div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Integrations;
