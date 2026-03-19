'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { ExternalLink, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/useToast';
import { apiClient } from '@/lib/api/client';

interface OAuthConnectProps {
    platform: 'zoom' | 'google' | 'microsoft' | 'slack';
    platformName: string;
    onConnect: (platform: string) => void;
}

export default function OAuthConnect({
    platform,
    platformName,
    onConnect,
}: OAuthConnectProps) {
    const [isConnecting, setIsConnecting] = useState(false);
    const { toast } = useToast();

    const handleConnect = async () => {
        setIsConnecting(true);

        try {
            // Get OAuth URL from backend
            const response = await apiClient.get(`/integrations/${platform}/connect`);

            const data = response.data;

            // Store state for verification after redirect
            sessionStorage.setItem('oauth_state', data.state);
            sessionStorage.setItem('oauth_platform', platform);

            // Redirect to OAuth provider
            window.location.href = data.authorization_url;
        } catch (error) {
            console.error('Connection error:', error);

            toast({
                title: 'Connection Failed',
                description: `Failed to connect ${platformName}. Please try again.`,
                variant: 'destructive',
            });

            setIsConnecting(false);
        }
    };

    return (
        <Button
            onClick={handleConnect}
            disabled={isConnecting}
            className="w-full gap-2"
        >
            {isConnecting ? (
                <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Connecting...
                </>
            ) : (
                <>
                    <ExternalLink className="h-4 w-4" />
                    Connect {platformName}
                </>
            )}
        </Button>
    );
}