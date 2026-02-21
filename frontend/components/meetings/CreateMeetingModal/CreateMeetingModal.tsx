import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { X, Calendar, Clock, Video, Users, Link as LinkIcon, Sparkles } from 'lucide-react';
import { CreateMeetingDTO } from '../../../types/meeting';

const schema = z.object({
    title: z.string().min(3, 'Title must be at least 3 characters'),
    description: z.string().optional(),
    startTime: z.string().min(1, 'Start time is required'),
    endTime: z.string().min(1, 'End time is required'),
    platform: z.enum(['google_meet', 'zoom', 'teams', 'other'] as const),
    meetingUrl: z.string().url('Must be a valid URL').optional().or(z.literal('')),
    attendeeEmails: z.string().optional(),
});

type FormData = z.infer<typeof schema>;

interface CreateMeetingModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: CreateMeetingDTO) => Promise<void>;
    isSubmitting: boolean;
}

export const CreateMeetingModal: React.FC<CreateMeetingModalProps> = ({
    isOpen,
    onClose,
    onSubmit,
    isSubmitting,
}) => {
    const {
        register,
        handleSubmit,
        reset,
        formState: { errors },
    } = useForm<FormData>({
        resolver: zodResolver(schema),
        defaultValues: {
            platform: 'google_meet',
            attendeeEmails: '',
        }
    });

    React.useEffect(() => {
        if (!isOpen) {
            reset();
        }
    }, [isOpen, reset]);

    if (!isOpen) return null;

    const handleFormSubmit = async (data: FormData) => {
        try {
            const { attendeeEmails, startTime, endTime, meetingUrl, ...rest } = data;
            await onSubmit({
                ...rest,
                startTime,
                // Pass these as extra fields — useMeetings transformer will pick them up
                ...(endTime ? { endTime } : {}),
                ...(meetingUrl ? { meetingUrl } : {}),
                attendees: attendeeEmails
                    ? attendeeEmails.split(',').map(e => e.trim()).filter(e => e)
                    : [],
            } as any);
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-in fade-in duration-300">
            <div className="bg-white w-full max-w-2xl rounded-[32px] shadow-2xl overflow-hidden animate-in zoom-in-95 slide-in-from-bottom-8 duration-500">
                {/* Header */}
                <div className="relative p-8 bg-gradient-to-br from-neutral-50 to-white border-b border-neutral-100">
                    <button
                        onClick={onClose}
                        className="absolute right-6 top-6 p-2 text-neutral-400 hover:text-neutral-900 hover:bg-neutral-100 rounded-full transition-all"
                    >
                        <X className="w-5 h-5" />
                    </button>
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-10 h-10 bg-primary/10 rounded-2xl flex items-center justify-center">
                            <Sparkles className="w-6 h-6 text-primary" />
                        </div>
                        <h2 className="text-2xl font-bold text-neutral-900 font-outfit">Schedule Meeting</h2>
                    </div>
                    <p className="text-neutral-500 text-sm font-medium">Configure your meeting workspace and invites.</p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit(handleFormSubmit)} className="p-8 space-y-6 max-h-[70vh] overflow-y-auto custom-scrollbar">
                    <div className="space-y-6">
                        {/* Title */}
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider">Meeting Title</label>
                            <input
                                {...register('title')}
                                type="text"
                                placeholder="e.g. Weekly Product Strategy Sync"
                                className={`w-full px-5 py-3.5 bg-neutral-50 border rounded-2xl outline-none transition-all font-medium ${errors.title ? 'border-error ring-4 ring-error/5' : 'border-neutral-100 focus:border-primary focus:ring-4 focus:ring-primary/5 focus:bg-white'
                                    }`}
                            />
                            {errors.title && <p className="text-xs text-error font-bold mt-1 ml-1">{errors.title.message}</p>}
                        </div>

                        {/* Times */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider flex items-center gap-2">
                                    <Calendar className="w-3.5 h-3.5" />
                                    Start Time
                                </label>
                                <input
                                    {...register('startTime')}
                                    type="datetime-local"
                                    className="w-full px-5 py-3.5 bg-neutral-50 border border-neutral-100 rounded-2xl outline-none focus:border-primary focus:ring-4 focus:ring-primary/5 focus:bg-white transition-all font-medium"
                                />
                                {errors.startTime && <p className="text-xs text-error font-bold mt-1 ml-1">{errors.startTime.message}</p>}
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider flex items-center gap-2">
                                    <Clock className="w-3.5 h-3.5" />
                                    End Time
                                </label>
                                <input
                                    {...register('endTime')}
                                    type="datetime-local"
                                    className="w-full px-5 py-3.5 bg-neutral-50 border border-neutral-100 rounded-2xl outline-none focus:border-primary focus:ring-4 focus:ring-primary/5 focus:bg-white transition-all font-medium"
                                />
                                {errors.endTime && <p className="text-xs text-error font-bold mt-1 ml-1">{errors.endTime.message}</p>}
                            </div>
                        </div>

                        {/* Platform & Link */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider flex items-center gap-2">
                                    <Video className="w-3.5 h-3.5" />
                                    Platform
                                </label>
                                <select
                                    {...register('platform')}
                                    className="w-full px-5 py-3.5 bg-neutral-50 border border-neutral-100 rounded-2xl outline-none focus:border-primary focus:ring-4 focus:ring-primary/5 focus:bg-white transition-all font-medium appearance-none"
                                >
                                    <option value="google_meet">Google Meet</option>
                                    <option value="zoom">Zoom</option>
                                    <option value="teams">Microsoft Teams</option>
                                    <option value="other">Other</option>
                                </select>
                            </div>
                            <div className="space-y-2">
                                <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider flex items-center gap-2">
                                    <LinkIcon className="w-3.5 h-3.5" />
                                    Link
                                </label>
                                <input
                                    {...register('meetingUrl')}
                                    type="text"
                                    placeholder="https://meet.google.com/..."
                                    className="w-full px-5 py-3.5 bg-neutral-50 border border-neutral-100 rounded-2xl outline-none focus:border-primary focus:ring-4 focus:ring-primary/5 focus:bg-white transition-all font-medium"
                                />
                            </div>
                        </div>

                        {/* Attendees */}
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-neutral-400 uppercase tracking-wider flex items-center gap-2">
                                <Users className="w-3.5 h-3.5" />
                                Attendees (Comma separated)
                            </label>
                            <input
                                {...register('attendeeEmails')}
                                type="text"
                                placeholder="john@example.com, jane@example.com"
                                className="w-full px-5 py-3.5 bg-neutral-50 border border-neutral-100 rounded-2xl outline-none focus:border-primary focus:ring-4 focus:ring-primary/5 focus:bg-white transition-all font-medium"
                            />
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center justify-end gap-3 pt-8 pb-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-8 py-3.5 text-neutral-500 font-bold hover:text-neutral-900 transition-all"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="px-10 py-3.5 bg-primary text-white font-bold rounded-2xl shadow-primary hover:shadow-xl hover:bg-primary-600 transition-all active:scale-95 disabled:opacity-50 disabled:pointer-events-none min-w-[160px]"
                        >
                            {isSubmitting ? (
                                <div className="flex items-center justify-center gap-2">
                                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    Scheduling...
                                </div>
                            ) : (
                                'Schedule Meeting'
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
