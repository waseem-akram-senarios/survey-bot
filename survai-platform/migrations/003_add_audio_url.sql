-- Add audio_url column to call_transcripts for storing call recording URLs
ALTER TABLE call_transcripts
    ADD COLUMN IF NOT EXISTS audio_url TEXT;
