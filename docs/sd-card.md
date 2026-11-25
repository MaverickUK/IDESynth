# The SD card

What goes on the card: sample packs, `pack.json` and `settings.json`. Back to the [README](../README.md).

## What goes on the card

```
/settings.json            optional, see below
/jingle.wav               optional, played once on first boot
/samples/<pack>/spinup.wav
/samples/<pack>/idle.wav
/samples/<pack>/access.wav
/samples/<pack>/spindown.wav
/samples/<pack>/pack.json optional, see below
/samples/<pack>/sequential.wav  optional, see link.md
/samples/<pack>/drive.json      a modelled drive instead of the WAVs, see modelled-drives.md
/powerlog.bin             created by the firmware (power-loss log)
/state.bin                created by the firmware (saved volume/balance)
```

The layout and `settings.json` keys are the same as the CircuitPython
firmware, so existing cards keep working. A pack is any folder in
`/samples` (name up to 63 characters); packs are used in alphabetical order.

**WAV files:** mono, 16-bit PCM at **16000, 22050, 32000, 44100 or 48000
Hz**. All of a pack's WAVs must use the same rate (the audio output
switches to it when the pack loads); a pack that mixes rates is reported as
broken, and the log names the mismatched files. The jingle may use any of
those rates. Higher rates sound crisper but cost RAM and SD bandwidth: the
spindown that fits in RAM gets shorter (from ~11 s at 16 kHz to ~4 s at 48
kHz; see the table under [Where each sound plays from](architecture.md#where-each-sound-plays-from)).
22.05 or 32 kHz gets most of the benefit through a small speaker. Any
length otherwise: everything else streams from the card.
Metadata that editors add before the audio (`bext`, `LIST`, markers) is
fine, as long as the audio starts within the first 4 KB of the file. A file
that breaks these rules is reported as a broken pack (4 low beeps).

## pack.json (optional, per pack)

A pack can carry its own settings in `/samples/<pack>/pack.json`. Every key
is optional:

```json
{
    "NAME": "IBM Ultrastar 36LZX",
    "AUTHOR": "PB",
    "GAIN": 1.4,
    "ACTIVITY_LED_COLOUR": "#FF8800",
    "BALANCE_DEFAULT": 0.3
}
```

| Key | Default | What it does |
|---|---|---|
| `NAME` | the folder name | Shown on the OLED's title bar. |
| `AUTHOR` | *(none)* | Credited in the boot log. |
| `GAIN` | `1.0` | Loudness trim for this pack's sounds (spinup, idle, access, spindown), 0.0 to 2.0, to even out packs recorded at different levels. Doesn't affect beeps or the jingle. |
| `ACTIVITY_LED_COLOUR` | settings.json's | This pack's activity LED colour (`"#RRGGBB"` or `[r, g, b]`). Demo mode's random colour still wins. |
| `BALANCE_DEFAULT` | settings.json's / 0.5 | This pack's starting balance, since packs differ in how loud idle is against access. A `BALANCE_DEFAULT` in settings.json overrides it, and so does a saved balance at boot (`SAVE_VOLUME_BALANCE`). On a pack change, the new pack's value applies. |

## settings.json

Every key is optional; anything missing (or of the wrong type) keeps its
default. For example:

```json
{
    "SAMPLE_PACK": "Mark1",
    "VOLUME_DEFAULT": 0.9,
    "BALANCE_DEFAULT": 0.2,
    "ACCESS_HOLD_TIME_MS": 500,
    "ACTIVITY_LED_COLOUR": "#00FF00"
}
```

| Key | Default | What it does |
|---|---|---|
| `SAMPLE_PACK` | *(none)* | Pack to play (a folder name in `/samples`). Wins over the pack chosen with the action button. If it doesn't exist, the firmware beeps 5 times and carries on with another pack. |
| `RANDOM_SAMPLE_PACK` | `false` | Pick a random pack at every boot, never the same one twice running. Overrides `SAMPLE_PACK`. |
| `VOLUME_DEFAULT` | `0.5` | Starting volume, 0.0 to 1.0. If set, it is used at every boot, even over a saved volume. |
| `BALANCE_DEFAULT` | `0.5` | Starting idle/access mix: 0.0 = idle only, 1.0 = access only. Idle plays at volume × (1 − balance), access at volume × balance. The spinup and spindown play at the idle level, as in the CircuitPython firmware, so the hand-overs never change volume (and they're silent at 1.0). If set, it is used at every boot, even over a saved balance. |
| `SAVE_VOLUME_BALANCE` | `false` | Remember the volume and balance when you change them (2 s after the last change), and use them at the next boot unless `VOLUME_DEFAULT`/`BALANCE_DEFAULT` is set. Saved on the SD card in `/state.bin`, so they go with the card. A factory reset clears them. *(New.)* |
| `PLAY_SPINUP` | `true` | Play the spinup at boot. |
| `PLAY_IDLE` | `true` | Play the idle loop. |
| `PLAY_SPINDOWN` | `true` | Play the spindown on power loss. |
| `ACCESS_HOLD_TIME_MS` | `100` | How long the access sound keeps playing after the HDD activity signal stops. |
| `SIMULATION_MODE` | `false` | Fake random HDD activity instead of reading the activity input. |
| `POWER_DETECTION` | `true` | Watch the eFuse for power loss. Set `false` to run from USB with no power-loss detection. |
| `ACTIVITY_LED_ENABLED` | `true` | Light the RGB LED on HDD activity. |
| `ACTIVITY_LED_COLOUR` | `"#00FF00"` | Activity LED colour, as `"#RRGGBB"` or `[r, g, b]` (0-255 each). |
| `RGB_LED_BRIGHTNESS` | `0.5` | Overall RGB LED brightness, 0.0 to 1.0 (applies to beeps and the jingle show too). |
| `ALWAYS_PLAY_JINGLE` | `false` | Play `/jingle.wav` at every boot, not just the first. *(New: a code constant in CircuitPython.)* |
| `DEMO_MODE` | `false` | Demo mode, see below. *(New.)* |
| `STANDBY_MINUTES` | `0` (off) | Spin down after this many minutes without HDD activity, like a real drive's power management: the spindown plays and the board goes quiet. The next HDD access spins it up again (spinup, then idle/access). A short press of the action button changes pack and spins up. Ignored in demo mode. *(New.)* |
| `OLED_ENABLED` | `false` | Use an SSD1306 128x64 I2C OLED on header J6, see [OLED display](controls.md#oled-display). *(New.)* |
| `OLED_MODE` | `"activity"` | The OLED's main screen: `"activity"`, `"supercap"` or `"debug"`. *(New.)* |
| `OLED_SAMPLE_MS` | `1000` | Time covered by each column of the activity and supercap graphs (minimum 50). *(New.)* |
| `EXPERIMENTAL_HDDSYNTHPRO_SUPPORT` | `false` | Listen for the activity link from an IDE Synth Bay on J6 and play `sequential.wav` during sequential transfers, see [IDE Synth Bay activity link](link.md). Turns the OLED off (same header). *(New, experimental.)* |
| `SEQUENTIAL_LED_COLOUR` | `"#FF1800"` (orange) | Activity LED colour during sequential transfers, with `EXPERIMENTAL_HDDSYNTHPRO_SUPPORT` on (a debugging aid). Same format as `ACTIVITY_LED_COLOUR`. *(New.)* |

**Demo mode:** each pack spins up, plays idle/access with simulated HDD
activity for 60 seconds, plays its spindown, and hands over to the next
pack, looping forever. Each pack gets a random activity LED colour. A short
press of the action button skips to the next pack. Demo pack changes are
not saved, so after a power cut it starts again from the usual pack.
