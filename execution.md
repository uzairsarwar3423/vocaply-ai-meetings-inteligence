# Fast Ship Plan: Vocaply AI MVP (1 Week to Beta)

Goal: Ship working end-to-end MVP **this week**. Focus on **core value**: Zoom → Bot records → Transcript → Basic AI actions/summary → Dashboard.

Current: 68% → MVP shippable with targeted fixes.

## MVP Scope (Ship Now - 80% users happy)

✅ **Already Works**:
- [x] Landing page + auth (email + Zoom OAuth)
- [x] User/company models + DB
- [x] Meeting CRUD (schedule, status)
- [x] Frontend dashboard skeleton
- [x] Bot services Dockerized (zoom-bot etc.)

🟢 **Complete This Week** (3-5 days):
1. **Bot Integration** (Day 1-2): Connect meeting → start/stop bot → get recording URL.
2. **Basic Transcription** (Day 2): Deepgram → store transcript chunks.
3. **Stub AI** (Day 3): OpenAI → extract 5 bullet actions + 1-paragraph summary.
4. **Dashboard Pages** (Day 3-4): Meeting list → detail (transcript + AI output).
5. **Deploy** (Day 5): Vercel (FE) + VPS/Docker (BE+Bots) + Supabase.

## Skip Now, Add Later (Post-MVP)

| Feature | Why Skip | Priority | Timeline |
|---------|----------|----------|----------|
| Google Meet/Teams bots | Focus Zoom (80% market) | Medium | Week 2 |
| Calendar auto-sync/join | Manual schedule OK for beta | Medium | Week 3 |
| Slack/Asana integrations | Email notifications suffice | Low | Week 4 |
| Advanced action items (kanban, assign, comments) | Simple list + edit | Low | Week 4 |
| Realtime WebSockets | Page refresh OK | Low | Week 5 |
| Billing/Stripe | Free beta (10 users) | Low | Week 6 |
| Analytics dashboard | Basic metrics in DB | Low | Week 6 |
| File upload (manual) | Bot auto-records | Low | Week 2 |
| Multi-speaker diarization | Single-channel transcript | Medium | Week 3 |
| Export PDF/DOCX | Copy-paste OK | Low | Week 5 |
| Mobile/responsive polish | Desktop-first | Low | Week 6 |
| Dark mode/onboarding tour | Basic UI works | Low | Never? |

**MVP Success Metric**: 5 beta users record 1 Zoom meeting each → see transcript + actions → \"wow\" reaction.

## Execution Steps (5 Days)

### Day 1: Bot → Backend Integration
```
1. Add /api/v1/meetings/{id}/bot/start (calls bot-service)
2. Store bot_session_id in meeting.bot_instance_id
3. Frontend: Add \"Start Recording Bot\" button
4. Test: docker-compose up → manual Zoom join → recording URL
```
Files: backend/app/services/bot_client.py, api/v1/bot.py, frontend/components/meetings/BotButton.tsx

### Day 2: Transcription Pipeline
```
1. POST recording to Deepgram → save chunks to transcript model
2. Celery task: transcribe → update meeting.status = 'transcribed'
3. Frontend poll: show progress bar
```
Files: backend/app/services/transcription/deepgram.py, workers/transcription_worker.py

### Day 3: MVP AI (Minimal Prompts)
```
1. POST transcript → OpenAI: \"Extract top 5 actions + 1 summary\"
2. Parse JSON → save action_items + meeting_summary
3. Frontend: Meeting detail shows bullets
```
Files: backend/app/services/ai/basic_extractor.py (hardcode prompt)

### Day 4: Dashboard Completion
```
1. /meetings → list with status icons
2. /meetings/[id] → transcript viewer + AI sections
3. Basic search/filter
```
Pages: frontend/app/(dashboard)/meetings/page.tsx + [id]/page.tsx

### Day 5: Deploy & Beta
```
1. docker-compose.prod.yml → VPS
2. Vercel FE
3. Supabase DB
4. Invite 5 beta users (your network)
5. Feedback loop: Discord/Slack
```

## Commands to Run Today
```bash
# Test current stack
make up

# Check Zoom setup
./check_zoom_setup.sh

# Run DB optimizations (if needed)
cd backend && alembic upgrade head

# Test bots
cd meeting-bot && docker-compose -f docker-compose.bots.yml up
```

## Risks & Mitigations
- **Bot fails to join**: Fallback manual upload. Test 3 Zoom meetings.
- **AI inaccurate**: Use structured prompts + manual edit.
- **Perf issues**: Skip indexes if blocking; add post-launch.
- **No users**: Demo video + your network.

**Commit to Ship**: By EOD Day 5, 5 users recording meetings successfully.

Next: After MVP validates → add Google bot → integrations → billing.

