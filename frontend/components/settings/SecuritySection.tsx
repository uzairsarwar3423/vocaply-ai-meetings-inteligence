"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { KeyRound, ShieldCheck, Smartphone, Laptop, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

export function SecuritySection() {
    const [isLoading, setIsLoading] = useState(false);

    const handleSave = () => {
        setIsLoading(true);
        setTimeout(() => {
            setIsLoading(false);
            toast.success("Security settings updated");
        }, 800);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="space-y-8"
        >
            <div>
                <h3 className="text-xl font-bold font-outfit">Security & Privacy</h3>
                <p className="text-sm text-neutral-500 mt-1">Manage your account security and authentication methods.</p>
            </div>

            <div className="bg-white rounded-2xl border border-neutral-100 shadow-sm overflow-hidden">
                {/* Change Password */}
                <div className="p-6 space-y-6">
                    <div className="flex items-center gap-3 border-b border-neutral-100 pb-4">
                        <div className="w-8 h-8 rounded-lg bg-neutral-100 flex items-center justify-center text-neutral-700">
                            <KeyRound className="w-4 h-4" />
                        </div>
                        <div>
                            <h4 className="font-medium">Change Password</h4>
                            <p className="text-sm text-neutral-500">Update your account password.</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="current-pwd">Current Password</Label>
                                <Input id="current-pwd" type="password" placeholder="••••••••" className="h-11 border-neutral-200" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="new-pwd">New Password</Label>
                                <Input id="new-pwd" type="password" placeholder="••••••••" className="h-11 border-neutral-200" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="confirm-pwd">Confirm New Password</Label>
                                <Input id="confirm-pwd" type="password" placeholder="••••••••" className="h-11 border-neutral-200" />
                            </div>
                            <Button className="bg-neutral-900 hover:bg-black text-white w-full sm:w-auto mt-2">
                                Update Password
                            </Button>
                        </div>

                        <div className="bg-neutral-50 p-6 rounded-xl border border-neutral-100">
                            <h5 className="font-medium mb-3 flex items-center gap-2">
                                <ShieldCheck className="w-4 h-4 text-primary" />
                                Password Requirements
                            </h5>
                            <ul className="text-sm text-neutral-600 space-y-2 list-disc pl-5">
                                <li>Minimum 8 characters long</li>
                                <li>At least one uppercase character</li>
                                <li>At least one number</li>
                                <li>At least one special character</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <hr className="border-neutral-100" />

                {/* Two-Factor Authentication */}
                <div className="p-6">
                    <div className="bg-primary/5 border border-primary/20 rounded-xl p-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary shrink-0">
                                <Smartphone className="w-5 h-5" />
                            </div>
                            <div>
                                <h4 className="font-bold text-lg mb-1">Two-Factor Authentication</h4>
                                <p className="text-sm text-neutral-600 max-w-md">
                                    Add an extra layer of security to your account. We'll ask for an authentication code when you sign in from a new device.
                                </p>
                            </div>
                        </div>
                        <Button className="bg-primary hover:bg-primary-600 text-white shrink-0 shadow-primary">
                            Enable 2FA
                        </Button>
                    </div>
                </div>

                <hr className="border-neutral-100" />

                {/* Active Sessions */}
                <div className="p-6 space-y-6">
                    <div className="flex items-center justify-between border-b border-neutral-100 pb-4">
                        <div>
                            <h4 className="font-medium">Active Sessions</h4>
                            <p className="text-sm text-neutral-500">Manage devices where you're currently logged in.</p>
                        </div>
                        <Button variant="outline" className="text-error hover:text-error hover:bg-error/5 border-neutral-200">
                            Log out all devices
                        </Button>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 rounded-xl border border-primary/20 bg-primary/5">
                            <div className="flex items-start gap-4">
                                <div className="mt-1 text-primary">
                                    <Laptop className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="font-medium text-primary-900 flex items-center gap-2">
                                        MacBook Pro - Chrome
                                        <span className="text-[10px] font-bold uppercase tracking-wider bg-primary text-white px-2 py-0.5 rounded-full">Current</span>
                                    </p>
                                    <div className="flex items-center gap-3 mt-1 text-xs text-neutral-500">
                                        <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> Active now</span>
                                        <span>•</span>
                                        <span>San Francisco, CA</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-between p-4 rounded-xl border border-neutral-100 bg-white">
                            <div className="flex items-start gap-4">
                                <div className="mt-1 text-neutral-400">
                                    <Smartphone className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="font-medium">iPhone 13 - Safari</p>
                                    <div className="flex items-center gap-3 mt-1 text-xs text-neutral-500">
                                        <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> Last active 2h ago</span>
                                        <span>•</span>
                                        <span>San Francisco, CA</span>
                                    </div>
                                </div>
                            </div>
                            <Button variant="ghost" size="sm" className="text-sm">Log out</Button>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
