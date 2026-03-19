/**
 * Example Zoom OAuth Login Component
 * Shows how to integrate Zoom sign-in button into your login page
 */

"use client";

import { useState } from "react";
import Link from "next/link";
import { useZoomAuth } from "@/hooks/useZoomAuth";
import { toast } from "sonner";

export function ZoomLoginExample() {
    const { initiateZoomLogin } = useZoomAuth();
    const [isLoading, setIsLoading] = useState(false);

    const handleZoomLogin = async () => {
        try {
            setIsLoading(true);
            initiateZoomLogin();
        } catch (error) {
            toast.error("Failed to initiate Zoom login");
            console.error("Zoom login error:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
            <div className="w-full max-w-md">
                <div className="bg-white py-8 px-6 shadow rounded-lg sm:px-10">
                    <h2 className="text-center text-3xl font-extrabold text-gray-900 mb-6">
                        Sign in to Vocaply
                    </h2>

                    {/* Zoom Sign In Button */}
                    <button
                        onClick={handleZoomLogin}
                        disabled={isLoading}
                        className="w-full flex justify-center items-center gap-2 px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? (
                            <>
                                <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                                <span>Connecting...</span>
                            </>
                        ) : (
                            <>
                                <svg
                                    className="w-5 h-5"
                                    fill="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    {/* Zoom Logo */}
                                    <path d="M11.5 0C5.1 0 0 3.5 0 7.75s5.1 7.75 11.5 7.75 11.5-3.5 11.5-7.75S17.9 0 11.5 0zm0 14c-5.2 0-9.5-2.8-9.5-6.25S6.3 1.5 11.5 1.5 21 4.3 21 7.75 16.7 14 11.5 14z" />
                                </svg>
                                <span>Sign in with Zoom</span>
                            </>
                        )}
                    </button>

                    {/* Divider */}
                    <div className="mt-6 relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-gray-300"></div>
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-2 bg-white text-gray-500">Or continue with email</span>
                        </div>
                    </div>

                    {/* Traditional Login Link */}
                    <div className="mt-6">
                        <Link
                            href="/login"
                            className="w-full flex justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
                        >
                            Sign in with Email
                        </Link>
                    </div>

                    {/* Sign Up Link */}
                    <p className="text-center text-sm text-gray-600 mt-4">
                        Don't have an account?{" "}
                        <Link href="/register" className="font-medium text-blue-600 hover:text-blue-500">
                            Sign up
                        </Link>
                    </p>
                </div>

                {/* Info Box */}
                <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-blue-900 mb-2">What is Zoom OAuth?</h3>
                    <p className="text-sm text-blue-700">
                        Sign in using your Zoom account. Your Zoom credentials are never shared with us - only your basic profile information.
                    </p>
                </div>
            </div>
        </div>
    );
}

export default ZoomLoginExample;
