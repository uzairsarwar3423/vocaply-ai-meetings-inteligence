'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, ExternalLink, Loader2, Settings, Unlink } from 'lucide-react';
import OAuthConnect from '../OAuthConnect/OAuthConnect';
import ZoomSettings from '../ZoomSettings/ZoomSettings';
import { Modal } from '@/components/ui/modal';
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

interface IntegrationCardProps {
    integration: Integration;
    onConnect: (platform: string) => void;
    onDisconnect: (platform: string) => void;
}

export default function IntegrationCard({
    integration,
    onConnect,
    onDisconnect,
}: IntegrationCardProps) {
    const [showSettings, setShowSettings] = useState(false);
    const [isDisconnecting, setIsDisconnecting] = useState(false);

    const handleDisconnect = async () => {
        setIsDisconnecting(true);

        try {
            await apiClient.post(`/integrations/${integration.platform}/disconnect`);
            onDisconnect(integration.platform);
        } catch (error) {
            console.error('Failed to disconnect:', error);
        } finally {
            setIsDisconnecting(false);
        }
    };

    return (
        <>
            <Card className={integration.connected ? 'border-green-200 bg-green-50/30' : ''}>
                <CardHeader>
                    <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                            <div>{integration.icon}</div>
                            <div>
                                <CardTitle className="text-base flex items-center gap-2">
                                    {integration.name}
                                    {integration.connected && (
                                        <Badge variant="success" className="gap-1 bg-green-50 border-green-200">
                                            <Check className="h-3 w-3 text-green-600" />
                                            <span className="text-green-700">Connected</span>
                                        </Badge>
                                    )}
                                </CardTitle>
                                {integration.userEmail && (
                                    <div className="text-xs text-gray-500 mt-1">
                                        {integration.userEmail}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </CardHeader>

                <CardContent>
                    <CardDescription className="mb-4">
                        {integration.description}
                    </CardDescription>

                    {integration.connected ? (
                        <div className="space-y-2">
                            <Button
                                onClick={() => setShowSettings(true)}
                                variant="outline"
                                className="w-full gap-2"
                            >
                                <Settings className="h-4 w-4" />
                                Settings
                            </Button>

                            <Button
                                onClick={handleDisconnect}
                                disabled={isDisconnecting}
                                variant="ghost"
                                className="w-full gap-2"
                            >
                                {isDisconnecting ? (
                                    <>
                                        <Loader2 className="h-4 w-4 animate-spin" />
                                        Disconnecting...
                                    </>
                                ) : (
                                    <>
                                        <Unlink className="h-4 w-4" />
                                        Disconnect
                                    </>
                                )}
                            </Button>
                        </div>
                    ) : (
                        <OAuthConnect
                            platform={integration.platform}
                            platformName={integration.name}
                            onConnect={onConnect}
                        />
                    )}

                    {integration.connectedAt && (
                        <div className="mt-4 pt-4 border-t text-xs text-gray-500">
                            Connected {new Date(integration.connectedAt).toLocaleDateString()}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Settings Modal */}
            <Modal
                isOpen={showSettings}
                onClose={() => setShowSettings(false)}
                title={`${integration.name} Settings`}
                description={`Configure your ${integration.name} integration`}
            >
                {integration.platform === 'zoom' && (
                    <ZoomSettings onClose={() => setShowSettings(false)} />
                )}

                {/* Add Google/Microsoft settings components here */}
            </Modal>
        </>
    );
}