"""Create isolated workshop copies with participant-specific Azure resource names."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "config" / "workshop-participants.json"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "participant-workspaces"
DEFAULT_ENVIRONMENT_TEMPLATE = REPO_ROOT / ".env.example"
COHORT_PATTERN = re.compile(r"^[a-z][a-z0-9]{2,11}$")
PARTICIPANT_PATTERN = re.compile(r"^[a-z]{2}$")
ENVIRONMENT_LINE_PATTERN = re.compile(r"^([A-Z][A-Z0-9_]*)=(.*)$")
SHARED_ENVIRONMENT_VARIABLES = {
    "FOUNDRY_PROJECT_ENDPOINT",
    "FOUNDRY_MODEL_NAME",
    "FOUNDRY_COMPARISON_MODEL_NAME",
    "FOUNDRY_PROJECT_RESOURCE_ID",
    "AZURE_SEARCH_ENDPOINT",
    "FOUNDRY_EMBEDDING_ENDPOINT",
    "FOUNDRY_EMBEDDING_MODEL_NAME",
    "FOUNDRY_EMBEDDING_MODEL",
    "FOUNDRY_EMBEDDING_DIMENSIONS",
}


def load_roster(config_path: Path) -> tuple[str, list[str]]:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    cohort_code = str(data["cohort_code"]).strip().lower()
    participant_ids = [
        str(participant_id).strip().lower()
        for participant_id in data["participant_ids"]
    ]
    validate_roster(cohort_code, participant_ids)
    return cohort_code, participant_ids


def validate_roster(cohort_code: str, participant_ids: list[str]) -> None:
    if not COHORT_PATTERN.fullmatch(cohort_code):
        raise ValueError(
            "Cohort code must start with a lowercase letter and contain 3-12 "
            "lowercase letters or digits."
        )
    invalid_ids = [
        participant_id
        for participant_id in participant_ids
        if not PARTICIPANT_PATTERN.fullmatch(participant_id)
    ]
    if invalid_ids:
        raise ValueError(
            "Participant IDs must be exactly two lowercase letters: "
            + ", ".join(invalid_ids)
        )
    if len(participant_ids) != len(set(participant_ids)):
        raise ValueError("Participant IDs must be unique within the cohort.")
    if not participant_ids:
        raise ValueError("At least one participant ID is required.")


def participant_assignments(cohort_code: str, participant_id: str) -> dict[str, str]:
    prefix = f"{cohort_code}-{participant_id}"
    return {
        "PARTICIPANT_ID": participant_id,
        "WORKSHOP_COHORT": cohort_code,
        "RESOURCE_PREFIX": prefix,
        "AZURE_SEARCH_INDEX_NAME": f"{prefix}-maintenance-documents",
        "AZURE_SEARCH_KNOWLEDGE_SOURCE_NAME": f"{prefix}-maintenance-source",
        "AZURE_SEARCH_KNOWLEDGE_BASE_NAME": f"{prefix}-maintenance-knowledge",
        "FOUNDRY_IQ_CONNECTION_NAME": f"{prefix}-maintenance-iq",
        "FOUNDRY_GROUNDED_AGENT_NAME": f"{prefix}-grounded-maintenance-agent",
        "HOSTED_AGENT_NAME": f"{prefix}-maintenance-agent",
        "AZURE_ENV_NAME": prefix,
        "EVALUATION_SUITE_NAME": f"{prefix}-maintenance-eval",
    }


def parse_environment(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ENVIRONMENT_LINE_PATTERN.fullmatch(line.strip())
        if match:
            values[match.group(1)] = match.group(2)
    return values


def render_environment(
    template_text: str,
    participant_values: dict[str, str],
    shared_values: dict[str, str] | None = None,
) -> str:
    replacements = dict(participant_values)
    replacements.update(
        {
            key: value
            for key, value in (shared_values or {}).items()
            if key in SHARED_ENVIRONMENT_VARIABLES
        }
    )
    rendered_lines: list[str] = []
    seen: set[str] = set()
    for line in template_text.splitlines():
        match = ENVIRONMENT_LINE_PATTERN.fullmatch(line.strip())
        if match and match.group(1) in replacements:
            key = match.group(1)
            rendered_lines.append(f"{key}={replacements[key]}")
            seen.add(key)
        else:
            rendered_lines.append(line)

    missing = [key for key in participant_values if key not in seen]
    participant_header = [
        "# Generated participant identity and collision-safe resource names.",
        *[f"{key}={participant_values[key]}" for key in missing],
        "",
    ]
    rendered = "\n".join([*participant_header, *rendered_lines]).rstrip() + "\n"
    return rendered.replace("<initials>", participant_values["PARTICIPANT_ID"])


def tracked_workshop_files(repo_root: Path) -> list[Path]:
    process = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files"],
        capture_output=True,
        check=True,
        text=True,
    )
    paths = [Path(line) for line in process.stdout.splitlines() if line]
    for required_path in (
        Path("config/workshop-participants.json"),
        Path("scripts/create_participant_workspaces.py"),
    ):
        if required_path not in paths and (repo_root / required_path).is_file():
            paths.append(required_path)
    return [path for path in paths if should_include(path)]


def should_include(path: Path) -> bool:
    if path.name == "FACILITATOR.md" or path == Path("AGENTS.md"):
        return False
    if path == Path("scripts/add_story_slides.ps1"):
        return False
    return True


def participant_manifest(assignments: dict[str, str]) -> str:
    rows = "\n".join(
        f"| `{key}` | `{value}` |" for key, value in assignments.items()
    )
    return (
        "# Your OPG Workshop Workspace\n\n"
        f"Your assigned resource prefix is `{assignments['RESOURCE_PREFIX']}`. "
        "Use only this workspace during the labs.\n\n"
        "The shared Foundry project, model deployments, and Search service are "
        "configured separately. The names below isolate the resources you create "
        "inside those shared services.\n\n"
        "| Setting | Assigned value |\n"
        "|---|---|\n"
        f"{rows}\n\n"
        "Do not change another participant's resources. Run Lab 03 cleanup only "
        "from this workspace so it targets your assigned names.\n"
    )


def create_workspaces(
    repo_root: Path,
    output_root: Path,
    cohort_code: str,
    participant_ids: list[str],
    environment_template: Path,
    shared_environment: Path | None = None,
) -> list[Path]:
    validate_roster(cohort_code, participant_ids)
    destinations = [
        output_root / f"{cohort_code}-{participant_id}"
        for participant_id in participant_ids
    ]
    existing = [destination for destination in destinations if destination.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite existing participant workspaces: "
            + ", ".join(str(path) for path in existing)
        )

    files = tracked_workshop_files(repo_root)
    template_text = environment_template.read_text(encoding="utf-8")
    shared_values = (
        parse_environment(shared_environment) if shared_environment else {}
    )
    created: list[Path] = []
    try:
        for participant_id, destination in zip(participant_ids, destinations):
            destination.mkdir(parents=True)
            created.append(destination)
            for relative_path in files:
                source = repo_root / relative_path
                target = destination / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

            assignments = participant_assignments(cohort_code, participant_id)
            environment_text = render_environment(
                template_text,
                assignments,
                shared_values,
            )
            (destination / ".env").write_text(environment_text, encoding="utf-8")
            (destination / "PARTICIPANT.md").write_text(
                participant_manifest(assignments),
                encoding="utf-8",
            )
    except Exception:
        for destination in created:
            shutil.rmtree(destination, ignore_errors=True)
        raise
    return created


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--environment-template",
        type=Path,
        default=DEFAULT_ENVIRONMENT_TEMPLATE,
    )
    parser.add_argument(
        "--shared-environment",
        type=Path,
        help=(
            "Optional .env file. Only allowlisted non-secret shared workshop "
            "settings are copied."
        ),
    )
    parser.add_argument(
        "--participant",
        action="append",
        dest="participants",
        help="Generate only this participant ID; repeat for more than one.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    cohort_code, configured_ids = load_roster(args.config.resolve())
    participant_ids = (
        [participant_id.lower() for participant_id in args.participants]
        if args.participants
        else configured_ids
    )
    created = create_workspaces(
        REPO_ROOT,
        args.output_root.resolve(),
        cohort_code,
        participant_ids,
        args.environment_template.resolve(),
        args.shared_environment.resolve() if args.shared_environment else None,
    )
    print(f"Created {len(created)} participant workspace(s):")
    for destination in created:
        print(f"- {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())