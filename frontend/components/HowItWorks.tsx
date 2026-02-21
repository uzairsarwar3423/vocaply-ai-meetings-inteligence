"use client";

import React from "react";
import { motion } from "framer-motion";
import { Video, Sparkles, CheckCircle2 } from "lucide-react";


const steps = [
    {
        title: "Connect Your Calendar",
        description: "Vocaply automatically syncs with your Google or Outlook calendar to join scheduled meetings.",
        icon: Video,
        image: "/images/how_it_works_calendar.png",
    },
    {
        title: "Meeting Magic Happens",
        description: "Our AI attends the call, transcribes everything, and identifies action items in real-time.",
        icon: Sparkles,
        image: "/images/how_it_works_transcription.png",
    },
    {
        title: "Action Items Sync",
        description: "Tasks are automatically assigned to owners and synced with your favorite project tools.",
        icon: CheckCircle2,
        image: "/images/how_it_works_action_items.png",
    },
];

const HowItWorks = () => {
    return (
        <section id="how-it-works" className="py-24 bg-gray-50/50">
            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center max-w-3xl mx-auto mb-20">
                    <h2 className="text-secondary font-bold tracking-wider uppercase text-sm mb-4">The Process</h2>
                    <h3 className="text-4xl md:text-5xl font-outfit font-bold text-gray-900 mb-6">
                        Three Steps to <br />
                        <span className="text-secondary">Meeting Excellence.</span>
                    </h3>
                </div>

                <div className="space-y-24">
                    {steps.map((step, index) => (
                        <motion.div
                            key={step.title}
                            initial={{ opacity: 0, x: index % 2 === 0 ? -40 : 40 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.8 }}
                            className={`flex flex-col ${index % 2 === 0 ? "lg:flex-row" : "lg:flex-row-reverse"} items-center gap-16`}
                        >
                            <div className="flex-1">
                                <div className="w-16 h-16 rounded-full bg-white shadow-lg flex items-center justify-center text-secondary mb-8 border border-secondary/10">
                                    <step.icon size={32} />
                                </div>
                                <h4 className="text-3xl font-outfit font-bold text-gray-900 mb-4">
                                    <span className="text-secondary/30 mr-4">0{index + 1}.</span>
                                    {step.title}
                                </h4>
                                <p className="text-xl text-gray-600 leading-relaxed font-inter">
                                    {step.description}
                                </p>
                            </div>
                            <div className="flex-1 w-full relative">
                                <div className="absolute -inset-4 bg-secondary/5 rounded-3xl blur-2xl -z-10"></div>
                                <div className="bg-white rounded-3xl shadow-xl border border-gray-100 aspect-[4/3] flex items-center justify-center overflow-hidden relative">
                                    <img
                                        src={step.image}
                                        alt={step.title}
                                        className="w-full h-full object-contain transition-transform duration-500 hover:scale-105"
                                    />
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default HowItWorks;
