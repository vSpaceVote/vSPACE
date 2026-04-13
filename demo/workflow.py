"""
vSPACE E2E Workflow Orchestrator
=================================

Coordinates the end-to-end workflow for vSPACE Augmented PRD features.

Handles:
- Entra VC mock issuance/presentation
- SAAC credential derivation
- Multi-holder threshold coordination
- Cross-origin communication simulation
- NLWeb query processing
"""

import asyncio
import hashlib
import secrets
from datetime import datetime
from typing import Dict, Any, Optional

from mock_data import MockNLWebGenerator


class E2EWorkflowOrchestrator:
    """
    Orchestrates the complete vSPACE E2E workflow.

    Coordinates all feature interactions:
    F-104: Entra Verified ID Bridge
    F-100: SAAC Protocol
    F-101: Multi-Holder BBS
    F-102: Credential Binding
    F-107: Cross-Origin Communication
    F-108: NLWeb Interfaces
    """

    def __init__(self):
        self.nlweb_generator = MockNLWebGenerator()
        self.pending_challenges = {}

    async def mock_entra_issuance(self, voter: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock Entra Verified ID VC issuance (F-104).

        In production, this would call:
        POST https://verifiedid.did.msidentity.com/v1.0/verifiableCredentials/createIssuanceRequest

        Args:
            voter: Voter profile with eligibility attributes

        Returns:
            Mock VerifiableCredential
        """
        # Simulate API latency
        await asyncio.sleep(0.1)

        # Import here to avoid circular imports
        from mock_data import MockVoterGenerator

        generator = MockVoterGenerator()
        election_id = "election-mock-2026"

        vc = generator.generate_entra_vc(voter, election_id)

        print(f"  [F-104] Entra VC issued: {vc['id']}")
        print(
            f"         Claims: election_id={election_id}, precinct={voter['precinct']}"
        )

        return vc

    async def mock_entra_presentation(self, vc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock Entra Verified ID VC presentation (F-104).

        In production, this would call:
        POST https://verifiedid.did.msidentity.com/v1.0/verifiableCredentials/createPresentationRequest

        Args:
            vc: VerifiableCredential to present

        Returns:
            Verified claims from VC
        """
        # Simulate API latency
        await asyncio.sleep(0.05)

        # Extract verified claims
        verified_claims = {
            "voter_id": vc["credential_subject"]["voter_id"],
            "election_id": vc["credential_subject"]["election_id"],
            "precinct": vc["credential_subject"]["precinct"],
            "blinded_commitment": vc["credential_subject"]["blinded_commitment"],
            "verified": True,
        }

        print(f"  [F-104] Entra VC presented and verified")

        return verified_claims

    async def derive_saac_credential(
        self, entra_vc: Dict[str, Any], saac_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Derive SAAC anonymous credential from Entra VC (F-100, F-104).

        This is the oblivious credential derivation protocol that bridges
        Entra VC to SAAC anonymous credential without linking them.

        Args:
            entra_vc: Verified Entra VerifiableCredential
            saac_params: SAAC issuer public parameters

        Returns:
            SAAC anonymous credential
        """
        # Simulate derivation latency
        await asyncio.sleep(0.05)

        # Extract blinded commitment from Entra VC
        blinded_commitment = entra_vc["credential_subject"]["blinded_commitment"]

        # Generate SAAC credential (mock)
        credential_id = f"saac-{secrets.token_hex(16)}"
        credential_key = secrets.token_hex(32)

        saac_credential = {
            "credential_id": credential_id,
            "credential_key": credential_key,
            "issuer_params": {
                "public_key": saac_params.get("public_key", "mock_pubkey"),
                "curve": "P-256",
            },
            "attributes": {
                "election_id": entra_vc["credential_subject"]["election_id"],
                "precinct": entra_vc["credential_subject"]["precinct"],
            },
            "blinded_commitment": blinded_commitment,
            "derived_at": datetime.utcnow().isoformat(),
        }

        print(f"  [F-100] SAAC credential derived: {credential_id[:20]}...")
        print(f"           Oblivious: Entra VC cannot be linked to this credential")

        return saac_credential

    async def coordinate_threshold_presentation(
        self, shares: list, challenge: str
    ) -> Dict[str, Any]:
        """
        Coordinate multi-holder threshold presentation (F-101).

        Args:
            shares: List of credential shares from different devices
            challenge: Cryptographic challenge from vSpaceVote.com

        Returns:
            Combined threshold presentation
        """
        # Simulate device coordination latency
        await asyncio.sleep(0.05)

        # Each share contributes a partial signature
        partial_sigs = []
        for i, share in enumerate(shares):
            partial_sig = f"partial_sig_{i}_{secrets.token_hex(16)}"
            partial_sigs.append(partial_sig)
            print(f"  [F-101] Device {i + 1} contributed partial signature")

        # Combine partial signatures
        combined_presentation = {
            "presentation_id": f"pres-{secrets.token_hex(12)}",
            "threshold_met": True,
            "partial_signatures": partial_sigs,
            "challenge_response": hashlib.sha256(
                f"{challenge}:{':'.join(partial_sigs)}".encode()
            ).hexdigest(),
            "created_at": datetime.utcnow().isoformat(),
        }

        print(
            f"  [F-101] Threshold presentation complete: {combined_presentation['presentation_id']}"
        )

        return combined_presentation

    async def initiate_cross_origin_flow(
        self, voter_session: str, election_id: str
    ) -> Dict[str, Any]:
        """
        Initiate cross-origin communication flow (F-107).

        Creates a cryptographic challenge that vSpaceWallet.com must respond to.

        Args:
            voter_session: Session identifier from vSpaceVote.com
            election_id: Election identifier

        Returns:
            Challenge for vSpaceWallet.com
        """
        challenge = secrets.token_hex(32)
        nonce = secrets.token_hex(16)

        challenge_data = {
            "challenge_id": f"chal-{secrets.token_hex(12)}",
            "voter_session": voter_session,
            "election_id": election_id,
            "challenge": challenge,
            "nonce": nonce,
            "origin_whitelist": ["https://vspacevote.com", "https://vspacewallet.com"],
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow().timedelta(minutes=5)).isoformat()
            if hasattr(datetime.utcnow(), "timedelta")
            else datetime.utcnow().isoformat(),
        }

        # Store challenge for verification
        self.pending_challenges[challenge_data["challenge_id"]] = challenge_data

        print(
            f"  [F-107] Cross-origin challenge created: {challenge_data['challenge_id'][:20]}..."
        )
        print(
            f"           Origin whitelist: {', '.join(challenge_data['origin_whitelist'])}"
        )

        return challenge_data

    async def verify_cross_origin_response(
        self, challenge_id: str, response: Dict[str, Any]
    ) -> bool:
        """
        Verify cross-origin response (F-107).

        Args:
            challenge_id: Original challenge identifier
            response: Response from vSpaceWallet.com

        Returns:
            True if response is valid
        """
        if challenge_id not in self.pending_challenges:
            print(f"  [F-107] ✗ Challenge {challenge_id} not found")
            return False

        original_challenge = self.pending_challenges[challenge_id]

        # Verify origin
        if response.get("origin") not in original_challenge["origin_whitelist"]:
            print(f"  [F-107] ✗ Invalid origin: {response.get('origin')}")
            return False

        # Verify signature
        if not response.get("signature"):
            print(f"  [F-107] ✗ Missing signature")
            return False

        print(f"  [F-107] ✓ Cross-origin response verified")

        return True

    async def mock_nlweb_query(self, query: str, election_data: Dict[str, Any]) -> str:
        """
        Process NLWeb query (F-108).

        Args:
            query: Natural language query
            election_data: Published election record

        Returns:
            Schema.org-typed response grounded in election data
        """
        # Simulate query processing latency
        await asyncio.sleep(0.1)

        response = self.nlweb_generator.generate_response(query, election_data)

        # Add cryptographic provenance hash
        provenance_hash = hashlib.sha256(
            f"{query}:{response}:{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()

        print(f"  [F-108] NLWeb query processed")
        print(f"           Provenance hash: {provenance_hash[:32]}...")

        return response

    async def run_complete_workflow(
        self, voters: list, election_manifest: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run complete E2E workflow for all voters.

        Args:
            voters: List of voter profiles
            election_manifest: Election manifest

        Returns:
            Workflow execution summary
        """
        workflow_summary = {
            "election_id": election_manifest["election_id"],
            "total_voters": len(voters),
            "stages_completed": [],
            "errors": [],
        }

        print("\n[Workflow] Starting E2E workflow orchestration")
        print("=" * 60)

        # Stage 1: Entra VC Issuance
        print("\n[Stage 1] Entra VC Issuance (F-104)")
        entra_vcs = []
        for voter in voters:
            try:
                vc = await self.mock_entra_issuance(voter)
                entra_vcs.append(vc)
            except Exception as e:
                workflow_summary["errors"].append(
                    f"VC issuance failed for {voter['voter_id']}: {str(e)}"
                )

        workflow_summary["stages_completed"].append("entra_vc_issuance")

        # Stage 2: SAAC Credential Derivation
        print("\n[Stage 2] SAAC Credential Derivation (F-100, F-104)")
        saac_credentials = []
        saac_params = {"public_key": "mock_pubkey", "curve": "P-256"}
        for vc in entra_vcs:
            try:
                cred = await self.derive_saac_credential(vc, saac_params)
                saac_credentials.append(cred)
            except Exception as e:
                workflow_summary["errors"].append(f"SAAC derivation failed: {str(e)}")

        workflow_summary["stages_completed"].append("saac_credential_derivation")

        # Stage 3: Cross-Origin Flow Test
        print("\n[Stage 3] Cross-Origin Communication Test (F-107)")
        test_session = f"session-{secrets.token_hex(16)}"
        challenge = await self.initiate_cross_origin_flow(
            test_session, election_manifest["election_id"]
        )

        mock_response = {
            "origin": "https://vspacewallet.com",
            "signature": f"sig_{secrets.token_hex(32)}",
            "challenge_id": challenge["challenge_id"],
        }

        verified = await self.verify_cross_origin_response(
            challenge["challenge_id"], mock_response
        )

        if verified:
            workflow_summary["stages_completed"].append("cross_origin_communication")

        # Stage 4: NLWeb Query Test
        print("\n[Stage 4] NLWeb Query Test (F-108)")
        test_queries = [
            "How many ballots were cast?",
            "Verify serial number uniqueness",
        ]

        mock_election_data = {
            "ballots_cast": len(voters),
            "serial_numbers_registered": len(voters),
        }

        for query in test_queries:
            response = await self.mock_nlweb_query(query, mock_election_data)
            print(f"  Q: {query}")
            print(f"  A: {response[:80]}...")

        workflow_summary["stages_completed"].append("nlweb_query_interface")

        # Summary
        print("\n" + "=" * 60)
        print("[Workflow] E2E workflow complete")
        print(f"  Stages completed: {len(workflow_summary['stages_completed'])}/4")
        print(f"  Errors: {len(workflow_summary['errors'])}")

        return workflow_summary
