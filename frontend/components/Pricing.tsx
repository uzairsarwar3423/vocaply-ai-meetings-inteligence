"use client";

import React from "react";
import { Button } from "./ui/button";
import { Check } from "lucide-react";

const tiers = [
    {
        name: "Starter",
        price: "$0",
        description: "Perfect for individuals and solo developers.",
        features: [
            "5 meetings per month",
            "Basic AI extraction",
            "Email summaries",
            "7-day history",
        ],
        cta: "Start for Free",
        popular: false,
    },
    {
        name: "Pro",
        price: "$29",
        description: "Ideal for fast-growing remote teams.",
        features: [
            "Unlimited meetings",
            "Advanced task ownership",
            "Slack & Jira integrations",
            "Unlimited history",
            "Priority AI processing",
        ],
        cta: "Join Pro Trial",
        popular: true,
    },
    {
        name: "Enterprise",
        price: "Custom",
        description: "Security and scale for large organizations.",
        features: [
            "SSO & SAML",
            "Dedicated account manager",
            "Custom AI model tuning",
            "On-premise deployment",
            "White-glove onboarding",
        ],
        cta: "Contact Sales",
        popular: false,
    },
];

const Pricing = () => {
    return (
        <section id="pricing" className="py-24 bg-white">
            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center max-w-3xl mx-auto mb-20">
                    <h2 className="text-primary font-bold tracking-wider uppercase text-sm mb-4">Pricing</h2>
                    <h3 className="text-4xl md:text-5xl font-outfit font-bold text-gray-900 mb-6">
                        Simple Plans for <br />
                        <span className="text-primary">Effective Teams.</span>
                    </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {tiers.map((tier) => (
                        <div
                            key={tier.name}
                            className={`relative p-10 rounded-[2.5rem] border ${tier.popular
                                    ? "border-primary shadow-xl bg-white scale-105 z-10"
                                    : "border-gray-100 bg-gray-50/50"
                                }`}
                        >
                            {tier.popular && (
                                <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-primary text-white px-4 py-1 rounded-full text-sm font-bold uppercase tracking-widest">
                                    Most Popular
                                </div>
                            )}
                            <div className="mb-8">
                                <h4 className="text-2xl font-outfit font-bold text-gray-900 mb-2">{tier.name}</h4>
                                <div className="flex items-baseline gap-1 mb-4">
                                    <span className="text-4xl font-bold font-outfit text-gray-900">{tier.price}</span>
                                    {tier.price !== "Custom" && <span className="text-gray-500">/mo</span>}
                                </div>
                                <p className="text-gray-600 line-clamp-2">{tier.description}</p>
                            </div>

                            <ul className="space-y-4 mb-10 text-gray-600">
                                {tier.features.map((feature) => (
                                    <li key={feature} className="flex items-center gap-3">
                                        <Check size={20} className="text-primary shrink-0" />
                                        <span>{feature}</span>
                                    </li>
                                ))}
                            </ul>

                            <Button
                                variant={tier.popular ? "primary" : "outline"}
                                className="w-full h-14"
                            >
                                {tier.cta}
                            </Button>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default Pricing;
