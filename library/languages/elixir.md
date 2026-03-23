# Elixir Quick Reference

## Language: Elixir 1.16+ / Erlang/OTP 26+
**Paradigm:** Functional, concurrent, distributed  
**Typing:** Dynamic, strong  
**Runtime:** BEAM VM (Erlang VM) — fault-tolerant, hot code swapping  

## Syntax Essentials

```elixir
# Pattern matching (= is match, not assignment)
{:ok, result} = {:ok, 42}
[head | tail] = [1, 2, 3]
%{name: name} = user

# Functions
defmodule Math do
  def add(a, b), do: a + b
  def factorial(0), do: 1
  def factorial(n) when n > 0, do: n * factorial(n - 1)
end

# Pipe operator
"  Hello World  "
|> String.trim()
|> String.downcase()
|> String.split()
|> Enum.join(" ")
```

## Control Flow

```elixir
# Case
case HTTP.get(url) do
  {:ok, %{status: 200, body: body}} -> parse(body)
  {:ok, %{status: 404}} -> :not_found
  {:error, reason} -> {:error, reason}
end

# With (happy path chaining)
with {:ok, user} <- find_user(id),
     {:ok, account} <- find_account(user),
     {:ok, balance} <- get_balance(account) do
  {:ok, balance}
end
```

## Processes & OTP

```elixir
# GenServer
defmodule Counter do
  use GenServer

  def start_link(initial \\ 0) do
    GenServer.start_link(__MODULE__, initial, name: __MODULE__)
  end

  def increment, do: GenServer.call(__MODULE__, :increment)

  @impl true
  def init(count), do: {:ok, count}

  @impl true
  def handle_call(:increment, _from, count), do: {:reply, count + 1, count + 1}
end

# Task (async)
task = Task.async(fn -> expensive_work() end)
result = Task.await(task)
```

## Tooling

```bash
mix new project_name
mix deps.get
mix compile
mix test
mix format
iex -S mix
```
