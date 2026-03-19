'use client';

import { useEffect, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/useToast';
import { apiClient } from '@/lib/api/client';

export default function SlackCallbackPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { toast } = useToast();
    const hasProcessed = useRef(false);

    useEffect(() => {
        const handleCallback = async () => {
            if (hasProcessed.current) return;
            hasProcessed.current = true;

            const code = searchParams.get('code');
            const state = searchParams.get('state');

            if (!code) {
                toast({
                    title: 'OAuth Error',
                    description: 'No authorization code received from Slack.',
                    variant: 'destructive',
                });
                router.push('/integrations');
                return;
            }

            try {
                await apiClient.get(`/integrations/slack/callback?code=${code}&state=${state}`);

                toast({
                    title: 'Success!',
                    description: 'Slack account connected successfully.',
                });
                router.push('/integrations');
            } catch (error: any) {
                console.error('Slack callback error:', error);
                const errorMessage = error.response?.data?.detail || 'An error occurred during Slack connection.';

                toast({
                    title: 'Connection Failed',
                    description: errorMessage,
                    variant: 'destructive',
                });
                router.push('/integrations');
            }
        };

        handleCallback();
    }, [router, searchParams, toast]);

    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh]">
            <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
            <h2 className="text-xl font-semibold mb-2">Connecting to Slack...</h2>
            <p className="text-neutral-500">Please wait while we finalize your account connection.</p>
        </div>
    );
}
