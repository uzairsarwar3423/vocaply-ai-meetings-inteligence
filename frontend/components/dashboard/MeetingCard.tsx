import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar } from '@/components/ui/avatar';
import { Calendar, Clock, MoreVertical, PlayCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface MeetingCardProps {
    title: string;
    date: string;
    duration: string;
    participants: { name: string; avatar?: string }[];
    status: "processed" | "processing" | "failed";
    thumbnail?: string;
    className?: string;
}

const MeetingCard: React.FC<MeetingCardProps> = ({
    title,
    date,
    duration,
    participants,
    status,
    thumbnail,
    className,
}) => {
    return (
        <Card className={cn("group overflow-hidden border-neutral-100", className)}>
            <div className="relative aspect-video bg-neutral-100 overflow-hidden">
                {thumbnail ? (
                    <img src={thumbnail} alt={title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50">
                        <PlayCircle className="w-12 h-12 text-primary/20 group-hover:text-primary transition-colors" />
                    </div>
                )}
                <div className="absolute top-3 right-3">
                    <Badge
                        variant={status === "processed" ? "success" : status === "processing" ? "warning" : "error"}
                        className="capitalize backdrop-blur-md"
                    >
                        {status}
                    </Badge>
                </div>
                <div className="absolute bottom-3 left-3 bg-black/50 backdrop-blur-md text-white px-2 py-1 rounded-lg text-xs font-medium flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {duration}
                </div>
            </div>

            <CardContent className="p-4">
                <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                        <h4 className="text-base font-bold text-neutral-900 truncate group-hover:text-primary transition-colors">{title}</h4>
                        <div className="flex items-center gap-3 mt-1.5 text-xs text-neutral-500">
                            <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {date}
                            </span>
                        </div>
                    </div>
                    <button className="p-1.5 rounded-full hover:bg-neutral-100 transition-colors text-neutral-400">
                        <MoreVertical className="w-4 h-4" />
                    </button>
                </div>

                <div className="flex items-center justify-between mt-4">
                    <div className="flex -space-x-2">
                        {participants.slice(0, 3).map((p, i) => (
                            <Avatar key={i} fallback={p.name} size="sm" className="ring-2 ring-white" />
                        ))}
                        {participants.length > 3 && (
                            <div className="h-8 w-8 rounded-full bg-neutral-100 border-2 border-white flex items-center justify-center text-[10px] font-bold text-neutral-500">
                                +{participants.length - 3}
                            </div>
                        )}
                    </div>
                    <button className="text-xs font-bold text-primary hover:underline transition-all">
                        View Details
                    </button>
                </div>
            </CardContent>
        </Card>
    );
};

export default MeetingCard;
