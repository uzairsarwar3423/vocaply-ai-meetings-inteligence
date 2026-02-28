"use client";

import { useState } from "react";
import { User, Settings, Bell, Shield, CreditCard } from "lucide-react";

import { ProfileSection } from "@/components/settings/ProfileSection";
import { PreferencesSection } from "@/components/settings/PreferencesSection";
import { NotificationsSection } from "@/components/settings/NotificationsSection";
import { SecuritySection } from "@/components/settings/SecuritySection";
import { BillingSection } from "@/components/settings/BillingSection";

type TabId = "profile" | "preferences" | "notifications" | "security" | "billing";

interface Tab {
    id: TabId;
    label: string;
    icon: React.ElementType;
}

const tabs: Tab[] = [
    { id: "profile", label: "Profile", icon: User },
    { id: "preferences", label: "Preferences", icon: Settings },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "security", label: "Security", icon: Shield },
    { id: "billing", label: "Billing", icon: CreditCard },
];

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState<TabId>("profile");

    const renderContent = () => {
        switch (activeTab) {
            case "profile":
                return <ProfileSection />;
            case "preferences":
                return <PreferencesSection />;
            case "notifications":
                return <NotificationsSection />;
            case "security":
                return <SecuritySection />;
            case "billing":
                return <BillingSection />;
            default:
                return null;
        }
    };

    return (
        <div className="max-w-6xl mx-auto pb-12">
            <div className="mb-8">
                <h1 className="text-3xl font-outfit font-bold text-neutral-900">Settings</h1>
                <p className="text-neutral-500 mt-2">Manage your account settings and preferences.</p>
            </div>

            <div className="flex flex-col md:flex-row gap-8">
                {/* Settings Sidebar Nav */}
                <div className="md:w-64 shrink-0">
                    <nav className="flex md:flex-col gap-2 overflow-x-auto md:overflow-visible pb-4 md:pb-0 scrollbar-hide">
                        {tabs.map((tab) => {
                            const isActive = activeTab === tab.id;
                            const Icon = tab.icon;

                            return (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all whitespace-nowrap md:whitespace-normal font-medium text-sm
                                        ${isActive
                                            ? "bg-white shadow-sm ring-1 ring-neutral-200/50 text-neutral-900 border-l-4 border-l-primary"
                                            : "text-neutral-500 hover:bg-neutral-100/50 hover:text-neutral-800 border-l-4 border-l-transparent"
                                        }`}
                                >
                                    <Icon className={`w-5 h-5 ${isActive ? "text-primary" : "text-neutral-400"}`} />
                                    {tab.label}
                                </button>
                            );
                        })}
                    </nav>
                </div>

                {/* Main Content Area */}
                <div className="flex-1 min-w-0">
                    {renderContent()}
                </div>
            </div>
        </div>
    );
}
