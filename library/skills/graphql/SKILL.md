---
name: graphql
description: GraphQL API design and implementation with schema design, resolvers, Apollo, and best practices
---

# GraphQL Development

## Schema Design
- Type system: scalar, object, input, enum, union, interface types
- Scalars: Int, Float, String, Boolean, ID, custom scalars (Date, JSON)
- Object types: fields with types, non-null (!), lists ([Type], [Type!]!)
- Input types: dedicated types for mutations, separate from output types
- Enums: finite set of allowed values
- Interfaces: shared fields across types, implementations
- Unions: type that could be one of several types, resolved with __typename
- Schema definition: type Query { }, type Mutation { }, type Subscription { }
- Directives: @deprecated, @skip, @include, custom directives

## Queries and Mutations
- Queries: read operations, field selection, nested fields
- Arguments: field(arg: Type), default values, required (!)
- Aliases: rename fields in response
- Fragments: reusable field selections, inline fragments (... on Type)
- Variables: $varName: Type, passed separately from query
- Mutations: create, update, delete operations, return modified data
- Input objects: grouping mutation arguments
- Subscriptions: real-time data, WebSocket-based

## Resolvers
- Resolver function: (parent, args, context, info) => result
- Context: shared state (auth, dataloaders, database connection)
- Default resolvers: trivial field resolution from parent
- Async resolvers: return Promise/async function
- Error handling: throw errors, format errors, error codes
- N+1 problem: DataLoader for batching and caching database queries
- DataLoader: batch function, per-request caching, loader.load(id)

## Server Implementation
- Apollo Server: type definitions + resolvers, plugins, context
- GraphQL Yoga: lightweight, Envelop plugin system
- NestJS GraphQL: code-first or schema-first, decorators
- Strawberry (Python): type-annotated schema definition
- Hot Chocolate (.NET): C# GraphQL server

## Client (Apollo Client)
- useQuery: loading, error, data states, variables, polling, refetching
- useMutation: mutate function, loading, error, onCompleted
- useLazyQuery: manual query execution
- Cache: InMemoryCache, type policies, field policies
- Cache updates: refetchQueries, cache.modify, cache.writeQuery
- Fragments on client: type-safe selections with useFragment
- Optimistic updates: optimisticResponse for instant UI feedback

## Pagination
- Cursor-based: edges/node/cursor pattern, pageInfo (hasNextPage, endCursor)
- Offset-based: limit/offset, simpler but less reliable
- Relay connection spec: standardized pagination format

## Authentication and Authorization
- Context: extract user from JWT/session in context function
- Field-level auth: directives (@auth, @hasRole) or resolver middleware
- Schema directives: custom directive implementations for auth

## Performance
- DataLoader: eliminate N+1 queries
- Query complexity: limit depth and complexity to prevent abuse
- Persisted queries: whitelist known queries, hash-based lookup
- Caching: HTTP caching headers, CDN, Apollo cache policies
- Fragments and selections: clients request only needed fields

## Best Practices
- Design schema around client needs, not database structure
- Use input types for mutations, separate from query types
- Non-null by default, nullable only when field can legitimately be null
- Pagination for all list fields
- DataLoader for every database relationship resolver
- Descriptive error messages with extensions for error codes
- Version via schema evolution, not URL versioning
- Document schema: descriptions on types and fields
