"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import {
    Users,
    BarChart3,
    Clock,
    Zap,
    CheckCircle2,
    ArrowRight,
    TrendingUp,
    Target,
    MessageSquare,
    Workflow,
    Users2,
    HeartHandshake,
    Shield,
    Bot,
} from "lucide-react";

interface Solution {
    id: string;
    title: string;
    subtitle: string;
    icon: React.ReactNode;
    description: string;
    benefits: string[];
    color: string;
    bgColor: string;
    features: string[];
}

const solutions: Solution[] = [
    {
        id: "sales",
        title: "Sales Teams",
        subtitle: "Accelerate Deal Closure",
        icon: <TrendingUp size={32} />,
        description:
            "Transform every client conversation into trackable action items and next steps. Automatically log outcomes to your CRM.",
        benefits: [
            "Auto-log calls to Salesforce/HubSpot",
            "Extract deal requirements and objections",
            "Never miss follow-up opportunities",
            "Track commitment patterns with clients",
        ],
        color: "text-primary",
        bgColor: "bg-primary/10",
        features: [
            "Automatic CRM sync",
            "Deal health tracking",
            "Follow-up reminders",
            "Call outcome summaries",
        ],
    },
    {
        id: "engineering",
        title: "Engineering Teams",
        subtitle: "Streamline Development",
        icon: <Workflow size={32} />,
        description:
            "Capture technical decisions and automatically create tickets in your preferred project management tool.",
        benefits: [
            "Auto-create Jira/Linear tickets",
            "Track technical debt discussions",
            "Preserve architecture decisions",
            "Speed up sprint planning",
        ],
        color: "text-secondary",
        bgColor: "bg-secondary/10",
        features: [
            "Ticket automation",
            "Tech debt tracking",
            "Decision logging",
            "Sprint readiness",
        ],
    },
    {
        id: "product",
        title: "Product Management",
        subtitle: "Feature Clarity",
        icon: <Target size={32} />,
        description:
            "Never miss feature requests or user feedback. Organize requirements and maintain a single source of truth for product decisions.",
        benefits: [
            "Capture user feedback instantly",
            "Organize feature requests",
            "Track product decisions",
            "Keep stakeholders aligned",
        ],
        color: "text-blue-500",
        bgColor: "bg-blue-500/10",
        features: [
            "Requirement extraction",
            "Feedback organization",
            "Stakeholder alignment",
            "Product roadmap sync",
        ],
    },
    {
        id: "leadership",
        title: "Leadership & Executives",
        subtitle: "Enterprise Visibility",
        icon: <Users2 size={32} />,
        description:
            "Get a bird's-eye view of all organizational commitments, OKRs, and strategic initiatives in one unified dashboard.",
        benefits: [
            "Organization-wide commitment tracking",
            "OKR progress monitoring",
            "Executive dashboards",
            "Strategic alignment reporting",
        ],
        color: "text-emerald-500",
        bgColor: "bg-emerald-500/10",
        features: [
            "Executive dashboards",
            "OKR tracking",
            "Team performance insights",
            "Strategic reporting",
        ],
    },
    {
        id: "hr",
        title: "HR & Recruiting",
        subtitle: "Talent Pipeline",
        icon: <Users size={32} />,
        description:
            "Transform candidate conversations into organized action items and keep recruiting workflows frictionless and data-driven.",
        benefits: [
            "Auto-log candidate feedback",
            "Track hiring decisions",
            "Schedule follow-ups instantly",
            "Standardize interview feedback",
        ],
        color: "text-pink-500",
        bgColor: "bg-pink-500/10",
        features: [
            "Interview feedback capture",
            "Hiring workflow automation",
            "Candidate tracking",
            "Team alignment",
        ],
    },
    {
        id: "customer-success",
        title: "Customer Success",
        subtitle: "Proactive Support",
        icon: <HeartHandshake size={32} />,
        description:
            "Ensure no customer concern goes unaddressed. Track commitments and automatically notify teams of critical follow-ups.",
        benefits: [
            "Instant action item capture",
            "Customer health tracking",
            "Proactive follow-ups",
            "Churn risk detection",
        ],
        color: "text-purple-500",
        bgColor: "bg-purple-500/10",
        features: [
            "Customer concern tracking",
            "Health monitoring",
            "Proactive alerts",
            "Resolution automation",
        ],
    },
];

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1,
            delayChildren: 0.2,
        },
    },
};

const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.5 },
    },
};

const Solutions = () => {
    const [selected, setSelected] = useState<string>("sales");
    const selectedSolution = solutions.find((s) => s.id === selected);

    return (
        <section className="relative py-32 overflow-hidden">
            {/* Background Elements */}
            <div className="absolute inset-0 bg-gradient-to-br from-neutral-50 via-white to-neutral-50" />
            <div className="absolute top-0 left-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
            <div className="absolute bottom-0 right-0 w-96 h-96 bg-secondary/5 rounded-full blur-3xl" />

            <div className="relative max-w-7xl mx-auto px-6">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="text-center max-w-3xl mx-auto mb-20"
                >
                    <div className="inline-block">
                        <span className="text-primary font-bold tracking-widest uppercase text-sm px-4 py-2 bg-primary/10 rounded-full">
                            Solutions for Every Team
                        </span>
                    </div>
                    <h2 className="text-5xl md:text-6xl font-bold mt-6 mb-6">
                        <span className="text-gray-900">Purpose-Built for </span>
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">
                            Your Role
                        </span>
                    </h2>
                    <p className="text-xl text-gray-600 leading-relaxed max-w-2xl mx-auto">
                        Whether you're in sales, engineering, product, or leadership, Vocaply adapts to your workflow and delivers
                        measurable results.
                    </p>
                </motion.div>

                {/* Solution Selector */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                    className="mb-16"
                >
                    <div className="flex flex-wrap justify-center gap-4">
                        {solutions.map((solution) => (
                            <motion.button
                                key={solution.id}
                                onClick={() => setSelected(solution.id)}
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className={`px-6 py-3 rounded-xl font-semibold transition-all duration-300 flex items-center gap-2 ${
                                    selected === solution.id
                                        ? "bg-gradient-to-r from-primary to-primary/80 text-white shadow-lg shadow-primary/30"
                                        : "bg-white text-gray-700 border border-gray-200 hover:border-primary/30 hover:shadow-md"
                                }`}
                            >
                                <span className="text-lg">{solution.icon}</span>
                                <span className="hidden sm:inline">{solution.title}</span>
                            </motion.button>
                        ))}
                    </div>
                </motion.div>

                {/* Main Content */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.5 }}
                    key={selected}
                    className="grid lg:grid-cols-2 gap-12 items-center"
                >
                    {/* Left Content */}
                    <motion.div
                        variants={containerVariants}
                        initial="hidden"
                        animate="visible"
                        className="space-y-8"
                    >
                        <div>
                            <motion.div variants={itemVariants} className="inline-block mb-4">
                                <div className={`w-16 h-16 rounded-2xl ${selectedSolution?.bgColor} flex items-center justify-center ${selectedSolution?.color}`}>
                                    {selectedSolution?.icon}
                                </div>
                            </motion.div>
                            <motion.h3 variants={itemVariants} className="text-4xl font-bold text-gray-900 mb-2">
                                {selectedSolution?.title}
                            </motion.h3>
                            <motion.p variants={itemVariants} className="text-xl text-gray-600">
                                {selectedSolution?.subtitle}
                            </motion.p>
                        </div>

                        <motion.p variants={itemVariants} className="text-lg text-gray-700 leading-relaxed">
                            {selectedSolution?.description}
                        </motion.p>

                        <motion.div variants={itemVariants} className="space-y-4">
                            <h4 className="text-lg font-bold text-gray-900">Key Benefits</h4>
                            <ul className="space-y-3">
                                {selectedSolution?.benefits.map((benefit, idx) => (
                                    <li key={idx} className="flex items-start gap-3">
                                        <CheckCircle2 size={24} className={selectedSolution?.color} />
                                        <span className="text-gray-700 pt-1">{benefit}</span>
                                    </li>
                                ))}
                            </ul>
                        </motion.div>

                        <motion.button
                            variants={itemVariants}
                            whileHover={{ scale: 1.05, x: 5 }}
                            whileTap={{ scale: 0.95 }}
                            className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-primary to-primary/80 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-primary/30 transition-all duration-300"
                        >
                            Learn More
                            <ArrowRight size={20} />
                        </motion.button>
                    </motion.div>

                    {/* Right Content */}
                    <motion.div
                        variants={containerVariants}
                        initial="hidden"
                        animate="visible"
                        className="space-y-4"
                    >
                        {/* Features Grid */}
                        <motion.div variants={itemVariants} className="space-y-4">
                            <h4 className="text-lg font-bold text-gray-900">Powerful Capabilities</h4>
                            <div className="grid grid-cols-2 gap-4">
                                {selectedSolution?.features.map((feature, idx) => (
                                    <div
                                        key={idx}
                                        className="p-4 bg-white border border-gray-100 rounded-xl hover:border-primary/20 hover:shadow-md transition-all duration-300"
                                    >
                                        <div className="flex items-center gap-2 mb-2">
                                            <CheckCircle2 size={18} className={selectedSolution?.color} />
                                            <span className="font-semibold text-gray-900">{feature}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </motion.div>

                        {/* Showcase Card */}
                        <motion.div
                            variants={itemVariants}
                            className={`p-8 rounded-2xl ${selectedSolution?.bgColor} border-2 border-gray-100 mt-8`}
                        >
                            <div className="flex items-center gap-3 mb-4">
                                <Zap size={24} className={selectedSolution?.color} />
                                <h4 className="font-bold text-gray-900">Quick Win</h4>
                            </div>
                            <p className="text-gray-700 leading-relaxed">
                                Start capturing action items today. Most teams see a 40% increase in commitment completion within the first week.
                            </p>
                        </motion.div>

                        {/* Stats */}
                        <motion.div variants={itemVariants} className="grid grid-cols-2 gap-4 mt-8">
                            <div className="p-4 bg-white rounded-xl border border-gray-100">
                                <div className="text-2xl font-bold text-primary mb-1">92%</div>
                                <p className="text-sm text-gray-600">Less Manual Work</p>
                            </div>
                            <div className="p-4 bg-white rounded-xl border border-gray-100">
                                <div className="text-2xl font-bold text-secondary mb-1">3x</div>
                                <p className="text-sm text-gray-600">Faster Execution</p>
                            </div>
                        </motion.div>
                    </motion.div>
                </motion.div>

                {/* Bottom CTA Section */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                    className="mt-24 p-8 md:p-12 bg-gradient-to-r from-gray-900 to-gray-800 rounded-3xl border border-gray-700"
                >
                    <div className="grid md:grid-cols-2 gap-8 items-center">
                        <div>
                            <h3 className="text-3xl font-bold text-white mb-4">
                                Ready to Transform Your Team?
                            </h3>
                            <p className="text-gray-300 text-lg leading-relaxed">
                                Get started with Vocaply today. Free for the first 30 days, no credit card required.
                            </p>
                        </div>
                        <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-end">
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-8 py-4 bg-gradient-to-r from-primary to-primary/80 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-primary/30 transition-all duration-300"
                            >
                                Get Started Free
                            </motion.button>
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-8 py-4 bg-white/10 text-white border border-white/20 rounded-xl font-semibold hover:bg-white/20 transition-all duration-300"
                            >
                                Schedule Demo
                            </motion.button>
                        </div>
                    </div>
                </motion.div>
            </div>
        </section>
    );
};

export default Solutions;
