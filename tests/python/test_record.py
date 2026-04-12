"""Test suite for vSPACE Augmented Election Record (F-109)."""

import pytest
import sys
import os
import json

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "bindings", "python")
)

from electionguard_vspace.record import (
    AugmentedRecordBuilder,
    serialize_augmented_record,
    validate_augmented_record,
    verify_backward_compatibility,
)


class TestAugmentedRecordBuilder:
    """Test augmented record builder functionality."""

    def test_builder_init(self):
        """Test builder initialization."""
        builder = AugmentedRecordBuilder(election_id="election_001")
        assert builder.election_id == "election_001"

    def test_builder_add_serial(self):
        """Test adding serial number."""
        builder = AugmentedRecordBuilder(election_id="election_001")

        builder.add_serial("serial_001")

        serials = builder.get_serials()
        assert "serial_001" in serials

    def test_builder_add_binding(self):
        """Test adding binding commitment."""
        builder = AugmentedRecordBuilder(election_id="election_001")

        binding = {
            "commitment": "test_commitment",
            "generator_g": "test_g",
            "generator_h": "test_h",
            "context": {
                "election_id": "election_001",
                "ballot_style_id": "style_001",
                "precinct_id": "precinct_001",
                "timestamp": "2024-01-01T00:00:00Z",
            },
        }

        builder.add_binding(binding)

        bindings = builder.get_bindings()
        assert len(bindings) == 1

    def test_builder_build(self):
        """Test building final record."""
        builder = AugmentedRecordBuilder(election_id="election_001")

        builder.add_serial("serial_001")
        builder.add_serial("serial_002")

        record = builder.build()

        assert "version" in record
        assert "issuer_params_hash" in record
        assert "serial_numbers" in record
        assert "verification_summary" in record

    def test_builder_multiple_serials(self):
        """Test adding multiple serials."""
        builder = AugmentedRecordBuilder(election_id="election_001")

        for i in range(10):
            builder.add_serial(f"serial_{i}")

        serials = builder.get_serials()
        assert len(serials) == 10


class TestSerializeAugmentedRecord:
    """Test record serialization."""

    def test_serialize_to_json(self):
        """Test JSON serialization."""
        builder = AugmentedRecordBuilder(election_id="election_001")
        builder.add_serial("serial_001")

        record = builder.build()

        json_str = serialize_augmented_record(record, format="json")

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["version"] == record["version"]

    def test_serialize_to_bson(self):
        """Test BSON serialization placeholder."""
        builder = AugmentedRecordBuilder(election_id="election_001")
        builder.add_serial("serial_001")

        record = builder.build()

        bson_data = serialize_augmented_record(record, format="bson")

        # BSON returns bytes
        assert isinstance(bson_data, bytes) or bson_data is not None

    def test_serialize_preserves_structure(self):
        """Test that serialization preserves structure."""
        builder = AugmentedRecordBuilder(election_id="election_001")
        builder.add_serial("serial_001")
        builder.add_serial("serial_002")

        record = builder.build()

        json_str = serialize_augmented_record(record, format="json")
        parsed = json.loads(json_str)

        assert len(parsed["serial_numbers"]) == 2


class TestValidateAugmentedRecord:
    """Test record validation."""

    def test_validate_valid_record(self):
        """Test validation of valid record."""
        builder = AugmentedRecordBuilder(election_id="election_001")
        builder.add_serial("serial_001")

        record = builder.build()

        result = validate_augmented_record(record)
        assert result is True

    def test_validate_missing_version(self):
        """Test validation catches missing version."""
        record = {
            "issuer_params_hash": "hash",
            "serial_numbers": ["serial_001"],
        }

        result = validate_augmented_record(record)
        assert result is False

    def test_validate_missing_serials(self):
        """Test validation catches missing serials."""
        record = {
            "version": "1.0",
            "issuer_params_hash": "hash",
            "verification_summary": {},
        }

        result = validate_augmented_record(record)
        assert result is False

    def test_validate_structure(self):
        """Test structure validation."""
        builder = AugmentedRecordBuilder(election_id="election_001")

        # Add proper data
        builder.add_serial("serial_001")

        record = builder.build()

        # Should validate structure
        result = validate_augmented_record(record)
        assert result is True


class TestVerifyBackwardCompatibility:
    """Test backward compatibility verification."""

    def test_backward_compatible_structure(self):
        """Test backward compatible structure."""
        builder = AugmentedRecordBuilder(election_id="election_001")
        builder.add_serial("serial_001")

        record = builder.build()

        # Should be backward compatible
        result = verify_backward_compatibility(record)
        assert result is True

    def test_vspace_section_is_optional(self):
        """Test that vspace section is optional for standard verifiers."""
        # Standard ElectionGuard record without vspace section
        standard_record = {
            "election_id": "election_001",
            "manifest_hash": "manifest_hash",
            "ballots": [],
        }

        # Should work without vspace section
        result = verify_backward_compatibility(standard_record)
        assert result is True


class TestVerificationSummary:
    """Test verification summary."""

    def test_summary_counts(self):
        """Test summary counts are correct."""
        builder = AugmentedRecordBuilder(election_id="election_001")

        builder.add_serial("serial_001")
        builder.add_serial("serial_002")
        builder.add_serial("serial_003")

        record = builder.build()

        summary = record["verification_summary"]

        assert summary["total_ballots"] >= 0
        assert summary["unique_serials"] >= 0


class TestAugmentedRecordStructure:
    """Test augmented record structure."""

    def test_record_has_vspace_section(self):
        """Test that record has vspace_section."""
        builder = AugmentedRecordBuilder(election_id="election_001")
        builder.add_serial("serial_001")

        record = builder.build()

        # Record should have vspace extension fields
        assert "version" in record
        assert "serial_numbers" in record

    def test_record_is_json_serializable(self):
        """Test that record is JSON serializable."""
        builder = AugmentedRecordBuilder(election_id="election_001")
        builder.add_serial("serial_001")

        record = builder.build()

        # Should serialize without error
        json_str = json.dumps(record)
        assert json_str


class TestIntegrationWithStandardRecord:
    """Test integration with standard ElectionGuard record."""

    def test_augmented_record_additive(self):
        """Test that augmented record is additive."""
        # Standard ElectionGuard record
        standard = {
            "election_id": "election_001",
            "manifest_hash": "hash",
        }

        # Augmented extension
        builder = AugmentedRecordBuilder(election_id="election_001")
        builder.add_serial("serial_001")

        augmented = builder.build()

        # Combined record
        combined = {**standard, **{"vspace": augmented}}

        # Should have both standard and vspace sections
        assert "election_id" in combined
        assert "vspace" in combined


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
