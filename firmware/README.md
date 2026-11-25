# IDE Synth firmware

Native C++ firmware for the IDE Synth's MK5 board (RP2354A), under PlatformIO with the Arduino-Pico core: one core plays the sound, the other runs the SD card, controls, link and console. It began as [HDDSynth_Native](https://github.com/MaverickUK/HDDSynth_Native), whose history it continues; the board is in [../hardware](../hardware).

| Folder | What's in it |
|---|---|
| [src/](src) | The firmware. `version.h` holds the version |
| [test/](test) | Host-side unit tests (`test/run_native_tests.sh`, no hardware needed) |
| [scripts/](scripts) | `flash-latest.sh` (flash the latest release) and the build's helper scripts |
| [companion/](companion) | The companion app: your computer's disk activity over USB |
| [tools/drive-lab/](tools/drive-lab) | The Drive Lab, for tuning modelled drives by ear |

How to build, test and flash it, the serial console and versioning: [docs/building.md](../docs/building.md). How it works: [docs/architecture.md](../docs/architecture.md). Every change: [CHANGELOG.md](CHANGELOG.md).

## Versions

[Semantic Versioning](https://semver.org), in one place: `FIRMWARE_VERSION` in [src/version.h](src/version.h). Bump it in the commit that changes the firmware, with a [CHANGELOG.md](CHANGELOG.md) entry, and tag that commit `vX.Y.Z`: the build checks the tag matches `version.h` and publishes a release with the UF2 (`hddsynth-mk5-vX.Y.Z.uf2`). Releases up to v0.24.1 are on [HDDSynth_Native's releases page](https://github.com/MaverickUK/HDDSynth_Native/releases).
