-- Run this in Supabase SQL Editor (https://supabase.com/dashboard → SQL Editor)

CREATE TABLE IF NOT EXISTS inspections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    type TEXT NOT NULL,
    unit_number INT DEFAULT 1,
    checklist_data JSONB NOT NULL,
    photo_url TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'baik',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast queries by type + date
CREATE INDEX IF NOT EXISTS idx_inspections_type_date 
ON inspections (type, created_at DESC);

-- Verify
SELECT 'Table inspections created successfully!' AS result;
