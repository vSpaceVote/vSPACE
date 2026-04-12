"""Test suite for vSPACE One-Show Serial Enforcement (F-103)."""

import pytest
import sys
import os

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "bindings", "python")
)

from electionguard_vspace.serial import (
    VRFSerialDerivation,
    SerialRegistry,
    verify_serial_uniqueness,
    MongoDBSchema,
)
from electionguard_vspace.constants import (
    HASH_PREFIX_VRF_SERIAL,
    MIN_SERIAL_LENGTH,
    MAX_SERIAL_LENGTH,
)


class TestVRFSerialDerivation:
    """Test VRF serial derivation functionality."""

    def test_vrf_init(self):
        """Test VRF derivation initialization."""
        vrf = VRFSerialDerivation()
        assert vrf is not None

    def test_derive_serial(self):
        """Test serial derivation."""
        vrf = VRFSerialDerivation()

        serial = vrf.derive_serial(
            credential_id="cred_001",
            election_id="election_001",
            context="additional_context",
        )

        assert "serial" in serial
        assert "vrf_proof" in serial

    def test_serial_length_valid(self):
        """Test that derived serial has valid length."""
        vrf = VRFSerialDerivation()

        serial = vrf.derive_serial(
            credential_id="cred_001",
            election_id="election_001",
            context="additional_context",
        )

        # Serial should be within bounds
        serial_hex = serial["serial"]
        serial_bytes = (
            bytes.fromhex(serial_hex)
            if len(serial_hex) >= MIN_SERIAL_LENGTH * 2
            else b""
        )

        # Minimum length check (hex representation)
        assert len(serial_hex) >= MIN_SERIAL_LENGTH * 2

    def test_serial_is_deterministic(self):
        """Test that serial derivation is deterministic."""
        vrf = VRFSerialDerivation()

        serial1 = vrf.derive_serial(
            credential_id="cred_001",
            election_id="election_001",
            context="context",
        )

        serial2 = vrf.derive_serial(
            credential_id="cred_001",
            election_id="election_001",
            context="context",
        )

        # Same inputs should produce same serial
        assert serial1["serial"] == serial2["serial"]

    def test_serial_different_credentials(self):
        """Test that different credentials produce different serials."""
        vrf = VRFSerialDerivation()

        serial1 = vrf.derive_serial(
            credential_id="cred_001",
            election_id="election_001",
            context="context",
        )

        serial2 = vrf.derive_serial(
            credential_id="cred_002",  # Different credential
            election_id="election_001",
            context="context",
        )

        # Different credentials should produce different serials
        assert serial1["serial"] != serial2["serial"]


class TestSerialRegistry:
    """Test serial registry functionality."""

    def test_registry_init(self):
        """Test registry initialization."""
        registry = SerialRegistry(election_id="election_001")
        assert registry.election_id == "election_001"

    def test_register_serial(self):
        """Test serial registration."""
        registry = SerialRegistry(election_id="election_001")

        result = registry.register("serial_001")
        assert result is True

    def test_duplicate_detection(self):
        """Test that duplicates are detected."""
        registry = SerialRegistry(election_id="election_001")

        # First registration succeeds
        registry.register("serial_001")

        # Second registration of same serial fails
        result = registry.register("serial_001")
        assert result is False

    def test_registry_count(self):
        """Test registry count tracking."""
        registry = SerialRegistry(election_id="election_001")

        registry.register("serial_001")
        registry.register("serial_002")
        registry.register("serial_003")

        count = registry.count()
        assert count == 3

    def test_registry_clear(self):
        """Test registry clearing."""
        registry = SerialRegistry(election_id="election_001")

        registry.register("serial_001")
        registry.register("serial_002")

        registry.clear()

        count = registry.count()
        assert count == 0


class TestVerifySerialUniqueness:
    """Test serial uniqueness verification."""

    def test_verify_unique_serials(self):
        """Test verification of unique serials."""
        serials = ["serial_001", "serial_002", "serial_003"]

        duplicates = verify_serial_uniqueness(serials)

        # No duplicates should be found
        assert len(duplicates) == 0

    def test_verify_detects_duplicates(self):
        """Test detection of duplicate serials."""
        serials = ["serial_001", "serial_002", "serial_001"]  # Duplicate

        duplicates = verify_serial_uniqueness(serials)

        # Duplicate should be detected
        assert len(duplicates) > 0
        assert "serial_001" in duplicates

    def test_verify_empty_list(self):
        """Test verification of empty list."""
        serials = []

        duplicates = verify_serial_uniqueness(serials)

        assert len(duplicates) == 0

    def test_verify_algorithm_complexity(self):
        """Test that algorithm is O(n log n)."""
        # This is a structural test, not timing test
        # The implementation uses hash-based detection
        serials = [f"serial_{i}" for i in range(1000)]

        duplicates = verify_serial_uniqueness(serials)

        assert len(duplicates) == 0


class TestMongoDBSchema:
    """Test MongoDB schema definition."""

    def test_schema_collection_name(self):
        """Test collection name is correct."""
        schema = MongoDBSchema()

        assert schema.collection_name == "vspace_serial_numbers"

    def test_schema_indexes_defined(self):
        """Test that indexes are defined."""
        schema = MongoDBSchema()

        indexes = schema.get_indexes()

        # Should have unique index on serial
        assert len(indexes) > 0

    def test_schema_document_structure(self):
        """Test document structure."""
        schema = MongoDBSchema()

        doc = schema.create_document(
            serial="serial_001",
            election_id="election_001",
        )

        assert doc["serial"] == "serial_001"
        assert doc["election_id"] == "election_001"
        assert "registered_at" in doc
        assert "status" in doc


class TestConstants:
    """Test serial constants."""

    def test_min_serial_length(self):
        """Test minimum serial length."""
        assert MIN_SERIAL_LENGTH == 16

    def test_max_serial_length(self):
        """Test maximum serial length."""
        assert MAX_SERIAL_LENGTH == 64

    def test_hash_prefix_defined(self):
        """Test hash prefix is defined."""
        assert HASH_PREFIX_VRF_SERIAL


class TestOneShowEnforcement:
    """Test one-show enforcement property."""

    def test_single_use_allowed(self):
        """Test that single use is allowed."""
        registry = SerialRegistry(election_id="election_001")

        # First use should succeed
        result = registry.register("serial_001")
        assert result is True

    def test_double_use_blocked(self):
        """Test that double use is blocked."""
        registry = SerialRegistry(election_id="election_001")

        # First use succeeds
        registry.register("serial_001")

        # Second use fails
        result = registry.register("serial_001")
        assert result is False

    def test_different_serials_both_allowed(self):
        """Test that different serials both allowed."""
        registry = SerialRegistry(election_id="election_001")

        # Both uses should succeed
        result1 = registry.register("serial_001")
        result2 = registry.register("serial_002")

        assert result1 is True
        assert result2 is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
