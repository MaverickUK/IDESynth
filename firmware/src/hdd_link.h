// The activity link from HDDSynthPro (EXPERIMENTAL_HDDSYNTHPRO_SUPPORT): a
// UART on the Synth Link header J8, pin 3 (GP1, UART0 RX) in and pin 4 (GP2,
// UART0 TX) out (board 5.4.0; it shared J6 with the OLED on 5.3.0). Core 0
// only; nothing here blocks for long. The
// sentences are parsed by link_parser.h.
#pragma once

#include "link_parser.h"

namespace hddlink {

void begin();       // start UART0 on GP1/GP2 (call once, only with the setting on)
void service();     // read whatever has arrived, send what's queued; call every loop() pass
bool enabled();     // begin() has been called
bool present();     // a valid sentence within the last second
LinkState state();  // the latest $HDA (meaningful while present())
const HeadFeed& heads();  // the latest $HDE, and whether they're still arriving
// A query or command ($HDQ, $HDC) that arrived on the link, oldest first:
// HDDSynthPro relays them from SynthMinder. Answer each with reply().
bool takeCommand(HostCommand& cmd);
// Send a sentence back to HDDSynthPro on J8 pin 4 (GP2, UART0 TX), the
// link's other direction: `body` is everything between '$' and '*'. send()
// is for the $HDM sent every 2 s: skipped if the queue is full. reply() is
// for answers, which HDDSynthPro counts: it waits up to 50 ms for room.
void send(const char* body);
void reply(const char* body);
void printStats();  // one line for the 's' output

} // namespace hddlink
