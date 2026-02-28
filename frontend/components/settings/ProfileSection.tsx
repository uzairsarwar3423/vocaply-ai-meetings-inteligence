"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Upload, Mail, User, Shield, Camera } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/store/authStore";
import { toast } from "sonner";

export function ProfileSection() {
    const { user } = useAuthStore();
    const [isLoading, setIsLoading] = useState(false);

    const handleSave = () => {
        setIsLoading(true);
        setTimeout(() => {
            setIsLoading(false);
            toast.success("Profile updated successfully");
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
                <h3 className="text-xl font-bold font-outfit">Profile Information</h3>
                <p className="text-sm text-neutral-500 mt-1">Update your personal details and public profile.</p>
            </div>

            <div className="bg-white rounded-2xl border border-neutral-100 p-6 shadow-sm space-y-8">
                {/* Avatar upload */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6 pb-6 border-b border-neutral-100">
                    <div className="relative group">
                        <div className="w-24 h-24 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-3xl overflow-hidden border-2 border-primary/20">
                            {user?.full_name?.[0] || 'U'}
                            <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
                                <Camera className="w-8 h-8 text-white" />
                            </div>
                        </div>
                    </div>
                    <div>
                        <h4 className="font-medium mb-1">Profile Photo</h4>
                        <p className="text-sm text-neutral-500 mb-3">Recommended size 256x256px. Max 2MB.</p>
                        <div className="flex gap-3">
                            <Button variant="outline" size="sm" className="gap-2 border-neutral-200">
                                <Upload className="w-4 h-4" />
                                Upload new
                            </Button>
                            <Button variant="ghost" size="sm" className="text-error hover:text-error hover:bg-error/5">
                                Remove
                            </Button>
                        </div>
                    </div>
                </div>

                {/* Form fields */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                        <Label htmlFor="fullName" className="text-neutral-700">Full Name</Label>
                        <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                            <Input
                                id="fullName"
                                defaultValue={user?.full_name || ''}
                                className="pl-10 border-neutral-200 focus:border-primary focus:ring-primary/20 h-11"
                            />
                        </div>
                    </div>

                    <div className="space-y-3">
                        <Label htmlFor="email" className="text-neutral-700">Email Address</Label>
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                            <Input
                                id="email"
                                type="email"
                                defaultValue={user?.email || ''}
                                disabled
                                className="pl-10 bg-neutral-50 border-neutral-200 h-11 text-neutral-500"
                            />
                        </div>
                        <p className="text-xs text-neutral-500">Contact support to change your email.</p>
                    </div>

                    <div className="space-y-3">
                        <Label htmlFor="role" className="text-neutral-700">Role</Label>
                        <div className="relative">
                            <Shield className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                            <Input
                                id="role"
                                defaultValue={user?.role || 'User'}
                                disabled
                                className="pl-10 bg-neutral-50 border-neutral-200 h-11 text-neutral-500"
                            />
                        </div>
                    </div>
                </div>

                <div className="pt-4 border-t border-neutral-100 flex justify-end">
                    <Button
                        onClick={handleSave}
                        disabled={isLoading}
                        className="bg-primary hover:bg-primary-600 text-white min-w-[120px] transition-all shadow-primary"
                    >
                        {isLoading ? (
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        ) : (
                            "Save Changes"
                        )}
                    </Button>
                </div>
            </div>
        </motion.div>
    );
}
