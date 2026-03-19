"""
Meeting Attendee Repository
Handles database operations for meeting attendees.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.repositories.base import CRUDBase
from app.models.meeting_attendee import MeetingAttendee


class CRUDMeetingAttendee(CRUDBase[MeetingAttendee, dict, dict]):
    """CRUD operations for MeetingAttendee"""

    def get_by_meeting(self, db: Session, *, meeting_id: str) -> List[MeetingAttendee]:
        """Get all attendees for a meeting"""
        return db.query(MeetingAttendee).filter(MeetingAttendee.meeting_id == meeting_id).all()

    def get_by_meeting_and_email(self, db: Session, *, meeting_id: str, email: str) -> Optional[MeetingAttendee]:
        """Get attendee by meeting and email"""
        return db.query(MeetingAttendee).filter(
            MeetingAttendee.meeting_id == meeting_id,
            MeetingAttendee.email == email
        ).first()

    def get_by_user(self, db: Session, *, user_id: str) -> List[MeetingAttendee]:
        """Get all meetings attended by a user"""
        return db.query(MeetingAttendee).filter(MeetingAttendee.user_id == user_id).all()

    def count_by_meeting(self, db: Session, *, meeting_id: str) -> int:
        """Count attendees for a meeting"""
        return db.query(MeetingAttendee).filter(MeetingAttendee.meeting_id == meeting_id).count()

    def get_present_attendees(self, db: Session, *, meeting_id: str) -> List[MeetingAttendee]:
        """Get attendees who are currently present (joined but not left)"""
        return db.query(MeetingAttendee).filter(
            MeetingAttendee.meeting_id == meeting_id,
            MeetingAttendee.is_present == True
        ).all()


meeting_attendee_repo = CRUDMeetingAttendee(MeetingAttendee)