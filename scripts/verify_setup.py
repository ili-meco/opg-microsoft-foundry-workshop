"""Verify local and Azure prerequisites for the OPG Foundry workshop."""

from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass

MINIMUM_PYTHON = (3, 11)
REQUIRED_MODULES = {
    "agent_framework": "agent-framework-core",
    "agent_framework.openai": "agent-framework-openai",
    "agent_framework.orchestrations": "agent-framework-orchestrations",
    "azure.ai.projects": "azure-ai-projects",
    "azure.identity": "azure-identity",
    "azure.search.documents": "azure-search-documents",
    "dotenv": "python-dotenv",
    "openai": "openai",
    "opentelemetry.exporter.otlp.proto.grpc": "opentelemetry-exporter-otlp-proto-grpc",
    "pydantic": "pydantic",
    "requests": "requests",
}
REQUIRED_ENVIRONMENT = ("FOUNDRY_PROJECT_ENDPOINT", "FOUNDRY_MODEL_NAME")
LAB_03_ENVIRONMENT = (
    "FOUNDRY_PROJECT_RESOURCE_ID",
    "AZURE_SEARCH_ENDPOINT",
    "FOUNDRY_EMBEDDING_ENDPOINT",
    "FOUNDRY_EMBEDDING_MODEL_NAME",
)


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    detail: str


def module_available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except ModuleNotFoundError:
        return False


def local_checks() -> list[CheckResult]:
    python_ok = sys.version_info >= MINIMUM_PYTHON
    results = [
        CheckResult(
            "Python",
            "PASS" if python_ok else "FAIL",
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        ),
        CheckResult(
            "Virtual environment",
            "PASS" if sys.prefix != sys.base_prefix else "WARN",
            "active" if sys.prefix != sys.base_prefix else "not detected",
        ),
        CheckResult(
            "Azure CLI",
            "PASS" if shutil.which("az") else "FAIL",
            "available" if shutil.which("az") else "not found on PATH",
        ),
    ]

    for module_name, package_name in REQUIRED_MODULES.items():
        installed = module_available(module_name)
        results.append(
            CheckResult(
                package_name,
                "PASS" if installed else "FAIL",
                "installed" if installed else f"missing module {module_name}",
            )
        )

    return results


def load_environment_file() -> None:
    if module_available("dotenv"):
        from dotenv import load_dotenv

        load_dotenv()


def configuration_checks(
    variables: tuple[str, ...] = REQUIRED_ENVIRONMENT,
) -> list[CheckResult]:
    results = []
    for variable in variables:
        value = os.getenv(variable, "").strip()
        results.append(
            CheckResult(
                variable,
                "PASS" if value else "WARN",
                "configured" if value else "not configured yet",
            )
        )
    return results


def azure_login_check() -> CheckResult:
    try:
        process = subprocess.run(
            ["az", "account", "show", "--query", "{name:name,tenantId:tenantId}", "--output", "tsv"],
            capture_output=True,
            check=False,
            text=True,
            timeout=20,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        return CheckResult("Azure sign-in", "FAIL", str(error))

    if process.returncode != 0:
        detail = process.stderr.strip() or "Run 'az login' and try again."
        return CheckResult("Azure sign-in", "FAIL", detail)

    return CheckResult("Azure sign-in", "PASS", process.stdout.strip())


def print_results(results: list[CheckResult]) -> None:
    labels = {"PASS": "[PASS]", "WARN": "[WARN]", "FAIL": "[FAIL]"}
    for result in results:
        print(f"{labels[result.status]} {result.name}: {result.detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--azure",
        action="store_true",
        help="Also verify that Azure CLI has an active signed-in account.",
    )
    parser.add_argument(
        "--lab-03",
        action="store_true",
        help="Also verify the Azure AI Search and Foundry IQ configuration.",
    )
    args = parser.parse_args()

    load_environment_file()
    configuration = REQUIRED_ENVIRONMENT + (LAB_03_ENVIRONMENT if args.lab_03 else ())
    results = [*local_checks(), *configuration_checks(configuration)]
    if args.azure:
        results.append(azure_login_check())

    print_results(results)
    return 1 if any(result.status == "FAIL" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())