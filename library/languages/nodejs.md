# Node.js Quick Reference

## Language: Node.js 20+ (LTS)
**Paradigm:** Event-driven, non-blocking I/O  
**Engine:** V8 JavaScript engine  
**Packages:** npm, pnpm, yarn  

## Core Modules

```javascript
import { readFile, writeFile, mkdir, readdir } from 'node:fs/promises';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createServer } from 'node:http';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
```

## File System

```javascript
const content = await readFile('data.json', 'utf-8');
await writeFile('output.json', JSON.stringify(data, null, 2));
await mkdir('output/sub', { recursive: true });

// Streams (large files)
import { createReadStream, createWriteStream } from 'node:fs';
import { pipeline } from 'node:stream/promises';
await pipeline(createReadStream('large.csv'), transform, createWriteStream('out.csv'));
```

## HTTP Server & Express

```javascript
import express from 'express';
const app = express();
app.use(express.json());

app.get('/api/users', async (req, res) => {
  const users = await db.users.findAll();
  res.json(users);
});

app.post('/api/users', async (req, res) => {
  const user = await db.users.create(req.body);
  res.status(201).json(user);
});

app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
});

app.listen(3000);
```

## Common Packages

| Package | Purpose |
|---------|---------|
| `express` / `fastify` | HTTP framework |
| `prisma` / `drizzle-orm` | Database ORM |
| `zod` | Schema validation |
| `pino` / `winston` | Logging |
| `vitest` / `jest` | Testing |
| `tsx` | TypeScript execution |

## Tooling

```bash
npm init -y
npm install package
npx tsx src/index.ts
node --watch src/index.js  # built-in watch (18.11+)
node --test                # built-in test runner
```
