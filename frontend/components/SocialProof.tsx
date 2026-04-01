"use client";

import React from "react";
import Image from "next/image";
import { motion } from "framer-motion";

const SocialProof = () => {
    const logos = [
        { name: "Asana", src: "/icons/asana.svg" },
        { name: "Slack", src: "/icons/icons8-slack-24.png" },
        { name: "Jira", src: "/icons/jira.png" },
        { name: "Linear", src: "/icons/linear.svg" },
        { name: "Google Calendar", src: "/icons/google-calendar.svg" },
        { name: "Notion", src: "/icons/notion.svg" },
    ];

    return (
        <section className="py-20 bg-neutral-50/50 border-y border-neutral-100 relative overflow-hidden">
            {/* Subtle light effect */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-[radial-gradient(circle_at_center,rgba(0,172,172,0.03)_0%,transparent_70%)] pointer-events-none" />

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="flex flex-col items-center mb-16"
                >
                    <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-neutral-200 shadow-sm mb-4">
                        <div className="flex -space-x-2">
                            {[1, 2, 3].map(i => (
                                <div key={i} className="w-5 h-5 rounded-full border-2 border-white bg-neutral-200" />
                            ))}
                        </div>
                        <span className="text-[10px] font-black uppercase tracking-widest text-neutral-500">Trusted by over 4,000 teams</span>
                    </div>
                </motion.div>

                <div className="flex flex-wrap items-center justify-center gap-x-12 md:gap-x-24 gap-y-12 opacity-60 hover:opacity-100 transition-opacity duration-700">
                    {logos.map((logo, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.8, delay: index * 0.1, ease: "easeOut" }}
                            viewport={{ once: true }}
                            whileHover={{ scale: 1.1, opacity: 1 }}
                            className="flex items-center gap-3 group grayscale hover:grayscale-0 transition-all duration-500 cursor-pointer"
                        >
                            <div className="relative w-7 h-7 flex items-center justify-center transform group-hover:rotate-6 transition-transform">
                                <Image
                                    src={logo.src}
                                    alt={logo.name}
                                    width={28}
                                    height={28}
                                    className="object-contain"
                                />
                            </div>
                            <span className="text-xl font-black text-neutral-900 font-outfit tracking-tighter opacity-80 group-hover:opacity-100 transition-opacity">
                                {logo.name}
                            </span>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default SocialProof;
