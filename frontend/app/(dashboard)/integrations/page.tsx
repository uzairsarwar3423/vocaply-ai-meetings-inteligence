'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import IntegrationCard from '@/components/integrations/IntegrationCard/IntegrationCard';
import { Loader2, Video, Calendar, Mail, Link2, Puzzle, Bot, HelpCircle, ShieldCheck, Info, Slack } from 'lucide-react';
import { apiClient } from '@/lib/api/client';

interface Integration {
    id: string;
    name: string;
    platform: 'zoom' | 'google' | 'microsoft' | 'slack';
    description: string;
    icon: React.ReactNode;
    connected: boolean;
    connectedAt?: string;
    userEmail?: string;
}

export default function IntegrationsPage() {
    const [integrations, setIntegrations] = useState<Integration[]>([
        {
            id: 'zoom',
            name: 'Zoom',
            platform: 'zoom',
            description: 'Connect your Zoom account to import meetings and enable auto-recording',
            icon: <Video className="h-8 w-8 text-blue-600" />,
            connected: false,
        },
        {
            id: 'google',
            name: 'Google Meet & Calendar',
            platform: 'google',
            description: 'Sync your Google Calendar and auto-join Google Meet meetings',
            icon: <Calendar className="h-8 w-8 text-red-500" />,
            connected: false,
        },
        {
            id: 'microsoft',
            name: 'Teams & Outlook',
            platform: 'microsoft',
            description: 'Connect Microsoft Teams and Outlook Calendar',
            icon: <Mail className="h-8 w-8 text-blue-500" />,
            connected: false,
        },
        {
            id: 'slack',
            name: 'Slack',
            platform: 'slack',
            description: 'Get action item notifications and meeting summaries directly in Slack',
            icon: <Slack className="h-8 w-8 text-purple-700" />,
            connected: false,
        },
    ]);

    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        fetchConnections();
    }, []);

    const fetchConnections = async () => {
        try {
            const response = await apiClient.get('/integrations/connections');
            const data = response.data;

            // Update integration status
            setIntegrations(prev =>
                prev.map(integration => {
                    const connection = data.connections.find(
                        (c: any) => c.platform === integration.platform
                    );

                    if (connection) {
                        return {
                            ...integration,
                            connected: connection.is_active,
                            connectedAt: connection.connected_at,
                            userEmail: connection.platform_email,
                        };
                    }

                    return integration;
                })
            );
        } catch (error) {
            console.error('Failed to fetch connections:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleConnect = (platform: string) => {
        fetchConnections();
    };

    const handleDisconnect = (platform: string) => {
        fetchConnections();
    };

    if (isLoading) {
        return (
            <div className="container max-w-6xl mx-auto py-8 px-4">
                <div className="flex items-center justify-center h-64">
                    <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                </div>
            </div>
        );
    }

    return (
        <div className="container max-w-6xl mx-auto py-8 px-4">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Integrations</h1>
                <p className="text-gray-600">
                    Connect your meeting platforms to enable automatic recording and transcription
                </p>
            </div>

            {/* Stats */}
            <Card className="mb-8">
                <CardContent className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="flex items-center gap-4">
                            <div className="p-2 bg-blue-50 rounded-lg">
                                <Link2 className="h-5 w-5 text-blue-600" />
                            </div>
                            <div>
                                <div className="text-sm text-gray-600">Connected Platforms</div>
                                <div className="text-2xl font-bold mt-1">
                                    {integrations.filter(i => i.connected).length}
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="p-2 bg-purple-50 rounded-lg">
                                <Puzzle className="h-5 w-5 text-purple-600" />
                            </div>
                            <div>
                                <div className="text-sm text-gray-600">Available Integrations</div>
                                <div className="text-2xl font-bold mt-1">
                                    {integrations.length}
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="p-2 bg-green-50 rounded-lg">
                                <Bot className="h-5 w-5 text-green-600" />
                            </div>
                            <div>
                                <div className="text-sm text-gray-600">Auto-Join Enabled</div>
                                <div className="text-2xl font-bold mt-1">
                                    {integrations.filter(i => i.connected).length > 0 ? 'Yes' : 'No'}
                                </div>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Integration Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {integrations.map((integration) => (
                    <IntegrationCard
                        key={integration.id}
                        integration={integration}
                        onConnect={handleConnect}
                        onDisconnect={handleDisconnect}
                    />
                ))}
            </div>

            {/* Help Section */}
            <Card className="mt-8">
                <CardHeader>
                    <CardTitle className="text-base">Need Help?</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4 text-sm text-gray-600">
                        <div>
                            <div className="font-medium text-gray-900 mb-1 flex items-center gap-2">
                                <HelpCircle className="h-4 w-4 text-blue-500" />
                                How do integrations work?
                            </div>
                            <p>
                                Connect your meeting platforms to automatically import meetings,
                                enable bot attendance, and sync recordings.
                            </p>
                        </div>

                        <div>
                            <div className="font-medium text-gray-900 mb-1 flex items-center gap-2">
                                <ShieldCheck className="h-4 w-4 text-green-500" />
                                What permissions are required?
                            </div>
                            <p>
                                We request read access to your meetings and write access to create
                                meeting bots. We never access personal messages or files.
                            </p>
                        </div>

                        <div>
                            <div className="font-medium text-gray-900 mb-1 flex items-center gap-2">
                                <Info className="h-4 w-4 text-purple-500" />
                                Can I disconnect at any time?
                            </div>
                            <p>
                                Yes! You can disconnect any integration at any time. Your existing
                                recordings and transcripts will remain available.
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}