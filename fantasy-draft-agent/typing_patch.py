"""
Patch typing module for Python 3.11 compatibility.
The 'override' decorator was added in Python 3.12.
For Python 3.11, we need to use typing_extensions.
"""

import sys
import typing

# Check if override is already available (Python 3.12+)
if not hasattr(typing, 'override'):
    try:
        # Try to import from typing_extensions
        from typing_extensions import override
        # Monkey-patch it into typing module
        typing.override = override
        print("✅ Patched typing.override from typing_extensions")
    except ImportError:
        # If typing_extensions is not available, create a dummy decorator
        def override(func):
            """Dummy override decorator for compatibility."""
            return func
        typing.override = override
        print("⚠️ Created dummy typing.override decorator") 