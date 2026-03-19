#!/usr/bin/env python3
"""
Database Optimization Script
Vocaply Platform - Database Design Improvements

This script applies database optimizations and validates improvements.
Run this after deploying the db_optimization_phase1 migration.
"""

import asyncio
import time
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal


async def run_optimization_checks():
    """Run database optimization validation checks"""

    print("🔍 Database Optimization Validation")
    print("=" * 50)

    async with AsyncSessionLocal() as db:
        try:
            # Check 1: Meeting attendees table exists and has data
            print("\n1. Checking meeting_attendees table...")
            result = await db.execute(text("SELECT COUNT(*) FROM meeting_attendees"))
            attendee_count = result.scalar()
            print(f"   ✅ meeting_attendees table exists with {attendee_count} records")

            # Check 2: New indexes exist
            print("\n2. Checking new indexes...")
            indexes_to_check = [
                'idx_meetings_company_status_created',
                'idx_meetings_company_platform',
                'idx_meetings_scheduled_range',
                'idx_transcripts_meeting_time',
                'idx_transcripts_speaker_email',
                'idx_action_items_company_status',
                'idx_action_items_assigned_due',
                'idx_user_sessions_user_created'
            ]

            for index_name in indexes_to_check:
                try:
                    result = await db.execute(text(f"SELECT 1 FROM pg_indexes WHERE indexname = '{index_name}'"))
                    exists = result.scalar()
                    status = "✅" if exists else "❌"
                    print(f"   {status} {index_name}")
                except Exception as e:
                    print(f"   ❌ {index_name} - Error: {e}")

            # Check 3: Table partitioning (if transcripts table is partitioned)
            print("\n3. Checking table partitioning...")
            try:
                result = await db.execute(text("""
                    SELECT COUNT(*) as partition_count
                    FROM pg_inherits i
                    JOIN pg_class c ON i.inhrelid = c.oid
                    WHERE c.relname LIKE 'transcripts_y%m%'
                """))
                partition_count = result.scalar()
                if partition_count > 0:
                    print(f"   ✅ Transcripts table has {partition_count} partitions")
                else:
                    print("   ⚠️  No partitions found (may not be created yet)")
            except Exception as e:
                print(f"   ❌ Partition check failed: {e}")

            # Check 4: Status transition trigger
            print("\n4. Checking status transition trigger...")
            try:
                result = await db.execute(text("""
                    SELECT COUNT(*) FROM pg_trigger
                    WHERE tgname = 'meeting_status_transition_trigger'
                """))
                trigger_exists = result.scalar()
                status = "✅" if trigger_exists else "❌"
                print(f"   {status} Status transition trigger exists")
            except Exception as e:
                print(f"   ❌ Trigger check failed: {e}")

            # Check 5: Performance test - Simple query timing
            print("\n5. Running performance tests...")

            # Test meeting query with new indexes
            start_time = time.time()
            result = await db.execute(text("""
                SELECT COUNT(*) FROM meetings
                WHERE company_id = (SELECT id FROM companies LIMIT 1)
                AND status = 'completed'
                AND created_at >= NOW() - INTERVAL '30 days'
            """))
            count = result.scalar()
            elapsed = time.time() - start_time
            print(".4f"
            # Test attendee query
            start_time = time.time()
            result = await db.execute(text("""
                SELECT COUNT(*) FROM meeting_attendees ma
                JOIN meetings m ON ma.meeting_id = m.id
                WHERE m.company_id = (SELECT id FROM companies LIMIT 1)
            """))
            count = result.scalar()
            elapsed = time.time() - start_time
            print(".4f"
            # Check 6: Data integrity
            print("\n6. Checking data integrity...")

            # Verify participant counts match
            result = await db.execute(text("""
                SELECT
                    m.id,
                    m.participant_count as json_count,
                    COUNT(ma.id) as actual_count
                FROM meetings m
                LEFT JOIN meeting_attendees ma ON m.id = ma.meeting_id
                GROUP BY m.id, m.participant_count
                HAVING m.participant_count != COUNT(ma.id)
                LIMIT 5
            """))
            mismatches = result.fetchall()
            if mismatches:
                print(f"   ⚠️  Found {len(mismatches)} meetings with participant count mismatches")
                for row in mismatches[:3]:
                    print(f"      Meeting {row[0]}: JSON={row[1]}, Actual={row[2]}")
            else:
                print("   ✅ Participant counts are consistent")

            print("\n" + "=" * 50)
            print("🎉 Database optimization validation complete!")
            print("\nNext steps:")
            print("1. Monitor query performance in production")
            print("2. Update application code to use MeetingAttendee model")
            print("3. Consider adding more partitions as data grows")
            print("4. Set up automated index usage monitoring")

        except Exception as e:
            print(f"❌ Error during validation: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(run_optimization_checks())</content>
<parameter name="filePath">/home/uzair/vocaply-ai-meeting-inteligence/backend/scripts/validate_db_optimizations.py