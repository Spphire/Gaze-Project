# Deployment

Last updated: 2026-07-22, Asia/Shanghai.

## Deployment Inventory

| Component | Deployment | Current purpose |
| --- | --- | --- |
| QuestGazeClient | Quest 3 device, package `com.Apricity.EyeTrackingTest` | Sends formal recording telemetry over UDP and calibration samples over HTTP. |
| Quest3DataCollector | `lvjun@10.128.1.95:/ssd1/shenyibo/Quest3DataCollector` | Receives Quest telemetry, records Flexiv/RealSense/gripper streams, serves viewer. |
| gaze-dp / Gaze-WAM | `H200-4042:/mnt/workspace/shenyibo/gaze-wam` | Trains and validates gaze-conditioned policies using HOT3D and future robot zarr data. |

## Network Protocols

| Path | Protocol | Endpoint |
| --- | --- | --- |
| Quest formal recording | UDP JSON | `10.128.1.95:9100` |
| Quest PC calibration recording | HTTP | `http://10.128.1.95:9101` |
| Collector viewer | HTTP | `http://10.128.1.95:8765/` |

## Collector Runtime

Observed lab receiver command:

```bash
/ssd1/shenyibo/Quest3DataCollector/.venv312/bin/python \
  pc/offline_calibration/scripts/quest_pc_receiver.py receive \
  --host 0.0.0.0 --port 9100 \
  --visualize --visualize-host 0.0.0.0 --visualize-port 8765 \
  --no-open-browser \
  --flexiv-network-interface 192.168.2.108 \
  --realsense-serial 244222073667 \
  --third-realsense-serial 750612070265 \
  --robot-state-hz 90 \
  --formal-control-mode record_only \
  --record-realsense-depth-every-n-frames 3 \
  --record-realsense-depth-format ffv1
```

Read-only health check:

```powershell
ssh lvjun@10.128.1.95 "cd /ssd1/shenyibo/Quest3DataCollector && git status -sb && git rev-parse --short=12 HEAD; pgrep -af quest_pc_receiver.py"
curl.exe -s -o NUL -w "%{http_code}\n" http://10.128.1.95:8765/
```

Important state:

- Remote Collector is a clean Git checkout on `codex/lvjun-deployment-preserved-20260722` at `9bc2dfc66734`, tracking the same branch on GitHub.
- `.venv312` is the active receiver environment.
- The current receiver is deliberately parked in `record_only`; normal formal teleoperation requires restarting with `controller_teleop` after an operator safety check.
- Runtime hardware assumptions include Flexiv RDK/license, robot network access,
  RealSense USB access, and gripper device access.

## H200 Training Runtime

Canonical deployment:

```bash
ssh H200-4042
cd /mnt/workspace/shenyibo/gaze-wam
. .venv/bin/activate
```

Read-only health check:

```powershell
ssh H200-4042 "cd /mnt/workspace/shenyibo/gaze-wam && git status -sb && git rev-parse --short=12 HEAD && .venv/bin/python - <<'PY'
import torch, zarr, cv2
print('torch', torch.__version__)
print('zarr', zarr.__version__)
print('cv2', cv2.__version__)
PY"
```

Use `.venv/bin/python`; do not use default H200 `python` for zarr
conversion/validation.

## Sync Policy

Shell repo:

```powershell
git -C W:\实验室项目\Gaze-Project push origin main
```

Component repos:

```powershell
git -C W:\实验室项目\Gaze-Project\thirdparty\QuestGazeClient push origin main
git -C W:\实验室项目\Gaze-Project\thirdparty\Quest3DataCollector push origin quest3-chessboard-flexiv
git -C W:\实验室项目\Gaze-Project\thirdparty\gaze-dp push gaze-dp gaze-wam-cleanup
```

Do not overwrite remote deployments with local files before checking remote
status and running process state. Preserve deployment-only changes on a branch,
then use fast-forward Git updates for reviewed code.
