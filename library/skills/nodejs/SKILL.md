---
name: nodejs
description: Server-side JavaScript with Node.js, Express, NestJS, databases, authentication, and production patterns
---

# Node.js Backend Development

## Core Node.js
- Event loop: single-threaded, non-blocking I/O, microtasks vs macrotasks
- Modules: ES modules (import/export), CommonJS (require/module.exports)
- Built-in modules: fs/promises, path, url, crypto, http, stream, events, child_process
- Streams: Readable, Writable, Transform, Duplex — pipeline() for chaining
- Buffer: binary data, Buffer.from, toString encoding
- EventEmitter: on, emit, once, removeListener
- Worker threads: CPU-intensive tasks off the main thread
- Environment: process.env, dotenv, node --env-file (Node 20+)
- Error handling: try/catch for async, process.on('uncaughtException'), process.on('unhandledRejection')

## Express
- App setup: express(), app.listen, middleware pipeline
- Routing: app.get/post/put/delete, Router(), route parameters (:id)
- Middleware: (req, res, next) => {}, app.use, order matters
- Request: req.params, req.query, req.body (with express.json())
- Response: res.json(), res.status(), res.send(), res.redirect()
- Error handling middleware: (err, req, res, next) — must have 4 params
- Static files: express.static('public')
- CORS: cors() middleware, origin configuration
- Rate limiting: express-rate-limit
- Helmet: security headers

## NestJS
- Modules: @Module, imports, controllers, providers
- Controllers: @Controller, @Get/@Post/@Put/@Delete, @Param, @Body, @Query
- Services: @Injectable, constructor injection
- Pipes: validation (ValidationPipe), transformation
- Guards: @UseGuards, CanActivate for auth
- Interceptors: logging, transformation, caching
- DTOs: class-validator decorators (@IsString, @IsEmail, @MinLength)
- TypeORM/Prisma integration
- Swagger: @ApiTags, @ApiOperation, auto-generated docs

## Database Integration
- Prisma: schema.prisma, prisma generate, type-safe client, migrations
- TypeORM: entities, repositories, query builder, migrations
- Knex: SQL query builder, migrations, seeds
- Mongoose: schemas, models, middleware, population (MongoDB)
- Connection pooling: pg Pool, mysql2 pool
- Redis: ioredis, caching, sessions, pub/sub, queues (BullMQ)

## Authentication
- JWT: jsonwebtoken, access + refresh token pattern
- Passport.js: strategies (local, jwt, oauth2), serialize/deserialize
- Session-based: express-session, connect-redis
- OAuth2/OIDC: authorization code flow, PKCE
- Password hashing: bcrypt, argon2 (prefer argon2)
- Rate limiting on auth endpoints

## API Design
- RESTful: resource-based URLs, proper HTTP methods and status codes
- Input validation: Joi, Zod, class-validator
- Pagination: cursor-based (preferred) or offset-based
- Filtering and sorting: query parameters
- Error responses: consistent format { error: { code, message, details } }
- API versioning: URL path (/v1/) or header-based
- File uploads: multer middleware, streaming to storage

## Testing
- Jest: describe/it, expect, beforeAll/afterAll, mocking
- Supertest: HTTP assertion library for Express
- Integration tests: test database, setup/teardown
- Mocking: jest.mock, jest.spyOn, manual mocks in __mocks__/
- E2E: Supertest against running app, test containers

## Production
- PM2: process manager, cluster mode, zero-downtime reload
- Logging: pino (fast structured logging), log levels
- Health checks: /health and /ready endpoints
- Graceful shutdown: SIGTERM handler, drain connections
- Security: helmet, CORS, rate limiting, input sanitization
- Docker: multi-stage build, node:alpine, non-root user

## Best Practices
- Always use async/await over callbacks
- Validate all external input at API boundaries
- Use parameterized queries — never string interpolation for SQL
- Structure: routes → controllers → services → repositories
- Keep route handlers thin — business logic in services
- Use environment variables for all configuration
- Handle errors centrally with error-handling middleware
