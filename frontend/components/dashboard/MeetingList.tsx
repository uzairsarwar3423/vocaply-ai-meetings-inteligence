import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Avatar } from '@/components/ui/avatar';
import {
    Calendar,
    Clock,
    FileText,
    MoreHorizontal,
    Mic2,
    Play,
    TrendingUp
} from 'lucide-react';
import { cn } from '@/lib/utils';

export interface MeetingListItem {
    id: string;
    title: string;
    date: string;
    time: string;
    duration: string;
    participants: { name: string; avatar?: string }[];
    status: "processed" | "processing" | "failed";
    sentiment: "positive" | "neutral" | "negative";
}

export interface MeetingListProps {
    items: MeetingListItem[];
    className?: string;
}

const MeetingList: React.FC<MeetingListProps> = ({ items, className }) => {
    return (
        <div className={cn("w-full overflow-hidden rounded-3xl border border-neutral-100 bg-white", className)}>
            <table className="w-full text-left border-collapse">
                <thead>
                    <tr className="bg-neutral-50/50 border-b border-neutral-100">
                        <th className="px-6 py-4 text-xs font-bold text-neutral-500 uppercase tracking-wider">Session</th>
                        <th className="px-6 py-4 text-xs font-bold text-neutral-500 uppercase tracking-wider">Participants</th>
                        <th className="px-6 py-4 text-xs font-bold text-neutral-500 uppercase tracking-wider">Date & Time</th>
                        <th className="px-6 py-4 text-xs font-bold text-neutral-500 uppercase tracking-wider">Duration</th>
                        <th className="px-6 py-4 text-xs font-bold text-neutral-500 uppercase tracking-wider">Sentiment</th>
                        <th className="px-6 py-4 text-xs font-bold text-neutral-500 uppercase tracking-wider text-right">Action</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-neutral-50">
                    {items.map((item) => (
                        <tr key={item.id} className="hover:bg-primary-50/10 transition-colors group">
                            <td className="px-6 py-4">
                                <div className="flex items-center gap-4">
                                    <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                                        <Mic2 className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <div className="font-bold text-neutral-900 group-hover:text-primary transition-colors">{item.title}</div>
                                        <div className="flex items-center gap-2 mt-0.5">
                                            <Badge variant={item.status === "processed" ? "success" : "warning"} className="text-[10px] px-1.5 py-0">
                                                {item.status}
                                            </Badge>
                                            <span className="text-[10px] text-neutral-400 flex items-center gap-1">
                                                <FileText className="w-3 h-3" />
                                                Transcript ready
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </td>
                            <td className="px-6 py-4">
                                <div className="flex -space-x-2">
                                    {item.participants.slice(0, 3).map((p, i) => (
                                        <Avatar key={i} fallback={p.name} size="sm" className="ring-2 ring-white" />
                                    ))}
                                    {item.participants.length > 3 && (
                                        <div className="h-8 w-8 rounded-full bg-neutral-100 border-2 border-white flex items-center justify-center text-[10px] font-bold text-neutral-500">
                                            +{item.participants.length - 3}
                                        </div>
                                    )}
                                </div>
                            </td>
                            <td className="px-6 py-4">
                                <div className="text-sm text-neutral-700 font-medium">{item.date}</div>
                                <div className="text-xs text-neutral-400 mt-0.5">{item.time}</div>
                            </td>
                            <td className="px-6 py-4">
                                <div className="flex items-center gap-1.5 text-sm text-neutral-600">
                                    <Clock className="w-4 h-4 text-neutral-400" />
                                    {item.duration}
                                </div>
                            </td>
                            <td className="px-6 py-4">
                                <div className={cn(
                                    "inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded-full",
                                    item.sentiment === "positive" ? "text-emerald-600 bg-emerald-50" :
                                        item.sentiment === "neutral" ? "text-neutral-600 bg-neutral-50" : "text-rose-600 bg-rose-50"
                                )}>
                                    <TrendingUp className="w-3 h-3" />
                                    {item.sentiment}
                                </div>
                            </td>
                            <td className="px-6 py-4 text-right">
                                <div className="flex items-center justify-end gap-2">
                                    <button className="p-2 rounded-xl text-primary hover:bg-primary-100 transition-colors">
                                        <Play className="w-4 h-4 fill-current" />
                                    </button>
                                    <button className="p-2 rounded-xl text-neutral-400 hover:bg-neutral-100 transition-colors">
                                        <MoreHorizontal className="w-4 h-4" />
                                    </button>
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default MeetingList;
