# Ruby Quick Reference

## Language: Ruby 3.3+
**Paradigm:** OOP (everything is an object), functional elements  
**Typing:** Dynamic, strong, duck typing  
**Runtime:** CRuby (MRI), JRuby, TruffleRuby  

## Syntax Essentials

```ruby
name = "Piddy"
config = { host: "localhost", port: 8889 }
nums = [1, 2, 3, 4, 5]

# Symbols, string interpolation
puts "Hello #{name}"
status = :active

# Blocks
[1, 2, 3].each { |n| puts n }

# Lambda (strict arity)
greet = ->(name) { "Hello #{name}" }

# Yield
def with_logging
  puts "start"
  result = yield
  puts "end"
  result
end
```

## Enumerable

```ruby
nums.map { |n| n * 2 }
nums.select { |n| n.even? }
nums.reduce(0) { |sum, n| sum + n }
nums.group_by { |n| n.even? ? :even : :odd }
nums.flat_map { |n| [n, n*2] }
nums.tally
```

## Classes & Modules

```ruby
class Animal
  attr_reader :name
  attr_accessor :age

  def initialize(name, age = 0)
    @name = name
    @age = age
  end
end

class Dog < Animal
  def speak
    "#{name} says Woof!"
  end
end

module Cacheable
  def cache_key
    "#{self.class.name}:#{id}"
  end
end

# Data class (Ruby 3.2+, immutable)
Person = Data.define(:name, :age)
```

## Pattern Matching (3.0+)

```ruby
case response
in { status: 200, body: String => body }
  process(body)
in { status: 404 }
  not_found
in { status: (500..) }
  server_error
end
```

## Tooling

```bash
gem install bundler
bundle init
bundle install
rspec spec/
rubocop
```
