"""
Zoom SDK Wrapper
Python wrapper around Zoom Meeting SDK (C++ library via ctypes)

Note: Zoom Meeting SDK is a C++ library. This wrapper uses ctypes
to interface with the compiled .so/.dll files.
"""

import os
import sys
import ctypes
from typing import Optional, Callable
from enum import IntEnum

from config.zoom_config import settings


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ZOOM SDK ENUMS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ZoomSDKError(IntEnum):
    """SDK error codes"""
    SUCCESS                = 0
    WRONG_USAGE           = 1
    INVALID_PARAMETER     = 2
    MODULE_LOAD_FAILED    = 3
    MEMORY_FAILED         = 4
    SERVICE_FAILED        = 5
    UNAUTHENTICATION      = 6
    NEED_LOGIN            = 7
    UNKNOWN               = 100


class MeetingStatus(IntEnum):
    """Meeting connection status"""
    IDLE           = 0
    CONNECTING     = 1
    WAITINGFORHOST = 2
    INMEETING      = 3
    DISCONNECTING  = 4
    RECONNECTING   = 5
    FAILED         = 6
    ENDED          = 7
    UNKNOWN        = 8


class AudioStatus(IntEnum):
    """Audio connection status"""
    AUDIO_MUTED    = 0
    AUDIO_UNMUTED  = 1
    AUDIO_MUTED_BY_HOST = 2


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SDK WRAPPER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ZoomSDKWrapper:
    """
    Wrapper for Zoom Meeting SDK C++ library.
    
    The actual Zoom SDK is distributed as:
    - Linux: libzoom_meeting_sdk.so
    - Windows: zoom_meeting_sdk.dll
    - macOS: libzoom_meeting_sdk.dylib
    
    This wrapper provides a Pythonic interface.
    """

    def __init__(self, sdk_path: Optional[str] = None):
        """
        Initialize SDK wrapper.
        
        Args:
            sdk_path: Path to SDK library directory
        """
        self.sdk_path = sdk_path or os.getenv("ZOOM_SDK_PATH", "/usr/local/lib/zoom-sdk")
        self.sdk_lib = None
        self._callbacks = {}

    # ── Initialization ───────────────────────────────

    def load_sdk(self) -> bool:
        """Load Zoom SDK library"""
        try:
            # Determine library name based on platform
            if sys.platform == "linux":
                lib_name = "libzoom_meeting_sdk.so"
            elif sys.platform == "darwin":
                lib_name = "libzoom_meeting_sdk.dylib"
            elif sys.platform == "win32":
                lib_name = "zoom_meeting_sdk.dll"
            else:
                raise RuntimeError(f"Unsupported platform: {sys.platform}")
            
            lib_path = os.path.join(self.sdk_path, lib_name)
            
            if not os.path.exists(lib_path):
                raise FileNotFoundError(f"Zoom SDK not found at: {lib_path}")
            
            # Load library
            self.sdk_lib = ctypes.CDLL(lib_path)
            
            # Define function signatures
            self._define_function_signatures()
            
            return True
            
        except Exception as e:
            print(f"Failed to load Zoom SDK: {e}")
            return False

    def _define_function_signatures(self):
        """Define ctypes function signatures for SDK functions"""
        if not self.sdk_lib:
            return
        
        # Example function signatures (actual SDK may vary)
        # These would be defined based on Zoom SDK documentation
        
        # Initialize SDK
        self.sdk_lib.InitSDK.argtypes = [ctypes.c_char_p]
        self.sdk_lib.InitSDK.restype = ctypes.c_int
        
        # Join meeting
        self.sdk_lib.JoinMeeting.argtypes = [
            ctypes.c_char_p,  # meeting_number
            ctypes.c_char_p,  # display_name
            ctypes.c_char_p,  # password
            ctypes.c_char_p,  # jwt_token
        ]
        self.sdk_lib.JoinMeeting.restype = ctypes.c_int
        
        # Leave meeting
        self.sdk_lib.LeaveMeeting.argtypes = []
        self.sdk_lib.LeaveMeeting.restype = ctypes.c_int

    def initialize(self) -> bool:
        """Initialize Zoom SDK"""
        if not self.sdk_lib:
            if not self.load_sdk():
                return False
        
        try:
            # Initialize with SDK key
            result = self.sdk_lib.InitSDK(settings.ZOOM_CLIENT_ID.encode('utf-8'))
            return result == ZoomSDKError.SUCCESS
        except Exception as e:
            print(f"SDK initialization failed: {e}")
            return False

    # ── Meeting Operations ───────────────────────────

    def join_meeting(
        self,
        meeting_number: str,
        display_name: str,
        password: str,
        jwt_token: str,
    ) -> int:
        """
        Join a Zoom meeting.
        
        Returns:
            ZoomSDKError code
        """
        if not self.sdk_lib:
            raise RuntimeError("SDK not initialized")
        
        result = self.sdk_lib.JoinMeeting(
            meeting_number.encode('utf-8'),
            display_name.encode('utf-8'),
            password.encode('utf-8'),
            jwt_token.encode('utf-8'),
        )
        
        return result

    def leave_meeting(self) -> int:
        """Leave current meeting"""
        if not self.sdk_lib:
            raise RuntimeError("SDK not initialized")
        
        return self.sdk_lib.LeaveMeeting()

    def get_meeting_status(self) -> MeetingStatus:
        """Get current meeting connection status"""
        if not self.sdk_lib:
            return MeetingStatus.UNKNOWN
        
        try:
            status = self.sdk_lib.GetMeetingStatus()
            return MeetingStatus(status)
        except:
            return MeetingStatus.UNKNOWN

    # ── Audio Operations ─────────────────────────────

    def mute_audio(self) -> bool:
        """Mute bot's audio"""
        if not self.sdk_lib:
            return False
        
        try:
            result = self.sdk_lib.MuteAudio()
            return result == ZoomSDKError.SUCCESS
        except:
            return False

    def unmute_audio(self) -> bool:
        """Unmute bot's audio"""
        if not self.sdk_lib:
            return False
        
        try:
            result = self.sdk_lib.UnmuteAudio()
            return result == ZoomSDKError.SUCCESS
        except:
            return False

    def start_audio(self) -> bool:
        """Join audio channel"""
        if not self.sdk_lib:
            return False
        
        try:
            result = self.sdk_lib.StartAudio()
            return result == ZoomSDKError.SUCCESS
        except:
            return False

    # ── Video Operations ─────────────────────────────

    def hide_video(self) -> bool:
        """Turn off bot's video feed"""
        if not self.sdk_lib:
            return False
        
        try:
            result = self.sdk_lib.StopVideo()
            return result == ZoomSDKError.SUCCESS
        except:
            return False

    # ── Participant Operations ───────────────────────

    def get_participant_count(self) -> int:
        """Get number of participants in meeting"""
        if not self.sdk_lib:
            return 0
        
        try:
            return self.sdk_lib.GetParticipantCount()
        except:
            return 0

    # ── Callbacks ────────────────────────────────────

    def register_callback(self, event_type: str, callback: Callable):
        """Register callback for SDK events"""
        self._callbacks[event_type] = callback

    def unregister_callback(self, event_type: str):
        """Unregister callback"""
        if event_type in self._callbacks:
            del self._callbacks[event_type]

    # ── Cleanup ──────────────────────────────────────

    def cleanup(self):
        """Cleanup SDK resources"""
        if self.sdk_lib:
            try:
                self.sdk_lib.CleanupSDK()
            except:
                pass
        
        self.sdk_lib = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MOCK SDK (for development without actual SDK)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class MockZoomSDK:
    """
    Mock Zoom SDK for testing without actual SDK installation.
    Simulates SDK behavior for development.
    """

    def __init__(self):
        self.initialized = False
        self.in_meeting = False
        self.audio_muted = True
        self.video_stopped = True
        self.participants = []

    def load_sdk(self) -> bool:
        return True

    def initialize(self) -> bool:
        self.initialized = True
        return True

    def join_meeting(self, meeting_number, display_name, password, jwt_token) -> int:
        if not self.initialized:
            return ZoomSDKError.UNAUTHENTICATION
        
        self.in_meeting = True
        self.participants = ["Host", display_name]
        return ZoomSDKError.SUCCESS

    def leave_meeting(self) -> int:
        self.in_meeting = False
        self.participants = []
        return ZoomSDKError.SUCCESS

    def get_meeting_status(self) -> MeetingStatus:
        if self.in_meeting:
            return MeetingStatus.INMEETING
        return MeetingStatus.IDLE

    def mute_audio(self) -> bool:
        self.audio_muted = True
        return True

    def unmute_audio(self) -> bool:
        self.audio_muted = False
        return True

    def start_audio(self) -> bool:
        return True

    def hide_video(self) -> bool:
        self.video_stopped = True
        return True

    def get_participant_count(self) -> int:
        return len(self.participants)

    def register_callback(self, event_type, callback):
        pass

    def cleanup(self):
        self.initialized = False
        self.in_meeting = False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FACTORY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_sdk(use_mock: bool = False):
    """
    Create SDK instance.
    
    Args:
        use_mock: Use mock SDK for development
    """
    if use_mock or os.getenv("USE_MOCK_SDK", "false").lower() == "true":
        return MockZoomSDK()
    return ZoomSDKWrapper()