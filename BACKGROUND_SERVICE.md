# Piddy Background Service Setup

This guide covers how to run Piddy as a continuous background service that listens to Slack messages 24/7.

## Quick Start

### Option 1: Simple Background Start (Development)

```bash
# Start Piddy in the background
./piddy-service.sh start

# Check status
./piddy-service.sh status

# View live logs
./piddy-service.sh logs

# Stop when done
./piddy-service.sh stop
```

### Option 2: Systemd Service (Production/Linux)

```bash
# Install as systemd service (one-time setup)
./piddy-service.sh install-service

# Enable auto-start on boot
sudo systemctl enable piddy@$USER

# Start the service
sudo systemctl start piddy@$USER

# Check status
sudo systemctl status piddy@$USER

# View logs
sudo journalctl -u piddy@$USER -f

# Stop the service
sudo systemctl stop piddy@$USER
```

## Service Management Commands

### Using piddy-service.sh

```bash
# Start Piddy in background
./piddy-service.sh start

# Stop Piddy gracefully
./piddy-service.sh stop

# Restart (stop + start)
./piddy-service.sh restart

# Check current status
./piddy-service.sh status

# View live logs
./piddy-service.sh logs

# Verify all prerequisites are met
./piddy-service.sh check

# Install as systemd service (Linux)
./piddy-service.sh install-service

# Remove systemd service
./piddy-service.sh uninstall-service
```

### Using systemd Commands (Linux)

```bash
# Start service
sudo systemctl start piddy@$USER

# Stop service
sudo systemctl stop piddy@$USER

# Restart service
sudo systemctl restart piddy@$USER

# Check service status
sudo systemctl status piddy@$USER

# View real-time logs
sudo journalctl -u piddy@$USER -f

# View last 100 lines
sudo journalctl -u piddy@$USER -n 100

# Enable auto-start on reboot
sudo systemctl enable piddy@$USER

# Disable auto-start
sudo systemctl disable piddy@$USER
```

## Features

### Automatic Restart

- Piddy automatically restarts if it crashes
- Exponential backoff (2s, 4s, 8s, 16s, 32s, 60s max)
- Maximum 5 restart attempts before stopping
- All retries logged for debugging

### Health Monitoring

The service includes comprehensive health monitoring:

```bash
# Quick health check
curl http://localhost:8000/health

# Detailed health status with metrics
curl http://localhost:8000/health/detailed

# Full service status
curl http://localhost:8000/status
```

Example response:
```json
{
  "health": {
    "status": "healthy",
    "pid": 12345,
    "uptime": 3600.5,
    "messages_processed": 42,
    "errors": 0,
    "latency_ms": 2.3,
    "memory_usage_mb": 145.6
  },
  "performance": {
    "uptime_hours": 1.0,
    "messages_processed": 42,
    "messages_per_hour": 42.0,
    "error_rate_percent": 0.0,
    "availability": "100.0%"
  }
}
```

### Status Files

Piddy creates status files to track its state:

- `.piddy_service_status.json` — Current service metrics
- `.piddy_service.log` — Service logs  
- `.piddy_audit.log` — Audit events
- `.piddy_memory.db` — Conversation memory database
- `.piddy_patterns.json` — Learned patterns

View current status:
```bash
cat .piddy_service_status.json
```

View logs:
```bash
# Follow logs in real-time
tail -f .piddy_service.log

# View last 50 lines
tail -50 .piddy_service.log

# Search for errors
grep ERROR .piddy_service.log
```

## Prerequisites

Before starting Piddy as a service, ensure:

1. ✅ Virtual environment created and activated
2. ✅ Dependencies installed (`pip install -r requirements.txt`)
3. ✅ `.env` file configured with:
   - `SLACK_BOT_TOKEN` — Slack bot token
   - `SLACK_APP_TOKEN` — Slack app token
   - `ANTHROPIC_API_KEY` — Claude API key
4. ✅ `start-slack.sh` script is executable

Run the prerequisite check:
```bash
./piddy-service.sh check
```

Output:
```
✅ Python found: Python 3.12.1
✅ Virtual environment ready
✅ Dependencies installed
✅ SLACK_BOT_TOKEN configured
✅ SLACK_APP_TOKEN configured
✅ ANTHROPIC_API_KEY configured
✅ start-slack.sh exists
✅ All prerequisites met, ready to start Piddy
```

## Configuration

### Service Resource Limits

The systemd service includes resource limits:

- **CPU**: 80% max utilization
- **Memory**: 2GB max allocation
- **Restart**: Always (with 10-second delay)

Edit `piddy.service` to change:
```ini
CPUQuota=80%                    # Change CPU limit
MemoryLimit=2G                  # Change memory limit
RestartSec=10                   # Change restart delay
```

Then reinstall:
```bash
./piddy-service.sh uninstall-service
# Edit piddy.service
./piddy-service.sh install-service
```

### Environment Configuration

Edit `.env` to customize:

```env
# Slack Settings
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_APP_TOKEN=xapp-your-token
SLACK_SIGNING_SECRET=your-secret

# API Configuration
ANTHROPIC_API_KEY=sk-your-key
AGENT_MODEL=claude-opus-4-1-20250805
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=4096

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

## Monitoring in Production

### Health Check Loop

Monitor Piddy health continuously:

```bash
#!/bin/bash
# Monitor every 30 seconds
while true; do
  status=$(curl -s http://localhost:8000/health | jq .health.status)
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] Status: $status"
  sleep 30
done
```

### Metrics Collection

View performance metrics:

```bash
# Get performance summary
curl http://localhost:8000/status | jq .performance

# Example output:
{
  "uptime_hours": 24.5,
  "messages_processed": 156,
  "messages_per_hour": 6.37,
  "error_rate_percent": 0.0,
  "availability": "100.0%"
}
```

### Alert on Failures

Set up alerts using monitoring tools:

```bash
# Check if service is unhealthy and send alert
health_status=$(curl -s http://localhost:8000/health | jq -r .health.status)
if [ "$health_status" != "healthy" ]; then
  # Send alert (email, Slack, PagerDuty, etc.)
  echo "Piddy health status: $health_status" | mail -s "Piddy Alert" admin@example.com
fi
```

## Troubleshooting

### Service Won't Start

1. Check prerequisites:
   ```bash
   ./piddy-service.sh check
   ```

2. Check logs:
   ```bash
   tail -f .piddy_service.log
   ```

3. Verify .env file:
   ```bash
   grep SLACK_ .env
   grep ANTHROPIC_ .env
   ```

### Service Keeps Restarting

1. View error logs:
   ```bash
   grep ERROR .piddy_service.log | tail -20
   ```

2. Check memory usage:
   ```bash
   curl http://localhost:8000/health/detailed | jq .health.memory_usage_mb
   ```

3. Verify token validity (tokens may expire)

### High Memory Usage

1. Check current memory:
   ```bash
   curl http://localhost:8000/health/detailed | jq .health.memory_usage_mb
   ```

2. Clear cache if needed:
   ```bash
   curl -X POST http://localhost:8000/api/tools/clear_cache
   ```

3. Restart service:
   ```bash
   ./piddy-service.sh restart
   ```

### No Slack Messages Received

1. Verify Slack app is configured:
   - Check bot token is valid
   - Confirm Piddy bot is in channels
   - Verify Socket Mode is enabled

2. Check Slack integration status:
   ```bash
   grep "Socket Mode" .piddy_service.log
   ```

3. Monitor message flow:
   ```bash
   tail -f .piddy_service.log | grep -i "slack\|request"
   ```

## Slack Usage

Once Piddy is running in the background, interact with it on Slack:

### Direct Messages

Send direct messages to Piddy to start conversations:

```
You: @Piddy generate a Python FastAPI endpoint for user authentication

Piddy: [Generates complete authentication endpoint with code examples]
```

### Commands

Use shorthand commands for specific tasks:

```
@Piddy commit                    # Auto-commit staged changes
@Piddy git status               # Check git status
@Piddy analyze_code_multilingual [code]  # Multi-language analysis
@Piddy review this: [code]      # Advanced code review
```

### Conversation Flow

Ask follow-up questions naturally:

```
You: @Piddy generate a REST API for managing tasks
Piddy: [Generates task API]

You: @Piddy add pagination to the list endpoint
Piddy: [Updates with pagination]

You: @Piddy add authentication
Piddy: [Adds auth middleware]

You: @Piddy commit all changes
Piddy: [Commits to git]
```

## Logs and Debugging

### View Service Logs

```bash
# Real-time logs
tail -f .piddy_service.log

# Last 100 lines
tail -100 .piddy_service.log

# Filter by level
grep "ERROR\|CRITICAL" .piddy_service.log

# View with timestamps
tail -f .piddy_service.log | awk '{print systime()" "$0}'
```

### Enable Debug Mode

In `.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

Then restart:
```bash
./piddy-service.sh restart
```

### Generate Status Report

```bash
# Create status report
cat > piddy_status_report.txt << EOF
=== Piddy Service Status Report ===
Generated: $(date)

=== Service Status ===
$(./piddy-service.sh status)

=== Health Check ===
$(curl -s http://localhost:8000/health/detailed)

=== Recent Logs ===
$(tail -50 .piddy_service.log)

=== Prerequisites ===
$(./piddy-service.sh check)
EOF

echo "Report saved to piddy_status_report.txt"
```

## Advanced Setup

### Multiple Instances

Run multiple Piddy instances for load balancing:

```bash
# Instance 1 (port 8000)
PIDDY_PORT=8000 ./piddy-service.sh start &

# Instance 2 (port 8001)
PIDDY_PORT=8001 ./piddy-service.sh start &

# Instance 3 (port 8002)
PIDDY_PORT=8002 ./piddy-service.sh start &

# Monitor all
./piddy-service.sh status
```

### Docker Container

Run Piddy in Docker for consistent environments:

```bash
# Build image
docker build -t piddy:latest .

# Run container
docker run -d \
  --name piddy \
  -e SLACK_BOT_TOKEN=$SLACK_BOT_TOKEN \
  -e SLACK_APP_TOKEN=$SLACK_APP_TOKEN \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  -p 8000:8000 \
  piddy:latest

# View logs
docker logs -f piddy

# Stop container
docker stop piddy
```

### Kubernetes Deployment

Deploy Piddy on Kubernetes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: piddy
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: piddy
        image: piddy:latest
        env:
        - name: SLACK_BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: piddy-secrets
              key: slack-bot-token
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## Summary

Piddy is now ready to run as a background service! 

### Quick Checklist

- [ ] Prerequisites verified: `./piddy-service.sh check`
- [ ] `.env` file configured with Slack tokens
- [ ] Service started: `./piddy-service.sh start`
- [ ] Health check passing: `curl http://localhost:8000/health`
- [ ] Service monitoring active
- [ ] Ready to message Piddy on Slack! 🚀

### Next Steps

1. Start the service: `./piddy-service.sh start`
2. Monitor status: `./piddy-service.sh status`
3. Message Piddy on Slack
4. View logs: `./piddy-service.sh logs`
5. Set up monitoring alerts (optional)

---

For issues or questions, check the logs with `./piddy-service.sh logs` and refer to the Troubleshooting section.
