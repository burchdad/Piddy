#!/usr/bin/env python3
"""
Quick test of RPC system initialization
"""

import sys
import os

# Add workspace to path
sys.path.insert(0, '/workspaces/Piddy')
os.chdir('/workspaces/Piddy')

print("=" * 80)
print("Testing RPC System Initialization")
print("=" * 80)

# Test 1: Import RPC Server
print("\n1. Testing RPC Server import...")
try:
    from piddy.rpc_server import get_rpc_server, register_default_endpoints, start_rpc_server
    print("   ✅ RPC Server imports successful")
except Exception as e:
    print(f"   ❌ Failed to import RPC Server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Get RPC Server instance
print("\n2. Testing RPC Server instantiation...")
try:
    server = get_rpc_server()
    print(f"   ✅ RPC Server instantiated: {server}")
except Exception as e:
    print(f"   ❌ Failed to instantiate RPC Server: {e}")
    sys.exit(1)

# Test 3: Register endpoints
print("\n3. Testing endpoint registration...")
try:
    success = register_default_endpoints()
    if success:
        print(f"   ✅ Endpoints registered successfully")
        print(f"   ✅ Total registered functions: {len(server.functions)}")
        print(f"   ✅ Registered endpoints:")
        for name in sorted(server.functions.keys()):
            print(f"      - {name}")
    else:
        print(f"   ⚠️  Endpoint registration returned False (some imports may have failed)")
        print(f"   ℹ️  Registered functions: {len(server.functions)}")
        if server.functions:
            for name in sorted(server.functions.keys()):
                print(f"      - {name}")
except Exception as e:
    print(f"   ❌ Failed to register endpoints: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test a simple endpoint call
print("\n4. Testing endpoint function calls...")
try:
    from piddy.rpc_endpoints import system_health, system_overview
    
    health = system_health()
    print(f"   ✅ system_health(): {health}")
    
    overview = system_overview()
    print(f"   ✅ system_overview() status: {overview.get('status')}")
except Exception as e:
    print(f"   ❌ Failed to call endpoints: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ All RPC initialization tests passed!")
print("=" * 80)
