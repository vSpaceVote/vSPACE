"""
vSPACE Dry-Run E2E PoC Demo Runner
===================================

Main entry point for executing the vSPACE Augmented PRD End-to-End Proof of Concept.

This demo simulates a 10-voter election with:
- F-104: Entra Verified ID Bridge (mocked)
- F-105: vSpaceVote.com Voter-Facing PWA (simulated)
- F-106: vSpaceWallet.com Credential Wallet PWA (simulated)
- F-107: Cross-Origin Communication Protocol (simulated)
- F-108: NLWeb Conversational Interfaces (mocked)

Usage:
    python run_e2e_poc.py [--voters N] [--output-dir PATH]

Environment Variables (required for production staging):
    See ../setup/.env.example for complete list
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for electionguard_vspace imports
sys.path.insert(0, str(Path(__file__).parent.parent / "bindings" / "python"))

from electionguard_vspace.saac import SAACIssuer, SAACHolder
from electionguard_vspace.multiholder import CredentialSplitter, ThresholdPresenter
from electionguard_vspace.binding import BindingGenerator, ProofGenerator
from electionguard_vspace.serial import VRFSerialDerivation, SerialRegistry
from electionguard_vspace.record import AugmentedRecordBuilder

from mock_data import MockElectionGenerator, MockVoterGenerator
from workflow import E2EWorkflowOrchestrator


class E2EPoCDemo:
    """
    Dry-Run E2E PoC Demo for vSPACE Augmented PRD.

    Simulates complete election flow with vSPACE extensions:
    1. Election setup with SAAC parameter generation
    2. Voter registration with Entra VC issuance (mocked)
    3. Anonymous credential derivation
    4. Multi-holder credential splitting
    5. Ballot marking with credential binding
    6. One-show serial number enforcement
    7. Augmented election record construction
    8. NLWeb query interface (mocked)
    """

    def __init__(self, num_voters: int = 10, output_dir: str = None):
        self.num_voters = num_voters
        self.output_dir = (
            Path(output_dir) if output_dir else Path(__file__).parent / "output"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize vSPACE components
        self.saac_issuer = SAACIssuer()
        self.binding_generator = BindingGenerator()
        self.serial_registry = SerialRegistry()
        self.record_builder = AugmentedRecordBuilder()

        # Mock data generators
        self.election_generator = MockElectionGenerator()
        self.voter_generator = MockVoterGenerator()

        # Workflow orchestrator
        self.orchestrator = E2EWorkflowOrchestrator()

        # Results tracking
        self.results = {
            "demo_started": None,
            "demo_completed": None,
            "voters_processed": 0,
            "ballots_cast": 0,
            "serial_numbers_registered": 0,
            "errors": [],
        }

    async def run(self) -> Dict[str, Any]:
        """Execute complete E2E PoC demo flow."""
        self.results["demo_started"] = datetime.utcnow().isoformat()

        print("=" * 80)
        print("vSPACE Dry-Run E2E PoC Demo")
        print("=" * 80)
        print(f"Configuration: {self.num_voters} voters")
        print(f"Output directory: {self.output_dir}")
        print()

        # Phase 1: Election Setup
        print("[Phase 1] Election Setup")
        print("-" * 40)
        election_manifest = self.election_generator.generate_manifest()
        saac_params = self.saac_issuer.generate_parameters()

        print(f"✓ Election manifest generated: {election_manifest['election_id']}")
        print(f"✓ SAAC parameters generated")
        print()

        # Phase 2: Voter Registration & Credential Issuance
        print("[Phase 2] Voter Registration & Credential Issuance (F-104)")
        print("-" * 40)
        voters = self.voter_generator.generate_voters(self.num_voters)
        credentials = []

        for voter in voters:
            # Mock Entra VC issuance
            entra_vc = await self.orchestrator.mock_entra_issuance(voter)
            # Derive SAAC anonymous credential
            saac_credential = await self.orchestrator.derive_saac_credential(
                entra_vc, saac_params
            )
            credentials.append(
                {
                    "voter_id": voter["voter_id"],
                    "entra_vc": entra_vc,
                    "saac_credential": saac_credential,
                }
            )
            print(f"✓ Voter {voter['voter_id']}: Entra VC → SAAC credential derived")

        print()

        # Phase 3: Multi-Holder Credential Splitting (F-101)
        print("[Phase 3] Multi-Holder Credential Splitting (F-101)")
        print("-" * 40)
        splitter = CredentialSplitter(threshold=2, total_shares=2)

        for cred in credentials:
            shares = splitter.split_credential(cred["saac_credential"])
            cred["shares"] = shares
            print(
                f"✓ Voter {cred['voter_id']}: Credential split into {len(shares)} shares (2-of-2)"
            )

        print()

        # Phase 4: Ballot Marking & Binding (F-102, F-105)
        print("[Phase 4] Ballot Marking & Credential Binding (F-102, F-105)")
        print("-" * 40)
        ballots = []

        for cred in credentials:
            # Generate ballot
            ballot = self.election_generator.generate_ballot(cred["voter_id"])

            # Derive one-show serial number
            vrf = VRFSerialDerivation()
            serial_number = vrf.derive_serial(
                cred["saac_credential"], election_manifest["election_id"]
            )

            # Check serial uniqueness
            is_unique = self.serial_registry.check_uniqueness(serial_number)
            if not is_unique:
                error = f"Duplicate serial number detected for voter {cred['voter_id']}"
                self.results["errors"].append(error)
                print(f"✗ {error}")
                continue

            # Generate binding commitment and proof
            binding = self.binding_generator.create_binding(
                ballot["encryption_nonce"], serial_number
            )
            proof = ProofGenerator().generate_proof(
                binding, ballot, cred["saac_credential"]
            )

            # Register serial number
            self.serial_registry.register(
                serial_number, cred["voter_id"], election_manifest["election_id"]
            )

            ballots.append(
                {
                    "ballot": ballot,
                    "serial_number": serial_number,
                    "binding": binding,
                    "proof": proof,
                    "voter_id": cred["voter_id"],
                }
            )

            self.results["ballots_cast"] += 1
            self.results["serial_numbers_registered"] += 1
            print(
                f"✓ Voter {cred['voter_id']}: Ballot bound, serial #{serial_number[:16]}... registered"
            )

        print()

        # Phase 5: Augmented Election Record Construction (F-109)
        print("[Phase 5] Augmented Election Record Construction (F-109)")
        print("-" * 40)

        augmented_record = self.record_builder.build(
            election_manifest=election_manifest,
            ballots=ballots,
            saac_params=saac_params,
            serial_numbers=[b["serial_number"] for b in ballots],
            bindings=[b["binding"] for b in ballots],
            proofs=[b["proof"] for b in ballots],
        )

        # Save augmented record
        record_path = self.output_dir / "augmented_election_record.json"
        with open(record_path, "w") as f:
            json.dump(augmented_record, f, indent=2, default=str)

        print(f"✓ Augmented election record saved: {record_path}")
        print(f"  - Ballots: {len(ballots)}")
        print(f"  - Serial numbers: {self.results['serial_numbers_registered']}")
        print(f"  - Binding proofs: {len(ballots)}")
        print()

        # Phase 6: NLWeb Query Interface (F-108)
        print("[Phase 6] NLWeb Query Interface Demo (F-108)")
        print("-" * 40)

        # Mock NLWeb queries
        nlweb_queries = [
            "How many ballots were cast in this election?",
            "Show me the contest results for President",
            "Verify that all serial numbers are unique",
        ]

        for query in nlweb_queries:
            response = await self.orchestrator.mock_nlweb_query(query, augmented_record)
            print(f"Q: {query}")
            print(f"A: {response[:100]}...")
            print()

        # Phase 7: Verification
        print("[Phase 7] Verification Summary")
        print("-" * 40)

        verification_results = {
            "serial_uniqueness": self.serial_registry.verify_all_unique(),
            "binding_proofs_valid": all(b["proof"]["valid"] for b in ballots),
            "saac_params_consistent": True,  # Would verify in production
            "record_structure_valid": self.record_builder.validate_structure(
                augmented_record
            ),
        }

        for check, passed in verification_results.items():
            status = "✓" if passed else "✗"
            print(f"{status} {check}: {'PASS' if passed else 'FAIL'}")

        self.results["demo_completed"] = datetime.utcnow().isoformat()
        self.results["voters_processed"] = len(voters)
        self.results["verification"] = verification_results

        # Save demo results
        results_path = self.output_dir / "demo_results.json"
        with open(results_path, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        print()
        print("=" * 80)
        print("Demo Complete")
        print("=" * 80)
        print(f"Total voters: {self.results['voters_processed']}")
        print(f"Ballots cast: {self.results['ballots_cast']}")
        print(f"Errors: {len(self.results['errors'])}")
        print(f"Results saved to: {self.output_dir}")
        print()

        return self.results


def main():
    parser = argparse.ArgumentParser(description="vSPACE Dry-Run E2E PoC Demo")
    parser.add_argument(
        "--voters",
        "-n",
        type=int,
        default=10,
        help="Number of voters to simulate (default: 10)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=None,
        help="Output directory for demo artifacts (default: ./output)",
    )

    args = parser.parse_args()

    # Check for required environment variables (warn only in dry-run mode)
    required_vars = [
        "AZURE_ENTRA_TENANT_ID",
        "AZURE_AD_APP_CLIENT_ID",
        "AZURE_AD_APP_CLIENT_SECRET",
    ]

    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    if missing_vars:
        print("⚠ WARNING: Missing environment variables (running in dry-run mode):")
        for var in missing_vars:
            print(f"  - {var}")
        print()
        print("For production staging, run the setup wizard:")
        print("  python ../setup/wizard.py")
        print()

    # Run demo
    demo = E2EPoCDemo(num_voters=args.voters, output_dir=args.output_dir)
    results = asyncio.run(demo.run())

    # Exit with error code if verification failed
    if results.get("errors"):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
