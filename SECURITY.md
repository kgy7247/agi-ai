# Security

The base project must run without API keys or private credentials.

## Do Not Commit

- API keys.
- Browser cookies.
- Private transcripts.
- Real user data.
- Local `.env` files.
- Generated `state/` files unless intentionally sanitized.

## Autonomy Safety

Any feature that lets an agent call tools, write files, run shell commands, access networks, or publish externally must include:

- A permission boundary.
- Logs.
- A dry-run mode when practical.
- Tests for blocked or invalid actions.
- Documentation of expected risks.

## Reporting

Open a GitHub issue for non-sensitive security problems. For sensitive issues, contact maintainers privately once a private channel exists.

