"""Backend design patterns and architecture templates."""

from typing import Dict, List, Any
from enum import Enum


class ArchitecturePattern(str, Enum):
    """Common backend architecture patterns."""
    MONOLITH = "monolith"
    MICROSERVICES = "microservices"
    SERVERLESS = "serverless"
    EVENT_DRIVEN = "event_driven"
    LAYERED = "layered"
    HEXAGONAL = "hexagonal"
    CQRS = "cqrs"


class DesignPattern(str, Enum):
    """Common design patterns for backend development."""
    SINGLETON = "singleton"
    FACTORY = "factory"
    STRATEGY = "strategy"
    OBSERVER = "observer"
    DECORATOR = "decorator"
    ADAPTER = "adapter"
    BUILDER = "builder"
    CHAIN_OF_RESPONSIBILITY = "chain_of_responsibility"
    COMMAND = "command"
    REPOSITORY = "repository"
    DEPENDENCY_INJECTION = "dependency_injection"
    MIDDLEWARE = "middleware"


def get_design_pattern(pattern: DesignPattern, language: str = "python") -> Dict[str, str]:
    """Get code template for a design pattern."""
    
    patterns = {
        DesignPattern.SINGLETON: _singleton_pattern,
        DesignPattern.FACTORY: _factory_pattern,
        DesignPattern.STRATEGY: _strategy_pattern,
        DesignPattern.OBSERVER: _observer_pattern,
        DesignPattern.DECORATOR: _decorator_pattern,
        DesignPattern.ADAPTER: _adapter_pattern,
        DesignPattern.BUILDER: _builder_pattern,
        DesignPattern.REPOSITORY: _repository_pattern,
        DesignPattern.DEPENDENCY_INJECTION: _dependency_injection_pattern,
        DesignPattern.MIDDLEWARE: _middleware_pattern,
    }
    
    template = patterns.get(pattern, lambda l: {})
    return template(language)


def _singleton_pattern(language: str) -> Dict[str, str]:
    """Singleton pattern implementation."""
    
    if language == "python":
        return {
            "name": "Singleton Pattern",
            "description": "Ensure a class has only one instance and provide global access",
            "code": '''class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

# Usage
instance1 = Singleton()
instance2 = Singleton()
assert instance1 is instance2  # Same instance
''',
            "use_cases": ["Database connections", "Configuration managers", "Logger instances"]
        }
    
    elif language == "javascript":
        return {
            "name": "Singleton Pattern",
            "code": '''class Singleton {
    static instance;
    
    private constructor() {}
    
    static getInstance() {
        if (!Singleton.instance) {
            Singleton.instance = new Singleton();
        }
        return Singleton.instance;
    }
}

// Usage
const instance1 = Singleton.getInstance();
const instance2 = Singleton.getInstance();
console.assert(instance1 === instance2);  // Same instance
''',
            "use_cases": ["Database connections", "Configuration managers", "Logger instances"]
        }
    
    return {"error": "Language not supported"}


def _factory_pattern(language: str) -> Dict[str, str]:
    """Factory pattern implementation."""
    
    if language == "python":
        return {
            "name": "Factory Pattern",
            "description": "Create objects without specifying exact classes",
            "code": '''from enum import Enum

class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"

class DatabaseFactory:
    @staticmethod
    def create_database(db_type: DatabaseType):
        if db_type == DatabaseType.POSTGRESQL:
            return PostgreSQLDatabase()
        elif db_type == DatabaseType.MONGODB:
            return MongoDBDatabase()
        elif db_type == DatabaseType.REDIS:
            return RedisDatabase()
        else:
            raise ValueError(f"Unknown database type: {db_type}")

class PostgreSQLDatabase:
    def connect(self): pass

class MongoDBDatabase:
    def connect(self): pass

class RedisDatabase:
    def connect(self): pass

# Usage
db = DatabaseFactory.create_database(DatabaseType.POSTGRESQL)
db.connect()
''',
            "use_cases": ["Database creation", "Payment processors", "Notification services"]
        }
    
    return {"error": "Language not supported"}


def _strategy_pattern(language: str) -> Dict[str, str]:
    """Strategy pattern implementation."""
    
    if language == "python":
        return {
            "name": "Strategy Pattern",
            "code": '''from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float) -> bool:
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self, amount: float) -> bool:
        print(f"Processing ${amount} via Credit Card")
        return True

class PayPalPayment(PaymentStrategy):
    def pay(self, amount: float) -> bool:
        print(f"Processing ${amount} via PayPal")
        return True

class CryptoPayment(PaymentStrategy):
    def pay(self, amount: float) -> bool:
        print(f"Processing ${amount} via Cryptocurrency")
        return True

class PaymentProcessor:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def process_payment(self, amount: float):
        return self.strategy.pay(amount)

# Usage
processor = PaymentProcessor(CreditCardPayment())
processor.process_payment(100.00)
''',
            "use_cases": ["Payment processing", "Data validation", "Algorithm selection"]
        }
    
    return {"error": "Language not supported"}


def _observer_pattern(language: str) -> Dict[str, str]:
    """Observer pattern implementation."""
    
    if language == "python":
        return {
            "name": "Observer Pattern",
            "code": '''from abc import ABC, abstractmethod
from typing import List

class Observer(ABC):
    @abstractmethod
    def update(self, subject: "Subject") -> None:
        pass

class Subject:
    def __init__(self):
        self._observers: List[Observer] = []
        self._state = None
    
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
    
    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        self._state = value
        self.notify()

class ConcreteObserver(Observer):
    def update(self, subject: Subject) -> None:
        print(f"Observer: State changed to {subject.state}")

# Usage
subject = Subject()
observer = ConcreteObserver()
subject.attach(observer)
subject.state = "New State"
''',
            "use_cases": ["Event systems", "User notifications", "Real-time updates"]
        }
    
    return {"error": "Language not supported"}


def _decorator_pattern(language: str) -> Dict[str, str]:
    """Decorator pattern implementation."""
    
    if language == "python":
        return {
            "name": "Decorator Pattern",
            "code": '''from functools import wraps
import time
import logging

def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

def logging_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"Finished {func.__name__}")
        return result
    return wrapper

@timing_decorator
@logging_decorator
def data_processing():
    time.sleep(1)
    return "Done"

# Usage
result = data_processing()
''',
            "use_cases": ["Authentication", "Caching", "Logging", "Performance monitoring"]
        }
    
    return {"error": "Language not supported"}


def _adapter_pattern(language: str) -> Dict[str, str]:
    """Adapter pattern implementation."""
    
    if language == "python":
        return {
            "name": "Adapter Pattern",
            "code": '''from abc import ABC, abstractmethod

class Target(ABC):
    @abstractmethod
    def request(self) -> str:
        pass

class Adaptee:
    def specific_request(self) -> str:
        return "Specific request"

class Adapter(Target):
    def __init__(self, adaptee: Adaptee):
        self.adaptee = adaptee
    
    def request(self) -> str:
        return self.adaptee.specific_request()

# Usage
adaptee = Adaptee()
adapter = Adapter(adaptee)
print(adapter.request())
''',
            "use_cases": ["Third-party integrations", "Legacy system integration"]
        }
    
    return {"error": "Language not supported"}


def _builder_pattern(language: str) -> Dict[str, str]:
    """Builder pattern implementation."""
    
    if language == "python":
        return {
            "name": "Builder Pattern",
            "code": '''class DatabaseConfig:
    def __init__(self, builder):
        self.host = builder.host
        self.port = builder.port
        self.username = builder.username
        self.password = builder.password
        self.database = builder.database

class DatabaseConfigBuilder:
    def __init__(self):
        self.host = "localhost"
        self.port = 5432
        self.username = None
        self.password = None
        self.database = None
    
    def set_host(self, host: str):
        self.host = host
        return self
    
    def set_port(self, port: int):
        self.port = port
        return self
    
    def set_username(self, username: str):
        self.username = username
        return self
    
    def set_password(self, password: str):
        self.password = password
        return self
    
    def set_database(self, database: str):
        self.database = database
        return self
    
    def build(self) -> DatabaseConfig:
        return DatabaseConfig(self)

# Usage
config = (DatabaseConfigBuilder()
    .set_host("db.example.com")
    .set_port(5432)
    .set_username("admin")
    .set_password("secret")
    .set_database("myapp")
    .build())
''',
            "use_cases": ["Complex object creation", "Configuration objects"]
        }
    
    return {"error": "Language not supported"}


def _repository_pattern(language: str) -> Dict[str, str]:
    """Repository pattern implementation."""
    
    if language == "python":
        return {
            "name": "Repository Pattern",
            "code": '''from abc import ABC, abstractmethod
from typing import List, Optional

class User:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

class UserRepository(ABC):
    @abstractmethod
    def get(self, id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_all(self) -> List[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> None:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> None:
        pass

class PostgreSQLUserRepository(UserRepository):
    def get(self, id: int) -> Optional[User]:
        # SQL query implementation
        pass
    
    def get_all(self) -> List[User]:
        # SQL query implementation
        pass
    
    def save(self, user: User) -> None:
        # SQL insert/update implementation
        pass
    
    def delete(self, id: int) -> None:
        # SQL delete implementation
        pass

# Usage
repo = PostgreSQLUserRepository()
user = repo.get(1)
''',
            "use_cases": ["Data access layer", "Database abstraction"]
        }
    
    return {"error": "Language not supported"}


def _dependency_injection_pattern(language: str) -> Dict[str, str]:
    """Dependency injection pattern."""
    
    if language == "python":
        return {
            "name": "Dependency Injection Pattern",
            "code": '''from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def query(self, sql: str): pass

class PostgresDB(Database):
    def query(self, sql: str):
        print(f"Executing PostgreSQL: {sql}")

class UserService:
    def __init__(self, db: Database):
        self.db = db
    
    def get_user(self, user_id: int):
        return self.db.query(f"SELECT * FROM users WHERE id = {user_id}")

# Usage
db = PostgresDB()
service = UserService(db)
user = service.get_user(1)
''',
            "use_cases": ["Testability", "Loose coupling", "Configuration flexibility"]
        }
    
    return {"error": "Language not supported"}


def _middleware_pattern(language: str) -> Dict[str, str]:
    """Middleware pattern."""
    
    if language == "python":
        return {
            "name": "Middleware Pattern",
            "code": '''from abc import ABC, abstractmethod
from typing import Callable

class Middleware(ABC):
    def __init__(self, next_middleware: "Middleware" = None):
        self.next_middleware = next_middleware
    
    def execute(self, request: dict) -> dict:
        response = self.process(request)
        if self.next_middleware:
            response = self.next_middleware.execute(response)
        return response
    
    @abstractmethod
    def process(self, request: dict) -> dict:
        pass

class AuthMiddleware(Middleware):
    def process(self, request: dict) -> dict:
        print("Checking authentication...")
        request["authenticated"] = True
        return request

class LoggingMiddleware(Middleware):
    def process(self, request: dict) -> dict:
        print(f"Logging request: {request}")
        return request

# Usage
middleware = AuthMiddleware(LoggingMiddleware())
request = {"endpoint": "/api/users"}
response = middleware.execute(request)
''',
            "use_cases": ["HTTP request processing", "Authentication", "Logging"]
        }
    
    return {"error": "Language not supported"}


def get_architecture_blueprint(architecture: ArchitecturePattern, language: str = "python") -> Dict[str, Any]:
    """Get complete architecture blueprint."""
    
    blueprints = {
        ArchitecturePattern.LAYERED: _layered_architecture,
        ArchitecturePattern.MICROSERVICES: _microservices_architecture,
        ArchitecturePattern.EVENT_DRIVEN: _event_driven_architecture,
        ArchitecturePattern.HEXAGONAL: _hexagonal_architecture,
    }
    
    blueprint_func = blueprints.get(architecture, lambda l: {})
    return blueprint_func(language)


def _layered_architecture(language: str) -> Dict[str, Any]:
    """Layered architecture blueprint."""
    return {
        "name": "Layered Architecture",
        "layers": [
            {
                "name": "Presentation Layer",
                "description": "HTTP endpoints, API routes, request handling"
            },
            {
                "name": "Business Logic Layer",
                "description": "Core business rules, service logic"
            },
            {
                "name": "Persistence Layer",
                "description": "Database access, repositories"
            },
            {
                "name": "Data Layer",
                "description": "Database, caches, external services"
            }
        ],
        "benefits": ["Simple", "Easy to understand", "Good for small to medium projects"],
        "drawbacks": ["Can become monolithic", "Scaling challenges"]
    }


def _microservices_architecture(language: str) -> Dict[str, Any]:
    """Microservices architecture blueprint."""
    return {
        "name": "Microservices Architecture",
        "services": ["User Service", "Order Service", "Payment Service", "Inventory Service"],
        "components": [
            "API Gateway",
            "Service Discovery",
            "Message Queue",
            "Load Balancer",
            "Logging & Monitoring"
        ],
        "benefits": ["Scalability", "Independent deployment", "Technology flexibility"],
        "drawbacks": ["Complexity", "Network latency", "Data consistency challenges"]
    }


def _event_driven_architecture(language: str) -> Dict[str, Any]:
    """Event-driven architecture blueprint."""
    return {
        "name": "Event-Driven Architecture",
        "components": [
            "Event Producers",
            "Message Broker",
            "Event Consumers",
            "Event Store"
        ],
        "benefits": ["Decoupling", "Scalability", "Real-time processing"],
        "drawbacks": ["Complexity", "Eventual consistency", "Debugging challenges"]
    }


def _hexagonal_architecture(language: str) -> Dict[str, Any]:
    """Hexagonal (Ports and Adapters) architecture."""
    return {
        "name": "Hexagonal Architecture",
        "core": "Domain Model & Business Logic",
        "ports": ["HTTP", "Database", "External APIs", "Message Queue"],
        "adapters": ["Web Framework", "ORM", "REST Clients", "Message Adapter"],
        "benefits": ["Framework independence", "Testability", "Flexibility"],
        "drawbacks": ["More complex structure", "Learning curve"]
    }
