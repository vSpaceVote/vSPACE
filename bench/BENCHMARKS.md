# vSPACE E2E MVP Simulation Benchmark Suite

Comprehensive benchmarking suite covering all features from the vSPACE technical specification and PRD documents.

## Table of Contents

- [Overview](#overview)
- [Benchmark Scenarios](#benchmark-scenarios)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Performance Targets](#performance-targets)
- [Output and Reporting](#output-and-reporting)
- [Interpreting Results](#interpreting-results)
- [CI/CD Integration](#cicd-integration)

---

## Overview

The vSPACE E2E MVP Simulation Benchmark Suite provides comprehensive performance testing for all features defined in:

1. **README.md** - Full technical specification (F-001 to F-112)
2. **vSPACE_Autonomous_PRD_v260412a.json** - Autonomous features (F-100 to F-103, F-109, F-110)
3. **vSPACE_Augmented_PRD_v260412a.json** - Augmented features (F-104 to F-108)

### Benchmark Categories

| Category | Features | Description |
|----------|----------|-------------|
| **Core** | F-001 to F-012 | ElectionGuard cryptographic foundation and infrastructure |
| **Autonomous** | F-100, F-101, F-102, F-103, F-109, F-110 | vSPACE anonymous credential and verification features |
| **Augmented** | F-104, F-105, F-106, F-107, F-108 | Azure-dependent identity and PWA features |

### Directory Structure

```
bench/
├── run_benchmarks.py          # Main benchmark runner
├── scenarios/
│   ├── core_benchmarks.py     # F-001 to F-012
│   ├── autonomous_benchmarks.py # F-100, F-101, F-102, F-103, F-109, F-110
│   └── augmented_benchmarks.py  # F-104, F-105, F-106, F-107, F-108
├── metrics/
│   └── collector.py           # Metrics collection and export
├── utils/
│   ├── benchmark_helpers.py   # Mock data generators
│   └── report_generator.py    # HTML report generation
├── output/                     # Benchmark output directory
│   ├── reports/               # JSON and HTML reports
│   └── metrics/               # CSV metrics exports
└── BENCHMARKS.md              # This documentation
```

---

## Benchmark Scenarios

### Core ElectionGuard Benchmarks (F-001 to F-012)

| Feature | Benchmark Name | Key Metrics | PRD Target |
|---------|---------------|-------------|------------|
| F-001 | Modular Arithmetic Engine | ops/sec, modular exp latency | >100K ops/sec |
| F-002 | ElGamal Encryption System | encryption/decryption latency | <200ms per ballot |
| F-003 | Chaum-Pedersen ZK Proofs | proof generation/verification | <50ms per proof |
| F-004 | Hash and HMAC Primitives | SHA-256/HMAC latency | <1ms per hash |
| F-005 | Precomputation Engine | buffer fill time, refill rate | Non-blocking |
| F-006 | Election Manifest Management | generation, validation latency | <20ms total |
| F-007 | Ballot Lifecycle Management | state transitions, serialization | <5ms per ballot |
| F-008 | Encryption Workflow Orchestration | end-to-end encryption | <200ms per ballot |
| F-009 | Cross-Language Binding Layer | C ABI, .NET, TypeScript overhead | <2ms overhead |
| F-010 | MongoDB Persistence Layer | insert, query, index latency | <10ms per operation |
| F-011 | CLI Tooling | startup, artifact generation | <200ms total |
| F-012 | Cross-Platform Build System | configure, build, test time | <30s total |

### Autonomous vSPACE Benchmarks (F-100 to F-103, F-109, F-110)

| Feature | Benchmark Name | Key Metrics | PRD Target |
|---------|---------------|-------------|------------|
| F-100 | SAAC Protocol | issuance, presentation, verification | <50ms verification |
| F-101 | Multi-Holder BBS | splitting, threshold presentation | <200ms per operation |
| F-102 | Credential Binding | commitment, proof generation/verification | <50ms per ballot |
| F-103 | One-Show Enforcement | serial derivation, uniqueness check | <10ms per voter |
| F-109 | Augmented Election Record | construction, serialization, validation | <5s for 1M ballots |
| F-110 | vSPACE Verifier | end-to-end verification | <50ms per ballot |

### Augmented vSPACE Benchmarks (F-104 to F-108)

| Feature | Benchmark Name | Key Metrics | PRD Target |
|---------|---------------|-------------|------------|
| F-104 | Entra Verified ID Bridge | VC issuance, presentation, derivation | <2000ms issuance, <1500ms presentation |
| F-105 | vSpaceVote.com PWA | HTMX partial response, size | <200ms, <2KB |
| F-106 | vSpaceWallet.com PWA | IndexedDB encryption, credential operations | <50ms encryption |
| F-107 | Cross-Origin Communication | postMessage, QR generation, WebSocket | <50ms total, <100ms QR |
| F-108 | NLWeb Conversational Interfaces | query response, vector search, LLM | <500ms total, 100% grounding |

---

## Quick Start

### Run All Benchmarks (Default)

```bash
cd bench
python run_benchmarks.py --voters 100
```

### Run Specific Scenario

```bash
# Core ElectionGuard features only
python run_benchmarks.py --scenario core --voters 1000

# Autonomous vSPACE features only
python run_benchmarks.py --scenario autonomous --voters 100

# Augmented vSPACE features only (dry-run mode)
python run_benchmarks.py --scenario augmented --voters 100 --dry-run
```

### Production-Scale Simulation

```bash
# 10,000 voters (Phase 4 target)
python run_benchmarks.py --voters 10000 --guardians 10 --threshold 6
```

---

## Usage

### Command-Line Options

```
usage: run_benchmarks.py [-h] [--scenario {all,core,autonomous,augmented}]
                         [--voters N] [--guardians N] [--threshold N]
                         [--output-dir PATH] [--dry-run] [--verbose]
                         [--save-metrics]

vSPACE E2E MVP Simulation Benchmark Suite

optional arguments:
  -h, --help            show this help message and exit
  --scenario, -s {all,core,autonomous,augmented}
                        Benchmark scenario to run (default: all)
  --voters, -n N        Number of voters to simulate (default: 100)
  --guardians, -g N     Number of guardians (default: 5)
  --threshold, -t N     Guardian threshold (default: 3)
  --output-dir, -o PATH
                        Output directory (default: ./bench/output)
  --dry-run             Enable dry-run mode (mock external services)
  --verbose, -v         Enable verbose output
  --save-metrics        Save detailed metrics (default: true)
```

### Programmatic Usage

```python
import asyncio
from bench.run_benchmarks import E2EBenchmarkRunner, BenchmarkConfig

async def run_custom_benchmark():
    config = BenchmarkConfig(
        scenario="autonomous",
        num_voters=500,
        num_guardians=7,
        threshold=4,
        output_dir="./custom_output",
        dry_run=True,
        verbose=True,
        save_metrics=True
    )
    
    runner = E2EBenchmarkRunner(config)
    summary = await runner.run()
    
    print(f"Pass rate: {summary['summary']['pass_rate']:.1f}%")
    print(f"Total duration: {summary['benchmark_run']['total_duration_ms']/1000:.2f}s")

asyncio.run(run_custom_benchmark())
```

---

## Performance Targets

### Phase Gate Acceptance Criteria

#### Phase 1 (TRL 3) - Foundation
- ✅ All SAAC, Multi-Holder, and binding unit tests pass
- ✅ 10-voter, 3-guardian, 2-of-3 threshold simulation produces verifiable augmented election record
- ✅ Credential verification < 500ms (Python reference)

#### Phase 2 (TRL 4) - Entra Integration
- ✅ Entra sandbox issuance/presentation flows succeed
- ✅ Oblivious credential derivation works
- ✅ 100-voter simulation with live Entra VCs
- ✅ VC issuance < 2000ms, presentation < 1500ms

#### Phase 3 (TRL 5) - Production Hardening
- ✅ C++ bit-identical to Python reference
- ✅ Credential verification < 50ms (C++ production)
- ✅ Rust verifier validates all records
- ✅ Docker health check < 60s

#### Phase 4 (TRL 6) - Validation
- ✅ 1,000,000-voter simulation in < 24 hours (16-core, 64GB RAM)
- ✅ External cryptographer review completed
- ✅ No critical security audit findings
- ✅ Non-Microsoft wallet interoperability verified

### Key Performance Indicators (KPIs)

| KPI | Target | Measurement |
|-----|--------|-------------|
| Ballot encryption latency | < 200ms | Load testing |
| Credential verification | < 50ms | Benchmarked on Intel Xeon E5-2680 |
| HTMX partial response | < 200ms | Browser network timing |
| NLWeb query response | < 500ms | End-to-end timing |
| Cross-platform build success | 100% | GitHub Actions CI matrix |
| Serial number uniqueness check | O(n log n) | Sort-based verification |

---

## Output and Reporting

### Generated Files

After running benchmarks, the following files are generated in `bench/output/`:

```
output/
├── reports/
│   ├── benchmark_summary_YYYYMMDD_HHMMSS.json    # Full JSON summary
│   └── benchmark_report_YYYYMMDD_HHMMSS.html     # HTML report with charts
└── metrics/
    └── metrics_YYYYMMDD_HHMMSS.csv               # Detailed metrics CSV
```

### JSON Summary Structure

```json
{
  "benchmark_run": {
    "start_time": "2026-04-13T09:00:00.000000",
    "end_time": "2026-04-13T09:05:00.000000",
    "total_duration_ms": 300000.0,
    "scenario": "all",
    "voters": 100,
    "guardians": 5,
    "threshold": 3
  },
  "summary": {
    "total_benchmarks": 19,
    "passed": 18,
    "failed": 1,
    "skipped": 0,
    "pass_rate": 94.7
  },
  "performance": {
    "average_duration_ms": 157.89,
    "median_duration_ms": 120.50,
    "p95_duration_ms": 450.20,
    "min_duration_ms": 5.30,
    "max_duration_ms": 890.10
  },
  "by_category": {
    "core": { "total": 12, "passed": 12, "failed": 0, "avg_duration_ms": 100.5 },
    "autonomous": { "total": 6, "passed": 5, "failed": 1, "avg_duration_ms": 250.3 },
    "augmented": { "total": 5, "passed": 5, "failed": 0, "avg_duration_ms": 180.7 }
  },
  "results": [...],
  "errors": [...],
  "warnings": [...]
}
```

### HTML Report

The HTML report includes:
- Executive summary with key metrics
- Performance charts (average, median, P95)
- Results breakdown by category
- Detailed table of all benchmarks
- Error and warning sections

Open the HTML file in any browser to view the interactive report.

---

## Interpreting Results

### Status Codes

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| **passed** | Benchmark met all acceptance criteria | None |
| **failed** | Benchmark failed one or more criteria | Investigate errors, optimize implementation |
| **skipped** | Benchmark was skipped (missing dependency, dry-run mode) | Enable required configuration |

### Performance Warnings

Warnings are generated when benchmarks pass but exceed recommended targets:

```
⚠ Verification latency 65.3ms exceeds target of 50ms
⚠ Projected record size for 1M ballots: 620.5 MB
```

These indicate potential optimization opportunities but do not cause benchmark failure.

### Error Categories

| Error Type | Description | Resolution |
|------------|-------------|------------|
| Cryptographic failure | SAAC/BBS verification failed | Check implementation correctness |
| Duplicate serial | One-show enforcement detected duplicate | Verify VRF derivation logic |
| Timeout | Benchmark exceeded maximum allowed time | Optimize algorithm or increase resources |
| Missing dependency | Required library or service unavailable | Install dependency or enable dry-run mode |

---

## CI/CD Integration

### GitHub Actions Workflow

Add the following workflow to `.github/workflows/benchmarks.yml`:

```yaml
name: vSPACE Benchmarks

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  benchmarks:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        scenario: [core, autonomous, augmented]
        voters: [100, 1000]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run benchmarks
        run: |
          cd bench
          python run_benchmarks.py \
            --scenario ${{ matrix.scenario }} \
            --voters ${{ matrix.voters }} \
            --output-dir ./output \
            --save-metrics
      
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results-${{ matrix.scenario }}-${{ matrix.voters }}
          path: bench/output/
      
      - name: Check for failures
        run: |
          cd bench/output/reports
          python -c "
          import json
          with open('$(ls benchmark_summary_*.json | head -1)') as f:
              summary = json.load(f)
          if summary['summary']['failed'] > 0:
              exit(1)
          "
```

### Performance Regression Detection

To detect performance regressions:

1. Store baseline metrics from each successful run
2. Compare new results against baseline
3. Flag any benchmark that exceeds baseline by >20%

Example regression check script:

```python
import json

def check_regression(current: dict, baseline: dict, threshold: float = 0.20):
    regressions = []
    
    for result in current['results']:
        feature_id = result['feature_id']
        baseline_result = next(
            (r for r in baseline['results'] if r['feature_id'] == feature_id),
            None
        )
        
        if baseline_result:
            duration_increase = (
                (result['duration_ms'] - baseline_result['duration_ms']) /
                baseline_result['duration_ms']
            )
            
            if duration_increase > threshold:
                regressions.append({
                    'feature': feature_id,
                    'increase': f"{duration_increase*100:.1f}%",
                    'current': result['duration_ms'],
                    'baseline': baseline_result['duration_ms']
                })
    
    return regressions
```

---

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'electionguard_vspace'"

**Solution**: Ensure Python path includes the bindings directory:
```bash
export PYTHONPATH="$PWD/bindings/python:$PYTHONPATH"
```

#### Benchmark timeout on large voter counts

**Solution**: Reduce voter count or increase timeout:
```bash
python run_benchmarks.py --voters 100  # Start small
```

#### Dry-run mode not working

**Solution**: Explicitly enable dry-run flag:
```bash
python run_benchmarks.py --dry-run
```

### Getting Help

1. Check benchmark logs in `bench/output/reports/`
2. Review error messages in JSON summary
3. Consult README.md for architecture details
4. Open GitHub issue with benchmark results attached

---

**Document Version**: 1.0.0  
**Last Updated**: 2026-04-13  
**Related Documents**: README.md, vSPACE_Autonomous_PRD_v260412a.json, vSPACE_Augmented_PRD_v260412a.json, SETUP.md
