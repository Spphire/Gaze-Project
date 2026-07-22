# Documentation Index

This directory is the stable project memory for the Gaze Project shell repo.

## Read Order

1. [gaze-project-overview.md](gaze-project-overview.md)  
   System map, repository inventory, protocol facts, data layout, and unresolved
   project decisions.
2. [deployment-environments.md](deployment-environments.md)  
   Python/Unity environment state, venv policy, requirements snapshots, and
   current deployment baseline.
3. [deployment.md](deployment.md)  
   Deployment hosts, paths, sync boundaries, and operational checks.
4. [development.md](development.md)  
   Local workspace layout, git ownership, branch policy, and implementation
   workflow.
5. [usage.md](usage.md)  
   Operator workflow for Quest recording, calibration, replay, teleop latency,
   and training handoff.
6. [performance.md](performance.md)
   Quest/Collector frequency contract, quality gates, and safe benchmark flow.
7. [quest-endpoint-test-20260717.md](quest-endpoint-test-20260717.md)
   Quest-only hardware test, APK integrity fix, timing evidence, and restore
   record.
8. [agent-context.md](agent-context.md)
   Short context file for future agents.

## Repository Boundaries

The shell repo tracks docs and `.codex` context. The source trees under
`thirdparty/*` are independent git repositories and are intentionally ignored by
the shell repo.

Use the component repos for source commits:

- `thirdparty/QuestGazeClient`
- `thirdparty/Quest3DataCollector`
- `thirdparty/gaze-dp`

Use this shell repo for cross-repo decisions, deployment notes, and project
handoff context.
