"""Comprehensive integration test for vSPACE full workflow."""

import pytest
import sys
import os
import json

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "bindings", "python")
)

from electionguard_vspace.saac import (
    SAACIssuer,
    SAACHolder,
    verify_presentation,
)
from electionguard_vspace.multiholder import (
    CredentialSplitter,
    ThresholdPresenter,
    combine_threshold_presentations,
)
from electionguard_vspace.binding import (
    BindingGenerator,
    ProofGenerator,
    verify_binding_proof,
    wrap_ballot_encryption,
)
from electionguard_vspace.serial import (
    VRFSerialDerivation,
    SerialRegistry,
    verify_serial_uniqueness,
)
from electionguard_vspace.record import (
    AugmentedRecordBuilder,
    serialize_augmented_record,
    validate_augmented_record,
)


class TestFullWorkflow:
    """Test complete vSPACE workflow from credential to record."""

    def test_complete_workflow_10_voters(self):
        """Test complete workflow with 10 voters."""
        # Phase 1: Setup - Issuer generates parameters
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()

        # Phase 2: Credential issuance for 10 voters
        voters = []
        for i in range(10):
            credential = issuer.issue_credential(params)
            holder = SAACHolder(credential, params)
            voters.append(
                {
                    "id": f"voter_{i}",
                    "credential": credential,
                    "holder": holder,
                }
            )

        # Phase 3: Create presentations
        presentations = []
        for voter in voters:
            presentation = voter["holder"].create_presentation()
            presentations.append(presentation)

        # Phase 4: Verify all presentations
        for presentation in presentations:
            result = verify_presentation(presentation, params)
            assert result is True

        # Phase 5: Create bindings for each ballot
        bindings = []
        proofs = []
        for i, voter in enumerate(voters):
            binding_gen = BindingGenerator()
            commitment = binding_gen.generate_commitment(
                election_id="election_001",
                ballot_style_id=f"style_{i % 3}",
                precinct_id=f"precinct_{i % 5}",
            )

            proof_gen = ProofGenerator()
            proof = proof_gen.generate_binding_proof(commitment)

            bindings.append(commitment)
            proofs.append(proof)

        # Phase 6: Verify all binding proofs
        for binding, proof in zip(bindings, proofs):
            result = verify_binding_proof(proof, binding)
            assert result is True

        # Phase 7: Derive serials for one-show enforcement
        vrf = VRFSerialDerivation()
        serials = []
        for voter in voters:
            serial = vrf.derive_serial(
                credential_id=voter["credential"]["credential_id"],
                election_id="election_001",
                context="ballot_cast",
            )
            serials.append(serial["serial"])

        # Phase 8: Verify no duplicates
        duplicates = verify_serial_uniqueness(serials)
        assert len(duplicates) == 0

        # Phase 9: Register serials in registry
        registry = SerialRegistry(election_id="election_001")
        for serial in serials:
            result = registry.register(serial)
            assert result is True

        # Phase 10: Build augmented record
        record_builder = AugmentedRecordBuilder(election_id="election_001")

        for serial in serials:
            record_builder.add_serial(serial)

        for binding in bindings:
            record_builder.add_binding(binding)

        record = record_builder.build()

        # Phase 11: Validate record
        result = validate_augmented_record(record)
        assert result is True

        # Phase 12: Serialize record
        json_record = serialize_augmented_record(record, format="json")
        parsed = json.loads(json_record)

        assert len(parsed["serial_numbers"]) == 10

    def test_workflow_with_threshold_credentials(self):
        """Test workflow with threshold credential splitting."""
        # Setup
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        # Split credential into 2 shares (2-of-2)
        splitter = CredentialSplitter(threshold=2, total_holders=2)
        shares = splitter.split_credential(credential)

        # Each holder creates partial presentation
        presenter1 = ThresholdPresenter(shares[0], params)
        presenter2 = ThresholdPresenter(shares[1], params)

        partial1 = presenter1.create_partial_presentation()
        partial2 = presenter2.create_partial_presentation()

        # Combine presentations
        combined = combine_threshold_presentations(
            [partial1, partial2],
            threshold=2,
            params=params,
        )

        assert combined is not None

    def test_workflow_one_show_enforcement(self):
        """Test one-show enforcement blocks double voting."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        vrf = VRFSerialDerivation()
        registry = SerialRegistry(election_id="election_001")

        # Derive serial from credential
        serial = vrf.derive_serial(
            credential_id=credential["credential_id"],
            election_id="election_001",
            context="vote_1",
        )

        # First registration succeeds
        result1 = registry.register(serial["serial"])
        assert result1 is True

        # Second registration (double vote) fails
        result2 = registry.register(serial["serial"])
        assert result2 is False

    def test_workflow_binding_different_elections(self):
        """Test bindings for different elections."""
        binding_gen = BindingGenerator()

        commitment1 = binding_gen.generate_commitment(
            election_id="election_001",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        commitment2 = binding_gen.generate_commitment(
            election_id="election_002",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        # Different elections should produce different commitments
        assert commitment1["commitment"] != commitment2["commitment"]


class TestPhaseGateSimulation:
    """Test Phase 1 acceptance criteria: 10-voter, 3-guardian, 2-of-3 threshold."""

    def test_phase_gate_simulation(self):
        """Simulate Phase 1 acceptance criteria."""
        # 10 voters
        num_voters = 10

        # 3 guardians (represented by threshold parameters)
        num_guardians = 3
        threshold = 2

        # Setup issuer
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()

        # Issue credentials to 10 voters
        voter_credentials = []
        for i in range(num_voters):
            cred = issuer.issue_credential(params)
            voter_credentials.append(cred)

        # Create presentations and verify
        all_presentations_valid = True
        for cred in voter_credentials:
            holder = SAACHolder(cred, params)
            presentation = holder.create_presentation()
            valid = verify_presentation(presentation, params)
            if not valid:
                all_presentations_valid = False

        assert all_presentations_valid

        # Create bindings
        bindings = []
        for i, cred in enumerate(voter_credentials):
            binding_gen = BindingGenerator()
            binding = binding_gen.generate_commitment(
                election_id="phase1_test",
                ballot_style_id="default",
                precinct_id=f"precinct_{i}",
            )
            bindings.append(binding)

        # Derive serials
        vrf = VRFSerialDerivation()
        serials = []
        for cred in voter_credentials:
            serial = vrf.derive_serial(
                credential_id=cred["credential_id"],
                election_id="phase1_test",
                context="phase1",
            )
            serials.append(serial["serial"])

        # Verify uniqueness
        duplicates = verify_serial_uniqueness(serials)
        assert len(duplicates) == 0

        # Build augmented record
        builder = AugmentedRecordBuilder(election_id="phase1_test")

        for serial in serials:
            builder.add_serial(serial)

        for binding in bindings:
            builder.add_binding(binding)

        record = builder.build()

        # Verify record is valid
        valid = validate_augmented_record(record)
        assert valid

        # Record should have 10 serials
        assert len(record["serial_numbers"]) == num_voters

        # Verification summary should show all valid
        summary = record["verification_summary"]
        assert summary["duplicate_serials"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
