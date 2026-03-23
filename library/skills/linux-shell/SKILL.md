---
name: linux-shell
description: Linux command line, shell scripting, system administration, and automation
---

# Linux & Shell

## Essential Commands
```bash
# File operations
find . -name "*.py" -mtime -7       # files modified in last 7 days
grep -rn "TODO" src/                 # search recursively with line numbers
wc -l src/**/*.py                    # count lines of code
du -sh */                            # directory sizes
tail -f /var/log/app.log             # follow log output
watch -n 2 "curl -s localhost:8000/health"  # repeat command every 2s

# Process management
ps aux | grep python
kill -SIGTERM <pid>                  # graceful stop
lsof -i :8000                       # what's using port 8000
nohup ./script.sh &                 # run in background, survive logout

# Networking
curl -s http://localhost:8000/api/health | jq .
ss -tlnp                            # listening ports
```

## Bash Scripting
```bash
#!/usr/bin/env bash
set -euo pipefail  # exit on error, undefined vars, pipe failures

# Variables
APP_DIR="${APP_DIR:-/opt/app}"
LOG_FILE="$APP_DIR/app.log"

# Functions
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# Conditionals
if [[ -f "$LOG_FILE" ]]; then
  log "Log file exists"
else
  log "Creating log file"
  touch "$LOG_FILE"
fi

# Loops
for f in "$APP_DIR"/*.py; do
  log "Processing: $f"
done
```

## File Permissions
```
chmod 755 script.sh    # rwxr-xr-x (owner: all, group/others: read+execute)
chmod 644 config.yaml  # rw-r--r-- (owner: read+write, others: read)
chmod 600 .env         # rw------- (owner only)
chown user:group file
```

## Text Processing
```bash
# awk — column extraction
awk '{print $1, $3}' access.log

# sed — find and replace
sed -i 's/old_text/new_text/g' file.txt

# sort + uniq — frequency analysis
cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# jq — JSON processing
curl -s api/status | jq '.services[] | select(.healthy == false)'
```

## Environment Management
- Use `.env` files for local config (never commit)
- Use `direnv` or `source .env` for loading
- Export variables: `export VAR="value"`
- Check if set: `${VAR:?Error: VAR not set}`
