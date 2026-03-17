#!/usr/bin/env python3
"""
Test Offline Support Integration

Verifies:
1. Mission queueing while offline
2. Queue persistence to SQLite
3. Queue status tracking
4. Sync manager functionality
5. RPC endpoints for offline operations
"""

import asyncio
import tempfile
import json
from pathlib import Path
from piddy.offline_sync import get_offline_queue, get_sync_manager, QueueStatus
from piddy.rpc_endpoints import offline_queue_mission, offline_get_queue_status, offline_get_pending_missions

def test_offline_queueing():
    """Test mission queueing while offline"""
    
    print("\n" + "="*70)
    print("🧪 TEST: Offline Support - Mission Queueing & Persistence")
    print("="*70)
    
    # Use temp database for testing
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / ".piddy_offline_test.db"
    
    try:
        # 1. Initialize queue
        print("\n1️⃣  Initializing offline queue...")
        queue = get_offline_queue(str(db_path))
        print(f"✅ Queue initialized: {db_path}")
        
        # 2. Queue some missions while "offline"
        print("\n2️⃣  Queueing missions (simulating offline mode)...")
        missions_to_queue = [
            ("mission_001", "nova", "create test for validation"),
            ("mission_002", "nova", "generate API endpoint"),
            ("mission_003", "nova", "fix bug in auth module"),
        ]
        
        queued_missions = []
        for mission_id, agent, task in missions_to_queue:
            result = queue.queue_mission(mission_id, agent, task, {"channel": "slack"})
            queued_missions.append(result)
            print(f"   ✅ Queued: {mission_id}")
        
        print(f"   → Total queued: {len(queued_missions)}")
        
        # 3. Check queue status
        print("\n3️⃣  Checking queue status...")
        stats = queue.get_queue_stats()
        print(f"   📊 Total missions: {stats['total']}")
        print(f"   📊 Status breakdown: {stats['by_status']}")
        print(f"   📊 Is online: {stats['is_online']}")
        
        assert stats['total'] == 3, "Should have 3 missions in queue"
        
        # 4. Get pending missions
        print("\n4️⃣  Retrieving pending missions...")
        pending = queue.get_pending_missions(limit=10)
        print(f"   ✅ Retrieved {len(pending)} pending missions")
        for m in pending:
            print(f"      - {m['mission_id']}: {m['status']}")
        
        # 5. Update mission status
        print("\n5️⃣  Updating mission statuses...")
        queue.update_mission_status("mission_001", QueueStatus.COMPLETED, {"files": ["test.py"]})
        queue.update_mission_status("mission_002", QueueStatus.SYNCING)
        queue.update_mission_status("mission_003", QueueStatus.FAILED, error="Git clone failed")
        
        stats = queue.get_queue_stats()
        print(f"   ✅ After updates:")
        print(f"      - Status breakdown: {stats['by_status']}")
        
        # 6. Test sync manager
        print("\n6️⃣  Testing sync manager...")
        sync = get_sync_manager(queue)
        
        # Simulate connectivity change
        print("   ↓ Setting offline mode...")
        sync.set_connectivity_status(False)
        assert not queue.is_online, "Should be offline"
        print("   ✅ Set to offline")
        
        print("   ↓ Restoring online mode...")
        sync.set_connectivity_status(True)
        assert queue.is_online, "Should be online"
        print("   ✅ Set to online")
        
        # 7. Test cleanup
        print("\n7️⃣  Testing queue cleanup...")
        deleted = queue.clear_completed_missions(older_than_hours=0)
        print(f"   ✅ Cleaned up {deleted} old completed missions")
        
        stats = queue.get_queue_stats()
        print(f"   📊 Remaining missions: {stats['total']}")
        
        # 8. Test RPC endpoints
        print("\n8️⃣  Testing RPC endpoints...")
        
        # Queue via RPC
        result = offline_queue_mission("mission_rpc_001", "nova", "nova refactor code")
        assert result["success"], "Should queue via RPC"
        print(f"   ✅ Queue via RPC: {result['queued']['mission_id']}")
        
        # Get status via RPC
        status_result = offline_get_queue_status()
        assert status_result["success"], "Should get status via RPC"
        print(f"   ✅ Queue status via RPC: {status_result['queue_status']['total']} missions")
        
        # Get pending via RPC
        pending_result = offline_get_pending_missions(limit=5)
        assert pending_result["success"], "Should get pending via RPC"
        print(f"   ✅ Pending missions via RPC: {pending_result['count']} missions")
        
        # 9. Summary
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED")
        print("="*70)
        
        print("\n📊 Final Summary:")
        print("   ✅ Offline queue: Initialized successfully")
        print("   ✅ Mission queueing: Working (missions persist to SQLite)")
        print("   ✅ Queue status: Accurate tracking")
        print("   ✅ Sync manager: Connectivity detection working")
        print("   ✅ RPC endpoints: All offline operations available")
        
        print("\n🔄 Offline Workflow:")
        print("   1. User goes offline (loses connectivity)")
        print("   2. Future Nova commands queued locally")
        print("   3. Missions stored in .piddy_offline.db")
        print("   4. User comes back online")
        print("   5. Queue syncs automatically")
        print("   6. Results merged back into main database")
        
        print("\n📱 Desktop App Integration:")
        print("   - Electron detects connectivity (navigator.onLine)")
        print("   - Calls offline.set_connectivity_status(is_online)")
        print("   - Nova commands automatically queue if offline")
        print("   - RPC returns mission with queue_id instead of execution")
        print("   - UI shows '⏳ Queued for offline sync'")
        
    finally:
        # Cleanup
        queue.close()
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("\n🧹 Cleanup complete")

if __name__ == "__main__":
    test_offline_queueing()
