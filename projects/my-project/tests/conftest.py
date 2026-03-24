import pytest
from my_project.config import settings

@pytest.fixture(scope="module")
def test_settings():
    return settings
