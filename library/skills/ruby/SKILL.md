---
name: ruby
description: Ruby programming with Rails framework, gems, testing with RSpec, and modern Ruby patterns
---

# Ruby Development

## Core Language
- Dynamic typing, everything is an object (even integers, nil, true/false)
- Variables: local, @instance, @@class, $global, CONSTANT
- Strings: single-quoted (literal), double-quoted (interpolation "Hello #{name}")
- Symbols: :name — immutable, intern pooled, used as hash keys and identifiers
- Arrays: [], push/pop/shift/unshift, map/select/reject/reduce/flat_map
- Hashes: {key: value}, fetch with default, transform_keys/transform_values
- Blocks, Procs, and Lambdas: yield, &block, Proc.new, ->(x) { x + 1 }
- Methods: def, default arguments, keyword arguments, splat (*args, **kwargs)
- Classes: initialize, attr_accessor/reader/writer, inheritance (<)
- Modules: mixins via include/extend/prepend, namespacing
- Enumerable module: each, map, select, inject, group_by, lazy enumerators
- Pattern matching (Ruby 3+): case/in, find pattern, pin operator (^)
- Ractors (Ruby 3+): actor-based concurrency model
- Fibers: lightweight cooperative concurrency

## Ruby on Rails
- MVC architecture: models, views, controllers
- Convention over configuration: naming conventions drive behavior
- Generators: rails generate model/controller/scaffold/migration
- Routing: resources, nested resources, constraints, namespace
- ActiveRecord: associations (has_many, belongs_to, has_many :through), scopes, validations, callbacks
- Migrations: create_table, add_column, add_index, change_column
- Query interface: where, order, joins, includes (eager loading), pluck, find_each
- Action Controller: before_action, strong_parameters (params.require.permit)
- Views: ERB/Haml templates, partials, layouts, helpers
- Active Job: background processing with Sidekiq/Resque/GoodJob
- Action Cable: WebSocket integration
- Turbo + Stimulus (Hotwire): modern Rails frontend approach
- API mode: rails new --api, serializers, JSONAPI

## Testing
- RSpec: describe/context/it blocks, let/let!, before/after hooks
- Matchers: eq, be, include, raise_error, change, have_attributes
- Mocking: double, allow/expect, receive, with, and_return
- FactoryBot: factories, traits, sequences, associations
- Capybara: integration/system tests, visit, fill_in, click_button
- VCR: record and replay HTTP interactions
- SimpleCov for code coverage
- Rails-specific: request specs, model specs, system specs

## Gems and Bundler
- Gemfile: source, gem, group, platforms
- bundle install, bundle update, bundle exec
- Key gems: devise (auth), pundit/cancancan (authorization), sidekiq (jobs), puma (server), pg (postgres), redis, rack-cors
- Creating gems: bundle gem name, gemspec

## Best Practices
- Follow Ruby style guide (rubocop)
- Duck typing: respond_to? over is_a? checks
- Prefer composition with modules over deep inheritance
- Use frozen_string_literal: true pragma
- N+1 query prevention: use includes/preload/eager_load
- Keep controllers thin, models focused, extract service objects
- Use keyword arguments for methods with multiple parameters
