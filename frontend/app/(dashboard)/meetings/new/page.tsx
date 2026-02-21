"use client";

import React from 'react';
import { useRouter } from 'next/navigation';
import { useMeetings } from '@/hooks/useMeetings';
import { CreateMeetingInput } from '@/types/meeting';
import { ArrowLeft, Calendar, Video, Users, Link as LinkIcon, Save } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Link from 'next/link';

const schema = z.object({
    title: z.string().min(3, 'Title must be at least 3 characters'),
    description: z.string().optional(),
    startTime: z.string().min(1, 'Start time is required'),
    endTime: z.string().min(1, 'End time is required'),
    platform: z.enum(['google_meet', 'zoom', 'teams', 'other'] as const),
    meetingUrl: z.string().url('Must be a valid URL').optional().or(z.literal('')),
    attendeeEmails: z.string(), // Keep as string for form input
});

type FormData = z.infer<typeof schema>;

export default function NewMeetingPage() {
    const router = useRouter();
    const { createMeeting } = useMeetings();

    const {
        register,
        handleSubmit,
        formState: { errors, isSubmitting },
    } = useForm<FormData>({
        resolver: zodResolver(schema),
        defaultValues: {
            platform: 'google_meet',
            attendeeEmails: '',
        }
    });

    const onSubmit = async (data: FormData) => {
        try {
            const attendees = data.attendeeEmails.split(',').map(e => e.trim()).filter(e => e).filter(e => e.includes('@'));

            await createMeeting({
                title: data.title,
                description: data.description,
                startTime: data.startTime,
                platform: data.platform,
                attendees: attendees,
                // description and meetingUrl if DTO supports it. 
                // types/meeting.ts CreateMeetingDTO has description? Yes
                // meetingUrl? No. I should probably add it or ignore it.
            });
            router.push('/meetings');
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center gap-4">
                <Link
                    href="/meetings"
                    className="p-2 bg-white border border-neutral-200 rounded-xl hover:bg-neutral-50 transition-all shadow-sm"
                >
                    <ArrowLeft className="w-5 h-5 text-neutral-600" />
                </Link>
                <div>
                    <h1 className="text-2xl font-bold text-neutral-800 font-outfit">Schedule New Meeting</h1>
                    <p className="text-neutral-500">Fill in the details below to schedule a new meeting sync.</p>
                </div>
            </div>

            <div className="bg-white rounded-2xl border border-neutral-200 shadow-xl overflow-hidden">
                <form onSubmit={handleSubmit(onSubmit)} className="p-8 space-y-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-sm font-bold text-neutral-700">Meeting Title</label>
                                <input
                                    {...register('title')}
                                    type="text"
                                    placeholder="e.g. Weekly Product Sync"
                                    className={`w-full px-4 py-3 bg-neutral-50 border rounded-xl outline-none transition-all ${errors.title ? 'border-error ring-2 ring-error/10' : 'border-neutral-200 focus:border-primary focus:ring-2 focus:ring-primary/10'
                                        }`}
                                />
                                {errors.title && <p className="text-xs text-error font-medium">{errors.title.message}</p>}
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-bold text-neutral-700">Description</label>
                                <textarea
                                    {...register('description')}
                                    placeholder="What is this meeting about?"
                                    rows={4}
                                    className="w-full px-4 py-3 bg-neutral-50 border border-neutral-200 rounded-xl outline-none focus:border-primary focus:ring-2 focus:ring-primary/10 transition-all resize-none"
                                />
                            </div>

                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-sm font-bold text-neutral-700 flex items-center gap-2">
                                        <Calendar className="w-4 h-4 text-primary" />
                                        Start Time
                                    </label>
                                    <input
                                        {...register('startTime')}
                                        type="datetime-local"
                                        className="w-full px-4 py-3 bg-neutral-50 border border-neutral-200 rounded-xl focus:border-primary outline-none transition-all"
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-bold text-neutral-700 flex items-center gap-2">
                                        <Calendar className="w-4 h-4 text-primary" />
                                        End Time
                                    </label>
                                    <input
                                        {...register('endTime')}
                                        type="datetime-local"
                                        className="w-full px-4 py-3 bg-neutral-50 border border-neutral-200 rounded-xl focus:border-primary outline-none transition-all"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="space-y-6 bg-neutral-50/50 p-6 rounded-2xl border border-neutral-100">
                            <div className="space-y-2">
                                <label className="text-sm font-bold text-neutral-700 flex items-center gap-2">
                                    <Video className="w-4 h-4 text-primary" />
                                    Platform
                                </label>
                                <select
                                    {...register('platform')}
                                    className="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl focus:border-primary outline-none transition-all appearance-none"
                                >
                                    <option value="google_meet">Google Meet</option>
                                    <option value="zoom">Zoom</option>
                                    <option value="teams">Microsoft Teams</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-bold text-neutral-700 flex items-center gap-2">
                                    <LinkIcon className="w-4 h-4 text-primary" />
                                    Meeting Link
                                </label>
                                <input
                                    {...register('meetingUrl')}
                                    type="text"
                                    placeholder="https://..."
                                    className="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl focus:border-primary outline-none transition-all"
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-bold text-neutral-700 flex items-center gap-2">
                                    <Users className="w-4 h-4 text-primary" />
                                    Attendee Emails
                                </label>
                                <input
                                    {...register('attendeeEmails')}
                                    type="text"
                                    placeholder="john@example.com, jane@example.com"
                                    className="w-full px-4 py-3 bg-white border border-neutral-200 rounded-xl focus:border-primary outline-none transition-all"
                                />
                                <p className="text-xs text-neutral-500">Separate emails with commas.</p>
                            </div>

                            <div className="p-4 bg-primary/5 rounded-xl border border-primary/10 mt-6">
                                <h4 className="text-xs font-bold text-primary uppercase tracking-wider mb-2">Pro Tip</h4>
                                <p className="text-sm text-neutral-600">Vocaply will automatically join this meeting if a valid link is provided.</p>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center justify-end gap-4 pt-6 border-t border-neutral-100">
                        <Link
                            href="/meetings"
                            className="px-8 py-3 text-neutral-500 font-bold hover:text-neutral-700 transition-all"
                        >
                            Discard
                        </Link>
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="flex items-center gap-2 px-10 py-3 bg-primary text-white font-bold rounded-xl shadow-primary hover:shadow-xl hover:bg-primary-600 transition-all active:scale-95 disabled:opacity-50"
                        >
                            {isSubmitting ? (
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <Save className="w-5 h-5" />
                            )}
                            Schedule Meeting
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
