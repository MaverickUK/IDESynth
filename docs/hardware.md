# The hardware

The IDE Synth board, what's on it, and where its design files are. Back to the [README](../README.md).

The board is the HDD Synth's fifth prototype (MK5), the one with the beta testers, at version 5.4.0: 5.3.0, the beta testers' board, with the changes below. The KiCad files keep the old name (`HDD Synth Prototype MK5.kicad_*`).

## On the board

- **An RP2354A**, a Raspberry Pi RP2350 with its flash inside the chip: one core plays the sound, the other runs everything else ([how it works](architecture.md)).
- **USB-C** with ESD protection, for power, flashing and the [companion app](companion.md).
- **An I2S amplifier** driving a speaker, on a JST PH 2-pin connector (U7), to suit [Pimoroni's mini speaker](https://shop.pimoroni.com/products/mini-speaker-4-3w-with-jst-ph-connector) (4 Ω, 3 W).
- **A microSD card reader** for the sample packs and settings ([the SD card](sd-card.md)).
- **A rotary encoder and an action button** for volume, balance and the sample pack ([controls](controls.md)).
- **An RGB LED** for activity, beeps and errors, and an output for your case's own HDD LED (LED out, H2).
- **A supercapacitor and an eFuse**, so the spindown still plays when the PC's power goes.
- **Header J6** for an optional OLED screen ([controls](controls.md#oled-display)), and **J8, the Synth Link**, for an [IDE Synth Bay](link.md).
- **The HDD LED input** (LED in, H3), which takes the activity signal from the motherboard's HDD LED header through an optocoupler.

## Connecting the LED headers

Both are marked + and − on the board. Pin 1, the square pad, is + on each:

| Header | + (pin 1) | − (pin 2) |
|---|---|---|
| LED in (H3) | The motherboard's HDD LED + (the optocoupler's anode) | The motherboard's HDD LED − |
| LED out (H2) | Your case's HDD LED + (through R1 on the board) | Your case's HDD LED − (ground) |

The speaker's + is marked by pin 2 of U7 (the amplifier's OUTP).

## Changes from 5.3.0

Each change, and why it was made. 5.3.0 is the board the beta testers have.

| Change | Why |
|---|---|
| **+ and − marks on the LED in (H3) and LED out (H2) headers** | The beta testers asked for them. The optocoupler on LED in only lights one way round, so a reversed lead just leaves the drive silent with no clue why; LED out drives the case's LED the same way. Pin 1 (square pad) is + on both. |
| **The speaker on a JST PH 2-pin connector (U7, JST B2B-PH-K-S, LCSC C131337)**, in place of the 3.5 mm screw terminal (KF350) | So [Pimoroni's mini speaker](https://shop.pimoroni.com/products/mini-speaker-4-3w-with-jst-ph-connector) (4 Ω, 3 W), which comes with a JST PH lead, plugs straight in: no bare wires to strip and clamp, and the plug is keyed. It's the same part the FDD Synth Duo's rev C uses for the same speaker. + (the amplifier's OUTP) is marked by pin 2. |
| **The IDE Synth logo** on the silkscreen, in place of the HDD Synth's | The project's new name: it now sounds like hard drives and optical drives alike. `tools/make_logo.py` draws it from `media/IDESynthLogo.png`. |
| **The Synth Link header (J8)**, pinned 1 5V, 2 GND, 3 RX, 4 TX, by the SD card | So the IDE Synth and an [IDE Synth Bay](https://github.com/MaverickUK/IDESynthBay) connect with a straight 4-way cable: the pinout matches the Bay's J3. Before, the link shared J6 with the OLED, so a synth could have the screen or the link, not both. |
| **The link on UART0, TX GPIO 2 and RX GPIO 1** (it was UART1 on J6's GPIO 24/25) | GPIO 24/25 stay the OLED's. GPIO 1 and 2 were free, and sit at the RP2354A's corner nearest J8; GPIO 3, the first choice for RX, couldn't get out between its neighbours' tracks. The firmware needs the new pins. |
| **1 kΩ in series on the link's RX and TX (R43, R42)** | The Bay has the same at its end. With them on both boards, either one is protected whatever it's connected to (a USB-serial adapter, a board without them), and an unpowered board isn't fed through its pin's protection diodes by a powered one. At 115,200 baud they make no difference to the signal. |
| **5 V on J8 pin 1, always, from after the eFuse (VIN_PROT)** | So one supply can power both boards: the Bay takes pin 1 in through its own Schottky diode. Taken after the eFuse, a short in the cable trips the eFuse's 1.16 A limit instead of the PC's supply. In a power cut the supercap's chip (TPS61094) opens its bypass switch, so the Bay can't drain the supercap the spindown needs; powering the Bay from the supercap to finish a write isn't worth it (the PC loses its own cache at the same moment, and the supercap's 4.2 V boost would reach the Bay as about 3.9 V). |
| **47K pull-ups on the SD card's DAT1 and DAT2 (R44, R45)** | They were left floating. The SD specification asks for pull-ups on every data line, even the ones SPI mode doesn't use, so a card never sees a floating input. |
| **Card detect wired to GPIO 29**, using the RP2354A's internal pull-up | The socket's switch was unconnected, so the firmware could only find out a card was gone by failing to read it. With card detect it knows at once, and can tell "no card" from "card not answering". GPIO 29 is the free pin that could be routed to the socket (GPIO 7, 16, 23 and 26 are boxed in by their neighbours' tracks). A 47K pull-up (R46) is in the schematic but not fitted: there was no room for it beside the route, and the internal pull-up does the same job for a switch to ground (the RP2350's erratum E9 concerns pull-downs, not pull-ups). The firmware must enable it. |
| **SD stays on SPI** (no 4-bit SDIO) | SPI at 25 MHz gives about 2 MB/s; two drives playing at once need at most about 0.6 MB/s (three voices each, at 48 kHz) and today's 16 kHz packs about 0.2 MB/s, with a one-second buffer per voice. SDIO would mean moving the RGB LED's pins and new firmware, for speed the synth can't use. |
| **ESD protection on USB (U10, USBLC6-2SC6)** across D+, D− and VBUS | The USB-C socket is a connector people plug things into, often from a motherboard header on a long cable, and D+/D− went straight to the RP2354A through 27 Ω. A USBLC6 clamps static before it reaches the chip; the IDE Synth Bay has the same part. |
| **The unused external flash removed** (U3, a W25Q32 footprint, and its options R6, R7, R9, with their tracks) | It was never fitted: the RP2354A has its 2 MB of flash inside the package. The empty footprint left the QSPI lines running to nothing (stubs on the fastest lines on the board) and took space that J8, U10 and the pull-ups now use. QSPI_SS keeps its path to R14 and the BOOTSEL button. |
| **The RGB LED's red, green and blue lines re-routed** | They crossed the space J8 now uses. They are slow PWM lines, so the longer path makes no difference. |
| **Ground jumpers on the top layer** | The new back-layer tracks fenced off small patches of the ground pour (the only ground plane, on the back), cutting C22's ground and J8's off; short top-layer tracks tie them back to the main pour. |
| **JLC placement offsets on U10 and U7** (`FT Rotation Offset`, `FT Position Offset`) | JLC's footprints for the USBLC6 (C7519) and the JST PH (C131337) are turned (and for the JST, centred) differently from KiCad's, as measured against JLC's own footprint data. Without them the CPL would place U10 a quarter-turn out and U7 1 mm off. |
| **R31 = 24K and R36 = 110K in the schematic** | The schematic said 22K and 120K, but the boards were built with 24K and 110K (the board file and the 5.3.0 BOM). Checked against TI's datasheets, the built values are right: 3.32 V from the TPS63020 and a 1.16 A eFuse limit (see *Before ordering*). |
| **Version 5.4.0** on the silkscreen | To tell these boards from the beta testers' 5.3.0. |

The ground pour was also refilled: 5.3.0 was saved with an out-of-date fill, which DRC showed as 156 clearance errors.

## Status (25 Nov 2026)

Routed: DRC finds no errors and no unconnected items, and the schematic and board agree (DRC's schematic parity check). The three dangling stubs DRC lists were already in 5.3.0. ERC is as 5.3.0's apart from two library-mismatch warnings (the USBLC6 symbol is a flattened copy of KiCad's). The production files are regenerated.

GPIO changes the firmware needs: the Synth Link on UART0, TX GPIO 2 and RX GPIO 1 (it was UART1 on GPIO 24/25, which stay the OLED's); card detect on GPIO 29, input with pull-up, low with a card in.

## Before ordering

- [x] **R31 and R36 validated** against TI's datasheets, and the schematic set to the values on the board and in 5.3.0's BOM (the boards built):

  | Part | What it sets | Value | Result | The schematic had |
  |---|---|---|---|---|
  | R31 | The TPS63020's 3.3 V: V = 0.5 V × (1 + (R30 100K + R31) / R22 22K) | 24K (C25769) | 3.32 V | 22K: 3.27 V |
  | R36 | The TPS25921A's current limit: I = 10.73 mA × R(kΩ) − 18 mA | 110K (C2909311) | 1.16 A | 120K: 1.27 A |
- [x] **`production/` regenerated** for 5.4.0 with the JLC Fabrication Toolkit (auto-translate, zones refilled, DNP parts left out).
- [ ] **Check JLC's placement preview** before paying, especially U10 (the USBLC6) and U7 (the JST): their offsets were measured, not yet seen on an order.

## Design files

| Folder | What's in it |
|---|---|
| [hardware/](../hardware) | The KiCad project: the schematic sheets (power, amplifier, SD card, encoder, RGB LED, OLED, reset) and the PCB |
| [hardware/production/](../hardware/production) | What a fab needs: Gerbers, BOM, positions and netlist |
| [hardware/tools/](../hardware/tools) | `make_logo.py`, which draws the logo footprint |

The board also uses footprints from two KiCad libraries outside this repository (`RP2350` and `easyeda2kicad`).

The hardware designs are CC BY-NC-SA 4.0: free for personal, non-commercial use and changes; commercial use needs permission ([licence](../README.md#licence-and-credits)).
