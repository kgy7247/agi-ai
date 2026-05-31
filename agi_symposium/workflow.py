from __future__ import annotations

import subprocess
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

