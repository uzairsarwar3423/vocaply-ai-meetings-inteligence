/**
 * Background Service Worker
 * Handles audio capture from Google Meet tabs
 */

// Store active capture streams
const activeCaptures = new Map();

// Listen for messages from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log('[Background] Received message:', message.type);

    switch (message.type) {
        case 'START_CAPTURE':
            startAudioCapture(sender.tab.id)
                .then(() => sendResponse({ success: true }))
                .catch(err => sendResponse({ success: false, error: err.message }));
            return true; // Keep channel open for async response

        case 'STOP_CAPTURE':
            stopAudioCapture(sender.tab.id);
            sendResponse({ success: true });
            return true;

        case 'GET_CAPTURE_STATUS':
            sendResponse({
                isCapturing: activeCaptures.has(sender.tab.id)
            });
            return true;
    }
});

/**
 * Start capturing audio from a tab
 */
async function startAudioCapture(tabId) {
    if (activeCaptures.has(tabId)) {
        console.log('[Background] Already capturing tab', tabId);
        return;
    }

    try {
        // Get tab audio stream
        const stream = await chrome.tabCapture.capture({
            audio: true,
            video: false
        });

        if (!stream) {
            throw new Error('Failed to capture tab audio');
        }

        console.log('[Background] Audio capture started for tab', tabId);
        activeCaptures.set(tabId, stream);

        // Store stream info
        chrome.storage.local.set({
            [`capture_${tabId}`]: {
                active: true,
                startedAt: Date.now()
            }
        });

        // Listen for stream end
        stream.getAudioTracks()[0].addEventListener('ended', () => {
            console.log('[Background] Stream ended for tab', tabId);
            stopAudioCapture(tabId);
        });

    } catch (error) {
        console.error('[Background] Capture error:', error);
        throw error;
    }
}

/**
 * Stop capturing audio from a tab
 */
function stopAudioCapture(tabId) {
    const stream = activeCaptures.get(tabId);

    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        activeCaptures.delete(tabId);

        chrome.storage.local.remove(`capture_${tabId}`);
        console.log('[Background] Stopped capture for tab', tabId);
    }
}

/**
 * Clean up when tab is closed
 */
chrome.tabs.onRemoved.addListener((tabId) => {
    if (activeCaptures.has(tabId)) {
        stopAudioCapture(tabId);
    }
});