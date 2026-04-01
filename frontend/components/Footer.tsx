"use client";

import React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Github, Twitter, Linkedin, ArrowUpRight, ShieldCheck, Globe } from "lucide-react";

const Footer = () => {
    return (
        <footer className="bg-neutral-950 pt-32 pb-12 overflow-hidden relative">
            {/* Background Decoration */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
            <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-primary/5 rounded-full blur-[140px]" />

            <div className="max-w-7xl mx-auto px-6 relative z-10">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-16 mb-24">
                    <div className="col-span-1 lg:col-span-1">
                        <Link href="/" className="flex items-center gap-3 mb-8 group">
                            <motion.div
                                whileHover={{ rotate: 360 }}
                                transition={{ duration: 0.8 }}
                                className="w-12 h-12 bg-primary rounded-[1rem] flex items-center justify-center shadow-2xl shadow-primary/20"
                            >
                                <span className="text-white font-black text-2xl">V</span>
                            </motion.div>
                            <span className="text-3xl font-black font-outfit text-white tracking-tighter">
                                Vocaply<span className="text-primary italic">.ai</span>
                            </span>
                        </Link>
                        <p className="text-neutral-500 mb-10 font-medium leading-relaxed tracking-tight text-lg">
                            The AI Meeting Intelligence platform that transforms conversations into accountability with high-fidelity extraction.
                        </p>
                        <div className="flex gap-4">
                            {[Twitter, Linkedin, Github].map((Icon, i) => (
                                <Link
                                    key={i}
                                    href="#"
                                    className="w-12 h-12 rounded-2xl bg-white/5 border border-white/5 flex items-center justify-center text-neutral-400 hover:text-white hover:bg-primary hover:border-primary transition-all duration-300"
                                >
                                    <Icon size={20} />
                                </Link>
                            ))}
                        </div>
                    </div>

                    <div className="lg:pl-12">
                        <h4 className="text-white text-[10px] font-black uppercase tracking-[0.3em] mb-10">Product</h4>
                        <ul className="space-y-5 text-neutral-500 font-medium tracking-tight">
                            <li><Link href="#features" className="hover:text-primary transition-colors flex items-center gap-2 group">Features <div className="w-1 h-1 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity" /></Link></li>
                            <li><Link href="#how-it-works" className="hover:text-primary transition-colors flex items-center gap-2 group">Solutions <div className="w-1 h-1 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity" /></Link></li>
                            <li><Link href="#pricing" className="hover:text-primary transition-colors flex items-center gap-2 group">Pricing <div className="w-1 h-1 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity" /></Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors flex items-center gap-1 group">Changelog <ArrowUpRight size={14} className="opacity-0 group-hover:opacity-100 transition-all -translate-x-1 group-hover:translate-x-0" /></Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-white text-[10px] font-black uppercase tracking-[0.3em] mb-10">Company</h4>
                        <ul className="space-y-5 text-neutral-500 font-medium tracking-tight">
                            <li><Link href="#" className="hover:text-primary transition-colors flex items-center gap-2 group">About <div className="w-1 h-1 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity" /></Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors flex items-center gap-2 group">Careers <span className="bg-primary/10 text-primary text-[8px] px-2 py-0.5 rounded-full ml-1">Hiring</span></Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors flex items-center gap-2 group">Partners <div className="w-1 h-1 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity" /></Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors flex items-center gap-2 group">Contact <div className="w-1 h-1 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity" /></Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-white text-[10px] font-black uppercase tracking-[0.3em] mb-10">Stay Updated</h4>
                        <div className="relative group">
                            <input
                                type="email"
                                placeholder="Enter your email"
                                className="w-full h-16 bg-white/5 border border-white/10 rounded-2xl px-6 text-white font-medium focus:outline-none focus:border-primary/50 transition-all placeholder:text-neutral-600"
                            />
                            <button className="absolute right-2 top-2 h-12 px-6 bg-primary text-white text-[10px] font-black uppercase tracking-widest rounded-xl hover:bg-white hover:text-black transition-all">
                                Join
                            </button>
                        </div>
                        <div className="mt-8 flex items-center gap-3 text-neutral-600 text-[10px] font-black uppercase tracking-widest">
                            <ShieldCheck size={14} className="text-neutral-700" />
                            <span>GDPR Compliant</span>
                        </div>
                    </div>
                </div>

                <div className="pt-12 border-t border-white/5 flex flex-col md:flex-row justify-between items-center gap-8">
                    <p className="text-neutral-600 font-black uppercase tracking-[0.2em] text-[10px]">
                        © {new Date().getFullYear()} Vocaply Engine. Built with Passion.
                    </p>

                    <div className="flex items-center gap-8">
                        <div className="flex items-center gap-3 text-neutral-600 text-[10px] font-black uppercase tracking-widest">
                            <Globe size={14} className="text-neutral-700" />
                            <span>English (US)</span>
                        </div>
                        <div className="flex items-center gap-2 text-neutral-600 font-black uppercase tracking-[0.1em] text-[10px]">
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                            Infrastructure Active
                        </div>
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
