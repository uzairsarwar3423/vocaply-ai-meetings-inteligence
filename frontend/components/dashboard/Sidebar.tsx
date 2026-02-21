import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    BarChart3,
    Calendar,
    ChevronLeft,
    ChevronRight,
    FileText,
    LayoutDashboard,
    LogOut,
    Mic,
    Settings,
    Users
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', href: '/dashboard' },
    { icon: Mic, label: 'Meetings', href: '/dashboard/meetings' },
    { icon: FileText, label: 'Transcripts', href: '/dashboard/transcripts' },
    { icon: Calendar, label: 'Calendar', href: '/dashboard/calendar' },
    { icon: Users, label: 'Team', href: '/dashboard/team' },
    { icon: BarChart3, label: 'Insights', href: '/dashboard/insights' },
];

const Sidebar = () => {
    const pathname = usePathname();
    const [isCollapsed, setIsCollapsed] = React.useState(false);

    return (
        <div
            className={cn(
                "h-screen bg-white border-r border-neutral-200 transition-all duration-300 flex flex-col sticky top-0 left-0 z-40",
                isCollapsed ? "w-20" : "w-72"
            )}
        >
            {/* Logo Section */}
            <div className="p-6 flex items-center gap-3">
                <div className="logo-circle w-10 h-10 shrink-0">
                    <Mic className="w-5 h-5" />
                </div>
                {!isCollapsed && (
                    <span className="text-xl font-bold text-neutral-900 tracking-tight">
                        Vocaply<span className="text-primary">.ai</span>
                    </span>
                )}
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-3 space-y-1 mt-4">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-3 py-3 rounded-2xl transition-all duration-200 group relative",
                                isActive
                                    ? "bg-primary text-white shadow-primary"
                                    : "text-neutral-500 hover:bg-primary-50 hover:text-primary-700"
                            )}
                        >
                            <item.icon className={cn("w-5 h-5", isActive ? "text-white" : "group-hover:text-primary")} />
                            {!isCollapsed && (
                                <span className="font-medium">{item.label}</span>
                            )}
                            {isActive && !isCollapsed && (
                                <div className="absolute right-3 w-1.5 h-1.5 rounded-full bg-white/50" />
                            )}
                            {isCollapsed && (
                                <div className="absolute left-full ml-4 px-2 py-1 bg-neutral-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                                    {item.label}
                                </div>
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Footer Actions */}
            <div className="p-4 border-t border-neutral-100 space-y-1">
                <Link
                    href="/dashboard/settings"
                    className={cn(
                        "flex items-center gap-3 px-3 py-3 rounded-2xl text-neutral-500 hover:bg-neutral-100 transition-all group",
                        isCollapsed && "justify-center"
                    )}
                >
                    <Settings className="w-5 h-5 group-hover:rotate-45 transition-transform" />
                    {!isCollapsed && <span className="font-medium">Settings</span>}
                </Link>
                <button
                    className={cn(
                        "w-full flex items-center gap-3 px-3 py-3 rounded-2xl text-rose-500 hover:bg-rose-50 transition-all group",
                        isCollapsed && "justify-center"
                    )}
                >
                    <LogOut className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                    {!isCollapsed && <span className="font-medium">Logout</span>}
                </button>
            </div>

            {/* Collapse Toggle */}
            <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="absolute -right-3 top-20 w-6 h-6 bg-white border border-neutral-200 rounded-full flex items-center justify-center shadow-sm hover:shadow-md transition-all text-neutral-400 hover:text-primary"
            >
                {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
            </button>
        </div>
    );
};

export default Sidebar;
