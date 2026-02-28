"""
Page Monitor
Monitors Google Meet page for events and state changes
"""

import asyncio
from typing import Optional, Callable, Dict, Any
from datetime import datetime, timezone

def _utcnow() -> datetime:
    """Timezone-aware UTC now"""
    return datetime.now(timezone.utc)



class PageMonitor:
    """
    Monitors Google Meet page for:
    - Participant changes
    - Meeting end
    - Network issues
    - Error messages
    """

    def __init__(self, browser_manager, meet_actions):
        self.browser = browser_manager
        self.actions = meet_actions
        
        # Callbacks
        self.callbacks: Dict[str, Callable] = {}
        
        # State
        self.is_monitoring = False
        self.last_participant_count = 0
        self.alone_since: Optional[datetime] = None
        
        # Stats
        self.events_detected = 0

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # LIFECYCLE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def start(self):
        """Start monitoring"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        print("[Monitor] Started")
        
        # Start monitoring loop
        asyncio.create_task(self._monitor_loop())

    async def stop(self):
        """Stop monitoring"""
        self.is_monitoring = False
        print("[Monitor] Stopped")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # CALLBACKS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def on(self, event: str, callback: Callable):
        """Register event callback"""
        self.callbacks[event] = callback

    async def _emit(self, event: str, data: Dict[str, Any]):
        """Emit event to callback"""
        if event in self.callbacks:
            callback = self.callbacks[event]
            
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        
        self.events_detected += 1

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # MONITORING LOOP
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds
                
                # Check meeting status
                await self._check_meeting_status()
                
                # Check participants
                await self._check_participants()
                
                # Check for errors
                await self._check_for_errors()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Monitor] Error: {e}")

    async def _check_meeting_status(self):
        """Check if meeting is still active"""
        status = await self.actions.get_meeting_status()
        
        # Meeting ended
        if status['ended']:
            await self._emit('meeting_ended', {
                'reason': 'Meeting ended by host',
                'timestamp': _utcnow().isoformat(),
            })
            self.is_monitoring = False
        
        # Waiting for host
        elif status['waiting']:
            await self._emit('waiting_for_host', {
                'timestamp': _utcnow().isoformat(),
            })

    async def _check_participants(self):
        """Check for participant changes"""
        try:
            count = await self.actions.get_participant_count()
            
            # Participant count changed
            if count != self.last_participant_count:
                await self._emit('participant_count_changed', {
                    'previous_count': self.last_participant_count,
                    'current_count': count,
                    'timestamp': _utcnow().isoformat(),
                })
                
                self.last_participant_count = count
            
            # Check if alone
            is_alone = await self.actions.is_alone()
            
            if is_alone:
                if not self.alone_since:
                    self.alone_since = _utcnow()
                    await self._emit('bot_alone', {
                        'timestamp': self.alone_since.isoformat(),
                    })
            else:
                self.alone_since = None
            
        except Exception as e:
            print(f"[Monitor] Participant check error: {e}")

    async def _check_for_errors(self):
        """Check for hard-failure error messages on the page"""
        try:
            # Only match explicit hard-failure phrases (avoid false positives —
            # words like 'connection'/'error' appear in every Meet page's JS)
            error_phrases = [
                'unable to join',
                'meeting ended',
                'something went wrong',
                'you have been removed',
                'this call has ended',
            ]
            
            page_text = await self.browser.execute_script(
                'document.body ? document.body.innerText.toLowerCase() : ""'
            )
            
            if not page_text:
                return
            
            for phrase in error_phrases:
                if phrase in page_text:
                    await self._emit('page_error', {
                        'error': phrase,
                        'timestamp': _utcnow().isoformat(),
                    })
                    
                    # Take screenshot for debugging
                    await self.actions.take_screenshot(
                        f"/tmp/meet_error_{int(_utcnow().timestamp())}.png"
                    )
                    break
            
        except Exception as e:
            print(f"[Monitor] Error check failed: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TIMEOUTS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def check_alone_timeout(self, timeout_seconds: int = 300) -> bool:
        """Check if bot has been alone too long"""
        if not self.alone_since:
            return False
        
        elapsed = (_utcnow() - self.alone_since).total_seconds()
        return elapsed > timeout_seconds

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # STATS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_stats(self) -> dict:
        """Get monitoring statistics"""
        return {
            'is_monitoring': self.is_monitoring,
            'events_detected': self.events_detected,
            'participant_count': self.last_participant_count,
            'alone_since': self.alone_since.isoformat() if self.alone_since else None,
        }