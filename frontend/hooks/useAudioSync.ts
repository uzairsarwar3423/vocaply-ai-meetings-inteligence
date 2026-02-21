import { useState, useEffect, useRef, useCallback } from 'react';

export interface AudioSyncState {
    currentTime: number;
    duration: number;
    isPlaying: boolean;
    playbackRate: number;
    volume: number;
    activeSegmentId: string | null;
}

export const useAudioSync = (
    audioUrl: string | undefined,
    segments: { id: string; start_time: number; end_time: number }[]
) => {
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [playbackRate, setPlaybackRate] = useState(1);
    const [volume, setVolume] = useState(1);
    const [activeSegmentId, setActiveSegmentId] = useState<string | null>(null);
    const [hasAudio, setHasAudio] = useState(false);

    // Create and configure audio element
    useEffect(() => {
        if (!audioUrl) { setHasAudio(false); return; }

        const audio = new Audio(audioUrl);
        audioRef.current = audio;
        setHasAudio(true);

        const onTimeUpdate = () => {
            const t = audio.currentTime;
            setCurrentTime(t);
            // Find active segment
            const active = segments.find((s) => t >= s.start_time && t <= s.end_time);
            setActiveSegmentId(active?.id ?? null);
        };
        const onDurationChange = () => setDuration(audio.duration);
        const onPlay = () => setIsPlaying(true);
        const onPause = () => setIsPlaying(false);
        const onEnded = () => setIsPlaying(false);

        audio.addEventListener('timeupdate', onTimeUpdate);
        audio.addEventListener('durationchange', onDurationChange);
        audio.addEventListener('play', onPlay);
        audio.addEventListener('pause', onPause);
        audio.addEventListener('ended', onEnded);

        audio.playbackRate = playbackRate;
        audio.volume = volume;

        return () => {
            audio.pause();
            audio.removeEventListener('timeupdate', onTimeUpdate);
            audio.removeEventListener('durationchange', onDurationChange);
            audio.removeEventListener('play', onPlay);
            audio.removeEventListener('pause', onPause);
            audio.removeEventListener('ended', onEnded);
            audioRef.current = null;
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [audioUrl]);

    // Keyboard shortcut: Space = play/pause
    useEffect(() => {
        const handler = (e: KeyboardEvent) => {
            const target = e.target as HTMLElement;
            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA') return;
            if (e.code === 'Space') {
                e.preventDefault();
                togglePlayPause();
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    });

    const togglePlayPause = useCallback(() => {
        const audio = audioRef.current;
        if (!audio) return;
        if (isPlaying) audio.pause();
        else audio.play().catch(() => { });
    }, [isPlaying]);

    const seekTo = useCallback((time: number) => {
        const audio = audioRef.current;
        if (!audio) return;
        audio.currentTime = Math.max(0, Math.min(time, audio.duration || 0));
    }, []);

    const changePlaybackRate = useCallback((rate: number) => {
        setPlaybackRate(rate);
        if (audioRef.current) audioRef.current.playbackRate = rate;
    }, []);

    const changeVolume = useCallback((vol: number) => {
        setVolume(vol);
        if (audioRef.current) audioRef.current.volume = vol;
    }, []);

    return {
        hasAudio,
        currentTime,
        duration,
        isPlaying,
        playbackRate,
        volume,
        activeSegmentId,
        togglePlayPause,
        seekTo,
        changePlaybackRate,
        changeVolume,
        audioRef,
    };
};
