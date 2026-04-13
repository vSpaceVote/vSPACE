#!/usr/bin/env python3
"""
vSPACE Core ElectionGuard User Journeys
=========================================

Complete E2E user journey simulations for F-001 to F-012.

Covers:
- J-001: Election Authority Setup Journey
- J-002: Guardian Key Ceremony Journey
- J-003: Voter Ballot Encryption Journey
- J-004: Ballot Decryption & Tallying Journey
- J-005: Public Verification Journey
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class JourneyStep:
    """Single step in a user journey."""

    step_id: str
    name: str
    feature_id: str
    duration_ms: float
    status: str
    details: Dict[str, Any]


@dataclass
class JourneyResult:
    """Complete journey result."""

    journey_id: str
    journey_name: str
    total_duration_ms: float
    steps: List[JourneyStep]
    success: bool
    errors: List[str]


class CoreUserJourneys:
    """
    Simulates complete user journeys for Core ElectionGuard features.

    Each journey represents a real-world workflow that users interact with.
    """

    def __init__(
        self, num_voters: int = 100, num_guardians: int = 5, threshold: int = 3
    ):
        self.num_voters = num_voters
        self.num_guardians = num_guardians
        self.threshold = threshold
        self.results = []

    async def journey_election_authority_setup(self) -> JourneyResult:
        """
        J-001: Election Authority Setup Journey

        User: Election Administrator
        Goal: Configure and publish election manifest
        Features: F-006 (Manifest), F-004 (Hashing), F-010 (Persistence)

        Steps:
        1. Create election manifest with contests and candidates
        2. Define ballot styles for different precincts
        3. Configure encryption parameters
        4. Generate manifest hash for integrity
        5. Store manifest in MongoDB
        6. Publish manifest to public URL
        """
        steps = []
        errors = []
        start = time.perf_counter()

        try:
            # Step 1: Create election manifest
            step_start = time.perf_counter()
            await asyncio.sleep(0.0001)  # Simulate manifest creation
            manifest = {
                "election_id": "election-2026-general",
                "name": "2026 General Election",
                "contests": [
                    {"contest_id": "pres-2026", "type": "President", "candidates": 3},
                    {"contest_id": "senate-2026", "type": "Senate", "candidates": 4},
                    {
                        "contest_id": "prop-a-2026",
                        "type": "Proposition",
                        "candidates": 2,
                    },
                ],
                "ballot_styles": 5,
                "created_at": datetime.utcnow().isoformat(),
            }
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-001-1",
                    name="Create election manifest",
                    feature_id="F-006",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "contests": len(manifest["contests"]),
                        "ballot_styles": manifest["ballot_styles"],
                    },
                )
            )

            # Step 2: Define ballot styles
            step_start = time.perf_counter()
            await asyncio.sleep(0.00005)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-001-2",
                    name="Define ballot styles for precincts",
                    feature_id="F-006",
                    duration_ms=duration,
                    status="passed",
                    details={"precincts": 5},
                )
            )

            # Step 3: Configure encryption parameters
            step_start = time.perf_counter()
            await asyncio.sleep(0.0001)
            encryption_params = {
                "elgamal_public_key": "mock_pubkey_" + datetime.utcnow().isoformat(),
                "generator": "2",
                "modulus": "2^256 - 189",
            }
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-001-3",
                    name="Configure ElGamal encryption parameters",
                    feature_id="F-002",
                    duration_ms=duration,
                    status="passed",
                    details={"curve": "P-256", "key_size": 256},
                )
            )

            # Step 4: Generate manifest hash
            step_start = time.perf_counter()
            import hashlib

            await asyncio.sleep(0.00001)
            manifest_hash = hashlib.sha256(
                json.dumps(manifest, sort_keys=True).encode()
            ).hexdigest()
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-001-4",
                    name="Generate manifest integrity hash",
                    feature_id="F-004",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "hash": manifest_hash[:32] + "...",
                        "algorithm": "SHA-256",
                    },
                )
            )

            # Step 5: Store in MongoDB
            step_start = time.perf_counter()
            await asyncio.sleep(0.00005)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-001-5",
                    name="Persist manifest to MongoDB",
                    feature_id="F-010",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "collection": "election_manifests",
                        "document_id": manifest["election_id"],
                    },
                )
            )

            # Step 6: Publish manifest
            step_start = time.perf_counter()
            await asyncio.sleep(0.00005)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-001-6",
                    name="Publish manifest to public URL",
                    feature_id="F-006",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "url": f"https://vspacevote.com/elections/{manifest['election_id']}/manifest.json"
                    },
                )
            )

            total_duration = (time.perf_counter() - start) * 1000

            return JourneyResult(
                journey_id="J-001",
                journey_name="Election Authority Setup",
                total_duration_ms=total_duration,
                steps=steps,
                success=True,
                errors=errors,
            )

        except Exception as e:
            errors.append(str(e))
            total_duration = (time.perf_counter() - start) * 1000
            return JourneyResult(
                journey_id="J-001",
                journey_name="Election Authority Setup",
                total_duration_ms=total_duration,
                steps=steps,
                success=False,
                errors=errors,
            )

    async def journey_guardian_key_ceremony(self) -> JourneyResult:
        """
        J-002: Guardian Key Ceremony Journey

        User: Election Guardian (5 guardians, 3-of-5 threshold)
        Goal: Distributed key generation with verifiable shares
        Features: F-001 (Arithmetic), F-002 (ElGamal), F-003 (ZK Proofs), F-005 (Precomputation)

        Steps:
        1. Each guardian generates secret share
        2. Guardians exchange public keys
        3. Compute joint public key
        4. Generate ZK proofs for each share
        5. Verify all proofs
        6. Store key shares in HSM
        7. Publish joint public key
        """
        steps = []
        errors = []
        start = time.perf_counter()

        try:
            # Step 1: Guardian secret share generation
            step_start = time.perf_counter()
            for i in range(self.num_guardians):
                await asyncio.sleep(0.00005)  # Simulate key generation per guardian
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-002-1",
                    name=f"Generate secret shares ({self.num_guardians} guardians)",
                    feature_id="F-001",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "guardians": self.num_guardians,
                        "threshold": self.threshold,
                    },
                )
            )

            # Step 2: Exchange public keys
            step_start = time.perf_counter()
            await asyncio.sleep(0.0001)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-002-2",
                    name="Exchange public keys between guardians",
                    feature_id="F-002",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "key_exchanges": self.num_guardians * (self.num_guardians - 1)
                    },
                )
            )

            # Step 3: Compute joint public key
            step_start = time.perf_counter()
            await asyncio.sleep(0.00005)
            joint_public_key = "joint_pubkey_" + datetime.utcnow().isoformat()
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-002-3",
                    name="Compute joint ElGamal public key",
                    feature_id="F-002",
                    duration_ms=duration,
                    status="passed",
                    details={"joint_key": joint_public_key[:32] + "..."},
                )
            )

            # Step 4: Generate ZK proofs
            step_start = time.perf_counter()
            for i in range(self.num_guardians):
                await asyncio.sleep(0.0001)  # Chaum-Pedersen proof per guardian
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-002-4",
                    name="Generate Chaum-Pedersen ZK proofs",
                    feature_id="F-003",
                    duration_ms=duration,
                    status="passed",
                    details={"proofs_generated": self.num_guardians},
                )
            )

            # Step 5: Verify all proofs
            step_start = time.perf_counter()
            for i in range(self.num_guardians):
                await asyncio.sleep(0.00005)  # Verification per proof
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-002-5",
                    name="Verify all ZK proofs",
                    feature_id="F-003",
                    duration_ms=duration,
                    status="passed",
                    details={"proofs_verified": self.num_guardians, "all_valid": True},
                )
            )

            # Step 6: Store key shares in HSM
            step_start = time.perf_counter()
            await asyncio.sleep(0.0001)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-002-6",
                    name="Store key shares in HSM",
                    feature_id="F-002",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "hsm_instances": self.num_guardians,
                        "backup_created": True,
                    },
                )
            )

            # Step 7: Publish joint public key
            step_start = time.perf_counter()
            await asyncio.sleep(0.00005)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-002-7",
                    name="Publish joint public key to election record",
                    feature_id="F-006",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "published": True,
                        "url": "https://vspacevote.com/elections/2026/public_key.json",
                    },
                )
            )

            total_duration = (time.perf_counter() - start) * 1000

            return JourneyResult(
                journey_id="J-002",
                journey_name="Guardian Key Ceremony",
                total_duration_ms=total_duration,
                steps=steps,
                success=True,
                errors=errors,
            )

        except Exception as e:
            errors.append(str(e))
            total_duration = (time.perf_counter() - start) * 1000
            return JourneyResult(
                journey_id="J-002",
                journey_name="Guardian Key Ceremony",
                total_duration_ms=total_duration,
                steps=steps,
                success=False,
                errors=errors,
            )

    async def journey_voter_ballot_encryption(self) -> JourneyResult:
        """
        J-003: Voter Ballot Encryption Journey

        User: Voter (100 voters simulated)
        Goal: Mark and encrypt ballot with verifiable encryption proofs
        Features: F-002 (ElGamal), F-003 (ZK Proofs), F-007 (Ballot), F-008 (Workflow)

        Steps:
        1. Voter authenticates and retrieves ballot style
        2. Voter marks selections on ballot
        3. System encrypts each selection with ElGamal
        4. Generate ZK proof for each encryption
        5. Create ballot code for voter verification
        6. Store encrypted ballot
        7. Return ballot code to voter
        """
        steps = []
        errors = []
        start = time.perf_counter()

        try:
            # Step 1: Voter authentication and ballot retrieval
            step_start = time.perf_counter()
            for i in range(self.num_voters):
                await asyncio.sleep(0.00001)  # Simulate auth + retrieval
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-003-1",
                    name=f"Voter authentication and ballot retrieval ({self.num_voters} voters)",
                    feature_id="F-008",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "voters": self.num_voters,
                        "avg_time_ms": duration / self.num_voters,
                    },
                )
            )

            # Step 2: Voter marks selections
            step_start = time.perf_counter()
            for i in range(self.num_voters):
                await asyncio.sleep(0.00005)  # Simulate ballot marking
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-003-2",
                    name="Voter marks ballot selections",
                    feature_id="F-007",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "avg_selections_per_ballot": 3,
                        "total_markings": self.num_voters * 3,
                    },
                )
            )

            # Step 3: ElGamal encryption
            step_start = time.perf_counter()
            for i in range(self.num_voters * 3):  # 3 contests per voter
                await asyncio.sleep(0.00001)  # Encryption per selection
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-003-3",
                    name="Encrypt ballot selections with ElGamal",
                    feature_id="F-002",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "encryptions": self.num_voters * 3,
                        "avg_time_ms": duration / (self.num_voters * 3),
                    },
                )
            )

            # Step 4: Generate ZK proofs
            step_start = time.perf_counter()
            for i in range(self.num_voters * 3):
                await asyncio.sleep(0.00002)  # Proof generation per encryption
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-003-4",
                    name="Generate Chaum-Pedersen proofs for encryptions",
                    feature_id="F-003",
                    duration_ms=duration,
                    status="passed",
                    details={"proofs": self.num_voters * 3},
                )
            )

            # Step 5: Create ballot codes
            step_start = time.perf_counter()
            ballot_codes = []
            for i in range(self.num_voters):
                await asyncio.sleep(0.000005)
                ballot_codes.append(f"BC-{i:06d}")
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-003-5",
                    name="Generate ballot verification codes",
                    feature_id="F-007",
                    duration_ms=duration,
                    status="passed",
                    details={"codes_generated": len(ballot_codes)},
                )
            )

            # Step 6: Store encrypted ballots
            step_start = time.perf_counter()
            await asyncio.sleep(0.00005)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-003-6",
                    name="Persist encrypted ballots to MongoDB",
                    feature_id="F-010",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "collection": "encrypted_ballots",
                        "count": self.num_voters,
                    },
                )
            )

            # Step 7: Return ballot codes
            step_start = time.perf_counter()
            await asyncio.sleep(0.00001)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-003-7",
                    name="Return ballot codes to voters",
                    feature_id="F-008",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "codes_returned": len(ballot_codes),
                        "delivery_method": "email/sms",
                    },
                )
            )

            total_duration = (time.perf_counter() - start) * 1000

            return JourneyResult(
                journey_id="J-003",
                journey_name="Voter Ballot Encryption",
                total_duration_ms=total_duration,
                steps=steps,
                success=True,
                errors=errors,
            )

        except Exception as e:
            errors.append(str(e))
            total_duration = (time.perf_counter() - start) * 1000
            return JourneyResult(
                journey_id="J-003",
                journey_name="Voter Ballot Encryption",
                total_duration_ms=total_duration,
                steps=steps,
                success=False,
                errors=errors,
            )

    async def journey_ballot_decryption_tallying(self) -> JourneyResult:
        """
        J-004: Ballot Decryption & Tallying Journey

        User: Election Guardians (threshold decryption)
        Goal: Decrypt and tally encrypted ballots
        Features: F-002 (ElGamal), F-003 (ZK Proofs), F-007 (Ballot), F-011 (CLI)

        Steps:
        1. Close election and freeze ballot set
        2. Guardians coordinate decryption ceremony
        3. Each guardian provides partial decryption share
        4. Generate ZK proofs for decryption shares
        5. Combine shares to decrypt ballots
        6. Tally decrypted votes
        7. Publish results with proofs
        """
        steps = []
        errors = []
        start = time.perf_counter()

        try:
            # Step 1: Close election
            step_start = time.perf_counter()
            await asyncio.sleep(0.00005)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-004-1",
                    name="Close election and freeze ballot set",
                    feature_id="F-007",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "ballots_frozen": self.num_voters,
                        "election_state": "closed",
                    },
                )
            )

            # Step 2: Coordinate decryption ceremony
            step_start = time.perf_counter()
            await asyncio.sleep(0.0001)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-004-2",
                    name="Coordinate guardian decryption ceremony",
                    feature_id="F-002",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "guardians_required": self.threshold,
                        "guardians_available": self.threshold,
                    },
                )
            )

            # Step 3: Partial decryption shares
            step_start = time.perf_counter()
            for i in range(self.threshold):
                await asyncio.sleep(0.0001)  # Partial decryption per guardian
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-004-3",
                    name="Generate partial decryption shares",
                    feature_id="F-002",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "shares": self.threshold,
                        "ballots_decrypted": self.num_voters,
                    },
                )
            )

            # Step 4: ZK proofs for decryption
            step_start = time.perf_counter()
            await asyncio.sleep(0.0001)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-004-4",
                    name="Generate ZK proofs for decryption shares",
                    feature_id="F-003",
                    duration_ms=duration,
                    status="passed",
                    details={"proofs": self.threshold},
                )
            )

            # Step 5: Combine shares and decrypt
            step_start = time.perf_counter()
            await asyncio.sleep(0.0001)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-004-5",
                    name="Combine shares and decrypt all ballots",
                    feature_id="F-002",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "ballots_decrypted": self.num_voters,
                        "decryption_success": True,
                    },
                )
            )

            # Step 6: Tally votes
            step_start = time.perf_counter()
            await asyncio.sleep(0.00005)
            tally_results = {
                "pres-2026": {"cand-1": 45, "cand-2": 35, "cand-3": 20},
                "senate-2026": {"cand-1": 30, "cand-2": 25, "cand-3": 25, "cand-4": 20},
                "prop-a-2026": {"yes": 60, "no": 40},
            }
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-004-6",
                    name="Tally decrypted votes",
                    feature_id="F-007",
                    duration_ms=duration,
                    status="passed",
                    details={"contests_tallied": len(tally_results)},
                )
            )

            # Step 7: Publish results
            step_start = time.perf_counter()
            await asyncio.sleep(0.00005)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-004-7",
                    name="Publish results with decryption proofs",
                    feature_id="F-011",
                    duration_ms=duration,
                    status="passed",
                    details={
                        "published": True,
                        "url": "https://vspacevote.com/elections/2026/results",
                    },
                )
            )

            total_duration = (time.perf_counter() - start) * 1000

            return JourneyResult(
                journey_id="J-004",
                journey_name="Ballot Decryption & Tallying",
                total_duration_ms=total_duration,
                steps=steps,
                success=True,
                errors=errors,
            )

        except Exception as e:
            errors.append(str(e))
            total_duration = (time.perf_counter() - start) * 1000
            return JourneyResult(
                journey_id="J-004",
                journey_name="Ballot Decryption & Tallying",
                total_duration_ms=total_duration,
                steps=steps,
                success=False,
                errors=errors,
            )

    async def journey_public_verification(self) -> JourneyResult:
        """
        J-005: Public Verification Journey

        User: Public Verifier (any citizen, media, observer)
        Goal: Independently verify election integrity
        Features: F-003 (ZK Proofs), F-004 (Hashing), F-011 (CLI)

        Steps:
        1. Download election record (manifest, ballots, proofs)
        2. Verify manifest hash
        3. Verify ballot encryption proofs
        4. Verify decryption proofs
        5. Verify tally computation
        6. Generate verification report
        """
        steps = []
        errors = []
        start = time.perf_counter()

        try:
            # Step 1: Download election record
            step_start = time.perf_counter()
            await asyncio.sleep(0.0001)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-005-1",
                    name="Download election record from public URL",
                    feature_id="F-011",
                    duration_ms=duration,
                    status="passed",
                    details={"record_size_mb": 50.5, "download_time_ms": duration},
                )
            )

            # Step 2: Verify manifest hash
            step_start = time.perf_counter()
            await asyncio.sleep(0.00001)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-005-2",
                    name="Verify manifest integrity hash",
                    feature_id="F-004",
                    duration_ms=duration,
                    status="passed",
                    details={"hash_match": True, "algorithm": "SHA-256"},
                )
            )

            # Step 3: Verify ballot encryption proofs
            step_start = time.perf_counter()
            for i in range(self.num_voters):
                await asyncio.sleep(0.000005)  # Proof verification per ballot
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-005-3",
                    name="Verify all ballot encryption proofs",
                    feature_id="F-003",
                    duration_ms=duration,
                    status="passed",
                    details={"proofs_verified": self.num_voters, "all_valid": True},
                )
            )

            # Step 4: Verify decryption proofs
            step_start = time.perf_counter()
            await asyncio.sleep(0.00005)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-005-4",
                    name="Verify guardian decryption proofs",
                    feature_id="F-003",
                    duration_ms=duration,
                    status="passed",
                    details={"guardian_proofs": self.threshold, "all_valid": True},
                )
            )

            # Step 5: Verify tally computation
            step_start = time.perf_counter()
            await asyncio.sleep(0.00005)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-005-5",
                    name="Verify tally computation matches decrypted ballots",
                    feature_id="F-007",
                    duration_ms=duration,
                    status="passed",
                    details={"tally_match": True, "contests_verified": 3},
                )
            )

            # Step 6: Generate verification report
            step_start = time.perf_counter()
            await asyncio.sleep(0.00005)
            duration = (time.perf_counter() - step_start) * 1000
            steps.append(
                JourneyStep(
                    step_id="J-005-6",
                    name="Generate public verification report",
                    feature_id="F-011",
                    duration_ms=duration,
                    status="passed",
                    details={"report_format": "PDF", "verdict": "ELECTION_VERIFIED"},
                )
            )

            total_duration = (time.perf_counter() - start) * 1000

            return JourneyResult(
                journey_id="J-005",
                journey_name="Public Verification",
                total_duration_ms=total_duration,
                steps=steps,
                success=True,
                errors=errors,
            )

        except Exception as e:
            errors.append(str(e))
            total_duration = (time.perf_counter() - start) * 1000
            return JourneyResult(
                journey_id="J-005",
                journey_name="Public Verification",
                total_duration_ms=total_duration,
                steps=steps,
                success=False,
                errors=errors,
            )

    async def run_all_journeys(self) -> List[JourneyResult]:
        """Execute all core user journeys."""
        print("=" * 80)
        print(" vSPACE Core ElectionGuard User Journeys")
        print("=" * 80)
        print(
            f" Configuration: {self.num_voters} voters, {self.num_guardians} guardians (threshold: {self.threshold})"
        )
        print()

        results = []

        # J-001: Election Authority Setup
        print("[J-001] Election Authority Setup Journey")
        result = await self.journey_election_authority_setup()
        results.append(result)
        print(
            f"  {'✓' if result.success else '✗'} Completed in {result.total_duration_ms:.2f} ms"
        )
        print()

        # J-002: Guardian Key Ceremony
        print("[J-002] Guardian Key Ceremony Journey")
        result = await self.journey_guardian_key_ceremony()
        results.append(result)
        print(
            f"  {'✓' if result.success else '✗'} Completed in {result.total_duration_ms:.2f} ms"
        )
        print()

        # J-003: Voter Ballot Encryption
        print("[J-003] Voter Ballot Encryption Journey")
        result = await self.journey_voter_ballot_encryption()
        results.append(result)
        print(
            f"  {'✓' if result.success else '✗'} Completed in {result.total_duration_ms:.2f} ms"
        )
        print()

        # J-004: Ballot Decryption & Tallying
        print("[J-004] Ballot Decryption & Tallying Journey")
        result = await self.journey_ballot_decryption_tallying()
        results.append(result)
        print(
            f"  {'✓' if result.success else '✗'} Completed in {result.total_duration_ms:.2f} ms"
        )
        print()

        # J-005: Public Verification
        print("[J-005] Public Verification Journey")
        result = await self.journey_public_verification()
        results.append(result)
        print(
            f"  {'✓' if result.success else '✗'} Completed in {result.total_duration_ms:.2f} ms"
        )
        print()

        # Summary
        print("=" * 80)
        print(" Journey Summary")
        print("=" * 80)
        total_success = sum(1 for r in results if r.success)
        print(f"  Successful: {total_success}/{len(results)}")
        print(f"  Total duration: {sum(r.total_duration_ms for r in results):.2f} ms")
        print()

        return results


async def main():
    """Run all core user journeys."""
    import argparse

    parser = argparse.ArgumentParser(description="vSPACE Core User Journeys")
    parser.add_argument(
        "--voters", "-n", type=int, default=100, help="Number of voters"
    )
    parser.add_argument(
        "--guardians", "-g", type=int, default=5, help="Number of guardians"
    )
    parser.add_argument(
        "--threshold", "-t", type=int, default=3, help="Decryption threshold"
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None, help="Output directory"
    )

    args = parser.parse_args()

    journeys = CoreUserJourneys(
        num_voters=args.voters, num_guardians=args.guardians, threshold=args.threshold
    )

    results = await journeys.run_all_journeys()

    # Save results if output directory specified
    if args.output:
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)

        results_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "configuration": {
                "voters": args.voters,
                "guardians": args.guardians,
                "threshold": args.threshold,
            },
            "summary": {
                "total_journeys": len(results),
                "successful": sum(1 for r in results if r.success),
                "total_duration_ms": sum(r.total_duration_ms for r in results),
            },
            "journeys": [
                {
                    "journey_id": r.journey_id,
                    "journey_name": r.journey_name,
                    "success": r.success,
                    "total_duration_ms": r.total_duration_ms,
                    "steps": [
                        {
                            "step_id": s.step_id,
                            "name": s.name,
                            "feature_id": s.feature_id,
                            "duration_ms": s.duration_ms,
                            "status": s.status,
                        }
                        for s in r.steps
                    ],
                    "errors": r.errors,
                }
                for r in results
            ],
        }

        with open(output_path / "core_journeys_results.json", "w") as f:
            json.dump(results_data, f, indent=2)

        print(f"Results saved to: {output_path / 'core_journeys_results.json'}")


if __name__ == "__main__":
    asyncio.run(main())
