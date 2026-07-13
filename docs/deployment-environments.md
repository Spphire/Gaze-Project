# Deployment Environments

Last checked: 2026-07-02, Asia/Shanghai.

This document records the runtime environments for the three local projects now consolidated under `W:\实验室项目\Gaze-Project\thirdparty`.

Venv policy: do not use conda as the active deployment path. Use project venvs plus requirements snapshots. `conda_environment.yaml` in Gaze-WAM is retained only as historical reference.

## Summary

| Component | Local path | Environment status | Requirement source |
| --- | --- | --- | --- |
| QuestGazeClient | `thirdparty\QuestGazeClient` | Unity project, no Python venv expected. UnityHub points here. | `ProjectSettings\ProjectVersion.txt`, `Packages\manifest.json`, `Packages\packages-lock.json`. |
| Quest3DataCollector | `thirdparty\Quest3DataCollector` | No local venv currently. Remote deployment uses `.venv312`. | Committed `thirdparty\Quest3DataCollector\requirements.txt`, created from the running remote `.venv312`. |
| gaze-dp / Gaze-WAM | `thirdparty\gaze-dp` | Local `.venv` exists. H200 remote `.venv` exists. Default H200 `python` is not the project env. | Committed venv requirements: `requirements.txt` / `requirements-h200.txt` for H200 and `requirements-local-windows.txt` for local Windows. `conda_environment.yaml` is legacy reference only. |

## QuestGazeClient

QuestGazeClient is a Unity/Android project, so Python `requirements.txt` and venv are not applicable.

Checked facts:

- Unity version: `6000.0.60f1`.
- Package manifest: `thirdparty\QuestGazeClient\Packages\manifest.json`.
- Package lock: `thirdparty\QuestGazeClient\Packages\packages-lock.json`.
- UnityHub project entry points to `W:\实验室项目\Gaze-Project\thirdparty\QuestGazeClient`.
- Quest USB device is authorized as `2G0YC1ZF940X95`.
- Android package `com.Apricity.EyeTrackingTest` is installed on Quest.

## Quest3DataCollector

Local project currently has no local venv. The remote deployment at `lvjun@10.128.0.227:/ssd1/shenyibo/Quest3DataCollector` uses:

- venv: `/ssd1/shenyibo/Quest3DataCollector/.venv312`
- Python: `3.12.13`
- pip: `26.1.2`

The runtime package set from that venv is captured in:

- `thirdparty\Quest3DataCollector\requirements.txt`

To recreate the receiver environment on Linux:

```bash
cd /ssd1/shenyibo/Quest3DataCollector
python3.12 -m venv .venv312
. .venv312/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
```

Runtime hardware/system assumptions still live outside pip:

- Flexiv RDK/license and robot network reachability.
- RealSense USB access and firmware compatibility.
- Robotiq gripper device access when gripper capture is enabled.
- Collector PC network interface `192.168.2.108` for Flexiv side.

Remote runtime currently listens on UDP `9100`, HTTP `9101`, and viewer `8765`.

## Gaze-WAM

Gaze-WAM should use venv, not conda, for current local and H200 deployments. The existing `conda_environment.yaml` is legacy reference only and should not be used as the deployment entry point.

Requirement files:

- `thirdparty\gaze-dp\requirements.txt`: canonical H200 training venv snapshot, sanitized so `pip install -r requirements.txt` can parse it.
- `thirdparty\gaze-dp\requirements-h200.txt`: same sanitized H200 snapshot, kept explicit for deployment review.
- `thirdparty\gaze-dp\requirements-h200-editables.txt`: non-portable editable installs observed in the H200 venv freeze; review before vendorizing or replacing with VCS URLs.
- `thirdparty\gaze-dp\requirements-local-windows.txt`: local Windows venv snapshot.

Local Windows workspace:

- venv: `thirdparty\gaze-dp\.venv`
- Python: `3.12.13`
- pip: `25.0.1`
- checked packages include `torch==2.11.0+cu128`, `zarr==2.18.7`, `opencv-python==4.13.0.92`, `hydra-core==1.3.2`, `diffusers==0.38.0`, `timm==1.0.27`.
- snapshot file: `thirdparty\gaze-dp\requirements-local-windows.txt`.

H200 deployment:

- venv: `/mnt/workspace/shenyibo/gaze-wam/.venv`
- Python: `3.12.12`
- pip: `25.0.1`
- `.venv` was created with `--system-site-packages`.
- checked packages include `torch==2.7.1+cu126`, `zarr==2.18.7`, `numpy==2.4.6`, `cv2==4.13.0`, `hydra==1.3.3`, `diffusers==0.36.0`, `timm==1.0.25`.
- Default `/usr/local/bin/python` on H200 did not have `zarr`; use `.venv/bin/python` for zarr conversion/validation/training tasks.
- snapshot files: `thirdparty\gaze-dp\requirements.txt` and `thirdparty\gaze-dp\requirements-h200.txt`.
- non-portable editable paths are listed separately in `thirdparty\gaze-dp\requirements-h200-editables.txt`.

To recreate or refresh the H200 venv from the snapshot:

```bash
cd /mnt/workspace/shenyibo/gaze-wam
python3.12 -m venv --system-site-packages .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install --no-deps -r requirements.txt
```

Use `--no-deps` for this frozen snapshot because the current H200 environment pins CUDA/PyTorch-family packages in a way that pip's dependency resolver reports as conflicting, even though the existing deployment imports the required modules successfully.

Do not replace H200 `.venv` from the local Windows `.venv` freeze. CUDA/PyTorch builds differ. The H200 requirements snapshot is the deployment baseline; any external editable installs must be reviewed separately from `requirements-h200-editables.txt`.

## Open Environment Work

Synced on 2026-07-02:

- Collector `.gitignore` and `requirements.txt` were copied to `lvjun@10.128.0.227:/ssd1/shenyibo/Quest3DataCollector/`.
- Gaze-WAM `requirements.txt`, `requirements-h200.txt`, `requirements-h200-editables.txt`, and `requirements-local-windows.txt` were copied to `H200-4042:/mnt/workspace/shenyibo/gaze-wam/`.
- Collector requirements are committed and pushed on `quest3-chessboard-flexiv` at `81b8cfa17ab2`.
- Gaze-WAM requirements are committed and pushed on `gaze-wam-cleanup` at `e111c7cdf77a`; H200 fast-forwarded to the same commit and is clean, with one pre-sync safety stash retained.
- Collector `.venv312` dry-run passed with `python -m pip install --dry-run -r requirements.txt`.
- H200 `.venv` dry-run passed with `python -m pip install --dry-run --no-deps -r requirements.txt`.

Remaining environment work:

1. Decide whether the H200 editable installs in `requirements-h200-editables.txt` should be preserved, removed, vendorized, or replaced by VCS URLs.
2. After Collector-to-zarr conversion is implemented, add converter-specific dependencies to either Collector requirements, Gaze-WAM requirements, or a separate bridge requirements file.
