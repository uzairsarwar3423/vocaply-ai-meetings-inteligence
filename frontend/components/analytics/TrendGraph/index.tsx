"use client";

import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend,
    Area,
    AreaChart,
} from "recharts";
import { motion } from "framer-motion";

interface TrendPoint {
    date: string;
    completion_rate?: number;
    created?: number;
    completed?: number;
}

interface TrendGraphProps {
    data: TrendPoint[];
    mode?: "completion" | "volume";   // completion_rate vs created/completed
    isLoading?: boolean;
}

const tooltipStyle = {
    borderRadius: "12px",
    border: "1px solid #f0f0f0",
    fontSize: 12,
    fontWeight: 700,
    boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
};

export default function TrendGraph({ data, mode = "completion", isLoading = false }: TrendGraphProps) {
    if (isLoading) {
        return (
            <div className="flex items-end gap-1 h-48 animate-pulse px-4">
                {[...Array(10)].map((_, i) => (
                    <div
                        key={i}
                        className="flex-1 bg-neutral-100 rounded-t-sm"
                        style={{ height: `${30 + Math.random() * 60}%` }}
                    />
                ))}
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="flex items-center justify-center h-48 text-neutral-300">
                <p className="text-xs font-bold uppercase tracking-widest">No trend data yet</p>
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <ResponsiveContainer width="100%" height={240}>
                {mode === "completion" ? (
                    <AreaChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
                        <defs>
                            <linearGradient id="completionGrad" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#0d9488" stopOpacity={0.15} />
                                <stop offset="95%" stopColor="#0d9488" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f5f5f5" />
                        <XAxis
                            dataKey="date"
                            tick={{ fontSize: 10, fontWeight: 700, fill: "#9ca3af" }}
                            axisLine={false}
                            tickLine={false}
                        />
                        <YAxis
                            domain={[0, 100]}
                            tick={{ fontSize: 10, fontWeight: 700, fill: "#9ca3af" }}
                            axisLine={false}
                            tickLine={false}
                            tickFormatter={(v) => `${v}%`}
                        />
                        <Tooltip
                            contentStyle={tooltipStyle}
                            formatter={(v: any) => [`${v}%`, "Completion Rate"]}
                        />
                        <Area
                            type="monotone"
                            dataKey="completion_rate"
                            stroke="#0d9488"
                            strokeWidth={2.5}
                            fill="url(#completionGrad)"
                            dot={{ fill: "#0d9488", r: 3, strokeWidth: 0 }}
                            activeDot={{ r: 5, fill: "#0d9488", strokeWidth: 0 }}
                        />
                    </AreaChart>
                ) : (
                    <LineChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f5f5f5" />
                        <XAxis
                            dataKey="date"
                            tick={{ fontSize: 10, fontWeight: 700, fill: "#9ca3af" }}
                            axisLine={false}
                            tickLine={false}
                        />
                        <YAxis
                            tick={{ fontSize: 10, fontWeight: 700, fill: "#9ca3af" }}
                            axisLine={false}
                            tickLine={false}
                            allowDecimals={false}
                        />
                        <Tooltip contentStyle={tooltipStyle} />
                        <Legend
                            iconType="circle"
                            iconSize={8}
                            formatter={(v) => (
                                <span style={{ fontSize: 11, fontWeight: 700, color: "#6b7280" }}>
                                    {v === "created" ? "Created" : "Completed"}
                                </span>
                            )}
                        />
                        <Line
                            type="monotone"
                            dataKey="created"
                            stroke="#94a3b8"
                            strokeWidth={2}
                            dot={false}
                            activeDot={{ r: 4 }}
                        />
                        <Line
                            type="monotone"
                            dataKey="completed"
                            stroke="#0d9488"
                            strokeWidth={2.5}
                            dot={false}
                            activeDot={{ r: 5 }}
                        />
                    </LineChart>
                )}
            </ResponsiveContainer>
        </motion.div>
    );
}
