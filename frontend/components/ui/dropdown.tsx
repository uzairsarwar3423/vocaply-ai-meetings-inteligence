import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { ChevronDown } from "lucide-react";

interface DropdownContextType {
    isOpen: boolean;
    setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
    toggle: () => void;
    close: () => void;
}

const DropdownContext = React.createContext<DropdownContextType | undefined>(undefined);

function useDropdown() {
    const context = React.useContext(DropdownContext);
    if (!context) {
        throw new Error("useDropdown must be used within a Dropdown");
    }
    return context;
}

interface DropdownProps {
    children: React.ReactNode;
    defaultOpen?: boolean;
    onOpenChange?: (open: boolean) => void;
}

const Dropdown: React.FC<DropdownProps> = ({ children, defaultOpen = false, onOpenChange }) => {
    const [isOpen, setIsOpen] = React.useState(defaultOpen);
    const containerRef = React.useRef<HTMLDivElement>(null);

    const handleOpenChange = React.useCallback((open: boolean) => {
        setIsOpen(open);
        onOpenChange?.(open);
    }, [onOpenChange]);

    const toggle = React.useCallback(() => handleOpenChange(!isOpen), [isOpen, handleOpenChange]);
    const close = React.useCallback(() => handleOpenChange(false), [handleOpenChange]);

    React.useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
                close();
            }
        };

        const handleEscape = (event: KeyboardEvent) => {
            if (event.key === "Escape") {
                close();
            }
        };

        if (isOpen) {
            document.addEventListener("mousedown", handleClickOutside);
            document.addEventListener("keydown", handleEscape);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
            document.removeEventListener("keydown", handleEscape);
        };
    }, [isOpen, close]);

    return (
        <DropdownContext.Provider value={{ isOpen, setIsOpen, toggle, close }}>
            <div ref={containerRef} className="relative inline-block text-left">
                {children}
            </div>
        </DropdownContext.Provider>
    );
};

interface DropdownTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    asChild?: boolean;
}

const DropdownTrigger = React.forwardRef<HTMLButtonElement, DropdownTriggerProps>(
    ({ className, children, asChild = false, ...props }, ref) => {
        const { toggle, isOpen } = useDropdown();

        if (asChild && React.isValidElement(children)) {
            const child = children as React.ReactElement<any>;
            return React.cloneElement(child, {
                onClick: (e: React.MouseEvent) => {
                    child.props.onClick?.(e);
                    toggle();
                },
                "aria-expanded": isOpen,
                "data-state": isOpen ? "open" : "closed",
                ref,
                ...props,
            });
        }

        return (
            <button
                ref={ref}
                onClick={toggle}
                className={cn(
                    "inline-flex items-center justify-center gap-2 rounded-xl bg-white px-4 py-2.5 text-sm font-medium text-neutral-700 shadow-sm ring-1 ring-inset ring-neutral-200 hover:bg-neutral-50 transition-all active:scale-95 focus:outline-none focus:ring-2 focus:ring-primary/20",
                    isOpen && "ring-primary/30 bg-primary/5 text-primary",
                    className
                )}
                aria-expanded={isOpen}
                data-state={isOpen ? "open" : "closed"}
                {...props}
            >
                {children}
                <ChevronDown
                    className={cn(
                        "h-4 w-4 text-neutral-400 transition-transform duration-200",
                        isOpen && "rotate-180 text-primary"
                    )}
                />
            </button>
        );
    }
);
DropdownTrigger.displayName = "DropdownTrigger";

interface DropdownContentProps {
    children: React.ReactNode;
    className?: string;
    align?: "start" | "end" | "center";
    sideOffset?: number;
    width?: number | string;
}

const DropdownContent: React.FC<DropdownContentProps> = ({
    children,
    className,
    align = "end",
    sideOffset = 4,
    width = 240,
}) => {
    const { isOpen } = useDropdown();

    const alignClass = {
        start: "left-0 origin-top-left",
        end: "right-0 origin-top-right",
        center: "left-1/2 -translate-x-1/2 origin-top",
    }[align];

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }} // smooth apple-like spring
                    className={cn(
                        "absolute z-50 mt-2 rounded-2xl bg-white/80 backdrop-blur-xl border border-white/20 shadow-xl ring-1 ring-black/5 p-1.5 focus:outline-none", // Glassmorphic
                        alignClass,
                        className
                    )}
                    style={{ width, marginTop: sideOffset }}
                >
                    {children}
                </motion.div>
            )}
        </AnimatePresence>
    );
};

interface DropdownItemProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    icon?: React.ReactNode;
    shortcut?: string;
    variant?: "default" | "destructive" | "primary";
}

const DropdownItem = React.forwardRef<HTMLButtonElement, DropdownItemProps>(
    ({ className, children, icon, shortcut, variant = "default", onClick, ...props }, ref) => {
        const { close } = useDropdown();

        const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
            onClick?.(e);
            close();
        };

        const variantStyles = {
            default: "text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900",
            primary: "text-primary hover:bg-primary/10 hover:text-primary-700",
            destructive: "text-red-600 hover:bg-red-50 hover:text-red-700",
        };

        return (
            <button
                ref={ref}
                onClick={handleClick}
                className={cn(
                    "group flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-sm font-medium transition-all outline-none",
                    variantStyles[variant],
                    className
                )}
                {...props}
            >
                {icon && (
                    <span className={cn(
                        "flex h-5 w-5 items-center justify-center transition-colors",
                        variant === 'destructive' ? "text-red-500 group-hover:text-red-600" : "text-neutral-400 group-hover:text-neutral-600",
                        variant === 'primary' && "text-primary group-hover:text-primary-700"
                    )}>
                        {icon}
                    </span>
                )}
                <span className="flex-1 text-left line-clamp-1">{children}</span>
                {shortcut && <span className="text-xs text-neutral-400 font-sans tracking-wide">{shortcut}</span>}
            </button>
        );
    }
);
DropdownItem.displayName = "DropdownItem";

const DropdownLabel: React.FC<{ children: React.ReactNode; className?: string }> = ({
    children,
    className,
}) => {
    return (
        <div className={cn("px-3 py-2 text-xs font-bold text-neutral-400 uppercase tracking-wider", className)}>
            {children}
        </div>
    );
};

const DropdownSeparator: React.FC<{ className?: string }> = ({ className }) => {
    return <div className={cn("-mx-1 my-1 h-px bg-neutral-100", className)} />;
};

export {
    Dropdown,
    DropdownTrigger,
    DropdownContent,
    DropdownItem,
    DropdownLabel,
    DropdownSeparator,
};
