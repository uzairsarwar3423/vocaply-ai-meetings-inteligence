"use client";

import React from "react";
import { motion } from "framer-motion";
import { Check, Zap, Shield, Star, Crown } from "lucide-react";
import { Button } from "./ui/button";

const tiers = [
    {
        name: "Starter",
        price: "$0",
        description: "Perfect for individuals and solo developers looking to optimize their workflow.",
        features: [
            "5 meetings per month",
            "Basic AI extraction",
            "Email summaries",
            "7-day history",
        ],
        cta: "Start for Free",
        popular: false,
        icon: <Zap size={20} className="text-primary" />,
    },
    {
        name: "Pro",
        price: "$29",
        description: "Ideal for fast-growing remote teams who need deep meeting intelligence.",
        features: [
            "Unlimited meetings",
            "Advanced task ownership",
            "Slack & Jira integrations",
            "Unlimited history",
            "Priority AI processing",
            "Custom metadata tags",
        ],
        cta: "Join Pro Trial",
        popular: true,
        icon: <Star size={20} className="text-secondary" />,
    },
    {
        name: "Enterprise",
        price: "Custom",
        description: "Security and scale for large organizations requiring bespoke solutions.",
        features: [
            "SSO & SAML",
            "Dedicated account manager",
            "Custom AI model tuning",
            "On-premise deployment",
            "White-glove onboarding",
            "24/7 Priority Support",
        ],
        cta: "Contact Sales",
        popular: false,
        icon: <Crown size={20} className="text-amber-500" />,
    },
];

const Pricing = () => {
    return (
        <section id="pricing" className="py-32 bg-neutral-50/50 relative overflow-hidden">
            {/* Premium Background Decoration */}
            <div className="absolute top-0 right-[-10%] w-[600px] h-[600px] bg-primary/5 rounded-full blur-[140px] -z-10" />
            <div className="absolute bottom-0 left-[-10%] w-[600px] h-[600px] bg-secondary/5 rounded-full blur-[140px] -z-10" />

            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center max-w-3xl mx-auto mb-24">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 text-primary border border-primary/20 mb-8"
                    >
                        <Shield size={14} />
                        <span className="text-[10px] font-black uppercase tracking-[0.2em]">Transparent Pricing</span>
                    </motion.div>

                    <motion.h3
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-5xl lg:text-6xl font-black font-outfit text-neutral-900 mb-8 tracking-tighter"
                    >
                        Simple Plans for <br />
                        <span className="text-primary">Effective Teams.</span>
                    </motion.h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
                    {tiers.map((tier, index) => (
                        <motion.div
                            key={tier.name}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            whileHover={{ y: -10 }}
                            className={`relative p-10 rounded-[3rem] border transition-all duration-500 glass-card ${tier.popular
                                ? "border-primary/40 bg-white/80 shadow-[0_40px_80px_rgba(0,172,172,0.15)] z-10 lg:-mt-6 lg:mb-6"
                                : "border-white/40 bg-white/40 shadow-sm"
                                }`}
                        >
                            {tier.popular && (
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-gradient-to-r from-primary to-teal-500 text-white px-6 py-1.5 rounded-full text-[10px] font-black uppercase tracking-[0.2em] shadow-xl shadow-primary/20">
                                    Most Popular Choice
                                </div>
                            )}

                            <div className="mb-10">
                                <div className="flex items-center justify-between mb-6">
                                    <div className="p-3 rounded-2xl bg-neutral-100/50 border border-neutral-100 shadow-inner">
                                        {tier.icon}
                                    </div>
                                    <span className="text-[10px] font-black uppercase tracking-widest text-neutral-400">{tier.name}</span>
                                </div>

                                <div className="flex items-baseline gap-1 mb-6">
                                    <span className="text-5xl font-black font-outfit text-neutral-900 tracking-tighter">{tier.price}</span>
                                    {tier.price !== "Custom" && <span className="text-neutral-400 font-bold ml-1">/month</span>}
                                </div>
                                <p className="text-neutral-500 font-medium leading-relaxed tracking-tight">{tier.description}</p>
                            </div>

                            <div className="h-px w-full bg-neutral-100 mb-10" />

                            <ul className="space-y-5 mb-12">
                                {tier.features.map((feature) => (
                                    <li key={feature} className="flex items-center gap-4 group/item">
                                        <div className="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover/item:scale-125 transition-transform">
                                            <Check size={12} strokeWidth={3} />
                                        </div>
                                        <span className="text-neutral-600 font-medium tracking-tight text-sm">{feature}</span>
                                    </li>
                                ))}
                            </ul>

                            <button className={`w-full h-16 rounded-[1.5rem] font-black uppercase tracking-widest text-[11px] transition-all duration-300 active:scale-95 ${tier.popular
                                ? "bg-primary text-white shadow-2xl shadow-primary/20 hover:bg-neutral-900"
                                : "bg-neutral-100 text-neutral-900 hover:bg-neutral-200 border border-neutral-200"
                                }`}>
                                {tier.cta}
                            </button>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Pricing;
