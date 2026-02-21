"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import {
    LayoutDashboard,
    Calendar,
    CheckSquare,
    Users,
    Settings,
    LogOut
} from "lucide-react";

const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Meetings", href: "/meetings", icon: Calendar },
    { label: "Action Items", href: "/action-items", icon: CheckSquare },
    { label: "Team", href: "/team", icon: Users },
    { label: "Settings", href: "/settings", icon: Settings },
];

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const { isAuthenticated, user, logout, _hasHydrated } = useAuthStore();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (_hasHydrated && !isAuthenticated) {
            router.push("/login");
        }
    }, [isAuthenticated, _hasHydrated, router]);

    if (!_hasHydrated) return null; // Or a loading spinner
    if (!isAuthenticated) return null;

    return (
        <div className="flex h-screen bg-gray-50 overflow-hidden font-inter">
            {/* Sidebar */}
            <aside className="hidden md:flex w-72 flex-col bg-white border-r border-neutral-100 p-6">
                <div className="flex items-center gap-3 mb-10 px-2 transition-transform hover:scale-105">
                    <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white font-bold shadow-primary">V</div>
                    <span className="text-2xl font-outfit font-bold bg-neutral-900 bg-clip-text">Vocaply</span>
                </div>

                <nav className="flex-1 space-y-2">
                    {navItems.map((item) => {
                        const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all duration-300 group ${isActive
                                    ? 'bg-primary/10 text-primary font-bold shadow-sm ring-1 ring-primary/5'
                                    : 'text-neutral-500 hover:bg-neutral-50 hover:text-neutral-900'
                                    }`}
                            >
                                <item.icon className={`w-5 h-5 transition-transform duration-300 ${isActive ? 'scale-110' : 'group-hover:scale-110'}`} />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>

                <div className="mt-auto pt-6 border-t border-neutral-100">
                    <button
                        onClick={() => logout()}
                        className="flex items-center gap-3 px-4 py-3 w-full rounded-xl text-neutral-500 hover:bg-error/5 hover:text-error transition-all group"
                    >
                        <LogOut className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                        <span className="font-medium">Logout</span>
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-hidden">
                <header className="h-16 bg-white border-b border-gray-100 px-8 flex items-center justify-between">
                    <h2 className="font-outfit font-bold text-lg">Good Morning, {user?.full_name?.split(' ')[0]}</h2>
                    <div className="flex items-center gap-4">
                        <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-xs">
                            {user?.full_name?.[0]}
                        </div>
                    </div>
                </header>

                <div className="flex-1 overflow-y-auto p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
