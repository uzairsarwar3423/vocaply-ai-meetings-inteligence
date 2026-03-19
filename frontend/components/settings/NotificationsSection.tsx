"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Bell, Mail, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { useAuthStore } from "@/store/authStore";
import { usersApi } from "@/lib/api/users";
import { toast } from "sonner";

export function NotificationsSection() {
    const { user, updateUser } = useAuthStore();
    const [isLoading, setIsLoading] = useState(false);

    const [emailAlerts, setEmailAlerts] = useState(user?.notification_settings?.email_alerts ?? true);
    const [pushNotifications, setPushNotifications] = useState(user?.notification_settings?.push_notifications ?? true);
    const [meetingReminders, setMeetingReminders] = useState(user?.notification_settings?.meeting_reminders ?? true);

    const handleSave = async () => {
        setIsLoading(true);
        try {
            const updated = await usersApi.updateNotifications({
                email_alerts: emailAlerts,
                push_notifications: pushNotifications,
                meeting_reminders: meetingReminders,
            });
            updateUser(updated);
            toast.success("Notification preferences updated");
        } catch (err: unknown) {
            const message =
                (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
                "Failed to update notifications";
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
                <h3 className="text-xl font-bold font-outfit">Notifications</h3>
                <p className="text-sm text-neutral-500 mt-1">Choose what updates you want to receive.</p>
            </div>

            <div className="bg-white rounded-2xl border border-neutral-100 p-6 shadow-sm space-y-8">

                {/* Email Notifications */}
                <div className="space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-orange-50 flex items-center justify-center text-orange-500">
                            <Mail className="w-4 h-4" />
                        </div>
                        <div>
                            <h4 className="font-medium">Email Notifications</h4>
                            <p className="text-sm text-neutral-500">Receive updates directly to your inbox.</p>
                        </div>
                    </div>

                    <div className="space-y-2 mt-4 ml-11">
                        <div className="flex items-center justify-between py-3 border-b border-neutral-50">
                            <div>
                                <p className="font-medium text-sm">Meeting Summaries & Action Items</p>
                                <p className="text-xs text-neutral-500">Get AI-generated summaries and tasks after every meeting.</p>
                            </div>
                            <Switch checked={emailAlerts} onCheckedChange={setEmailAlerts} />
                        </div>
                    </div>
                </div>

                <hr className="border-neutral-100" />

                {/* Push / In-App Notifications */}
                <div className="space-y-4">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-blue-500">
                            <Bell className="w-4 h-4" />
                        </div>
                        <div>
                            <h4 className="font-medium">In-App Notifications</h4>
                            <p className="text-sm text-neutral-500">Alerts delivered while you have the app open.</p>
                        </div>
                    </div>

                    <div className="space-y-2 mt-4 ml-11 bg-neutral-50/50 p-4 rounded-xl border border-neutral-100">
                        <div className="flex items-center justify-between py-2 border-b border-neutral-200/50">
                            <div>
                                <p className="font-medium text-sm">Bot Status & Transcription Ready</p>
                                <p className="text-xs text-neutral-500">When the bot joins, leaves, or processing completes.</p>
                            </div>
                            <Switch checked={pushNotifications} onCheckedChange={setPushNotifications} />
                        </div>
                        <div className="flex items-center justify-between py-2">
                            <div>
                                <p className="font-medium text-sm">Meeting Reminders</p>
                                <p className="text-xs text-neutral-500">Alerts before upcoming scheduled meetings.</p>
                            </div>
                            <Switch checked={meetingReminders} onCheckedChange={setMeetingReminders} />
                        </div>
                    </div>
                </div>

                <div className="rounded-xl bg-orange-50 border border-orange-100 p-4 flex gap-3 text-orange-800">
                    <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-orange-500" />
                    <div className="text-sm">
                        <p className="font-medium mb-1">Important System Alerts</p>
                        <p className="opacity-90">You cannot disable notifications for security alerts, billing issues, or major system outages.</p>
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
