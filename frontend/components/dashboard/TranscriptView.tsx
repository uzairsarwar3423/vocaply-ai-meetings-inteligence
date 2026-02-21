import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar } from '@/components/ui/avatar';
import { CheckCircle2, Copy, Download, MessageSquare, Search, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface TranscriptEntry {
    speaker: string;
    timestamp: string;
    text: string;
    sentiment?: "positive" | "neutral" | "negative";
}

export interface TranscriptViewProps {
    summary: string;
    keyPoints: string[];
    actionItems: string[];
    transcript: TranscriptEntry[];
    className?: string;
}

const TranscriptView: React.FC<TranscriptViewProps> = ({
    summary,
    keyPoints,
    actionItems,
    transcript,
    className,
}) => {
    return (
        <div className={cn("w-full h-full flex flex-col space-y-6", className)}>
            <Tabs defaultValue="transcript" className="w-full">
                <div className="flex items-center justify-between mb-2">
                    <TabsList className="bg-neutral-100/50 p-1 rounded-2xl">
                        <TabsTrigger value="summary" className="px-6 flex items-center gap-2">
                            <Sparkles className="w-4 h-4" />
                            AI Summary
                        </TabsTrigger>
                        <TabsTrigger value="transcript" className="px-6 flex items-center gap-2">
                            <MessageSquare className="w-4 h-4" />
                            Full Transcript
                        </TabsTrigger>
                        <TabsTrigger value="insights" className="px-6 flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4" />
                            Insights
                        </TabsTrigger>
                    </TabsList>

                    <div className="flex items-center gap-2">
                        <button className="p-2.5 rounded-2xl hover:bg-neutral-100 text-neutral-500 transition-colors border border-neutral-200">
                            <Search className="w-4 h-4" />
                        </button>
                        <button className="p-2.5 rounded-2xl hover:bg-neutral-100 text-neutral-500 transition-colors border border-neutral-200">
                            <Copy className="w-4 h-4" />
                        </button>
                        <button className="flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-neutral-900 text-white text-sm font-semibold hover:bg-neutral-800 transition-colors">
                            <Download className="w-4 h-4" />
                            Export
                        </button>
                    </div>
                </div>

                {/* Summary Content */}
                <TabsContent value="summary" className="mt-6">
                    <Card className="border-none shadow-none bg-primary-50/30">
                        <CardContent className="p-8">
                            <h3 className="text-xl font-bold text-neutral-900 mb-4 flex items-center gap-2">
                                <Sparkles className="w-5 h-5 text-primary" />
                                Meeting Executive Summary
                            </h3>
                            <p className="text-neutral-700 leading-relaxed text-lg italic">
                                "{summary}"
                            </p>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Transcript Content */}
                <TabsContent value="transcript" className="mt-6">
                    <div className="space-y-8 max-h-[600px] overflow-y-auto pr-4 custom-scrollbar">
                        {transcript.map((entry, i) => (
                            <div key={i} className="flex gap-4 group">
                                <Avatar fallback={entry.speaker} className="mt-1" size="md" />
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-1.5">
                                        <span className="font-bold text-neutral-900">{entry.speaker}</span>
                                        <span className="text-xs font-medium text-neutral-400 bg-neutral-100 px-2 py-0.5 rounded-md">{entry.timestamp}</span>
                                    </div>
                                    <p className="text-neutral-600 leading-relaxed group-hover:text-neutral-900 transition-colors">
                                        {entry.text}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </TabsContent>

                {/* Insights Content */}
                <TabsContent value="insights" className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Card className="border-emerald-100 bg-emerald-50/30">
                        <CardContent className="p-6">
                            <h4 className="font-bold text-emerald-900 mb-4 flex items-center gap-2">
                                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                                Action Items
                            </h4>
                            <ul className="space-y-3">
                                {actionItems.map((item, i) => (
                                    <li key={i} className="flex gap-3 text-sm text-emerald-800 group cursor-pointer">
                                        <div className="mt-1 w-4 h-4 rounded-full border-2 border-emerald-300 flex-shrink-0 group-hover:border-emerald-600 group-hover:bg-emerald-100 transition-all" />
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>

                    <Card className="border-sky-100 bg-sky-50/30">
                        <CardContent className="p-6">
                            <h4 className="font-bold text-sky-900 mb-4 flex items-center gap-2">
                                <Sparkles className="w-5 h-5 text-sky-600" />
                                Key Points
                            </h4>
                            <ul className="space-y-3">
                                {keyPoints.map((item, i) => (
                                    <li key={i} className="flex gap-3 text-sm text-sky-800">
                                        <div className="mt-2 w-1.5 h-1.5 rounded-full bg-sky-400 flex-shrink-0" />
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    );
};

export default TranscriptView;
