"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "./ui/button";
import { Menu, X, ChevronDown, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

const Navbar = () => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20);
        };
        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    const navLinks = [
        { name: "Product", href: "#features", hasDropdown: true },
        { name: "How it Works", href: "#how-it-works" },
        { name: "Solutions", href: "/solutions", hasDropdown: true },
        { name: "Pricing", href: "#pricing" },
    ];

    return (
        <header className="fixed top-0 left-0 right-0 z-50 px-6 py-4 pointer-events-none font-inter">
            <div className={cn(
                "max-w-7xl mx-auto transition-all duration-700 pointer-events-auto",
                isScrolled ? "translate-y-0" : "translate-y-2"
            )}>
                <nav
                    className={cn(
                        "flex items-center justify-between transition-all duration-500",
                        "backdrop-blur-xl bg-white/70 border border-white/40 rounded-[2rem] px-6 py-2.5 shadow-[0_8px_32px_rgba(0,0,0,0.04)]",
                        isScrolled ? "py-2 px-6 shadow-[0_20px_40px_rgba(0,0,0,0.06)] scale-[0.98]" : "py-3.5 px-8"
                    )}
                >
                    {/* Logo Section */}
                    <Link href="/" className="flex items-center gap-3 group">
                        <motion.div
                            whileHover={{ rotate: 15, scale: 1.1 }}
                            className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-primary to-teal-400 flex items-center justify-center shadow-lg shadow-primary/20 relative overflow-hidden"
                        >
                            <div className="absolute inset-0 bg-white/20 animate-pulse" />
                            <span className="text-white font-black text-xl relative z-10">V</span>
                        </motion.div>
                        <span className="text-2xl font-black font-outfit text-neutral-900 tracking-tighter flex items-center">
                            Vocaply<span className="text-primary">.ai</span>
                        </span>
                    </Link>

                    {/* Desktop Nav Links */}
                    <div className="hidden lg:flex items-center gap-2">
                        {navLinks.map((link, idx) => (
                            <Link
                                key={link.name}
                                href={link.href}
                                className="px-5 py-2 text-sm font-bold text-neutral-500 hover:text-neutral-900 transition-all duration-300 rounded-full hover:bg-neutral-50/50 flex items-center gap-1.5 group/item"
                            >
                                <span className="relative">
                                    {link.name}
                                    <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary transition-all duration-300 group-hover/item:w-full opacity-50" />
                                </span>
                                {link.hasDropdown && (
                                    <ChevronDown size={14} className="text-neutral-300 group-hover/item:rotate-180 group-hover/item:text-primary transition-all duration-500" />
                                )}
                            </Link>
                        ))}
                    </div>

                    {/* CTA Section */}
                    <div className="flex items-center gap-4">
                        <Link
                            href="/login"
                            className="hidden md:block text-sm font-bold text-neutral-400 hover:text-neutral-900 transition-colors tracking-tight"
                        >
                            Login
                        </Link>
                        <button
                            className="rounded-2xl px-7 py-3 bg-neutral-900 text-white text-[11px] font-black uppercase tracking-[0.2em] hover:bg-primary transition-all duration-500 shadow-xl shadow-neutral-200 hover:shadow-primary/20 active:scale-95 whitespace-nowrap group relative overflow-hidden"
                        >
                            <span className="relative z-10 flex items-center gap-2">
                                Request Pilot <Sparkles size={12} className="fill-white" />
                            </span>
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                        </button>

                        {/* Mobile Menu Toggle */}
                        <button
                            className="lg:hidden w-11 h-11 flex items-center justify-center rounded-2xl bg-neutral-100/50 text-neutral-600 border border-neutral-200/50 hover:bg-white transition-all shadow-sm"
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        >
                            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
                        </button>
                    </div>
                </nav>
            </div>

            {/* Mobile Menu Dropdown */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -10 }}
                        className="lg:hidden mt-4 mx-auto max-w-sm glass-card rounded-[2.5rem] border-white/50 p-6 pointer-events-auto flex flex-col gap-4 overflow-hidden shadow-2xl"
                    >
                        {navLinks.map((link) => (
                            <Link
                                key={link.name}
                                href={link.href}
                                className="flex items-center justify-between text-neutral-700 font-bold py-4 px-6 rounded-2xl hover:bg-primary/5 hover:text-primary transition-all text-sm"
                                onClick={() => setMobileMenuOpen(false)}
                            >
                                {link.name}
                                {link.hasDropdown && <ChevronDown size={18} className="text-neutral-300" />}
                            </Link>
                        ))}
                        <div className="h-px bg-neutral-100/50 my-2" />
                        <div className="flex flex-col gap-3">
                            <Link href="/login" className="text-center font-bold text-neutral-400 py-2 hover:text-neutral-900 transition-colors uppercase tracking-widest text-[10px]">
                                Already a member?
                            </Link>
                            <button className="w-full rounded-2xl h-14 bg-primary text-white font-black uppercase tracking-widest text-[11px] shadow-lg shadow-primary/20">Get Started Now</button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </header>
    );
};

export default Navbar;
