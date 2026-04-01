"use client";

import React from "react";
import { motion } from "framer-motion";
import { Code, Briefcase, HeartHandshake, Rocket, Sparkles } from "lucide-react";

const cases = [
    {
        title: "Engineering Teams",
        desc: "Sync technical decisions and action items directly to Jira or Linear tickets.",
        icon: Code,
        color: "text-primary",
        bg: "bg-primary/10",
    },
    {
        title: "Product Managers",
        desc: "Never miss a feature request or feedback point discussed in stakeholder calls.",
        icon: Rocket,
        color: "text-secondary",
        bg: "bg-secondary/10",
    },
    {
        title: "Sales & CRM",
        desc: "Automatically update your CRM with the next steps after every discovery call.",
        icon: Briefcase,
        color: "text-blue-600",
        bg: "bg-blue-50",
    },
    {
        title: "Leadership",
        desc: "Get a bird's-eye view of all commitments made across the entire organization.",
        icon: HeartHandshake,
        color: "text-amber-600",
        bg: "bg-amber-50",
    },
];

const UseCases = () => {
    return (
        <section className="py-32 bg-neutral-50/50 relative overflow-hidden text-neutral-900">
            {/* Premium Background Decoration */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full bg-[radial-gradient(circle_at_center,rgba(0,172,172,0.03)_0%,transparent_70%)] pointer-events-none" />
            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-primary/3 rounded-full blur-[120px] -z-10" />

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                <div className="text-center max-w-3xl mx-auto mb-24">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-neutral-900/5 text-neutral-900 border border-neutral-900/10 mb-8"
                    >
                        <Sparkles size={14} />
                        <span className="text-[10px] font-black uppercase tracking-[0.2em]">Designed for Every Team</span>
                    </motion.div>

                    <motion.h3
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-5xl lg:text-6xl font-black font-outfit text-neutral-900 mb-8 tracking-tighter"
                    >
                        Tailored for your <br />
                        <span className="text-primary italic">Specific Workflows.</span>
                    </motion.h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
                    {cases.map((item, idx) => (
                        <motion.div
                            key={item.title}
                            initial={{ opacity: 0, scale: 0.9 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: idx * 0.1 }}
                            whileHover={{ y: -10 }}
                            className="p-10 rounded-[2.5rem] glass-card border-white/40 bg-white/40 hover:bg-white hover:shadow-2xl hover:shadow-primary/5 transition-all duration-500 cursor-default group"
                        >
                            <div className={`w-14 h-14 rounded-2xl ${item.bg} ${item.color} shadow-lg flex items-center justify-center mb-8 group-hover:rotate-12 transition-transform duration-500`}>
                                <item.icon size={26} strokeWidth={2.5} />
                            </div>
                            <h4 className="text-2xl font-black font-outfit text-neutral-900 mb-4 tracking-tight group-hover:text-primary transition-colors">{item.title}</h4>
                            <p className="text-neutral-500 font-medium leading-relaxed tracking-tight">{item.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default UseCases;
