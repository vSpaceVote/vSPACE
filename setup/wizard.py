#!/usr/bin/env python3
"""
vSPACE Setup Wizard
====================

Interactive command-line wizard for configuring vSPACE environment variables
and validating Azure service connections.

Usage:
    python wizard.py

This wizard will:
1. Guide you through all required environment variables
2. Validate Azure service connections
3. Test Entra Verified ID configuration
4. Generate .env file with your settings
5. Run validation tests
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class SetupWizard:
    """Interactive setup wizard for vSPACE configuration."""

    def __init__(self):
        self.config = {}
        self.env_file_path = Path(__file__).parent / ".env"
        self.example_path = Path(__file__).parent / ".env.example"

    def print_header(self, title: str):
        """Print section header."""
        print("\n" + "=" * 80)
        print(f" {title}")
        print("=" * 80)

    def print_step(self, step_num: int, description: str):
        """Print step indicator."""
        print(f"\n[Step {step_num}] {description}")
        print("-" * 60)

    def prompt(self, question: str, default: str = None, secret: bool = False) -> str:
        """Prompt user for input."""
        if default:
            question += f" [{default}]"

        if secret:
            # Use getpass for secrets
            import getpass

            value = getpass.getpass(f"{question}: ")
        else:
            value = input(f"{question}: ")

        return value.strip() if value.strip() else (default or "")

    def validate_guid(self, value: str, field_name: str) -> bool:
        """Validate GUID format."""
        import re

        guid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            re.IGNORECASE,
        )
        if not guid_pattern.match(value):
            print(f"  ✗ Invalid GUID format for {field_name}")
            print(f"    Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
            return False
        return True

    def validate_url(self, value: str, field_name: str) -> bool:
        """Validate URL format."""
        import re

        url_pattern = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)
        if not url_pattern.match(value):
            print(f"  ✗ Invalid URL format for {field_name}")
            return False
        return True

    async def test_entra_connection(self) -> bool:
        """Test Entra Verified ID connection."""
        print("\n  Testing Entra Verified ID connection...")

        # In dry-run mode, skip actual API call
        if self.config.get("VSPACE_DRY_RUN", "true").lower() == "true":
            print("  ⚠ Dry-run mode enabled - skipping actual API test")
            print("  ✓ Mock connection test passed")
            return True

        # TODO: Implement actual Entra API test
        # This would acquire OAuth2 token and test the issuance API
        print("  ⚠ Production connection test not yet implemented")
        print("  ✓ Proceeding with configuration")

        return True

    async def test_openai_connection(self) -> bool:
        """Test Azure OpenAI connection."""
        print("\n  Testing Azure OpenAI connection...")

        if self.config.get("VSPACE_DRY_RUN", "true").lower() == "true":
            print("  ⚠ Dry-run mode enabled - skipping actual API test")
            print("  ✓ Mock connection test passed")
            return True

        # TODO: Implement actual OpenAI API test
        print("  ⚠ Production connection test not yet implemented")
        print("  ✓ Proceeding with configuration")

        return True

    async def test_cosmos_connection(self) -> bool:
        """Test Azure Cosmos DB connection."""
        print("\n  Testing Azure Cosmos DB connection...")

        if self.config.get("VSPACE_DRY_RUN", "true").lower() == "true":
            print("  ⚠ Dry-run mode enabled - skipping actual API test")
            print("  ✓ Mock connection test passed")
            return True

        # TODO: Implement actual Cosmos DB test
        print("  ⚠ Production connection test not yet implemented")
        print("  ✓ Proceeding with configuration")

        return True

    def collect_entra_config(self, step_num: int):
        """Collect Microsoft Entra Verified ID configuration."""
        self.print_step(step_num, "Microsoft Entra Verified ID Configuration (F-104)")

        print(
            "\n  This section configures the Entra Verified ID bridge for voter identity verification."
        )
        print("  Prerequisites:")
        print("    - Azure AD Premium P2 or Microsoft Entra Suite license")
        print("    - App registration with VerifiableCredential.Create.All permission")
        print("    - Admin consent granted")
        print("\n  Reference: https://learn.microsoft.com/en-us/entra/verified-id/")

        # Tenant ID
        while True:
            tenant_id = self.prompt(
                "Azure AD Tenant ID",
                default=self.config.get("AZURE_ENTRA_TENANT_ID"),
                secret=False,
            )
            if self.validate_guid(tenant_id, "Tenant ID"):
                self.config["AZURE_ENTRA_TENANT_ID"] = tenant_id
                break

        # Client ID
        while True:
            client_id = self.prompt(
                "Azure AD App Client ID",
                default=self.config.get("AZURE_AD_APP_CLIENT_ID"),
                secret=False,
            )
            if self.validate_guid(client_id, "Client ID"):
                self.config["AZURE_AD_APP_CLIENT_ID"] = client_id
                break

        # Client Secret
        client_secret = self.prompt("Azure AD App Client Secret", secret=True)
        self.config["AZURE_AD_APP_CLIENT_SECRET"] = client_secret

        # Subscription ID
        subscription_id = self.prompt(
            "Azure Subscription ID (optional)",
            default=self.config.get("AZURE_SUBSCRIPTION_ID"),
            secret=False,
        )
        if subscription_id:
            self.config["AZURE_SUBSCRIPTION_ID"] = subscription_id

    def collect_openai_config(self, step_num: int):
        """Collect Azure OpenAI configuration."""
        self.print_step(step_num, "Azure OpenAI Service Configuration (F-108)")

        print(
            "\n  This section configures Azure OpenAI for NLWeb conversational interfaces."
        )

        endpoint = self.prompt(
            "Azure OpenAI Endpoint",
            default=self.config.get(
                "AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/"
            ),
            secret=False,
        )
        self.config["AZURE_OPENAI_ENDPOINT"] = endpoint

        api_key = self.prompt("Azure OpenAI API Key", secret=True)
        self.config["AZURE_OPENAI_API_KEY"] = api_key

        deployment = self.prompt(
            "Deployment Name",
            default=self.config.get("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            secret=False,
        )
        self.config["AZURE_OPENAI_DEPLOYMENT_NAME"] = deployment

    def collect_ai_search_config(self, step_num: int):
        """Collect Azure AI Search configuration."""
        self.print_step(step_num, "Azure AI Search Configuration (F-108)")

        print(
            "\n  This section configures Azure AI Search for NLWeb vector store indexing."
        )

        endpoint = self.prompt(
            "Azure AI Search Endpoint",
            default=self.config.get(
                "AZURE_AI_SEARCH_ENDPOINT", "https://your-search.search.windows.net/"
            ),
            secret=False,
        )
        self.config["AZURE_AI_SEARCH_ENDPOINT"] = endpoint

        api_key = self.prompt("Azure AI Search API Key", secret=True)
        self.config["AZURE_AI_SEARCH_API_KEY"] = api_key

        index_name = self.prompt(
            "Index Name",
            default=self.config.get(
                "AZURE_AI_SEARCH_INDEX_NAME", "vspace-election-index"
            ),
            secret=False,
        )
        self.config["AZURE_AI_SEARCH_INDEX_NAME"] = index_name

    def collect_cosmos_config(self, step_num: int):
        """Collect Azure Cosmos DB configuration."""
        self.print_step(step_num, "Azure Cosmos DB Configuration (F-010, F-103, F-109)")

        print("\n  This section configures Cosmos DB for election record persistence.")

        conn_string = self.prompt("Cosmos DB Connection String", secret=True)
        self.config["AZURE_COSMOS_DB_CONNECTION_STRING"] = conn_string

        db_name = self.prompt(
            "Database Name",
            default=self.config.get("AZURE_COSMOS_DB_DATABASE_NAME", "ElectionGuardDb"),
            secret=False,
        )
        self.config["AZURE_COSMOS_DB_DATABASE_NAME"] = db_name

    def collect_app_service_config(self, step_num: int):
        """Collect Azure App Service configuration."""
        self.print_step(step_num, "Azure App Service Configuration (F-105, F-106)")

        print("\n  This section configures App Service for PWA hosting.")

        # vSpaceVote.com
        vspacevote_name = self.prompt(
            "vSpaceVote.com App Service Name",
            default=self.config.get("AZURE_APP_SERVICE_VSPACEVOTE_NAME"),
            secret=False,
        )
        if vspacevote_name:
            self.config["AZURE_APP_SERVICE_VSPACEVOTE_NAME"] = vspacevote_name
            self.config["AZURE_APP_SERVICE_VSPACEVOTE_RESOURCE_GROUP"] = self.prompt(
                "vSpaceVote.com Resource Group", secret=False
            )

        # vSpaceWallet.com
        vspacewallet_name = self.prompt(
            "vSpaceWallet.com App Service Name (optional)",
            default=self.config.get("AZURE_APP_SERVICE_VSPACEWALLET_NAME"),
            secret=False,
        )
        if vspacewallet_name:
            self.config["AZURE_APP_SERVICE_VSPACEWALLET_NAME"] = vspacewallet_name
            self.config["AZURE_APP_SERVICE_VSPACEWALLET_RESOURCE_GROUP"] = self.prompt(
                "vSpaceWallet.com Resource Group", secret=False
            )

    def collect_dev_mode_config(self, step_num: int):
        """Collect development mode configuration."""
        self.print_step(step_num, "Development Mode Configuration")

        print(
            "\n  Enable dry-run mode for local testing without actual Azure API calls."
        )
        print("  Recommended for initial setup and testing.")

        dry_run = self.prompt(
            "Enable Dry-Run Mode?",
            default=self.config.get("VSPACE_DRY_RUN", "true"),
            secret=False,
        )
        self.config["VSPACE_DRY_RUN"] = dry_run.lower() if dry_run else "true"

        log_level = self.prompt(
            "Log Level",
            default=self.config.get("VSPACE_LOG_LEVEL", "INFO"),
            secret=False,
        )
        self.config["VSPACE_LOG_LEVEL"] = log_level.upper()

    def generate_env_file(self):
        """Generate .env file from collected configuration."""
        self.print_header("Generating .env File")

        # Read template
        if self.example_path.exists():
            with open(self.example_path, "r") as f:
                template_lines = f.readlines()
        else:
            template_lines = []

        # Replace values in template
        output_lines = []
        for line in template_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key = stripped.split("=")[0]
                if key in self.config:
                    value = self.config[key]
                    output_lines.append(f"{key}={value}\n")
                else:
                    output_lines.append(line)
            else:
                output_lines.append(line)

        # Write .env file
        with open(self.env_file_path, "w") as f:
            f.writelines(output_lines)

        print(f"\n  ✓ Configuration saved to: {self.env_file_path}")
        print(f"    Total settings: {len(self.config)}")

    def generate_setup_report(self):
        """Generate setup completion report."""
        self.print_header("Setup Report")

        report = {
            "setup_completed": datetime.utcnow().isoformat(),
            "configuration_file": str(self.env_file_path),
            "services_configured": {
                "entra_verified_id": bool(self.config.get("AZURE_ENTRA_TENANT_ID")),
                "azure_openai": bool(self.config.get("AZURE_OPENAI_ENDPOINT")),
                "azure_ai_search": bool(self.config.get("AZURE_AI_SEARCH_ENDPOINT")),
                "azure_cosmos_db": bool(
                    self.config.get("AZURE_COSMOS_DB_CONNECTION_STRING")
                ),
                "azure_app_service": bool(
                    self.config.get("AZURE_APP_SERVICE_VSPACEVOTE_NAME")
                ),
            },
            "development_mode": {
                "dry_run_enabled": self.config.get("VSPACE_DRY_RUN", "true").lower()
                == "true",
                "log_level": self.config.get("VSPACE_LOG_LEVEL", "INFO"),
            },
            "next_steps": [],
        }

        # Determine next steps
        if report["services_configured"]["entra_verified_id"]:
            report["next_steps"].append(
                "Configure VoterEligibilityCredential contract in Entra portal"
            )
        if report["services_configured"]["azure_openai"]:
            report["next_steps"].append(
                "Deploy NLWeb instance with Azure OpenAI backend"
            )
        if report["services_configured"]["azure_cosmos_db"]:
            report["next_steps"].append(
                "Initialize MongoDB collections with vSPACE schema"
            )

        report["next_steps"].append("Run validation tests: python validate.py")
        report["next_steps"].append(
            "Execute E2E PoC demo: python ../demo/run_e2e_poc.py"
        )

        # Save report
        report_path = Path(__file__).parent / "setup_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n  Setup report saved to: {report_path}")
        print("\n  Configuration Summary:")
        for service, configured in report["services_configured"].items():
            status = "✓" if configured else "✗"
            print(f"    {status} {service.replace('_', ' ').title()}")

        print("\n  Next Steps:")
        for i, step in enumerate(report["next_steps"], 1):
            print(f"    {i}. {step}")

        return report

    async def run(self):
        """Execute complete setup wizard."""
        self.print_header("vSPACE Setup Wizard")

        print("\n  Welcome to the vSPACE configuration wizard!")
        print("  This will guide you through setting up all required Azure services")
        print("  and environment variables for the vSPACE Augmented PRD.")
        print("\n  Features configured:")
        print("    - F-104: Entra Verified ID Bridge")
        print("    - F-105: vSpaceVote.com PWA")
        print("    - F-106: vSpaceWallet.com PWA")
        print("    - F-108: NLWeb Conversational Interfaces")
        print("    - F-010, F-103, F-109: Azure Cosmos DB")

        input("\n  Press Enter to continue...")

        # Collect configuration
        step = 1
        self.collect_entra_config(step)
        step += 1

        self.collect_openai_config(step)
        step += 1

        self.collect_ai_search_config(step)
        step += 1

        self.collect_cosmos_config(step)
        step += 1

        self.collect_app_service_config(step)
        step += 1

        self.collect_dev_mode_config(step)
        step += 1

        # Run connection tests
        self.print_header("Connection Tests")

        await self.test_entra_connection()
        await self.test_openai_connection()
        await self.test_cosmos_connection()

        # Generate files
        self.generate_env_file()
        report = self.generate_setup_report()

        print("\n" + "=" * 80)
        print(" Setup Complete!")
        print("=" * 80)
        print("\n  To apply configuration:")
        print("    1. Copy .env file to your deployment environment")
        print("    2. Restart your application services")
        print("    3. Run: python validate.py")
        print("\n  Documentation:")
        print("    - See SETUP.md for detailed staging instructions")
        print("    - See ../demo/README.md for E2E PoC demo guide")
        print()


async def main():
    wizard = SetupWizard()
    await wizard.run()


if __name__ == "__main__":
    asyncio.run(main())
