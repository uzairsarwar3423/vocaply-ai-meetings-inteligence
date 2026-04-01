"use client";

import React, { useState } from "react";
import { Plus, Minus, HelpCircle } from "lucide-react";
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
        <section id="faq" className="py-32 bg-neutral-50/50 relative overflow-hidden">
            {/* Decoration */}
            <div className="absolute top-1/2 left-[-10%] w-[400px] h-[400px] bg-primary/5 rounded-full blur-[100px] -z-10" />

            <div className="max-w-4xl mx-auto px-6 relative z-10">
                <div className="text-center mb-24">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-neutral-900/5 text-neutral-900 border border-neutral-900/10 mb-8"
                    >
                        <HelpCircle size={14} />
                        <span className="text-[10px] font-black uppercase tracking-[0.2em]">Got Questions?</span>
                    </motion.div>

                    <motion.h3
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.1 }}
                        className="text-5xl font-black font-outfit text-neutral-900 mb-8 tracking-tighter"
                    >
                        Questions? <br />
                        <span className="text-primary">We have answers.</span>
                    </motion.h3>
                </div>

                <div className="space-y-6">
                    {faqs.map((faq, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: index * 0.05 }}
                            className={`rounded-[2rem] border transition-all duration-500 overflow-hidden ${openIndex === index
                                    ? "bg-white border-primary shadow-2xl shadow-primary/5"
                                    : "bg-white/40 border-white shadow-sm hover:bg-white hover:border-neutral-200"
                                }`}
                        >
                            <button
                                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                                className="w-full px-10 py-8 flex items-center justify-between text-left group"
                            >
                                <span className={`text-xl font-black font-outfit tracking-tight transition-colors duration-300 ${openIndex === index ? "text-primary" : "text-neutral-900"
                                    }`}>
                                    {faq.question}
                                </span>
                                <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 ${openIndex === index ? "bg-primary text-white rotate-180" : "bg-neutral-100 text-neutral-400"
                                    }`}>
                                    {openIndex === index ? (
                                        <Minus size={20} strokeWidth={3} />
                                    ) : (
                                        <Plus size={20} strokeWidth={3} />
                                    )}
                                </div>
                            </button>
                            <AnimatePresence>
                                {openIndex === index && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: "auto", opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        transition={{ duration: 0.4, ease: "circOut" }}
                                    >
                                        <div className="px-10 pb-10 text-neutral-500 font-medium leading-relaxed tracking-tight text-lg">
                                            {faq.answer}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default FAQ;
