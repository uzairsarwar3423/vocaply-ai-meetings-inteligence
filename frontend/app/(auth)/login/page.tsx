"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card";
import { authService } from "@/lib/auth/auth";

const loginSchema = z.object({
    email: z.string().email("Invalid email address"),
    password: z.string().min(6, "Password must be at least 6 characters"),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginFormValues>({
        resolver: zodResolver(loginSchema),
    });

    const onSubmit = async (data: LoginFormValues) => {
        setIsLoading(true);
        try {
            await authService.login(data);
            toast.success("Welcome back!");
            router.push("/dashboard");
        } catch (error: any) {
            const message = error.response?.data?.detail || "Invalid email or password";
            toast.error(message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card className="border-none shadow-none md:shadow-xl">
            <CardHeader>
                <h2 className="text-2xl font-outfit font-bold text-gray-900">Sign In</h2>
                <p className="text-gray-500 font-inter text-sm mt-1">
                    Enter your credentials to access your workspace.
                </p>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    <Input
                        label="Email Address"
                        type="email"
                        placeholder="name@company.com"
                        error={errors.email?.message}
                        {...register("email")}
                    />
                    <div className="space-y-1">
                        <div className="flex items-center justify-between">
                            <label className="block text-sm font-medium text-gray-700 font-outfit">
                                Password
                            </label>
                            <Link
                                href="/forgot-password"
                                className="text-xs font-semibold text-primary hover:text-primary-600 font-outfit"
                            >
                                Forgot?
                            </Link>
                        </div>
                        <Input
                            type="password"
                            placeholder="••••••••"
                            error={errors.password?.message}
                            {...register("password")}
                        />
                    </div>
                    <Button type="submit" className="w-full" isLoading={isLoading}>
                        Sign In
                    </Button>
                </form>
            </CardContent>
            <CardFooter className="flex flex-col gap-4">
                <div className="relative w-full">
                    <div className="absolute inset-0 flex items-center">
                        <span className="w-full border-t border-gray-100" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                        <span className="bg-white px-2 text-gray-400 font-inter font-medium">
                            New to Vocaply?
                        </span>
                    </div>
                </div>
                <Link href="/register" className="w-full">
                    <Button variant="outline" className="w-full">
                        Create Account
                    </Button>
                </Link>
            </CardFooter>
        </Card>
    );
}
