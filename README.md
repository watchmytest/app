# watchmytest sync automation

This repository automatically tracks:

- Releases from `mov2day/watchmytest`
- Documentation-like files in `mov2day/watchmytest`

## How it works

A GitHub Actions workflow runs every 6 hours (and manually via `workflow_dispatch`) and regenerates `WATCHMYTEST_UPDATES.md` using the GitHub API.

- Workflow: `.github/workflows/sync-watchmytest.yml`
- Script: `scripts/sync_watchmytest.py`
- Output: `WATCHMYTEST_UPDATES.md`
