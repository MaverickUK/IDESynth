# Companion app and protocol

Your computer's own disk activity over USB, and the serial protocol the app, the IDE Synth Bay and SynthMinder share. Back to the [README](../README.md).

## Companion app: your computer's disk activity over USB

Plug the IDE Synth into a Mac or PC with a USB cable and run the
[**HDD Synth Companion**](../firmware/companion/README.md), a tray (menu bar) app. It
sends the computer's own disk activity, so the IDE Synth needs no HDD LED
wiring. From its menu and settings window you can also choose the sample
pack and set the volume and balance. It's a Python app installed with one
`pipx` command, unsigned and needing no admin rights; see
[companion/README.md](../firmware/companion/README.md).

The app's activity is added to the activity input (and to the IDE Synth Bay
link): either one plays the access sound. Nothing needs turning on in
settings.json. Large file copies count as sequential transfers, which play
`sequential.wav` when `EXPERIMENTAL_HDDSYNTHPRO_SUPPORT` is on. Over USB the
board is powered by the computer, so a power-loss spindown happens when the
computer cuts USB power (shutdown, or sleep on some machines). Set
`POWER_DETECTION` to `false` if that isn't wanted.

## Protocol

The app talks over the board's USB serial console (115200 baud). Any line
starting with `$` is a protocol sentence; everything else is the normal
console, so the single-key commands still work from a terminal while the app
isn't running. Sentences use the same format as the IDE Synth Bay link:
`$<fields>*<checksum>`, where the checksum is two hex digits, the XOR of
every byte between `$` and `*`.

| Direction | Sentence | Meaning |
|---|---|---|
| app → board | `$HDA,1,<busy>,<class>,<op>` | Disk activity: busy `0`/`1`; class `I` idle, `S` sequential, `R` random; op `R`, `W` or `-`. Sent on every change and every 200 ms; after 1 s without one the board stops using it. |
| app → board | `$HDQ,1,STATUS` | Ask for `$HDS`. |
| app → board | `$HDQ,1,PACKS` | Ask for the pack list (`$HDP` for each pack). |
| app → board | `$HDQ,1,MODEL` | Ask for `$HDM`: the modelled drive's timing, as sent to an IDE Synth Bay (see [the IDE Synth Bay link](link.md)). |
| app → board | `$HDE,2,<pos>,<op>,<sectors>` | A command's target, as from an IDE Synth Bay: for testing modelled drives (the app itself can't see LBAs). |
| app → board | `$HDC,1,VOL,<0-100>` | Set the volume (saved like an encoder change). |
| app → board | `$HDC,1,BAL,<0-100>` | Set the balance. |
| app → board | `$HDC,1,PACK,<index>` | Switch to that pack (as the action button does, remembered). Only in RUN or STANDBY, and not in demo mode. |
| board → app | `$HDS,1,<firmware>,<state>,<packIndex>,<packCount>,<volume>,<balance>,<supercapMv>` | Status. Also sent unprompted when the pack, volume, balance or state changes (at most every 250 ms) while the app is connected. |
| board → app | `$HDP,1,<index>,<count>,<folder>,<name>,<kind>` | One pack: its folder and its pack.json `NAME` (or the folder), each up to 32 characters, with `,`, `*` and `$` replaced by `_`; and its kind, `R` (recorded: WAVs) or `M` (modelled: `drive.json`). The kind was added in v0.24.0; earlier firmware leaves it out. |
| board → app | `$HDK,1,<VOL\|BAL\|PACK>,<OK\|ERR>,<reason>` | Reply to a command; reasons are `busy`, `demo` and `range`. |
| board → app | `$HDM,2,<V\|S>,<rpm>,<cylinders>,<fullStroke ms x10>,<track ms x10>,<settleDamp x100>,<step ms x10>,<stepRamp x100>,<zoned>` | The modelled drive's timing (`$HDM,2,-` for a recorded pack). |

For example `$HDQ,1,STATUS*78` and `$HDC,1,VOL,55*07` can be pasted into a
serial terminal to try it.
