# Dart Quick Reference

## Language: Dart 3.3+ / Flutter 3.x
**Paradigm:** OOP, functional elements  
**Typing:** Static, strong, sound null safety  
**Targets:** Mobile (iOS/Android), Web, Desktop via Flutter; Server  

## Syntax Essentials

```dart
var name = 'Piddy';
final port = 8889;           // runtime constant
const pi = 3.14159;          // compile-time constant
String? email;               // nullable

// Collection if/for
var filtered = [
  for (var item in items)
    if (item.isActive) item.name,
];

// Cascade
var button = Button()
  ..text = 'Click'
  ..color = Colors.blue
  ..onPressed = handleClick;
```

## Sealed Classes & Pattern Matching (Dart 3)

```dart
sealed class Shape {}
class Circle extends Shape { final double radius; Circle(this.radius); }
class Rectangle extends Shape { final double w, h; Rectangle(this.w, this.h); }

double area(Shape shape) => switch (shape) {
  Circle(radius: var r)     => 3.14159 * r * r,
  Rectangle(w: var w, h: var h) => w * h,
};

// Records
(String, int) userInfo = ('Piddy', 1);
var (name, age) = userInfo;
```

## Async

```dart
Future<User> fetchUser(int id) async {
  final response = await http.get(Uri.parse('/api/users/$id'));
  if (response.statusCode != 200) throw HttpException('Failed');
  return User.fromJson(jsonDecode(response.body));
}

// Streams
Stream<int> countDown(int from) async* {
  for (var i = from; i >= 0; i--) {
    await Future.delayed(Duration(seconds: 1));
    yield i;
  }
}
```

## Tooling

```bash
dart create project_name
dart run
dart test
dart compile exe bin/main.dart
flutter create app_name
flutter run
flutter build apk / ios / web
```
