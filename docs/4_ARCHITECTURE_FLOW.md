# Architecture & Control Flow

## The Stack
*   **Frontend / Portal:** Streamlit (Admin & Worker)
*   **Database:** Supabase (PG) + Offline Unified Dictionary Sync
*   **AI/ML:** Scikit-Learn | Google Generative AI 
*   **Cron:** APScheduler

## Process Lifecycle
1. **Sweep:** Background Scheduler triggers API sweep.
2. **Breach:** Environment detects threshold crossed.
3. **Guard:** API is validated for non-tampered bounds (<150mm).
4. **Calculations:** Total pool exposure measured. If <40% pool balance, proceed.
5. **Execution:** ML Risk algorithm validates lack of geographic proxy clusters.
6. **Payout:** Engine generates simulated hashes.
7. **Sync:** Cloud DB reflects new pool. Dashboards update instantly.

## Hybrid Safe-State Pattern
If Supabase times out, the `BaseRepository._data` cache natively absorbs operations, routing the UI into a verified `FALLBACK MODE` without missing an execution frame.
