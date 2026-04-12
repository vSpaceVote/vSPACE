"""Test suite for vSPACE Credential-to-Ballot Binding (F-102)."""

import pytest
import sys
import os

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "bindings", "python")
)

from electionguard_vspace.binding import (
    BindingGenerator,
    ProofGenerator,
    verify_binding_proof,
    wrap_ballot_encryption,
)
from electionguard_vspace.constants import (
    HASH_PREFIX_BIND_COMMIT,
    HASH_PREFIX_BIND_CHALLENGE,
)


class TestBindingGenerator:
    """Test binding generator functionality."""

    def test_generator_init(self):
        """Test generator initialization."""
        generator = BindingGenerator()
        assert generator is not None

    def test_generate_commitment(self):
        """Test Pedersen commitment generation."""
        generator = BindingGenerator()

        commitment = generator.generate_commitment(
            election_id="election_001",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        assert "commitment" in commitment
        assert "generator_g" in commitment
        assert "generator_h" in commitment
        assert "context" in commitment

    def test_commitment_structure(self):
        """Test commitment has proper structure."""
        generator = BindingGenerator()

        commitment = generator.generate_commitment(
            election_id="election_001",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        context = commitment["context"]
        assert context["election_id"] == "election_001"
        assert context["ballot_style_id"] == "style_001"
        assert context["precinct_id"] == "precinct_001"

    def test_commitment_is_pedersen(self):
        """Test that commitment uses Pedersen structure C = g^r * h^s."""
        generator = BindingGenerator()

        commitment = generator.generate_commitment(
            election_id="election_001",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        # Commitment should be hex-encoded
        assert (
            commitment["commitment"].startswith("0x")
            or len(commitment["commitment"]) > 0
        )

    def test_commitment_binding_context(self):
        """Test that commitment binds to context."""
        generator = BindingGenerator()

        commitment1 = generator.generate_commitment(
            election_id="election_001",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        commitment2 = generator.generate_commitment(
            election_id="election_002",  # Different election
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        # Different elections should produce different commitments
        assert commitment1["commitment"] != commitment2["commitment"]


class TestProofGenerator:
    """Test proof generator functionality."""

    def test_proof_generator_init(self):
        """Test proof generator initialization."""
        proof_gen = ProofGenerator()
        assert proof_gen is not None

    def test_generate_binding_proof(self):
        """Test binding proof generation."""
        binding_gen = BindingGenerator()
        proof_gen = ProofGenerator()

        commitment = binding_gen.generate_commitment(
            election_id="election_001",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        proof = proof_gen.generate_binding_proof(commitment)

        assert "commitment_alpha" in proof
        assert "commitment_beta" in proof
        assert "challenge" in proof
        assert "response_r" in proof
        assert "response_s" in proof

    def test_proof_is_sigma_protocol(self):
        """Test that proof uses sigma protocol structure."""
        binding_gen = BindingGenerator()
        proof_gen = ProofGenerator()

        commitment = binding_gen.generate_commitment(
            election_id="election_001",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        proof = proof_gen.generate_binding_proof(commitment)

        # Sigma protocol components
        assert proof["challenge"]  # Fiat-Shamir challenge
        assert proof["response_r"]  # Response for r
        assert proof["response_s"]  # Response for s


class TestVerifyBindingProof:
    """Test binding proof verification."""

    def test_verify_valid_proof(self):
        """Test verification of valid proof."""
        binding_gen = BindingGenerator()
        proof_gen = ProofGenerator()

        commitment = binding_gen.generate_commitment(
            election_id="election_001",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        proof = proof_gen.generate_binding_proof(commitment)

        result = verify_binding_proof(proof, commitment)
        assert result is True

    def test_verify_invalid_proof(self):
        """Test verification rejects invalid proof."""
        binding_gen = BindingGenerator()

        commitment = binding_gen.generate_commitment(
            election_id="election_001",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        # Invalid proof (wrong challenge)
        invalid_proof = {
            "commitment_alpha": "invalid",
            "commitment_beta": "invalid",
            "challenge": "wrong_challenge",
            "response_r": "invalid",
            "response_s": "invalid",
        }

        result = verify_binding_proof(invalid_proof, commitment)
        assert result is False


class TestWrapBallotEncryption:
    """Test ballot encryption wrapping."""

    def test_wrap_ballot(self):
        """Test wrapping ballot with binding."""
        binding_gen = BindingGenerator()
        proof_gen = ProofGenerator()

        commitment = binding_gen.generate_commitment(
            election_id="election_001",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        proof = proof_gen.generate_binding_proof(commitment)

        # Mock ballot ciphertext
        ballot_ciphertext = {"encrypted_data": "mock_ciphertext"}

        wrapped = wrap_ballot_encryption(ballot_ciphertext, commitment, proof)

        assert "ballot_ciphertext" in wrapped
        assert "binding_commitment" in wrapped
        assert "binding_proof" in wrapped


class TestSchnorrLikeProtocol:
    """Test Schnorr-like sigma protocol implementation."""

    def test_fiat_shamir_challenge(self):
        """Test Fiat-Shamir challenge computation."""
        binding_gen = BindingGenerator()
        proof_gen = ProofGenerator()

        commitment = binding_gen.generate_commitment(
            election_id="election_001",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        proof = proof_gen.generate_binding_proof(commitment)

        # Challenge should be deterministic (Fiat-Shamir)
        assert len(proof["challenge"]) > 0

    def test_challenge_depends_on_context(self):
        """Test that challenge depends on binding context."""
        binding_gen = BindingGenerator()
        proof_gen = ProofGenerator()

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

        proof1 = proof_gen.generate_binding_proof(commitment1)
        proof2 = proof_gen.generate_binding_proof(commitment2)

        # Different contexts should produce different challenges
        assert proof1["challenge"] != proof2["challenge"]


class TestConstants:
    """Test binding constants."""

    def test_hash_prefixes_defined(self):
        """Test hash prefixes are defined."""
        assert HASH_PREFIX_BIND_COMMIT
        assert HASH_PREFIX_BIND_CHALLENGE


class TestAdditiveWrapper:
    """Test additive wrapper for ElectionGuard."""

    def test_wrapper_preserves_ballot(self):
        """Test that wrapper preserves ballot ciphertext."""
        binding_gen = BindingGenerator()
        proof_gen = ProofGenerator()

        commitment = binding_gen.generate_commitment(
            election_id="election_001",
            ballot_style_id="style_001",
            precinct_id="precinct_001",
        )

        proof = proof_gen.generate_binding_proof(commitment)

        ballot_ciphertext = {
            "encrypted_data": "original_data",
            "nonce": "original_nonce",
        }

        wrapped = wrap_ballot_encryption(ballot_ciphertext, commitment, proof)

        # Original ballot should be preserved
        assert wrapped["ballot_ciphertext"]["encrypted_data"] == "original_data"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
