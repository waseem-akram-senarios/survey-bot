-- Survey Bot Database Schema
-- Run this file once on any environment to initialize the database:
--   psql $DATABASE_URL -f db/schema.sql

CREATE TABLE IF NOT EXISTS calls (
    id                    SERIAL PRIMARY KEY,
    recipient_number      TEXT        NOT NULL,
    call_start_time       TIMESTAMPTZ NOT NULL,
    call_duration_seconds NUMERIC(8, 2),
    completed             BOOLEAN     DEFAULT FALSE,
    call_transcript       JSONB
    -- call_transcript is a JSON array of turn objects:
    -- [
    --   { "turn_index": 0, "speaker": "agent",    "text": "...", "timestamp": "2026-02-24T15:28:24" },
    --   { "turn_index": 1, "speaker": "customer", "text": "...", "timestamp": "2026-02-24T15:28:30" }
    -- ]
);

-- Index for fast lookup by phone number and date range
CREATE INDEX IF NOT EXISTS idx_calls_recipient_number ON calls (recipient_number);
CREATE INDEX IF NOT EXISTS idx_calls_call_start_time  ON calls (call_start_time);
