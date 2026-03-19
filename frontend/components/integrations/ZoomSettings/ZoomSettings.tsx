'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Loader2, Save, ExternalLink, Calendar, Plus, Video, Clock } from 'lucide-react';
import { useToast } from '@/hooks/useToast';
import { apiClient } from '@/lib/api/client';

interface ZoomSettingsProps {
    onClose: () => void;
}

interface ZoomMeeting {
    id: string;
    topic: string;
    start_time: string;
    duration: number;
    join_url: string;
}

export default function ZoomSettings({ onClose }: ZoomSettingsProps) {
    const [settings, setSettings] = useState({
        autoImportMeetings: true,
        autoJoinMeetings: false,
        autoRecordMeetings: true,
        syncCalendar: true,
    });

    const [meetings, setMeetings] = useState<ZoomMeeting[]>([]);
    const [isLoadingMeetings, setIsLoadingMeetings] = useState(true);
    const [isSaving, setIsSaving] = useState(false);

    const { toast } = useToast();

    useEffect(() => {
        fetchZoomSettings();
        fetchZoomMeetings();
    }, []);

    const fetchZoomSettings = async () => {
        try {
            const response = await apiClient.get('/integrations/zoom/settings');
            setSettings(response.data);
        } catch (error) {
            console.error('Failed to fetch settings:', error);
        }
    };

    const fetchZoomMeetings = async () => {
        try {
            const response = await apiClient.get('/integrations/zoom/meetings');
            setMeetings(response.data.meetings || []);
        } catch (error) {
            console.error('Failed to fetch meetings:', error);
        } finally {
            setIsLoadingMeetings(false);
        }
    };

    const handleSave = async () => {
        setIsSaving(true);

        try {
            await apiClient.put('/integrations/zoom/settings', settings);

            toast({
                title: 'Settings Saved',
                description: 'Your Zoom settings have been updated.',
            });

            onClose();
        } catch (error) {
            toast({
                title: 'Error',
                description: 'Failed to save settings',
                variant: 'destructive',
            });
        } finally {
            setIsSaving(false);
        }
    };

    const handleImportMeeting = async (meeting_id: string) => {
        try {
            await apiClient.post('/integrations/zoom/import-meeting', {
                zoom_meeting_id: meeting_id,
            });

            toast({
                title: 'Meeting Imported',
                description: 'Zoom meeting has been imported to your platform.',
            });
        } catch (error) {
            toast({
                title: 'Import Failed',
                description: 'Failed to import meeting',
                variant: 'destructive',
            });
        }
    };

    return (
        <div className="space-y-6">
            {/* Settings */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                        <Label htmlFor="auto-import">Auto-import meetings</Label>
                        <div className="text-sm text-gray-500">
                            Automatically import new Zoom meetings to the platform
                        </div>
                    </div>
                    <Switch
                        id="auto-import"
                        checked={settings.autoImportMeetings}
                        onCheckedChange={(checked) =>
                            setSettings(prev => ({ ...prev, autoImportMeetings: checked }))
                        }
                    />
                </div>

                <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                        <Label htmlFor="auto-join">Auto-join meetings</Label>
                        <div className="text-sm text-gray-500">
                            Automatically join imported meetings with a bot
                        </div>
                    </div>
                    <Switch
                        id="auto-join"
                        checked={settings.autoJoinMeetings}
                        onCheckedChange={(checked) =>
                            setSettings(prev => ({ ...prev, autoJoinMeetings: checked }))
                        }
                    />
                </div>

                <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                        <Label htmlFor="auto-record">Auto-record meetings</Label>
                        <div className="text-sm text-gray-500">
                            Automatically record when bot joins
                        </div>
                    </div>
                    <Switch
                        id="auto-record"
                        checked={settings.autoRecordMeetings}
                        onCheckedChange={(checked) =>
                            setSettings(prev => ({ ...prev, autoRecordMeetings: checked }))
                        }
                    />
                </div>

                <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                        <Label htmlFor="sync-calendar">Sync to calendar</Label>
                        <div className="text-sm text-gray-500">
                            Add Zoom meetings to your calendar
                        </div>
                    </div>
                    <Switch
                        id="sync-calendar"
                        checked={settings.syncCalendar}
                        onCheckedChange={(checked) =>
                            setSettings(prev => ({ ...prev, syncCalendar: checked }))
                        }
                    />
                </div>
            </div>

            <Separator />

            {/* Upcoming Meetings */}
            <div>
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    Upcoming Zoom Meetings
                </h3>

                {isLoadingMeetings ? (
                    <div className="flex items-center justify-center py-8">
                        <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
                    </div>
                ) : meetings.length === 0 ? (
                    <div className="text-center py-8 text-gray-500 text-sm">
                        No upcoming meetings found
                    </div>
                ) : (
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                        {meetings.slice(0, 5).map((meeting) => (
                            <div
                                key={meeting.id}
                                className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                            >
                                <div className="flex-1 min-w-0 flex items-center gap-3">
                                    <div className="p-1.5 bg-blue-50 rounded-lg">
                                        <Video className="h-4 w-4 text-blue-600" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="font-medium text-sm truncate">
                                            {meeting.topic}
                                        </div>
                                        <div className="text-xs text-gray-500 flex items-center gap-1">
                                            <Calendar className="h-3 w-3" />
                                            {new Date(meeting.start_time).toLocaleDateString()}
                                            <span className="mx-1">•</span>
                                            <Clock className="h-3 w-3" />
                                            {new Date(meeting.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            <span className="mx-1">•</span>
                                            {meeting.duration} min
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => window.open(meeting.join_url, '_blank')}
                                    >
                                        <ExternalLink className="h-3 w-3" />
                                    </Button>
                                    <Button
                                        size="sm"
                                        onClick={() => handleImportMeeting(meeting.id)}
                                        className="gap-1"
                                    >
                                        <Plus className="h-3 w-3" />
                                        Import
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
                <Button onClick={handleSave} disabled={isSaving} className="flex-1">
                    {isSaving ? (
                        <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Saving...
                        </>
                    ) : (
                        <>
                            <Save className="mr-2 h-4 w-4" />
                            Save Settings
                        </>
                    )}
                </Button>
                <Button onClick={onClose} variant="outline">
                    Cancel
                </Button>
            </div>
        </div>
    );
}