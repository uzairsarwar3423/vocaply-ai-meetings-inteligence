"use client";

import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
    CheckSquare,
    TrendingUp,
    Clock,
    AlertTriangle,
    Video,
    Zap,
    Users,
    BarChart2,
} from "lucide-react";

import MetricsCard from "@/components/analytics/MetricsCard";
import CompletionChart from "@/components/analytics/CompletionChart";
import TeamPerformance from "@/components/analytics/TeamPerformance";
import TrendGraph from "@/components/analytics/TrendGraph";
import ExportButton from "@/components/analytics/ExportButton";
import { apiClient } from "@/lib/api/client";

// ─── Types ────────────────────────────────────────────────────────────────────

type Granularity = "daily" | "weekly" | "monthly";
type Period = 7 | 30 | 90;

const PERIOD_OPTIONS: { label: string; value: Period }[] = [
    { label: "7 Days", value: 7 },
    { label: "30 Days", value: 30 },
    { label: "90 Days", value: 90 },
];

// ─── Animation variants ───────────────────────────────────────────────────────

const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.08 } },
};
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fmtRate(v: number) {
    return `${v}%`;
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function AnalyticsPage() {
    const [period, setPeriod] = useState<Period>(30);
    const [granularity, setGranularity] = useState<Granularity>("daily");

    const [overview, setOverview] = useState<any>(null);
    const [completion, setCompletion] = useState<any>(null);
    const [teamPerf, setTeamPerf] = useState<any>(null);
    const [timeTrends, setTimeTrends] = useState<any>(null);

    const [loading, setLoading] = useState({
        overview: true,
        completion: true,
        team: true,
        trends: true,
    });

    const fetchAll = useCallback(async () => {
        setLoading({ overview: true, completion: true, team: true, trends: true });

        const params = `?days=${period}&granularity=${granularity}`;

        await Promise.allSettled([
            apiClient.get(`/analytics/overview${params}`).then((r) => {
                setOverview(r.data);
                setLoading((l) => ({ ...l, overview: false }));
            }),
            apiClient.get(`/analytics/completion-rate${params}`).then((r) => {
                setCompletion(r.data);
                setLoading((l) => ({ ...l, completion: false }));
            }),
            apiClient.get(`/analytics/team-performance${params}`).then((r) => {
                setTeamPerf(r.data);
                setLoading((l) => ({ ...l, team: false }));
            }),
            apiClient.get(`/analytics/time-trends${params}`).then((r) => {
                setTimeTrends(r.data);
                setLoading((l) => ({ ...l, trends: false }));
            }),
        ]);
    }, [period, granularity]);

    useEffect(() => { fetchAll(); }, [fetchAll]);

    // ── Render ──────────────────────────────────────────────────────────────

    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-10 pb-20"
        >
            {/* ── Header ─────────────────────────────────────────────────── */}
            <motion.div
                variants={item}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <div className="h-1 w-8 bg-primary rounded-full" />
                        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-primary">
                            Company Analytics
                        </span>
                    </div>
                    <h1 className="text-4xl font-outfit font-black text-neutral-900 tracking-tight">
                        Analytics Dashboard
                    </h1>
                    <p className="text-neutral-400 mt-1 font-medium text-sm">
                        Track meeting productivity, completion rates, and team performance.
                    </p>
                </div>

                <div className="flex items-center gap-3 flex-wrap">
                    {/* Period selector */}
                    <div className="flex bg-neutral-100 rounded-xl p-1 gap-1">
                        {PERIOD_OPTIONS.map((opt) => (
                            <button
                                key={opt.value}
                                onClick={() => setPeriod(opt.value)}
                                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${period === opt.value
                                        ? "bg-white text-primary shadow-sm"
                                        : "text-neutral-500 hover:text-neutral-900"
                                    }`}
                            >
                                {opt.label}
                            </button>
                        ))}
                    </div>

                    {/* Granularity selector */}
                    <select
                        value={granularity}
                        onChange={(e) => setGranularity(e.target.value as Granularity)}
                        className="text-xs font-bold border border-neutral-200 rounded-xl px-3 py-2 bg-white text-neutral-600 focus:outline-none focus:ring-2 focus:ring-primary/20"
                    >
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                    </select>

                    <ExportButton days={period} />
                </div>
            </motion.div>

            {/* ── KPI Cards ──────────────────────────────────────────────── */}
            <motion.div
                variants={item}
                className="grid grid-cols-2 md:grid-cols-4 gap-5"
            >
                <MetricsCard
                    label="Total Created"
                    value={overview?.total_created ?? "—"}
                    icon={CheckSquare}
                    color="text-primary"
                    bg="bg-primary/10"
                    delta={undefined}
                    deltaLabel={`Last ${period} days`}
                    isLoading={loading.overview}
                />
                <MetricsCard
                    label="Completion Rate"
                    value={overview ? fmtRate(overview.completion_rate) : "—"}
                    icon={TrendingUp}
                    color="text-emerald-500"
                    bg="bg-emerald-50"
                    deltaLabel="Action items"
                    isLoading={loading.overview}
                />
                <MetricsCard
                    label="Avg Completion"
                    value={overview ? `${overview.avg_completion_hours}h` : "—"}
                    icon={Clock}
                    color="text-indigo-500"
                    bg="bg-indigo-50"
                    deltaLabel="Hours to complete"
                    isLoading={loading.overview}
                />
                <MetricsCard
                    label="Overdue Items"
                    value={overview?.overdue ?? "—"}
                    icon={AlertTriangle}
                    color="text-rose-500"
                    bg="bg-rose-50"
                    deltaLabel="Need attention"
                    isLoading={loading.overview}
                />
            </motion.div>

            {/* ── Secondary KPIs ─────────────────────────────────────────── */}
            <motion.div
                variants={item}
                className="grid grid-cols-2 md:grid-cols-3 gap-5"
            >
                <MetricsCard
                    label="Total Meetings"
                    value={overview?.total_meetings ?? "—"}
                    icon={Video}
                    color="text-sky-500"
                    bg="bg-sky-50"
                    deltaLabel={`Last ${period} days`}
                    isLoading={loading.overview}
                />
                <MetricsCard
                    label="Items / Meeting"
                    value={overview?.avg_items_per_meeting ?? "—"}
                    icon={Zap}
                    color="text-amber-500"
                    bg="bg-amber-50"
                    deltaLabel="Meeting efficiency"
                    isLoading={loading.overview}
                />
                <MetricsCard
                    label="Team Members"
                    value={teamPerf?.team?.length ?? "—"}
                    icon={Users}
                    color="text-violet-500"
                    bg="bg-violet-50"
                    deltaLabel="With activity"
                    isLoading={loading.team}
                />
            </motion.div>

            {/* ── Charts Row 1 ────────────────────────────────────────────── */}
            <motion.div
                variants={item}
                className="grid grid-cols-1 lg:grid-cols-3 gap-8"
            >
                {/* Completion Rate Trend */}
                <div className="lg:col-span-2 bg-white rounded-2xl border border-neutral-100 shadow-sm p-6">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-base font-black text-neutral-900 tracking-tight">
                                Completion Rate Over Time
                            </h2>
                            <p className="text-[10px] text-neutral-400 font-bold uppercase tracking-widest mt-0.5">
                                {granularity} · last {period} days
                            </p>
                        </div>
                        <div className="w-8 h-8 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-500">
                            <TrendingUp size={16} />
                        </div>
                    </div>
                    <TrendGraph
                        data={completion?.trend ?? []}
                        mode="completion"
                        isLoading={loading.completion}
                    />
                </div>

                {/* Status Distribution */}
                <div className="bg-white rounded-2xl border border-neutral-100 shadow-sm p-6">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-base font-black text-neutral-900 tracking-tight">
                                Status Distribution
                            </h2>
                            <p className="text-[10px] text-neutral-400 font-bold uppercase tracking-widest mt-0.5">
                                Action items
                            </p>
                        </div>
                        <div className="w-8 h-8 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                            <BarChart2 size={16} />
                        </div>
                    </div>
                    <CompletionChart
                        data={overview?.status_distribution ?? []}
                        isLoading={loading.overview}
                    />
                </div>
            </motion.div>

            {/* ── Charts Row 2 ────────────────────────────────────────────── */}
            <motion.div
                variants={item}
                className="grid grid-cols-1 lg:grid-cols-2 gap-8"
            >
                {/* Team Performance */}
                <div className="bg-white rounded-2xl border border-neutral-100 shadow-sm p-6">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-base font-black text-neutral-900 tracking-tight">
                                Team Performance
                            </h2>
                            <p className="text-[10px] text-neutral-400 font-bold uppercase tracking-widest mt-0.5">
                                Assigned vs completed
                            </p>
                        </div>
                        <div className="w-8 h-8 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-500">
                            <Users size={16} />
                        </div>
                    </div>
                    <TeamPerformance
                        data={teamPerf?.team ?? []}
                        isLoading={loading.team}
                    />
                </div>

                {/* Volume Trend */}
                <div className="bg-white rounded-2xl border border-neutral-100 shadow-sm p-6">
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h2 className="text-base font-black text-neutral-900 tracking-tight">
                                Action Item Volume
                            </h2>
                            <p className="text-[10px] text-neutral-400 font-bold uppercase tracking-widest mt-0.5">
                                Created vs completed
                            </p>
                        </div>
                        <div className="w-8 h-8 rounded-xl bg-sky-50 flex items-center justify-center text-sky-500">
                            <CheckSquare size={16} />
                        </div>
                    </div>
                    <TrendGraph
                        data={timeTrends?.action_item_trends ?? []}
                        mode="volume"
                        isLoading={loading.trends}
                    />
                </div>
            </motion.div>

            {/* ── Team Productivity Table ────────────────────────────────── */}
            <motion.div variants={item}>
                <div className="bg-white rounded-2xl border border-neutral-100 shadow-sm overflow-hidden">
                    <div className="flex items-center justify-between px-6 py-5 border-b border-neutral-50">
                        <div>
                            <h2 className="text-base font-black text-neutral-900 tracking-tight">
                                Individual Productivity
                            </h2>
                            <p className="text-[10px] text-neutral-400 font-bold uppercase tracking-widest mt-0.5">
                                Team member breakdown
                            </p>
                        </div>
                    </div>

                    {loading.team ? (
                        <div className="p-8 space-y-3 animate-pulse">
                            {[...Array(4)].map((_, i) => (
                                <div key={i} className="h-10 bg-neutral-50 rounded-xl" />
                            ))}
                        </div>
                    ) : !teamPerf?.team?.length ? (
                        <div className="p-16 text-center text-neutral-300">
                            <p className="text-xs font-black uppercase tracking-widest">No team data yet</p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-neutral-50 bg-neutral-50/50">
                                        <th className="px-6 py-3 text-left text-[10px] font-black text-neutral-400 uppercase tracking-widest">Member</th>
                                        <th className="px-4 py-3 text-right text-[10px] font-black text-neutral-400 uppercase tracking-widest">Assigned</th>
                                        <th className="px-4 py-3 text-right text-[10px] font-black text-neutral-400 uppercase tracking-widest">Completed</th>
                                        <th className="px-4 py-3 text-right text-[10px] font-black text-neutral-400 uppercase tracking-widest">Rate</th>
                                        <th className="px-4 py-3 text-right text-[10px] font-black text-neutral-400 uppercase tracking-widest">Avg Time</th>
                                        <th className="px-4 py-3 text-right text-[10px] font-black text-neutral-400 uppercase tracking-widest">Meetings</th>
                                        <th className="px-6 py-3 text-left text-[10px] font-black text-neutral-400 uppercase tracking-widest">Progress</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-neutral-50">
                                    {teamPerf.team.map((member: any) => (
                                        <tr key={member.user_id} className="hover:bg-neutral-50/50 transition-colors group">
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center text-primary font-black text-xs shadow-inner">
                                                        {member.name?.[0] || "?"}
                                                    </div>
                                                    <div>
                                                        <p className="text-xs font-black text-neutral-900 leading-tight">{member.name}</p>
                                                        <p className="text-[10px] text-neutral-400 font-medium">{member.email}</p>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-4 py-4 text-right text-xs font-bold text-neutral-600">{member.assigned}</td>
                                            <td className="px-4 py-4 text-right text-xs font-bold text-emerald-600">{member.completed}</td>
                                            <td className="px-4 py-4 text-right">
                                                <span className={`text-xs font-black px-2 py-0.5 rounded-full ${member.completion_rate >= 80
                                                        ? "bg-emerald-50 text-emerald-600"
                                                        : member.completion_rate >= 50
                                                            ? "bg-amber-50 text-amber-600"
                                                            : "bg-rose-50 text-rose-500"
                                                    }`}>
                                                    {member.completion_rate}%
                                                </span>
                                            </td>
                                            <td className="px-4 py-4 text-right text-xs font-bold text-neutral-500">
                                                {member.avg_completion_hours ? `${member.avg_completion_hours}h` : "—"}
                                            </td>
                                            <td className="px-4 py-4 text-right text-xs font-bold text-neutral-500">{member.meetings_created}</td>
                                            <td className="px-6 py-4">
                                                <div className="w-full bg-neutral-100 rounded-full h-1.5 overflow-hidden">
                                                    <div
                                                        className="h-full bg-gradient-to-r from-primary to-primary-300 rounded-full transition-all duration-500"
                                                        style={{ width: `${member.completion_rate}%` }}
                                                    />
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </motion.div>
        </motion.div>
    );
}
