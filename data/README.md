<!-- Purpose: Describe ignored runtime storage, immutable evidence lifecycle, safe cleanup, and separation from test data. -->
# Runtime artifacts and evidence

This directory is application-managed local storage. Runtime data may already exist; the previous “no runtime data exists yet” statement is obsolete. Everything except this README is ignored by the current .gitignore. Do not infer that ignored files are disposable or safe to delete.

## Current and target contents

Current code creates scan, patch, demo and validation workspaces, SQLite fusion.db, and local process markers. Target storage also includes immutable revision artifacts, parent validation manifests, traces, attachment metadata, test/visual evidence and managed-session records as implementation arrives.

Use server-generated IDs and relative internal paths. Suggested organization is scans/<id>, revisions/<id>, validation/<run-id>, demo/<run-id>, artifacts/<id>, and verification/<session-id>. These are target conventions, not claims that every directory/model already exists.

## Integrity and retention

Original uploaded bytes and derived candidates are immutable separate artifacts. Store SHA-256, size, type, parent/run relationship and timestamps. Recheck before execution/download. Display strings and truncated logs are not replacements for authoritative source/report artifacts.

Retain partial failure evidence with error/timeout/truncation labels. Mark old-chain evidence historical after reset; reset must not erase DB/source/history. A missing/corrupt artifact produces an integrity error rather than a new fabricated report.

Logs/reports have enforced bounds. Do not write real wallet keys, credentials, broad environment dumps or external-source secrets here. Sources remain local by default.

## Tests and cleanup

Tests should receive separate temporary DB/artifact roots and disposable owned RPC sessions. A pytest scratch directory under data is not automatically safe if tests still point at the ordinary database. Confirm injected configuration.

Before cleanup, stop only the relevant owned job, verify the resolved absolute target is inside the intended disposable root, check references/retention, and remove using one native shell. Do not recursively delete data as a routine reset. Preserve user evidence and backups before migrations.

Verification captures belong under an ignored evidence subdirectory; immutable user reference PNGs belong in CONTEXT/references instead. Link exact evidence paths from progress when checks actually run.
