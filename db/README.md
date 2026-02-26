# Database Setup

This project uses PostgreSQL to store call records. Follow the steps below to set up the database on any system or server.

---

## Prerequisites

- PostgreSQL 14 or later installed and running
- `psql` CLI available (comes with PostgreSQL)

---

## 1. Install PostgreSQL

**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS (Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Other:** Follow the official guide at https://www.postgresql.org/download/

---

## 2. Create the Database and User

Connect as the postgres superuser:
```bash
sudo -u postgres psql
```

Then run:
```sql
CREATE DATABASE survey_bot;
-- Optional: create a dedicated user instead of using postgres
CREATE USER survey_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE survey_bot TO survey_user;
\q
```

---

## 3. Run the Schema

Create all required tables:
```bash
sudo -u postgres psql -d survey_bot -f db/schema.sql
```

Or if using a dedicated user with password:
```bash
psql -h localhost -U survey_user -d survey_bot -f db/schema.sql
```

Verify the table was created:
```bash
sudo -u postgres psql -d survey_bot -c "\dt"
```

Expected output:
```
        List of relations
 Schema | Name  | Type  |  Owner
--------+-------+-------+----------
 public | calls | table | postgres
```

---

## 4. Configure the Application

Update your `.env` file with the connection details:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=survey_bot
DB_USER=postgres
DB_PASSWORD=yourpassword
```

For a remote server, replace `localhost` with the server's IP or hostname.

---

## 5. Verify Connection

Start the agent — it performs a DB connection check on startup:
```bash
python agent.py start
```

On success you will see:
```
DB connection OK
```

On failure, the agent will exit with a clear error message pointing to the misconfigured credentials.

---

## Schema Reference

The schema is defined in [`schema.sql`](schema.sql). It creates one table:

```sql
CREATE TABLE IF NOT EXISTS calls (
    id                    SERIAL PRIMARY KEY,
    recipient_number      TEXT        NOT NULL,
    call_start_time       TIMESTAMPTZ NOT NULL,
    call_duration_seconds NUMERIC(8, 2),
    completed             BOOLEAN     DEFAULT FALSE,
    call_transcript       JSONB
);
```

`call_transcript` stores the full conversation as a JSON array of turn objects:
```json
[
  { "turn_index": 0, "speaker": "agent",    "text": "Hello...", "timestamp": "2026-02-24T15:28:18" },
  { "turn_index": 1, "speaker": "customer", "text": "Hi...",    "timestamp": "2026-02-24T15:28:22" }
]
```

---

## Querying Calls

Via the API (requires `api_server.py` running):
```bash
GET /calls/+13854156545
```

Directly via psql:
```sql
SELECT id, recipient_number, call_start_time, call_duration_seconds, completed
FROM calls
WHERE recipient_number = '+13854156545'
ORDER BY call_start_time DESC;
```
