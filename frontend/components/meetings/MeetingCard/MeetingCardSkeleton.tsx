import React from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';

interface MeetingCardSkeletonProps {
    viewMode: 'grid' | 'list';
}

export const MeetingCardSkeleton: React.FC<MeetingCardSkeletonProps> = ({ viewMode }) => {
    if (viewMode === 'list') {
        return (
            <div className="bg-white rounded-2xl border border-neutral-100 p-4 flex items-center gap-6">
                <Skeleton className="w-12 h-12 rounded-xl flex-shrink-0" />
                <div className="flex-grow min-w-0 space-y-2">
                    <div className="flex items-center gap-3">
                        <Skeleton className="h-5 w-48 rounded-md" />
                        <Skeleton className="h-5 w-20 rounded-full" />
                    </div>
                    <div className="flex items-center gap-4">
                        <Skeleton className="h-4 w-24 rounded-md" />
                        <Skeleton className="h-4 w-20 rounded-md" />
                        <Skeleton className="h-4 w-24 rounded-md" />
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <Skeleton className="h-9 w-9 rounded-lg" />
                    <Skeleton className="h-5 w-5 rounded-full" />
                </div>
            </div>
        );
    }

    return (
        <Card className="h-full bg-white border-neutral-100 rounded-3xl overflow-hidden flex flex-col shadow-none">
            <CardHeader className="pb-4 pt-6 px-6 space-y-4">
                <div className="flex justify-between items-start">
                    <Skeleton className="h-10 w-10 rounded-xl" />
                    <Skeleton className="h-6 w-20 rounded-full" />
                </div>
                <Skeleton className="h-7 w-3/4 rounded-lg" />
            </CardHeader>
            <CardContent className="flex-grow pb-6 px-6 space-y-6">
                <div className="space-y-2">
                    <Skeleton className="h-4 w-full rounded-md" />
                    <Skeleton className="h-4 w-2/3 rounded-md" />
                </div>
                <div className="space-y-3">
                    <Skeleton className="h-4 w-32 rounded-md" />
                    <Skeleton className="h-4 w-40 rounded-md" />
                </div>
            </CardContent>
            <CardFooter className="pt-4 border-t border-neutral-50 mt-auto px-6 py-4 flex items-center justify-between bg-neutral-50/30">
                <div className="flex -space-x-2">
                    <Skeleton className="h-8 w-8 rounded-full border-2 border-white" />
                    <Skeleton className="h-8 w-8 rounded-full border-2 border-white" />
                    <Skeleton className="h-8 w-8 rounded-full border-2 border-white" />
                </div>
                <div className="flex gap-2">
                    <Skeleton className="h-8 w-8 rounded-lg" />
                    <Skeleton className="h-8 w-8 rounded-lg" />
                </div>
            </CardFooter>
        </Card>
    );
};
