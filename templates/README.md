# Piddy Templates

Reusable scaffolds for quickly spinning up new APIs, microservices, workers, and other components.
Clone a template folder to start a new project instead of building from scratch.

## Available Templates

| Template | Description | Stack |
|----------|-------------|-------|
| `api/` | FastAPI REST endpoint scaffold | Python, FastAPI, Pydantic |
| `microservice/` | Standalone microservice with health checks | Python, FastAPI, Docker |
| `worker/` | Background task processor | Python, asyncio |
| `webhook/` | Incoming webhook receiver | Python, FastAPI, HMAC |
| `database/` | Database schema + migration starter | SQLAlchemy, Alembic |

## Usage

```bash
# Copy a template to start a new component
cp -r templates/api/ src/my_new_api/

# Or use Piddy's built-in scaffolding
python start_piddy.py scaffold --template api --name my_new_api
```
