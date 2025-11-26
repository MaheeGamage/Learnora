# DB connection limits (Supabase / pooled Postgres)

Problem (short):
- Your app can open more client sessions than Supabase's pooler allows. When that happens asyncpg reports:
  "MaxClientsInSessionMode: max clients reached - in Session mode max clients are limited to pool_size"

Why it happens (one line):
- Long-lived client pools (per process) × multiple processes exceed the server-side pool limit.

Prioritized fixes (easy → harder):

1) Dev quick: disable client pooling
- Leave `DB_POOL_SIZE` unset in `.env` (our app defaults to NullPool in dev). This avoids long-lived sessions.

2) Small explicit pool
- Set `DB_POOL_SIZE=3` and `DB_MAX_OVERFLOW=0` in `.env` so each process keeps only a few connections.

3) Run fewer processes in dev
- Start the server with a single worker / disable extra reload workers to reduce total pools.

4) Use transaction pooling (recommended for production)
- Enable Supabase / pgbouncer transaction pooling so many app clients share fewer server connections.

5) Scale or clear connections
- If DB is saturated, use Supabase dashboard to restart or terminate idle backends, or upgrade plan.

Quick diagnostics (safe):
- View connections:
  ```sql
  SELECT state, application_name, count(*) FROM pg_stat_activity GROUP BY state, application_name;
  ```
- Terminate an idle session (careful):
  ```sql
  SELECT pg_terminate_backend(<pid>);
  ```

Notes:
- Calculate safe pool size: let L = DB connection limit, P = # processes, choose S so P * S <= L - reserve.
- Avoid killing internal Supabase processes (pgbouncer, postgrest).

Short and simple — follow 1) for dev, 2)–3) for small deployments, 4) for production.
