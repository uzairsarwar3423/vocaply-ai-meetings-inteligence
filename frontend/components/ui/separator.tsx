import * as React from "react"
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs))
}

export interface SeparatorProps extends React.HTMLAttributes<HTMLDivElement> {
    orientation?: "horizontal" | "vertical"
    decorative?: boolean
}

const Separator = React.forwardRef<HTMLDivElement, SeparatorProps>(
    (
        { className, orientation = "horizontal", decorative = true, ...props },
        ref
    ) => {
        return (
            <div
                ref={ref}
                role={decorative ? "none" : "separator"}
                aria-orientation={decorative ? undefined : orientation}
                className={cn(
                    "shrink-0 bg-neutral-200 dark:bg-neutral-800",
                    orientation === "horizontal" ? "h-[1px] w-full" : "h-full w-[1px]",
                    className
                )}
                {...props}
            />
        )
    }
)
Separator.displayName = "Separator"

export { Separator }
