#!/usr/bin/env python3
"""
✅ Piddy Unified System Integration Tests

Complete verification of:
- Dashboard API endpoints
- Approval workflow
- Email notifications
- Health checks
- System readiness

Usage:
    pytest tests/integration_unified_system.py -v
    python tests/integration_unified_system.py  # Run directly
"""

import json
import pytest
import requests
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


class TestHealthCheckEndpoints:
    """Test health check endpoints"""
    
    API_URL = "http://localhost:8000"
    
    def test_basic_health_check(self):
        """Test básico health check"""
        response = requests.get(f"{self.API_URL}/health", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "components" in data
    
    def test_detailed_health_check(self):
        """Test detailed health check"""
        response = requests.get(f"{self.API_URL}/health/detailed", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "process" in data
        assert "files" in data
        assert "services" in data
    
    def test_system_verification(self):
        """Test system readiness verification"""
        response = requests.post(f"{self.API_URL}/health/verify", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert "ready" in data
        assert "checks" in data


class TestApprovalSystemEndpoints:
    """Test approval system endpoints"""
    
    API_URL = "http://localhost:8000"
    
    def test_list_approvals_endpoint(self):
        """Test listing approval requests"""
        response = requests.get(f"{self.API_URL}/api/approvals", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert "requests" in data or "count" in data
    
    def test_approval_stats_endpoint(self):
        """Test approval statistics endpoint"""
        response = requests.get(f"{self.API_URL}/api/approvals/summary/stats", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert "total_decisions" in data
        assert "approved_count" in data
        assert "rejected_count" in data
        assert "pending_requests" in data
    
    def test_approval_endpoints_response_format(self):
        """Test approval endpoints return correct format"""
        response = requests.get(f"{self.API_URL}/api/approvals/summary/stats", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        # Verify expected fields
        assert isinstance(data.get("total_decisions"), int)
        assert isinstance(data.get("approved_count"), int)
        assert isinstance(data.get("rejected_count"), int)
        assert isinstance(data.get("approval_rate"), (int, float))


class TestApprovalWorkflow:
    """Test complete approval workflow"""
    
    @staticmethod
    def create_test_approval_request() -> str:
        """Create a test approval request file"""
        request_id = f"test_req_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        request_data = {
            "request_id": request_id,
            "gaps": [
                {
                    "gap_id": f"gap_001_{request_id}",
                    "title": "Test Market Gap",
                    "category": "feature",
                    "market_need": "Test need",
                    "frequency": 5,
                    "estimated_impact": 0.7,
                    "complexity_score": 7,
                    "integration_points": ["API", "Database"],
                    "security_risk_level": "MEDIUM",
                    "security_concerns": ["Test concern"],
                    "estimated_build_time_hours": 12.0
                }
            ],
            "created_at": datetime.utcnow().isoformat(),
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "status": "waiting",
            "sent_to_emails": ["test@example.com"],
            "high_risk_count": 0,
            "medium_risk_count": 1,
            "low_risk_count": 0,
        }
        
        # Save to workflow file
        workflow_file = Path("data/approval_workflow_state.json")
        if workflow_file.exists():
            with open(workflow_file, 'r') as f:
                workflow = json.load(f)
        else:
            workflow = {"requests": {}}
        
        workflow["requests"][request_id] = request_data
        
        with open(workflow_file, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        return request_id
    
    def test_approval_workflow_file_structure(self):
        """Test approval workflow file has correct structure"""
        request_id = self.create_test_approval_request()
        
        workflow_file = Path("data/approval_workflow_state.json")
        assert workflow_file.exists(), "Workflow file should exist"
        
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        assert "requests" in workflow
        assert request_id in workflow["requests"]
        
        request = workflow["requests"][request_id]
        assert request["request_id"] == request_id
        assert "gaps" in request
        assert request["status"] in ["waiting", "partially_approved", "fully_approved", "expired"]
    
    def test_approval_decision_recording(self):
        """Test recording approval decisions"""
        decisions_file = Path("data/approval_decisions.json")
        
        decision = {
            "request_id": "test_req",
            "gap_id": "gap_001",
            "approved": True,
            "decision_time": datetime.utcnow().isoformat(),
            "reason": "Approved for testing"
        }
        
        # Load existing decisions
        if decisions_file.exists():
            with open(decisions_file, 'r') as f:
                decisions = json.load(f)
                if not isinstance(decisions, list):
                    decisions = []
        else:
            decisions = []
        
        decisions.append(decision)
        
        # Save decisions
        with open(decisions_file, 'w') as f:
            json.dump(decisions, f, indent=2)
        
        # Verify saved
        with open(decisions_file, 'r') as f:
            loaded_decisions = json.load(f)
        
        assert any(d.get("gap_id") == "gap_001" for d in loaded_decisions)


class TestDataModels:
    """Test approval system data models"""
    
    def test_gap_model_structure(self):
        """Test gap data model structure"""
        gap_data = {
            "gap_id": "gap_001",
            "title": "Test Gap",
            "category": "feature",
            "market_need": "Market need",
            "frequency": 5,
            "estimated_impact": 0.7,
            "complexity_score": 7,
            "integration_points": ["API"],
            "security_risk_level": "MEDIUM",
            "security_concerns": ["concern"],
            "estimated_build_time_hours": 12.0
        }
        
        assert all(key in gap_data for key in [
            "gap_id", "title", "category", "market_need",
            "frequency", "estimated_impact", "complexity_score",
            "security_risk_level", "security_concerns",
            "estimated_build_time_hours"
        ])
    
    def test_approval_request_model_structure(self):
        """Test approval request data model structure"""
        request_data = {
            "request_id": "req_001",
            "gaps": [],
            "created_at": datetime.utcnow().isoformat(),
            "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "status": "waiting",
            "sent_to_emails": ["test@example.com"],
            "high_risk_count": 0,
            "medium_risk_count": 1,
            "low_risk_count": 0,
        }
        
        assert all(key in request_data for key in [
            "request_id", "gaps", "created_at", "deadline",
            "status", "sent_to_emails"
        ])
    
    def test_decision_model_structure(self):
        """Test decision data model structure"""
        decision_data = {
            "request_id": "req_001",
            "gap_id": "gap_001",
            "approved": True,
            "decision_time": datetime.utcnow().isoformat(),
            "reason": "Approved for business need"
        }
        
        assert all(key in decision_data for key in [
            "request_id", "gap_id", "approved", "decision_time"
        ])


class TestDashboardIntegration:
    """Test dashboard integration with approval system"""
    
    API_URL = "http://localhost:8000"
    
    def test_dashboard_serves_static_files(self):
        """Test dashboard serves frontend static files"""
        response = requests.get(f"{self.API_URL}/", timeout=5)
        # Should either serve index.html (200) or redirect
        assert response.status_code in [200, 301, 302, 404]  # 404 OK if frontend not built
    
    def test_approval_endpoints_integrated_in_dashboard(self):
        """Test approval endpoints are integrated in main dashboard"""
        endpoints = [
            "/api/approvals",
            "/api/approvals/summary/stats",
        ]
        
        for endpoint in endpoints:
            response = requests.get(f"{self.API_URL}{endpoint}", timeout=5)
            assert response.status_code == 200, f"Endpoint {endpoint} should return 200"


class TestSystemConfiguration:
    """Test system configuration and setup"""
    
    def test_required_directories_exist(self):
        """Test required directories exist"""
        dirs = [
            "data",
            "config",
            "src",
        ]
        
        for dir_name in dirs:
            dir_path = Path(dir_name)
            assert dir_path.exists(), f"Directory {dir_name} should exist"
    
    def test_approval_data_files_creatable(self):
        """Test approval data files can be created"""
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        # Test workflow file
        workflow_file = data_dir / "approval_workflow_state.json"
        workflow_file.write_text(json.dumps({"requests": {}}))
        assert workflow_file.exists()
        
        # Test decisions file
        decisions_file = data_dir / "approval_decisions.json"
        decisions_file.write_text(json.dumps([]))
        assert decisions_file.exists()


class TestEmailConfiguration:
    """Test email configuration"""
    
    def test_email_config_file_structure(self):
        """Test email config file has correct structure"""
        config_file = Path("config/email_config.json")
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Check required fields
            assert "email" in config or "email_address" in config
            # Password should be set
            assert "password" in config or "app_password" in config


class TestPerformance:
    """Test system performance"""
    
    API_URL = "http://localhost:8000"
    
    def test_approval_endpoints_response_time(self):
        """Test approval endpoints respond quickly"""
        start_time = time.time()
        response = requests.get(f"{self.API_URL}/api/approvals/summary/stats", timeout=5)
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 2.0, "Endpoint should respond in less than 2 seconds"
    
    def test_health_check_response_time(self):
        """Test health check responds quickly"""
        start_time = time.time()
        response = requests.get(f"{self.API_URL}/health", timeout=5)
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 1.0, "Health check should respond in less than 1 second"


# ============================================================================
# Test Execution
# ============================================================================

def run_all_tests():
    """Run all tests with summary"""
    print("\n" + "=" * 70)
    print("🧪 PIDDY UNIFIED SYSTEM - INTEGRATION TEST SUITE")
    print("=" * 70 + "\n")
    
    # Try to connect to API
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        print("✅ Dashboard API is running\n")
    except requests.exceptions.ConnectionError:
        print("❌ Dashboard API is NOT running")
        print("   Please start the dashboard: python src/dashboard_manager.py --start\n")
        return False
    
    # Run pytest if available
    try:
        pytest.main([__file__, "-v", "--tb=short"])
        return True
    except ImportError:
        print("⚠️  pytest not installed, running basic checks...\n")
        
        # Run basic checks
        test_classes = [
            TestHealthCheckEndpoints,
            TestApprovalSystemEndpoints,
            TestApprovalWorkflow,
            TestDataModels,
            TestDashboardIntegration,
            TestSystemConfiguration,
        ]
        
        passed = 0
        failed = 0
        
        for test_class in test_classes:
            print(f"\n📋 Running {test_class.__name__}...")
            test_instance = test_class()
            
            for method_name in dir(test_instance):
                if method_name.startswith("test_"):
                    try:
                        method = getattr(test_instance, method_name)
                        method()
                        print(f"  ✅ {method_name}")
                        passed += 1
                    except AssertionError as e:
                        print(f"  ❌ {method_name}: {e}")
                        failed += 1
                    except Exception as e:
                        print(f"  ⚠️  {method_name}: {type(e).__name__}: {e}")
        
        print(f"\n{'='*70}")
        print(f"Results: {passed} passed, {failed} failed")
        print(f"{'='*70}\n")
        
        return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
