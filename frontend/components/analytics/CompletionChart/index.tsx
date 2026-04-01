"use client";

import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    ResponsiveContainer,
    Legend,
} from "recharts";
import { motion } from "framer-motion";

interface StatusSlice {
    status: string;
    count: number;
    color: string;
}

interface CompletionChartProps {
    data: StatusSlice[];
    isLoading?: boolean;
}

const renderCustomLabel = ({
    cx,
    cy,
    midAngle,
    innerRadius,
    outerRadius,
    percent,
}: any) => {
    if (percent < 0.05) return null;
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.55;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    return (
        <text
            x={x}
            y={y}
            fill="white"
            textAnchor="middle"
            dominantBaseline="central"
            className="text-[11px] font-black"
            style={{ fontSize: 11, fontWeight: 800 }}
        >
            {`${(percent * 100).toFixed(0)}%`}
        </text>
    );
};

export default function CompletionChart({ data, isLoading = false }: CompletionChartProps) {
    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-48 animate-pulse">
                <div className="w-36 h-36 rounded-full bg-neutral-100" />
            </div>
        );
    }

    const hasData = data && data.some((d) => d.count > 0);

    if (!hasData) {
        return (
            <div className="flex flex-col items-center justify-center h-48 text-neutral-300">
                <p className="text-xs font-bold uppercase tracking-widest">No data yet</p>
            </div>
        );
    }

    const filtered = data.filter((d) => d.count > 0);

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
        >
            <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                    <Pie
                        data={filtered}
                        dataKey="count"
                        nameKey="status"
                        cx="50%"
                        cy="50%"
                        outerRadius={90}
                        innerRadius={48}
                        paddingAngle={3}
                        labelLine={false}
                        label={renderCustomLabel}
                    >
                        {filtered.map((entry, index) => (
                            <Cell
                                key={`cell-${index}`}
                                fill={entry.color}
                                stroke="transparent"
                            />
                        ))}
                    </Pie>
                    <Tooltip
                        formatter={(value: any, name: any) => [value, name]}
                        contentStyle={{
                            borderRadius: "12px",
                            border: "1px solid #f0f0f0",
                            fontSize: 12,
                            fontWeight: 700,
                            boxShadow: "0 4px 20px rgba(0,0,0,0.08)",
                        }}
                    />
                    <Legend
                        iconType="circle"
                        iconSize={8}
                        formatter={(value) => (
                            <span style={{ fontSize: 11, fontWeight: 700, color: "#6b7280" }}>
                                {value}
                            </span>
                        )}
                    />
                </PieChart>
            </ResponsiveContainer>
        </motion.div>
    );
}
