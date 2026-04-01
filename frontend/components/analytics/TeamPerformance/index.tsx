"use client";

import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    Cell,
} from "recharts";
import { motion } from "framer-motion";

interface TeamMember {
    user_id: string;
    name: string;
    assigned: number;
    completed: number;
    completion_rate: number;
    meetings_created: number;
}

interface TeamPerformanceProps {
    data: TeamMember[];
    isLoading?: boolean;
}

const tooltipStyle = {
    borderRadius: "12px",
    border: "1px solid #f0f0f0",
    fontSize: 12,
    fontWeight: 700,
    boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
};

export default function TeamPerformance({ data, isLoading = false }: TeamPerformanceProps) {
    if (isLoading) {
        return (
            <div className="space-y-3 animate-pulse">
                {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-8 bg-neutral-100 rounded-lg" style={{ width: `${80 - i * 15}%` }} />
                ))}
            </div>
        );
    }

    if (!data || data.length === 0) {
        return (
            <div className="flex items-center justify-center h-48 text-neutral-300">
                <p className="text-xs font-bold uppercase tracking-widest">No team data yet</p>
            </div>
        );
    }

    // Truncate long names
    const chartData = data.slice(0, 8).map((m) => ({
        ...m,
        displayName: m.name.split(" ")[0], // first name only
    }));

    return (
        <motion.div
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
        >
            <ResponsiveContainer width="100%" height={260}>
                <BarChart data={chartData} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f5f5f5" />
                    <XAxis
                        dataKey="displayName"
                        tick={{ fontSize: 11, fontWeight: 700, fill: "#9ca3af" }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <YAxis
                        tick={{ fontSize: 11, fontWeight: 700, fill: "#9ca3af" }}
                        axisLine={false}
                        tickLine={false}
                        allowDecimals={false}
                    />
                    <Tooltip
                        contentStyle={tooltipStyle}
                        formatter={(value: any, name: any) => [
                            value,
                            name === "assigned" ? "Assigned" : "Completed",
                        ]}
                    />
                    <Legend
                        iconType="circle"
                        iconSize={8}
                        formatter={(v) => (
                            <span style={{ fontSize: 11, fontWeight: 700, color: "#6b7280" }}>
                                {v === "assigned" ? "Assigned" : "Completed"}
                            </span>
                        )}
                    />
                    <Bar dataKey="assigned" fill="#e0f2fe" radius={[6, 6, 0, 0]} />
                    <Bar dataKey="completed" fill="#0d9488" radius={[6, 6, 0, 0]} />
                </BarChart>
            </ResponsiveContainer>
        </motion.div>
    );
}
