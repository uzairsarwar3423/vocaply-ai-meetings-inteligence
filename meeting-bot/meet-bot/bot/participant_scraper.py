"""
Participant Scraper
Scrapes participant information from Google Meet DOM
"""

from typing import List, Dict, Optional
from datetime import datetime, timezone

def _utcnow() -> datetime:
    """Timezone-aware UTC now"""
    return datetime.now(timezone.utc)



class Participant:
    """Participant data"""
    def __init__(
        self,
        participant_id: str,
        name: str,
        is_muted: bool = True,
        has_video: bool = False,
    ):
        self.id = participant_id
        self.name = name
        self.is_muted = is_muted
        self.has_video = has_video
        self.joined_at = _utcnow()
        self.left_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'is_muted': self.is_muted,
            'has_video': self.has_video,
            'joined_at': self.joined_at.isoformat(),
            'left_at': self.left_at.isoformat() if self.left_at else None,
        }


class ParticipantScraper:
    """
    Scrapes and tracks participants from Google Meet.
    Uses content script to extract DOM data.
    """

    def __init__(self, meet_actions):
        self.actions = meet_actions
        
        # Tracked participants
        self.participants: Dict[str, Participant] = {}
        
        # Stats
        self.total_joined = 0
        self.total_left = 0

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # SCRAPING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def refresh(self):
        """Refresh participant list from page"""
        participants_data = await self.actions.get_participants()
        
        current_ids = set()
        
        for data in participants_data:
            participant_id = data.get('id', '')
            name = data.get('name', 'Unknown')
            
            current_ids.add(participant_id)
            
            # New participant
            if participant_id not in self.participants:
                participant = Participant(
                    participant_id=participant_id,
                    name=name,
                    is_muted=data.get('isMuted', True),
                    has_video=data.get('hasVideo', False),
                )
                
                self.participants[participant_id] = participant
                self.total_joined += 1
                
                print(f"[Participants] {name} joined")
            
            # Update existing participant
            else:
                participant = self.participants[participant_id]
                participant.is_muted = data.get('isMuted', True)
                participant.has_video = data.get('hasVideo', False)
        
        # Mark left participants
        for participant_id, participant in list(self.participants.items()):
            if participant_id not in current_ids and not participant.left_at:
                participant.left_at = _utcnow()
                self.total_left += 1
                
                print(f"[Participants] {participant.name} left")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # QUERIES
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_active_participants(self) -> List[Participant]:
        """Get currently active participants"""
        return [
            p for p in self.participants.values()
            if not p.left_at
        ]

    def get_participant(self, participant_id: str) -> Optional[Participant]:
        """Get participant by ID"""
        return self.participants.get(participant_id)

    def get_count(self) -> int:
        """Get active participant count"""
        return len(self.get_active_participants())

    async def get_count_from_page(self) -> int:
        """Get participant count directly from page"""
        return await self.actions.get_participant_count()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stats(self) -> dict:
        """Get participant statistics"""
        return {
            'current_count': self.get_count(),
            'total_joined': self.total_joined,
            'total_left': self.total_left,
            'participants': [p.to_dict() for p in self.get_active_participants()],
        }

    def clear(self):
        """Clear all participant data"""
        self.participants.clear()
        self.total_joined = 0
        self.total_left = 0