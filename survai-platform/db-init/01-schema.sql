-- Base schema: core tables
CREATE TABLE IF NOT EXISTS questions (
  id         TEXT PRIMARY KEY,
  text       TEXT NOT NULL,
  criteria   TEXT,
  scales     SMALLINT,
  parent_id  TEXT REFERENCES questions(id) ON DELETE SET NULL,
  autofill   TEXT DEFAULT 'No' NOT NULL
);

CREATE TABLE IF NOT EXISTS question_categories (
  id          TEXT PRIMARY KEY,
  question_id TEXT NOT NULL REFERENCES questions(id),
  text        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS question_category_mappings (
  child_question_id TEXT NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
  parent_category_id TEXT NOT NULL REFERENCES question_categories(id) ON DELETE CASCADE,
  PRIMARY KEY (child_question_id, parent_category_id)
);

CREATE TABLE IF NOT EXISTS templates (
  name          TEXT     PRIMARY KEY,
  created_at    TIMESTAMP NOT NULL,
  status        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS template_questions (
  template_name TEXT NOT NULL REFERENCES templates(name),
  question_id  TEXT  NOT NULL REFERENCES questions(id),
  ord          SMALLINT NOT NULL,
  PRIMARY KEY (template_name, question_id)
);

CREATE TABLE IF NOT EXISTS surveys (
  id                  TEXT   PRIMARY KEY,
  template_name       TEXT  NOT NULL REFERENCES templates(name),
  url                 TEXT,
  biodata             TEXT,
  status              TEXT,
  name                TEXT,
  recipient           TEXT,
  launch_date         TIMESTAMP NOT NULL,
  completion_date     TIMESTAMP,
  completion_duration SMALLINT,
  csat                SMALLINT,
  email               TEXT,
  phone               TEXT,
  rider_name          TEXT,
  ride_id             TEXT,
  tenant_id           TEXT,
  call_id             TEXT,
  workflow_id         TEXT
);

CREATE TABLE IF NOT EXISTS survey_response_items (
  survey_id     TEXT   NOT NULL REFERENCES surveys(id),
  question_id   TEXT   NOT NULL REFERENCES questions(id),
  ord           SMALLINT  NOT NULL,
  answer        TEXT,
  raw_answer    TEXT,
  autofill      TEXT,
  PRIMARY KEY (survey_id, question_id),
  UNIQUE (survey_id, ord)
);

CREATE TABLE IF NOT EXISTS job_history (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255),
    run_time TIMESTAMP NOT NULL,
    status VARCHAR(50)
);
