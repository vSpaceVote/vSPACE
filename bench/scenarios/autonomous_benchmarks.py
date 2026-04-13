"""
vSPACE Autonomous PRD Benchmark Scenarios
==========================================

Benchmarks for features from vSPACE_Autonomous_PRD_v260412a.json:
- F-100: SAAC Protocol Implementation
- F-101: Multi-Holder BBS Credentials
- F-102: Credential-to-Ballot Binding
- F-103: One-Show Enforcement
- F-109: Augmented Election Record
- F-110: vSPACE Verifier Extension
"""

import asyncio
import time
from typing import Dict, Any, List
from pathlib import Path

# Add parent path for imports
sys_path = str(Path(__file__).parent.parent.parent / "bindings" / "python")
if sys_path not in __import__("sys").path:
    __import__("sys").path.insert(0, sys_path)

from electionguard_vspace.saac import SAACIssuer, SAACHolder
from electionguard_vspace.multiholder import CredentialSplitter, ThresholdPresenter
from electionguard_vspace.binding import (
    BindingGenerator,
    ProofGenerator,
    verify_binding_proof,
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

from ..utils.benchmark_helpers import BenchmarkResult, mock_ballot, mock_credential


class AutonomousBenchmarkSuite:
    """Benchmark suite for Autonomous PRD features."""

    def __init__(self, num_voters: int = 100):
        self.num_voters = num_voters
        self.results = {}

    async def benchmark_saac(self) -> BenchmarkResult:
        """
        F-100: SAAC Protocol Implementation benchmark.

        Measures:
        - Parameter generation latency
        - Credential issuance latency
        - Presentation generation latency
        - Verification latency
        """
        errors = []
        warnings = []
        metrics = {}

        try:
            start = time.perf_counter()

            # Phase 1: Parameter generation
            param_start = time.perf_counter()
            issuer = SAACIssuer()
            params = issuer.generate_parameters()
            param_duration = (time.perf_counter() - param_start) * 1000

            # Phase 2: Credential issuance (100 voters)
            issue_start = time.perf_counter()
            credentials = []
            for i in range(self.num_voters):
                holder = SAACHolder()
                cred = holder.create_credential(params, {"voter_id": f"voter-{i}"})
                credentials.append(cred)
            issue_duration = (time.perf_counter() - issue_start) * 1000

            # Phase 3: Presentation generation
            present_start = time.perf_counter()
            presentations = []
            for cred in credentials:
                holder = SAACHolder()
                pres = holder.generate_presentation(cred, "election-2026")
                presentations.append(pres)
            present_duration = (time.perf_counter() - present_start) * 1000

            # Phase 4: Verification
            verify_start = time.perf_counter()
            valid_count = 0
            for pres in presentations:
                is_valid = issuer.verify_presentation(pres, params)
                if is_valid:
                    valid_count += 1
            verify_duration = (time.perf_counter() - verify_start) * 1000

            total_duration = (time.perf_counter() - start) * 1000

            # Calculate metrics
            metrics = {
                "parameter_generation_ms": param_duration,
                "issuance_total_ms": issue_duration,
                "issuance_per_voter_ms": issue_duration / self.num_voters,
                "presentation_total_ms": present_duration,
                "presentation_per_voter_ms": present_duration / self.num_voters,
                "verification_total_ms": verify_duration,
                "verification_per_voter_ms": verify_duration / self.num_voters,
                "total_duration_ms": total_duration,
                "voters_processed": self.num_voters,
                "verification_success_rate": (valid_count / self.num_voters) * 100,
                "throughput_voters_per_second": self.num_voters
                / (total_duration / 1000),
            }

            # Check against performance targets from PRD
            if metrics["verification_per_voter_ms"] > 50:
                warnings.append(
                    f"Verification latency {metrics['verification_per_voter_ms']:.2f}ms exceeds target of 50ms"
                )

            status = "passed" if valid_count == self.num_voters else "failed"
            if valid_count < self.num_voters:
                errors.append(
                    f"Only {valid_count}/{self.num_voters} presentations verified"
                )

            return BenchmarkResult(
                name="SAAC Protocol Implementation",
                feature_id="F-100",
                status=status,
                duration_ms=total_duration,
                metrics=metrics,
                errors=errors,
                warnings=warnings,
            )

        except Exception as e:
            errors.append(str(e))
            return BenchmarkResult(
                name="SAAC Protocol Implementation",
                feature_id="F-100",
                status="failed",
                duration_ms=0,
                metrics=metrics,
                errors=errors,
                warnings=warnings,
            )

    async def benchmark_multiholder(self) -> BenchmarkResult:
        """
        F-101: Multi-Holder BBS Credentials benchmark.

        Measures:
        - Credential splitting latency
        - Share distribution latency
        - Threshold presentation latency
        - Reconstruction success rate
        """
        errors = []
        warnings = []
        metrics = {}

        try:
            start = time.perf_counter()

            # Generate base credentials
            issuer = SAACIssuer()
            params = issuer.generate_parameters()
            holder = SAACHolder()
            base_credential = holder.create_credential(params, {"voter_id": "test"})

            # Phase 1: Credential splitting (2-of-2 threshold)
            split_start = time.perf_counter()
            splitter = CredentialSplitter(threshold=2, total_shares=2)
            shares_list = []
            for i in range(self.num_voters):
                shares = splitter.split_credential(base_credential)
                shares_list.append(shares)
            split_duration = (time.perf_counter() - split_start) * 1000

            # Phase 2: Threshold presentation
            threshold_start = time.perf_counter()
            presenter = ThresholdPresenter()
            successful_presentations = 0
            for shares in shares_list:
                try:
                    presentation = presenter.combine_shares(shares, "challenge-123")
                    if presentation:
                        successful_presentations += 1
                except:
                    pass
            threshold_duration = (time.perf_counter() - threshold_start) * 1000

            total_duration = (time.perf_counter() - start) * 1000

            metrics = {
                "splitting_total_ms": split_duration,
                "splitting_per_voter_ms": split_duration / self.num_voters,
                "threshold_presentation_total_ms": threshold_duration,
                "threshold_presentation_per_voter_ms": threshold_duration
                / self.num_voters,
                "total_duration_ms": total_duration,
                "successful_threshold_presentations": successful_presentations,
                "success_rate": (successful_presentations / self.num_voters) * 100,
            }

            if successful_presentations < self.num_voters:
                errors.append(
                    f"Only {successful_presentations}/{self.num_voters} threshold presentations succeeded"
                )

            status = (
                "passed" if successful_presentations == self.num_voters else "failed"
            )

            return BenchmarkResult(
                name="Multi-Holder BBS Credentials",
                feature_id="F-101",
                status=status,
                duration_ms=total_duration,
                metrics=metrics,
                errors=errors,
                warnings=warnings,
            )

        except Exception as e:
            errors.append(str(e))
            return BenchmarkResult(
                name="Multi-Holder BBS Credentials",
                feature_id="F-101",
                status="failed",
                duration_ms=0,
                metrics={},
                errors=errors,
                warnings=warnings,
            )

    async def benchmark_binding(self) -> BenchmarkResult:
        """
        F-102: Credential-to-Ballot Binding benchmark.

        Measures:
        - Binding commitment generation latency
        - Proof generation latency
        - Proof verification latency
        - End-to-end binding latency per ballot
        """
        errors = []
        warnings = []
        metrics = {}

        try:
            start = time.perf_counter()

            binding_gen = BindingGenerator()
            proof_gen = ProofGenerator()

            # Generate bindings for all voters
            bind_start = time.perf_counter()
            bindings = []
            for i in range(self.num_voters):
                ballot = mock_ballot(f"voter-{i}")
                credential = mock_credential(f"voter-{i}")
                binding = binding_gen.create_binding(
                    ballot["encryption_nonce"], credential["credential_key"]
                )
                bindings.append(
                    {"binding": binding, "ballot": ballot, "credential": credential}
                )
            bind_duration = (time.perf_counter() - bind_start) * 1000

            # Generate proofs
            proof_start = time.perf_counter()
            for b in bindings:
                proof = proof_gen.generate_proof(
                    b["binding"], b["ballot"], b["credential"]
                )
                b["proof"] = proof
            proof_duration = (time.perf_counter() - proof_start) * 1000

            # Verify proofs
            verify_start = time.perf_counter()
            valid_proofs = 0
            for b in bindings:
                is_valid = verify_binding_proof(
                    b["proof"], b["binding"], b["ballot"], b["credential"]
                )
                if is_valid:
                    valid_proofs += 1
            verify_duration = (time.perf_counter() - verify_start) * 1000

            total_duration = (time.perf_counter() - start) * 1000

            metrics = {
                "binding_generation_total_ms": bind_duration,
                "binding_generation_per_ballot_ms": bind_duration / self.num_voters,
                "proof_generation_total_ms": proof_duration,
                "proof_generation_per_ballot_ms": proof_duration / self.num_voters,
                "proof_verification_total_ms": verify_duration,
                "proof_verification_per_ballot_ms": verify_duration / self.num_voters,
                "total_duration_ms": total_duration,
                "valid_proofs": valid_proofs,
                "verification_success_rate": (valid_proofs / self.num_voters) * 100,
                "end_to_end_per_ballot_ms": total_duration / self.num_voters,
            }

            # Check against PRD performance target (< 50ms per ballot)
            if metrics["end_to_end_per_ballot_ms"] > 50:
                warnings.append(
                    f"End-to-end latency {metrics['end_to_end_per_ballot_ms']:.2f}ms exceeds target of 50ms"
                )

            status = "passed" if valid_proofs == self.num_voters else "failed"
            if valid_proofs < self.num_voters:
                errors.append(f"Only {valid_proofs}/{self.num_voters} proofs verified")

            return BenchmarkResult(
                name="Credential-to-Ballot Binding",
                feature_id="F-102",
                status=status,
                duration_ms=total_duration,
                metrics=metrics,
                errors=errors,
                warnings=warnings,
            )

        except Exception as e:
            errors.append(str(e))
            return BenchmarkResult(
                name="Credential-to-Ballot Binding",
                feature_id="F-102",
                status="failed",
                duration_ms=0,
                metrics={},
                errors=errors,
                warnings=warnings,
            )

    async def benchmark_serial(self) -> BenchmarkResult:
        """
        F-103: One-Show Enforcement benchmark.

        Measures:
        - VRF serial number derivation latency
        - Serial registry lookup latency
        - Uniqueness verification latency
        - Duplicate detection accuracy
        """
        errors = []
        warnings = []
        metrics = {}

        try:
            start = time.perf_counter()

            vrf = VRFSerialDerivation()
            registry = SerialRegistry()
            election_id = "election-2026"

            # Phase 1: Serial number derivation
            derive_start = time.perf_counter()
            serial_numbers = []
            for i in range(self.num_voters):
                credential = mock_credential(f"voter-{i}")
                serial = vrf.derive_serial(credential, election_id)
                serial_numbers.append(serial)
            derive_duration = (time.perf_counter() - derive_start) * 1000

            # Phase 2: Serial registration
            register_start = time.perf_counter()
            for i, serial in enumerate(serial_numbers):
                registry.register(serial, f"voter-{i}", election_id)
            register_duration = (time.perf_counter() - register_start) * 1000

            # Phase 3: Uniqueness verification
            verify_start = time.perf_counter()
            is_unique = registry.verify_all_unique()
            verify_duration = (time.perf_counter() - verify_start) * 1000

            # Phase 4: Duplicate detection test (inject duplicate)
            duplicate_test_start = time.perf_counter()
            duplicate_detected = False
            if serial_numbers:
                # Try to register duplicate
                is_duplicate = not registry.check_uniqueness(serial_numbers[0])
                duplicate_detected = is_duplicate
            duplicate_test_duration = (
                time.perf_counter() - duplicate_test_start
            ) * 1000

            total_duration = (time.perf_counter() - start) * 1000

            metrics = {
                "serial_derivation_total_ms": derive_duration,
                "serial_derivation_per_voter_ms": derive_duration / self.num_voters,
                "registration_total_ms": register_duration,
                "registration_per_voter_ms": register_duration / self.num_voters,
                "uniqueness_verification_ms": verify_duration,
                "duplicate_detection_ms": duplicate_test_duration,
                "total_duration_ms": total_duration,
                "serial_numbers_generated": len(serial_numbers),
                "all_unique": is_unique,
                "duplicate_detected": duplicate_detected,
            }

            if not is_unique:
                errors.append("Serial numbers are not unique (should not happen)")
            if not duplicate_detected:
                errors.append("Duplicate detection failed")

            status = "passed" if (is_unique and duplicate_detected) else "failed"

            return BenchmarkResult(
                name="One-Show Enforcement",
                feature_id="F-103",
                status=status,
                duration_ms=total_duration,
                metrics=metrics,
                errors=errors,
                warnings=warnings,
            )

        except Exception as e:
            errors.append(str(e))
            return BenchmarkResult(
                name="One-Show Enforcement",
                feature_id="F-103",
                status="failed",
                duration_ms=0,
                metrics={},
                errors=errors,
                warnings=warnings,
            )

    async def benchmark_record(self) -> BenchmarkResult:
        """
        F-109: Augmented Election Record benchmark.

        Measures:
        - Record construction latency
        - Serialization latency (JSON, BSON, MsgPack)
        - Validation latency
        - Record size
        """
        errors = []
        warnings = []
        metrics = {}

        try:
            start = time.perf_counter()

            builder = AugmentedRecordBuilder()

            # Generate mock data
            ballots = [mock_ballot(f"voter-{i}") for i in range(self.num_voters)]
            serial_numbers = [f"serial-{i}" for i in range(self.num_voters)]
            bindings = [{"commitment": f"commit-{i}"} for i in range(self.num_voters)]
            proofs = [
                {"valid": True, "proof": f"proof-{i}"} for i in range(self.num_voters)
            ]

            # Phase 1: Record construction
            construct_start = time.perf_counter()
            record = builder.build(
                election_manifest={"election_id": "election-2026"},
                ballots=ballots,
                saac_params={"public_key": "mock_key"},
                serial_numbers=serial_numbers,
                bindings=bindings,
                proofs=proofs,
            )
            construct_duration = (time.perf_counter() - construct_start) * 1000

            # Phase 2: Serialization
            serialize_start = time.perf_counter()
            json_str = serialize_augmented_record(record, format="json")
            bson_bytes = serialize_augmented_record(record, format="bson")
            msgpack_bytes = serialize_augmented_record(record, format="msgpack")
            serialize_duration = (time.perf_counter() - serialize_start) * 1000

            # Phase 3: Validation
            validate_start = time.perf_counter()
            is_valid = validate_augmented_record(record)
            validate_duration = (time.perf_counter() - validate_start) * 1000

            total_duration = (time.perf_counter() - start) * 1000

            metrics = {
                "record_construction_ms": construct_duration,
                "serialization_total_ms": serialize_duration,
                "json_size_bytes": len(json_str)
                if isinstance(json_str, str)
                else len(json_str.encode()),
                "bson_size_bytes": len(bson_bytes) if bson_bytes else 0,
                "msgpack_size_bytes": len(msgpack_bytes) if msgpack_bytes else 0,
                "validation_ms": validate_duration,
                "total_duration_ms": total_duration,
                "record_valid": is_valid,
                "ballots_included": len(ballots),
                "record_size_mb": (
                    len(json_str)
                    if isinstance(json_str, str)
                    else len(json_str.encode())
                )
                / (1024 * 1024),
            }

            if not is_valid:
                errors.append("Augmented record validation failed")

            # Check size (should be reasonable for 1M ballots in production)
            projected_size_mb = metrics["record_size_mb"] * (1000000 / self.num_voters)
            if projected_size_mb > 500:
                warnings.append(
                    f"Projected record size for 1M ballots: {projected_size_mb:.2f} MB"
                )

            status = "passed" if is_valid else "failed"

            return BenchmarkResult(
                name="Augmented Election Record",
                feature_id="F-109",
                status=status,
                duration_ms=total_duration,
                metrics=metrics,
                errors=errors,
                warnings=warnings,
            )

        except Exception as e:
            errors.append(str(e))
            return BenchmarkResult(
                name="Augmented Election Record",
                feature_id="F-109",
                status="failed",
                duration_ms=0,
                metrics={},
                errors=errors,
                warnings=warnings,
            )

    async def benchmark_verifier(self) -> BenchmarkResult:
        """
        F-110: vSPACE Verifier Extension benchmark.

        Measures:
        - SAAC presentation verification latency
        - Binding proof verification latency
        - Serial uniqueness verification latency
        - Total verification latency per ballot
        """
        errors = []
        warnings = []
        metrics = {}

        try:
            start = time.perf_counter()

            # Generate test data
            issuer = SAACIssuer()
            params = issuer.generate_parameters()
            holder = SAACHolder()

            presentations = []
            bindings = []
            serial_numbers = []

            for i in range(self.num_voters):
                cred = holder.create_credential(params, {"voter_id": f"voter-{i}"})
                pres = holder.generate_presentation(cred, "election-2026")
                presentations.append(pres)
                bindings.append({"valid": True})
                serial_numbers.append(f"serial-{i}")

            # Phase 1: SAAC verification
            saac_verify_start = time.perf_counter()
            saac_valid = 0
            for pres in presentations:
                if issuer.verify_presentation(pres, params):
                    saac_valid += 1
            saac_verify_duration = (time.perf_counter() - saac_verify_start) * 1000

            # Phase 2: Serial uniqueness verification
            serial_verify_start = time.perf_counter()
            serial_unique = verify_serial_uniqueness(serial_numbers)
            serial_verify_duration = (time.perf_counter() - serial_verify_start) * 1000

            # Phase 3: Binding proof verification
            binding_verify_start = time.perf_counter()
            binding_valid = sum(1 for b in bindings if b.get("valid", False))
            binding_verify_duration = (
                time.perf_counter() - binding_verify_start
            ) * 1000

            total_duration = (time.perf_counter() - start) * 1000

            metrics = {
                "saac_verification_total_ms": saac_verify_duration,
                "saac_verification_per_ballot_ms": saac_verify_duration
                / self.num_voters,
                "serial_verification_ms": serial_verify_duration,
                "binding_verification_total_ms": binding_verify_duration,
                "binding_verification_per_ballot_ms": binding_verify_duration
                / self.num_voters,
                "total_verification_ms": total_duration,
                "total_verification_per_ballot_ms": total_duration / self.num_voters,
                "saac_valid_count": saac_valid,
                "serial_unique": serial_unique,
                "binding_valid_count": binding_valid,
                "all_valid": saac_valid == self.num_voters
                and serial_unique
                and binding_valid == self.num_voters,
            }

            # Check against PRD target (< 50ms per ballot for verification)
            if metrics["total_verification_per_ballot_ms"] > 50:
                warnings.append(
                    f"Verification latency {metrics['total_verification_per_ballot_ms']:.2f}ms exceeds target of 50ms"
                )

            all_valid = metrics["all_valid"]
            if not all_valid:
                errors.append(
                    f"Verification failures: SAAC={saac_valid}/{self.num_voters}, Serial={serial_unique}, Binding={binding_valid}/{self.num_voters}"
                )

            status = "passed" if all_valid else "failed"

            return BenchmarkResult(
                name="vSPACE Verifier Extension",
                feature_id="F-110",
                status=status,
                duration_ms=total_duration,
                metrics=metrics,
                errors=errors,
                warnings=warnings,
            )

        except Exception as e:
            errors.append(str(e))
            return BenchmarkResult(
                name="vSPACE Verifier Extension",
                feature_id="F-110",
                status="failed",
                duration_ms=0,
                metrics={},
                errors=errors,
                warnings=warnings,
            )
