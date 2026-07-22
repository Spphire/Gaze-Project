# Usage

Last updated: 2026-07-22, Asia/Shanghai.

This document is the operator-level workflow across the three project
components. Component-specific details live in each `thirdparty` repository.

## 1. Start Or Check Collector

On the Collector PC:

```bash
ssh lvjun@10.128.1.95
cd /ssd1/shenyibo/Quest3DataCollector
pc/offline_calibration/scripts/start_lab_receiver.sh --restart
```

From this workstation, check:

```powershell
curl.exe -s -o NUL -w "%{http_code}\n" http://10.128.1.95:8765/
```

Expected result: `200`.

Viewer:

- `http://10.128.1.95:8765/`
- `http://10.128.1.95:8765/recordings`

## 2. Quest Recording

Quest app package:

```text
com.Apricity.EyeTrackingTest
```

Check device:

```powershell
adb devices
```

Controls:

- A button: start/stop formal recording telemetry.
- B button: start/stop PC calibration recording.
- Right hand side/grip trigger: enable right-controller robot teleop during
  formal robot recording.
- Right index trigger: gripper control when gripper support is enabled.

## 3. Calibration

Quest B-button calibration sends HTTP samples to:

```text
http://10.128.1.95:9101
```

Collector raw calibration folders:

```text
pc/offline_calibration/raw/<recordId>/
```

Collector calibration outputs:

```text
pc/offline_calibration/outputs/pc_live_calibration/<recordId>/
```

## 4. Formal Recording Artifacts

Formal A-button recordings are written under:

```text
pc/offline_calibration/pc_recordings/<recordId>/
```

Important files:

- `pc_telemetry_raw.jsonl`
- `pc_samples.jsonl`
- `pc_controllers.csv`
- `pc_session_summary.json`
- `robot_realsense/robot_states.jsonl`
- `robot_realsense/controller_motion.jsonl`
- `robot_realsense/video_frames.jsonl`
- `robot_realsense/gripper_commands.jsonl`
- `robot_realsense/samples.jsonl`, the fixed 30 Hz training-alignment stream
- `teleop_latency_analysis.json`, when teleop latency analysis has run

Rate contract:

- `robot_realsense/robot_states.jsonl`: 90 Hz Flexiv state.
- RealSense video: 30 Hz per role.
- `robot_realsense/samples.jsonl`: stable 30 Hz fused timeline.

Performance audit:

```bash
.venv312/bin/python pc/offline_calibration/scripts/quest_pc_receiver.py audit-performance \
  --pc-session pc/offline_calibration/pc_recordings/<record_id>
```

## 5. Replay And Teleop Latency

Open:

```text
http://10.128.1.95:8765/recordings
```

Select a record to inspect Quest samples, gaze, controller poses, robot TCP,
camera videos, gripper events, and teleop latency.

Manual teleop latency analysis:

```bash
cd /ssd1/shenyibo/Quest3DataCollector
.venv312/bin/python pc/offline_calibration/scripts/quest_pc_receiver.py teleop-latency \
  --pc-session pc/offline_calibration/pc_recordings/<record_id>
```

Interpretation:

- `targetToRobot` is preferred. It compares Collector command target TCP speed
  to Flexiv robot TCP speed on the same PC timeline.
- `controllerToRobot` is a fallback. It compares Quest right-controller motion
  to Flexiv robot TCP speed.
- Positive lag means robot motion follows the command/controller by that delay.
- This is a system responsiveness metric, not absolute one-way network latency.

## 6. Training Handoff

Current Gaze-WAM training deployment:

```bash
ssh H200-4042
cd /mnt/workspace/shenyibo/gaze-wam
. .venv/bin/activate
```

Current missing bridge:

```text
Collector pc_recordings/<recordId>/ -> canonical Gaze-WAM robot zarr
```

Do not lock converter semantics without confirming:

- policy camera source and serial
- `action_abs_tcp` target definition
- gripper label source
- timestamp alignment strategy
