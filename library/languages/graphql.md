# GraphQL Quick Reference

## Language: GraphQL (Oct 2021 Spec)
**Paradigm:** Declarative query language for APIs  
**Typing:** Static, strong schema  
**Transport:** Typically HTTP POST, also WebSocket for subscriptions  

## Schema Definition

```graphql
type User {
  id: ID!
  name: String!
  email: String
  posts(first: Int = 10): PostConnection!
}

input CreateUserInput {
  name: String!
  email: String!
}

enum Role { USER ADMIN MODERATOR }

type Query {
  user(id: ID!): User
  users(first: Int, after: String): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  deleteUser(id: ID!): Boolean!
}
```

## Queries

```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    name
    posts(first: 5) {
      edges { node { title } }
    }
  }
}

# Fragments
fragment UserFields on User { id name email }

query { user(id: "1") { ...UserFields } }
```

## Pagination (Relay Cursor)

```graphql
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PageInfo {
  hasNextPage: Boolean!
  endCursor: String
}

query {
  users(first: 10, after: "cursor123") {
    edges { node { id name } cursor }
    pageInfo { hasNextPage endCursor }
  }
}
```

## Best Practices

| Pattern | Description |
|---------|-------------|
| Input types | Use dedicated input types for mutations |
| Connections | Cursor-based pagination for lists |
| Batching | Use DataLoader to avoid N+1 |
| Depth limiting | Prevent deeply nested queries |
| Persisted queries | Hash queries for security/performance |
