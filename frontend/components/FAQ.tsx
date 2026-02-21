"use client";

import React, { useState } from "react";
import { Plus, Minus } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const faqs = [
    {
        question: "How does Vocaply join my meetings?",
        answer: "Vocaply connects to your Google or Outlook calendar. Once authorized, it looks for meeting invites with links (Zoom, Google Meet, Teams) and joins automatically as a silent participant.",
    },
    {
        question: "Is my meeting data secure?",
        answer: "Absolutely. We use enterprise-grade encryption for both data at rest and in transit. Your recordings and transcripts are private to your workspace and never used for model training without explicit consent.",
    },
    {
        question: "Can it distinguish between multiple speakers?",
        answer: "Yes, our advanced AI uses speaker diarization to correctly identify who said what, even in crowded meetings, ensuring action items are assigned to the right owner.",
    },
    {
        question: "What integrations do you support?",
        answer: "Currently, we support Slack for notifications, and Jira, Linear, and Asana for task management. We're constantly adding more—Notion and Trello are coming next month!",
    },
];

const FAQ = () => {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    return (
        <section id="faq" className="py-24 bg-gray-50/50">
            <div className="max-w-4xl mx-auto px-6">
                <div className="text-center mb-16">
                    <h2 className="text-primary font-bold tracking-wider uppercase text-sm mb-4">FAQ</h2>
                    <h3 className="text-4xl font-outfit font-bold text-gray-900 mb-4">Questions? We have answers.</h3>
                </div>

                <div className="space-y-4">
                    {faqs.map((faq, index) => (
                        <div
                            key={index}
                            className="bg-white rounded-2xl border border-gray-100 overflow-hidden"
                        >
                            <button
                                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                                className="w-full px-8 py-6 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                            >
                                <span className="text-lg font-semibold text-gray-900">{faq.question}</span>
                                {openIndex === index ? (
                                    <Minus className="text-primary shrink-0" size={20} />
                                ) : (
                                    <Plus className="text-primary shrink-0" size={20} />
                                )}
                            </button>
                            <AnimatePresence>
                                {openIndex === index && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: "auto", opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        transition={{ duration: 0.3 }}
                                    >
                                        <div className="px-8 pb-6 text-gray-600 leading-relaxed font-inter">
                                            {faq.answer}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default FAQ;
