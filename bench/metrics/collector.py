"""
vSPACE Metrics Collector
=========================

Collects and exports benchmark metrics.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from .benchmark_helpers import BenchmarkResult


class MetricsCollector:
    """Collects and exports benchmark metrics."""

    def __init__(self, output_dir: str, save_metrics: bool = True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.save_metrics = save_metrics
        self.metrics_data: List[Dict[str, Any]] = []

    def record(self, feature_id: str, result: BenchmarkResult):
        """Record a benchmark result."""
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "feature_id": feature_id,
            "benchmark_name": result.name,
            "status": result.status,
            "duration_ms": result.duration_ms,
            "metrics": json.dumps(result.metrics),
            "errors": json.dumps(result.errors),
            "warnings": json.dumps(result.warnings),
        }
        self.metrics_data.append(record)

    def save_csv(self) -> Path:
        """Save metrics to CSV file."""
        if not self.metrics_data or not self.save_metrics:
            return None

        csv_path = (
            self.output_dir
            / f"metrics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.metrics_data[0].keys())
            writer.writeheader()
            writer.writerows(self.metrics_data)

        return csv_path

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        if not self.metrics_data:
            return {}

        total = len(self.metrics_data)
        passed = sum(1 for m in self.metrics_data if m["status"] == "passed")
        failed = sum(1 for m in self.metrics_data if m["status"] == "failed")

        durations = [
            m["duration_ms"] for m in self.metrics_data if m["status"] == "passed"
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0

        return {
            "total_benchmarks": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "average_duration_ms": avg_duration,
        }
