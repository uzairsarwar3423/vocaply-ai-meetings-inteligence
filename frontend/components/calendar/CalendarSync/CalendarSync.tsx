'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar, Loader2, Check, AlertCircle } from 'lucide-react';
import { useToast } from '@/hooks/useToast';
import { Badge } from '@/components/ui/badge';

interface CalendarProvider {
    id: 'google' | 'outlook';
    name: string;
    icon: string;
    connected: boolean;
    lastSyncedAt?: string;
}

interface CalendarSyncProps {
    onSyncComplete?: () => void;
}

export default function CalendarSync({ onSyncComplete }: CalendarSyncProps) {
    const [isSyncing, setIsSyncing] = useState(false);
    const [providers, setProviders] = useState<CalendarProvider[]>([
        { id: 'google', name: 'Google Calendar', icon: '📅', connected: false },
        { id: 'outlook', name: 'Outlook Calendar', icon: '📧', connected: false },
    ]);
    const { toast } = useToast();

    const handleConnect = async (providerId: 'google' | 'outlook') => {
        // In production, this would trigger OAuth flow
        if (providerId === 'google') {
            // Redirect to Google OAuth
            const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
            const redirectUri = `${window.location.origin}/api/auth/google/callback`;
            const scope = 'https://www.googleapis.com/auth/calendar.readonly';

            const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
                `client_id=${clientId}&` +
                `redirect_uri=${redirectUri}&` +
                `response_type=code&` +
                `scope=${scope}&` +
                `access_type=offline&` +
                `prompt=consent`;

            window.location.href = authUrl;
        } else {
            toast({
                title: 'Coming Soon',
                description: 'Outlook integration is coming soon!',
            });
        }
    };

    const handleSync = async (providerId: 'google' | 'outlook') => {
        setIsSyncing(true);

        try {
            const response = await fetch('/api/v1/calendar/sync', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    provider: providerId,
                    days_ahead: 7,
                }),
            });

            if (!response.ok) {
                throw new Error('Sync failed');
            }

            const data = await response.json();

            toast({
                title: 'Sync Complete',
                description: `Synced ${data.synced_count} events from ${providerId === 'google' ? 'Google Calendar' : 'Outlook'}`,
            });

            // Update provider status
            setProviders(prev =>
                prev.map(p =>
                    p.id === providerId
                        ? { ...p, lastSyncedAt: new Date().toISOString() }
                        : p
                )
            );

            onSyncComplete?.();
        } catch (error) {
            console.error('Sync error:', error);

            toast({
                title: 'Sync Failed',
                description: 'Failed to sync calendar. Please try again.',
                variant: 'destructive',
            });
        } finally {
            setIsSyncing(false);
        }
    };

    const handleDisconnect = async (providerId: 'google' | 'outlook') => {
        // In production, revoke OAuth token
        setProviders(prev =>
            prev.map(p =>
                p.id === providerId
                    ? { ...p, connected: false, lastSyncedAt: undefined }
                    : p
            )
        );

        toast({
            title: 'Disconnected',
            description: `${providerId === 'google' ? 'Google Calendar' : 'Outlook'} has been disconnected.`,
        });
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Calendar className="h-5 w-5" />
                    Calendar Integration
                </CardTitle>
                <CardDescription>
                    Connect your calendar to automatically sync meetings and enable auto-join
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
                {providers.map((provider) => (
                    <div
                        key={provider.id}
                        className="flex items-center justify-between p-4 border rounded-lg"
                    >
                        <div className="flex items-center gap-3">
                            <div className="text-2xl">{provider.icon}</div>
                            <div>
                                <div className="font-medium flex items-center gap-2">
                                    {provider.name}
                                    {provider.connected && (
                                        <Badge variant="neutral" className="gap-1">
                                            <Check className="h-3 w-3" />
                                            Connected
                                        </Badge>
                                    )}
                                </div>
                                {provider.lastSyncedAt && (
                                    <div className="text-sm text-gray-500">
                                        Last synced: {new Date(provider.lastSyncedAt).toLocaleString()}
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="flex items-center gap-2">
                            {provider.connected ? (
                                <>
                                    <Button
                                        onClick={() => handleSync(provider.id)}
                                        disabled={isSyncing}
                                        variant="outline"
                                        size="sm"
                                    >
                                        {isSyncing ? (
                                            <>
                                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                                Syncing...
                                            </>
                                        ) : (
                                            'Sync Now'
                                        )}
                                    </Button>
                                    <Button
                                        onClick={() => handleDisconnect(provider.id)}
                                        variant="ghost"
                                        size="sm"
                                    >
                                        Disconnect
                                    </Button>
                                </>
                            ) : (
                                <Button
                                    onClick={() => handleConnect(provider.id)}
                                    size="sm"
                                >
                                    Connect
                                </Button>
                            )}
                        </div>
                    </div>
                ))}

                {/* Info Box */}
                <div className="flex gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div className="text-sm text-blue-900">
                        <div className="font-medium mb-1">What happens when you connect?</div>
                        <ul className="list-disc list-inside space-y-1 text-blue-800">
                            <li>We'll sync your upcoming meetings (next 7 days)</li>
                            <li>Meeting URLs (Zoom, Meet, Teams) will be detected automatically</li>
                            <li>You can enable auto-join for any meeting</li>
                            <li>Calendar syncs every 15 minutes</li>
                        </ul>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}