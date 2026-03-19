"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useZoomAuth } from "../../../hooks/useZoomAuth";
import { toast } from "sonner";

export default function ZoomCallbackPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { handleZoomCallback } = useZoomAuth();
    const [isProcessing, setIsProcessing] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const processCallback = async () => {
            try {
                // Get authorization code from URL
                const code = searchParams.get("code");
                const state = searchParams.get("state");

                // Handle error from Zoom
                const errorParam = searchParams.get("error");
                if (errorParam) {
                    const errorDescription = searchParams.get("error_description") || errorParam;
                    throw new Error(`Zoom error: ${errorDescription}`);
                }

                if (!code) {
                    throw new Error("Authorization code not found in callback URL");
                }

                // Process the callback
                await handleZoomCallback(code);
            } catch (err) {
                const message = err instanceof Error ? err.message : "Failed to process Zoom callback";
                setError(message);
                toast.error(message);
                console.error("Zoom callback error:", err);
                
                // Redirect to login after delay
                setTimeout(() => {
                    router.push("/login");
                }, 2000);
            } finally {
                setIsProcessing(false);
            }
        };

        processCallback();
    }, [searchParams, handleZoomCallback, router]);

    if (isProcessing) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mb-4"></div>
                    <p className="text-gray-600">Authenticating with Zoom...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center max-w-md">
                    <div className="text-red-500 text-xl mb-2">✕</div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">Authentication Failed</h1>
                    <p className="text-gray-600 mb-6">{error}</p>
                    <p className="text-sm text-gray-500">Redirecting to login...</p>
                </div>
            </div>
        );
    }

    // Should not reach here as handleZoomCallback redirects on success
    return null;
}
