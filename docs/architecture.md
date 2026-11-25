# How it works

The two cores, where each sound plays from, and what happens when the power goes. Back to the [README](../README.md).

## Architecture

| Core | Owns | Never does |
|---|---|---|
| **Core 1** | Mixer and I2S output. Reads RAM only. | Touch the SD card, block, allocate |
| **Core 0** | SD card (sole owner), power monitoring, LEDs, activity, serial console | Generate audio |

The two cores share only lock-free ring buffers (about 1 s of audio per
streamed voice) and a small per-voice state handshake (see `src/mixer.h`).
Because only core 0 ever touches the SD card, the CircuitPython race cannot
occur. An SD stall or read error just drains the ring while core 0 retries
or re-initialises the card.

- **Samples:** only the spindown is held in RAM; everything else streams
  from SD (see below).
- **Power loss** comes from the eFuse FLT pin: an interrupt plus a 3 ms
  confirmation, instead of 50 ms+ polling.
- **Safety:**
  - Hardware watchdog (2 s), fed only while the audio core's heartbeat is
    advancing.
  - SD transfers are CRC-checked (`USE_SD_CRC=1`).
  - Level changes ramp over one 8 ms block, so there are no clicks.

### Where each sound plays from

| Sound | Plays from | Loaded |
|---|---|---|
| Idle | SD, streamed through its own 32 KB buffer (~1 s) | Buffer filled while the spinup plays, so RUN starts seamlessly; topped up continuously |
| Access | SD, streamed through its own 32 KB buffer (~1 s) | As idle. It plays all the time; HDD activity only changes its volume. After each burst it silently jumps to a random point, so regular activity doesn't keep hearing the same part of the loop |
| Spinup | SD, streamed through a shared 32 KB "one-shot" buffer | At boot |
| Jingle | SD, streamed through the one-shot buffer | First boot, before the spinup |
| Spindown | **RAM**, the whole file, if it fits; otherwise SD through the one-shot buffer | When the pack loads (boot or pack change); the previous pack's copy is freed first |
| Beeps | Neither: the audio core synthesises each sample as it plays | n/a |
| Modelled drive | Neither: the audio core synthesises it (`drive.json` packs) | Its engine (2.9 KB) is allocated when the pack loads, and freed when it unloads |

**Why the spindown is in RAM:** it plays while the power is failing,
running off the supercap. From RAM it starts instantly and needs nothing
else to keep working. Streaming would rely on the SD card reading reliably
while the supply sags. The other sounds play with power present, and
streaming them keeps RAM free for the spindown.

**When it fits:** the spindown is loaded only if at least 32 KB of memory
is still free afterwards (`HEAP_RESERVE_BYTES`, a margin for everything
else). About 391 KB is free before it loads, so the largest spindown that
fits is about 359 KB. How long that is depends on the pack's sample rate
(mono 16-bit is 2 bytes per sample):

| Pack sample rate | Data per second | Longest spindown in RAM | Stream buffer cover |
|---|---|---|---|
| 16 kHz | 32 KB | ~11.2 s | ~1.0 s |
| 22.05 kHz | 44 KB | ~8.1 s | ~0.74 s |
| 32 kHz | 64 KB | ~5.6 s | ~0.51 s |
| 44.1 kHz | 88 KB | ~4.1 s | ~0.37 s |
| 48 kHz | 96 KB | ~3.7 s | ~0.34 s |

("Stream buffer cover" is how long each streamed sound can ride out a
slow SD read.) Every current pack is 16 kHz and fits; the largest,
`PB_MicroScience612` (11.0 s), leaves about 6 KB to spare (13 KB before
the modelled drive's code moved into RAM, v0.20.0). With
`EXPERIMENTAL_HDDSYNTHPRO_SUPPORT` on, `sequential.wav`'s 32 KB buffer means
it streams instead. The boot log says which happened:
`spindown in RAM (… ms)` or `spindown will stream from SD`.

**If it doesn't fit:** once running, the one-shot buffer is kept
pre-filled with the start of the spindown, so it still starts instantly on
power loss and the rest streams while it plays. One weak spot: during the
spinup and jingle that buffer is busy, so a power cut then has to fill it
first (a short SD read before the spindown starts). No current pack is
affected. `pio run -e mk5_stream_test` builds a variant that always
streams the spindown, to test this path.

**Memory overall:** the three 32 KB buffers (96 KB) and the rest of the
firmware permanently use about 125 KB of the 512 KB, leaving the ~391 KB
the spindown draws from. Features that add RAM shrink the space for big
spindowns.

## Power loss

When power fails the spindown plays from the supercap. Then the board waits
for power to come back in a **low-power state**: the audio core is stopped,
the clock drops from 150 to 48 MHz, and the LEDs, amp and OLED are off. That
stretches how long the supercap lasts, so short outages are ridden out, and
the board reboots normally when power returns.

## Power-loss log

A real power cut takes USB down with it, so the serial console can't see
what happens. From the moment power loss is detected, the power lines and
supercap readings are also written to `/powerlog.bin` on the SD card (raw
sector writes into a preallocated file, flushed every 250 ms, so a sudden
death can at worst lose the last chunk). After power returns, send `l` to
print it: the spindown at 100 ms resolution, then the supercap every 500 ms
until power returns or the board dies. Only the latest power loss is kept.
