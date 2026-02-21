"use client";

import React from "react";
import { motion } from "framer-motion";
import { Target, Zap, BarChart3, Bell, Share2, Shield } from "lucide-react";

const features = [
    {
        title: "AI Action Item Extraction",
        description: "Automatically identify tasks, owners, and deadlines directly from your meeting transcriptions.",
        icon: Target,
        color: "bg-primary/10 text-primary",
    },
    {
        title: "Real-time Transcription",
        description: "Multi-language support with high accuracy for Zoom, Google Meet, and Microsoft Teams.",
        icon: Zap,
        color: "bg-secondary/10 text-secondary",
    },
    {
        title: "Commitment Tracking",
        description: "Monitor progress on every task assigned during meetings without manually checking in.",
        icon: BarChart3,
        color: "bg-blue-500/10 text-blue-500",
    },
    {
        title: "Smart Notifications",
        description: "Push reminders to Slack or Email when deadlines are approaching or things fall through the cracks.",
        icon: Bell,
        color: "bg-orange-500/10 text-orange-500",
    },
    {
        title: "Deep Integrations",
        description: "Sync your meeting action items directly with Jira, Linear, Asana, and Notion.",
        icon: Share2,
        color: "bg-purple-500/10 text-purple-500",
    },
    {
        title: "Enterprise Security",
        description: "SOC2 compliant, end-to-end encryption. Your meeting data is private and secure.",
        icon: Shield,
        color: "bg-emerald-500/10 text-emerald-500",
    },
];

const Features = () => {
    return (
        <section id="features" className="py-24 bg-white relative">
            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center max-w-3xl mx-auto mb-20">
                    <h2 className="text-primary font-bold tracking-wider uppercase text-sm mb-4">Powerful Features</h2>
                    <h3 className="text-4xl md:text-5xl font-outfit font-bold text-gray-900 mb-6">
                        Everything you need to turn <br />
                        <span className="text-primary">Talk into Results.</span>
                    </h3>
                    <p className="text-lg text-gray-600 font-inter">
                        Stop losing track of meeting outcomes. Vocaply provides a comprehensive suite of tools to ensure every commitment is captured and completed.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {features.map((feature, index) => (
                        <motion.div
                            key={feature.title}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            className="p-8 rounded-2xl border border-gray-100 bg-white hover:border-primary/20 hover:shadow-xl transition-all duration-300 group"
                        >
                            <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 ${feature.color}`}>
                                <feature.icon size={28} />
                            </div>
                            <h4 className="text-xl font-outfit font-bold text-gray-900 mb-3">{feature.title}</h4>
                            <p className="text-gray-600 leading-relaxed font-inter">
                                {feature.description}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Features;
