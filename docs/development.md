# Development Workflow

Last updated: 2026-07-13, Asia/Shanghai.

## Workspace Layout

Canonical local workspace:

```text
W:\实验室项目\Gaze-Project
├── docs\                         # shell-level project docs
├── .codex\skills\gaze-project-context
└── thirdparty\
    ├── QuestGazeClient           # independent Unity git repo
    ├── Quest3DataCollector       # independent Collector git repo
    └── gaze-dp                   # independent Gaze-WAM git repo
```

Legacy compatibility junctions:

| Legacy path | Target |
| --- | --- |
| `W:\lasertag-projs` | `W:\实验室项目\Gaze-Project\thirdparty\QuestGazeClient` |
| `W:\Quest3DataCollector` | `W:\实验室项目\Gaze-Project\thirdparty\Quest3DataCollector` |
| `W:\实验室项目\gaze-wam` | `W:\实验室项目\Gaze-Project\thirdparty\gaze-dp` |

## Git Ownership

This shell repository tracks:

- `README.md`
- `docs/**`
- `.codex/skills/gaze-project-context/**`
- lightweight workspace metadata such as `.gitignore`

This shell repository does not track:

- `thirdparty/*` source contents
- Unity build outputs
- venvs
- zarr stores
- recordings
- model outputs

The three codebases keep their own git history and remotes:

```powershell
git -C thirdparty\QuestGazeClient remote -v
git -C thirdparty\Quest3DataCollector remote -v
git -C thirdparty\gaze-dp remote -v
```

## Normal Development Flow

1. Check shell and component status:

   ```powershell
   git status -sb
   git -C thirdparty\QuestGazeClient status -sb
   git -C thirdparty\Quest3DataCollector status -sb
   git -C thirdparty\gaze-dp status -sb
   ```

2. Make source changes inside the owning `thirdparty` repository.
3. Commit and push in that component repository.
4. Update shell docs when a cross-component fact changes.
5. Commit and push the shell documentation update separately.

## Current Source Branches

| Component | Branch | Remote |
| --- | --- | --- |
| QuestGazeClient | `main` | `origin` -> `git@github.com:Spphire/QuestGazeClient.git` |
| Quest3DataCollector | `quest3-chessboard-flexiv` | `origin` -> `git@github.com:Spphire/Quest3DataCollector.git` |
| gaze-dp / Gaze-WAM | `gaze-wam-cleanup` | `gaze-dp` -> `git@github.com:Spphire/gaze-dp.git` |

As of 2026-07-13, `Quest3DataCollector` has local uncommitted teleop-latency
development changes. Commit those in the Collector repo before treating the
Collector source as synchronized.

## Implementation Priorities

Current high-value missing bridge:

1. Collector formal recording folder to Gaze-WAM robot zarr converter.
2. Clear semantics for policy camera source, action labels, and gripper labels.
3. Deployment sync policy for the unmanaged Collector PC folder.

Do not assume these semantics silently. Record any decision in
[gaze-project-overview.md](gaze-project-overview.md) and
[agent-context.md](agent-context.md).
