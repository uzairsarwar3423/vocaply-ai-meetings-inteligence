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
        <section className="py-16 bg-white border-y border-neutral-100">
            <div className="max-w-7xl mx-auto px-6">
                <p className="text-center text-[15px] font-medium text-slate-500 mb-12 font-inter">
                    Join 4,000+ companies already growing
                </p>
                <div className="flex flex-wrap items-center justify-center gap-x-12 md:gap-x-16 gap-y-10">
                    {logos.map((logo, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 10 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            viewport={{ once: true }}
                            className="flex items-center gap-2 group transition-all duration-300"
                        >
                            <div className="relative w-8 h-8 flex items-center justify-center">
                                <Image
                                    src={logo.src}
                                    alt={logo.name}
                                    width={32}
                                    height={32}
                                    className="object-contain"
                                />
                            </div>
                            <span className="text-[20px] font-bold text-slate-900 font-outfit tracking-tight">
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
