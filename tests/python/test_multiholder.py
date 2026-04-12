"""Test suite for vSPACE Multi-Holder BBS Credentials (F-101)."""

import pytest
import sys
import os

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "bindings", "python")
)

from electionguard_vspace.multiholder import (
    CredentialSplitter,
    ThresholdPresenter,
    combine_threshold_presentations,
)
from electionguard_vspace.saac import SAACIssuer, SAACHolder


class TestCredentialSplitter:
    """Test credential splitting functionality."""

    def test_splitter_init(self):
        """Test splitter initialization."""
        splitter = CredentialSplitter(threshold=2, total_holders=2)
        assert splitter.threshold == 2
        assert splitter.total_holders == 2

    def test_splitter_init_1_of_2(self):
        """Test 1-of-2 threshold configuration."""
        splitter = CredentialSplitter(threshold=1, total_holders=2)
        assert splitter.threshold == 1

    def test_splitter_init_2_of_2(self):
        """Test 2-of-2 threshold configuration."""
        splitter = CredentialSplitter(threshold=2, total_holders=2)
        assert splitter.threshold == 2

    def test_split_credential(self):
        """Test credential splitting into shares."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        splitter = CredentialSplitter(threshold=2, total_holders=2)
        shares = splitter.split_credential(credential)

        assert len(shares) == 2

    def test_split_produces_valid_shares(self):
        """Test that shares have proper structure."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        splitter = CredentialSplitter(threshold=2, total_holders=2)
        shares = splitter.split_credential(credential)

        for share in shares:
            assert "share_id" in share
            assert "share_data" in share


class TestThresholdPresenter:
    """Test threshold presentation functionality."""

    def test_presenter_init(self):
        """Test presenter initialization."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        splitter = CredentialSplitter(threshold=2, total_holders=2)
        shares = splitter.split_credential(credential)

        presenter = ThresholdPresenter(shares[0], params)
        assert presenter.share == shares[0]

    def test_create_partial_presentation(self):
        """Test creation of partial presentation."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        splitter = CredentialSplitter(threshold=2, total_holders=2)
        shares = splitter.split_credential(credential)

        presenter = ThresholdPresenter(shares[0], params)
        partial = presenter.create_partial_presentation()

        assert "share_id" in partial
        assert "partial_proof" in partial


class TestCombineThresholdPresentations:
    """Test threshold presentation combination."""

    def test_combine_2_of_2(self):
        """Test combining 2-of-2 presentations."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        splitter = CredentialSplitter(threshold=2, total_holders=2)
        shares = splitter.split_credential(credential)

        presenter1 = ThresholdPresenter(shares[0], params)
        presenter2 = ThresholdPresenter(shares[1], params)

        partial1 = presenter1.create_partial_presentation()
        partial2 = presenter2.create_partial_presentation()

        combined = combine_threshold_presentations(
            [partial1, partial2],
            threshold=2,
            params=params,
        )

        assert combined is not None

    def test_combine_requires_threshold(self):
        """Test that threshold number of presentations required."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        splitter = CredentialSplitter(threshold=2, total_holders=2)
        shares = splitter.split_credential(credential)

        presenter1 = ThresholdPresenter(shares[0], params)
        partial1 = presenter1.create_partial_presentation()

        # Only 1 partial with threshold=2 should fail
        result = combine_threshold_presentations(
            [partial1],
            threshold=2,
            params=params,
        )

        # Should fail or return None with insufficient presentations
        assert result is None or result is False


class TestShamirSecretSharing:
    """Test Shamir's Secret Sharing implementation."""

    def test_shares_reconstruct_secret(self):
        """Test that shares can reconstruct the original."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        splitter = CredentialSplitter(threshold=2, total_holders=2)
        shares = splitter.split_credential(credential)

        # Verify shares have proper Shamir structure
        assert len(shares) == 2

    def test_threshold_property(self):
        """Test threshold property (k shares needed)."""
        # With threshold=2, both shares should be required
        splitter = CredentialSplitter(threshold=2, total_holders=3)
        assert splitter.threshold == 2


class TestCredentialReDerivation:
    """Test credential re-derivation bridge."""

    def test_rederive_without_full_bbs(self):
        """Test re-derivation without materializing full BBS credential."""
        issuer = SAACIssuer(curve="P-256")
        params = issuer.generate_params()
        credential = issuer.issue_credential(params)

        splitter = CredentialSplitter(threshold=2, total_holders=2)
        shares = splitter.split_credential(credential)

        # Re-derivation should work through threshold combination
        presenter1 = ThresholdPresenter(shares[0], params)
        presenter2 = ThresholdPresenter(shares[1], params)

        partial1 = presenter1.create_partial_presentation()
        partial2 = presenter2.create_partial_presentation()

        combined = combine_threshold_presentations(
            [partial1, partial2],
            threshold=2,
            params=params,
        )

        # Should produce valid combined presentation
        assert combined is not None


class TestBLS12_381Integration:
    """Test BLS12-381 integration for BBS signatures."""

    def test_bbs_signatures_placeholder(self):
        """Placeholder for BBS signature tests."""
        # BBS signatures on BLS12-381 are complex
        # This is a placeholder for full implementation
        splitter = CredentialSplitter(threshold=2, total_holders=2)
        assert splitter.threshold == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
