---
name: project-scaffolding
description: Create new projects from scratch with proper structure, tooling, and configuration for any stack
---

# Project Scaffolding

Generate well-structured projects with proper tooling, configuration, and conventions from the start.

## Python Project Setup

```
my-project/
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── main.py
│       └── config.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── pyproject.toml
├── README.md
├── .gitignore
└── .env.example
```

### pyproject.toml (modern Python)

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "my-project"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=7.4", "ruff>=0.1", "mypy>=1.5"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

## Node.js / TypeScript Project

```
my-app/
├── src/
│   ├── index.ts
│   ├── config.ts
│   └── routes/
├── tests/
│   └── index.test.ts
├── package.json
├── tsconfig.json
├── .eslintrc.json
├── .gitignore
└── README.md
```

### tsconfig.json essentials

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

## React / Vite Frontend

```bash
npm create vite@latest my-app -- --template react-ts
```

Standard structure:
```
src/
├── components/     # Reusable UI components
├── hooks/          # Custom React hooks
├── pages/          # Route-level components
├── styles/         # CSS/SCSS files
├── utils/          # Helper functions
├── api/            # API client functions
├── App.tsx
└── main.tsx
```

## FastAPI Backend

```
backend/
├── src/
│   ├── main.py          # App factory, middleware
│   ├── config.py        # Settings via pydantic-settings
│   ├── database.py      # SQLAlchemy engine/session
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response
│   ├── routers/         # Route handlers
│   └── services/        # Business logic
├── migrations/
│   └── alembic/
├── tests/
├── pyproject.toml
└── Dockerfile
```

## Essential Config Files

### .gitignore patterns

```
# Python
__pycache__/
*.pyc
.venv/
*.egg-info/
dist/

# Node
node_modules/
dist/
.next/

# Environment
.env
.env.local
*.enc

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

### .env.example

Always include an example env file with dummy values:
```
DATABASE_URL=sqlite:///./dev.db
API_KEY=your-key-here
LOG_LEVEL=INFO
PORT=8000
```

## Monorepo Setup

```
monorepo/
├── packages/
│   ├── shared/        # Shared types/utils
│   ├── frontend/      # React app
│   └── backend/       # API server
├── package.json       # Workspace root
├── turbo.json         # Turborepo config (or nx.json)
└── tsconfig.base.json
```

## Decision Checklist

Before scaffolding, determine:
1. **Runtime**: Python, Node, Deno, Go?
2. **Package manager**: pip/uv, npm/pnpm/yarn?
3. **TypeScript?** Almost always yes for JS projects
4. **Testing framework**: pytest, vitest, jest?
5. **Linter/formatter**: ruff, eslint+prettier, biome?
6. **CI/CD**: GitHub Actions, GitLab CI?
7. **Containerized?** Dockerfile from day one if deploying
8. **Database?** ORM choice drives project shape
