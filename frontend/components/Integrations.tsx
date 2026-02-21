"use client";

import React from "react";
import { motion } from "framer-motion";
import Image from "next/image";

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
        <section id="integrations" className="py-24 bg-gray-50 overflow-hidden">
            <div className="max-w-7xl mx-auto px-6">
                <div className="flex flex-col lg:flex-row items-center gap-16">
                    <div className="flex-1 text-center lg:text-left">
                        <h2 className="text-primary font-bold tracking-wider uppercase text-sm mb-4">Ecosystem</h2>
                        <h3 className="text-4xl md:text-5xl font-outfit font-bold text-gray-900 mb-6">
                            Works with the tools <br />
                            <span className="text-primary">You already love.</span>
                        </h3>
                        <p className="text-lg text-gray-600 mb-8 max-w-xl mx-auto lg:mx-0 font-inter">
                            Sync action items and meeting insights directly to your workspace. No more manual data entry.
                        </p>
                        <div className="flex flex-wrap justify-center lg:justify-start gap-4">
                            {/* Integration Icons Grid */}
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-6 sm:gap-8 mx-auto lg:mx-0">
                                {integrations.map((item) => (
                                    <motion.div
                                        key={item.name}
                                        whileHover={{ y: -5, scale: 1.05 }}
                                        className="w-20 h-20 sm:w-24 sm:h-24 bg-white rounded-2xl shadow-sm border border-gray-100 flex items-center justify-center cursor-pointer transition-all hover:shadow-md"
                                    >
                                        <div className="relative w-10 h-10 sm:w-12 sm:h-12">
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
                    </div>

                    <div className="flex-1 relative">
                        {/* Visual representation of connectivity */}
                        <div className="relative w-full aspect-square max-w-md mx-auto">
                            <div className="absolute inset-0 border-2 border-dashed border-primary/20 rounded-full animate-[spin_20s_linear_infinite]"></div>
                            <div className="absolute inset-8 border-2 border-dashed border-secondary/20 rounded-full animate-[spin_15s_linear_infinite_reverse]"></div>

                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="w-24 h-24 bg-primary rounded-3xl shadow-primary flex items-center justify-center text-white relative z-10">
                                    <span className="text-4xl font-bold">V</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};

export default Integrations;
