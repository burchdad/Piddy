---
name: auto-maintenance
description: Automated maintenance routines for keeping projects healthy — dependency updates, cleanup, health checks, and housekeeping
---

# Auto Maintenance

Keep projects healthy with systematic maintenance routines. Run these checks regularly to prevent decay.

## Daily Checks

```
□ Build still passes?
□ Tests still green?
□ No new security advisories?
□ Logs show any new errors?
□ Disk space adequate?
```

## Weekly Maintenance

### Dependency Updates

```bash
# Python
pip list --outdated
pip audit                    # Check for vulnerabilities
# Update one at a time, test between each
pip install --upgrade <package>

# Node.js
npm outdated
npm audit
npm update                   # Minor/patch updates
npx npm-check-updates -u     # Major updates (review first)
```

### Update strategy

| Type | Action | Risk |
|------|--------|------|
| Patch (1.0.x) | Auto-update | Low — bug fixes |
| Minor (1.x.0) | Review changelog, then update | Medium — new features |
| Major (x.0.0) | Read migration guide, test thoroughly | High — breaking changes |

### Dead Code Cleanup

```bash
# Find unused Python imports
ruff check --select F401 src/

# Find unused JavaScript exports
npx ts-prune

# Find unused dependencies
pip install pip-autoremove
pip-autoremove --list

npx depcheck
```

### Log Rotation

```python
# Keep logs from growing unbounded
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    'app.log',
    maxBytes=10_000_000,   # 10MB
    backupCount=5           # Keep 5 rotated files
)
```

## Monthly Maintenance

### Database Maintenance

```sql
-- SQLite: reclaim space after deletes
VACUUM;

-- Analyze tables for query optimizer
ANALYZE;

-- Check database integrity
PRAGMA integrity_check;
```

### Security Audit

```bash
# Python
pip audit
safety check

# Node.js
npm audit
npx snyk test

# Docker
docker scout cves <image>
```

### Performance Baseline

- Record current response times
- Record database query times
- Record build/test duration
- Compare against previous month
- Investigate any regressions > 20%

## Cleanup Checklist

### Files to remove periodically

```
□ __pycache__/ and *.pyc files
□ node_modules/.cache/
□ .pytest_cache/
□ dist/ and build/ (if rebuilding)
□ Old log files
□ Temporary test files (_test_*.py, *.tmp)
□ Orphaned migration files
□ Unused configuration files
```

### Git hygiene

```bash
# Remove merged branches
git branch --merged | grep -v "main\|master" | xargs git branch -d

# Clean up remote tracking branches
git remote prune origin

# Check repo size
git count-objects -vH
```

## Health Dashboard Signals

| Signal | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Build | Passes | Flaky (intermittent) | Broken |
| Tests | 100% passing | >95% passing | <95% |
| Dependencies | All current | 1-2 minor behind | Security advisory |
| Disk | >20% free | 10-20% free | <10% |
| Response time | <200ms | 200-500ms | >500ms |

## Automation Tips

1. **Schedule updates** — Don't wait for things to break
2. **Atomic changes** — Update one thing, verify, commit
3. **Pin versions** — Use lockfiles, not loose version ranges
4. **Monitor alerts** — Set up notifications for failures
5. **Document changes** — Keep a changelog of maintenance work
