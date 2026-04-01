"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import {
    LayoutDashboard,
    Calendar,
    Video,
    CheckSquare,
    Users,
    Settings,
    LogOut,
    Blocks,
    Menu,
    X,
    UserCircle,
    Bell,
    BarChart2
} from "lucide-react";

const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Meetings", href: "/meetings", icon: Video },
    { label: "Calendar", href: "/calendar", icon: Calendar },
    { label: "Action Items", href: "/action-items", icon: CheckSquare },
    { label: "Analytics", href: "/analytics", icon: BarChart2 },
    { label: "Team", href: "/team", icon: Users },
    { label: "Integrations", href: "/integrations", icon: Blocks },
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
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    useEffect(() => {
        if (_hasHydrated && !isAuthenticated) {
            router.push("/login");
        }
    }, [isAuthenticated, _hasHydrated, router]);

    // Close sidebar on route change
    useEffect(() => {
        setIsSidebarOpen(false);
    }, [pathname]);

    if (!_hasHydrated) return null; // Or a loading spinner
    if (!isAuthenticated) return null;

    const SidebarContent = () => (
        <div className="flex flex-col h-full">
            <div className="flex items-center gap-3 mb-10 px-2 transition-all duration-500 hover:translate-x-1 select-none">
                <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary-700 rounded-xl flex items-center justify-center text-white font-black shadow-lg shadow-primary/20 ring-1 ring-white/20">
                    <Blocks className="w-6 h-6" />
                </div>
                <span className="text-2xl font-outfit font-black tracking-tight bg-gradient-to-r from-neutral-900 to-neutral-600 bg-clip-text text-transparent">Vocaply</span>
            </div>

            <nav className="flex-1 space-y-2 overflow-y-auto custom-scrollbar pr-2">
                {navItems.map((item) => {
                    const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all duration-300 group relative ${isActive
                                ? 'bg-primary/10 text-primary font-bold shadow-[inset_0px_0px_12px_rgba(13,148,136,0.05)] ring-1 ring-primary/20'
                                : 'text-neutral-500 hover:bg-white hover:text-neutral-900 hover:shadow-sm hover:ring-1 hover:ring-neutral-200'
                                }`}
                        >
                            <item.icon className={`w-5 h-5 transition-all duration-300 ${isActive ? 'scale-110 drop-shadow-[0_0_8px_rgba(13,148,136,0.3)]' : 'group-hover:scale-110 group-hover:text-primary'}`} />
                            <span className="tracking-tight text-sm">{item.label}</span>
                            {isActive && (
                                <div className="absolute left-0 w-1 h-6 bg-primary rounded-r-full shadow-[0_0_8px_rgba(13,148,136,0.5)]" />
                            )}
                        </Link>
                    );
                })}
            </nav>

            <div className="mt-auto pt-6 border-t border-neutral-100/50">
                <div className="mb-4 px-1">
                    <div className="bg-white/50 backdrop-blur-sm p-3 rounded-2xl flex items-center gap-3 border border-white/60 shadow-sm transition-all hover:bg-white/80">
                        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center text-primary font-bold text-sm ring-1 ring-primary/10 shadow-inner">
                            {user?.full_name?.[0] || 'U'}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-xs font-bold text-neutral-900 truncate tracking-tight">{user?.full_name}</p>
                            <p className="text-[10px] text-neutral-400 truncate font-medium uppercase tracking-wider">{user?.email?.split('@')[0]}</p>
                        </div>
                    </div>
                </div>
                <button
                    onClick={() => logout()}
                    className="flex items-center gap-3 px-4 py-3 w-full rounded-xl text-neutral-400 hover:bg-rose-50 hover:text-rose-500 transition-all group font-semibold text-sm"
                >
                    <LogOut className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                    <span>Logout</span>
                </button>
            </div>
        </div>
    );

    return (
        <div className="flex h-screen bg-gray-50 overflow-hidden font-inter text-neutral-900">
            {/* Desktop Sidebar */}
            <aside className="hidden lg:flex w-72 flex-col bg-white/70 backdrop-blur-xl border-r border-white/40 p-6 flex-shrink-0 relative z-20 shadow-[4px_0_24px_rgba(0,0,0,0.02)]">
                <SidebarContent />
            </aside>

            {/* Mobile Sidebar (Drawer) */}
            <div className={`fixed inset-0 z-50 lg:hidden transition-all duration-300 ${isSidebarOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'}`}>
                {/* Backdrop */}
                <div
                    className="absolute inset-0 bg-neutral-900/40 backdrop-blur-sm transition-opacity duration-300"
                    onClick={() => setIsSidebarOpen(false)}
                />

                {/* Drawer Panel */}
                <aside className={`absolute top-0 bottom-0 left-0 w-[280px] bg-white p-6 transition-transform duration-300 transform shadow-2xl ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
                    <div className="absolute top-6 right-6 lg:hidden">
                        <button
                            onClick={() => setIsSidebarOpen(false)}
                            className="p-2 rounded-lg bg-neutral-50 text-neutral-500 hover:text-neutral-900 transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                    <div className="flex flex-col h-full overflow-y-auto">
                        <SidebarContent />
                    </div>
                </aside>
            </div>

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-hidden relative z-10 w-full">
                {/* Global Header */}
                <header className="h-16 lg:h-20 bg-white/60 backdrop-blur-md border-b border-white/40 px-4 lg:px-8 flex items-center justify-between sticky top-0 z-30 shadow-sm">
                    <div className="flex items-center gap-4">
                        {/* Mobile Toggle */}
                        <button
                            onClick={() => setIsSidebarOpen(true)}
                            className="lg:hidden p-2 -ml-2 rounded-xl bg-white/80 text-neutral-600 shadow-sm border border-neutral-100 hover:text-primary transition-all active:scale-95"
                            aria-label="Open menu"
                        >
                            <Menu className="w-6 h-6" />
                        </button>

                        <div className="flex flex-col">
                            <h2 className="font-outfit font-black text-lg lg:text-xl tracking-tight text-neutral-900 drop-shadow-sm">
                                {pathname === '/dashboard' ? `Hello, ${user?.full_name?.split(' ')[0]}!` : navItems.find(i => pathname.startsWith(i.href))?.label || 'Overview'}
                            </h2>
                            <p className="hidden sm:block text-[10px] lg:text-[11px] text-neutral-400 font-bold uppercase tracking-widest">
                                {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 lg:gap-4">
                        <button className="hidden sm:flex p-2.5 rounded-xl text-neutral-400 hover:text-primary hover:bg-primary/5 transition-all shadow-sm bg-white/50 border border-white/80">
                            <Bell className="w-5 h-5" />
                        </button>

                        <div className="h-8 w-px bg-neutral-200/50 mx-1 hidden sm:block" />

                        <div className="flex items-center gap-3 pl-1">
                            <div className="hidden sm:flex flex-col items-end">
                                <span className="text-xs font-black text-neutral-900 leading-tight uppercase tracking-tight">{user?.full_name}</span>
                                <div className="flex items-center gap-1.5 mt-0.5">
                                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                                    <span className="text-[9px] text-neutral-400 font-bold uppercase tracking-widest">Pro Member</span>
                                </div>
                            </div>
                            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center text-primary font-bold shadow-md ring-1 ring-white cursor-pointer hover:scale-105 hover:shadow-lg transition-all active:scale-95">
                                {user?.full_name?.[0] || 'U'}
                            </div>
                        </div>
                    </div>
                </header>

                {/* Page View */}
                <div className="flex-1 overflow-y-auto w-full">
                    <div className="max-w-[1600px] mx-auto p-4 lg:p-8">
                        {children}
                    </div>
                </div>
            </main>
        </div>
    );
}
