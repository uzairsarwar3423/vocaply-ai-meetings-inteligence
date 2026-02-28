'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import BotStatus from '@/components/meetings/BotStatus/BotStatus';
import BotControls from '@/components/meetings/BotControls/BotControls';
import LiveRecording from '@/components/meetings/LiveRecording/LiveRecording';
import { useMeetingWebSocket, useBotEvents, useRecordingEvents, useParticipantEvents } from '@/hooks/useWebSocket';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/hooks/useToast';

interface BotSession {
    bot_session_id: string;
    bot_id: string | null;
    status: string;
    platform: string;
    joined_at: string | null;
    left_at: string | null;
    participant_count: number;
    is_alone: boolean;
    recording_url: string | null;
    recording_duration: number | null;
    error: string | null;
}

export default function MeetingBotPage() {
    const params = useParams();
    const meetingId = params?.id as string;
    const { toast } = useToast();

    const [botSession, setBotSession] = useState<BotSession | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // WebSocket connection
    const ws = useMeetingWebSocket(meetingId);

    const fetchBotStatus = async () => {
        try {
            const response = await fetch(`/api/v1/meetings/${meetingId}/bot/status`);

            if (response.ok) {
                const data = await response.json();
                setBotSession(data);
            } else if (response.status === 404) {
                // No bot session exists
                setBotSession(null);
            }
        } catch (error) {
            console.error('Failed to fetch bot status:', error);
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) {
        return (
            <div className="space-y-4">
                <Skeleton className="h-32 w-full" />
                <Skeleton className="h-24 w-full" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Bot Overview Card */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle>Recording Bot</CardTitle>
                            <CardDescription>
                                Automated meeting bot for recording and transcription
                            </CardDescription>
                        </div>

                        {/* Connection Status */}
                        <div className="flex items-center gap-2 text-sm">
                            <div
                                className={`
                  h-2 w-2 rounded-full
                  ${ws?.isConnected ? 'bg-green-500' : 'bg-gray-300'}
                `}
                            />
                            <span className="text-gray-500">
                                {ws?.isConnected ? 'Live' : 'Disconnected'}
                            </span>
                        </div>
                    </div>
                </CardHeader>

                <CardContent className="space-y-4">
                    {/* Bot Status */}
                    {botSession ? (
                        <div className="space-y-4">
                            <div>
                                <div className="text-sm font-medium text-gray-700 mb-2">Status</div>
                                <BotStatus
                                    status={botSession.status as any}
                                    participantCount={botSession.participant_count}
                                    isAlone={botSession.is_alone}
                                    error={botSession.error}
                                />
                            </div>

                            {/* Platform Info */}
                            {botSession.platform && (
                                <div>
                                    <div className="text-sm font-medium text-gray-700 mb-1">Platform</div>
                                    <div className="text-sm capitalize">{botSession.platform.replace('_', ' ')}</div>
                                </div>
                            )}

                            {/* Joined/Left Times */}
                            {botSession.joined_at && (
                                <div className="grid grid-cols-2 gap-4 text-sm">
                                    <div>
                                        <div className="text-gray-500">Joined</div>
                                        <div className="font-medium">
                                            {new Date(botSession.joined_at).toLocaleTimeString()}
                                        </div>
                                    </div>

                                    {botSession.left_at && (
                                        <div>
                                            <div className="text-gray-500">Left</div>
                                            <div className="font-medium">
                                                {new Date(botSession.left_at).toLocaleTimeString()}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="text-sm text-gray-500">
                            No bot is currently assigned to this meeting.
                        </div>
                    )}

                    {/* Bot Controls */}
                    <div className="pt-4 border-t">
                        <BotControls
                            meetingId={meetingId}
                            botStatus={botSession?.status || null}
                            onBotStarted={fetchBotStatus}
                            onBotStopped={fetchBotStatus}
                        />
                    </div>
                </CardContent>
            </Card>

            {/* Live Recording Card */}
            {botSession && ['in_meeting', 'recording', 'completed'].includes(botSession.status) && (
                <LiveRecording
                    botStatus={botSession.status}
                    participantCount={botSession.participant_count}
                    isAlone={botSession.is_alone}
                    joinedAt={botSession.joined_at}
                    recordingUrl={botSession.recording_url}
                />
            )}

            {/* How It Works */}
            {!botSession && (
                <Card>
                    <CardHeader>
                        <CardTitle className="text-base">How It Works</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ol className="list-decimal list-inside space-y-2 text-sm text-gray-600">
                            <li>Click "Start Bot" to send a bot to your meeting</li>
                            <li>The bot will join automatically and start recording</li>
                            <li>Recording is uploaded to cloud storage when complete</li>
                            <li>Transcription begins automatically after recording</li>
                            <li>You can stop the bot at any time</li>
                        </ol>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}