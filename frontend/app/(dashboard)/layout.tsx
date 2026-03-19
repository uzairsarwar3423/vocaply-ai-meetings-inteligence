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
    Bell
} from "lucide-react";

const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: "Meetings", href: "/meetings", icon: Video },
    { label: "Calendar", href: "/calendar", icon: Calendar },
    { label: "Action Items", href: "/action-items", icon: CheckSquare },
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
        <>
            <div className="flex items-center gap-3 mb-10 px-2 transition-transform hover:scale-105 select-none">
                <div className="w-10 h-10 bg-gradient-to-br from-primary to-primary/80 rounded-xl flex items-center justify-center text-white font-black shadow-lg shadow-primary/20 ring-2 ring-primary/10">
                    <Blocks className="w-6 h-6" />
                </div>
                <span className="text-2xl font-outfit font-bold bg-neutral-900 bg-clip-text">Vocaply</span>
            </div>

            <nav className="flex-1 space-y-1.5 overflow-y-auto">
                {navItems.map((item) => {
                    const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all duration-300 group ${isActive
                                ? 'bg-primary/10 text-primary font-bold shadow-sm ring-1 ring-primary/5'
                                : 'text-neutral-500 hover:bg-neutral-50'
                                }`}
                        >
                            <item.icon className={`w-5 h-5 transition-all duration-300 ${isActive ? 'scale-110 drop-shadow-sm' : 'group-hover:scale-110'}`} />
                            <span className="tracking-tight">{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            <div className="mt-auto pt-6 border-t border-neutral-100">
                <div className="mb-4 px-2">
                    <div className="bg-neutral-50 p-3 rounded-2xl flex items-center gap-3 border border-neutral-100">
                        <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-xs ring-2 ring-white shadow-sm">
                            {user?.full_name?.[0] || 'U'}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-xs font-bold text-neutral-900 truncate tracking-tight">{user?.full_name}</p>
                            <p className="text-[10px] text-neutral-500 truncate">{user?.email}</p>
                        </div>
                    </div>
                </div>
                <button
                    onClick={() => logout()}
                    className="flex items-center gap-3 px-4 py-3 w-full rounded-xl text-neutral-500 hover:bg-red-50 hover:text-red-500 transition-all group font-medium"
                >
                    <LogOut className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                    <span>Logout</span>
                </button>
            </div>
        </>
    );

    return (
        <div className="flex h-screen bg-gray-50 overflow-hidden font-inter text-neutral-900">
            {/* Desktop Sidebar */}
            <aside className="hidden lg:flex w-72 flex-col bg-white border-r border-neutral-100 p-6 flex-shrink-0 relative z-20">
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
                <header className="h-16 lg:h-20 bg-white border-b border-gray-100 px-4 lg:px-8 flex items-center justify-between sticky top-0 z-30">
                    <div className="flex items-center gap-4">
                        {/* Mobile Toggle */}
                        <button
                            onClick={() => setIsSidebarOpen(true)}
                            className="lg:hidden p-2 -ml-2 rounded-xl bg-neutral-50 text-neutral-600 hover:text-neutral-900 transition-all hover:scale-105 active:scale-95"
                            aria-label="Open menu"
                        >
                            <Menu className="w-6 h-6" />
                        </button>

                        <div className="flex flex-col">
                            <h2 className="font-outfit font-black text-lg lg:text-xl tracking-tight text-neutral-900">
                                {pathname === '/dashboard' ? `Welcome back, ${user?.full_name?.split(' ')[0]}` : navItems.find(i => pathname.startsWith(i.href))?.label || 'Overview'}
                            </h2>
                            <p className="hidden sm:block text-[11px] lg:text-xs text-neutral-500 font-medium">
                                Today is {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 lg:gap-4">
                        <button className="hidden sm:flex p-2.5 rounded-xl text-neutral-400 hover:text-neutral-900 hover:bg-neutral-50 transition-all">
                            <Bell className="w-5 h-5" />
                        </button>

                        <div className="h-8 w-px bg-neutral-100 mx-1 hidden sm:block" />

                        <div className="flex items-center gap-3 pl-1">
                            <div className="hidden sm:flex flex-col items-end">
                                <span className="text-xs font-bold text-neutral-900 leading-tight">{user?.full_name}</span>
                                <span className="text-[10px] text-neutral-400 font-medium tracking-tight">Standard Plan</span>
                            </div>
                            <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary font-bold shadow-sm ring-1 ring-primary/5 cursor-pointer hover:scale-105 transition-transform">
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
