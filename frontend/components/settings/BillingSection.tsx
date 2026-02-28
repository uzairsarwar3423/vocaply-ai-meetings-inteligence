"use client";

import { motion } from "framer-motion";
import { CreditCard, Zap, CheckCircle2, Download } from "lucide-react";
import { Button } from "@/components/ui/button";

export function BillingSection() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="space-y-8"
        >
            <div>
                <h3 className="text-xl font-bold font-outfit">Subscription & Billing</h3>
                <p className="text-sm text-neutral-500 mt-1">Manage your plan, payment methods, and billing history.</p>
            </div>

            {/* Current Plan Card (Premium Styling) */}
            <div className="relative overflow-hidden rounded-2xl p-[1px] bg-gradient-to-r from-primary to-secondary/80">
                <div className="absolute inset-0 bg-gradient-to-r from-primary/10 to-secondary/10" />
                <div className="relative bg-white rounded-2xl h-full p-8 space-y-6">

                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                        <div>
                            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-bold mb-3 border border-primary/20">
                                <Zap className="w-4 h-4" /> Pro Plan
                            </div>
                            <h4 className="text-3xl font-outfit font-bold">
                                $29<span className="text-lg text-neutral-500 font-normal">/month</span>
                            </h4>
                            <p className="text-neutral-500 mt-2 max-w-md">
                                You are currently on the Pro plan. Your next billing date is <strong className="text-neutral-900">April 15, 2026</strong>.
                            </p>
                        </div>

                        <div className="flex flex-col gap-3">
                            <Button className="bg-neutral-900 hover:bg-black text-white shadow-lg w-full md:w-auto">
                                Upgrade Plan
                            </Button>
                            <Button variant="outline" className="text-neutral-600 border-neutral-200">
                                Cancel Subscription
                            </Button>
                        </div>
                    </div>

                    <div className="pt-6 border-t border-gradient-to-r from-neutral-100 to-primary/10">
                        <h5 className="font-medium mb-4 text-sm uppercase tracking-wider text-neutral-500">Plan Features</h5>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                            <div className="flex items-center gap-2 text-sm text-neutral-700">
                                <CheckCircle2 className="w-4 h-4 text-primary" /> Unlimited meeting recordings
                            </div>
                            <div className="flex items-center gap-2 text-sm text-neutral-700">
                                <CheckCircle2 className="w-4 h-4 text-primary" /> Premium AI summaries
                            </div>
                            <div className="flex items-center gap-2 text-sm text-neutral-700">
                                <CheckCircle2 className="w-4 h-4 text-primary" /> Auto action items extraction
                            </div>
                            <div className="flex items-center gap-2 text-sm text-neutral-700">
                                <CheckCircle2 className="w-4 h-4 text-primary" /> Multi-language transcription
                            </div>
                            <div className="flex items-center gap-2 text-sm text-neutral-700">
                                <CheckCircle2 className="w-4 h-4 text-primary" /> Custom vocabulary
                            </div>
                            <div className="flex items-center gap-2 text-sm text-neutral-700">
                                <CheckCircle2 className="w-4 h-4 text-primary" /> Priority support
                            </div>
                        </div>
                    </div>

                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Payment Method */}
                <div className="lg:col-span-1 bg-white rounded-2xl border border-neutral-100 shadow-sm p-6 space-y-6">
                    <div>
                        <h4 className="font-medium">Payment Method</h4>
                        <p className="text-sm text-neutral-500">Your primary card on file.</p>
                    </div>

                    <div className="bg-neutral-50 border border-neutral-200 rounded-xl p-4 flex items-start gap-4">
                        <div className="bg-white p-2 rounded shadow-sm border border-neutral-100">
                            <CreditCard className="w-6 h-6 text-neutral-600" />
                        </div>
                        <div className="flex-1">
                            <p className="font-medium flex items-center justify-between">
                                Visa ending in 4242
                                <span className="text-[10px] font-bold uppercase tracking-wider bg-neutral-200 text-neutral-600 px-2 py-0.5 rounded-full">Default</span>
                            </p>
                            <p className="text-sm text-neutral-500 mt-0.5">Expires 12/28</p>
                        </div>
                    </div>

                    <Button variant="outline" className="w-full border-neutral-200">
                        Update Payment Method
                    </Button>
                </div>

                {/* Billing History */}
                <div className="lg:col-span-2 bg-white rounded-2xl border border-neutral-100 shadow-sm overflow-hidden">
                    <div className="p-6 border-b border-neutral-100 flex items-center justify-between">
                        <div>
                            <h4 className="font-medium">Billing History</h4>
                            <p className="text-sm text-neutral-500">Download past invoices.</p>
                        </div>
                    </div>

                    <div className="divide-y divide-neutral-100">
                        {[
                            { date: "Mar 15, 2026", amount: "$29.00", status: "Paid", invoice: "#INV-2026-03" },
                            { date: "Feb 15, 2026", amount: "$29.00", status: "Paid", invoice: "#INV-2026-02" },
                            { date: "Jan 15, 2026", amount: "$29.00", status: "Paid", invoice: "#INV-2026-01" },
                        ].map((item, idx) => (
                            <div key={idx} className="p-4 px-6 flex items-center justify-between hover:bg-neutral-50 transition-colors">
                                <div className="flex items-center gap-6">
                                    <div>
                                        <p className="font-medium text-sm">{item.date}</p>
                                        <p className="text-xs text-neutral-500">{item.invoice}</p>
                                    </div>
                                    <div className="hidden sm:block">
                                        <span className="inline-flex items-center rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700 ring-1 ring-inset ring-emerald-600/20">
                                            {item.status}
                                        </span>
                                    </div>
                                </div>
                                <div className="flex items-center gap-6">
                                    <span className="font-medium">{item.amount}</span>
                                    <button className="text-neutral-400 hover:text-primary transition-colors">
                                        <Download className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

        </motion.div>
    );
}
