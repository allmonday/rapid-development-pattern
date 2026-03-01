"""Pytest configuration for benchmark tests."""

import asyncio
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def db_setup():
    """Initialize database for testing."""
    import src.db as db

    await db.init()
    await db.prepare()

    yield

    await db.engine.dispose()


@pytest.fixture
def collector():
    """Create a fresh metrics collector."""
    from benchmark.metrics.collector import MetricsCollector
    return MetricsCollector()


@pytest.fixture
def iterations(quick_test):
    """Get number of iterations based on quick mode."""
    return 10 if quick_test else 50


@pytest.fixture
def quick_test(request):
    """Check if running in quick mode."""
    return request.config.getoption("--quick", default=False)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--quick",
        action="store_true",
        default=False,
        help="Run quick tests with fewer iterations"
    )
