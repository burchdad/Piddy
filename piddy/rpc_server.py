"""
Piddy RPC Server - Direct Python function execution over stdio
Replaces HTTP with lightweight message-based protocol
"""

import json
import sys
import traceback
import logging
from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
import asyncio
import inspect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[RPC] %(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Log to stderr to avoid polluting stdout (which carries RPC protocol)
)
logger = logging.getLogger(__name__)


class MessageType(Enum):
    """RPC message types"""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    STREAM_START = "stream_start"
    STREAM_CHUNK = "stream_chunk"
    STREAM_ERROR = "stream_error"
    STREAM_END = "stream_end"
    PING = "ping"
    PONG = "pong"


@dataclass
class RPCMessage:
    """RPC message structure"""
    type: str
    id: int
    function: Optional[str] = None
    args: Optional[list] = None
    kwargs: Optional[dict] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    error_traceback: Optional[str] = None
    sequence: Optional[int] = None  # For streams
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> "RPCMessage":
        """Deserialize from JSON"""
        data = json.loads(json_str)
        return cls(**data)


class RPCServer:
    """
    RPC Server that communicates over stdin/stdout
    Replaces HTTP with direct function calls
    """
    
    def __init__(self):
        self.functions: Dict[str, Callable] = {}
        self.stream_functions: Dict[str, Callable] = {}
        self.request_id = 0
        self.lock = threading.Lock()
        self.running = True
        
        logger.info("RPC Server initialized")
        
        # Register built-in health check
        self.register("__ping__", self._ping)
    
    def register(self, name: str, func: Callable):
        """Register a function to be called via RPC"""
        self.functions[name] = func
        logger.info(f"Registered function: {name}")
    
    def register_stream(self, name: str, func: Callable):
        """Register a streaming function"""
        self.stream_functions[name] = func
        logger.info(f"Registered stream function: {name}")
    
    def _ping(self) -> dict:
        """Health check function"""
        return {"status": "pong", "timestamp": time.time()}
    
    def _send_message(self, message: RPCMessage):
        """Send message to client"""
        try:
            json_str = message.to_json()
            sys.stdout.write(json_str + '\n')
            sys.stdout.flush()
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    def _send_error(self, request_id: int, error_msg: str, tb: str = ""):
        """Send error response"""
        msg = RPCMessage(
            type=MessageType.ERROR.value,
            id=request_id,
            error=error_msg,
            error_traceback=tb
        )
        self._send_message(msg)
    
    def _handle_request(self, message: RPCMessage):
        """Handle RPC request"""
        try:
            func_name = message.function
            
            if not func_name:
                self._send_error(message.id, "No function specified")
                return
            
            # Check if it's a stream request
            if func_name in self.stream_functions:
                self._handle_stream(message)
                return
            
            # Regular function call
            if func_name not in self.functions:
                self._send_error(message.id, f"Function not found: {func_name}")
                return
            
            func = self.functions[func_name]
            args = message.args or []
            kwargs = message.kwargs or {}
            
            logger.debug(f"Calling {func_name}({args}, {kwargs})")
            
            # Check if function is async
            if asyncio.iscoroutinefunction(func):
                try:
                    # Get or create event loop
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If loop is already running, create a new one in a thread
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(asyncio.run, func(*args, **kwargs))
                                result = future.result(timeout=30)
                        else:
                            result = loop.run_until_complete(func(*args, **kwargs))
                    except RuntimeError:
                        # No event loop, create new one
                        result = asyncio.run(func(*args, **kwargs))
                except Exception as e:
                    error_msg = str(e)
                    tb = traceback.format_exc()
                    logger.error(f"Error calling async {func_name}: {error_msg}\n{tb}")
                    self._send_error(message.id, error_msg, tb)
                    return
            else:
                # Synchronous function
                result = func(*args, **kwargs)
            
            response = RPCMessage(
                type=MessageType.RESPONSE.value,
                id=message.id,
                result=result
            )
            self._send_message(response)
            
        except Exception as e:
            error_msg = str(e)
            tb = traceback.format_exc()
            logger.error(f"Error calling {message.function}: {error_msg}\n{tb}")
            self._send_error(message.id, error_msg, tb)
    
    def _handle_stream(self, message: RPCMessage):
        """Handle streaming function call"""
        try:
            func_name = message.function
            func = self.stream_functions[func_name]
            args = message.args or []
            kwargs = message.kwargs or {}
            
            logger.debug(f"Starting stream {func_name}")
            
            # Send stream start
            start_msg = RPCMessage(
                type=MessageType.STREAM_START.value,
                id=message.id
            )
            self._send_message(start_msg)
            
            # Call generator function and stream results
            sequence = 0
            try:
                for chunk in func(*args, **kwargs):
                    chunk_msg = RPCMessage(
                        type=MessageType.STREAM_CHUNK.value,
                        id=message.id,
                        result=chunk,
                        sequence=sequence
                    )
                    self._send_message(chunk_msg)
                    sequence += 1
            except GeneratorExit:
                pass
            
            # Send stream end
            end_msg = RPCMessage(
                type=MessageType.STREAM_END.value,
                id=message.id,
                sequence=sequence
            )
            self._send_message(end_msg)
            
        except Exception as e:
            error_msg = str(e)
            tb = traceback.format_exc()
            logger.error(f"Stream error in {message.function}: {error_msg}\n{tb}")
            error_msg_obj = RPCMessage(
                type=MessageType.STREAM_ERROR.value,
                id=message.id,
                error=error_msg,
                error_traceback=tb
            )
            self._send_message(error_msg_obj)
    
    def listen(self):
        """Listen for RPC requests on stdin and respond on stdout"""
        logger.info("RPC Server listening on stdin")
        
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    message = RPCMessage.from_json(line)
                    
                    if message.type == MessageType.PING.value:
                        pong = RPCMessage(
                            type=MessageType.PONG.value,
                            id=message.id
                        )
                        self._send_message(pong)
                    elif message.type == MessageType.REQUEST.value:
                        self._handle_request(message)
                    else:
                        logger.warning(f"Unknown message type: {message.type}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                except Exception as e:
                    logger.error(f"Message processing error: {e}\n{traceback.format_exc()}")
        
        except KeyboardInterrupt:
            logger.info("RPC Server shutting down")
        except Exception as e:
            logger.error(f"Fatal error in RPC server: {e}\n{traceback.format_exc()}")
        finally:
            self.running = False


# Singleton instance
_rpc_server: Optional[RPCServer] = None


def get_rpc_server() -> RPCServer:
    """Get or create RPC server instance"""
    global _rpc_server
    if _rpc_server is None:
        _rpc_server = RPCServer()
    return _rpc_server


def register_function(name: str, func: Callable):
    """Register a function for RPC"""
    get_rpc_server().register(name, func)


def register_stream(name: str, func: Callable):
    """Register a streaming function for RPC"""
    get_rpc_server().register_stream(name, func)


def start_rpc_server():
    """Start listening for RPC requests"""
    get_rpc_server().listen()


def register_default_endpoints():
    """Register all default API endpoints for RPC"""
    try:
        from piddy.rpc_endpoints import RPC_ENDPOINTS
        server = get_rpc_server()
        
        for name, func in RPC_ENDPOINTS.items():
            server.register(name, func)
        
        logger.info(f"✅ Registered {len(RPC_ENDPOINTS)} API endpoints for RPC")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import RPC endpoints: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to register endpoints: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    server = get_rpc_server()
    
    # Register example functions
    def add(a, b):
        return {"result": a + b}
    
    def echo(message):
        return {"echo": message}
    
    def count_to_n(n):
        """Example streaming function"""
        for i in range(n):
            yield {"count": i + 1}
    
    server.register("add", add)
    server.register("echo", echo)
    server.register_stream("count_to_n", count_to_n)
    
    # Start server
    server.listen()
