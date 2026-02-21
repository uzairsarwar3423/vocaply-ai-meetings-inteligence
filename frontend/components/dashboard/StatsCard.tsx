import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown } from 'lucide-react';

export interface StatsCardProps {
    label: string;
    value: string | number;
    icon: React.ElementType;
    trend?: {
        value: number;
        isUp: boolean;
    };
    color?: "primary" | "secondary" | "success" | "info";
    className?: string;
}

const StatsCard: React.FC<StatsCardProps> = ({
    label,
    value,
    icon: Icon,
    trend,
    color = "primary",
    className,
}) => {
    const colorMap = {
        primary: "bg-primary-50 text-primary-600 shadow-primary",
        secondary: "bg-secondary-50 text-secondary-600 shadow-secondary",
        success: "bg-emerald-50 text-emerald-600",
        info: "bg-sky-50 text-sky-600",
    };

    return (
        <Card className={cn("group hover:-translate-y-1 transition-all duration-300", className)}>
            <CardContent className="p-6">
                <div className="flex items-center justify-between">
                    <div className={cn(
                        "p-3 rounded-2xl transition-colors duration-300",
                        colorMap[color]
                    )}>
                        <Icon className="w-6 h-6" />
                    </div>
                    {trend && (
                        <div className={cn(
                            "flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full",
                            trend.isUp ? "bg-emerald-50 text-emerald-600" : "bg-rose-50 text-rose-600"
                        )}>
                            {trend.isUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                            {trend.value}%
                        </div>
                    )}
                </div>
                <div className="mt-4">
                    <p className="text-sm font-medium text-neutral-500">{label}</p>
                    <h3 className="text-2xl font-bold text-neutral-900 mt-1">{value}</h3>
                </div>
            </CardContent>
        </Card>
    );
};

export default StatsCard;
