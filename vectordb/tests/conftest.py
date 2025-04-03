import os
import sys
from pathlib import Path

# Add the parent directory to PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))


# Configure test settings
def pytest_configure(config):
    """Configure test settings."""
    # Add markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
