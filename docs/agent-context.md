# Agent Context For Gaze Project

Load this file before working on tasks involving Quest gaze collection, `Quest3DataCollector`, `gaze-dp`/Gaze-WAM, Collector-to-zarr conversion, or the lab deployments.

## Operating Rules

- Treat `W:\实验室项目\Gaze-Project` as the shell git repository for cross-component docs, deployment notes, and persistent agent context.
- Do not commit `thirdparty/*` source contents into the shell repository. Those directories are independent git repositories and are intentionally ignored by the shell `.gitignore`.
- Do not modify remote running services or remote dirty training trees unless the user explicitly asks.
- Treat `W:\实验室项目\Gaze-Project\thirdparty\QuestGazeClient` and `W:\实验室项目\Gaze-Project\thirdparty\Quest3DataCollector` as the active local source trees for Quest and Collector.
- Treat `W:\lasertag-projs` and `W:\Quest3DataCollector` as legacy junction paths, not separate copies.
- Treat `W:\实验室项目\Gaze-Project\thirdparty\gaze-dp` as the active Gaze-WAM path.
- Treat `W:\实验室项目\gaze-wam` as a legacy junction path, not a separate copy.
- Prefer read-only checks on `lvjun@10.128.0.227` and `H200-4042` before making claims about live deployment state.
- Preserve unrelated local or remote changes. The H200 training tree was previously ahead/dirty, but was synced to `e111c7cdf77a` on 2026-07-02; verify current status before modifying it.
- Use `rg`/`rg --files` first for code search.

## Quick Inventory

| Component | Local path | Remote/deploy path | Branch/commit observed |
| --- | --- | --- | --- |
| Shell docs/context | `W:\实验室项目\Gaze-Project` | `git@github.com:Spphire/Gaze-Project.git` | `main`; tracks docs and `.codex`, ignores `thirdparty/*` source |
| Quest client | `W:\实验室项目\Gaze-Project\thirdparty\QuestGazeClient` | Quest 3 APK package `com.Apricity.EyeTrackingTest` | `main`, `dbc9b0d7cb61` |
| Collector | `W:\实验室项目\Gaze-Project\thirdparty\Quest3DataCollector` | `lvjun@10.128.0.227:/ssd1/shenyibo/Quest3DataCollector` | local `quest3-chessboard-flexiv`, `81b8cfa17ab2`; remote folder has no `.git` |
| Training | `W:\实验室项目\Gaze-Project\thirdparty\gaze-dp` | `H200-4042:/mnt/workspace/shenyibo/gaze-wam` | local/remote `gaze-wam-cleanup`, `e111c7cdf77a`; H200 worktree clean with one safety stash |

## Latest Health Check

Checked on 2026-07-02:

- Local repos are clean and synced: Quest with `origin/main`, Collector with `origin/quest3-chessboard-flexiv`, and Gaze-WAM with `gaze-dp/gaze-wam-cleanup`.
- Quest USB is authorized as device `2G0YC1ZF940X95`. Package `com.Apricity.EyeTrackingTest` is installed with `versionCode=220`, `versionName=0.0.0a`, and Unity activity records are visible.
- UnityHub points to `W:\实验室项目\Gaze-Project\thirdparty\QuestGazeClient`.
- Collector remote is running at `lvjun@10.128.0.227`; UDP `9100`, TCP `9101`, and TCP `8765` are listening; viewer `http://10.128.0.227:8765/` returned HTTP 200.
- Collector remote is not a git checkout. `.gitignore` and `requirements.txt` are copied there and the remote `.venv312` dry-run passed, but full deployment sync cannot be proven by git until the remote is made a git checkout or a manifest/hash sync is maintained.
- Collector hardware visibility checked: network interface `192.168.2.108` is up; RealSense `750612070265` and `244222073667` enumerate.
- H200 training deployment is synced with `gaze-dp/gaze-wam-cleanup` at `e111c7cdf77a`; `git status -sb` is clean. A safety stash remains: `stash@{Thu Jul 2 17:00:23 2026}: On gaze-wam-cleanup: pre-sync dirty tree before e111c7c 2026-07-02`.
- H200 data exists: HOT3D processed data, `data/hot3d_open_train.zarr`, `data/hot3d_open_val.zarr`, and Cosmos latent stats file. Default H200 `python` has `torch` and `cv2`, but did not have `zarr`; use or create the intended training environment before running zarr conversion/validation.
- H200 fetched from GitHub successfully during the sync to `e111c7cdf77a`.

## Environment Notes

- See `docs/deployment-environments.md` for the current environment/requirements inventory.
- QuestGazeClient is a Unity project and does not use a Python venv. Use Unity `6000.0.60f1` and `Packages/manifest.json`.
- Quest3DataCollector has committed `thirdparty\Quest3DataCollector\requirements.txt`, generated from the running remote `.venv312` package set. Local Collector has no venv yet; remote uses `.venv312` with Python `3.12.13`.
- Gaze-WAM is venv-only for current deployment. Use local `thirdparty\gaze-dp\.venv` and H200 `/mnt/workspace/shenyibo/gaze-wam/.venv`; do not use default H200 `python` for zarr work. H200 `.venv` uses `--system-site-packages`; install the frozen H200 snapshot with `python -m pip install --no-deps -r requirements.txt`. `requirements.txt`, `requirements-h200.txt`, `requirements-h200-editables.txt`, and `requirements-local-windows.txt` are committed on `gaze-wam-cleanup`. `conda_environment.yaml` is legacy reference only.

## Useful Checks

Local git state:

```powershell
git -C 'W:\实验室项目\Gaze-Project\thirdparty\QuestGazeClient' status -sb
git -C 'W:\实验室项目\Gaze-Project\thirdparty\Quest3DataCollector' status -sb
git -C 'W:\实验室项目\Gaze-Project\thirdparty\gaze-dp' status -sb
```

Collector deployment read-only status:

```powershell
ssh lvjun@10.128.0.227 "ps -ef | grep -F quest_pc_receiver.py | grep -v grep; ss -lunpt | grep -E ':9100|:9101|:8765' || true"
```

Training deployment read-only status:

```powershell
ssh H200-4042 "cd /mnt/workspace/shenyibo/gaze-wam && git status -sb && git rev-parse --short=12 HEAD && du -sh data/hot3d_open_train.zarr data/hot3d_open_val.zarr 2>/dev/null"
```

Quest device:

```powershell
adb devices
```

If the Quest shows `unauthorized`, ask the user to accept the RSA/USB debugging prompt inside the headset.

## Protocol And Runtime Facts

Quest formal recording:

- A button toggles formal recording.
- `QuestRecordingTelemetrySender.cs` sends UDP JSON datagrams to `10.128.0.227:9100`.
- Protocol: `quest_recording_telemetry_v1`.
- Events: `recording_start`, `sample`, `recording_stop`.
- Important sample fields: `recordId`, `sampleIndex`, Quest timestamps, gaze rays/points, eye/camera/head poses, left/right controller state.

Quest calibration recording:

- B button toggles PC calibration recording.
- `QuestPcCalibrationRecorder.cs` talks to `http://10.128.0.227:9101`.
- Endpoints: `/calibration/start`, `/calibration/sample`, `/calibration/stop`.

Collector receiver:

- Main script: `W:\实验室项目\Gaze-Project\thirdparty\Quest3DataCollector\pc\offline_calibration\scripts\quest_pc_receiver.py`.
- Remote viewer: `http://10.128.0.227:8765/`.
- Observed live receiver uses Flexiv network interface `192.168.2.108`, end RealSense serial `244222073667`, third RealSense serial `750612070265`, robot state 90 Hz, depth every 3 frames, FFV1 depth, Robotiq 2F-85 gripper.
- Coordinate conversion from Unity to PC/robot frame: `pc = [unity.z, -unity.x, unity.y]`.
- Teleop responsiveness can be analyzed with `quest_pc_receiver.py teleop-latency --pc-session <record_dir>`; formal robot recordings also auto-write `teleop_latency_analysis.json`, and replay exposes a Teleop latency panel.

Collector data layout:

- Formal recordings: `pc/offline_calibration/pc_recordings/<recordId>/`.
- Formal root files: `pc_telemetry_raw.jsonl`, `pc_samples.jsonl`, `pc_controllers.csv`, `pc_session_summary.json`.
- Robot/camera files: `robot_realsense/samples.jsonl`, `robot_realsense/robot_states.jsonl`, `robot_realsense/video_frames.jsonl`, `robot_realsense/controller_motion.jsonl`, `robot_realsense/gripper_commands.jsonl`, `cameras.json`, `capture_config.json`, videos/depth streams, `session_summary.json`.
- Teleop latency output: `teleop_latency_analysis.json`, comparing command target/controller speed to robot TCP speed on the Collector PC perf-counter timeline.
- Calibration raw: `pc/offline_calibration/raw/<recordId>/`.
- Calibration outputs: `pc/offline_calibration/outputs/pc_live_calibration/<recordId>/`.

Gaze-WAM training:

- Key dataset class: `W:\实验室项目\Gaze-Project\thirdparty\gaze-dp\diffusion_policy\dataset\gaze_wam_dataset.py`.
- Existing robot zarr tools:
  - `W:\实验室项目\Gaze-Project\thirdparty\gaze-dp\diffusion_policy\scripts\canonicalize_robot_gaze_wam_zarr.py`
  - `W:\实验室项目\Gaze-Project\thirdparty\gaze-dp\diffusion_policy\scripts\prepare_robot_gaze_wam_zarr.py`
  - `W:\实验室项目\Gaze-Project\thirdparty\gaze-dp\diffusion_policy\scripts\validate_gaze_wam_zarr.py`
- HOT3D processed data on H200: `/mnt/workspace/shenyibo/datasets/HOT3D/processed`.
- Existing open-data zarrs on H200: `data/hot3d_open_train.zarr`, `data/hot3d_open_val.zarr`.

## Collector-To-Zarr Bridge

The missing converter should turn Collector formal recording folders into robot zarr data for Gaze-WAM. Before implementing, confirm unresolved semantics with the user.

Candidate input streams:

- `pc_samples.jsonl` or `pc_telemetry_raw.jsonl` for Quest gaze/controller samples.
- `robot_realsense/video_frames.jsonl` plus video files for images.
- `robot_realsense/robot_states.jsonl` for executed TCP pose.
- `robot_realsense/controller_motion.jsonl` for teleop command target, if action labels should be command-based.
- `robot_realsense/gripper_commands.jsonl` or measured gripper state for gripper labels.

Candidate canonical zarr output:

- `data/camera0_rgb`
- `data/gaze_xy`
- `data/action_abs_tcp`
- `data/tcp_pose_abs`
- `data/gripper_width`
- optional masks/timestamps
- `meta/episode_ends`

Known decisions still open:

1. Confirm policy camera source and RealSense serial.
2. Confirm whether `action_abs_tcp` means executed future TCP, command target, or another target.
3. Confirm gripper label semantics.
4. Confirm how to synchronize the unmanaged remote Collector deployment with git.
