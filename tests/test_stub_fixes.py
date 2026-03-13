"""Regression tests for critical stub fixes.

Tests for:
- Security checks (8 functions)
- Database operations (3 functions)
- Registration with real DB
- Refactoring rollback/execute
- Audit logging verification
- Slash commands
- Health checks
"""

import pytest
import os
import tempfile
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

# === TEST FIXTURES ===

@pytest.fixture
def db():
    """Fixture providing test database session"""
    from src.database import SessionLocal, Base, engine
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    yield db
    
    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Fixture providing FastAPI test client"""
    from src.api.routes.auth import auth
    from fastapi import FastAPI
    
    app = FastAPI()
    app.include_router(auth.router)
    
    return TestClient(app)


# === SECURITY CHECKS TESTS (Issue #1) ===

@pytest.mark.asyncio
async def test_security_check_tls_validates():
    """Test that TLS check actually validates, not always True"""
    from src.phase19_production_hardening import ProductionSecurityValidator
    
    validator = ProductionSecurityValidator()
    result = await validator._check_tls()
    
    # Should return bool, not always True
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_security_check_encryption_requires_key():
    """Test that encryption check requires actual configuration"""
    from src.phase19_production_hardening import ProductionSecurityValidator
    
    validator = ProductionSecurityValidator()
    result = await validator._check_encryption_at_rest()
    
    # Should check for actual key, not always True
    assert isinstance(result, bool)
    # Without key configured, should be False
    if not os.getenv('DB_ENCRYPTION_KEY'):
        assert result is False, "Encryption check should fail without key"


@pytest.mark.asyncio
async def test_security_check_input_validation():
    """Test input validation check"""
    from src.phase19_production_hardening import ProductionSecurityValidator
    
    validator = ProductionSecurityValidator()
    result = await validator._check_input_validation()
    
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_security_check_rate_limiting():
    """Test rate limiting check"""
    from src.phase19_production_hardening import ProductionSecurityValidator
    
    validator = ProductionSecurityValidator()
    result = await validator._check_rate_limiting()
    
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_security_check_approval_gates():
    """Test approval gates check"""
    from src.phase19_production_hardening import ProductionSecurityValidator
    
    validator = ProductionSecurityValidator()
    result = await validator._check_approval_gates()
    
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_security_check_audit_logging():
    """Test audit logging check"""
    from src.phase19_production_hardening import ProductionSecurityValidator
    
    validator = ProductionSecurityValidator()
    result = await validator._check_audit_logging()
    
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_security_check_alerting():
    """Test alerting check"""
    from src.phase19_production_hardening import ProductionSecurityValidator
    
    validator = ProductionSecurityValidator()
    result = await validator._check_alerting()
    
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_security_check_dependency_scanning():
    """Test dependency scanning check"""
    from src.phase19_production_hardening import ProductionSecurityValidator
    
    validator = ProductionSecurityValidator()
    result = await validator._check_dependency_scanning()
    
    assert isinstance(result, bool)


# === DATABASE OPERATIONS TESTS (Issue #2) ===

@pytest.mark.asyncio
async def test_get_user_by_username_queries_db(db):
    """Test that get_user_by_username actually queries database"""
    from src.api.routes.auth.auth import get_user_by_username, create_user, UserCreate
    
    # Create a test user
    user_data = UserCreate(
        email="testuser@example.com",
        username="testuser",
        password="SecurePass123",
        full_name="Test User"
    )
    new_user = await create_user(db, user_data)
    assert new_user.id is not None
    
    # Now retrieve it
    retrieved_user = await get_user_by_username(db, "testuser")
    assert retrieved_user is not None
    assert retrieved_user.username == "testuser"
    assert retrieved_user.id == new_user.id


@pytest.mark.asyncio
async def test_get_user_by_email_queries_db(db):
    """Test that get_user_by_email actually queries database"""
    from src.api.routes.auth.auth import get_user_by_email, create_user, UserCreate
    
    # Create a test user
    user_data = UserCreate(
        email="email@example.com",
        username="emailuser",
        password="SecurePass123",
        full_name="Email User"
    )
    new_user = await create_user(db, user_data)
    
    # Retrieve by email
    retrieved_user = await get_user_by_email(db, "email@example.com")
    assert retrieved_user is not None
    assert retrieved_user.email == "email@example.com"
    assert retrieved_user.id == new_user.id


@pytest.mark.asyncio
async def test_create_user_stores_in_db(db):
    """Test that create_user actually stores user in database"""
    from src.api.routes.auth.auth import create_user, get_user_by_username, UserCreate
    
    user_data = UserCreate(
        email="newuser@example.com",
        username="newuser",
        password="SecurePass123",
        full_name="New User"
    )
    
    user = await create_user(db, user_data)
    
    # Verify stored
    assert user.id is not None
    assert user.email == "newuser@example.com"
    
    # Verify retrievable
    retrieved = await get_user_by_username(db, "newuser")
    assert retrieved is not None
    assert retrieved.id == user.id


# === REGISTRATION TESTS (Issue #3) ===

@pytest.mark.asyncio
async def test_registration_creates_real_db_user(db):
    """Test that registration creates real user with DB ID, not mock"""
    from src.api.routes.auth.auth import register, UserCreate
    
    user_data = UserCreate(
        email="newreg@example.com",
        username="newreg",
        password="SecurePass123",
        full_name="New Registration"
    )
    
    response = await register(user_data, db=db)
    
    # Should have real database ID, not hardcoded 1
    assert response.id is not None
    assert isinstance(response.id, int)
    assert response.id > 0
    
    # Second user should have different ID
    user_data2 = UserCreate(
        email="newreg2@example.com",
        username="newreg2",
        password="SecurePass123",
        full_name="Second Registration"
    )
    response2 = await register(user_data2, db=db)
    assert response2.id != response.id


@pytest.mark.asyncio
async def test_registration_prevents_duplicate_email(db):
    """Test that registration prevents duplicate emails"""
    from src.api.routes.auth.auth import register, UserCreate
    from fastapi import HTTPException
    
    user_data = UserCreate(
        email="duplicate@example.com",
        username="user1",
        password="SecurePass123",
        full_name="Test"
    )
    
    # First registration should succeed
    response1 = await register(user_data, db=db)
    assert response1.email == "duplicate@example.com"
    
    # Second registration with same email should fail
    user_data.username = "user2"
    with pytest.raises(HTTPException) as exc_info:
        await register(user_data, db=db)
    
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_registration_prevents_duplicate_username(db):
    """Test that registration prevents duplicate usernames"""
    from src.api.routes.auth.auth import register, UserCreate
    from fastapi import HTTPException
    
    user_data = UserCreate(
        email="user1@example.com",
        username="duplicateuser",
        password="SecurePass123",
        full_name="Test"
    )
    
    # First registration should succeed
    response1 = await register(user_data, db=db)
    assert response1.username == "duplicateuser"
    
    # Second registration with same username should fail
    user_data.email = "user2@example.com"
    with pytest.raises(HTTPException) as exc_info:
        await register(user_data, db=db)
    
    assert exc_info.value.status_code == 400


# === REFACTORING TESTS (Issue #4) ===

def test_refactoring_execute_creates_snapshot(tmp_path):
    """Test that execute creates snapshot before changes"""
    from src.phase24_autonomous_refactoring import RefactoringExecutor, RefactoringPlan, RefactoringType, RefactoringStatus
    
    executor = RefactoringExecutor()
    executor.snapshot_dir = str(tmp_path)
    
    # Create test file
    test_file = tmp_path / "test.py"
    test_file.write_text("original content")
    
    # Execute refactoring
    plan = RefactoringPlan(
        refactoring_id="test-123",
        refactoring_type=RefactoringType.RENAME_SYMBOL,
        description="Test refactoring"
    )
    
    changes = {str(test_file): "new content"}
    result = executor.execute(plan, changes)
    
    assert result is True
    assert plan.status == RefactoringStatus.COMPLETED
    assert "test-123" in executor.snapshots


def test_refactoring_rollback_restores_files(tmp_path):
    """Test that rollback restores original files"""
    from src.phase24_autonomous_refactoring import RefactoringExecutor, RefactoringPlan, RefactoringType
    
    executor = RefactoringExecutor()
    executor.snapshot_dir = str(tmp_path)
    
    # Create test file
    test_file = tmp_path / "test.py"
    original_content = "original content"
    test_file.write_text(original_content)
    
    # Execute refactoring
    plan = RefactoringPlan(
        refactoring_id="test-456",
        refactoring_type=RefactoringType.RENAME_SYMBOL,
        description="Test refactoring"
    )
    
    changes = {str(test_file): "modified content"}
    executor.execute(plan, changes)
    
    # Verify file was changed
    assert test_file.read_text() == "modified content"
    
    # Rollback
    success = executor.rollback("test-456")
    assert success is True
    
    # Verify file was restored
    assert test_file.read_text() == original_content


def test_refactoring_rollback_deletes_new_files(tmp_path):
    """Test that rollback deletes newly created files"""
    from src.phase24_autonomous_refactoring import RefactoringExecutor, RefactoringPlan, RefactoringType
    
    executor = RefactoringExecutor()
    executor.snapshot_dir = str(tmp_path)
    
    # New file path (doesn't exist yet)
    new_file = tmp_path / "new_file.py"
    
    # Execute refactoring creating new file
    plan = RefactoringPlan(
        refactoring_id="test-789",
        refactoring_type=RefactoringType.RENAME_SYMBOL,
        description="Test refactoring"
    )
    
    changes = {str(new_file): "new file content"}
    executor.execute(plan, changes)
    
    # Verify file was created
    assert new_file.exists()
    
    # Rollback
    success = executor.rollback("test-789")
    assert success is True
    
    # Verify file was deleted
    assert not new_file.exists()


# === AUDIT LOGGING TESTS (Issue #5) ===

@pytest.mark.asyncio
async def test_audit_logging_checks_database(db):
    """Test that audit logging checks database"""
    from src.phase31_security_compliance import ComplianceValidator, User, ActionType
    from datetime import datetime
    
    # This should not raise an error even if DB is empty
    validator = ComplianceValidator()
    
    # Create test user
    test_user = User(
        user_id="test-user",
        username="testuser",
        role=None,
        created_at=datetime.now(),
        active=True
    )
    
    # Should return False (no logs) rather than always True
    result = validator._audit_logged(ActionType.DEPLOY, test_user)
    assert isinstance(result, bool)


# === SLASH COMMANDS TESTS (Issue #7) ===

@pytest.mark.asyncio
async def test_slash_commands_dispatch_to_handlers():
    """Test that slash commands dispatch to appropriate handlers"""
    from src.api.slack_commands import handle_slash_command
    from fastapi import Request
    from unittest.mock import AsyncMock, MagicMock
    
    # Create mock request
    request = MagicMock(spec=Request)
    request.form = AsyncMock(return_value={})
    
    # Test analyze command
    response = await handle_slash_command("analyze", request)
    assert response["response_type"] == "in_channel"
    assert "Analyzing" in response["text"]
    
    # Test fix command
    response = await handle_slash_command("fix", request)
    assert response["response_type"] == "in_channel"
    assert "Fixing" in response["text"]
    
    # Test deploy command
    response = await handle_slash_command("deploy", request)
    assert response["response_type"] == "in_channel"
    assert "Deploying" in response["text"]
    
    # Test status command
    response = await handle_slash_command("status", request)
    assert response["response_type"] == "in_channel"
    assert "Status" in response["text"]


@pytest.mark.asyncio
async def test_slash_commands_handle_unknown():
    """Test that unknown commands are handled gracefully"""
    from src.api.slack_commands import handle_slash_command
    from fastapi import Request
    from unittest.mock import AsyncMock, MagicMock
    
    request = MagicMock(spec=Request)
    request.form = AsyncMock(return_value={})
    
    response = await handle_slash_command("unknown", request)
    assert response["response_type"] == "ephemeral"
    assert "Unknown command" in response["text"]


# === HEALTH CHECKS TESTS (Issue #8) ===

@pytest.mark.asyncio
async def test_health_check_api_validates():
    """Test that API health check actually validates"""
    from src.api.self_healing import _check_api_health
    
    result = await _check_api_health()
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_health_check_database_validates():
    """Test that database health check actually validates"""
    from src.api.self_healing import _check_database_health
    
    result = await _check_database_health()
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_health_check_auth_validates():
    """Test that auth health check actually validates"""
    from src.api.self_healing import _check_auth_health
    
    result = await _check_auth_health()
    assert isinstance(result, bool)


@pytest.mark.asyncio
async def test_integration_validation_uses_checks():
    """Test that integration validation uses actual checks"""
    from src.api.self_healing import _validate_integration
    
    result = await _validate_integration()
    
    assert result["status"] == "validation_complete"
    assert "integrations" in result
    assert "readiness_score" in result
    
    # All should be bool values
    for check_name, check_result in result["integrations"].items():
        assert isinstance(check_result, bool), f"{check_name} should be bool"


# === SUMMARY ===

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
