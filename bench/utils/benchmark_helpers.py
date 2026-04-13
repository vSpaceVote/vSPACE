"""
vSPACE Benchmark Utilities
===========================

Helper modules for benchmark execution.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
import secrets
import hashlib
from datetime import datetime


@dataclass
class BenchmarkResult:
    """Single benchmark result."""

    name: str
    feature_id: str
    status: str  # "passed", "failed", "skipped"
    duration_ms: float
    metrics: Dict[str, Any]
    errors: List[str]
    warnings: List[str]


def mock_voter(voter_id: str) -> Dict[str, Any]:
    """Generate mock voter profile."""
    return {
        "voter_id": voter_id,
        "first_name": "Test",
        "last_name": "Voter",
        "email": f"{voter_id}@example.com",
        "precinct": f"precinct-{secrets.token_hex(4)}",
        "eligibility": {"citizen": True, "age_verified": True, "registered": True},
    }


def mock_ballot(voter_id: str) -> Dict[str, Any]:
    """Generate mock encrypted ballot."""
    return {
        "ballot_id": f"ballot-{secrets.token_hex(8)}",
        "voter_id": voter_id,
        "encryption_nonce": secrets.token_hex(32),
        "encrypted_contests": [
            {
                "contest_id": "pres-2026",
                "candidate_id": "cand-1",
                "encrypted_vote": f"enc_{secrets.token_hex(16)}",
            }
        ],
        "ballot_code": hashlib.sha256(
            f"{voter_id}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:32],
        "state": "encrypted",
    }


def mock_credential(voter_id: str) -> Dict[str, Any]:
    """Generate mock SAAC credential."""
    return {
        "credential_id": f"cred-{secrets.token_hex(8)}",
        "credential_key": secrets.token_hex(32),
        "attributes": {"voter_id": voter_id, "election_id": "election-2026"},
        "issuer_params": {"public_key": "mock_pubkey", "curve": "P-256"},
    }


def mock_entra_vc(voter: Dict[str, Any], election_id: str) -> Dict[str, Any]:
    """Generate mock Entra Verified ID credential."""
    return {
        "id": f"vc-{secrets.token_hex(8)}",
        "type": ["VerifiableCredential", "VoterEligibilityCredential"],
        "issuer": "did:web:vspacevote.com",
        "issuance_date": datetime.utcnow().isoformat(),
        "credential_subject": {
            "voter_id": voter["voter_id"],
            "election_id": election_id,
            "precinct": voter["precinct"],
            "blinded_commitment": secrets.token_hex(32),
        },
        "proof": {
            "type": "Ed25519Signature2018",
            "proof_value": f"mock_proof_{secrets.token_hex(64)}",
        },
    }


def mock_nlweb_response(query: str) -> Dict[str, Any]:
    """Generate mock NLWeb response."""
    return {
        "query": query,
        "response": f"Mock response to: {query}",
        "schema_org_type": "Answer",
        "provenance_hash": hashlib.sha256(
            f"{query}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest(),
        "grounded": True,
    }
