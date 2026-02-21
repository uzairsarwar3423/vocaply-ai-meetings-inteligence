/**
 * Common formatting utilities for data presentation.
 */

/**
 * Formats a date string or Date object to a localized date string.
 * @param date - Date string or object.
 * @param options - Intl.DateTimeFormatOptions.
 * @returns Formatted date string.
 */
export const formatDate = (
    date: string | Date | null | undefined,
    options: Intl.DateTimeFormatOptions = {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
    }
): string => {
    if (!date) return '';
    const d = new Date(date);
    return new Intl.DateTimeFormat('en-US', options).format(d);
};

/**
 * Formats a date string or Date object to a localized time string.
 * @param date - Date string or object.
 * @returns Formatted time string (e.g., "10:30 AM").
 */
export const formatTime = (date: string | Date | null | undefined): string => {
    if (!date) return '';
    const d = new Date(date);
    return new Intl.DateTimeFormat('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
    }).format(d);
};

/**
 * Formats a date string or Date object to a standard "Start - End" time range string.
 * @param start - Start date/time.
 * @param end - End date/time.
 * @returns Formatted range string (e.g., "Jan 1, 2024 • 10:00 AM - 11:00 AM").
 */
export const formatDateTimeRange = (
    start: string | Date,
    end: string | Date
): string => {
    const startDate = new Date(start);
    const endDate = new Date(end);

    const dateStr = formatDate(startDate);
    const startTime = formatTime(startDate);
    const endTime = formatTime(endDate);

    return `${dateStr} • ${startTime} - ${endTime}`;
};

/**
 * Formats duration in seconds to a human-readable string (e.g., "1h 30m" or "45m 12s").
 * @param seconds - Duration in seconds.
 * @returns Formatted duration string.
 */
export const formatDuration = (seconds: number): string => {
    if (!seconds || seconds < 0) return '0s';

    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);

    const parts = [];
    if (h > 0) parts.push(`${h}h`);
    if (m > 0) parts.push(`${m}m`);
    if (s > 0 && h === 0) parts.push(`${s}s`); // Only show seconds if less than an hour

    return parts.join(' ');
};

/**
 * Formats file size in bytes to a human-readable string (e.g., "1.5 MB").
 * @param bytes - Size in bytes.
 * @param decimals - Number of decimal places.
 * @returns Formatted size string.
 */
export const formatFileSize = (bytes: number, decimals: number = 2): string => {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Truncates a string to a specified length and adds an ellipsis.
 * @param str - The string to truncate.
 * @param length - Maximum length.
 * @returns Truncated string.
 */
export const truncateText = (str: string, length: number = 30): string => {
    if (!str) return '';
    if (str.length <= length) return str;
    return str.substring(0, length) + '...';
};

/**
 * Formats a currency amount.
 * @param amount - The numeric amount.
 * @param currency - The currency code (default 'USD').
 * @returns Formatted currency string.
 */
export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
    }).format(amount);
};
