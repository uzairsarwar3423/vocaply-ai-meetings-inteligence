'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Play, Square, Loader2, AlertCircle } from 'lucide-react';
import { useToast } from '@/hooks/useToast';
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from '@/components/ui/AlertDialog';

interface BotControlsProps {
    meetingId: string;
    botStatus: string | null;
    onBotStarted?: () => void;
    onBotStopped?: () => void;
}

export default function BotControls({
    meetingId,
    botStatus,
    onBotStarted,
    onBotStopped,
}: BotControlsProps) {
    const [isStarting, setIsStarting] = useState(false);
    const [isStopping, setIsStopping] = useState(false);
    const [showStopDialog, setShowStopDialog] = useState(false);
    const { toast } = useToast();

    const isActive = botStatus && ['assigned', 'joining', 'in_meeting', 'recording'].includes(botStatus);
    const canStart = !botStatus || ['completed', 'failed', 'terminated'].includes(botStatus);
    const canStop = isActive;

    const handleStartBot = async () => {
        setIsStarting(true);

        try {
            const response = await fetch(`/api/v1/meetings/${meetingId}/bot/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to start bot');
            }

            const data = await response.json();

            toast({
                title: 'Bot Started',
                description: `Bot is joining the meeting. Platform: ${data.platform}`,
            });

            onBotStarted?.();
        } catch (error) {
            console.error('Failed to start bot:', error);

            toast({
                title: 'Error',
                description: error instanceof Error ? error.message : 'Failed to start bot',
                variant: 'destructive',
            });
        } finally {
            setIsStarting(false);
        }
    };

    const handleStopBot = async () => {
        setIsStopping(true);
        setShowStopDialog(false);

        try {
            const response = await fetch(`/api/v1/meetings/${meetingId}/bot/stop`, {
                method: 'POST',
            });

            if (!response.ok) {
                throw new Error('Failed to stop bot');
            }

            toast({
                title: 'Bot Stopped',
                description: 'The bot is leaving the meeting.',
            });

            onBotStopped?.();
        } catch (error) {
            console.error('Failed to stop bot:', error);

            toast({
                title: 'Error',
                description: 'Failed to stop bot',
                variant: 'destructive',
            });
        } finally {
            setIsStopping(false);
        }
    };

    return (
        <>
            <div className="flex items-center gap-2">
                {canStart && (
                    <Button
                        onClick={handleStartBot}
                        disabled={isStarting}
                        className="gap-2"
                    >
                        {isStarting ? (
                            <>
                                <Loader2 className="h-4 w-4 animate-spin" />
                                Starting Bot...
                            </>
                        ) : (
                            <>
                                <Play className="h-4 w-4" />
                                Start Bot
                            </>
                        )}
                    </Button>
                )}

                {canStop && (
                    <Button
                        onClick={() => setShowStopDialog(true)}
                        disabled={isStopping}
                        variant="outline"
                        className="gap-2"
                    >
                        {isStopping ? (
                            <>
                                <Loader2 className="h-4 w-4 animate-spin" />
                                Stopping...
                            </>
                        ) : (
                            <>
                                <Square className="h-4 w-4" />
                                Stop Bot
                            </>
                        )}
                    </Button>
                )}

                {botStatus === 'failed' && (
                    <div className="flex items-center gap-2 text-sm text-red-600">
                        <AlertCircle className="h-4 w-4" />
                        <span>Bot failed to join</span>
                    </div>
                )}
            </div>

            {/* Stop Confirmation Dialog */}
            <AlertDialog open={showStopDialog} onOpenChange={setShowStopDialog}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Stop Recording Bot?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This will make the bot leave the meeting and stop recording.
                            Any recording in progress will be saved and processed.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={handleStopBot}>
                            Stop Bot
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </>
    );
}