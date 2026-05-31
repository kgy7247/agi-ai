from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import os
from pathlib import Path
from typing import Any


def validate_patch_with_git(patch_path: Path, repo_root: Path) -> dict[str, Any]:
    if not patch_path.exists():
        return {
            "ok": False,
            "command": f"git apply --check {patch_path}",
            "returncode": None,
            "stdout": "",
            "stderr": "patch file does not exist",
        }
    try:
        result = subprocess.run(
            ["git", "apply", "--check", str(patch_path)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "ok": False,
            "command": f"git apply --check {patch_path}",
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
        }
    return {
        "ok": result.returncode == 0,
        "command": f"git apply --check {patch_path}",
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def apply_patch_and_run_tests_in_sandbox(
    patch_path: Path,
    repo_root: Path,
    test_command: list[str] | None = None,
) -> dict[str, Any]:
    if test_command is None:
        test_command = [sys.executable, "-m", "unittest", "discover", "-v"]
    if not patch_path.exists():
        return {
            "ok": False,
            "patch_apply": {
                "ok": False,
                "command": f"git apply {patch_path}",
                "returncode": None,
                "stdout": "",
                "stderr": "patch file does not exist",
            },
            "tests": None,
        }

    with tempfile.TemporaryDirectory(prefix="agi-symposium-demo-") as tmp:
        sandbox_root = Path(tmp) / "repo"
        copy_repo_for_sandbox(repo_root, sandbox_root)

        apply_result = subprocess.run(
            ["git", "apply", str(patch_path)],
            cwd=sandbox_root,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        patch_apply = subprocess_result(f"git apply {patch_path}", apply_result)
        if apply_result.returncode != 0:
            return {"ok": False, "patch_apply": patch_apply, "tests": None}

        test_result = subprocess.run(
            test_command,
            cwd=sandbox_root,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
            env={**os.environ, "AGI_SYMPOSIUM_SANDBOX": "1"},
        )
        tests = subprocess_result(" ".join(test_command), test_result)
        return {
            "ok": bool(patch_apply["ok"] and tests["ok"]),
            "patch_apply": patch_apply,
            "tests": tests,
        }


def copy_repo_for_sandbox(repo_root: Path, sandbox_root: Path) -> None:
    ignore = shutil.ignore_patterns(
        ".git",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "state",
        "exports",
    )
    shutil.copytree(repo_root, sandbox_root, ignore=ignore)


def subprocess_result(command: str, result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    return {
        "ok": result.returncode == 0,
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout[-6000:],
        "stderr": result.stderr[-6000:],
    }
