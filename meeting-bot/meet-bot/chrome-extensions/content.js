/**
 * Content Script
 * Runs in Google Meet pages for DOM manipulation and monitoring
 */

console.log('[Vocaply Meet Bot] Content script loaded');

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// AUTO-JOIN HELPERS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * Automatically turn off camera
 */
function disableCamera() {
    // Find camera toggle button
    const cameraButton = document.querySelector('[aria-label*="camera" i][aria-label*="turn off" i]') ||
        document.querySelector('[data-is-muted="false"][aria-label*="camera" i]');

    if (cameraButton) {
        console.log('[Meet Bot] Turning off camera');
        cameraButton.click();
        return true;
    }
    return false;
}

/**
 * Automatically mute microphone
 */
function muteMicrophone() {
    // Find microphone toggle button (unmuted state)
    const micButton = document.querySelector('[aria-label*="microphone" i][aria-label*="turn off" i]') ||
        document.querySelector('[data-is-muted="false"][aria-label*="microphone" i]');

    if (micButton) {
        console.log('[Meet Bot] Muting microphone');
        micButton.click();
        return true;
    }
    return false;
}

/**
 * Click "Join now" button
 */
function clickJoinButton() {
    const joinButton = document.querySelector('[aria-label*="Join" i]') ||
        document.querySelector('button:has-text("Join now")') ||
        document.querySelector('[jsname="Qx7uuf"]'); // Meet's join button jsname

    if (joinButton && !joinButton.disabled) {
        console.log('[Meet Bot] Clicking join button');
        joinButton.click();
        return true;
    }
    return false;
}

/**
 * Dismiss "Your name" dialog if present
 */
function dismissNameDialog() {
    const input = document.querySelector('input[aria-label*="name" i]');
    if (input) {
        input.value = 'Vocaply Bot';
        input.dispatchEvent(new Event('input', { bubbles: true }));

        // Click next/join button
        setTimeout(() => {
            const nextButton = document.querySelector('[jsname="Qx7uuf"]');
            if (nextButton) nextButton.click();
        }, 500);

        return true;
    }
    return false;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// PARTICIPANT SCRAPING
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * Get list of participants from DOM
 */
function getParticipants() {
    const participants = [];

    // Meet stores participants in a side panel
    const participantElements = document.querySelectorAll('[data-participant-id]');

    participantElements.forEach(el => {
        const nameEl = el.querySelector('[data-self-name]') ||
            el.querySelector('span[class*="participant"]');

        if (nameEl) {
            participants.push({
                id: el.getAttribute('data-participant-id'),
                name: nameEl.textContent.trim(),
                isMuted: el.querySelector('[data-is-muted="true"]') !== null,
                hasVideo: el.querySelector('[data-has-video="true"]') !== null,
            });
        }
    });

    return participants;
}

/**
 * Get participant count
 */
function getParticipantCount() {
    const countEl = document.querySelector('[aria-label*="participant" i]') ||
        document.querySelector('[data-participant-count]');

    if (countEl) {
        const match = countEl.textContent.match(/\d+/);
        return match ? parseInt(match[0]) : 0;
    }

    // Fallback: count participant tiles
    return document.querySelectorAll('[data-participant-id]').length;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// MEETING STATUS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * Check if we're in a meeting
 */
function isInMeeting() {
    // Check for meeting controls (mic, camera buttons)
    return document.querySelector('[aria-label*="microphone" i]') !== null &&
        document.querySelector('[aria-label*="camera" i]') !== null;
}

/**
 * Check if waiting for host
 */
function isWaitingForHost() {
    const waitingText = document.body.textContent.toLowerCase();
    return waitingText.includes('waiting for') ||
        waitingText.includes('ask to join') ||
        waitingText.includes('host will let you in');
}

/**
 * Check if meeting ended
 */
function isMeetingEnded() {
    const endedText = document.body.textContent.toLowerCase();
    return endedText.includes('meeting ended') ||
        endedText.includes('left the meeting') ||
        endedText.includes('you left');
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// MESSAGE HANDLER
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * Handle messages from Python bot
 */
window.addEventListener('message', (event) => {
    if (event.source !== window) return;

    const { type, action } = event.data;

    if (type !== 'VOCAPLY_BOT_ACTION') return;

    let result = { success: false };

    switch (action) {
        case 'GET_PARTICIPANTS':
            result = { success: true, participants: getParticipants() };
            break;

        case 'GET_PARTICIPANT_COUNT':
            result = { success: true, count: getParticipantCount() };
            break;

        case 'GET_STATUS':
            result = {
                success: true,
                inMeeting: isInMeeting(),
                waiting: isWaitingForHost(),
                ended: isMeetingEnded(),
            };
            break;

        case 'DISABLE_CAMERA':
            result = { success: disableCamera() };
            break;

        case 'MUTE_MIC':
            result = { success: muteMicrophone() };
            break;

        case 'JOIN':
            result = { success: clickJoinButton() };
            break;
    }

    // Send response
    window.postMessage({
        type: 'VOCAPLY_BOT_RESPONSE',
        action,
        result,
    }, '*');
});

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// AUTO-ACTIONS ON PAGE LOAD
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

/**
 * Run auto-actions when page loads
 */
function runAutoActions() {
    // Wait for page to settle
    setTimeout(() => {
        // Dismiss name dialog if present
        if (dismissNameDialog()) {
            console.log('[Meet Bot] Name dialog handled');
        }

        // Disable camera and mic
        disableCamera();
        muteMicrophone();
    }, 2000);
}

// Run on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runAutoActions);
} else {
    runAutoActions();
}

console.log('[Vocaply Meet Bot] Ready');