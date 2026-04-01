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
import { Github } from "lucide-react";
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

                <div className="mt-8">
                    <div className="relative">
                        <div className="absolute inset-0 flex items-center shadow-sm">
                            <span className="w-full border-t border-gray-100" />
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-white px-3 text-gray-400 font-inter font-medium tracking-wider">
                                Or sign up with
                            </span>
                        </div>
                    </div>

                    <div className="mt-6 grid grid-cols-2 gap-3">
                        <Button
                            variant="outline"
                            className="w-full h-11 px-4 gap-2 border-gray-200 hover:border-primary/30 hover:bg-primary/5 group transition-all duration-300"
                            onClick={() => authService.loginWithGoogle()}
                        >
                            <svg className="w-5 h-5 group-hover:scale-110 transition-transform" viewBox="0 0 24 24">
                                <path
                                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                                    fill="#4285F4"
                                />
                                <path
                                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                                    fill="#34A853"
                                />
                                <path
                                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
                                    fill="#FBBC05"
                                />
                                <path
                                    d="M12 5.38c1.62 0 3.06.56 4.21 1.66l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                                    fill="#EA4335"
                                />
                            </svg>
                            <span className="text-gray-600 font-outfit text-sm">Google</span>
                        </Button>
                        <Button variant="outline" className="w-full h-11 px-4 gap-2 border-gray-200 hover:border-black/30 hover:bg-black/5 group transition-all duration-300">
                            <Github className="w-5 h-5 group-hover:scale-110 transition-transform text-gray-900" />
                            <span className="text-gray-600 font-outfit text-sm">GitHub</span>
                        </Button>
                    </div>
                </div>
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
