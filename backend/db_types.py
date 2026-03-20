"""
Custom SQLAlchemy Types for Merbana Backend

This module contains custom SQLAlchemy types if needed for specialized
data handling beyond standard SQLAlchemy types.

Currently, the schema uses standard types only. This file is provided
for future extensibility (e.g., JSON handling, encrypted fields, etc.)
"""

from sqlalchemy import TypeDecorator, String
from typing import Optional


# Example custom type (for future use):
# class ISODateTime(TypeDecorator):
#     """
#     Custom type for ISO 8601 datetime strings.
#     Ensures consistent datetime storage format.
#     """
#     impl = String(50)
#     cache_ok = True
#
#     def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
#         """Validate and normalize datetime before storage."""
#         if value is None:
#             return None
#         # Validation logic here if needed
#         return value
#
#     def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
#         """Process value when reading from database."""
#         return value


# Note: Currently using plain String columns for dates to match
# the existing JSON behavior exactly. If stricter datetime validation
# is needed later, use the custom type pattern above.
