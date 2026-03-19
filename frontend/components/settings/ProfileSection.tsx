"use client";

import { useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, Mail, User, Shield, Camera, X, Check, ImageIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuthStore } from "@/store/authStore";
import { usersApi } from "@/lib/api/users";
import { toast } from "sonner";

export function ProfileSection() {
    const { user, updateUser } = useAuthStore();
    const [isLoading, setIsLoading] = useState(false);
    const [fullName, setFullName] = useState(user?.full_name || "");

    // Avatar state
    const [avatarPreview, setAvatarPreview] = useState<string | null>(null);
    const [avatarFile, setAvatarFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const currentAvatar = avatarPreview || user?.avatar_url;
    const avatarLetter =
        (user?.full_name?.[0] || user?.email?.[0] || "U").toUpperCase();

    // Convert file to base64 data URL
    const fileToBase64 = (file: File): Promise<string> =>
        new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result as string);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });

    const processFile = useCallback(async (file: File) => {
        if (!file.type.startsWith("image/")) {
            toast.error("Please select an image file (JPG, PNG, GIF, WebP)");
            return;
        }
        if (file.size > 3 * 1024 * 1024) {
            toast.error("Image must be smaller than 3MB");
            return;
        }

        const dataUrl = await fileToBase64(file);
        setAvatarPreview(dataUrl);
        setAvatarFile(file);
    }, []);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) processFile(file);
        // reset so same file can be re-selected
        e.target.value = "";
    };

    const handleDrop = useCallback(
        (e: React.DragEvent) => {
            e.preventDefault();
            setIsDragging(false);
            const file = e.dataTransfer.files?.[0];
            if (file) processFile(file);
        },
        [processFile]
    );

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => setIsDragging(false);

    const handleRemoveAvatar = async () => {
        if (avatarPreview) {
            // Just cancel the pending upload (not yet saved)
            setAvatarPreview(null);
            setAvatarFile(null);
            return;
        }
        // Remove existing saved avatar
        setIsUploadingAvatar(true);
        try {
            const updated = await usersApi.updateProfile({ avatar_url: "" });
            updateUser(updated);
            toast.success("Avatar removed");
        } catch {
            toast.error("Failed to remove avatar");
        } finally {
            setIsUploadingAvatar(false);
        }
    };

    const handleSaveAvatar = async () => {
        if (!avatarFile || !avatarPreview) return;
        setIsUploadingAvatar(true);
        try {
            const updated = await usersApi.updateProfile({ avatar_url: avatarPreview });
            updateUser(updated);
            setAvatarFile(null);
            // Keep preview in sync (it's now saved)
            toast.success("Avatar updated successfully!");
        } catch {
            toast.error("Failed to upload avatar");
        } finally {
            setIsUploadingAvatar(false);
        }
    };

    const handleSaveProfile = async () => {
        setIsLoading(true);
        try {
            // If avatar is pending, upload it first
            if (avatarFile && avatarPreview) {
                await handleSaveAvatar();
            }
            const updated = await usersApi.updateProfile({ full_name: fullName });
            updateUser(updated);
            toast.success("Profile updated successfully");
        } catch (err: unknown) {
            const message =
                (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
                "Failed to update profile";
            toast.error(message);
        } finally {
            setIsLoading(false);
        }
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
                <p className="text-sm text-neutral-500 mt-1">
                    Update your personal details and public profile.
                </p>
            </div>

            <div className="bg-white rounded-2xl border border-neutral-100 p-6 shadow-sm space-y-8">
                {/* ── Avatar Section ── */}
                <div className="flex flex-col sm:flex-row items-start gap-8 pb-8 border-b border-neutral-100">
                    {/* Avatar preview circle */}
                    <div className="relative shrink-0">
                        <div
                            className={`w-28 h-28 rounded-2xl overflow-hidden border-2 transition-all duration-200 flex items-center justify-center text-3xl font-bold cursor-pointer group ${isDragging
                                    ? "border-primary scale-105 ring-4 ring-primary/20"
                                    : "border-neutral-200 hover:border-primary/40"
                                } ${currentAvatar ? "bg-neutral-100" : "bg-primary/10 text-primary"}`}
                            onClick={() => fileInputRef.current?.click()}
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                        >
                            {currentAvatar ? (
                                <img
                                    src={currentAvatar}
                                    alt="Avatar"
                                    className="w-full h-full object-cover"
                                />
                            ) : (
                                avatarLetter
                            )}

                            {/* hover overlay */}
                            <div className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl">
                                <Camera className="w-6 h-6 text-white mb-1" />
                                <span className="text-[10px] text-white font-semibold uppercase tracking-wide">
                                    Change
                                </span>
                            </div>
                        </div>

                        {/* Pending badge */}
                        <AnimatePresence>
                            {avatarFile && (
                                <motion.div
                                    initial={{ scale: 0 }}
                                    animate={{ scale: 1 }}
                                    exit={{ scale: 0 }}
                                    className="absolute -top-2 -right-2 w-6 h-6 bg-orange-500 rounded-full flex items-center justify-center"
                                    title="Unsaved — click Save Changes"
                                >
                                    <span className="text-white text-[10px] font-bold">!</span>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        {/* Hidden file input */}
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            className="hidden"
                            onChange={handleFileChange}
                        />
                    </div>

                    {/* Upload info & actions */}
                    <div className="flex-1 space-y-4">
                        <div>
                            <h4 className="font-semibold text-neutral-800 mb-1">Profile Photo</h4>
                            <p className="text-sm text-neutral-500">
                                JPG, PNG, GIF or WebP · Max 3MB · Recommended 256×256px
                            </p>
                        </div>

                        {/* Upload drop zone */}
                        <div
                            className={`border-2 border-dashed rounded-xl p-5 text-center cursor-pointer transition-all duration-200 ${isDragging
                                    ? "border-primary bg-primary/5"
                                    : "border-neutral-200 hover:border-primary/50 hover:bg-neutral-50/80"
                                }`}
                            onClick={() => fileInputRef.current?.click()}
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                            onDragLeave={handleDragLeave}
                        >
                            <ImageIcon className="w-6 h-6 text-neutral-400 mx-auto mb-2" />
                            <p className="text-sm text-neutral-600 font-medium">
                                Drop your photo here, or{" "}
                                <span className="text-primary underline-offset-2 hover:underline">browse</span>
                            </p>
                            <p className="text-xs text-neutral-400 mt-1">Drag & drop supported</p>
                        </div>

                        {/* Action row */}
                        <div className="flex flex-wrap gap-3">
                            <Button
                                variant="outline"
                                size="sm"
                                className="gap-2 border-neutral-200"
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <Upload className="w-4 h-4" />
                                {currentAvatar ? "Replace photo" : "Upload photo"}
                            </Button>

                            {/* Save avatar immediately */}
                            {avatarFile && (
                                <Button
                                    size="sm"
                                    className="gap-2 bg-primary text-white"
                                    onClick={handleSaveAvatar}
                                    disabled={isUploadingAvatar}
                                >
                                    {isUploadingAvatar ? (
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    ) : (
                                        <Check className="w-4 h-4" />
                                    )}
                                    {isUploadingAvatar ? "Saving…" : "Save Avatar"}
                                </Button>
                            )}

                            {(currentAvatar || avatarPreview) && (
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    className="gap-2 text-red-500 hover:text-red-600 hover:bg-red-50"
                                    onClick={handleRemoveAvatar}
                                    disabled={isUploadingAvatar}
                                >
                                    <X className="w-4 h-4" />
                                    Remove
                                </Button>
                            )}
                        </div>
                    </div>
                </div>

                {/* ── Form fields ── */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-3">
                        <Label htmlFor="fullName" className="text-neutral-700">
                            Full Name
                        </Label>
                        <div className="relative">
                            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                            <Input
                                id="fullName"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                placeholder="Your full name"
                                className="pl-10 border-neutral-200 focus:border-primary focus:ring-primary/20 h-11"
                            />
                        </div>
                    </div>

                    <div className="space-y-3">
                        <Label htmlFor="email" className="text-neutral-700">
                            Email Address
                        </Label>
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                            <Input
                                id="email"
                                type="email"
                                defaultValue={user?.email || ""}
                                disabled
                                className="pl-10 bg-neutral-50 border-neutral-200 h-11 text-neutral-500"
                            />
                        </div>
                        <p className="text-xs text-neutral-500">
                            Contact support to change your email.
                        </p>
                    </div>

                    <div className="space-y-3">
                        <Label htmlFor="role" className="text-neutral-700">
                            Role
                        </Label>
                        <div className="relative">
                            <Shield className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                            <Input
                                id="role"
                                defaultValue={user?.role || "User"}
                                disabled
                                className="pl-10 bg-neutral-50 border-neutral-200 h-11 text-neutral-500 capitalize"
                            />
                        </div>
                    </div>
                </div>

                {/* ── Footer ── */}
                <div className="pt-4 border-t border-neutral-100 flex items-center justify-between">
                    <p className="text-xs text-neutral-400">
                        {avatarFile ? "⚠ You have an unsaved avatar — it will be saved with your profile." : ""}
                    </p>
                    <Button
                        onClick={handleSaveProfile}
                        disabled={isLoading}
                        className="bg-primary hover:bg-primary-600 text-white min-w-[130px] transition-all shadow-primary"
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
