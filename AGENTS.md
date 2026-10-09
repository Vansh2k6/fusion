<!-- Purpose: Load the authoritative project guide for coding agents without duplicating its rules. -->
# Fusion agent entry point

Read [CONTEXT/agent.md](CONTEXT/agent.md) in full before planning, editing, or executing project work. It is the authoritative project-level guide; follow its precedence and permission boundaries. Resolve its supporting references relative to CONTEXT.

The guide points to rules, decisions, PRD, architecture, design, phases, and progress. Read relevant component READMEs and existing code before changing a component. Current implementation status is in [CONTEXT/progress.md](CONTEXT/progress.md); sequencing and test gates are in [CONTEXT/phases.md](CONTEXT/phases.md).

The single [prompt.md](prompt.md) is a reusable implementation/resumption instruction for the user. It does not override the guide or authorize implementation during a documentation-only request. Keep this entry point short so there is only one authoritative rule set.
