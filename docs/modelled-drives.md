# Modelled drives

A sample pack that is a physics model of a drive (`drive.json`) instead of recordings. Back to the [README](../README.md).

## drive.json

A pack can be a **model of a drive** instead of recordings: put a
`drive.json` in its folder (the WAVs are then ignored, and can be left
out). The firmware synthesises the drive live on the audio core:

- **The spindle** spins up and coasts down with real dynamics: rotation hum
  at rpm/60 Hz, the motor's whine at rpm/60 × slots (loudest while it
  works hard, so the spin-up rises then settles), bearing noise and the air
  dragged round by the platters.
- **A virtual head** seeks with real actuator physics. A voice coil
  accelerates at full force and brakes at full force (bang-bang), so short
  seeks tick and long ones clunk, and each force change rings the arm and
  case. A stepper clicks once per cylinder. Power-on unparks and calibrates;
  power-off parks (with the latch's clack) and coasts down.
- **HDD activity** sets a virtual workload: random access, or a file copy
  (sequential, with trips to the FAT). The head's pace is a real drive's:
  each random access waits for the seek and for the sector to come round.
  A plain HDD LED can't say which kind of access it is, so activity that
  stays on for 1.5 s counts as a file copy; with the IDE Synth Bay link or
  the companion app, their own class decides.

Volume, the pack's `GAIN`, `PLAY_SPINUP`, `PLAY_IDLE`, `PLAY_SPINDOWN`,
standby and demo mode all work as with recorded packs. **Balance** mixes the
running sound (spindle, bearing, air) against the seeks (actuator, servo);
at 0.5 both are at full level.

The easiest way to make one is the **Drive Lab**, online at
<https://maverickuk.github.io/HDDSynth_Native/drive-lab/> (source in
[`tools/drive-lab`](../firmware/tools/drive-lab)): tune the drive by ear, with a real
pack's WAV alongside to compare, and download its `drive.json`.
The smallest drive.json names a built-in preset, and any group can then
change some of its parameters:

```json
{ "format": "hddsynth-drive", "version": 2, "name": "1997 voice coil",
  "preset": "voice97", "sampleRate": 32000,
  "spindle": { "rpm": 7200 }, "bearing": { "type": "fdb" } }
```

The Drive Lab exports every group in full, grouped as its cards. The flat
format of v0.20.0 and v0.21.0 (version 1, one `params` object) is refused
(the log says so): set the drive up again in the Drive Lab and copy the
new one.

| Key | Default | What it does |
|---|---|---|
| `preset` | `voice97` | Starting parameters: `stepper85` (1985, 5.25″ MFM stepper, 3600 rpm), `voice91` (1991, 3.5″ voice coil, 3600 rpm, landing zone), `voice97` (1997, 5400 rpm, thermal recalibration) or `fdb05` (2005, 7200 rpm, fluid bearing, ramp load). |
| `sampleRate` | `32000` | The output rate while the pack plays: 16000, 22050, 32000, 44100 or 48000. The engine takes about a quarter of the audio core at 32 kHz. |
| `name` | *(none)* | Logged at load (`pack.json`'s `NAME` still names the pack). |
| *the groups below* | *(none)* | Each overrides the preset's parameters it names. Unknown groups or keys, and bad values, are logged and skipped. |

The groups and their parameters, as the Drive Lab's cards (numbers are
clamped to their range):

| Group | Parameters |
|---|---|
| `spindle` | `rpm` (1800-15000), `spinupS` (1-20 s), `coastS` (2-30 s, the coast-down and so the spindown's length), `slots` (6-18), `polePairs` (2-8), `whine`, `hum`, `imbalance` (0-1) |
| `platters` (platters and air) | `count` (1-10), `size` (`"5.25"`, `"3.5"`, `"2.5"`), `windage` (0-1), `zoned` (true: LBA 0 at the outer edge, with more sectors per track there) |
| `bearing` | `type` (`"ball"`, `"fdb"`), `wear`, `noise` (0-1) |
| `actuator` | `type` (`"voice"`, `"stepper"`), `cylinders` (300-100000), `tick` (0-1, the track-to-track tick); voice coil: `fullStrokeMs` (8-60), `trackMs` (0.5-8), `settleDamp` (0.1-1.2), `buzz` (0-1); stepper: `stepMs` (0.2-6), `stepRamp` (0-1, buffered seeks) |
| `resonance` (arm and case) | `armHz` (200-4000), `armRingMs` (5-200), `caseHz` (80-1200), `caseRingMs` (10-400), `hardness` (0-1) |
| `heads` (head events) | `parking` (`"ramp"`, `"zone"`, `"none"`), `calSeeks` (0-8), `recalS` (0-120 s, 0 off), `wedges` (0-400 servo wedges), `servo` (0-1) |
| `enclosure` | `mount` (`"bare"`, `"case"`, `"sled"`), `bright` (-1 to 1), `caseRes` (0-1) |
| `mixer` | `spindle`, `bearing`, `air`, `actuator`, `servo` (0-1.5, per layer), `master` (0-1.5). The Drive Lab exports its mixer's gains (not mute or solo). |

The spindown on a power cut is the coast-down: `coastS` long, entirely
from RAM, like a recorded spindown in RAM. The serial `t` stress test
exercises SD streaming, so it isn't available with a modelled pack.
