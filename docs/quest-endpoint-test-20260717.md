# Quest Endpoint Hardware Test - 2026-07-17

This report covers Quest-only validation of `QuestGazeClient`. The Collector PC
at `10.128.0.227` was unreachable, so no Collector, Flexiv, RealSense, or
end-to-end latency claim is included.

## Safety Boundary

- Quest serial: `2G0YC1ZF940X95` (`Quest 3`, Android 14).
- Quest Wi-Fi was disabled before the app was launched or a recording command
  was sent.
- Collector ports `22`, `8765`, `9100`, and `9101` were unreachable.
- The robot receiver was never started and no arm, Cartesian, freedrive, or
  gripper command was sent.
- The app was force-stopped before Wi-Fi was restored.
- Temporary Quest proximity automation was restored after the test.

## Deployment And Data Preservation

The package already on the Quest had SHA256
`474697EE26247EA41F0E0FCB140585A18E0A480224DCF1A52C4601B5EBF5369C`.
It used a different signing key and produced metadata schema `v6` with a
nominal 60 Hz target. Android therefore rejected an in-place update.

Before uninstalling it, the old APK and all app files were backed up. After the
test, all historical recordings were restored and verified:

- 17 historical record directories.
- 102 files.
- 697,781,302 file bytes, identical before and after restore.

The first target APK had SHA256
`E92AFC6165EEF5AA92879AABFFC2C066334E3BDBA5CA5FC30811D836C3DA8CEE`.
Testing exposed that its metadata hash represented encoded H.264 sample bytes,
not the finalized MP4 container. `EncorderThread.java` was changed to hash the
file after `MediaMuxer.stop()` and `release()`.

The fixed APK was built successfully with Unity `6000.0.60f1` through
`W:\lasertag-projs`:

- APK SHA256: `71F30C3E65E68A9908607B22C8C4293E0F7336D20650ECEFB0F3845A12DF1A48`.
- APK size: 166,255,380 bytes.
- Build log: `W:\lasertag-projs\Logs\codex_quest_hash_build_20260717.log`.
- Device APK hash matched the local APK exactly after installation.

## Permissions And Unattended Operation

The following grants were required after reinstalling the package:

```powershell
adb shell pm grant com.Apricity.EyeTrackingTest android.permission.CAMERA
adb shell pm grant com.Apricity.EyeTrackingTest horizonos.permission.HEADSET_CAMERA
adb shell pm grant com.Apricity.EyeTrackingTest com.oculus.permission.USE_SCENE
adb shell cmd appops set com.Apricity.EyeTrackingTest CAMERA allow
adb shell cmd appops set com.Apricity.EyeTrackingTest HEADSET_CAMERA allow
```

Without `horizonos.permission.HEADSET_CAMERA`, Horizon opened a permission
activity and paused Unity. For an unattended USB test, the following temporary
broadcasts kept the headset awake:

```powershell
adb shell am broadcast -a com.oculus.vrpowermanager.automation_disable
adb shell am broadcast -a com.oculus.vrpowermanager.prox_close
```

They must always be restored:

```powershell
adb shell am broadcast -a com.oculus.vrpowermanager.prox_open
adb shell am broadcast -a com.oculus.vrpowermanager.automation_enable
```

The app command bridge consumed `record_command.txt` from
`/sdcard/Android/data/com.Apricity.EyeTrackingTest/files/`. The startup probe
reported `recorderReady=true`, both cameras enabled, synchronized trajectory
enabled, and the recording scene active.

## Test Results

| Metric | 76.62 s run | 122.18 s quiet run |
| --- | ---: | ---: |
| Metadata schema | v7 | v7 |
| Left video effective rate | 29.143 Hz | 29.464 Hz |
| Right video effective rate | 29.169 Hz | 29.496 Hz |
| Trajectory metadata rate | 29.952 Hz | 29.881 Hz |
| Left frames | 2,233 | 3,600 |
| Right frames | 2,235 | 3,604 |
| Trajectory samples | 2,295 | 3,651 |
| Pipeline drops, left/right | 0 / 0 | 0 / 0 |
| Encoder drops, left/right | 0 / 0 | 0 / 0 |
| Trajectory missed ticks | 1 | 5 |
| Gaze sample/hit ratio | 1.0 / 1.0 | 1.0 / 1.0 |
| Metadata MP4 SHA matches file | no, pre-fix build | yes / yes |
| Full MP4 decode | pass / pass | pass / pass |
| `recordingQualitySummary` | `trajectory_sample_missed_ticks` | `trajectory_sample_missed_ticks` |

The quiet run MP4s were H.264 High, `640x480`, `yuv420p`, fixed 30 fps:

- Left: 3,600 frames, 120.000 seconds, full decode exit 0.
- Right: 3,604 frames, 120.133 seconds, full decode exit 0.
- Final MP4 SHA256 values matched metadata exactly after the hash fix.
- Quest process RSS after recording was approximately 1.62 GB; SoC temperature
  was approximately 43 C and no app crash or encoder queue drop was observed.

## Timing Finding

The quiet run did not satisfy the strict zero-missed-tick gate:

- Left camera timestamp p95 gap: 34.0 ms; maximum: 200.0 ms.
- Right camera timestamp p95 gap: 34.0 ms; maximum: 200.0 ms.
- Trajectory p95 gap: 43.245 ms; maximum: 212.863 ms.
- The largest camera and trajectory pause occurred at the same point, about
  65 seconds into the recording.

The matching system log window showed Horizon's `ocal` client changing the
color-camera stream configuration and reporting a late color frame set. No GC,
MediaCodec queue-full event, app crash, or out-of-memory event coincided with
the pause. The current evidence therefore points to a Quest system camera mux
transition rather than Collector load or test-file polling.

## Verdict

Passed:

- Authorized USB deployment and exact APK verification.
- Recording command bridge and unattended permission setup.
- Dual-camera recording, synchronized trajectory, gaze coverage, and file
  creation.
- Zero app pipeline drops and zero MediaCodec enqueue drops.
- Final MP4 integrity hashes and complete video decoding.
- Backup and byte-exact restoration of historical recordings.

Not yet passed:

- Stable Quest camera/trajectory timing with zero missed ticks.
- Controller-pose coverage; no physical controller was active in the
  unattended test.
- End-to-end Quest-to-Collector 30 Hz, Flexiv 90 Hz, RealSense 30 Hz, and
  teleop-latency qualification because the Collector PC was unreachable.

Do not weaken the missed-tick gate based on this run. The next investigation
should determine whether Horizon `ocal` transitions can be disabled safely for
formal collection or whether camera acquisition must be isolated from the
Unity main-thread trajectory clock. After that, run a five-minute worn-headset
test with controllers and a Collector receiver explicitly started with
`--formal-control-mode record_only`.

## Final Device State

- Fixed APK `71F30C...1A48` remains installed.
- App is stopped.
- Wi-Fi is restored (`10.128.1.5/23`).
- Normal proximity behavior is restored.
- Historical recordings and the two new Quest-only test recordings are on the
  device; the record root contains 19 directories and uses about 781 MiB.
- Collector PC remains unreachable on `22`, `8765`, `9100`, and `9101`.
