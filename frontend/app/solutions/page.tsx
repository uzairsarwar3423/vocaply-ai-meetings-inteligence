"use client";

import React from "react";
import Navbar from "@/components/Navbar";
import Solutions from "@/components/Solutions";
import CTA from "@/components/CTA";
import Footer from "@/components/Footer";

export default function SolutionsPage() {
  return (
    <main className="min-h-screen">
      <Navbar />
      <Solutions />
      <CTA />
      <Footer />
    </main>
  );
}
