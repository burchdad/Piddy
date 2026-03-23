# Scala Quick Reference

## Language: Scala 3.4+
**Paradigm:** OOP + functional, concurrent  
**Typing:** Static, strong, inferred  
**Runtime:** JVM (also Scala.js, Scala Native)  

## Syntax Essentials

```scala
val name = "Piddy"          // immutable (preferred)
var count = 0                // mutable

// String interpolation
s"Hello $name, count=$count"

def add(a: Int, b: Int): Int = a + b

// Extension methods
extension (s: String)
  def greet: String = s"Hello $s"
```

## Algebraic Data Types

```scala
enum Shape:
  case Circle(radius: Double)
  case Rectangle(w: Double, h: Double)

def area(s: Shape): Double = s match
  case Shape.Circle(r)        => Math.PI * r * r
  case Shape.Rectangle(w, h)  => w * h

case class User(name: String, age: Int)
val u2 = user.copy(age = 2)
```

## Collections & For-Comprehensions

```scala
list.map(_ * 2)
list.filter(_ > 1)
list.foldLeft(0)(_ + _)
list.groupBy(_ % 2)

// For-comprehension
for
  user <- users
  if user.active
  order <- user.orders
yield order.total
```

## Effect Handling

```scala
// Option
val opt: Option[Int] = Some(42)
opt.map(_ * 2).getOrElse(0)

// Either
def parse(s: String): Either[String, Int] =
  s.toIntOption.toRight(s"Invalid: $s")

// Try
Try(riskyOp()) match
  case Success(v) => use(v)
  case Failure(e) => handle(e)
```

## Tooling

```bash
sbt compile
sbt test
sbt run
scala-cli run script.sc
```
