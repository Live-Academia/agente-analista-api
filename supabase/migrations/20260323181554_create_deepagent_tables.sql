-- Deep Agent: tabelas internas de logging e historico
-- Prefixo _deepagent_ para nao colidir com tabelas do usuario

CREATE TABLE IF NOT EXISTS _deepagent_logs (
  id           BIGSERIAL PRIMARY KEY,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  session_id   TEXT,
  username     TEXT,
  operation    TEXT NOT NULL,
  source_name  TEXT,
  duration_ms  INTEGER,
  status       TEXT,
  metadata     JSONB
);

CREATE TABLE IF NOT EXISTS _deepagent_analyses (
  id                   BIGSERIAL PRIMARY KEY,
  created_at           TIMESTAMPTZ DEFAULT NOW(),
  session_id           TEXT UNIQUE,
  username             TEXT,
  source_name          TEXT NOT NULL,
  template_used        TEXT,
  data_summary         JSONB NOT NULL,
  statistical_analysis JSONB,
  patterns             JSONB,
  insights             JSONB
);

CREATE TABLE IF NOT EXISTS _deepagent_messages (
  id           BIGSERIAL PRIMARY KEY,
  created_at   TIMESTAMPTZ DEFAULT NOW(),
  session_id   TEXT NOT NULL,
  username     TEXT,
  role         TEXT NOT NULL,
  content      TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_deepagent_messages_session  ON _deepagent_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_deepagent_logs_username     ON _deepagent_logs(username);
CREATE INDEX IF NOT EXISTS idx_deepagent_analyses_username ON _deepagent_analyses(username);
