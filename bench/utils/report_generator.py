"""
vSPACE Report Generator
========================

Generates HTML and text reports from benchmark results.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class ReportGenerator:
    """Generates benchmark reports."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_html_report(self, summary: Dict[str, Any]) -> Path:
        """Generate HTML report from benchmark summary."""
        html_path = (
            self.output_dir
            / f"benchmark_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
        )

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>vSPACE E2E Benchmark Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: #ecf0f1; padding: 20px; border-radius: 6px; text-align: center; }}
        .summary-card h3 {{ margin: 0; color: #7f8c8d; font-size: 14px; }}
        .summary-card .value {{ font-size: 36px; font-weight: bold; color: #2c3e50; margin: 10px 0; }}
        .summary-card.passed .value {{ color: #27ae60; }}
        .summary-card.failed .value {{ color: #e74c3c; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .status-passed {{ color: #27ae60; font-weight: bold; }}
        .status-failed {{ color: #e74c3c; font-weight: bold; }}
        .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .metric-label {{ font-weight: bold; color: #7f8c8d; }}
        .metric-value {{ font-size: 18px; color: #2c3e50; }}
        .errors {{ background: #fdedec; border-left: 4px solid #e74c3c; padding: 15px; margin: 20px 0; }}
        .warnings {{ background: #fef9e7; border-left: 4px solid #f39c12; padding: 15px; margin: 20px 0; }}
        .timestamp {{ color: #95a5a6; font-size: 12px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>vSPACE E2E MVP Benchmark Report</h1>
        <p class="timestamp">Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}</p>
        
        <h2>Executive Summary</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Total Duration</h3>
                <div class="value">{summary["benchmark_run"]["total_duration_ms"] / 1000:.2f}s</div>
            </div>
            <div class="summary-card passed">
                <h3>Passed</h3>
                <div class="value">{summary["summary"]["passed"]}</div>
            </div>
            <div class="summary-card failed">
                <h3>Failed</h3>
                <div class="value">{summary["summary"]["failed"]}</div>
            </div>
            <div class="summary-card">
                <h3>Pass Rate</h3>
                <div class="value">{summary["summary"]["pass_rate"]:.1f}%</div>
            </div>
        </div>
        
        <h2>Performance Metrics</h2>
        <div class="summary-grid">
            <div class="metric">
                <div class="metric-label">Average Duration</div>
                <div class="metric-value">{summary["performance"]["average_duration_ms"]:.2f} ms</div>
            </div>
            <div class="metric">
                <div class="metric-label">Median Duration</div>
                <div class="metric-value">{summary["performance"]["median_duration_ms"]:.2f} ms</div>
            </div>
            <div class="metric">
                <div class="metric-label">P95 Duration</div>
                <div class="metric-value">{summary["performance"]["p95_duration_ms"]:.2f} ms</div>
            </div>
            <div class="metric">
                <div class="metric-label">Min Duration</div>
                <div class="metric-value">{summary["performance"]["min_duration_ms"]:.2f} ms</div>
            </div>
            <div class="metric">
                <div class="metric-label">Max Duration</div>
                <div class="metric-value">{summary["performance"]["max_duration_ms"]:.2f} ms</div>
            </div>
        </div>
        
        <h2>Results by Category</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Total</th>
                <th>Passed</th>
                <th>Failed</th>
                <th>Avg Duration (ms)</th>
            </tr>
"""

        for cat, stats in summary["by_category"].items():
            html_content += f"""
            <tr>
                <td>{cat.title()}</td>
                <td>{stats["total"]}</td>
                <td class="status-passed">{stats["passed"]}</td>
                <td class="status-failed">{stats["failed"]}</td>
                <td>{stats["avg_duration_ms"]:.2f}</td>
            </tr>
"""

        html_content += """
        </table>
        
        <h2>Detailed Results</h2>
        <table>
            <tr>
                <th>Feature</th>
                <th>Benchmark</th>
                <th>Status</th>
                <th>Duration (ms)</th>
                <th>Key Metrics</th>
            </tr>
"""

        for result in summary["results"]:
            key_metric = (
                list(result["metrics"].items())[0][1] if result["metrics"] else "N/A"
            )
            status_class = (
                "status-passed" if result["status"] == "passed" else "status-failed"
            )
            html_content += f"""
            <tr>
                <td>{result["feature_id"]}</td>
                <td>{result["name"]}</td>
                <td class="{status_class}">{result["status"].upper()}</td>
                <td>{result["duration_ms"]:.2f}</td>
                <td>{key_metric}</td>
            </tr>
"""

        html_content += """
        </table>
"""

        if summary["errors"]:
            html_content += """
        <h2>Errors</h2>
        <div class="errors">
            <ul>
"""
            for error in summary["errors"][:10]:
                html_content += f"                <li>{error}</li>\n"
            html_content += """
            </ul>
        </div>
"""

        if summary["warnings"]:
            html_content += """
        <h2>Warnings</h2>
        <div class="warnings">
            <ul>
"""
            for warning in summary["warnings"][:10]:
                html_content += f"                <li>{warning}</li>\n"
            html_content += """
            </ul>
        </div>
"""

        html_content += """
    </div>
</body>
</html>
"""

        with open(html_path, "w") as f:
            f.write(html_content)

        return html_path
