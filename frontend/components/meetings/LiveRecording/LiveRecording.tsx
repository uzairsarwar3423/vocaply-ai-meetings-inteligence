'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Radio, Clock, Users, AlertTriangle } from 'lucide-react';
import { Progress } from '@/components/ui/Progress';

interface LiveRecordingProps {
    botStatus: string;
    participantCount: number;
    isAlone: boolean;
    joinedAt: string | null;
    recordingUrl: string | null;
}

export default function LiveRecording({
    botStatus,
    participantCount,
    isAlone,
    joinedAt,
    recordingUrl,
}: LiveRecordingProps) {
    const [duration, setDuration] = useState(0);
    const [audioLevel, setAudioLevel] = useState(0);

    const isRecording = botStatus === 'recording' || botStatus === 'in_meeting';
    const isCompleted = botStatus === 'completed' && recordingUrl;

    // Update duration timer
    useEffect(() => {
        if (!isRecording || !joinedAt) {
            setDuration(0);
            return;
        }

        const startTime = new Date(joinedAt).getTime();

        const interval = setInterval(() => {
            const now = Date.now();
            const elapsed = Math.floor((now - startTime) / 1000);
            setDuration(elapsed);
        }, 1000);

        return () => clearInterval(interval);
    }, [isRecording, joinedAt]);

    // Simulate audio level (in real app, this would come from WebSocket)
    useEffect(() => {
        if (!isRecording) {
            setAudioLevel(0);
            return;
        }

        const interval = setInterval(() => {
            // Random audio level between 20-80
            setAudioLevel(Math.random() * 60 + 20);
        }, 200);

        return () => clearInterval(interval);
    }, [isRecording]);

    const formatDuration = (seconds: number): string => {
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hrs > 0) {
            return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    if (!isRecording && !isCompleted) {
        return null;
    }

    return (
        <Card>
            <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                    {isRecording ? (
                        <>
                            <Radio className="h-4 w-4 text-red-500 animate-pulse" />
                            <span>Recording in Progress</span>
                        </>
                    ) : (
                        <>
                            <Radio className="h-4 w-4 text-green-500" />
                            <span>Recording Complete</span>
                        </>
                    )}
                </CardTitle>
            </CardHeader>

            <CardContent className="space-y-4">
                {/* Recording Stats */}
                {isRecording && (
                    <div className="grid grid-cols-2 gap-4">
                        {/* Duration */}
                        <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-gray-400" />
                            <div>
                                <div className="text-sm text-gray-500">Duration</div>
                                <div className="text-lg font-mono font-semibold">
                                    {formatDuration(duration)}
                                </div>
                            </div>
                        </div>

                        {/* Participants */}
                        <div className="flex items-center gap-2">
                            <Users className="h-4 w-4 text-gray-400" />
                            <div>
                                <div className="text-sm text-gray-500">Participants</div>
                                <div className="text-lg font-semibold">
                                    {participantCount}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Audio Waveform */}
                {isRecording && (
                    <div className="space-y-2">
                        <div className="text-sm text-gray-500">Audio Level</div>
                        <div className="flex items-center gap-1 h-8">
                            {Array.from({ length: 20 }).map((_, i) => {
                                const isActive = (audioLevel / 100) * 20 > i;
                                const height = isActive
                                    ? Math.random() * 60 + 40
                                    : 20;

                                return (
                                    <div
                                        key={i}
                                        className={`
                      flex-1 rounded-sm transition-all duration-100
                      ${isActive ? 'bg-green-500' : 'bg-gray-200'}
                    `}
                                        style={{
                                            height: `${height}%`,
                                            minHeight: '20%'
                                        }}
                                    />
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* Alone Warning */}
                {isRecording && isAlone && (
                    <div className="flex items-center gap-2 p-3 rounded-lg bg-yellow-50 border border-yellow-200">
                        <AlertTriangle className="h-4 w-4 text-yellow-600 flex-shrink-0" />
                        <div className="text-sm text-yellow-700">
                            Bot is alone in the meeting. It will automatically leave after 5 minutes.
                        </div>
                    </div>
                )}

                {/* Completed Message */}
                {isCompleted && (
                    <div className="text-sm text-gray-600">
                        Recording has been saved and is being processed for transcription.
                    </div>
                )}
            </CardContent>
        </Card>
    );
}