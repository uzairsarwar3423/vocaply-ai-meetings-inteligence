"use client";

import { motion } from "framer-motion";
import { LucideIcon, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MetricsCardProps {
    label: string;
    value: string | number;
    icon: LucideIcon;
    color: string;      // Tailwind text color e.g. "text-primary"
    bg: string;         // Tailwind bg color e.g. "bg-primary/10"
    delta?: string;     // e.g. "+12%" or "-3%"
    deltaLabel?: string;  // e.g. "vs last period"
    isLoading?: boolean;
}

export default function MetricsCard({
    label,
    value,
    icon: Icon,
    color,
    bg,
    delta,
    deltaLabel = "vs last period",
    isLoading = false,
}: MetricsCardProps) {
    const isPositive = delta ? delta.startsWith("+") : null;
    const isNegative = delta ? delta.startsWith("-") : null;

    const TrendIcon = isPositive ? TrendingUp : isNegative ? TrendingDown : Minus;
    const trendColor = isPositive
        ? "text-emerald-500"
        : isNegative
            ? "text-rose-500"
            : "text-neutral-400";

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="group cursor-default"
        >
            <div className="relative bg-white rounded-2xl border border-white/20 shadow-sm hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300 overflow-hidden p-6">
                {/* Background accent */}
                <div className={`absolute -top-6 -right-6 w-24 h-24 ${bg} rounded-full opacity-20 group-hover:opacity-40 group-hover:scale-125 transition-all duration-500`} />

                {isLoading ? (
                    <div className="space-y-3 animate-pulse">
                        <div className="w-10 h-10 rounded-xl bg-neutral-100" />
                        <div className="h-3 w-20 rounded bg-neutral-100" />
                        <div className="h-8 w-16 rounded bg-neutral-100" />
                    </div>
                ) : (
                    <>
                        <div className="flex items-center justify-between mb-4">
                            <div className={`w-12 h-12 rounded-2xl ${bg} ${color} flex items-center justify-center shadow-inner`}>
                                <Icon size={22} className="group-hover:scale-110 transition-transform" />
                            </div>

                            {delta && (
                                <div className={`flex items-center gap-1 text-[11px] font-bold ${trendColor}`}>
                                    <TrendIcon size={13} />
                                    <span>{delta}</span>
                                </div>
                            )}
                        </div>

                        <p className="text-[10px] font-black text-neutral-400 uppercase tracking-widest leading-none">
                            {label}
                        </p>
                        <h3 className="text-3xl font-black font-outfit mt-2 text-neutral-900 tracking-tight">
                            {value}
                        </h3>
                        {deltaLabel && (
                            <p className="text-[10px] text-neutral-300 mt-1 font-medium">{deltaLabel}</p>
                        )}
                    </>
                )}
            </div>
        </motion.div>
    );
}
