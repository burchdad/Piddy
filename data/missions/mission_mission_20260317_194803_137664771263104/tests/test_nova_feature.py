import pytest
from src.nova_feature import main

def test_feature():
    assert main() == "Nova feature working"
