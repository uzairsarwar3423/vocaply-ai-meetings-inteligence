"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Moon, Sun, Monitor, Globe, Clock, Volume2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { useAuthStore } from "@/store/authStore";
import { usersApi } from "@/lib/api/users";
import { toast } from "sonner";

export function PreferencesSection() {
    const { user, updateUser } = useAuthStore();
    const [isLoading, setIsLoading] = useState(false);

    const [theme, setTheme] = useState<"light" | "dark" | "system">(
        user?.preferences?.theme || "system"
    );
    const [language, setLanguage] = useState(user?.preferences?.language || "en");
    const [timezone, setTimezone] = useState("America/New_York");
    const [autoJoin, setAutoJoin] = useState(user?.preferences?.auto_join_meetings ?? true);

    const handleSave = async () => {
        setIsLoading(true);
        try {
            const updated = await usersApi.updatePreferences({ theme, language, auto_join_meetings: autoJoin });
            updateUser(updated);
            toast.success("Preferences saved successfully");
        } catch (err: unknown) {
            const message =
                (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
                "Failed to save preferences";
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
                <h3 className="text-xl font-bold font-outfit">App Preferences</h3>
                <p className="text-sm text-neutral-500 mt-1">Customize how Vocaply looks and feels.</p>
            </div>

            <div className="bg-white rounded-2xl border border-neutral-100 p-6 shadow-sm space-y-8">
                {/* Theme Selection */}
                <div className="space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                            <Monitor className="w-4 h-4" />
                        </div>
                        <div>
                            <h4 className="font-medium">Appearance</h4>
                            <p className="text-sm text-neutral-500">Select your preferred theme.</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
                        {(["light", "dark", "system"] as const).map((t) => (
                            <button
                                key={t}
                                onClick={() => setTheme(t)}
                                className={`flex flex-col items-center gap-3 p-4 rounded-xl border-2 transition-all ${theme === t ? "border-primary bg-primary/5" : "border-neutral-100 hover:border-neutral-200"
                                    }`}
                            >
                                <div className={`w-12 h-12 rounded-full flex items-center justify-center ${t === "light" ? "bg-neutral-100" : t === "dark" ? "bg-neutral-900" : "bg-gradient-to-br from-neutral-100 to-neutral-800"
                                    }`}>
                                    {t === "light" && <Sun className="w-6 h-6 text-neutral-600" />}
                                    {t === "dark" && <Moon className="w-6 h-6 text-white" />}
                                    {t === "system" && <Monitor className="w-6 h-6 text-neutral-500 mix-blend-difference" />}
                                </div>
                                <span className="font-medium capitalize">{t}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <hr className="border-neutral-100" />

                {/* Regional Settings */}
                <div className="space-y-6">
                    <h4 className="font-medium">Regional Settings</h4>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-3">
                            <Label htmlFor="language" className="text-neutral-700 flex items-center gap-2">
                                <Globe className="w-4 h-4 text-neutral-400" />
                                Language
                            </Label>
                            <select
                                id="language"
                                value={language}
                                onChange={(e) => setLanguage(e.target.value)}
                                className="w-full h-11 px-4 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 appearance-none"
                            >
                                <option value="en">English (US)</option>
                                <option value="es">Spanish</option>
                                <option value="fr">French</option>
                                <option value="de">German</option>
                            </select>
                        </div>

                        <div className="space-y-3">
                            <Label htmlFor="timezone" className="text-neutral-700 flex items-center gap-2">
                                <Clock className="w-4 h-4 text-neutral-400" />
                                Timezone
                            </Label>
                            <select
                                id="timezone"
                                value={timezone}
                                onChange={(e) => setTimezone(e.target.value)}
                                className="w-full h-11 px-4 rounded-xl border border-neutral-200 bg-white focus:outline-none focus:ring-2 focus:ring-primary/20 appearance-none"
                            >
                                <option value="America/New_York">Eastern Time (ET)</option>
                                <option value="America/Chicago">Central Time (CT)</option>
                                <option value="America/Denver">Mountain Time (MT)</option>
                                <option value="America/Los_Angeles">Pacific Time (PT)</option>
                                <option value="Europe/London">London (GMT)</option>
                                <option value="Asia/Karachi">Pakistan Standard Time (PKT)</option>
                            </select>
                        </div>
                    </div>
                </div>

                <hr className="border-neutral-100" />

                {/* Meeting Preferences */}
                <div className="space-y-6">
                    <h4 className="font-medium">Meeting Defaults</h4>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 rounded-xl bg-neutral-50 border border-neutral-100">
                            <div className="flex items-start gap-4">
                                <div className="mt-1 bg-white p-2 rounded-lg border border-neutral-100 text-neutral-500">
                                    <Volume2 className="w-4 h-4" />
                                </div>
                                <div>
                                    <p className="font-medium">Auto-join audio</p>
                                    <p className="text-sm text-neutral-500">Automatically connect to audio when joining a meeting.</p>
                                </div>
                            </div>
                            <Switch
                                checked={autoJoin}
                                onCheckedChange={setAutoJoin}
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
                            "Save Preferences"
                        )}
                    </Button>
                </div>
            </div>
        </motion.div>
    );
}
