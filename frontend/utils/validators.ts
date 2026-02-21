/**
 * Common validation utilities for forms and inputs.
 */

// Email validation regex (RFC 5322 Official Standard)
const EMAIL_REGEX = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;

/**
 * Validates an email address format.
 * @param email - The email string to validate.
 * @returns true if valid, false otherwise.
 */
export const isValidEmail = (email: string): boolean => {
    if (!email) return false;
    return EMAIL_REGEX.test(email);
};

/**
 * Validates password strength.
 * Requirements:
 * - At least 8 characters
 * - Contains at least one uppercase letter
 * - Contains at least one lowercase letter
 * - Contains at least one number
 * @param password - The password string to validate.
 * @returns true if valid, false otherwise.
 */
export const isStrongPassword = (password: string): boolean => {
    if (!password) return false;
    if (password.length < 8) return false;
    if (!/[A-Z]/.test(password)) return false;
    if (!/[a-z]/.test(password)) return false;
    if (!/[0-9]/.test(password)) return false;
    return true;
};

/**
 * Checks if a value is empty (null, undefined, or empty string).
 * @param value - The value to check.
 * @returns true if empty, false otherwise.
 */
export const isEmpty = (value: any): boolean => {
    if (value === null || value === undefined) return true;
    if (typeof value === 'string' && value.trim() === '') return true;
    if (Array.isArray(value) && value.length === 0) return true;
    if (typeof value === 'object' && Object.keys(value).length === 0) return true;
    return false;
};

/**
 * Validates a URL string.
 * @param url - The URL string to validate.
 * @returns true if valid, false otherwise.
 */
export const isValidUrl = (url: string): boolean => {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
};

/**
 * Validates if a string is a valid UUID.
 * @param uuid - The string to check.
 * @returns true if valid UUID, false otherwise.
 */
export const isValidUUID = (uuid: string): boolean => {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidRegex.test(uuid);
};
