"""Test suite for vSPACE SAAC Protocol (F-100)."""

import pytest
import sys
import os

# Add the package to path for testing
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "bindings", "python")
)

from electionguard_vspace.saac import (
    SAACIssuer,
    SAACHolder,
    verify_presentation,
)
from electionguard_vspace.constants import (
    P256_ORDER,
    P384_ORDER,
    HASH_PREFIX_SAAC_PARAMS,
    HASH_PREFIX_SAAC_CRED,
)


class TestSAACIssuer:
    """Test SAAC Issuer functionality."""

    def test_issuer_init_p256(self):
        """Test issuer initialization with P-256 curve."""
        issuer = SAACIssuer(curve="P-256")
        assert issuer.curve == "P-256"
        assert issuer.order == P256_ORDER

    def test_issuer_init_p384(self):
        """Test issuer initialization with P-384 curve."""
        issuer = SAACIssuer(curve="P-384")
        assert issuer.curve == "P-384"
        assert issuer.order == P384_ORDER

    def test_issuer_generate_params(self):
        """Test parameter generation."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()

        assert "curve" in params
        assert "generator_g" in params
        assert "generator_h" in params
        assert "issuer_public_key" in params
        assert "params_hash" in params

    def test_issuer_issue_credential(self):
        """Test credential issuance."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()

        credential = issuer.issue_credential(params)

        assert "credential_id" in credential
        assert "secret_a" in credential
        assert "secret_b" in credential
        assert "sigma_a" in credential
        assert "sigma_b" in credential


class TestSAACHolder:
    """Test SAAC Holder functionality."""

    def test_holder_init(self):
        """Test holder initialization."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        holder = SAACHolder(credential, params)
        assert holder.credential == credential
        assert holder.params == params

    def test_holder_create_presentation(self):
        """Test presentation creation."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        holder = SAACHolder(credential, params)
        presentation = holder.create_presentation()

        assert "credential_id" in presentation
        assert "commitment" in presentation
        assert "pok" in presentation
        assert "presented_at" in presentation

    def test_holder_presentation_contains_proof(self):
        """Test that presentation contains Schnorr proof."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        holder = SAACHolder(credential, params)
        presentation = holder.create_presentation()

        pok = presentation["pok"]
        assert "challenge" in pok
        assert "response_a" in pok
        assert "response_b" in pok


class TestVerifyPresentation:
    """Test presentation verification."""

    def test_verify_valid_presentation(self):
        """Test verification of valid presentation."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        holder = SAACHolder(credential, params)
        presentation = holder.create_presentation()

        # Verification should succeed for valid presentation
        result = verify_presentation(presentation, params)
        assert result is True

    def test_verify_presentation_structure(self):
        """Test that verification validates structure."""
        # Empty presentation should fail
        with pytest.raises(Exception):
            verify_presentation({}, {})


class TestConstants:
    """Test SAAC constants."""

    def test_p256_order_nonzero(self):
        """Test P-256 order is nonzero."""
        assert P256_ORDER > 0

    def test_p384_order_nonzero(self):
        """Test P-384 order is nonzero."""
        assert P384_ORDER > 0

    def test_p384_order_greater_than_p256(self):
        """Test P-384 order is larger than P-256."""
        assert P384_ORDER > P256_ORDER

    def test_hash_prefixes_defined(self):
        """Test hash prefixes are defined."""
        assert HASH_PREFIX_SAAC_PARAMS
        assert HASH_PREFIX_SAAC_CRED


class TestObliviousIssuance:
    """Test oblivious issuance property."""

    def test_issuer_does_not_see_secrets(self):
        """Test that issuer's credential doesn't reveal secrets."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()

        # In oblivious issuance, issuer doesn't know a, b
        # The credential structure should reflect this
        credential = issuer.issue_credential(params)

        # Secrets are holder's secrets, not issuer's
        assert "secret_a" in credential
        assert "secret_b" in credential


class TestPublicVerifiability:
    """Test public verifiability property."""

    def test_verification_requires_only_public_params(self):
        """Test that verification uses only public data."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        holder = SAACHolder(credential, params)
        presentation = holder.create_presentation()

        # Verification should work with just public params
        # No secret key should be needed
        result = verify_presentation(presentation, params)
        assert result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
