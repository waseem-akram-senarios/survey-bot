# SurvAI Platform - Architecture Documentation

## Overview

SurvAI is an AI-powered voice survey platform for transit agencies. It conducts natural, human-like phone surveys with riders to collect feedback about their transportation experience.

---

## System Architecture Diagram

```
╔═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                    SURVAI PLATFORM ARCHITECTURE                                                ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

                                              ┌─────────────────────────────────┐
                                              │         EXTERNAL WORLD          │
                                              └─────────────────────────────────┘
                                                              │
                 ┌──────────────────────────────────────────────────────────────────────────────────┐
                 │                                          │                                       │
                 ▼                                          ▼                                       ▼
    ┌────────────────────────┐              ┌────────────────────────┐              ┌────────────────────────┐
    │    👤 AGENCY ADMIN     │              │      📱 RIDER          │              │    ☁️ CLOUD SERVICES   │
    │                        │              │                        │              │                        │
    │  • Creates Templates   │              │  • Receives Calls      │              │  • OpenAI (GPT-4)      │
    │  • Imports CSV Data    │              │  • Gets SMS Links      │              │  • VAPI (Voice AI)     │
    │  • Launches Surveys    │              │  • Takes Web Surveys   │              │  • Twilio (SMS)        │
    │  • Views Analytics     │              │  • Provides Feedback   │              │                        │
    └───────────┬────────────┘              └───────────┬────────────┘              └───────────┬────────────┘
                │                                       │                                       │
                │ HTTPS                                 │ HTTPS/Phone                           │ API Calls
                │                                       │                                       │
╔═══════════════▼═══════════════════════════════════════▼═══════════════════════════════════════▼═══════════════╗
║                                                                                                                ║
║                                         AWS EC2 SERVER                                                         ║
║  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐  ║
║  │                                                                                                         │  ║
║  │                                    🌐 GATEWAY (nginx:8080)                                              │  ║
║  │                                    • Reverse Proxy                                                      │  ║
║  │                                    • Load Balancer                                                      │  ║
║  │                                    • Route: /api/* → Services                                           │  ║
║  │                                                                                                         │  ║
║  └─────────────────────────────────────────────────┬───────────────────────────────────────────────────────┘  ║
║                                                    │                                                          ║
║            ┌───────────────────┬───────────────────┼───────────────────┬───────────────────┐                  ║
║            │                   │                   │                   │                   │                  ║
║            ▼                   ▼                   ▼                   ▼                   ▼                  ║
║  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐          ║
║  │   📊 DASHBOARD  │ │  📝 RECIPIENT   │ │  📋 SURVEY      │ │  📄 TEMPLATE    │ │  ❓ QUESTION    │          ║
║  │   (React:8082)  │ │  (Next.js:3000) │ │  SERVICE:8020   │ │  SERVICE:8040   │ │  SERVICE:8030   │          ║
║  ├─────────────────┤ ├─────────────────┤ ├─────────────────┤ ├─────────────────┤ ├─────────────────┤          ║
║  │ • Login Page    │ │ • Survey UI     │ │ • Generate      │ │ • CRUD          │ │ • CRUD          │          ║
║  │ • Template Mgmt │ │ • Q&A Flow      │ │ • List/Get      │ │ • Publish       │ │ • Categories    │          ║
║  │ • Survey List   │ │ • Submit        │ │ • Send SMS      │ │ • Config        │ │ • Link to       │          ║
║  │ • Analytics     │ │ • Multi-lang    │ │ • Make Calls    │ │                 │ │   Templates     │          ║
║  │ • CSV Export    │ │                 │ │ • Save Response │ │                 │ │                 │          ║
║  └─────────────────┘ └─────────────────┘ └────────┬────────┘ └─────────────────┘ └─────────────────┘          ║
║                                                   │                                                           ║
║            ┌──────────────────────────────────────┼──────────────────────────────────────┐                    ║
║            │                                      │                                      │                    ║
║            ▼                                      ▼                                      ▼                    ║
║  ┌─────────────────┐                   ┌─────────────────┐                   ┌─────────────────┐              ║
║  │  🧠 BRAIN       │                   │  🎙️ VOICE       │                   │  📈 ANALYTICS   │              ║
║  │  SERVICE:8016   │                   │  SERVICE:8017   │                   │  SERVICE:8060   │              ║
║  ├─────────────────┤                   ├─────────────────┤                   ├─────────────────┤              ║
║  │ • LLM Prompts   │◀──────────────────│ • VAPI Calls    │                   │ • Stats Summary │              ║
║  │ • Parse Response│                   │ • Transcripts   │                   │ • Demand Track  │              ║
║  │ • Autofill      │                   │ • Call Status   │                   │ • Incentives    │              ║
║  │ • Translation   │                   │                 │                   │ • CSV Export    │              ║
║  │ • Empathy Gen   │                   │                 │                   │                 │              ║
║  └────────┬────────┘                   └────────┬────────┘                   └─────────────────┘              ║
║           │                                     │                                                             ║
║           │ API                                 │ API                                                         ║
║           ▼                                     ▼                                                             ║
║  ┌─────────────────┐                   ┌─────────────────┐                                                    ║
║  │  ☁️ OPENAI      │                   │  ☁️ VAPI        │                                                    ║
║  │  (GPT-4)        │                   │  (Voice AI)     │                                                    ║
║  └─────────────────┘                   └─────────────────┘                                                    ║
║                                                                                                               ║
║            ┌────────────────────────────────────────────────────────────────┐                                 ║
║            │                                                                │                                 ║
║            ▼                                      ▼                         ▼                                 ║
║  ┌─────────────────┐                   ┌─────────────────┐       ┌─────────────────┐                          ║
║  │  🤖 AGENT       │                   │  ⏰ SCHEDULER   │       │  📱 TWILIO      │                          ║
║  │  SERVICE:8050   │                   │  SERVICE:8070   │       │  (SMS Cloud)    │                          ║
║  ├─────────────────┤                   ├─────────────────┤       ├─────────────────┤                          ║
║  │ • VAPI Webhooks │                   │ • Scheduled     │       │ • Send SMS      │                          ║
║  │ • Call Events   │                   │   Callbacks     │       │ • Survey Links  │                          ║
║  │ • Transcripts   │                   │ • Batch Jobs    │       │ • Notifications │                          ║
║  └─────────────────┘                   └─────────────────┘       └─────────────────┘                          ║
║                                                                                                               ║
║  ┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐  ║
║  │                                        💾 DATA LAYER                                                    │  ║
║  │  ┌─────────────────────────────────────────────┐  ┌─────────────────────────────────────────────┐      │  ║
║  │  │           🐘 POSTGRESQL:5432                │  │              🔴 REDIS:6379                  │      │  ║
║  │  ├─────────────────────────────────────────────┤  ├─────────────────────────────────────────────┤      │  ║
║  │  │  • templates                                │  │  • Session Cache                            │      │  ║
║  │  │  • surveys                                  │  │  • Job Queue                                │      │  ║
║  │  │  • questions                                │  │  • Rate Limiting                            │      │  ║
║  │  │  • template_questions                       │  │  • Temporary Data                           │      │  ║
║  │  │  • survey_response_items                    │  │                                             │      │  ║
║  │  │  • call_transcripts                         │  │                                             │      │  ║
║  │  │  • campaigns                                │  │                                             │      │  ║
║  │  └─────────────────────────────────────────────┘  └─────────────────────────────────────────────┘      │  ║
║  └─────────────────────────────────────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

---

## Service Details

### Frontend Services

| Service | Port | Technology | Purpose |
|---------|------|------------|---------|
| Dashboard | 8082 | React/Vite | Admin interface for agencies |
| Recipient | 3000 | Next.js | Web survey interface for riders |

### Backend Microservices

| Service | Port | Technology | Purpose |
|---------|------|------------|---------|
| Gateway | 8080 | Nginx | Reverse proxy, load balancer |
| Survey Service | 8020 | FastAPI | Survey CRUD, SMS, calls |
| Template Service | 8040 | FastAPI | Template management |
| Question Service | 8030 | FastAPI | Question management |
| Analytics Service | 8060 | FastAPI | Stats, reporting, export |
| Brain Service | 8016 | FastAPI | LLM integration, parsing |
| Voice Service | 8017 | FastAPI | VAPI integration |
| Scheduler Service | 8070 | FastAPI | Scheduled jobs |
| Agent Service | 8050 | FastAPI | VAPI webhooks |

### Data Layer

| Service | Port | Technology | Purpose |
|---------|------|------------|---------|
| PostgreSQL | 5432 | PostgreSQL 14 | Primary database |
| Redis | 6379 | Redis 7 | Cache, queue |

---

## Database Schema

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            POSTGRESQL DATABASE                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐      ┌──────────────────┐      ┌─────────────┐                │
│  │  templates  │──────│template_questions│──────│  questions  │                │
│  ├─────────────┤      ├──────────────────┤      ├─────────────┤                │
│  │ name (PK)   │      │ template_name    │      │ id (PK)     │                │
│  │ status      │      │ question_id      │      │ text        │                │
│  │ created_at  │      │ ord              │      │ criteria    │                │
│  │ max_questions│     └──────────────────┘      │ autofill    │                │
│  │ time_limit  │                                │ categories  │                │
│  └──────┬──────┘                                └─────────────┘                │
│         │                                                                       │
│         ▼                                                                       │
│  ┌─────────────────┐      ┌───────────────────────┐                            │
│  │    surveys      │──────│ survey_response_items │                            │
│  ├─────────────────┤      ├───────────────────────┤                            │
│  │ id (PK)         │      │ survey_id             │                            │
│  │ template_name   │      │ question_id           │                            │
│  │ rider_name      │      │ raw_answer            │                            │
│  │ phone/email     │      │ answer (parsed)       │                            │
│  │ status          │      │ ord                   │                            │
│  │ tenant_id       │      └───────────────────────┘                            │
│  │ channel         │                                                           │
│  │ launch_date     │      ┌───────────────────────┐                            │
│  │ completion_date │      │   call_transcripts    │                            │
│  └─────────────────┘      ├───────────────────────┤                            │
│                           │ call_id (PK)          │                            │
│  ┌─────────────┐          │ survey_id             │                            │
│  │  campaigns  │          │ transcript            │                            │
│  ├─────────────┤          │ call_status           │                            │
│  │ id (PK)     │          │ call_duration_seconds │                            │
│  │ name        │          └───────────────────────┘                            │
│  │ template    │                                                               │
│  │ tenant_id   │                                                               │
│  └─────────────┘                                                               │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## User Journey Flows

### Flow 1: Voice Survey (AI Phone Call)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    VOICE SURVEY FLOW                                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                      │
│   📞 Rider          🎙️ VAPI           🤖 Agent Svc         🧠 Brain Svc         ☁️ OpenAI           │
│      │                 │                    │                    │                 │                 │
│      │  1. Phone Rings │                    │                    │                 │                 │
│      │ ◀───────────────│                    │                    │                 │                 │
│      │                 │                    │                    │                 │                 │
│      │  2. "Hello?"    │                    │                    │                 │                 │
│      │ ───────────────▶│  3. Webhook        │                    │                 │                 │
│      │                 │ ──────────────────▶│                    │                 │                 │
│      │                 │                    │  4. Get greeting   │                 │                 │
│      │                 │                    │ ──────────────────▶│  5. Generate    │                 │
│      │                 │                    │                    │ ───────────────▶│                 │
│      │                 │                    │                    │                 │                 │
│      │  6. "Hey John!  │◀───────────────────│◀───────────────────│◀────────────────│                 │
│      │   How was your  │                    │                    │                 │                 │
│      │   trip today?"  │                    │                    │                 │                 │
│      │                 │                    │                    │                 │                 │
│      │  7. "It was     │                    │                    │                 │                 │
│      │   great!"       │  8. Transcribe     │  9. Parse          │  10. Understand │                 │
│      │ ───────────────▶│ ──────────────────▶│ ──────────────────▶│ ───────────────▶│                 │
│      │                 │                    │                    │                 │                 │
│      │  11. Empathetic │◀───────────────────│◀───────────────────│◀────────────────│                 │
│      │   follow-up     │                    │                    │                 │                 │
│      │                 │                    │                    │                 │                 │
│      │     ... (repeat for each question) ...                    │                 │                 │
│      │                 │                    │                    │                 │                 │
│      │  12. "Thanks!"  │  13. Call ended    │  14. Save to DB    │                 │                 │
│      │ ◀───────────────│ ──────────────────▶│ ──────────────────▶│                 │                 │
│                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Flow 2: Web Survey (Text-Based)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    WEB SURVEY FLOW                                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                      │
│   📱 Rider            📱 Twilio         📝 Recipient App      📋 Survey Svc        🗄️ Database       │
│      │                    │                    │                    │                 │              │
│      │  1. SMS Received   │                    │                    │                 │              │
│      │  "Take survey at:  │                    │                    │                 │              │
│      │   survai.com/xyz"  │                    │                    │                 │              │
│      │ ◀──────────────────│                    │                    │                 │              │
│      │                    │                    │                    │                 │              │
│      │  2. Click Link     │                    │                    │                 │              │
│      │ ──────────────────────────────────────▶ │                    │                 │              │
│      │                    │                    │  3. GET /survey/id │                 │              │
│      │                    │                    │ ──────────────────▶│  4. Get data    │              │
│      │                    │                    │                    │ ────────────────▶              │
│      │                    │                    │                    │                 │              │
│      │  5. Survey Page    │                    │◀───────────────────│◀────────────────│              │
│      │ ◀─────────────────────────────────────  │                    │                 │              │
│      │                    │                    │                    │                 │              │
│      │  6. Type answers   │                    │  7. POST response  │  8. Save        │              │
│      │ ──────────────────────────────────────▶ │ ──────────────────▶│ ────────────────▶              │
│      │                    │                    │                    │                 │              │
│      │     ... (repeat for each question) ...  │                    │                 │              │
│      │                    │                    │                    │                 │              │
│      │  9. "Thank You!"   │                    │                    │                 │              │
│      │ ◀─────────────────────────────────────  │                    │                 │              │
│                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Flow 3: Admin Dashboard

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    ADMIN DASHBOARD FLOW                                               │
├──────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                      │
│   👤 Admin              🌐 Dashboard           📋 Services              🗄️ Database                  │
│      │                       │                       │                       │                       │
│      │  1. Login             │                       │                       │                       │
│      │  (admin/admin123)     │                       │                       │                       │
│      │ ─────────────────────▶│                       │                       │                       │
│      │                       │                       │                       │                       │
│      │  2. Create Template   │  3. POST /templates   │  4. INSERT            │                       │
│      │ ─────────────────────▶│ ─────────────────────▶│ ─────────────────────▶│                       │
│      │                       │                       │                       │                       │
│      │  5. Upload CSV        │  6. Parse & Generate  │  7. INSERT surveys    │                       │
│      │  (riders.csv)         │     surveys           │                       │                       │
│      │ ─────────────────────▶│ ─────────────────────▶│ ─────────────────────▶│                       │
│      │                       │                       │                       │                       │
│      │  8. Launch Surveys    │  9. Trigger calls/SMS │                       │                       │
│      │ ─────────────────────▶│ ─────────────────────▶│                       │                       │
│      │                       │                       │                       │                       │
│      │  10. View Analytics   │  11. GET /analytics   │  12. Query stats      │                       │
│      │ ─────────────────────▶│ ─────────────────────▶│ ─────────────────────▶│                       │
│      │                       │                       │                       │                       │
│      │  13. Dashboard View   │◀──────────────────────│◀──────────────────────│                       │
│      │  ┌─────────────────────────────────────────┐  │                       │                       │
│      │  │  📊 Total: 50 │ Done: 35 │ Rate: 70%   │  │                       │                       │
│      │  └─────────────────────────────────────────┘  │                       │                       │
│      │ ◀─────────────────────│                       │                       │                       │
│      │                       │                       │                       │                       │
│      │  14. Export CSV       │  15. GET /export      │  16. Query all        │                       │
│      │ ─────────────────────▶│ ─────────────────────▶│ ─────────────────────▶│                       │
│      │                       │                       │                       │                       │
│      │  17. Download file    │◀──────────────────────│◀──────────────────────│                       │
│      │ ◀─────────────────────│                       │                       │                       │
│                                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Multi-Tenant Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MULTI-TENANT SYSTEM                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐              │
│   │     OZARK       │   │  NEW BRAUNFELS  │   │    IT CURVES    │              │
│   │   Transit       │   │    Transit      │   │    (Admin)      │              │
│   ├─────────────────┤   ├─────────────────┤   ├─────────────────┤              │
│   │ tenant_id:      │   │ tenant_id:      │   │ tenant_id:      │              │
│   │ "ozark"         │   │ "newbraunfels"  │   │ "itcurves"      │              │
│   │                 │   │                 │   │                 │              │
│   │ Login:          │   │ Login:          │   │ Login:          │              │
│   │ ozark/ozark123  │   │ newbraunfels/   │   │ admin/admin123  │              │
│   │                 │   │ nb123           │   │                 │              │
│   └────────┬────────┘   └────────┬────────┘   └────────┬────────┘              │
│            │                     │                     │                        │
│            └─────────────────────┼─────────────────────┘                        │
│                                  │                                              │
│                                  ▼                                              │
│                    ┌─────────────────────────┐                                  │
│                    │    SHARED DATABASE      │                                  │
│                    │    (Data Isolation)     │                                  │
│                    ├─────────────────────────┤                                  │
│                    │ surveys.tenant_id       │                                  │
│                    │ campaigns.tenant_id     │                                  │
│                    │                         │                                  │
│                    │ Each agency sees only   │                                  │
│                    │ their own data          │                                  │
│                    └─────────────────────────┘                                  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Port Mapping

### External (Public) Ports

| Port | Service | Description |
|------|---------|-------------|
| 8080 | Gateway | Main API endpoint |
| 3000 | Recipient | Survey web app |
| 8082 | Dashboard | Admin interface |
| 5432 | PostgreSQL | Database (optional) |

### Gateway Routes

| Route | Target Service |
|-------|----------------|
| `/api/surveys/*` | survey-service:8020 |
| `/api/templates/*` | template-service:8040 |
| `/api/questions/*` | question-service:8030 |
| `/api/analytics/*` | analytics-service:8060 |
| `/api/brain/*` | brain-service:8016 |
| `/api/voice/*` | voice-service:8017 |
| `/api/scheduler/*` | scheduler-service:8070 |
| `/api/agent/*` | agent-service:8050 |

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React, Vite, Next.js, TailwindCSS, Material-UI |
| **Backend** | Python, FastAPI, Uvicorn |
| **AI/ML** | OpenAI GPT-4, VAPI Voice AI |
| **Database** | PostgreSQL 14, Redis 7 |
| **Communication** | Twilio SMS, VAPI Voice |
| **Infrastructure** | Docker, Docker Compose, Nginx |
| **Cloud** | AWS EC2 |

---

## Production URLs

| Service | URL |
|---------|-----|
| Dashboard | `http://54.86.65.150:8080/dashboard` |
| Recipient App | `http://54.86.65.150:3000` |
| API | `http://54.86.65.150:8080/api/` |

---

## Key Features

- 🎙️ **Natural AI Voice Calls** - Human-like conversations with empathy & dynamic follow-ups
- 🌐 **Multi-Channel** - Phone, SMS (Twilio), Web surveys
- 🇺🇸🇪🇸 **Bilingual** - English & Spanish
- 🏢 **Multi-Tenant Dashboard** - Agency-specific logins & data
- 📊 **Analytics** - Completion rates, demand tracking, incentive management
- 📤 **CSV Export** - Full data export capability
