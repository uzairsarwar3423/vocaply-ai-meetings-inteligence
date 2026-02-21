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

const registerSchema = z.object({
    full_name: z.string().min(2, "Full name must be at least 2 characters"),
    email: z.string().email("Invalid email address"),
    company_name: z.string().min(2, "Company name must be at least 2 characters"),
    password: z.string().min(6, "Password must be at least 6 characters"),
});

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<RegisterFormValues>({
        resolver: zodResolver(registerSchema),
    });

    const onSubmit = async (data: RegisterFormValues) => {
        setIsLoading(true);
        try {
            await authService.register(data);
            toast.success("Account created! Please sign in.");
            router.push("/login");
        } catch (error: any) {
            const message = error.response?.data?.detail || "Something went wrong. Please try again.";
            toast.error(message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card className="border-none shadow-none md:shadow-xl">
            <CardHeader>
                <h2 className="text-2xl font-outfit font-bold text-gray-900">Create Account</h2>
                <p className="text-gray-500 font-inter text-sm mt-1">
                    Start your free trial and automate your meetings.
                </p>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                    <Input
                        label="Full Name"
                        placeholder="John Doe"
                        error={errors.full_name?.message}
                        {...register("full_name")}
                    />
                    <Input
                        label="Email Address"
                        type="email"
                        placeholder="name@company.com"
                        error={errors.email?.message}
                        {...register("email")}
                    />
                    <Input
                        label="Company Name"
                        placeholder="Acme Inc."
                        error={errors.company_name?.message}
                        {...register("company_name")}
                    />
                    <Input
                        label="Password"
                        type="password"
                        placeholder="••••••••"
                        error={errors.password?.message}
                        {...register("password")}
                    />
                    <p className="text-[11px] text-gray-400 font-inter leading-relaxed">
                        By clicking "Create Account", you agree to our{" "}
                        <Link href="#" className="underline">Terms of Service</Link> and{" "}
                        <Link href="#" className="underline">Privacy Policy</Link>.
                    </p>
                    <Button type="submit" className="w-full" isLoading={isLoading}>
                        Create Account
                    </Button>
                </form>
            </CardContent>
            <CardFooter className="flex flex-col gap-4 text-center">
                <p className="text-sm font-inter text-gray-500">
                    Already have an account?{" "}
                    <Link href="/login" className="font-semibold text-primary hover:text-primary-600 font-outfit">
                        Sign In
                    </Link>
                </p>
            </CardFooter>
        </Card>
    );
}
