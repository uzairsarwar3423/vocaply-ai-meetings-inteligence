import * as React from "react";
import { cn } from "@/lib/utils";

export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
    src?: string;
    fallback?: string;
    size?: "sm" | "md" | "lg" | "xl";
}

const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
    ({ className, src, fallback, size = "md", ...props }, ref) => {
        const sizeClasses = {
            sm: "h-8 w-8 text-[10px]",
            md: "h-10 w-10 text-xs",
            lg: "h-14 w-14 text-base",
            xl: "h-20 w-20 text-xl",
        };

        return (
            <div
                ref={ref}
                className={cn(
                    "relative flex shrink-0 overflow-hidden rounded-full bg-primary-100 border-2 border-white shadow-sm transition-transform hover:scale-105",
                    sizeClasses[size],
                    className
                )}
                {...props}
            >
                {src ? (
                    <img
                        src={src}
                        alt={fallback || "avatar"}
                        className="aspect-square h-full w-full object-cover"
                    />
                ) : (
                    <div className="flex h-full w-full items-center justify-center font-bold text-primary-700 uppercase">
                        {fallback?.substring(0, 2) || "?"}
                    </div>
                )}
            </div>
        );
    }
);
Avatar.displayName = "Avatar";

export { Avatar };
