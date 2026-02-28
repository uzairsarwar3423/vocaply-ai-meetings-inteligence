"""
Participant Tracker
Tracks participants joining/leaving the meeting
"""

from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class Participant:
    """Meeting participant"""
    user_id:     str
    user_name:   str
    joined_at:   datetime = field(default_factory=datetime.utcnow)
    left_at:     Optional[datetime] = None
    is_host:     bool = False
    is_cohost:   bool = False
    audio_muted: bool = True
    video_on:    bool = False


class ParticipantTracker:
    """
    Tracks all participants in a Zoom meeting.
    Monitors join/leave events and participant state changes.
    """

    def __init__(self, meeting_id: str):
        self.meeting_id = meeting_id
        self.participants: Dict[str, Participant] = {}
        self.active_user_ids: Set[str] = set()
        
        # Stats
        self.total_joined = 0
        self.total_left = 0
        self.peak_count = 0

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PARTICIPANT EVENTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def on_user_join(
        self,
        user_id: str,
        user_name: str,
        is_host: bool = False,
    ) -> Participant:
        """Handle participant joining"""
        participant = Participant(
            user_id=user_id,
            user_name=user_name,
            is_host=is_host,
        )
        
        self.participants[user_id] = participant
        self.active_user_ids.add(user_id)
        
        self.total_joined += 1
        
        # Update peak count
        current_count = len(self.active_user_ids)
        if current_count > self.peak_count:
            self.peak_count = current_count
        
        print(f"[Participant] {user_name} joined (total: {current_count})")
        
        return participant

    def on_user_leave(self, user_id: str):
        """Handle participant leaving"""
        if user_id in self.participants:
            participant = self.participants[user_id]
            participant.left_at = datetime.utcnow()
            
            self.active_user_ids.discard(user_id)
            self.total_left += 1
            
            print(f"[Participant] {participant.user_name} left (remaining: {len(self.active_user_ids)})")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATE CHANGES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def on_audio_status_change(self, user_id: str, muted: bool):
        """Handle audio mute/unmute"""
        if user_id in self.participants:
            self.participants[user_id].audio_muted = muted

    def on_video_status_change(self, user_id: str, video_on: bool):
        """Handle video on/off"""
        if user_id in self.participants:
            self.participants[user_id].video_on = video_on

    def on_host_change(self, user_id: str, is_host: bool):
        """Handle host role change"""
        if user_id in self.participants:
            self.participants[user_id].is_host = is_host

    def on_cohost_change(self, user_id: str, is_cohost: bool):
        """Handle co-host role change"""
        if user_id in self.participants:
            self.participants[user_id].is_cohost = is_cohost

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # QUERIES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_active_participants(self) -> List[Participant]:
        """Get list of currently active participants"""
        return [
            p for user_id, p in self.participants.items()
            if user_id in self.active_user_ids
        ]

    def get_participant(self, user_id: str) -> Optional[Participant]:
        """Get participant by user ID"""
        return self.participants.get(user_id)

    def get_participant_count(self) -> int:
        """Get current number of active participants"""
        return len(self.active_user_ids)

    def get_host(self) -> Optional[Participant]:
        """Get meeting host"""
        for p in self.participants.values():
            if p.is_host:
                return p
        return None

    def is_bot_alone(self, bot_user_id: str) -> bool:
        """Check if bot is the only participant"""
        active = self.active_user_ids - {bot_user_id}
        return len(active) == 0

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stats(self) -> dict:
        """Get participant statistics"""
        return {
            "current_count": len(self.active_user_ids),
            "peak_count": self.peak_count,
            "total_joined": self.total_joined,
            "total_left": self.total_left,
            "participants": [
                {
                    "user_id": p.user_id,
                    "user_name": p.user_name,
                    "is_host": p.is_host,
                    "is_cohost": p.is_cohost,
                    "audio_muted": p.audio_muted,
                    "video_on": p.video_on,
                    "joined_at": p.joined_at.isoformat(),
                    "left_at": p.left_at.isoformat() if p.left_at else None,
                }
                for p in self.get_active_participants()
            ],
        }

    def clear(self):
        """Clear all participant data"""
        self.participants.clear()
        self.active_user_ids.clear()
        self.total_joined = 0
        self.total_left = 0
        self.peak_count = 0