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
| **The link on UART0, TX GPIO 2 and RX GPIO 1** (it was UART1 on J6's GPIO 24/25) | GPIO 24/25 stay the OLED's. GPIO 1 and 2 were free, and sit at the RP2354A's corner nearest J8; GPIO 3, the first choice for RX, couldn't get out between its neighbours' tracks. Firmware 0.26.0 uses the new pins; 0.25.0 is the last with the link on 5.3.0's J6. |
| **1 kΩ in series on the link's RX and TX (R43, R42)** | The Bay has the same at its end. With them on both boards, either one is protected whatever it's connected to (a USB-serial adapter, a board without them), and an unpowered board isn't fed through its pin's protection diodes by a powered one. At 115,200 baud they make no difference to the signal. |
| **5 V on J8 pin 1, always, from after the eFuse (VIN_PROT)** | So one supply can power both boards: the Bay takes pin 1 in through its own Schottky diode. Taken after the eFuse, a short in the cable trips the eFuse's 1.27 A limit instead of the PC's supply. In a power cut the supercap's chip (TPS61094) opens its bypass switch, so the Bay can't drain the supercap the spindown needs; powering the Bay from the supercap to finish a write isn't worth it (the PC loses its own cache at the same moment, and the supercap's 4.2 V boost would reach the Bay as about 3.9 V). |
| **47K pull-ups on the SD card's DAT1 and DAT2 (R44, R45)** | They were left floating. The SD specification asks for pull-ups on every data line, even the ones SPI mode doesn't use, so a card never sees a floating input. |
| **Card detect wired to GPIO 29**, using the RP2354A's internal pull-up | The socket's switch was unconnected, so the firmware could only find out a card was gone by failing to read it. With card detect it knows at once, and can tell "no card" from "card not answering". GPIO 29 is the free pin that could be routed to the socket (GPIO 7, 16, 23 and 26 are boxed in by their neighbours' tracks). A 47K pull-up (R46) is in the schematic but not fitted: there was no room for it beside the route, and the internal pull-up does the same job for a switch to ground (the RP2350's erratum E9 concerns pull-downs, not pull-ups). Firmware 0.26.0 enables it. |
| **SD stays on SPI** (no 4-bit SDIO) | SPI at 25 MHz gives about 2 MB/s; two drives playing at once need at most about 0.6 MB/s (three voices each, at 48 kHz) and today's 16 kHz packs about 0.2 MB/s, with a one-second buffer per voice. SDIO would mean moving the RGB LED's pins and new firmware, for speed the synth can't use. |
| **ESD protection on USB (U10, USBLC6-2SC6)** across D+, D− and VBUS | The USB-C socket is a connector people plug things into, often from a motherboard header on a long cable, and D+/D− went straight to the RP2354A through 27 Ω. A USBLC6 clamps static before it reaches the chip; the IDE Synth Bay has the same part. |
| **The unused external flash removed** (U3, a W25Q32 footprint, and its options R6, R7, R9, with their tracks) | It was never fitted: the RP2354A has its 2 MB of flash inside the package. The empty footprint left the QSPI lines running to nothing (stubs on the fastest lines on the board) and took space that J8, U10 and the pull-ups now use. QSPI_SS keeps its path to R14 and the BOOTSEL button. |
| **The RGB LED's red, green and blue lines re-routed** | They crossed the space J8 now uses. They are slow PWM lines, so the longer path makes no difference. |
| **Ground jumpers on the top layer** | The new back-layer tracks fenced off small patches of the ground pour (the only ground plane, on the back), cutting C22's ground and J8's off; short top-layer tracks tie them back to the main pour. |
| **JLC placement offsets on U10 and U7** (`FT Rotation Offset`, `FT Position Offset`) | JLC's footprints for the USBLC6 (C7519) and the JST PH (C131337) are turned (and for the JST, centred) differently from KiCad's, as measured against JLC's own footprint data. Without them the CPL would place U10 a quarter-turn out and U7 1 mm off. |
| **R31 = 24K in the schematic** | The schematic said 22K, but the boards were built with 24K (the board file and the 5.3.0 BOM). Checked against TI's datasheet, the built value is right: 3.32 V from the TPS63020 (see *Before ordering*). |
| **R36 = 120K (C25750): the eFuse's limit raised from 1.16 A to 1.27 A** | The 5.3.0 boards were built with 110K (1.16 A). With Pimoroni's 4 Ω speaker at full volume a full-scale sample draws up to about 0.75 A from 5 V (1.6 W at the amplifier's 6 dB gain), and at power-on the supercap charges at 250 mA at the same moment the spinup plays: about 1.07 A in all, with the RP2354A. 1.27 A leaves room. 120K is the part R34 already uses, so the BOM loses a line and an extended part. |
| **D4, an SS34 Schottky, in series with USB's VBUS** (the USB side is now net VIN_RAW) | USB-C's VBUS and the aux header H14 were one net, with nothing to stop one supply feeding the other: with the USB lead in a motherboard header and the aux lead in the PSU, two supplies were tied together through the board. Now USB can only feed in, and aux, which doesn't pass through a diode, takes over whenever it's there. The cost: on USB alone the board sees about 0.33 V less (about 4.7 V from a 5.0 V port). That's above the eFuse's 4.14 V cut-out and the TPS61094's roughly 4.3 V, but a weak port at USB's 4.75 V minimum leaves little margin. U10's VBUS clamp stays on the connector side. |
| **The eFuse's ENUV line rerouted**, and H14's label shortened to "Aux 5v in" | Both ran where D4 now sits. The ENUV line goes 0.7 mm further right, between D4 and C34's soft-start line. The label's last letters ran under D4's cathode pad, and C26 leaves no room to move it. |
| **C1, C6 and C26 (100 nF) and R24, R25 (22K) 0603 to 0402** | The same values, voltage rating and dielectric as the 0402 parts already on the board (C1525, C25768), so they join those BOM lines: two fewer lines and feeder set-ups. The tracks are unchanged; a short stub along each pad's axis joins them to the smaller pad. The two 10 µF 1206 capacitors (C2, C5) stay: the 0805 is a 25 V part that keeps less of its capacitance at 5 V, and C2 is bulk on VSYS, which is already thin. |
| **BOM fixes**: L2 was C167802 (1.5 µH, the TPS63020's L3 part) and is now C167804, the 2.2 µH the schematic shows; C34 (C1538), C35 (C52923) and D1 (C113952) had no part numbers | L2's footprint carried a second, stale "LCSC Part" field, which the Fabrication Toolkit reads first. TI names 1 µH or 2.2 µH for the TPS61094. The C167802 inductor the beta boards have is the same family, at 1.5 µH. |
| **A 10 kΩ pull-up (R47) on the HDD LED input's output, GP18** | The firmware used the RP2354A's internal pull-up, about 50 kΩ, so each falling edge from the optocoupler recovered slowly, and a high-impedance line inside a PC case picks up noise. 10 kΩ gives cleaner, faster edges for about 0.3 mA more while the HDD LED is lit. It sits next to the line's via, beside the +3V3 track; the firmware's own pull-up stays on, in parallel. |
| **The TPS63020's loop tightened**: C31 (22 µF) moved next to U6, L3 2.8 mm closer to it | In buck mode (5 V to 3.3 V) the loop that carries the switching current runs from the input capacitor through U6 to ground and back. C31, the nearest input capacitor, was about 9.5 mm away; now its VSYS pad sits on the trunk that feeds U6's VIN pins and its ground pad on U6's own ground strap and via, about 3 mm round. L3 sits beside the switch pins, on 0.6 mm traces at the pins and 1.0 mm to the inductor (0.3 mm before, twice as long). VINA's track moves 0.5 mm up to make room. Less ripple and less radiated noise next to the amplifier. |
| **VSYS and the speaker path widened** | VSYS had 0.2 and 0.3 mm stretches (25 mm in all), now 0.4 to 0.5 mm; FB1 and FB2 to the speaker connector go from 0.3 to 0.5 mm, and the amplifier's outputs to 0.4 to 0.5 mm except at its fine-pitch pins. A 4 Ω speaker draws twice the current of an 8 Ω one, and VSYS feeds the amplifier. The outputs still run on the back layer between the amplifier and the ferrites, through the ground plane, as in 5.3.0. |
| **The amplifier sheet's gain note corrected** | It had the GAIN_SLOT table upside down. GAIN_SLOT is tied to VDD, which is 6 dB, the quietest setting short of a 100k to VDD (datasheet Table 8). Tying it to GND would give 12 dB. |
| **Version 5.4.0** on the silkscreen | To tell these boards from the beta testers' 5.3.0. |

The ground pour was also refilled: 5.3.0 was saved with an out-of-date fill, which DRC showed as 156 clearance errors.

## Status (26 Nov 2026)

Routed: DRC finds no errors and no unconnected items, and the schematic and board agree (DRC's schematic parity check). Its warnings are the same 52 as before D4 and the 0402 changes. The three dangling stubs DRC lists were already in 5.3.0. ERC is as 5.3.0's apart from two library-mismatch warnings (the USBLC6 symbol is a flattened copy of KiCad's). The production files are regenerated.

Firmware 0.26.0 has the GPIO changes: the Synth Link on UART0, TX GPIO 2 and RX GPIO 1 (it was UART1 on GPIO 24/25, which stay the OLED's); card detect on GPIO 29, input with pull-up, low with a card in.

## Before ordering

- [x] **R31 and R36 validated** against TI's datasheets. R31 is as built; R36 is raised from the built 110K:

  | Part | What it sets | Value | Result | Before |
  |---|---|---|---|---|
  | R31 | The TPS63020's 3.3 V: V = 0.5 V × (1 + (R30 100K + R31) / R22 22K) | 24K (C25769) | 3.32 V | 22K: 3.27 V |
  | R36 | The TPS25921A's current limit: I = 10.73 mA × R(kΩ) − 18 mA | 120K (C25750) | 1.27 A | 110K, as built: 1.16 A |
- [x] **`production/` regenerated** after D4 and the 0402 changes: the BOM, CPL and designators by hand in the Fabrication Toolkit's format, the Gerbers, drills and IPC netlist with `kicad-cli` 10.0.8 using the Toolkit's settings (X1 attributes, routed oval holes, aux origin, mask subtracted from silk, zones refilled).
- [ ] **Re-run the Fabrication Toolkit on a computer with the Chalkduster font** (a macOS font). The "BETA TEST EDITION" text uses it, and it isn't embedded in the board; the Windows PC that made these Gerbers substituted Verdana Bold, so that text is in the wrong typeface in `F_Silkscreen`. Everything else matches what the Toolkit made.
- [ ] **Check JLC's placement preview** before paying, especially U10 (the USBLC6), U7 (the JST) and D4 (the SS34, cathode band towards U8): U10 and U7's offsets were measured, not yet seen on an order.

## Design files

| Folder | What's in it |
|---|---|
| [hardware/](../hardware) | The KiCad project: the schematic sheets (power, amplifier, SD card, encoder, RGB LED, OLED, reset) and the PCB |
| [hardware/production/](../hardware/production) | What a fab needs: Gerbers, BOM, positions and netlist |
| [hardware/tools/](../hardware/tools) | `make_logo.py`, which draws the logo footprint |

The board also uses footprints from two KiCad libraries outside this repository (`RP2350` and `easyeda2kicad`).

The hardware designs are CC BY-NC-SA 4.0: free for personal, non-commercial use and changes; commercial use needs permission ([licence](../README.md#licence-and-credits)).
