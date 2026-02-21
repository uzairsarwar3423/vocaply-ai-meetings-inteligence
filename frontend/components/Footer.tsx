"use client";

import React from "react";
import Link from "next/link";
import { Button } from "./ui/button";
import { Github, Twitter, Linkedin, ArrowUpRight } from "lucide-react";

const Footer = () => {
    return (
        <footer className="bg-gray-900 pt-32 pb-12 overflow-hidden">
            <div className="max-w-7xl mx-auto px-6">


                {/* Real Footer */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-20">
                    <div className="col-span-1 lg:col-span-1">
                        <Link href="/" className="flex items-center gap-2 mb-6">
                            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-primary">
                                <span className="text-white font-bold text-xl">V</span>
                            </div>
                            <span className="text-2xl font-outfit font-bold text-white">
                                Vocaply<span className="text-primary">.ai</span>
                            </span>
                        </Link>
                        <p className="text-gray-400 mb-8 font-inter">
                            The AI Meeting Intelligence platform that transforms conversations into accountability.
                        </p>
                        <div className="flex gap-4">
                            <Link href="#" className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 hover:text-white hover:bg-primary transition-all">
                                <Twitter size={20} />
                            </Link>
                            <Link href="#" className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 hover:text-white hover:bg-primary transition-all">
                                <Linkedin size={20} />
                            </Link>
                            <Link href="#" className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 hover:text-white hover:bg-primary transition-all">
                                <Github size={20} />
                            </Link>
                        </div>
                    </div>

                    <div>
                        <h4 className="text-white font-bold mb-6 font-outfit uppercase tracking-wider text-sm">Product</h4>
                        <ul className="space-y-4 text-gray-400">
                            <li><Link href="#features" className="hover:text-primary transition-colors">Features</Link></li>
                            <li><Link href="#how-it-works" className="hover:text-primary transition-colors">How it Works</Link></li>
                            <li><Link href="#pricing" className="hover:text-primary transition-colors">Pricing</Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors flex items-center gap-1">Changelog <ArrowUpRight size={14} /></Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-white font-bold mb-6 font-outfit uppercase tracking-wider text-sm">Company</h4>
                        <ul className="space-y-4 text-gray-400">
                            <li><Link href="#" className="hover:text-primary transition-colors">About Us</Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors">Our Vision</Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors">Careers</Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors">Contact</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h4 className="text-white font-bold mb-6 font-outfit uppercase tracking-wider text-sm">Legal</h4>
                        <ul className="space-y-4 text-gray-400">
                            <li><Link href="#" className="hover:text-primary transition-colors">Privacy Policy</Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors">Terms of Service</Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors">Security</Link></li>
                            <li><Link href="#" className="hover:text-primary transition-colors">Cookies</Link></li>
                        </ul>
                    </div>
                </div>

                <div className="pt-12 border-t border-gray-800 flex flex-col md:flex-row justify-between items-center gap-6">
                    <p className="text-gray-500 font-inter text-sm">
                        © {new Date().getFullYear()} Vocaply AI. All rights reserved.
                    </p>
                    <div className="flex items-center gap-2 text-gray-500 text-sm">
                        <div className="w-2 h-2 rounded-full bg-success animate-pulse"></div>
                        All systems operational
                    </div>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
