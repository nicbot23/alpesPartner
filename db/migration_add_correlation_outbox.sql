-- Migration script to add correlation and causation columns to existing outbox_event table
-- Safe to run multiple times (uses conditional checks)
ALTER TABLE outbox_event ADD COLUMN IF NOT EXISTS correlation_id CHAR(36) NULL;
ALTER TABLE outbox_event ADD COLUMN IF NOT EXISTS causation_id CHAR(36) NULL;
CREATE INDEX IF NOT EXISTS idx_outbox_correlation ON outbox_event (correlation_id);
