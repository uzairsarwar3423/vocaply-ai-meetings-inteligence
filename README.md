# Vocaply AI - Meeting Intelligence Platform

Vocaply AI is a high-end meeting intelligence platform that provides AI-powered summaries, transcripts, and insights from your meetings.

## Tech Stack

- **Frontend**: Next.js 16, Tailwind CSS v4, Framer Motion, Lucide Icons
- **Backend**: FastAPI, SQLAlchemy, Alembic, PostgreSQL (Supabase), Redis
- **Infrastructure**: Docker, Backblaze B2 (Storage), Vercel (Frontend), VPS (Backend)

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

### Local Development

1. **Clone the repository**
2. **Setup Backend**
   ```bash
   cd backend
   cp .env.example .env
   # Fill in your environment variables
   ```
3. **Setup Frontend**
   ```bash
   cd frontend
   cp .env.local.example .env.local
   # Fill in your environment variables
   ```
4. **Run with Docker**
   ```bash
   make up
   ```

## Infrastructure Status

- [x] Backend Boilerplate
- [x] Frontend UI Components
- [x] Database Schema (Initial)
- [x] Docker Configuration
- [x] Makefile for common tasks
