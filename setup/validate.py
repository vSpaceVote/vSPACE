#!/usr/bin/env python3
"""
vSPACE Configuration Validator
===============================

Validates environment configuration and Azure service connections.

Usage:
    python validate.py [--strict]

Options:
    --strict    Fail on any missing configuration (default: warn only)
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple


class ConfigurationValidator:
    """Validate vSPACE configuration and service connections."""

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.env_file = Path(__file__).parent / ".env"
        self.errors = []
        self.warnings = []
        self.successes = []
        self.config = {}

    def load_env(self) -> bool:
        """Load .env file."""
        if not self.env_file.exists():
            self.errors.append(".env file not found. Run wizard.py first.")
            return False

        # Parse .env file
        with open(self.env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    self.config[key.strip()] = value.strip()

        return True

    def validate_required_vars(self) -> bool:
        """Validate required environment variables."""
        print("\n[Validation] Required Environment Variables")
        print("-" * 60)

        required_groups = {
            "Entra Verified ID (F-104)": [
                "AZURE_ENTRA_TENANT_ID",
                "AZURE_AD_APP_CLIENT_ID",
                "AZURE_AD_APP_CLIENT_SECRET",
            ],
            "Azure OpenAI (F-108)": ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY"],
            "Azure AI Search (F-108)": [
                "AZURE_AI_SEARCH_ENDPOINT",
                "AZURE_AI_SEARCH_API_KEY",
            ],
            "Azure Cosmos DB (F-010, F-103, F-109)": [
                "AZURE_COSMOS_DB_CONNECTION_STRING"
            ],
        }

        all_valid = True

        for group, vars in required_groups.items():
            print(f"\n  {group}:")
            missing = []

            for var in vars:
                if var in self.config and self.config[var]:
                    # Mask secrets in output
                    value = self.config[var]
                    masked = (
                        value[:4] + "..." + value[-4:] if len(value) > 8 else "****"
                    )
                    self.successes.append(f"{var}={masked}")
                    print(f"    ✓ {var}")
                else:
                    missing.append(var)
                    all_valid = False

            if missing:
                for var in missing:
                    self.errors.append(f"Missing required variable: {var}")
                    print(f"    ✗ {var} (MISSING)")

        return all_valid

    def validate_optional_vars(self):
        """Validate optional environment variables."""
        print("\n[Validation] Optional Environment Variables")
        print("-" * 60)

        optional = {
            "AZURE_SUBSCRIPTION_ID": "Azure Subscription",
            "AZURE_KEY_VAULT_URI": "Azure Key Vault",
            "AZURE_APP_SERVICE_VSPACEVOTE_NAME": "vSpaceVote.com App Service",
            "AZURE_APP_SERVICE_VSPACEWALLET_NAME": "vSpaceWallet.com App Service",
            "APPLICATIONINSIGHTS_CONNECTION_STRING": "Application Insights",
        }

        for var, description in optional.items():
            if var in self.config and self.config[var]:
                print(f"  ✓ {description}: {var}")
                self.successes.append(f"Optional: {var}")
            else:
                print(f"  - {description}: Not configured")
                self.warnings.append(f"Optional variable not set: {var}")

    def validate_dry_run_mode(self) -> bool:
        """Check if dry-run mode is enabled."""
        print("\n[Validation] Development Mode")
        print("-" * 60)

        dry_run = self.config.get("VSPACE_DRY_RUN", "false").lower() == "true"

        if dry_run:
            print("  ✓ Dry-run mode ENABLED")
            print("    - Azure API calls will be mocked")
            print("    - Safe for local testing")
            self.successes.append("Dry-run mode enabled")
            return True
        else:
            print("  ⚠ Dry-run mode DISABLED")
            print("    - Will attempt actual Azure API calls")
            print("    - Ensure all credentials are valid")
            self.warnings.append("Dry-run mode disabled - production mode active")
            return False

    async def test_entra_connection(self) -> bool:
        """Test Entra Verified ID connection."""
        print("\n[Validation] Entra Verified ID Connection Test")
        print("-" * 60)

        if self.config.get("VSPACE_DRY_RUN", "true").lower() == "true":
            print("  ⚠ Skipping test (dry-run mode)")
            return True

        # Check required credentials
        required = [
            "AZURE_ENTRA_TENANT_ID",
            "AZURE_AD_APP_CLIENT_ID",
            "AZURE_AD_APP_CLIENT_SECRET",
        ]
        if not all(self.config.get(var) for var in required):
            print("  ✗ Missing credentials for Entra test")
            return False

        # TODO: Implement actual Entra API test
        # This would:
        # 1. Acquire OAuth2 token using MSAL
        # 2. Call createIssuanceRequest API
        # 3. Verify response

        print("  ⚠ Connection test not implemented")
        print(
            "    - Would test: POST /v1.0/verifiableCredentials/createIssuanceRequest"
        )
        self.warnings.append("Entra connection test not implemented")
        return True

    async def test_openai_connection(self) -> bool:
        """Test Azure OpenAI connection."""
        print("\n[Validation] Azure OpenAI Connection Test")
        print("-" * 60)

        if self.config.get("VSPACE_DRY_RUN", "true").lower() == "true":
            print("  ⚠ Skipping test (dry-run mode)")
            return True

        if not all(
            [
                self.config.get("AZURE_OPENAI_ENDPOINT"),
                self.config.get("AZURE_OPENAI_API_KEY"),
            ]
        ):
            print("  ✗ Missing credentials for OpenAI test")
            return False

        # TODO: Implement actual OpenAI API test
        print("  ⚠ Connection test not implemented")
        print("    - Would test: ChatCompletions API")
        self.warnings.append("OpenAI connection test not implemented")
        return True

    async def test_cosmos_connection(self) -> bool:
        """Test Azure Cosmos DB connection."""
        print("\n[Validation] Azure Cosmos DB Connection Test")
        print("-" * 60)

        if self.config.get("VSPACE_DRY_RUN", "true").lower() == "true":
            print("  ⚠ Skipping test (dry-run mode)")
            return True

        if not self.config.get("AZURE_COSMOS_DB_CONNECTION_STRING"):
            print("  ✗ Missing connection string for Cosmos DB test")
            return False

        # TODO: Implement actual Cosmos DB test
        print("  ⚠ Connection test not implemented")
        print("    - Would test: MongoDB API connection")
        print("    - Would verify: vspace_serial_numbers collection exists")
        self.warnings.append("Cosmos DB connection test not implemented")
        return True

    def validate_vspace_config(self) -> bool:
        """Validate vSPACE-specific configuration."""
        print("\n[Validation] vSPACE Configuration")
        print("-" * 60)

        # SAAC curve
        curve = self.config.get("VSPACE_SAAC_CURVE", "P-256")
        if curve in ["P-256", "P-384"]:
            print(f"  ✓ SAAC Curve: {curve}")
            self.successes.append(f"SAAC curve: {curve}")
        else:
            print(f"  ✗ Invalid SAAC curve: {curve} (must be P-256 or P-384)")
            self.errors.append(f"Invalid SAAC curve: {curve}")
            return False

        # Multi-holder threshold
        try:
            threshold = int(self.config.get("VSPACE_MULTIHOLDER_THRESHOLD", "2"))
            total = int(self.config.get("VSPACE_MULTIHOLDER_TOTAL", "2"))

            if 1 <= threshold <= total:
                print(f"  ✓ Multi-Holder: {threshold}-of-{total}")
                self.successes.append(f"Multi-holder threshold: {threshold}-of-{total}")
            else:
                print(f"  ✗ Invalid threshold: {threshold}-of-{total}")
                self.errors.append(
                    f"Invalid multi-holder threshold: {threshold}-of-{total}"
                )
                return False
        except ValueError:
            print(f"  ✗ Invalid multi-holder configuration")
            self.errors.append("Multi-holder threshold must be integers")
            return False

        return True

    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        report = {
            "validation_timestamp": datetime.utcnow().isoformat(),
            "strict_mode": self.strict,
            "env_file": str(self.env_file),
            "summary": {
                "total_checks": len(self.successes)
                + len(self.errors)
                + len(self.warnings),
                "passed": len(self.successes),
                "warnings": len(self.warnings),
                "errors": len(self.errors),
            },
            "successes": self.successes,
            "warnings": self.warnings,
            "errors": self.errors,
            "configuration": {
                "dry_run_enabled": self.config.get("VSPACE_DRY_RUN", "true").lower()
                == "true",
                "log_level": self.config.get("VSPACE_LOG_LEVEL", "INFO"),
                "saac_curve": self.config.get("VSPACE_SAAC_CURVE", "P-256"),
                "multi_holder_threshold": self.config.get(
                    "VSPACE_MULTIHOLDER_THRESHOLD", "2"
                ),
            },
        }

        # Save report
        report_path = Path(__file__).parent / "validation_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        return report

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 80)
        print(" Validation Summary")
        print("=" * 80)

        print(
            f"\n  Total Checks: {len(self.successes) + len(self.errors) + len(self.warnings)}"
        )
        print(f"  ✓ Passed: {len(self.successes)}")
        print(f"  ⚠ Warnings: {len(self.warnings)}")
        print(f"  ✗ Errors: {len(self.errors)}")

        if self.errors:
            print("\n  Errors:")
            for error in self.errors:
                print(f"    ✗ {error}")

        if self.warnings:
            print("\n  Warnings:")
            for warning in self.warnings:
                print(f"    ⚠ {warning}")

        # Determine overall status
        if self.errors:
            if self.strict:
                print("\n  Status: FAILED (strict mode)")
                return False
            else:
                print("\n  Status: PASSED with errors (warnings only)")
                return True
        else:
            print("\n  Status: PASSED")
            return True

    async def run(self) -> bool:
        """Execute complete validation."""
        print("=" * 80)
        print(" vSPACE Configuration Validator")
        print("=" * 80)

        # Load environment
        if not self.load_env():
            print("\n  ✗ Failed to load .env file")
            return False

        print(f"  ✓ Loaded: {self.env_file}")
        print(f"    Configuration entries: {len(self.config)}")

        # Run validations
        env_valid = self.validate_required_vars()
        self.validate_optional_vars()
        self.validate_dry_run_mode()
        config_valid = self.validate_vspace_config()

        # Connection tests
        await self.test_entra_connection()
        await self.test_openai_connection()
        await self.test_cosmos_connection()

        # Generate report
        report = self.generate_validation_report()

        # Print summary
        overall_valid = self.print_summary()

        print(
            f"\n  Report saved to: {Path(__file__).parent / 'validation_report.json'}"
        )
        print()

        return overall_valid


async def main():
    import argparse

    parser = argparse.ArgumentParser(description="vSPACE Configuration Validator")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on any missing configuration (default: warn only)",
    )

    args = parser.parse_args()

    validator = ConfigurationValidator(strict=args.strict)
    success = await validator.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
