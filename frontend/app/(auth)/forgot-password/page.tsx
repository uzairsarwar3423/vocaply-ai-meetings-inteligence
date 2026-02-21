"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardContent, CardFooter, CardTitle, CardDescription } from "@/components/ui/card";
import { ChevronLeft } from "lucide-react";

export default function ForgotPasswordPage() {
    return (
        <Card className="border-none shadow-none md:shadow-xl">
            <CardHeader>
                <div className="mb-4">
                    <Link href="/login" className="text-sm font-semibold text-gray-500 hover:text-primary flex items-center gap-1 transition-colors">
                        <ChevronLeft size={16} />
                        Back to Login
                    </Link>
                </div>
                <CardTitle>Reset Password</CardTitle>
                <CardDescription>
                    Enter your email address and we'll send you a link to reset your password.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <form className="space-y-4">
                    <Input
                        label="Email Address"
                        type="email"
                        placeholder="name@company.com"
                    />
                    <Button className="w-full">
                        Send Reset Link
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
}
