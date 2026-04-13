#!/usr/bin/env python3
"""
vSPACE E2E MVP Simulation Benchmark Suite
==========================================

Comprehensive benchmarking covering all features from:
- README.md (F-001 to F-112)
- vSPACE_Autonomous_PRD_v260412a.json (F-100 to F-103, F-109, F-110)
- vSPACE_Augmented_PRD_v260412a.json (F-104 to F-108)

Usage:
    python run_benchmarks.py [--scenario NAME] [--voters N] [--output-dir PATH]

Examples:
    python run_benchmarks.py --scenario all --voters 100
    python run_benchmarks.py --scenario autonomous --voters 1000
    python run_benchmarks.py --scenario augmented --voters 100
"""

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import statistics

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bindings" / "python"))
sys.path.insert(0, str(Path(__file__).parent))

from scenarios.autonomous_benchmarks import AutonomousBenchmarkSuite
from scenarios.augmented_benchmarks import AugmentedBenchmarkSuite
from scenarios.core_benchmarks import CoreBenchmarkSuite
from metrics.collector import MetricsCollector
from utils.report_generator import ReportGenerator


@dataclass
class BenchmarkConfig:
    """Benchmark configuration."""

    scenario: str
    num_voters: int
    num_guardians: int
    threshold: int
    output_dir: str
    dry_run: bool
    verbose: bool
    save_metrics: bool


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


class E2EBenchmarkRunner:
    """
    Main E2E benchmark runner orchestrating all test scenarios.

    Covers:
    - Core ElectionGuard features (F-001 to F-012)
    - Autonomous vSPACE features (F-100 to F-103, F-109, F-110)
    - Augmented vSPACE features (F-104 to F-108)
    """

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize benchmark suites
        self.core_suite = CoreBenchmarkSuite(
            config.num_voters, config.num_guardians, config.threshold
        )
        self.autonomous_suite = AutonomousBenchmarkSuite(config.num_voters)
        self.augmented_suite = AugmentedBenchmarkSuite(
            config.num_voters, config.dry_run
        )

        # Initialize metrics collector
        self.metrics_collector = MetricsCollector(
            output_dir=self.output_dir / "metrics", save_metrics=config.save_metrics
        )

        # Results tracking
        self.results: List[BenchmarkResult] = []
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    def print_header(self):
        """Print benchmark header."""
        print("=" * 100)
        print(" vSPACE E2E MVP Simulation Benchmark Suite")
        print("=" * 100)
        print(f" Configuration:")
        print(f"   Scenario: {self.config.scenario}")
        print(f"   Voters: {self.config.num_voters}")
        print(
            f"   Guardians: {self.config.num_guardians} (threshold: {self.config.threshold})"
        )
        print(f"   Output: {self.output_dir}")
        print(f"   Dry-run: {self.config.dry_run}")
        print(f"   Verbose: {self.config.verbose}")
        print("=" * 100)

    def print_suite_header(self, suite_name: str, feature_range: str):
        """Print suite section header."""
        print(f"\n{'=' * 80}")
        print(f" {suite_name} ({feature_range})")
        print(f"{'=' * 80}")

    async def run_core_benchmarks(self) -> List[BenchmarkResult]:
        """Run Core ElectionGuard benchmarks (F-001 to F-012)."""
        self.print_suite_header("Core ElectionGuard Benchmarks", "F-001 to F-012")

        results = []

        # F-001: Modular Arithmetic
        print("\n[F-001] Modular Arithmetic Engine")
        result = await self.core_suite.benchmark_arithmetic()
        results.append(result)
        self.metrics_collector.record("F-001", result)

        # F-002: ElGamal Encryption
        print("\n[F-002] ElGamal Encryption System")
        result = await self.core_suite.benchmark_encryption()
        results.append(result)
        self.metrics_collector.record("F-002", result)

        # F-003: Chaum-Pedersen ZK Proofs
        print("\n[F-003] Chaum-Pedersen Zero-Knowledge Proofs")
        result = await self.core_suite.benchmark_zk_proofs()
        results.append(result)
        self.metrics_collector.record("F-003", result)

        # F-004: Hash and HMAC
        print("\n[F-004] Hash and HMAC Primitives")
        result = await self.core_suite.benchmark_hash()
        results.append(result)
        self.metrics_collector.record("F-004", result)

        # F-005: Precomputation Engine
        print("\n[F-005] Precomputation Engine")
        result = await self.core_suite.benchmark_precomputation()
        results.append(result)
        self.metrics_collector.record("F-005", result)

        # F-006: Election Manifest
        print("\n[F-006] Election Manifest Management")
        result = await self.core_suite.benchmark_manifest()
        results.append(result)
        self.metrics_collector.record("F-006", result)

        # F-007: Ballot Lifecycle
        print("\n[F-007] Ballot Lifecycle Management")
        result = await self.core_suite.benchmark_ballot_lifecycle()
        results.append(result)
        self.metrics_collector.record("F-007", result)

        # F-008: Encryption Workflow
        print("\n[F-008] Encryption Workflow Orchestration")
        result = await self.core_suite.benchmark_encryption_workflow()
        results.append(result)
        self.metrics_collector.record("F-008", result)

        # F-009: Cross-Language Bindings
        print("\n[F-009] Cross-Language Binding Layer")
        result = await self.core_suite.benchmark_bindings()
        results.append(result)
        self.metrics_collector.record("F-009", result)

        # F-010: MongoDB Persistence
        print("\n[F-010] MongoDB Persistence Layer")
        result = await self.core_suite.benchmark_persistence()
        results.append(result)
        self.metrics_collector.record("F-010", result)

        # F-011: CLI Tooling
        print("\n[F-011] CLI Tooling")
        result = await self.core_suite.benchmark_cli()
        results.append(result)
        self.metrics_collector.record("F-011", result)

        # F-012: Build System
        print("\n[F-012] Cross-Platform Build System")
        result = await self.core_suite.benchmark_build()
        results.append(result)
        self.metrics_collector.record("F-012", result)

        return results

    async def run_autonomous_benchmarks(self) -> List[BenchmarkResult]:
        """Run Autonomous vSPACE benchmarks (F-100 to F-103, F-109, F-110)."""
        self.print_suite_header(
            "Autonomous vSPACE Benchmarks", "F-100 to F-103, F-109, F-110"
        )

        results = []

        # F-100: SAAC Protocol
        print("\n[F-100] SAAC Protocol Implementation")
        result = await self.autonomous_suite.benchmark_saac()
        results.append(result)
        self.metrics_collector.record("F-100", result)

        # F-101: Multi-Holder BBS
        print("\n[F-101] Multi-Holder BBS Credentials")
        result = await self.autonomous_suite.benchmark_multiholder()
        results.append(result)
        self.metrics_collector.record("F-101", result)

        # F-102: Credential Binding
        print("\n[F-102] Credential-to-Ballot Binding")
        result = await self.autonomous_suite.benchmark_binding()
        results.append(result)
        self.metrics_collector.record("F-102", result)

        # F-103: One-Show Enforcement
        print("\n[F-103] One-Show Enforcement")
        result = await self.autonomous_suite.benchmark_serial()
        results.append(result)
        self.metrics_collector.record("F-103", result)

        # F-109: Augmented Election Record
        print("\n[F-109] Augmented Election Record")
        result = await self.autonomous_suite.benchmark_record()
        results.append(result)
        self.metrics_collector.record("F-109", result)

        # F-110: vSPACE Verifier
        print("\n[F-110] vSPACE Verifier Extension")
        result = await self.autonomous_suite.benchmark_verifier()
        results.append(result)
        self.metrics_collector.record("F-110", result)

        return results

    async def run_augmented_benchmarks(self) -> List[BenchmarkResult]:
        """Run Augmented vSPACE benchmarks (F-104 to F-108)."""
        self.print_suite_header("Augmented vSPACE Benchmarks", "F-104 to F-108")

        results = []

        # F-104: Entra Verified ID Bridge
        print("\n[F-104] Entra Verified ID Bridge")
        result = await self.augmented_suite.benchmark_entra()
        results.append(result)
        self.metrics_collector.record("F-104", result)

        # F-105: vSpaceVote.com PWA
        print("\n[F-105] vSpaceVote.com Voter-Facing PWA")
        result = await self.augmented_suite.benchmark_vspacevote()
        results.append(result)
        self.metrics_collector.record("F-105", result)

        # F-106: vSpaceWallet.com PWA
        print("\n[F-106] vSpaceWallet.com Credential Wallet PWA")
        result = await self.augmented_suite.benchmark_vspacewallet()
        results.append(result)
        self.metrics_collector.record("F-106", result)

        # F-107: Cross-Origin Communication
        print("\n[F-107] Cross-Origin Communication Protocol")
        result = await self.augmented_suite.benchmark_cross_origin()
        results.append(result)
        self.metrics_collector.record("F-107", result)

        # F-108: NLWeb Conversational Interfaces
        print("\n[F-108] NLWeb Conversational Interfaces")
        result = await self.augmented_suite.benchmark_nlweb()
        results.append(result)
        self.metrics_collector.record("F-108", result)

        return results

    async def run(self) -> Dict[str, Any]:
        """Execute complete benchmark suite."""
        self.start_time = datetime.utcnow()
        self.print_header()

        all_results = []

        # Run scenarios based on configuration
        if self.config.scenario in ["all", "core"]:
            results = await self.run_core_benchmarks()
            all_results.extend(results)

        if self.config.scenario in ["all", "autonomous"]:
            results = await self.run_autonomous_benchmarks()
            all_results.extend(results)

        if self.config.scenario in ["all", "augmented"]:
            results = await self.run_augmented_benchmarks()
            all_results.extend(results)

        self.results = all_results
        self.end_time = datetime.utcnow()

        # Generate summary
        summary = self.generate_summary()

        # Print summary
        self.print_summary(summary)

        # Save results
        self.save_results(summary)

        return summary

    def generate_summary(self) -> Dict[str, Any]:
        """Generate benchmark summary."""
        total_duration = (self.end_time - self.start_time).total_seconds() * 1000

        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        skipped = sum(1 for r in self.results if r.status == "skipped")

        durations = [r.duration_ms for r in self.results if r.status == "passed"]
        avg_duration = statistics.mean(durations) if durations else 0
        median_duration = statistics.median(durations) if durations else 0
        p95_duration = (
            sorted(durations)[int(len(durations) * 0.95)]
            if len(durations) > 20
            else max(durations)
            if durations
            else 0
        )

        # Group by feature category
        categories = {
            "core": [r for r in self.results if r.feature_id.startswith("F-0")],
            "autonomous": [
                r
                for r in self.results
                if r.feature_id
                in ["F-100", "F-101", "F-102", "F-103", "F-109", "F-110"]
            ],
            "augmented": [
                r
                for r in self.results
                if r.feature_id in ["F-104", "F-105", "F-106", "F-107", "F-108"]
            ],
        }

        summary = {
            "benchmark_run": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "total_duration_ms": total_duration,
                "scenario": self.config.scenario,
                "voters": self.config.num_voters,
                "guardians": self.config.num_guardians,
                "threshold": self.config.threshold,
            },
            "summary": {
                "total_benchmarks": len(self.results),
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "pass_rate": (passed / len(self.results) * 100) if self.results else 0,
            },
            "performance": {
                "average_duration_ms": avg_duration,
                "median_duration_ms": median_duration,
                "p95_duration_ms": p95_duration,
                "min_duration_ms": min(durations) if durations else 0,
                "max_duration_ms": max(durations) if durations else 0,
            },
            "by_category": {
                cat: {
                    "total": len(results),
                    "passed": sum(1 for r in results if r.status == "passed"),
                    "failed": sum(1 for r in results if r.status == "failed"),
                    "avg_duration_ms": statistics.mean(
                        [r.duration_ms for r in results if r.status == "passed"]
                    )
                    if results
                    else 0,
                }
                for cat, results in categories.items()
            },
            "results": [asdict(r) for r in self.results],
            "errors": [e for r in self.results for e in r.errors],
            "warnings": [w for r in self.results for w in r.warnings],
        }

        return summary

    def print_summary(self, summary: Dict[str, Any]):
        """Print benchmark summary."""
        print("\n" + "=" * 100)
        print(" BENCHMARK SUMMARY")
        print("=" * 100)

        print(
            f"\n  Total Duration: {summary['benchmark_run']['total_duration_ms']:.2f} ms ({summary['benchmark_run']['total_duration_ms'] / 1000:.2f} s)"
        )
        print(f"  Scenario: {summary['benchmark_run']['scenario']}")
        print(f"  Voters: {summary['benchmark_run']['voters']}")

        print(f"\n  Results:")
        print(
            f"    ✓ Passed: {summary['summary']['passed']}/{summary['summary']['total_benchmarks']} ({summary['summary']['pass_rate']:.1f}%)"
        )
        print(f"    ✗ Failed: {summary['summary']['failed']}")
        print(f"    - Skipped: {summary['summary']['skipped']}")

        print(f"\n  Performance:")
        print(f"    Average: {summary['performance']['average_duration_ms']:.2f} ms")
        print(f"    Median: {summary['performance']['median_duration_ms']:.2f} ms")
        print(f"    P95: {summary['performance']['p95_duration_ms']:.2f} ms")
        print(f"    Min: {summary['performance']['min_duration_ms']:.2f} ms")
        print(f"    Max: {summary['performance']['max_duration_ms']:.2f} ms")

        print(f"\n  By Category:")
        for cat, stats in summary["by_category"].items():
            print(
                f"    {cat.title()}: {stats['passed']}/{stats['total']} passed (avg: {stats['avg_duration_ms']:.2f} ms)"
            )

        if summary["errors"]:
            print(f"\n  Errors ({len(summary['errors'])}):")
            for error in summary["errors"][:10]:  # Show first 10
                print(f"    ✗ {error}")
            if len(summary["errors"]) > 10:
                print(f"    ... and {len(summary['errors']) - 10} more")

        print("\n" + "=" * 100)

    def save_results(self, summary: Dict[str, Any]):
        """Save benchmark results to files."""
        # Save JSON summary
        summary_path = (
            self.output_dir
            / "reports"
            / f"benchmark_summary_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        )
        summary_path.parent.mkdir(parents=True, exist_ok=True)

        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"\n  Results saved to: {summary_path}")

        # Generate HTML report
        report_gen = ReportGenerator(self.output_dir / "reports")
        html_path = report_gen.generate_html_report(summary)
        print(f"  HTML report: {html_path}")

        # Generate metrics CSV
        if self.config.save_metrics:
            metrics_path = self.metrics_collector.save_csv()
            print(f"  Metrics CSV: {metrics_path}")


async def main():
    parser = argparse.ArgumentParser(
        description="vSPACE E2E MVP Simulation Benchmark Suite"
    )
    parser.add_argument(
        "--scenario",
        "-s",
        type=str,
        default="all",
        choices=["all", "core", "autonomous", "augmented"],
        help="Benchmark scenario to run (default: all)",
    )
    parser.add_argument(
        "--voters",
        "-n",
        type=int,
        default=100,
        help="Number of voters to simulate (default: 100)",
    )
    parser.add_argument(
        "--guardians",
        "-g",
        type=int,
        default=5,
        help="Number of guardians (default: 5)",
    )
    parser.add_argument(
        "--threshold", "-t", type=int, default=3, help="Guardian threshold (default: 3)"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default=None,
        help="Output directory (default: ./bench/output)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Enable dry-run mode (mock external services)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--save-metrics",
        action="store_true",
        default=True,
        help="Save detailed metrics (default: true)",
    )

    args = parser.parse_args()

    config = BenchmarkConfig(
        scenario=args.scenario,
        num_voters=args.voters,
        num_guardians=args.guardians,
        threshold=args.threshold,
        output_dir=args.output_dir or str(Path(__file__).parent / "output"),
        dry_run=args.dry_run,
        verbose=args.verbose,
        save_metrics=args.save_metrics,
    )

    runner = E2EBenchmarkRunner(config)
    summary = await runner.run()

    # Exit with error code if any benchmarks failed
    if summary["summary"]["failed"] > 0:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
