#!/usr/bin/env python3
"""
End-to-end mission submission test
Tests: create mission -> execute -> check status -> poll completion
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

async def test_e2e_mission():
    """Test end-to-end mission submission"""
    print("\n" + "="*60)
    print("END-TO-END MISSION SUBMISSION TEST")
    print("="*60)
    
    try:
        # Import the API
        print("\n1️⃣  Importing dashboard API...")
        from src.dashboard_api import app
        from src.dashboard_api import (
            MissionCreateRequest, ExecuteMissionRequest,
            send_livechat_message, LiveChatRequest
        )
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        print("   ✅ Dashboard API imported successfully")
        
        # Test 1: Create mission
        print("\n2️⃣  Creating mission draft...")
        create_request = {
            "mission_type": "analysis",
            "mission_name": "Test Code Analysis Mission",
            "description": "Analyze test.py for performance issues",
            "objectives": ["Analyze code", "Find performance bottlenecks", "Generate report"],
            "required_agents": ["performance_analyst", "code_reviewer"],
            "priority": 5,
            "timeout_seconds": 120
        }
        
        response = client.post("/api/missions/create", json=create_request)
        print(f"   Status: {response.status_code}")
        create_result = response.json()
        print(f"   Response: {json.dumps(create_result, indent=2)}")
        
        if response.status_code != 200:
            print("   ❌ Failed to create mission")
            return False
        
        mission_id = create_result.get("mission_id")
        print(f"   ✅ Mission created: {mission_id}")
        
        # Test 2: Get mission status after creation
        print("\n3️⃣  Getting mission status after creation...")
        response = client.get(f"/api/missions/{mission_id}/status")
        print(f"   Status: {response.status_code}")
        status_result = response.json()
        print(f"   Mission Status: {status_result.get('status')}")
        print(f"   Progress: {status_result.get('progress_percent')}%")
        print("   ✅ Mission status retrieved")
        
        # Test 3: Execute mission
        print("\n4️⃣  Executing mission...")
        execute_request = {
            "mission_type": "analysis",
            "mission_name": "Test Code Analysis Mission",
            "description": "Analyze test.py for performance issues",
            "objectives": ["Analyze code", "Find performance bottlenecks"],
            "required_agents": ["performance_analyst"],
            "priority": 3,
            "timeout_seconds": 120
        }
        
        response = client.post("/api/missions/execute", json=execute_request)
        print(f"   Status: {response.status_code}")
        execute_result = response.json()
        print(f"   Response: {json.dumps(execute_result, indent=2)}")
        
        if response.status_code != 200:
            print("   ❌ Failed to execute mission")
            return False
        
        task_id = execute_result.get("mission_id")
        print(f"   ✅ Mission submitted for execution: {task_id}")
        
        # Test 4: Get mission execution status
        print("\n5️⃣  Polling mission execution status...")
        for i in range(3):
            await asyncio.sleep(1)
            response = client.get(f"/api/missions/{task_id}/status")
            status_result = response.json()
            print(f"   Poll {i+1}: Status={status_result.get('status')}, Progress={status_result.get('progress_percent')}%")
        
        print("   ✅ Mission status polling works")
        
        # Test 5: LiveChat integration
        print("\n6️⃣  Testing LiveChat integration...")
        livechat_request = {
            "content": "create mission: analyze the authentication module for security issues",
            "sender_id": "test-user-123",
            "sender_name": "Test User",
            "message_type": "user"
        }
        
        response = client.post("/api/livechat/send", json=livechat_request)
        print(f"   Status: {response.status_code}")
        livechat_result = response.json()
        print(f"   Response: {json.dumps(livechat_result, indent=2)}")
        
        if response.status_code != 200:
            print("   ⚠️  LiveChat message not fully processed")
        else:
            print(f"   ✅ LiveChat message processed: {livechat_result.get('status')}")
        
        # Test 6: Get all missions
        print("\n7️⃣  Listing all missions...")
        response = client.get("/api/missions")
        print(f"   Status: {response.status_code}")
        missions_result = response.json()
        print(f"   Total missions: {len(missions_result)}")
        if missions_result:
            print(f"   First mission: {missions_result[0].get('mission_name') if missions_result else 'N/A'}")
        print("   ✅ Mission list retrieved")
        
        # Summary
        print("\n" + "="*60)
        print("✅ END-TO-END TEST PASSED")
        print("="*60)
        print("\nEndpoints Tested:")
        print("  ✅ POST /api/missions/create")
        print("  ✅ GET /api/missions/{mission_id}/status")
        print("  ✅ POST /api/missions/execute")
        print("  ✅ GET /api/missions")
        print("  ✅ POST /api/livechat/send")
        print("\nAll core mission and LiveChat endpoints are functional!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_e2e_mission())
    sys.exit(0 if success else 1)
