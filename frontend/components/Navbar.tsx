"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "./ui/button";
import { Menu, X, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

const Navbar = () => {
    const [isScrolled, setIsScrolled] = useState(false);
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 10);
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
        <header className="fixed top-6 left-0 right-0 z-50 px-6 pointer-events-none font-inter">
            <nav
                className={cn(
                    "max-w-6xl mx-auto flex items-center justify-between transition-all duration-500 pointer-events-auto",
                    "navbar-glass rounded-full px-6 py-2.5 shadow-[0_8px_30px_rgb(0,172,172,0.08)]",
                    isScrolled ? "py-2 scale-[0.98] border-neutral-200/50 shadow-lg" : "py-3"
                )}
            >
                {/* Logo Section */}
                <Link href="/" className="flex items-center gap-2 group">
                    <div className="w-9 h-9 md:w-10 md:h-10 logo-circle group-hover:rotate-12 transition-all duration-500">
                        <span className="text-white font-bold text-lg md:text-xl">V</span>
                    </div>
                    <span className="text-xl md:text-2xl font-outfit font-bold text-neutral-900 tracking-tight">
                        Vocaply<span className="text-[#00ACAC]">.ai</span>
                    </span>
                </Link>

                {/* Desktop Nav Links */}
                <div className="hidden lg:flex items-center gap-1">
                    {navLinks.map((link) => (
                        <Link
                            key={link.name}
                            href={link.href}
                            className="px-4 py-2 text-neutral-600 hover:text-[#00ACAC] font-medium transition-all duration-300 rounded-full hover:bg-primary-50 flex items-center gap-1 group/item"
                        >
                            <span className="relative">
                                {link.name}
                                <span className="absolute -bottom-0.5 left-0 w-0 h-0.5 bg-[#00ACAC] transition-all duration-300 group-hover/item:w-full" />
                            </span>
                            {link.hasDropdown && (
                                <ChevronDown size={14} className="text-neutral-400 group-hover/item:rotate-180 group-hover/item:text-[#00ACAC] transition-all duration-300" />
                            )}
                        </Link>
                    ))}
                </div>

                {/* CTA Section */}
                <div className="flex items-center gap-3">
                    <Link
                        href="/login"
                        className="hidden md:block px-4 py-2 text-neutral-600 hover:text-[#00ACAC] font-medium transition-colors"
                    >
                        Log in
                    </Link>
                    <button
                        className="rounded-full px-6 py-2.5 btn-primary-enhanced text-sm font-semibold transition-all duration-300 active:scale-95 whitespace-nowrap"
                    >
                        Request demo
                    </button>

                    {/* Mobile Menu Toggle */}
                    <button
                        className="lg:hidden w-10 h-10 flex items-center justify-center rounded-full bg-neutral-100/50 text-neutral-600 border border-neutral-200"
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                    >
                        {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
                    </button>
                </div>
            </nav>

            {/* Mobile Menu Dropdown */}
            <AnimatePresence>
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: -20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -20, scale: 0.95 }}
                        className="lg:hidden mt-4 mx-auto max-w-sm bg-white/95 backdrop-blur-xl rounded-[2.5rem] border border-neutral-200 shadow-2xl p-6 pointer-events-auto flex flex-col gap-4 overflow-hidden"
                    >
                        {navLinks.map((link) => (
                            <Link
                                key={link.name}
                                href={link.href}
                                className="flex items-center justify-between text-neutral-700 font-medium py-3 px-5 rounded-2xl hover:bg-primary-50 hover:text-[#00ACAC] transition-all"
                                onClick={() => setMobileMenuOpen(false)}
                            >
                                {link.name}
                                {link.hasDropdown && <ChevronDown size={18} className="text-neutral-400" />}
                            </Link>
                        ))}
                        <div className="h-px bg-neutral-100 my-2" />
                        <div className="flex flex-col gap-3">
                            <Link href="/login" className="text-center font-medium text-neutral-600 py-2 hover:text-[#00ACAC] transition-colors">
                                Log in
                            </Link>
                            <button className="w-full rounded-2xl h-12 btn-primary-enhanced font-bold">Get Started</button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </header>
    );
};

export default Navbar;
