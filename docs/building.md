# Building and flashing

Flashing a release, building the firmware yourself, the tests and the serial console. Back to the [README](../README.md).

## Build and flash

**Flash a board with the latest release** (needs the GitHub CLI, `gh`):

```sh
scripts/flash-latest.sh           # or: scripts/flash-latest.sh v0.14.0
```

It downloads the release UF2, waits for the board's RP2350 drive (a blank
board shows it straight away; otherwise hold BOOT, tap RESET), copies the
firmware on and checks the board comes back as HDDSYNTH.

**Ready-made UF2s:** download `hddsynth-mk5-vX.Y.Z.uf2` from the
[latest release](https://github.com/MaverickUK/HDDSynth_Native/releases/latest).
GitHub Actions builds every push (the UF2 is in the run's artifacts) and
publishes a release for every `vX.Y.Z` tag.

To build it yourself, one-time setup: VS Code + the PlatformIO extension (or `pip install platformio`).

```sh
pio run                  # build -> .pio/build/mk5/firmware.uf2
pio run -t upload        # build and flash
pio device monitor       # serial console, 115200
```

**First flash** (the board is running CircuitPython):
1. Hold **S2 (BOOT)**, tap **S1 (RESET)**, release S2.
2. A drive called `RP2350` appears.
3. Run `pio run -t upload`, or drag `firmware.uf2` onto the drive.

After that, uploads reset the board into the bootloader automatically. The
serial command `b` also does it.

While the firmware runs, the board appears over USB as **HDDSYNTH** (by
"IDE Synth"). The `RP2350` drive name in bootloader mode comes from the
chip's boot ROM and doesn't change.

**Back to CircuitPython:** same BOOT/RESET dance, then drag the CircuitPython
UF2 back on. Your CIRCUITPY files are untouched by this firmware.

### Versioning

The firmware follows [Semantic Versioning](https://semver.org). The version
lives in `src/version.h`, is printed at boot and by the `h` command, and each
release commit is tagged `vX.Y.Z`.

- **MAJOR:** incompatible changes to the SD card layout or `settings.json`.
- **MINOR:** new features that stay backwards compatible.
- **PATCH:** bug fixes only.

While the version is `0.y.z`, anything may change between minor versions.

### Unit tests (runs locally, not on IDE Synth hardware)

```sh
test/run_native_tests.sh ../HDDSynth_Samples   # optional: path to sample packs
```

Covers:
- WAV parsing, including every file in the sample pack repo.
- The ring buffer and the mixer, under AddressSanitizer/UBSan.
- Two-thread producer/consumer tests that mirror core 0 and core 1.
- Beep synthesis, encoder decoding, button timing, the saved-state and
  power-log formats, and the jingle light show's level follower.
- The modelled drive: spin-up and coast-down times, seek physics, the
  workloads' pace, balance, parameter updates and the two-core handover.
  With node installed, it also renders the same scenario on the firmware's
  engine and the browser prototype's (`tools/drive-lab/compare.js`) and
  checks that they agree.

GitHub Actions runs them on every push.

## Serial console

```
h  help
s  stats now (also printed every 5 s in RUN)
t  stress test on/off: restarts streamed voices every 30-250 ms
p  simulate power loss (runs the spindown path)
a  toggle simulated HDD activity
+  / -  volume
>  / <  balance (towards access / towards idle)
n  next sample pack (same as a short press of the action button; remembered)
l  print the log of the last power loss (kept on the SD card)
k  play the next beep profile (to audition them)
d  list the SD card's root directory
m  demo mode on/off (as DEMO_MODE, not saved)
o  next OLED mode: activity, supercap, debug (not saved)
z  go into standby now (as if STANDBY_MINUTES had passed)
j  replay the jingle (clears its flag and reboots)
r  reboot
u  reboot into USB drive mode (share the SD card; eject it to return)
b  reboot into the USB bootloader
$  a line starting with $ is the companion app's protocol (companion.md)
```

Stats lines look like:

```
[stats] t=65s state=RUN heap=301234 mix_max=95us i2s_underflow=0 | idle: on under=0 min_ring=871ms | access: on under=0 min_ring=902ms | spindown: off under=0 min_ring=-
[stats] sd: chunks=4120 read_err=0 recoveries=0 failed_rec=0 max_read=2210us | stress: ON transitions=812 failures=0 | supercap=4148mV flt=1
```

- `under` counts samples the mixer had to fill with silence because the ring
  ran dry. **It should stay at 0.**
- `min_ring` is the lowest buffer level seen while streaming: the headroom
  against SD stalls.
- `max_read` is the slowest single 2 KB SD read since the last stats line.
- `i2s_underflow` means the audio core itself fell behind. It should never
  happen.

## Development notes

**Boot wait (debug only):** when you upload over USB (`pio run -t upload`,
or VS Code's Upload), the firmware waits up to 1.5 s at boot for the serial
console to attach, so you see the boot log; the log says
`debug build (USB upload)`. Every other build, including the GitHub release
UF2s, boots straight away. This is done by `scripts/serial_wait.py`.

`pio run -e mk5_stream_test` builds a test variant that always streams the
spindown from SD (no current pack is too big for RAM, so that path is
otherwise never used).
