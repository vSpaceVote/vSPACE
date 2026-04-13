"""
vSPACE Mock Data Generators
============================

Generates realistic mock data for E2E PoC demonstrations.

Includes:
- Election manifests with contests and candidates
- Voter profiles with eligibility attributes
- Ballot selections
- Entra VC mock responses
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any


class MockElectionGenerator:
    """Generate mock election manifests and ballots."""

    def __init__(self):
        self.sample_contests = [
            {
                "contest_id": "pres-2026",
                "contest_type": "President",
                "selections_limit": 1,
                "candidates": [
                    {"candidate_id": "pres-cand-1", "name": "Alice Johnson"},
                    {"candidate_id": "pres-cand-2", "name": "Bob Smith"},
                    {"candidate_id": "pres-cand-3", "name": "Carol Williams"},
                ],
            },
            {
                "contest_id": "senate-2026",
                "contest_type": "Senate",
                "selections_limit": 2,
                "candidates": [
                    {"candidate_id": "sen-cand-1", "name": "David Brown"},
                    {"candidate_id": "sen-cand-2", "name": "Eva Davis"},
                    {"candidate_id": "sen-cand-3", "name": "Frank Miller"},
                    {"candidate_id": "sen-cand-4", "name": "Grace Wilson"},
                ],
            },
            {
                "contest_id": "prop-2026-a",
                "contest_type": "Proposition",
                "selections_limit": 1,
                "candidates": [
                    {"candidate_id": "prop-a-yes", "name": "Yes"},
                    {"candidate_id": "prop-a-no", "name": "No"},
                ],
            },
        ]

    def generate_manifest(self, election_id: str = None) -> Dict[str, Any]:
        """Generate a complete election manifest."""
        if election_id is None:
            election_id = f"election-{uuid.uuid4().hex[:12]}"

        manifest = {
            "election_id": election_id,
            "manifest_hash": self._generate_hash(election_id),
            "election_name": "2026 General Election",
            "start_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "end_date": (datetime.now() + timedelta(days=31)).isoformat(),
            "geopolitical_units": [
                {
                    "gp_unit_id": "state-01",
                    "name": "State of California",
                    "type": "state",
                },
                {
                    "gp_unit_id": "county-001",
                    "name": "San Francisco County",
                    "type": "county",
                },
            ],
            "parties": [
                {"party_id": "party-dem", "name": "Democratic Party"},
                {"party_id": "party-rep", "name": "Republican Party"},
                {"party_id": "party-ind", "name": "Independent"},
            ],
            "contests": self.sample_contests,
            "ballot_styles": [
                {
                    "ballot_style_id": "style-001",
                    "gp_unit_ids": ["state-01", "county-001"],
                    "party_id": "party-dem",
                }
            ],
            "vspace_metadata": {
                "saac_required": True,
                "multi_holder_threshold": 2,
                "multi_holder_total": 2,
            },
        }

        return manifest

    def generate_ballot(self, voter_id: str) -> Dict[str, Any]:
        """Generate a mock encrypted ballot for a voter."""
        ballot_id = f"ballot-{uuid.uuid4().hex[:12]}"
        encryption_nonce = secrets.token_hex(32)

        # Generate random selections
        selections = []
        for contest in self.sample_contests:
            num_selections = min(
                contest["selections_limit"], len(contest["candidates"])
            )
            selected = secrets.SystemRandom().sample(
                contest["candidates"], k=num_selections
            )
            for candidate in selected:
                selections.append(
                    {
                        "contest_id": contest["contest_id"],
                        "candidate_id": candidate["candidate_id"],
                        "encrypted_vote": f"enc_{secrets.token_hex(16)}",
                    }
                )

        ballot = {
            "ballot_id": ballot_id,
            "voter_id": voter_id,
            "ballot_style_id": "style-001",
            "encryption_nonce": encryption_nonce,
            "encrypted_contests": selections,
            "ballot_code": self._generate_ballot_code(ballot_id, encryption_nonce),
            "state": "encrypted",
            "created_at": datetime.utcnow().isoformat(),
        }

        return ballot

    def _generate_hash(self, data: str) -> str:
        """Generate SHA-256 hash of data."""
        return hashlib.sha256(data.encode()).hexdigest()

    def _generate_ballot_code(self, ballot_id: str, nonce: str) -> str:
        """Generate deterministic ballot code."""
        combined = f"{ballot_id}:{nonce}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]


class MockVoterGenerator:
    """Generate mock voter profiles and credentials."""

    def __init__(self):
        self.first_names = [
            "James",
            "Mary",
            "John",
            "Patricia",
            "Robert",
            "Jennifer",
            "Michael",
            "Linda",
            "William",
            "Elizabeth",
            "David",
            "Barbara",
            "Richard",
            "Susan",
            "Joseph",
            "Jessica",
            "Thomas",
            "Sarah",
            "Charles",
            "Karen",
        ]
        self.last_names = [
            "Smith",
            "Johnson",
            "Williams",
            "Brown",
            "Jones",
            "Garcia",
            "Miller",
            "Davis",
            "Rodriguez",
            "Martinez",
            "Hernandez",
            "Lopez",
            "Gonzalez",
            "Wilson",
            "Anderson",
            "Thomas",
            "Taylor",
            "Moore",
            "Jackson",
            "Martin",
        ]

    def generate_voters(self, count: int) -> List[Dict[str, Any]]:
        """Generate a list of mock voter profiles."""
        voters = []

        for i in range(count):
            first_name = secrets.SystemRandom().choice(self.first_names)
            last_name = secrets.SystemRandom().choice(self.last_names)
            voter_id = f"voter-{uuid.uuid4().hex[:8]}"

            voter = {
                "voter_id": voter_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": f"{first_name.lower()}.{last_name.lower()}@example.com",
                "precinct": f"precinct-{(i % 10) + 1:03d}",
                "district": f"district-{(i % 5) + 1}",
                "eligibility": {
                    "citizen": True,
                    "age_verified": True,
                    "registered": True,
                    "registration_date": (
                        datetime.now() - timedelta(days=secrets.randbelow(365))
                    ).isoformat(),
                },
                "device_info": {
                    "primary_device": f"device-{uuid.uuid4().hex[:8]}",
                    "backup_device": f"device-{uuid.uuid4().hex[:8]}",
                },
            }

            voters.append(voter)

        return voters

    def generate_entra_vc(
        self, voter: Dict[str, Any], election_id: str
    ) -> Dict[str, Any]:
        """
        Generate a mock Entra Verified ID credential.

        In production, this would be issued by Microsoft Entra Verified ID service.
        """
        vc_id = f"vc-{uuid.uuid4().hex[:12]}"
        issuance_date = datetime.utcnow()
        expiration_date = issuance_date + timedelta(days=365)

        # Blinded commitment for oblivious credential derivation
        blinded_commitment = secrets.token_hex(32)

        vc = {
            "id": vc_id,
            "type": ["VerifiableCredential", "VoterEligibilityCredential"],
            "issuer": "did:web:vspacevote.com",
            "issuance_date": issuance_date.isoformat(),
            "expiration_date": expiration_date.isoformat(),
            "credential_subject": {
                "voter_id": voter["voter_id"],
                "election_id": election_id,
                "precinct": voter["precinct"],
                "blinded_commitment": blinded_commitment,
            },
            "proof": {
                "type": "Ed25519Signature2018",
                "created": issuance_date.isoformat(),
                "verification_method": "did:web:vspacevote.com#keys-1",
                "proof_purpose": "assertionMethod",
                "proof_value": f"mock_proof_{secrets.token_hex(64)}",
            },
        }

        return vc


class MockNLWebGenerator:
    """Generate mock NLWeb query responses."""

    def __init__(self):
        self.query_templates = {
            "ballot_count": "Based on the published election record, {count} ballots were cast in this election.",
            "contest_results": "Contest '{contest}' results: {results}",
            "serial_verification": "All {count} serial numbers in the election record are unique. No duplicate voting detected.",
            "voter_eligibility": "Voter eligibility was verified through Microsoft Entra Verified ID credentials.",
            "credential_status": "Anonymous credentials were derived using the SAAC protocol with 2-of-2 multi-holder threshold.",
        }

    def generate_response(self, query: str, election_data: Dict[str, Any]) -> str:
        """Generate a mock NLWeb response grounded in election data."""
        query_lower = query.lower()

        if "how many" in query_lower and "ballot" in query_lower:
            count = election_data.get("ballots_cast", 0)
            return self.query_templates["ballot_count"].format(count=count)

        elif "result" in query_lower or "contest" in query_lower:
            contest = "President"
            results = (
                "Alice Johnson: 4 votes, Bob Smith: 3 votes, Carol Williams: 3 votes"
            )
            return self.query_templates["contest_results"].format(
                contest=contest, results=results
            )

        elif "serial" in query_lower and "unique" in query_lower:
            count = election_data.get("serial_numbers_registered", 0)
            return self.query_templates["serial_verification"].format(count=count)

        elif "eligibility" in query_lower:
            return self.query_templates["voter_eligibility"]

        elif "credential" in query_lower:
            return self.query_templates["credential_status"]

        else:
            return "I found relevant information in the election record. Please refine your query for more specific results."
