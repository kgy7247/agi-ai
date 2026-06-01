from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PUBLIC_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "GOVERNANCE.md",
    "SECURITY.md",
    "NOTICE.md",
    "LICENSE",
    ".gitattributes",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/agi_experiment.md",
    ".github/ISSUE_TEMPLATE/agent_contribution.md",
    ".github/workflows/ci.yml",
]

REQUIRED_IGNORED_PATHS = [
    "state",
    "exports",
    "agi_symposium/__pycache__",
    "tests/__pycache__",
]

SECRET_PATTERNS = [
    "secrets/",
    ".env",
    "client_secret",
    "token.json",
    "blogger_token",
    "OPENAI_API_KEY",
]

LIVE_STATE_FILES = [
    "state/symposium_state.json",
    "state/transcript.jsonl",
    "state/verification_ledger.jsonl",
]


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str


def run_command(args: list[str], *, cwd: Path = ROOT, timeout: int = 120) -> tuple[int, str, str]:
    completed = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def check_required_files(root: Path = ROOT) -> CheckResult:
    missing = [path for path in REQUIRED_PUBLIC_FILES if not (root / path).exists()]
    if missing:
        return CheckResult("required_files", False, "missing: " + ", ".join(missing))
    return CheckResult("required_files", True, f"{len(REQUIRED_PUBLIC_FILES)} files present")


def check_git_clean(root: Path = ROOT) -> CheckResult:
    code, stdout, stderr = run_command(["git", "status", "--short"], cwd=root)
    if code != 0:
        return CheckResult("git_clean", False, stderr or stdout)
    if stdout.strip():
        return CheckResult("git_clean", False, stdout)
    return CheckResult("git_clean", True, "no tracked or untracked public changes")


def check_ignored_outputs(root: Path = ROOT) -> CheckResult:
    missing = []
    for path in REQUIRED_IGNORED_PATHS:
        code, _, _ = run_command(["git", "check-ignore", "-q", path], cwd=root)
        if code != 0:
            missing.append(path)
    if missing:
        return CheckResult("ignored_outputs", False, "not ignored: " + ", ".join(missing))
    return CheckResult("ignored_outputs", True, "local state/export/cache paths are ignored")


def check_no_tracked_secrets(root: Path = ROOT) -> CheckResult:
    code, stdout, stderr = run_command(["git", "ls-files"], cwd=root)
    if code != 0:
        return CheckResult("tracked_secrets", False, stderr or stdout)
    tracked = stdout.splitlines()
    suspicious = [
        path
        for path in tracked
        if any(pattern.lower() in path.lower() for pattern in SECRET_PATTERNS)
    ]
    if suspicious:
        return CheckResult("tracked_secrets", False, "suspicious tracked paths: " + ", ".join(suspicious))
    return CheckResult("tracked_secrets", True, "no obvious secret paths tracked")


def check_remote(root: Path = ROOT) -> CheckResult:
    code, stdout, stderr = run_command(["git", "remote", "-v"], cwd=root)
    if code != 0:
        return CheckResult("git_remote", False, stderr or stdout)
    if not stdout.strip():
        return CheckResult("git_remote", False, "no remote configured yet")
    return CheckResult("git_remote", True, stdout.splitlines()[0])


def check_tests(root: Path = ROOT) -> CheckResult:
    snapshot = snapshot_live_state(root)
    try:
        code, stdout, stderr = run_command([sys.executable, "-m", "unittest", "discover", "-v"], cwd=root)
    finally:
        restore_live_state(root, snapshot)
    if code != 0:
        return CheckResult("unit_tests", False, stderr or stdout)
    return CheckResult("unit_tests", True, "unittest discover passed")


def check_demo(root: Path = ROOT) -> CheckResult:
    snapshot = snapshot_live_state(root)
    try:
        code, stdout, stderr = run_command(
            [
                sys.executable,
                "-m",
                "agi_symposium.demo",
                "--reset",
                "--nickname",
                "releasecheck",
                "--ai-system",
                "local",
            ],
            cwd=root,
        )
    finally:
        restore_live_state(root, snapshot)
    if code != 0:
        return CheckResult("full_demo", False, stderr or stdout)
    try:
        result = json.loads(stdout)
    except json.JSONDecodeError:
        return CheckResult("full_demo", False, "demo returned non-json output")
    demo_run = result.get("demo_run", {})
    if not demo_run.get("patch_validation", {}).get("ok"):
        return CheckResult("full_demo", False, "patch validation failed")
    if not demo_run.get("sandbox_result", {}).get("ok"):
        return CheckResult("full_demo", False, "sandbox tests failed")
    return CheckResult("full_demo", True, "patch check and sandbox tests passed")


def snapshot_live_state(root: Path = ROOT) -> dict[str, bytes | None]:
    snapshot: dict[str, bytes | None] = {}
    for relative_path in LIVE_STATE_FILES:
        path = root / relative_path
        snapshot[relative_path] = path.read_bytes() if path.exists() else None
    return snapshot


def restore_live_state(root: Path, snapshot: dict[str, bytes | None]) -> None:
    for relative_path, content in snapshot.items():
        path = root / relative_path
        if content is None:
            if path.exists():
                path.unlink()
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def run_release_checks(*, include_runtime: bool = False, root: Path = ROOT) -> list[CheckResult]:
    checks = [
        check_required_files(root),
        check_git_clean(root),
        check_ignored_outputs(root),
        check_no_tracked_secrets(root),
        check_remote(root),
    ]
    if include_runtime:
        checks.extend([check_tests(root), check_demo(root)])
    return checks


def summarize(checks: list[CheckResult]) -> dict[str, Any]:
    blocking = [check for check in checks if not check.ok and check.name != "git_remote"]
    warnings = [check for check in checks if not check.ok and check.name == "git_remote"]
    return {
        "ok": not blocking,
        "blocking_count": len(blocking),
        "warning_count": len(warnings),
        "checks": [asdict(check) for check in checks],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Check whether this repo is ready for public GitHub release.")
    parser.add_argument("--runtime", action="store_true", help="also run unittest and the full demo")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    summary = summarize(run_release_checks(include_runtime=args.runtime))
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("AGI Symposium public release check")
        for check in summary["checks"]:
            marker = "OK" if check["ok"] else "WARN" if check["name"] == "git_remote" else "FAIL"
            print(f"[{marker}] {check['name']}: {check['detail']}")
        print(f"ready={summary['ok']} blocking={summary['blocking_count']} warnings={summary['warning_count']}")

    raise SystemExit(0 if summary["ok"] else 1)


if __name__ == "__main__":
    main()
