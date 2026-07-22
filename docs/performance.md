# Data Collection Performance

Last updated: 2026-07-22, Asia/Shanghai.

This document defines the runtime performance contract for `QuestGazeClient`
and `Quest3DataCollector`. It does not cover Gaze-WAM training performance.

## Frequency Contract

| Stream | Target | Purpose |
| --- | ---: | --- |
| Flexiv robot state | 90 Hz | Preserve high-frequency executed robot motion and joint state. |
| RealSense RGB per camera | 30 Hz | Policy observation video. |
| Collector aligned samples | 30 Hz | Final training timeline combining the latest Quest, robot, and camera observations. |
| Quest formal video | 30 Hz | Quest-local synchronized camera record. |
| Quest formal trajectory/UDP sample | 30 Hz | Gaze, head, eye, and controller input for formal recording and teleoperation. |
| Quest B-button calibration | 15 Hz | Calibration-only JPEG/pose capture; not the policy training timeline. |

`robot_realsense/robot_states.jsonl` remains 90 Hz. Do not downsample it to
30 Hz during collection. `robot_realsense/samples.jsonl` is the fixed 30 Hz
training-alignment stream and references the newest available 90 Hz robot row
and 30 Hz camera frame at each scheduled tick.

## Implemented Optimizations

Quest:

- Formal camera, trajectory, and UDP output are fixed at 30 Hz.
- UDP UTF-8 buffers use `ArrayPool<byte>` instead of allocating one byte array
  per datagram.
- The RGBA-to-NV12 pipeline depth is 6 instead of 30, substantially reducing
  persistent native memory for dual-camera recording.
- The managed JNI `sbyte[]` frame buffer is reused. Java reports whether the
  MediaCodec queue accepted each frame, and metadata records pipeline and
  encoder drops.
- Environment depth scanning no longer starts two concurrent async loops.
- Gaze depth raycast buffers and matrix arrays are reused. The environment
  depth raycast runs at 30 Hz and its result is reused by the recorder instead
  of performing the same synchronous GPU raycast twice per rendered frame.

Collector:

- Quest input remains latest-value driven, but formal fusion is written by an
  independent fixed-deadline 30 Hz sampler.
- Flexiv state polling uses a fixed-deadline 90 Hz loop rather than accumulating
  phase drift after slow calls.
- RGB and depth frames are passed to ffmpeg with buffer views instead of
  allocating full-frame `bytes` objects with `numpy.tobytes()`.
- RealSense rate quality is computed from camera capture timestamps, while
  capture-to-write latency separately measures encoder and disk backlog.
- PC raw telemetry and controller CSV logs preserve every received formal
  Quest sample; only `robot_realsense/samples.jsonl` is resampled onto the
  fixed 30 Hz training timeline.
- Formal summaries record effective rate, target rate, p95 gap, p95 lateness,
  missed ticks, source age, camera queue drops, and capture-to-write latency.

At 1280x720 with two RGB cameras and depth every third frame, removing
`tobytes()` avoids roughly 203 MB/s of temporary Python byte allocations. The
Quest pipeline change reduces its persistent RGBA/NV12 ring memory by 80%; the
exact byte count is stored in Quest recording metadata because passthrough
resolution may vary.

## Quality Gates

Run after every representative formal recording:

```bash
cd /ssd1/shenyibo/Quest3DataCollector
.venv312/bin/python pc/offline_calibration/scripts/quest_pc_receiver.py audit-performance \
  --pc-session pc/offline_calibration/pc_recordings/<record_id>
```

Default gates:

- Robot and camera effective rate must be at least 95% of target.
- Robot state p95 gap must be no more than 1.5 times the 90 Hz period.
- Robot sampler p95 lateness must be at most 6 ms with zero missed ticks.
- Final aligned sampler p95 lateness must be at most 15 ms with zero missed
  ticks.
- Aligned Quest source age p95 must be at most 50 ms.
- Camera queue drop ratio must be zero.
- Camera capture-to-write latency p95 must be at most 100 ms.

The final record is not considered performance-qualified merely because files
exist. `audit-performance` must pass, and Quest metadata must report
`recordingQualitySummary: ok` with no video or trajectory drops.

## Safe Live Evaluation

Live performance evaluation may read robot state, camera streams, process
metrics, disk metrics, and Quest profiler counters. It must not call robot arm,
freedrive, or Cartesian target endpoints. Do not hold the Quest right grip/side
trigger during a no-motion benchmark. Gripper movement is permitted only when a
test explicitly needs it.

Start the benchmark receiver with:

```bash
.venv312/bin/python pc/offline_calibration/scripts/quest_pc_receiver.py receive \
  <normal lab options> --formal-control-mode record_only
```

Suggested test duration is at least 60 seconds, preferably 5 minutes, with both
RealSense cameras and depth enabled. Collect:

- Quest frame time, CPU, memory, thermal status, and recording metadata.
- Collector process CPU/RSS/thread count and disk throughput.
- `session_summary.json` performance payload and `audit-performance` output.
- Camera/depth ffmpeg logs when a stream fails or drops.

On 2026-07-17 Quest `2G0YC1ZF940X95` was tested locally with Wi-Fi disabled.
Dual H.264 video, gaze, and synchronized trajectory recording worked, both
videos decoded fully, and pipeline/encoder drops were zero. A finalized-file
SHA256 bug was fixed and verified. The strict timing gate did not pass: a
122-second quiet run reported five trajectory missed ticks and one common
camera/trajectory pause of about 200-213 ms, correlated with a Horizon `ocal`
color-camera stream transition. The Collector remained unreachable, so the
end-to-end benchmark is still pending. See
[quest-endpoint-test-20260717.md](quest-endpoint-test-20260717.md).

## Qualified Hardware Runs - 2026-07-22

Quest record `record_20260722_140745` ran for 397.199 seconds with metadata v12:

- trajectory: 29.9983 Hz, zero missed ticks;
- left/right video: 29.9989 / 29.9989 Hz;
- output missed ticks: 0 / 0;
- source reuse: 71 / 75, maximum source age 75 / 79 ms;
- both finalized MP4 SHA256 values matched metadata and both videos decoded fully.

The bounded real-robot run `record_bounded_teleop_v3_20260722_180900` passed
all 26 `audit-performance` checks:

- Flexiv state: 89.99995 Hz, p95 gap 11.5 ms, p95 lateness 0.5 ms, zero missed ticks;
- aligned output: 29.99755 Hz, p95 gap 34.3 ms, p95 lateness 8.9 ms;
- Quest source age p95: 27.4 ms; reuse 109 / 3925, or 2.8%;
- end/third RealSense RGB: 29.9786 / 29.9791 Hz;
- camera queue drops: 0; capture-to-write p95: 3.8 / 4.2 ms;
- UDP loss, duplicate, and reorder counts: 0; maximum datagram: 1423 bytes;
- generated range: 39.992 mm / 7.998 deg; actual TCP range: 40.500 mm / 7.957 deg;
- hard range: 50 mm / 10 deg; watchdog: 49 mm / 9.8 deg; no violation;
- 1058 TCP targets were sent at about 8.81 Hz; the final motion state was disarmed.

The bounded run used the synthetic random-walk sender requested for safe
qualification, not physical Touch-controller input. `targetToRobot` reported a
280 ms correlation peak at correlation 0.681 and no target onset events.
`controllerToRobot` found five onset events with mean 36.8 ms and p95 42.8 ms.
These are responsiveness correlation/onset metrics on the Collector PC clock,
not absolute one-way network latency.

Committed evidence lives under:

- `artifacts/record_20260722_140745/quest_camera_metadata.json`
- `artifacts/record_bounded_teleop_v3_20260722_180900/performance_audit.json`
- `artifacts/record_bounded_teleop_v3_20260722_180900/bounded_teleop_probe_report.json`
- `artifacts/record_bounded_teleop_v3_20260722_180900/teleop_latency_analysis.json`
- `artifacts/record_bounded_teleop_v3_20260722_180900/pc_session_summary.json`

## Build Path Constraint

Unity Android tools reject non-ASCII project paths. The source remains under:

```text
W:\实验室项目\Gaze-Project\thirdparty\QuestGazeClient
```

Build through the zero-copy junction registered in UnityHub:

```text
W:\lasertag-projs
```

Both paths point to the same working tree.
