---
name: elixir
description: Elixir programming with Phoenix framework, OTP patterns, concurrency, and the BEAM virtual machine
---

# Elixir and Erlang Development

## Core Language
- Immutability: all data is immutable, transformations return new values
- Pattern matching: = is match operator, destructuring, pin operator ^
- Data types: atoms, tuples, lists, maps, keyword lists, binaries, strings
- Functions: def/defp, multi-clause with pattern matching, guards (when)
- Pipe operator: |> chains function calls left to right
- Modules: defmodule, @moduledoc, @doc, @spec for typespecs
- Protocols: polymorphism, defprotocol/defimpl (like interfaces)
- Behaviours: callback contracts (@callback, @impl)
- Structs: defstruct, %Module{}, enforce_keys
- Comprehensions: for x <- list, filter, do: body, into: target
- Sigils: ~r (regex), ~w (word list), ~s (string), custom sigils
- Metaprogramming: macros (defmacro), quote/unquote, AST manipulation
- With expression: with for chaining pattern matches with early exit

## Concurrency and OTP
- Processes: spawn, send/receive, lightweight (millions possible)
- GenServer: init, handle_call (sync), handle_cast (async), handle_info
- Supervisor: one_for_one, one_for_all, rest_for_one strategies
- Supervision trees: fault tolerance through process isolation
- Agent: simple state wrapper around GenServer
- Task: async/await for one-off concurrent work
- Registry: process name registration and lookup
- ETS: in-memory key-value store, concurrent reads
- GenStage: producer/consumer pipeline with backpressure
- Phoenix.PubSub: distributed pub/sub messaging

## Phoenix Framework
- MVC: controllers, views, templates (HEEx)
- Router: scope, pipe_through (pipelines), resources
- Ecto: schemas, changesets, migrations, Repo, queries
- Ecto.Query: from, where, select, join, preload, fragment
- Changesets: validation (validate_required, validate_format), casting
- LiveView: real-time server-rendered UI, handle_event, assigns
- LiveView: mount, handle_event, handle_info, phx-click, phx-submit
- Channels: WebSocket real-time communication, topic/event model
- Context modules: bounded contexts grouping related business logic
- Authentication: phx.gen.auth, session-based, token-based

## Testing
- ExUnit: describe/test, setup, assert/refute, async: true
- Doctests: examples in @doc that run as tests
- Mox: behavior-based mocking, define expectations
- Wallaby: browser-based integration testing
- Property-based: StreamData, property testing

## Mix and Hex
- Mix: build tool, mix new, mix deps.get, mix test, mix format
- Hex: package manager, hex.pm registry
- Releases: mix release for production deployments
- Configuration: config.exs, runtime.exs for runtime config
- Umbrella projects: multiple apps in one repository

## Best Practices
- Let it crash: don't over-handle errors, let supervisors restart
- Use pattern matching everywhere — clear, explicit code
- Pipe chains for data transformation
- Small focused functions, descriptive names
- Use typespecs (@spec) for documentation and dialyzer
- Supervision trees for fault isolation
- Context modules for clean architecture boundaries
