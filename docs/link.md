# The IDE Synth Bay link

How the IDE Synth hears exactly what an [IDE Synth Bay](https://github.com/MaverickUK/IDESynthBay) drive is doing, and sends it the timing of the drive it plays. Back to the [README](../README.md).

## How it works

[IDE Synth Bay](https://github.com/MaverickUK/IDESynthBay) emulates an IDE
hard disk, so it knows exactly what the drive is doing, not just when its
activity LED is lit. With `"EXPERIMENTAL_HDDSYNTHPRO_SUPPORT": true` the
IDE Synth listens for it on header **J8, the Synth Link** (board 5.4.0). A
straight 4-way cable connects J8 to the Bay's J3, and the OLED on J6 can stay
on:

| J8 pin | Signal | Connect to |
|---|---|---|
| 1 | 5 V, from after the eFuse | IDE Synth Bay's J3 pin 1: one supply can run both boards |
| 2 | GND | IDE Synth Bay GND |
| 3 | GP1, UART0 RX, through 1 kΩ (R43) | IDE Synth Bay's link TX |
| 4 | GP2, UART0 TX, through 1 kΩ (R42) | IDE Synth Bay's link RX, for its `seek_timing = synth` |

On the beta testers' 5.3.0 boards the link shared J6 with the OLED (pin 3
GP25 in, pin 4 GP24 out, OLED off): firmware 0.25.0 is the last for that.

It's a one-way UART at 115200 baud, 8N1, carrying lines like
`$HDA,1,1,S,R*4C` (busy, sequential, reading); the protocol is in
the IDE Synth Bay's [docs/activity-link.md](https://github.com/MaverickUK/IDESynthBay/blob/main/docs/activity-link.md). While valid lines arrive:

- the link's busy flag drives the access sound instead of the activity
  input (with the same `ACCESS_HOLD_TIME_MS` release);
- during **sequential** transfers (e.g. a large file copy) the pack's
  `sequential.wav` plays instead of `access.wav`, and the activity LED turns
  `SEQUENTIAL_LED_COLOUR` (orange by default). A pack without
  `sequential.wav` plays `access.wav` throughout.

`sequential.wav` is optional and follows the same rules as `access.wav`
(the same format and sample rate as the pack's other files, a seamless
loop). After a second without a valid line the link counts as lost and the
activity input takes over again; the log says `[link] up` and `[link] lost`.
The `s` stats include the link's state and counts of valid and rejected
lines.

**Modelled drives (protocol version 2, v0.21.0):** with a `drive.json`
pack, IDE Synth Bay can also send each command's target,
`$HDE,2,<pos>,<op>,<sectors>` (`pos` is the LBA as a fraction of the disk,
0-65535). While they arrive, the modelled head goes where the computer is
really reading and writing, instead of the virtual workload: another sector
on the same track doesn't move it, a few tracks away it ticks, further it
seeks. Back the other way, on pin 4 (the UART's other direction), the synth sends IDE Synth Bay the
playing drive's timing every 2 s and on each pack change,
`$HDM,2,<V|S>,<rpm>,...` (or `$HDM,2,-` for a recorded pack), so
IDE Synth Bay's authentic timing can hold each command for as long as that
drive would take (`src/drive_timing.h`; the IDE Synth Bay's
[head position brief](https://github.com/MaverickUK/IDESynthBay/blob/main/docs/hddsynth-head-position-brief.md)). The `s` stats show `heads=` (how
many targets have arrived) and `sent=` (the `$HDM` replies).

**SynthMinder (v0.25.0):** the companion app's queries and commands
(`$HDQ`, `$HDC`; see [the protocol](companion.md#protocol)) are also answered when they
arrive on the link, and the replies go back on pin 4. The IDE Synth Bay
relays them from [SynthMinder](https://github.com/MaverickUK/SynthMinder),
a DOS program that shows and changes the volume, balance and pack from the
PC the Bay is fitted to. Both wires are needed. The `s` stats show
`commands=` (how many arrived), `sent=` and `skipped=` (sentences that didn't
fit the 2 KB transmit queue).

To try it without an IDE Synth Bay: with `SIMULATION_MODE` on, one simulated
burst in three becomes a longer sequential spell. Or connect a 3.3 V
USB-serial adapter's TX to J8 pin 3 (and GND to pin 2) and paste lines such
as `$HDA,1,1,S,R*4C` (busy, sequential) and `$HDA,1,0,I,-*28` (idle).
