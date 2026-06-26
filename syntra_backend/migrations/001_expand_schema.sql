-- ═══════════════════════════════════════════════════════
-- Syntra AI - Database Expansion Migration
-- Run this in your Supabase SQL Editor
-- ═══════════════════════════════════════════════════════

-- 1. Create ENUM type for feature names
DO $$ BEGIN
    CREATE TYPE featurenameenum AS ENUM ('enhance', 'intent', 'compress', 'chat');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 2. Workspaces table
CREATE TABLE IF NOT EXISTS workspaces (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_workspaces_user_id ON workspaces(user_id);

-- 3. Default Workspace (for history logging before UI is connected)
-- This inserts a "Default Workspace" for any existing user with id=1
INSERT INTO workspaces (user_id, name, description)
SELECT 1, 'Default Workspace', 'Auto-created default workspace'
WHERE EXISTS (SELECT 1 FROM users WHERE id = 1)
  AND NOT EXISTS (SELECT 1 FROM workspaces WHERE user_id = 1 AND name = 'Default Workspace');

-- 4. Chat Sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    workspace_id INTEGER NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    session_name VARCHAR(255) NOT NULL DEFAULT 'Untitled Session',
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_workspace_id ON chat_sessions(workspace_id);

-- 5. Default Session (needed for history logging before Workspace UI is connected)
--    Uses sequence-assigned id — the backend always uses session_id=1 by default
INSERT INTO chat_sessions (id, workspace_id, session_name)
SELECT 1,
       (SELECT id FROM workspaces WHERE user_id = 1 AND name = 'Default Workspace' LIMIT 1),
       'Default Session'
WHERE NOT EXISTS (SELECT 1 FROM chat_sessions WHERE id = 1)
  AND EXISTS (SELECT 1 FROM workspaces WHERE user_id = 1 AND name = 'Default Workspace');

-- 6. Feature History table
CREATE TABLE IF NOT EXISTS feature_history (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    feature_name featurenameenum NOT NULL,
    input_prompt TEXT NOT NULL,
    output_data TEXT NOT NULL,
    model_used VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_feature_history_feature_name ON feature_history(feature_name);
CREATE INDEX IF NOT EXISTS idx_feature_history_session_id ON feature_history(session_id);
CREATE INDEX IF NOT EXISTS idx_feature_history_created_at ON feature_history(created_at DESC);

-- 7. Usage Metrics table
CREATE TABLE IF NOT EXISTS usage_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    feature_name featurenameenum NOT NULL,
    provider VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_usage_metrics_user_id ON usage_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_metrics_provider ON usage_metrics(provider);
