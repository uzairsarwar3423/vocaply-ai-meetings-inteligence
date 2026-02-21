import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: "primary" | "secondary" | "success" | "warning" | "error" | "info" | "neutral";
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
    ({ className, variant = "primary", ...props }, ref) => {
        const variants = {
            primary: "bg-primary-50 text-primary-700 border-primary-200",
            secondary: "bg-secondary-50 text-secondary-700 border-secondary-200",
            success: "bg-emerald-50 text-emerald-700 border-emerald-200",
            warning: "bg-amber-50 text-amber-700 border-amber-200",
            error: "bg-rose-50 text-rose-700 border-rose-200",
            info: "bg-sky-50 text-sky-700 border-sky-200",
            neutral: "bg-neutral-100 text-neutral-700 border-neutral-200",
        };

        return (
            <div
                ref={ref}
                className={cn(
                    "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border transition-colors",
                    variants[variant],
                    className
                )}
                {...props}
            />
        );
    }
);
Badge.displayName = "Badge";

export { Badge };
