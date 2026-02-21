"use client";

import React from "react";
import { motion } from "framer-motion";
import { Code, Briefcase, HeartHandshake, Rocket } from "lucide-react";

const cases = [
    {
        title: "Engineering Teams",
        desc: "Sync technical decisions and action items directly to Jira or Linear tickets.",
        icon: Code,
    },
    {
        title: "Product Managers",
        desc: "Never miss a feature request or feedback point discussed in stakeholder calls.",
        icon: Rocket,
    },
    {
        title: "Sales & CRM",
        desc: "Automatically update your CRM with the next steps after every discovery call.",
        icon: Briefcase,
    },
    {
        title: "Leadership",
        desc: "Get a bird's-eye view of all commitments made across the entire organization.",
        icon: HeartHandshake,
    },
];

const UseCases = () => {
    return (
        <section className="py-24 bg-white">
            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center max-w-3xl mx-auto mb-16">
                    <h2 className="text-primary font-bold tracking-wider uppercase text-sm mb-4">Use Cases</h2>
                    <h3 className="text-4xl font-outfit font-bold text-gray-900 mb-6">Designed for every team.</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {cases.map((item, idx) => (
                        <motion.div
                            key={item.title}
                            whileHover={{ y: -10 }}
                            className="p-8 rounded-3xl bg-gray-50 border border-gray-100 transition-all cursor-default"
                        >
                            <div className="w-12 h-12 rounded-2xl bg-white shadow-sm border border-gray-100 flex items-center justify-center text-primary mb-6">
                                <item.icon size={24} />
                            </div>
                            <h4 className="text-xl font-outfit font-bold text-gray-900 mb-2">{item.title}</h4>
                            <p className="text-gray-600 font-inter">{item.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default UseCases;
