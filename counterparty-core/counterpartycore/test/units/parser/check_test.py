import pytest
from counterpartycore.lib import config, exceptions
from counterpartycore.lib.parser import check


def test_check_change_version_ok():
    """Test check_change when version is acceptable."""
    protocol_change = {
        "block_index": 100,
        "minimum_version_major": config.VERSION_MAJOR,
        "minimum_version_minor": config.VERSION_MINOR,
        "minimum_version_revision": config.VERSION_REVISION,
    }

    # Should not raise any exception
    check.check_change(protocol_change, "test_change")


def test_check_change_version_major_too_low(ledger_db, current_block_index):
    """Test check_change when major version is too low."""
    protocol_change = {
        "block_index": 1,  # In the past
        "minimum_version_major": config.VERSION_MAJOR + 1,
        "minimum_version_minor": 0,
        "minimum_version_revision": 0,
    }

    with pytest.raises(exceptions.VersionUpdateRequiredError):
        check.check_change(protocol_change, "test_change")


def test_check_change_version_minor_too_low(ledger_db, current_block_index):
    """Test check_change when minor version is too low."""
    protocol_change = {
        "block_index": 1,  # In the past
        "minimum_version_major": config.VERSION_MAJOR,
        "minimum_version_minor": config.VERSION_MINOR + 1,
        "minimum_version_revision": 0,
    }

    with pytest.raises(exceptions.VersionUpdateRequiredError):
        check.check_change(protocol_change, "test_change")


def test_check_change_version_revision_too_low(ledger_db, current_block_index):
    """Test check_change when revision version is too low."""
    protocol_change = {
        "block_index": 1,  # In the past
        "minimum_version_major": config.VERSION_MAJOR,
        "minimum_version_minor": config.VERSION_MINOR,
        "minimum_version_revision": config.VERSION_REVISION + 1,
    }

    with pytest.raises(exceptions.VersionUpdateRequiredError):
        check.check_change(protocol_change, "test_change")


def test_check_change_version_warning_future_block(ledger_db, current_block_index, caplog):
    """Test check_change logs warning when block is in the future."""
    protocol_change = {
        "block_index": 999999999,  # Far in the future
        "minimum_version_major": config.VERSION_MAJOR + 1,
        "minimum_version_minor": 0,
        "minimum_version_revision": 0,
    }

    # Should not raise, just log a warning (block is in the future)
    check.check_change(protocol_change, "test_change")


def test_software_version_force_mode():
    """Test software_version with FORCE mode enabled."""
    original_force = config.FORCE
    config.FORCE = True

    try:
        result = check.software_version()
        assert result is True
    finally:
        config.FORCE = original_force


def test_software_version_connection_error(monkeypatch):
    """Test software_version with connection error."""
    original_force = config.FORCE
    config.FORCE = False

    def mock_get(*args, **kwargs):
        raise ConnectionRefusedError("Connection refused")

    monkeypatch.setattr("requests.get", mock_get)

    try:
        with pytest.raises(
            exceptions.VersionCheckError, match="Unable to check Counterparty version"
        ):
            check.software_version()
    finally:
        config.FORCE = original_force


def test_software_version_timeout_error(monkeypatch):
    """Test software_version with timeout error."""
    import requests

    original_force = config.FORCE
    config.FORCE = False

    def mock_get(*args, **kwargs):
        raise requests.exceptions.ReadTimeout("Read timed out")

    monkeypatch.setattr("requests.get", mock_get)

    try:
        with pytest.raises(
            exceptions.VersionCheckError, match="Unable to check Counterparty version"
        ):
            check.software_version()
    finally:
        config.FORCE = original_force


def test_software_version_json_decode_error(monkeypatch):
    """Test software_version with invalid JSON response."""

    original_force = config.FORCE
    config.FORCE = False

    class MockResponse:
        status_code = 200
        text = "not valid json"

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)

    try:
        with pytest.raises(
            exceptions.VersionCheckError, match="Unable to check Counterparty version"
        ):
            check.software_version()
    finally:
        config.FORCE = original_force


def test_software_version_success(monkeypatch):
    """Test software_version with valid response."""
    import json

    original_force = config.FORCE
    config.FORCE = False

    class MockResponse:
        status_code = 200
        text = json.dumps(
            {
                "test_change": {
                    "block_index": 999999999,
                    "minimum_version_major": 0,
                    "minimum_version_minor": 0,
                    "minimum_version_revision": 0,
                }
            }
        )

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)

    try:
        result = check.software_version()
        assert result is True
    finally:
        config.FORCE = original_force


def test_consensus_hash_invalid_field(ledger_db):
    """Test consensus_hash with invalid field."""
    with pytest.raises(AssertionError):
        check.consensus_hash(ledger_db, "invalid_field", None, [])
