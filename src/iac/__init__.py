"""Infrastructure as Code (IaC) validation module."""

from .validator import IaCValidator, get_iac_validator
import logging

logger = logging.getLogger(__name__)
__all__ = ["IaCValidator", "get_iac_validator"]
