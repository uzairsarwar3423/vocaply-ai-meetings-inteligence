'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Settings, Save, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/useToast';

interface AutoJoinSettingsProps {
    initialSettings?: {
        enabledByDefault: boolean;
        minutesBefore: number;
        autoRecordAll: boolean;
        autoTranscribeAll: boolean;
    };
}

export default function AutoJoinSettings({ initialSettings }: AutoJoinSettingsProps) {
    const [settings, setSettings] = useState({
        enabledByDefault: initialSettings?.enabledByDefault ?? false,
        minutesBefore: initialSettings?.minutesBefore ?? 2,
        autoRecordAll: initialSettings?.autoRecordAll ?? true,
        autoTranscribeAll: initialSettings?.autoTranscribeAll ?? true,
    });
    const [isSaving, setIsSaving] = useState(false);
    const { toast } = useToast();

    const handleSave = async () => {
        setIsSaving(true);

        try {
            // In production, save to backend
            await new Promise(resolve => setTimeout(resolve, 1000));

            toast({
                title: 'Settings Saved',
                description: 'Your auto-join preferences have been updated.',
            });
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

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    Auto-Join Settings
                </CardTitle>
                <CardDescription>
                    Configure default behavior for automatically joining meetings
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
                {/* Enable by Default */}
                <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                        <Label htmlFor="enabled-default">Enable auto-join by default</Label>
                        <div className="text-sm text-gray-500">
                            Automatically enable auto-join for all new calendar events with meeting URLs
                        </div>
                    </div>
                    <Switch
                        id="enabled-default"
                        checked={settings.enabledByDefault}
                        onCheckedChange={(checked) =>
                            setSettings(prev => ({ ...prev, enabledByDefault: checked }))
                        }
                    />
                </div>

                {/* Minutes Before */}
                <div className="space-y-2">
                    <Label htmlFor="minutes-before">Join meeting (minutes before)</Label>
                    <div className="text-sm text-gray-500 mb-2">
                        Bot will join this many minutes before the scheduled start time
                    </div>
                    <select
                        id="minutes-before"
                        value={settings.minutesBefore}
                        onChange={(e) =>
                            setSettings(prev => ({ ...prev, minutesBefore: parseInt(e.target.value) }))
                        }
                        className="w-full px-3 py-2 border rounded-md"
                    >
                        <option value={0}>At start time</option>
                        <option value={1}>1 minute before</option>
                        <option value={2}>2 minutes before</option>
                        <option value={5}>5 minutes before</option>
                    </select>
                </div>

                {/* Auto Record */}
                <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                        <Label htmlFor="auto-record">Auto-record all meetings</Label>
                        <div className="text-sm text-gray-500">
                            Automatically start recording when bot joins
                        </div>
                    </div>
                    <Switch
                        id="auto-record"
                        checked={settings.autoRecordAll}
                        onCheckedChange={(checked) =>
                            setSettings(prev => ({ ...prev, autoRecordAll: checked }))
                        }
                    />
                </div>

                {/* Auto Transcribe */}
                <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                        <Label htmlFor="auto-transcribe">Auto-transcribe all recordings</Label>
                        <div className="text-sm text-gray-500">
                            Automatically transcribe recordings after meeting ends
                        </div>
                    </div>
                    <Switch
                        id="auto-transcribe"
                        checked={settings.autoTranscribeAll}
                        onCheckedChange={(checked) =>
                            setSettings(prev => ({ ...prev, autoTranscribeAll: checked }))
                        }
                    />
                </div>

                {/* Save Button */}
                <div className="pt-4 border-t">
                    <Button onClick={handleSave} disabled={isSaving} className="w-full sm:w-auto">
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
                </div>
            </CardContent>
        </Card>
    );
}