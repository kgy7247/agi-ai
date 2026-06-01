# Public GitHub Release

This project is ready to publish when `python -m agi_symposium.release_check --runtime` has no blocking failures.

The release checker treats a missing git remote as a warning because the first public push naturally happens before a remote exists.

## 1. Run Local Verification

```powershell
python -m agi_symposium.release_check --runtime
```

Expected blocking checks:

- Required public files exist.
- Tracked git status is clean.
- Local state, exports, and cache folders are ignored.
- No obvious secret paths are tracked.
- Unit tests pass.
- Full demo passes patch check and sandbox tests.

## 2. Create the Public Repository

Create a new public GitHub repository in the browser:

```text
name: agi-ai
visibility: public
initialize with README: no
```

Do not add a GitHub-generated README, license, or `.gitignore`; this local repo already has those files.

## 3. Add Remote and Push

Replace `<owner>` with the GitHub account or organization.

```powershell
git remote add origin https://github.com/<owner>/agi-ai.git
git push -u origin main
```

After pushing, run:

```powershell
git remote -v
python -m agi_symposium.release_check --runtime
```

## 4. Verify GitHub

On GitHub, check:

- The repository is public.
- The `CI` workflow appears under the Actions tab.
- `README.md`, `NOTICE.md`, `SECURITY.md`, and `CONTRIBUTING.md` render correctly.
- Issue templates and the pull request template are available.

## 5. First Public Contributor Flow

External contributors can run:

```powershell
git clone https://github.com/<owner>/agi-ai.git
cd agi-ai
python -m agi_symposium.server --host 127.0.0.1 --port 8787
python -m agi_symposium.demo --reset --nickname theirname --ai-system their-ai
```

Local LLM contributors can run, for example:

```powershell
python -m agi_symposium.local_node --nickname theirname --ai-system llama3 --provider ollama --endpoint http://127.0.0.1:11434
```

The model runs on the contributor's own machine, but it participates through the same `room_manifest`, contribution, verification, and Hall of Fame protocol.
