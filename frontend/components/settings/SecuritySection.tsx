"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { KeyRound, ShieldCheck, Smartphone, Laptop, Clock, Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { usersApi } from "@/lib/api/users";
import { toast } from "sonner";

export function SecuritySection() {
    const [isLoading, setIsLoading] = useState(false);
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showCurrent, setShowCurrent] = useState(false);
    const [showNew, setShowNew] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);

    const handlePasswordChange = async () => {
        if (!currentPassword || !newPassword || !confirmPassword) {
            toast.error("Please fill in all password fields");
            return;
        }
        if (newPassword !== confirmPassword) {
            toast.error("New passwords do not match");
            return;
        }
        if (newPassword.length < 8) {
            toast.error("New password must be at least 8 characters");
            return;
        }

        setIsLoading(true);
        try {
            await usersApi.changePassword({
                current_password: currentPassword,
                new_password: newPassword,
            });
            toast.success("Password updated successfully");
            setCurrentPassword("");
            setNewPassword("");
            setConfirmPassword("");
        } catch (err: unknown) {
            const message =
                (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
                "Failed to update password";
            toast.error(message);
        } finally {
            setIsLoading(false);
        }
    };

    const passwordStrength = () => {
        if (!newPassword) return null;
        const checks = [
            newPassword.length >= 8,
            /[A-Z]/.test(newPassword),
            /[0-9]/.test(newPassword),
            /[^A-Za-z0-9]/.test(newPassword),
        ];
        const passed = checks.filter(Boolean).length;
        if (passed <= 1) return { label: "Weak", color: "bg-red-500", width: "w-1/4" };
        if (passed === 2) return { label: "Fair", color: "bg-orange-500", width: "w-2/4" };
        if (passed === 3) return { label: "Good", color: "bg-yellow-500", width: "w-3/4" };
        return { label: "Strong", color: "bg-green-500", width: "w-full" };
    };

    const strength = passwordStrength();

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
                                <div className="relative">
                                    <Input
                                        id="current-pwd"
                                        type={showCurrent ? "text" : "password"}
                                        placeholder="••••••••"
                                        value={currentPassword}
                                        onChange={(e) => setCurrentPassword(e.target.value)}
                                        className="h-11 border-neutral-200 pr-10"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowCurrent(!showCurrent)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
                                    >
                                        {showCurrent ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                    </button>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="new-pwd">New Password</Label>
                                <div className="relative">
                                    <Input
                                        id="new-pwd"
                                        type={showNew ? "text" : "password"}
                                        placeholder="••••••••"
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                        className="h-11 border-neutral-200 pr-10"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowNew(!showNew)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
                                    >
                                        {showNew ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                    </button>
                                </div>
                                {strength && (
                                    <div className="space-y-1">
                                        <div className="h-1.5 bg-neutral-100 rounded-full overflow-hidden">
                                            <div className={`h-full rounded-full transition-all ${strength.color} ${strength.width}`} />
                                        </div>
                                        <p className="text-xs text-neutral-500">Strength: <span className="font-medium">{strength.label}</span></p>
                                    </div>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="confirm-pwd">Confirm New Password</Label>
                                <div className="relative">
                                    <Input
                                        id="confirm-pwd"
                                        type={showConfirm ? "text" : "password"}
                                        placeholder="••••••••"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                        className={`h-11 border-neutral-200 pr-10 ${confirmPassword && confirmPassword !== newPassword
                                                ? "border-red-400 focus:ring-red-300"
                                                : ""
                                            }`}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowConfirm(!showConfirm)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
                                    >
                                        {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                    </button>
                                </div>
                                {confirmPassword && confirmPassword !== newPassword && (
                                    <p className="text-xs text-red-500">Passwords do not match</p>
                                )}
                            </div>

                            <Button
                                onClick={handlePasswordChange}
                                disabled={isLoading}
                                className="bg-neutral-900 hover:bg-black text-white w-full sm:w-auto mt-2"
                            >
                                {isLoading ? (
                                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                ) : (
                                    "Update Password"
                                )}
                            </Button>
                        </div>

                        <div className="bg-neutral-50 p-6 rounded-xl border border-neutral-100">
                            <h5 className="font-medium mb-3 flex items-center gap-2">
                                <ShieldCheck className="w-4 h-4 text-primary" />
                                Password Requirements
                            </h5>
                            <ul className="text-sm text-neutral-600 space-y-2">
                                {[
                                    { text: "Minimum 8 characters long", met: newPassword.length >= 8 },
                                    { text: "At least one uppercase character", met: /[A-Z]/.test(newPassword) },
                                    { text: "At least one number", met: /[0-9]/.test(newPassword) },
                                    { text: "At least one special character", met: /[^A-Za-z0-9]/.test(newPassword) },
                                ].map(({ text, met }) => (
                                    <li key={text} className={`flex items-center gap-2 ${newPassword ? (met ? "text-green-600" : "text-neutral-400") : ""}`}>
                                        <span className={`w-1.5 h-1.5 rounded-full ${newPassword ? (met ? "bg-green-500" : "bg-neutral-300") : "bg-neutral-400"}`} />
                                        {text}
                                    </li>
                                ))}
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
                        <Button
                            onClick={() => toast.info("2FA setup coming soon!")}
                            className="bg-primary hover:bg-primary-600 text-white shrink-0 shadow-primary"
                        >
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
                        <Button
                            variant="outline"
                            className="text-red-500 hover:text-red-600 hover:bg-red-50 border-neutral-200"
                            onClick={() => toast.info("Session management coming soon!")}
                        >
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
                                        Current Browser
                                        <span className="text-[10px] font-bold uppercase tracking-wider bg-primary text-white px-2 py-0.5 rounded-full">Current</span>
                                    </p>
                                    <div className="flex items-center gap-3 mt-1 text-xs text-neutral-500">
                                        <span className="flex items-center gap-1">
                                            <Clock className="w-3 h-3" /> Active now
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
