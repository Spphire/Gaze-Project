# Gaze Project Deployment Context

This is a compact fallback for `$gaze-project-context`. Prefer `W:\实验室项目\Gaze-Project\docs\agent-context.md` when that workspace file exists.

## Components

- Quest client: `W:\实验室项目\Gaze-Project\thirdparty\QuestGazeClient`, branch `main`, commit `dbc9b0d7cb61`, remote `git@github.com:Spphire/QuestGazeClient.git`. Legacy `W:\lasertag-projs` is a junction.
- Collector: `W:\实验室项目\Gaze-Project\thirdparty\Quest3DataCollector`, branch `quest3-chessboard-flexiv`, commit `81b8cfa17ab2`, remote `git@github.com:Spphire/Quest3DataCollector.git`. Legacy `W:\Quest3DataCollector` is a junction.
- Collector deployment: `lvjun@10.128.0.227:/ssd1/shenyibo/Quest3DataCollector`, no `.git` observed, receiver listens on UDP `9100`, TCP `9101`, TCP `8765`.
- Training: `W:\实验室项目\Gaze-Project\thirdparty\gaze-dp`, branch `gaze-wam-cleanup`, commit `e111c7cdf77a`, remote `git@github.com:Spphire/gaze-dp.git`. Legacy `W:\实验室项目\gaze-wam` is a junction.
- Training deployment: `H200-4042:/mnt/workspace/shenyibo/gaze-wam`, branch `gaze-wam-cleanup`, observed remote commit `e111c7cdf77a`, clean with one pre-sync safety stash.

## Protocols

- Quest formal recording: A button, UDP JSON, `quest_recording_telemetry_v1`, target `10.128.0.227:9100`.
- Quest calibration recording: B button, HTTP `quest_pc_calibration_recording_v1`, target `http://10.128.0.227:9101`.
- Collector viewer: `http://10.128.0.227:8765/`.
- Unity frame to PC frame: `pc = [unity.z, -unity.x, unity.y]`.
- Teleop latency: `quest_pc_receiver.py teleop-latency --pc-session <record_dir>` reads `teleop_latency_analysis.json` / `robot_realsense/controller_motion.jsonl` / `robot_realsense/robot_states.jsonl`; positive lag means robot TCP motion follows command/controller motion on the Collector PC timeline.

## Data Layout

- Formal Collector recordings: `pc/offline_calibration/pc_recordings/<recordId>/`.
- Formal files: `pc_telemetry_raw.jsonl`, `pc_samples.jsonl`, `pc_controllers.csv`, `pc_session_summary.json`.
- Robot/camera files: `robot_realsense/samples.jsonl`, `robot_states.jsonl`, `video_frames.jsonl`, `controller_motion.jsonl`, `gripper_commands.jsonl`, cameras/config/session metadata, videos/depth streams.
- Calibration raw: `pc/offline_calibration/raw/<recordId>/`.
- Calibration outputs: `pc/offline_calibration/outputs/pc_live_calibration/<recordId>/`.

## Gaze-WAM Bridge Target

The missing converter should produce robot zarr data with `data/camera0_rgb`, `data/gaze_xy`, `data/action_abs_tcp`, `data/tcp_pose_abs`, `data/gripper_width`, optional masks/timestamps, and `meta/episode_ends`. Use the existing Gaze-WAM scripts `prepare_robot_gaze_wam_zarr.py`, `canonicalize_robot_gaze_wam_zarr.py`, and `validate_gaze_wam_zarr.py` after conversion.

Confirm policy camera serial, action semantics, gripper label source, and remote Collector sync policy with the user before locking converter behavior.
