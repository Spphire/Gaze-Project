---
name: gaze-project-context
description: Project context and operating guide for the QuestGazeClient, Quest3DataCollector, and gaze-dp/Gaze-WAM robotics gaze project. Use when Codex works on Quest gaze telemetry, PC-side Flexiv/RealSense collection, calibration recordings, Collector-to-zarr conversion, HOT3D/Gaze-WAM training data, or the lab deployments at lvjun@10.128.0.227 and H200-4042.
---

# Gaze Project Context

## Overview

Use this skill to quickly rehydrate the project map before making changes or answering questions. Start by reading `W:\实验室项目\Gaze-Project\docs\agent-context.md` when available. For Python/Unity environment and requirements questions, also read `W:\实验室项目\Gaze-Project\docs\deployment-environments.md`. If the workspace docs are missing or stale, read `references/deployment-context.md` for a compact fallback.

## Guardrails

- Treat `W:\实验室项目\Gaze-Project` as the shell git repository for docs, deployment notes, and persistent agent context.
- Do not commit `thirdparty/*` source contents into the shell repository; those are independent git repositories.
- Do not modify remote running services unless the user explicitly asks.
- Treat `W:\实验室项目\Gaze-Project\thirdparty\QuestGazeClient` and `W:\实验室项目\Gaze-Project\thirdparty\Quest3DataCollector` as the active local source trees for Quest and Collector.
- Treat `W:\lasertag-projs` and `W:\Quest3DataCollector` as legacy junctions to the workspace paths.
- Treat `W:\实验室项目\Gaze-Project\thirdparty\gaze-dp` as the active Gaze-WAM path.
- Treat `W:\实验室项目\gaze-wam` as a legacy junction path, not a separate copy.
- Preserve unrelated changes. H200 was synced to `e111c7cdf77a` on 2026-07-02 and left with one safety stash; always verify current status before modifying it.
- Use read-only SSH checks before claiming current remote state.
- Use `rg` and `rg --files` first for code discovery.

## Canonical Paths

- Quest Unity client: `W:\实验室项目\Gaze-Project\thirdparty\QuestGazeClient`, remote `git@github.com:Spphire/QuestGazeClient.git`, package `com.Apricity.EyeTrackingTest`.
- Collector: `W:\实验室项目\Gaze-Project\thirdparty\Quest3DataCollector`, remote `git@github.com:Spphire/Quest3DataCollector.git`, deployed at `lvjun@10.128.0.227:/ssd1/shenyibo/Quest3DataCollector`.
- Training: `W:\实验室项目\Gaze-Project\thirdparty\gaze-dp`, remote `git@github.com:Spphire/gaze-dp.git`, deployed at `H200-4042:/mnt/workspace/shenyibo/gaze-wam`.

## Key Facts

- Quest A button sends formal recording telemetry over UDP to `10.128.0.227:9100`.
- Quest B button sends PC calibration data over HTTP to `http://10.128.0.227:9101`.
- Collector viewer is normally `http://10.128.0.227:8765/`.
- Collector formal recordings live under `pc/offline_calibration/pc_recordings/<recordId>/`.
- Collector calibration raw/output folders are `pc/offline_calibration/raw/<recordId>/` and `pc/offline_calibration/outputs/pc_live_calibration/<recordId>/`.
- Unity-to-PC coordinate conversion is `pc = [unity.z, -unity.x, unity.y]`.
- Collector can analyze teleop responsiveness with `quest_pc_receiver.py teleop-latency --pc-session <record_dir>` and replay `Teleop latency`; it compares command target/controller speed to robot TCP speed on the PC perf-counter timeline.
- Gaze-WAM already has HOT3D/open-only training data support and robot zarr canonicalization tools.
- The missing bridge is a converter from Collector formal recording folders to canonical robot zarr.
- Collector has a committed `requirements.txt` generated from the remote `.venv312`; Gaze-WAM is venv-only with committed H200 `requirements.txt` / `requirements-h200.txt` installed via `--no-deps`, `requirements-h200-editables.txt` for non-portable editables, and local `requirements-local-windows.txt`; Quest is Unity-only with no Python venv.

## Common Workflows

For status or deployment questions:

1. Read `docs/agent-context.md`.
2. Check local `git status -sb` in the three active source trees.
3. Use read-only `ssh` commands for `lvjun@10.128.0.227` and `H200-4042`.
4. Report exact paths, branches, ports, stash state, and any dirty/unmanaged state.

For Collector-to-zarr work:

1. Inspect Collector recording files under `pc_recordings/<recordId>/`.
2. Align Quest samples, RealSense frames, robot states, and gripper data by timestamps.
3. Confirm unresolved semantics before choosing policy camera, action target, and gripper labels.
4. Write output compatible with `data/camera0_rgb`, `data/gaze_xy`, `data/action_abs_tcp`, `data/tcp_pose_abs`, `data/gripper_width`, and `meta/episode_ends`.
5. Run Gaze-WAM prepare/canonicalize/validate scripts after conversion.

For teleop latency questions:

1. Use `quest_pc_receiver.py teleop-latency --pc-session <record_dir>` or inspect `teleop_latency_analysis.json`.
2. Prefer `targetToRobot` for control-loop responsiveness; use `controllerToRobot` only when command target rows are missing.
3. Treat positive lag as robot TCP following the command/controller after that delay; do not report it as absolute one-way network latency.

For Quest APK work:

1. Check `adb devices`.
2. If the Quest is `unauthorized`, ask the user to accept the RSA/USB debugging prompt inside the headset.
3. Use the local APKs in `W:\实验室项目\Gaze-Project\thirdparty\QuestGazeClient\Build`, `dist`, or `ReleaseAssets` only after confirming the desired build.

## Open Decisions To Reconfirm

- Which RealSense serial is the current policy/end-effector camera.
- Whether the remote Collector deployment should become a git checkout or remain an unmanaged copy.
- Whether Gaze-WAM action labels should use executed TCP, command targets, or another target.
- Which source should define gripper width/action labels.
