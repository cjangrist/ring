# FiKavi F3 ring: Bluetooth protocol and cross-platform client handoff

**Research date:** 1 November 2026. **Target:** FiKavi F3, Amazon ASIN **B0F9DZPJ9Y**, UPC **741365744597**, photographed FCC ID **2BPGR-F3**, IC label **34005-F3**. **Phone:** unrooted Samsung Galaxy Z Fold6; supplied screenshot shows **Android 17 / One UI 9.0**, build **CP2A.260605.016.F956U1UEU4EZIH**. This is one self-contained implementation handoff; the links are inline so a coding agent can check each claim against its source.

**Navigation:** Sections 1–2 identify the hardware and every documented button behavior; section 3 contains GATT, bytes, and commands; sections 4–5 cover desktop/Android APIs; sections 6–9 specify the decoder, capture plan, remaining ambiguities, and acceptance criteria.

## 0. Implementation verdict and evidence boundaries

**There is enough public evidence to implement and test a real F3 input decoder. A complete, verified specification of every physical click/hold and every firmware control is not available from the examined sources.** The strongest discovery is a public investigation of this same product listing with actual GATT discovery, a complete HID Report Map, and timestamped notification payloads. The capture project's [product link](https://a.co/d/02kHmFEA) resolves to a product page whose information table identifies **B0F9DZPJ9Y**, matching [the user's listing](https://www.amazon.com/dp/B0F9DZPJ9Y). The physical ring still needs a descriptor fingerprint and labeled button capture before that sample's behavior becomes a verified contract for this unit. [Investigation repository](https://github.com/JPHutchins/ble-page-turner-investigations).

The evidence identifies **Bluetooth Low Energy HID-over-GATT**, with **touchscreen gestures** and **consumer-control reports**. The captured descriptor declares **report ID 3, four payload bytes**, and **report ID 2, two payload bytes**. The F3 does not expose three independent physical-button states in those reports. A client must decode generated input, recognize completed gestures, and separately arrange any suppression or replacement of the operating system's normal response. [Frozen capture A](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T060407Z-eb800388708b.jsonl), [hardware-test report](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1#issuecomment-6205704870).

| Question | Best-supported answer | What remains to establish |
|---|---|---|
| What is O/T/C? | O is off; T supplies short-video/eBook functions; C supplies camera/eBook functions. | Whether this unit announces switch changes or supports a remote mode query. [Filed manual](https://fccid.io/2BPGR-F3/User-Manual/User-manual-8423991.pdf). |
| Can a host read the ring? | A public F3 sample was successfully read over BLE and through a Linux-based Kindle input stack. | The exact target OS backend, access permission, and descriptor on this unit. [Captured evidence](https://github.com/JPHutchins/ble-page-turner-investigations). |
| Can software change the firmware mapping or physical T/C mode? | No verified command was found. The captured HID descriptor has no Output/Feature reports. | Vendor service FAB0 is present but undocumented. Do not invent opcodes. [Capture B](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T061403Z-eb800388708b.jsonl). |
| Are all double clicks, triple clicks, and holds known? | Manufacturer diagrams document intended effects; the public raw datasets cover repeated single presses. | Measure exact packets, thresholds, repetition, and application effects for the remaining actions. [Manufacturer diagrams](https://fikavi.com/f3-shorts-scrolling/), [HIL limitations](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1#issuecomment-6205704870). |
| Is unrooted Android fully capable? | Foreground app input is a practical baseline. Android 17 also introduces native HID APIs. | Public reference versions 37.1/37.2 and conflicting ACCESS_HID permission documentation require a runtime probe on this Fold6. See the Android section. [HidManager](https://developer.android.com/reference/android/hardware/hid/HidManager), [HidDevice](https://developer.android.com/reference/android/hardware/hid/HidDevice). |

**Evidence vocabulary throughout:** “photographed” means visible in the supplied images; “manufacturer-documented” means an advertised instruction or specification; “captured” means observed in the linked public sample; “derived” means decoded/calculated from those bytes; “proposed” means an implementation or validation recommendation. No Bluetooth connection to CJ's ring or phone was made during this research. Source pages were fetched through **Jasa**, including full source documents and raw capture files. PDF diagrams and manufacturer images were also downloaded and visually inspected because text extraction omitted button annotations.

## 1. Exact identity, manufacturer, silicon, and public documentation

### 1.1 Product identity and the physical QR code

The supplied photographs directly show **Model F3**, **FCC ID 2BPGR-F3**, **IC 34005-F3**, three front buttons, and the three-position **O / T / C** switch. The QR code in the second photograph decodes to the exact URL [http://tsmartelectronic.com/f3-scrolling-remote-for-phone](http://tsmartelectronic.com/f3-scrolling-remote-for-phone). That live page provides the F3 guide and support links. This binds the Tsmart documentation to the actual photographed unit; it does not by itself establish Tsmart's legal relationship to FiKavi or HK JAJA. [Actual QR destination](http://tsmartelectronic.com/f3-scrolling-remote-for-phone), [linked guide](https://tsmartelectronic.com/f3-user-guide-for-product/).

| Item | Verified value and source |
|---|---|
| Retail brand/model | FiKavi / F3. [Amazon information table](https://www.amazon.com/dp/B0F9DZPJ9Y). |
| Retail identifiers | ASIN B0F9DZPJ9Y; UPC 741365744597. [Amazon](https://www.amazon.com/dp/B0F9DZPJ9Y). |
| FCC applicant, manufacturer, and factory as declared in the test report | **HK JAJA LIMITED**, **3/F, WORKINGTON TOWER, 78 BONHAM STRAND, SHEUNG WAN, HONG KONG**. The same company/address is entered for all three roles in report sections 2.1–2.3; this is a regulatory declaration, not independent verification of an assembly factory at that address. [RF report, p.6](https://fccid.io/2BPGR-F3/Test-Report/FCC-Part-15-247-BLE-RF-8423980.pdf). |
| FCC application/grant | 2BPGR-F3; original equipment; grant 27 June 2025. Grantee contact Peter Han; public contact info@hkjaja.com. [FCC filing mirror](https://fccid.io/2BPGR-F3). |
| Brand support | hi@fikavi.com. [FiKavi contact page](https://fikavi.com/contact/). |
| Support reached from the physical ring QR | info@tsmartelectronic.com; support form requests the purchased brand. [F3 support page](https://tsmartelectronic.com/f3-i-need-help/). |
| ISED/IC | **34005-F3 is confirmed from the user's label only.** An independently verified Canadian certification record was not recovered in this investigation; do not infer a second manufacturer from the number. |
| Public FCC engineering files | User manual, internal/external photos, antenna/RF reports are public. The index lists block diagram, schematic, and operational description as metadata-only. [Exhibit index](https://fccid.io/2BPGR-F3). |

The manufacturer source chain is stronger than an Amazon field alone: the matching FCC report explicitly names the manufacturer, and its internal photographs show the matching three-key PCB and switch. Similar-looking rings under other models, including JieLi-based JX-05 units, are not interchangeable protocol evidence for this WS8100 sample. [Internal photos](https://fccid.io/2BPGR-F3/Internal-Photos/Intermal-photos-8423977.pdf).

### 1.2 Hardware and radio facts

| Property | Supported information |
|---|---|
| Power | Rechargeable Li-ion polymer battery **3.7 V, 55 mAh, 0.204 Wh**; internal battery photo corroborates its rating. [RF report p.6](https://fccid.io/2BPGR-F3/Test-Report/FCC-Part-15-247-BLE-RF-8423980.pdf), [internal photos p.3](https://fccid.io/2BPGR-F3/Internal-Photos/Intermal-photos-8423977.pdf). |
| Physical product | Manufacturer leaflet: plastic body, **35 × 30 × 18 mm**, USB-C charging, nominal **10 m** wireless range, pairing name **F3**. USB-C data/HID functionality is not specified. [Filed leaflet](https://fccid.io/2BPGR-F3/User-Manual/User-manual-8423991.pdf). |
| Radio tested | **2402–2480 MHz**, **40 channels**, **2 MHz spacing**, **GFSK**, declared **LE 1M PHY / 1 Mbps**, maximum conducted power **−2.13 dBm**, internal antenna, declared gain **−0.85 dBi**, SISO. [RF report §2.5](https://fccid.io/2BPGR-F3/Test-Report/FCC-Part-15-247-BLE-RF-8423980.pdf). |
| Test dates | Sample received 24 April 2025; testing 25 April–16 May; report issued 12 June 2025; report **BTF250424R00101** by BTF Testing Lab. [RF report p.1](https://fccid.io/2BPGR-F3/Test-Report/FCC-Part-15-247-BLE-RF-8423980.pdf). |
| Silicon visibly fitted in the FCC sample | Chip marking **WS8100**, with **F5EQ4** suffix visible in the enlarged internal photograph. This is evidence about the filed sample, not a teardown of the user's unit. [Internal photos p.2](https://fccid.io/2BPGR-F3/Internal-Photos/Intermal-photos-8423977.pdf). |
| Silicon vendor / family | **Shenzhen Qianhai WiseSun Intelligence Technology Co., Ltd.** publishes the WS8100 BLE 5.0 SoC. Its ordering table lists WS8100F5EQ4 as 512 KB flash / 40 KB SRAM / QFN48. The datasheet also describes 32-bit RISC, 16/32 MHz clocks, UART, JTAG/cJTAG, and OTA capability. [WiseSun datasheet pp.1,11](https://www.wisesun.com/upload/attachment/202606/03/094250/WS8100_BLE5.0%E8%8A%AF%E7%89%87%E7%AE%80%E4%BB%8B-V1.8.pdf), [vendor product table](http://wisesun.com/product/7.html). |

**Do not conflate chip capability with F3 firmware capability.** WiseSun's BLE 5.0/OTA/UART descriptions do not identify the F3's implemented update protocol, firmware image format, exposed flash size, or usable debug pads. AT commands documented for a WS8100-M2 transparent serial module are not established F3 Bluetooth commands. The F3 RF report lists hardware/software versions as **N/A**. The report also has later 2M “worst case” text despite its LE 1M technical table; record that inconsistency instead of claiming verified LE 2M support. [WiseSun chip datasheet](https://www.wisesun.com/upload/attachment/202606/03/094250/WS8100_BLE5.0%E8%8A%AF%E7%89%87%E7%AE%80%E4%BB%8B-V1.8.pdf), [F3 RF report §§2.4–2.5,6.6.3,6.8.3](https://fccid.io/2BPGR-F3/Test-Report/FCC-Part-15-247-BLE-RF-8423980.pdf).

The retail listing specifies one supported device. Treat that as **one active host**, not proof of exactly one stored bond or any particular multipoint state machine. Exact bonding capacity, idle timeout, wake behavior, charging-time operation, and reset/pairing-clear combinations were not established. Manufacturer pairing instructions say power on, select **F3** in the host Bluetooth list, and wait for the flashing blue LED to turn off on connection. [Amazon](https://www.amazon.com/dp/B0F9DZPJ9Y), [FiKavi Android instructions](https://fikavi.com/f3-android-phones-tablets/).

## 2. Physical switch and complete manufacturer-documented button behavior

### 2.1 Label the buttons before programming

Use **U**, **M**, and **D** to mean the upper arrow-like button, middle square button, and lower arrow-like button **as drawn in the manufacturer's diagrams**. Photograph the ring in that orientation and record the USB-C port position. Do not define up/down from how a person happens to wear or rotate the ring: the public capture already contains a documented up/down labeling error. “Single”, “double”, “triple”, and “long” below are the manufacturer's terms; the timing thresholds remain unmeasured. [Manufacturer video diagram](https://fikavi.com/wp-content/uploads/2025/06/TIKTOK-VIDEO.jpg), [public capture correction](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1).

| Switch | Documented behavior | Programming implication |
|---|---|---|
| **O** | Off/power switch position. | No verified software wake or power-on command. |
| **T** | Short-video controls and eBook page turning. | Firmware emits mode-dependent input; app orientation/layout determines its visible effect. |
| **C** | Camera controls and eBook page turning. | Captured short presses produce horizontal swipes or alternating volume-key input. |

The O/T/C function mapping is shown in the [filed F3 leaflet](https://fccid.io/2BPGR-F3/User-Manual/User-manual-8423991.pdf) and the [guide linked by the ring's QR](https://tsmartelectronic.com/f3-user-guide-for-product/). **Portrait/landscape is a host viewing context, not an additional switch position or a verified firmware command.** Standard Bluetooth HID Boot/Report Protocol is another separate concept and must never be substituted for T/C.

### 2.2 T mode: short-video browsing

The table transcribes the intended effects in FiKavi's [short-video guide](https://fikavi.com/f3-shorts-scrolling/) and its [full button diagram](https://fikavi.com/wp-content/uploads/2025/06/TIKTOK-VIDEO.jpg). These are app-facing behaviors, not named Bluetooth opcodes.

| Viewing context | Button | Single press | Double press | Long press | Triple press |
|---|---|---|---|---|---|
| Portrait | U | Previous video | Leave profile / return to video | Volume up | Not documented for browsing |
| Portrait | M | Swipe left / open profile | Pause/play | See recording instructions below | See recording instructions below |
| Portrait | D | Next video | Like video | Volume down | Not documented for browsing |
| Landscape | U | Not specified for this context | Next video | Not specified for this context | Not specified |
| Landscape | M | Previous video | Not specified for this context | Not specified for this context | Not specified |
| Landscape | D | Not specified for this context | Not specified for this context | Not specified for this context | Not specified |

**“Not specified” does not mean “no packet.”** The physical action can still produce input that the particular app ignores or interprets differently. The manufacturer does not provide a packet-level landscape profile or say the device senses display rotation. Test both landscape rotations; foldable-display coordinate transforms must be captured, not guessed.

### 2.3 T mode: recording inside short-video apps

Manually open the recording screen first. The manufacturer's table assigns **M long press** to photo/video triggering and **M triple press** to camera flip for TikTok, YouTube, Instagram, and Facebook. It separately states that Snapchat supports photo capture but not remote video recording. It warns about device/app differences, gives Samsung S6 Lite/YouTube as an example, and says camera flipping during recording depends on the app. For zoom it instructs switching to C, adjusting zoom, then returning to T. [FiKavi recording instructions](https://fikavi.com/f3-shorts-scrolling/).

The manufacturer supplies these video references: [short-video browsing](https://www.youtube.com/watch?v=3ZSQPiG0mgU), [Reels recording](https://www.youtube.com/watch?v=-Rlq5GlewrQ). They are additional references linked by the source page; the button claims above are grounded in the fetched page and diagrams, not an assumed video transcript.

### 2.4 C mode: native phone camera

| Button | Single press | Double press | Triple press | Long press |
|---|---|---|---|---|
| U | Swipe left | Not documented | Not documented | Zoom in |
| M | Trigger photo/video | Flip camera | Flip camera on Pixel 6 series | Flip camera on Pixel 7/8/9 series |
| D | Swipe right | Not documented | Not documented | Zoom out |

Source: [FiKavi camera guide](https://fikavi.com/f3-phone-camera-remote/), specifically its [camera button diagram](https://fikavi.com/wp-content/uploads/2025/05/camera-remote-1024x514.jpg). The Pixel-specific mappings are not Samsung guarantees. The public F3 short-press capture shows C/M emitting alternating volume events, so shutter behavior can depend on the camera app's volume-key setting. Confirm actual Fold6 Camera settings and event traces before labeling that key “shutter” in software. [Captured C/M reports](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T061403Z-eb800388708b.jsonl).

### 2.5 eBooks: T/C and orientation

| Reading context | Mode | Previous page, as documented | Next page, as documented |
|---|---|---|---|
| Portrait | T | U double press | M single press |
| Portrait | C | U single press | D single press |
| Landscape | T | U single press | D single press |
| Landscape | C | No separate landscape mapping published on the inspected page | No separate landscape mapping published |

This uses FiKavi's newer [page-turner page](https://fikavi.com/f3-page-turner/), its [portrait diagram](https://fikavi.com/wp-content/uploads/2025/07/%E5%8A%9F%E8%83%BD.jpg), and [landscape diagram](https://fikavi.com/wp-content/uploads/2025/07/%E5%8A%9F%E8%83%BD2.jpg). **Source discrepancy:** the older FCC leaflet's C-mode next-page annotation points to the middle button; the newer portrait diagram points to the lower button. The later raw evidence also makes C/M a volume input. Use the newer diagram as intended usage guidance, and validate physical buttons on the actual reader. Do not silently copy the older drawing. [Older leaflet](https://fccid.io/2BPGR-F3/User-Manual/User-manual-8423991.pdf).

The manufacturer asks for **Kindle continuous scrolling off**, **Adobe Acrobat view set to Single page**, and **Wattpad Reading Mode set to Paging**. These are app settings, not ring firmware settings. Physical swipe direction and app “next/previous” are separate mappings; reading direction, rotation, and the app's own response can reverse the visible result. [FiKavi eBook setup](https://fikavi.com/f3-page-turner/).

### 2.6 Pairing and iOS instructions prevent a common model mix-up

For this F3, FiKavi's own iPhone/iPad page specifies **Settings → Accessibility → Zoom → On**, followed by the stated screen-unzoom gesture. Its Android page simply describes Bluetooth pairing. Do not substitute an unrelated scroller's AssistiveTouch tutorial or assume an Android AccessibilityService is necessary for stock ring operation. An AccessibilityService is relevant to a custom Android remapper, which is a different use case. [FiKavi iOS guide](https://fikavi.com/f3-iphone-ipad/), [FiKavi Android guide](https://fikavi.com/f3-android-phones-tablets/), [QR-linked landing page](http://tsmartelectronic.com/f3-scrolling-remote-for-phone).

## 3. Actual Bluetooth database, packet formats, and defined commands

### 3.1 The critical evidence and its limits

A public firsthand investigation of a FiKavi F3 contains two timestamped raw BLE JSONL captures from 2026-10-15, complete discovered GATT tables and HID descriptors, and a later separately reported hardware test on a Kindle. The raw captures are frozen here at repository commit `b21c12636439e1e705ad8c8e354253c0cae88980`: [capture A](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T060407Z-eb800388708b.jsonl), [capture B](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T061403Z-eb800388708b.jsonl), [hardware-test comment](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1#issuecomment-6205704870). These are device observations, not manufacturer firmware specifications. The sources identify FiKavi F3 and link the same ASIN B0F9DZPJ9Y, but do not establish CJ's exact hardware/firmware revision. Their author also discloses AI assistance; the useful evidence is the actual machine-readable captures and separately reported hardware traces.

**Important correction:** the old JSONL `step.button` labels reversed up/down in both modes. The later PR explicitly acknowledges and corrects that labeling mistake. Use the raw packet bytes for protocol work, and the corrected hardware table for tentative physical-button attribution. Do not silently copy the old step names into production. [Explicit correction, “What the F3 sends (observed)”](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1)

The old data show a Bluetooth Low Energy GATT HID device, not a three-key keyboard. Touchscreen reports carry synthetic gesture trajectories; a separate consumer collection carries at least C-center volume events. The independent hardware trace reports two Linux input nodes with one Bluetooth identity, `F3 Touchscreen` and `F3 Consumer Control`. Selecting the node with the most keys can miss both directional buttons. This behavior was reproduced in the upstream issue and hardware test. [Issue #89](https://github.com/zampierilucas/kindle-button-mapper-rs/issues/89), [hardware test](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1#issuecomment-6205704870)

**Do not extrapolate** this to Classic Bluetooth HID, SPP/RFCOMM, AVRCP, an app API, OTA, LED control, remote mode switching or remappable firmware. None of those is proved by the BLE traces. A mode switch can change generated input without exposing a readable mode variable.

### 3.2 Exact sample GATT database

The numbers in this table are **sample characteristic-value handles**, in decimal and hexadecimal. They are NOT universally assigned handles. Discover UUIDs and descriptors afresh. Source data: [capture A, first connected record](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T060407Z-eb800388708b.jsonl). Bluetooth names and standard UUID numbers are cross-checked against [Assigned Numbers](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Assigned_Numbers/out/en/index-en.html).

| Service | Value handle | Characteristic | Observed properties / value |
|---|---:|---|---|
| 1801 GATT | 3 / 0003 | 2A05 Service Changed | Indicate; CCCD at 4 |
| 1800 GAP | 7 / 0007 | 2A00 Device Name | Read; `46 33 00` = F3 plus NUL |
| 1800 GAP | 9 / 0009 | 2A01 Appearance | Read; `c1 03` = 03C1, keyboard appearance |
| 1800 GAP | 11 / 000B | 2A04 Preferred Connection Parameters | Read; `18 00 18 00 00 00 54 01` |
| 180A Device Information | 14 / 000E | 2A50 PnP ID | Read; `01 ac 05 20 02 10 01` |
| 1812 HID | 17 / 0011 | 2A4E Protocol Mode | Read, Write Without Response; `01` |
| 1812 HID | 19 / 0013 | 2A4D Report | Read, Notify; 2908 at 21 = `01 01`; CCCD20 |
| 1812 HID | 23 / 0017 | 2A4D Report | Read, Notify, Indicate; 2908 at 25 = `02 01`; CCCD24 |
| 1812 HID | 27 / 001B | 2A4D Report | Read, Notify, Indicate; 2908 at 29 = `03 01`; CCCD28 |
| 1812 HID | 31 / 001F | 2A4D Report | Read, Notify, Indicate; 2908 at 33 = `04 01`; CCCD32 |
| 1812 HID | 35 / 0023 | 2A4D Report | Read, Notify, Indicate; 2908 at 37 = `05 01`; CCCD36 |
| 1812 HID | 39 / 0027 | 2A4B Report Map | Read; 141-byte descriptor below |
| 1812 HID | 41 / 0029 | 2A4A HID Information | Read; `01 01 00 00` |
| 1812 HID | 43 / 002B | 2A4C HID Control Point | Write Without Response |
| FAB0 unexplained service | 46 / 002E | FAB3 | Notify; CCCD47 |
| FAB0 unexplained service | 49 / 0031 | FAB1 | Write Without Response |
| FAB0 unexplained service | 51 / 0033 | FAB2 | Write Without Response |

Service handle ranges: 1801=1–4; 1800=5–11; 180A=12–14; 1812=15–43; FAB0=44–51. No 180F Battery Service, manufacturer/model/serial strings, firmware revision string, Output report or Feature report appears in this sample table. Reports 1, 4, 5 are advertised but have no definitions in the captured Report Map; the observed notifications are IDs 2 and 3. Several initial Report reads return four bytes even where ID2 notifications are two bytes. Keep these inconsistencies in diagnostics; do not fabricate a parser for the undefined IDs. [Capture B](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T061403Z-eb800388708b.jsonl)

Our numeric decoding of the PnP payload is source = 1, vendor = 05AC, product=0220, product version=0110 (1.1.0 under the DIS BCD convention). Source 1 means Bluetooth SIG vendor namespace; source 2 means USB-IF. In particular, **do not call this Apple hardware because USB vendor 05AC is familiar**: this payload selects another namespace. The fetched Assigned Numbers table associates SIG company code 05AC with GoerTek Dynaudio, but a self-reported identifier is not evidence that it manufactured this ring. Treat the label/FCC chain separately. [DIS v1.2 §3.9](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/DIS_v1.2/out/en/index-en.html), [Assigned Numbers](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Assigned_Numbers/out/en/index-en.html)

Appearance 03C1 says keyboard despite the actual touch/consumer descriptor. HID Information `01 01 00 00` means bcdHID=0101, country = 0, flags = 0, under HIDS; it is **not a Bluetooth version or a reliable firmware version**. The preferred-connection-parameter bytes numerically decode to interval min=max 24 units (30 ms), latency 0, supervision timeout 340 units (3.4 s), but do not infer actual negotiated timing from a preferred-parameters field. [HIDS §2.10](https://www.bluetooth.com/specifications/specs/html/?src=hids_v1-0_1765320236/HIDS_v1.0/out/en/index-en.html)

No public meaning for FAB0/FAB1/FAB2/FAB3 was established. Presence of writable characteristics is not a programming specification. Do not guess opcodes or send trial writes. Read-only discovery and notification logging are useful; unsupported firmware/OTA writes are outside a button-client implementation.

### 3.3 Descriptor and fingerprint

The following is the full 141-byte captured descriptor, a protocol-data fixture rather than software from the repository. Locally calculated SHA-256 over its binary bytes: `ce5d2e5408156a0fa29b3e7fc3546c1d19e0473c80ac1bf3dfef9b881937a927`. Both captures and the separately obtained HIL cache agree on these bytes. [Capture A](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T060407Z-eb800388708b.jsonl), [HIL descriptor](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1#issuecomment-6205704870)

```text
050d0904a1018503050d0922a102094215002501750195018102093281020947810209517505950115002505810205010930750c9501550e653326e80381020931750c9501550e653326e8038102c0c0050c0901a101850209300940098209a009b509b609e909ea09e209cd0a83010a96010a23020a24020a2d020a2e021900290115002501750195108102c0
```

A fingerprint mismatch is not a minor warning: fall back to descriptor-driven discovery and calibration. A matching hash supports applying the known packed layout, but does not prove identical mode behavior. Record the manufacturer's physical model/FCC markings, actual connected name/address identity, PnP bytes, map hash, service table, current switch position and exact source of a report (BLE versus OS HID).

#### Report ID 3: four-byte digitizer payload

The descriptor declares Usage Page0D, Touch Screen04, nested Finger22; Tip Switch42, In Range32, Confidence47, Contact Identifier51; then Generic Desktop X30/Y31. The touch values use unsigned 12-bit absolute coordinates and logical range0–1000. Our byte/bit decoding is directly derived from the captured descriptor and corroborated by the HIL report. [Descriptor and HIL](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1#issuecomment-6205704870)

| Field | Position within BLE payload `b0 b1 b2 b3` | Decode |
|---|---|---|
| Tip/contact down | b0 bit0 | `b0 & 1` |
| In range | b0 bit1 | `(b0 >> 1) & 1` |
| Confidence | b0 bit2 | `(b0 >> 2) & 1` |
| Contact identifier (declared range 0–5) | b0 bits3–7 | `b0 >> 3` |
| X | bit8–19 | `b1 \| ((b2 & 0x0f) << 8)` |
| Y | bit20–31 | `(b2 >> 4) \| (b3 << 4)` |

This layout has no physical-button number, hardware switch value, physical release time, press duration or repeat counter. These must be inferred from observed firmware-generated contacts, if distinguishable at all. The source only covers short presses, and explicitly says long press/repeat were not tested. Do not promise an arbitrary hold gesture from a fixed-duration swipe. [HIL “Not covered”](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1#issuecomment-6205704870)

**BLE versus OS framing:** the 4-byte BLE notification does **not** start with Report ID 3. Its characteristic's Report Reference provides that ID. A Linux numbered hidraw input report normally starts with `03` followed by the same four data bytes. An API may instead provide reportID separately. Never strip or prepend an ID just from payload length; document each backend's contract. [HOGP §4.8.1](https://www.bluetooth.com/specifications/specs/html/?src=HOGP_v1.0/out/en/index-en.html), [Linux hidraw read()](https://docs.kernel.org/hid/hidraw.html)

#### Report ID 2: two-byte consumer bitmap

Our descriptor decoding gives `mask = b0 | b1 << 8`, little-endian. The following are **declared bit meanings**, not proof the firmware ever emits every bit. Only Volume Increment/Decrement have been directly observed in the supplied short-press captures. [Capture B](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T061403Z-eb800388708b.jsonl)

| Bit | Mask (hex) | Consumer usage (hex) | Assigned meaning |
|---:|---:|---:|---|
| 0 | 0001 | 0030 | Power |
| 1 | 0002 | 0040 | Menu |
| 2 | 0004 | 0082 | Mode Step |
| 3 | 0008 | 00A0 | VCR Plus |
| 4 | 0010 | 00B5 | Scan Next Track |
| 5 | 0020 | 00B6 | Scan Previous Track |
| 6 | 0040 | 00E9 | Volume Increment |
| 7 | 0080 | 00EA | Volume Decrement |
| 8 | 0100 | 00E2 | Mute |
| 9 | 0200 | 00CD | Play/Pause |
| 10 | 0400 | 0183 | AL Consumer Control Configuration |
| 11 | 0800 | 0196 | AL Internet Browser |
| 12 | 1000 | 0223 | AC Home |
| 13 | 2000 | 0224 | AC Back |
| 14 | 4000 | 022D | AC Zoom In |
| 15 | 8000 | 022E | AC Zoom Out |

Assigned names verified in [USB-IF HID Usage Tables1.12, Consumer Page §15/table17](https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf). An INPUT Usage named Mode Step is an event *to the host*, not a command to change the ring's switch/mode. Likewise a declared Play/Pause usage does not establish that center press sends a media key.

C-center sample sequence: `40 00` → `00 00`; then `80 00` → `00 00`; then `40 00` → `00 00`. If mapping center to one application action, accept both volume bits as equivalent center presses, deduplicate within a press, and use release reports to return to idle. Binding only VolumeUp misses alternating presses. Do not assume the initial phase after reconnect. [Capture A](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T060407Z-eb800388708b.jsonl)

### 3.4 Exact observed short-press vectors, corrected physical mapping

These are analyzed raw packets from the captures with physical labels corrected by the later HIL. They are a candidate fixture for CJ's device, not a manufacturer guarantee. The old raw JSONL up/down labels are wrong. A raw sequence contains precontact/hover and lift-tail packets; count a completed contact once, not every packet as a press. [Raw capture B](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T061403Z-eb800388708b.jsonl), [label correction](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1), [HIL physical table](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1#issuecomment-6205704870)

| Corrected control | ID | Sequence of BLE payloads |
|---|---:|---|
| C-up; T-center | 3 | `00bc421f 02bc421f 07bc921f 0794421f 076c921f 0744421f 07c8901f 02c8401f 0064401f` |
| C-down | 3 | `002c411f 022c411f 072c911f 0754411f 077c911f 07a4411f 0720931f 0220431f 0084431f` |
| T-up | 3 | `00f4c126 07f4c126 07f4e124 07f40123 07f42121 07f4611d 07f40100 02f4611d 00f4611d` |
| T-down | 3 | `00f4e115 07f4e115 07f4c117 07f4a119 07f4811b 07f4611d 07f42121 07f4014b 00f42121` |
| C-center | 2 | `4000 0000`, alternating with `8000 0000` |

Our exact decoding of *in-contact* coordinates is:

- Left: X700→660→620→580→200; Y500/505 alternates.
- Right: X300→340→380→420→800; Y500/505 alternates.
- Up: X500 fixed; Y620→590→560→530→470→0.
- Down: X500 fixed; Y350→380→410→440→470→530→1200.

**Range anomaly:** raw BLE sends Y1200 although descriptor maximum is1000; the HIL evdev trace reports1000. Preserve raw1200 for forensic logs and do not discard the whole contact as invalid. OS-level clamping can explain differing backend coordinates. This is our comparison/inference from the two datasets, not a claim of a specific kernel path. [Raw capture B](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T061403Z-eb800388708b.jsonl), [HIL](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1#issuecomment-6205704870)

**Identifiability limitation:** C-up and T-center are byte-identical in these samples. If software starts without knowing the physical mode, that event alone cannot distinguish the two controls. The capture's switch-mode steps show no HID notifications, so do not assume switch changes announce themselves. Provide explicit mode selection/calibration in the client, or admit mode unknown. Other gestures may support a tentative inference, but there is no verified remote mode query.

Suggested classifier, as engineering design rather than source behavior: start a contact on tip0→1; keep initial/current coordinates for that contact ID; compute net displacement and maximum extent while tip1; finish once on tip1→0; ignore postrelease movement for the completed stroke; classify dominant signed axis after a threshold learned from the live unit; clear incomplete contacts on disconnect/timeout; preserve original packets for mismatches. Do not use in-range or confidence as separate buttons. Do not classify solely from first and final packet including lift tails, because those tail coordinates are no longer a pressed contact.

### 3.5 Standard Bluetooth operations that are actually defined

For SIG16-bit UUIDs, the full form is `0000XXXX-0000-1000-8000-00805f9b34fb`. UUID1812 identifies HID service; 2A4B the map; each 2A4D Report must be distinguished by its own readable 2908 descriptor: byte 0 report ID, byte 1 type 1=Input/2=Output/3=Feature. Read 2A4A for HID information. These fixed numbers identify kinds of attributes; handles and report layouts are discovered device data. [Assigned Numbers](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Assigned_Numbers/out/en/index-en.html), [HIDS §§2.5–2.6](https://www.bluetooth.com/specifications/specs/html/?src=hids_v1-0_1765320236/HIDS_v1.0/out/en/index-en.html)

| Operation | Target and exact value | What it does / does not do |
|---|---|---|
| Enable notifications | Report's 2902 CCCD: `01 00` | Subscribes this client to notifications; not a button command |
| Disable notifications | CCCD: `00 00` | Stops this subscription |
| Enable indications where supported | CCCD: `02 00` | Requests indications; not needed for known reports; Service Changed uses indications |
| Read current HID protocol | Read 2A4E | Sample returns 01 |
| Select Report Protocol | Write Without Response to 2A4E: `01` | HID report framing; **not T/C** |
| Select Boot Protocol | Write Without Response to 2A4E: `00` | Standard operation only if supported; sample has no Boot characteristics; do not use to obtain keyboard keys |
| Exit Suspend | Write Without Response to 2A4C: `01` | Announces host resume |
| Suspend | Write Without Response to 2A4C: `00` | Announces host suspend; not ring hardware power-off |
| Get report data | Read a discovered 2A4D | Current report state, not queued button history |
| Output/Feature write | Only discovered advertised Output/Feature report | No such report in captured F3; no verified F3 write payload exists |

CCCD semantics including per-client configuration, little two-byte flags and notification/indication bits are from [Core 5.4 Vol3 PartG §3.3.3.3](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host/generic-attribute-profile--gatt-.html). Protocol/Suspend values are from [HIDS §§2.4,2.11](https://www.bluetooth.com/specifications/specs/html/?src=hids_v1-0_1765320236/HIDS_v1.0/out/en/index-en.html). Read/subscribe/discover the report references, and the BLE/USB reportID translation behavior, are from [HOGP §§4.5–4.8.1](https://www.bluetooth.com/specifications/specs/html/?src=HOGP_v1.0/out/en/index-en.html).

Modern HIDS 1.1 adds optional Shorter Connection Interval features. That is **not evidence this 2025-market F3 supports them**, and those “modes” are unrelated to its O/T/C switch. Default to the observed HID1.0-style service until actual feature discovery proves more. [HIDS 1.1, SCI feature §3](https://www.bluetooth.com/specifications/specs/html/?src=hids_v1-1_1777413158/HIDS_v1.1/out/en/index-en.html)

#### Proposed direct BLE host startup

1. Identify the actual ring with an interactive device selection and physical button test; never hardcode the sample MAC.
2. Discover/connect, follow the OS-supported pairing/bonding flow, then discover every service/characteristic/descriptor. HOGP requires bonding/encrypted HID access; the actual negotiated policy remains hardware evidence to collect.
3. Read the full Report Map using long-read support where necessary; hash it. Read every 2908 and build `(service-instance,reportID,type) → characteristic`; duplicate UUIDs are expected.
4. Log unknown characteristics without writing them. Subscribe each input report supported by the descriptor; if exploring anomalous extra IDs1/4/5, retain their raw notifications as unknowns.
5. If a valid ProtocolMode value is Boot, switch to Report 01 using WWR. The sample is already01. Exit Suspend 01 is a known standard command.
6. Route Report 2 to its consumer bitfield parser and Report 3 to its packed contact parser only after matching the descriptor. Preserve other report IDs unparsed.
7. Register disconnect and ServiceChanged handling; rediscover if cached attribute identities become stale. Clean up a half-open contact on disconnect. The sample disconnected repeatedly during the probing sessions, so a quiet timeout is not evidence “no button command exists.”
8. Separate “read input”, “suppress OS-native gesture”, and “send replacement action” capabilities per backend. Connecting with a BLE library does not automatically suppress the OS HID stack.

The published collector follows the same broad shape: pair, snapshot GATT, subscribe input-report references, issue ExitSuspend, and select Report only if Boot was read. It uses a Bumble HCI controller over `serial:COM3,1000000,rtscts`, not an ordinary Windows BLE API. It stores pairing keys only in memory and has permissive test-oriented pairing callbacks; do not copy its pairing policy into a production application without redesign. [Collector link.py](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/src/page_turner/link.py), [GATT mapping logic](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/src/page_turner/gatt.py)

### 3.6 ATT wire examples and capture coverage

#### Wire-format cross-check (ATT only)

These are synthesized ATT PDUs using the observed sample handles, not captured HCI packets. They exclude L2CAP/HCI headers. In a BLE client API, pass only the value bytes to the selected characteristic/descriptor; the OS constructs ATT. [Core 5.4 Vol3 PartF §§3.4.4.3–6,3.4.5.1–3,3.4.7.1](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host/attribute-protocol--att-.html)

| Purpose | Example ATT bytes |
|---|---|
| Read map, handle 0027 | `0a 27 00` |
| Read map continuation, offset 22 | `0c 27 00 16 00` |
| Subscribe consumer CCCD 0018 | `12 18 00 01 00` |
| Subscribe touch CCCD 001C | `12 1c 00 01 00` |
| Successful write-response | `13` |
| Set Report protocol | `52 11 00 01` |
| Exit Suspend | `52 2b 00 01` |
| Touch notification example | `1b 1b 00 07 bc 92 1f` |
| Consumer notification example | `1b 17 00 40 00` |

Read response opcode=`0b`; blob response=`0d`. WriteCommand52 has no acknowledgement/error response, so API send success does not prove semantic success. Common ATT errors:01 invalid handle,02 read prohibited,03 write prohibited,05 authentication,08 authorization,0F encryption. At MTU 23 a 141-byte map requires multiple reads; a 4-byte report fits. [ATT specification](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host/attribute-protocol--att-.html)

#### Coverage caveat

The two captures contain 237 notifications: 225 touch packets and 12 consumer packets, corresponding to 25 complete touch contacts and 6 C-center presses. Capture A loses all C/down attempts; capture B records only 1 of 3 requested T/down presses before disconnection. `count:3` means three individual short presses, not a triple-click gesture. Nine BLE packets include hover/precontact/release tails; the HIL's 5–7 active movement frames are not a contradiction. The records do not establish double/triple-click or hold behavior. These counts are our analysis of [capture A](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T060407Z-eb800388708b.jsonl) and [capture B](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T061403Z-eb800388708b.jsonl).

## 4. Linux, macOS, and Windows client paths

### 4.1 Keep the three layers distinct

The program can consume (1) Bluetooth GATT notifications, (2) HID input reports after the OS Bluetooth stack, or (3) translated OS input events. These are different interfaces. Linux hidraw exposes unparsed reports; evdev exposes translated timestamped input events. The HID report descriptor explains the report fields, so the discovery phase should preserve both the descriptor and raw report bytes, even if the eventual client uses evdev. [Linux hidraw](https://docs.kernel.org/hid/hidraw.html), [Linux input architecture](https://docs.kernel.org/input/input.html), [HID descriptor introduction](https://docs.kernel.org/hid/hidintro.html).

HIDAPI is a possible cross-platform implementation layer, but its available transport backends and OS restrictions matter. On Linux link the **hidraw** backend (`libhidapi-hidraw`); the libusb backend does not talk to Bluetooth peripherals. Windows uses hid.dll and macOS uses IOHIDManager. HIDAPI cannot manufacture access to an OS-reserved collection. [HIDAPI upstream README, About/backends](https://github.com/libusb/hidapi).

**F3-specific requirement:** the public sample emits complete synthetic touch gestures for its directional controls. A key-only listener is insufficient. A contact-down event alone cannot distinguish gestures whose difference is their X/Y trajectory. Validate this profile against the target ring, then listen to the actual touch and consumer collections. [F3 hardware evidence](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1#issuecomment-6205704870).

### 4.2 Linux: capture and implement first

#### Discovery and evidence capture

Use native Linux or a VM with an actual Bluetooth adapter passed through to Linux. Merely running a Linux userspace without access to the host's Bluetooth/input devices does not supply these interfaces. This is an architectural requirement of the interfaces, not a device-specific compatibility claim.

Run these inventory commands; retain their output in the case folder:

```bash
uname -a
bluetoothctl --version
bluetoothctl list
bluetoothctl devices
cat /proc/bus/input/devices
```

`bluetoothctl list` identifies controllers; `devices` identifies known peripherals. Confirm the ring by turning only it on/off and comparing discovery results; record observed address/address type rather than matching solely on the short name `F3`. `bluetoothctl info ACTUAL_RING_ADDRESS` retrieves the selected device information. BlueZ's CLI supports Classic and LE, with `scan le` available for LE discovery. [BlueZ bluetoothctl manual](https://github.com/bluez/bluez/blob/master/doc/bluetoothctl.rst).

For an already paired ring, capture the reconnect before doing the button matrix. Choose the observed controller, not an assumed `hci0`:

```bash
# Replace ACTUAL_CONTROLLER_INDEX with the selected adapter index, e.g. 0.
sudo btmon -i ACTUAL_CONTROLLER_INDEX -w f3-T.btsnoop
```

Leave that terminal capturing, reconnect or switch the ring on in T, run the labeled button sequence, then stop with Ctrl-C. Repeat to a separate file for C. Decode offline:

```bash
btmon -r f3-T.btsnoop > f3-T-btmon.txt
btmon -r f3-C.btsnoop > f3-C-btmon.txt
```

The `-i`, `-w`, and `-r` options select a controller, record btsnoop, and read btsnoop respectively. This records the Linux host's HCI monitor interface; it is not an over-the-air passive radio capture. [BlueZ btmon reference](https://github.com/bluez/bluez/wiki/btmon).

Once the ring's HID device is identified, preserve the kernel report descriptor from its actual sysfs device path. Do not copy an example device ID from a guide:

```bash
# Replace ACTUAL_HID_DEVICE with the observed basename under /sys/bus/hid/devices.
cat '/sys/bus/hid/devices/ACTUAL_HID_DEVICE/report_descriptor' > f3-T-report-descriptor.bin
hexdump -C f3-T-report-descriptor.bin > f3-T-report-descriptor.hex.txt
```

For raw input recording, `hid-recorder` from the Linux HID maintainers' hid-tools is documented by the kernel:

```bash
# Replace hidrawN with the ring's verified node; repeat for every ring HID node.
sudo hid-recorder /dev/hidrawN > f3-T-hidraw.txt
```

The kernel documentation explicitly shows the sysfs descriptor route and hid-recorder for collecting report sequences. [Linux HID descriptor/capture guide](https://docs.kernel.org/hid/hidintro.html).

Capture interpreted events from each associated event node as a second view:

```bash
# First enumerate and select the ring's nodes from evtest's device list.
sudo evtest
# Then record the actual selected ring event node.
sudo evtest /dev/input/eventN > f3-T-evdev.txt
```

`evtest` is the kernel documentation's suggested input-event testing utility. Its events include type, code, value, and timestamps; EV_KEY values 0/1/2 mean release/press/repeat. Preserve EV_ABS and EV_SYN frames as well as EV_KEY. [Linux input event interface](https://docs.kernel.org/input/input.html). A practical capture should start all required node loggers concurrently, since one physical ring can expose several collections; distinguish capture scheduling from ring functionality.

The examples above are command templates, not executed tests. `ACTUAL_HID_DEVICE`, `hidrawN`, `eventN`, and `ACTUAL_CONTROLLER_INDEX` must be replaced after identification. Package availability and permissions differ by distribution. Use a narrowly matched udev rule for the finished application; do not permanently grant arbitrary applications access to every input device. HIDAPI documents the need for suitable udev access for unprivileged clients. [HIDAPI upstream](https://github.com/libusb/hidapi).

#### Linux client contract

For raw reports, enumerate through libudev and use the actual `/dev/hidraw*` node. `HIDIOCGRDESCSIZE` followed by `HIDIOCGRDESC` obtains the descriptor; `HIDIOCGRAWINFO` gives bus/VID/PID; `HIDIOCGRAWNAME` and `HIDIOCGRAWPHYS` provide identifying strings. Blocking or nonblocking `read()` receives reports. Numbered reports include the report number as the first byte; unnumbered reads begin directly with report data. Write/feature-report API buffers have different framing conventions, so do not blindly reuse a raw BLE notification as a hidraw write buffer. [Linux hidraw API](https://docs.kernel.org/hid/hidraw.html).

For an application that only needs semantic actions, use libevdev over the ring's event nodes and maintain complete frame/contact state. Capture broad capabilities first; only then map observed usages/axes to actions. Emit one action per physical gesture, not one action per coordinate sample. Handling contact lifecycle, reset/reconnect, overflow resynchronization, and duplicate events are engineering requirements for the proposed client.

If native touchscreen/volume behavior must stop while remapping, `libevdev_grab(..., LIBEVDEV_GRAB)` uses `EVIOCGRAB` and prevents other input clients from receiving events from that event node. This is optional and materially changes desktop input behavior. Grab **only verified ring nodes**, release on shutdown, and reacquire after a new file descriptor on reconnect. It does not make arbitrary Bluetooth GATT services private or alter the ring's firmware. [libevdev grab documentation](https://www.freedesktop.org/software/libevdev/doc/latest/group__init.html).

To produce replacement desktop key/mouse events, use uinput, preferably through libevdev's uinput helpers. The kernel describes uinput as a userspace-created virtual input device and recommends libevdev as less error-prone than direct ioctl handling. The raw-ring reader and virtual-output device should have distinct identities to prevent feedback loops. [Linux uinput](https://docs.kernel.org/input/uinput.html).

#### Optional Linux GATT view

In an active `bluetoothctl` session:

```text
menu gatt
list-attributes ACTUAL_RING_ADDRESS
select-attribute ACTUAL_ATTRIBUTE_OBJECT_PATH
attribute-info
read
```

Select an **observed object path**, especially for repeated Report characteristic UUIDs; UUID alone may be ambiguous. The `read` command operates on the selected attribute. `notify on` requests notifications when the selected characteristic supports them; `notify off` ends that session. Do not substitute a guessed handle such as `0x0025`. [BlueZ GATT CLI manual](https://github.com/bluez/bluez/blob/master/doc/bluetoothctl-gatt.rst).

Programmatically, use `org.bluez.GattCharacteristic1.ReadValue`, `StartNotify`, `StopNotify`, and its `Value`/`PropertiesChanged` notifications. `WriteValue` accepts explicit write type `request`, `command`, or `reliable`; capability flags and errors must be honored. Notification sessions may be shared, and `AcquireNotify` can conflict with other users. The OS HID implementation may already be consuming the same device; prefer hidraw for ordinary HID reception and preserve any observed GATT access failure. [BlueZ GATT characteristic API](https://github.com/bluez/bluez/blob/master/doc/org.bluez.GattCharacteristic.rst), [BlueZ complete GATT API](https://bluez.readthedocs.io/en/latest/gatt-api/).

### 4.3 macOS: supported native HID APIs

#### Inventory and modern Swift client

Start with:

```bash
sw_vers
hidutil list
```

Record all entries belonging to the ring, including usage page/usage, registry ID, vendor/product IDs and transport. Apple explicitly warns that one product can have multiple HID entries representing different functions. Do not infer three physical buttons imply exactly one input collection. [Apple, Discovering HID devices from Terminal](https://developer.apple.com/documentation/corehid/discoveringhiddevicesfromterminal).

Apple now documents **CoreHID** as a public framework with macOS 15.0+ availability. It supports interaction with HID devices and virtual devices; the existence of CoreHID should not be overlooked in favor of an exclusively legacy recipe. [CoreHID overview](https://developer.apple.com/documentation/corehid).

For a new native Swift application: use `HIDDeviceManager.monitorNotifications(matchingCriteria:)`, instantiate `HIDDeviceClient` for every matching device reference, and verify `transport`, `product`, `primaryUsage`, and identifiers. Subscribe with `monitorNotifications(reportIDsToMonitor: [HIDReportID.allReports], elementsToMonitor: [])`; log `.inputReport(reportID, reportData, timestamp)` and removal notifications. This provides actual input reports; repeatedly polling a Get Report request is not a substitute for event reception. [Apple communicating with HID devices](https://developer.apple.com/documentation/corehid/communicatingwithhiddevices).

Save `HIDDeviceClient.descriptor`, `deviceUsages`, `elements`, vendor/product/version information, and report notifications. Supported get/set-report calls are `dispatchGetReportRequest(type:id:timeout:)` and `dispatchSetReportRequest(type:id:data:timeout:)`. Their existence is a host API capability, **not evidence that the F3 implements a writable mode setting**. Do not send speculative Feature or Output reports. [HIDDeviceClient API](https://developer.apple.com/documentation/corehid/hiddeviceclient).

`seizeDevice()` attempts exclusive client access. If successful only that client receives its notifications; it remains seized until that client is deinitialized, and there must be no outstanding calls when seizure is attempted. Test this on the target ring and selected collections before promising suppression of its normal UI effects. [CoreHID seizeDevice](https://developer.apple.com/documentation/corehid/hiddeviceclient/seizedevice()).

#### Existing C/C++ or HIDAPI client

Legacy IOHIDManager remains a documented option: create a manager, apply narrow matching, register input-report callbacks, schedule its run loop, and open it. `IOHIDManagerRegisterInputReportCallback` receives reports from enumerated devices. Match all actual ring functions rather than assuming keyboard usage. [IOHIDManager input-report callback](https://developer.apple.com/documentation/iokit/1438397-iohidmanagerregisterinputreportc). `IOHIDManagerOpen` accepts `kIOHIDOptionsTypeSeizeDevice` for an exclusive link; avoid using that with unfiltered matching. [IOHIDManagerOpen](https://developer.apple.com/documentation/iokit/1438369-iohidmanageropen).

User approval for input access matters. Apple's headers document `IOHIDCheckAccess(kIOHIDRequestTypeListenEvent)` and `IOHIDRequestAccess(kIOHIDRequestTypeListenEvent)` for IOHIDManager/IOHIDDevice reception. A client must not treat “enumeration succeeded but no reports arrived” as proof that the ring is silent before checking access. [Apple IOKitUser IOHIDLib.h](https://raw.githubusercontent.com/apple-oss-distributions/IOKitUser/main/hidsystem.subproj/IOHIDLib.h). The visible user setting is **System Settings → Privacy & Security → Input Monitoring**. [Apple Input Monitoring guide](https://support.apple.com/guide/mac-help/control-access-to-input-monitoring-on-mac-mchl4cedafb6/mac).

CoreBluetooth is not the recommended primary ring input path: the supported native HID frameworks already handle Bluetooth HID transport and report descriptors. **This research did not verify an authoritative current blanket statement that macOS CoreBluetooth hides all 0x1812 services. Do not claim that as settled fact.** Test any custom non-HID service separately and log actual discovery/read/write behavior; publishing a HID peripheral and connecting as a HID host are different roles, and an iOS peripheral-role error proves neither macOS host restriction nor F3 capability.

### 4.4 Windows: Win32 Raw Input first, with collection-specific limits

#### Read device-specific input

A conventional desktop client should enumerate `GetRawInputDeviceList`, query `GetRawInputDeviceInfo`, then register the ring's **observed top-level usages** using `RegisterRawInputDevices`. Receive `WM_INPUT`, fetch `GetRawInputData`, and filter by `RAWINPUTHEADER.hDevice`. `RIDEV_INPUTSINK` permits background receipt when a target window is supplied. Registration is by usage, so per-ring filtering still happens against the incoming device identity. [Microsoft Raw Input overview](https://learn.microsoft.com/en-us/windows/win32/inputdev/about-raw-input).

Candidate usage pairs are generic mouse `(0x01,0x02)`, keyboard `(0x01,0x06)`, consumer control `(0x0C,0x01)`, or digitizer touchscreen `(0x0D,0x04)`, but the descriptor decides which actually exist. Do not register only keyboard and conclude that the ring has no usable inputs. The observed report/collection inventory, not Amazon wording, is the client contract.

Use `RIDI_DEVICENAME`, `RIDI_DEVICEINFO`, and `RIDI_PREPARSEDDATA` to identify collections and obtain parser data. `RIDI_PREPARSEDDATA` gives a Windows parser structure, not necessarily the original byte-for-byte Report Map. [GetRawInputDeviceInfo](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getrawinputdeviceinfoa). `HidP_GetCaps` describes a collection from its preparsed data; `HidD_GetPreparsedData` can obtain it from an open collection and its allocated buffer must later be freed with `HidD_FreePreparsedData`. [HidP_GetCaps](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/hidpi/nf-hidpi-hidp_getcaps), [HidD_GetPreparsedData](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/hidsdi/nf-hidsdi-hidd_getpreparseddata).

For `RIM_TYPEHID`, process all `RAWHID.dwCount` reports, each `dwSizeHid` bytes in `bRawData`; a single `WM_INPUT` may carry several reports. Save their boundary information. For keyboard and mouse Raw Input types, Windows supplies its keyboard/mouse structures rather than a universal raw BLE payload. [RAWHID definition](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawhid).

#### Avoid the wrong Windows API assumptions

Microsoft's HID architecture marks mouse, keyboard, touchscreen, pen and precision-touchpad collections as **exclusive** system inputs. Consumer controls are listed as shared. A metadata-only HID handle can still be opened without read/write access for information queries, but generic `ReadFile`/hidapi cannot be promised for the exclusive categories. [Windows HID architecture and access table](https://learn.microsoft.com/en-us/windows-hardware/drivers/hid/hid-architecture).

The UWP/WinRT `Windows.Devices.HumanInterfaceDevice` API is more restricted: its documented inaccessible usages include keyboard, mouse, consumer and digitizer collections. Therefore do not select that API as the cross-platform solution for every F3 function. That restriction does **not** mean classic Win32 Raw Input is equally blocked. [Microsoft WinRT HID namespace, inaccessible usages](https://learn.microsoft.com/en-us/uwp/api/windows.devices.humaninterfacedevice?view=winrt-28000).

`RIDEV_NOLEGACY` stops the registered mouse/keyboard legacy messages **for the registering application**. It is not a global per-device interception switch. Background receipt with `RIDEV_INPUTSINK` also does not consume the input so that all other applications stop seeing it. Native OS side effects must be separately tested. [RAWINPUTDEVICE flags and remarks](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-rawinputdevice).

If the F3 is exposed as touch input and Raw Input does not provide the required stream on the actual Windows build, test the focused application's pointer path: `GetPointerInfo` includes a `sourceDevice` handle plus raw/predicted coordinates and flags. Record raw coordinates when classifying captured gestures. [POINTER_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-pointer_info).

For **global** pointer redirection, `RegisterPointerInputTarget` requires UI Access privilege. It redirects all input of the requested pointer type, not only the ring, and only one target per pointer type per desktop is allowed. This is a significant deployment/design step, not something an ordinary background app gets automatically. Do not use an indiscriminate global redirection approach as the first implementation. [RegisterPointerInputTarget](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerpointerinputtarget).

For replacement keyboard/mouse output, `SendInput` is subject to UIPI: injection is limited to equal or lower integrity targets. A standard user background agent cannot promise to control elevated windows just because it received ring input. [SendInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput).

**Unresolved Windows GATT point:** older reports describe protected HID GATT access, but this research did not recover a current primary-source client-side blanket prohibition adequate to claim all Windows builds reject 0x1812. The official GATT-server restricted-service page concerns publishing services and must not be cited as proof of client access restrictions. Plan on Win32 HID/Raw Input for HID and experimentally test any separate vendor GATT service; report `AccessDenied`/empty characteristics exactly if encountered.

## 5. Unrooted Galaxy Z Fold6: Android 17 / One UI 9.0

### 5.0 Specific conclusion for this phone

**Do not write “Android cannot read raw HID” as an unconditional statement.** Current official reference pages document a new `android.hardware.hid` API, including Bluetooth transport, enumeration, report descriptors, feature/output reports, and—in a later minor API version—input-report callbacks. **Do not promise that CJ's Fold6 can use it either.** The screenshot gives Android 17 / One UI 9.0, not the minor SDK version or app permission state. There is also a real contradiction between Google's enterprise overview and its API/manifest permission definition. The correct implementation plan is: capability-test the new API first; keep a normal Android input-event implementation as the baseline; use Linux to complete the Bluetooth protocol capture if raw access is unavailable on the phone. [HidManager](https://developer.android.com/reference/android/hardware/hid/HidManager), [HidDevice](https://developer.android.com/reference/android/hardware/hid/HidDevice), [Android 17 enterprise changes](https://developer.android.com/work/versions/android-17), [ACCESS_HID reference](https://developer.android.com/reference/android/Manifest.permission#ACCESS_HID).

The screenshot is direct evidence for the displayed software identity: Android 17, One UI 9.0, build `CP2A.260605.016.F956U1UEU4EZIH`, and an enforcing SELinux status. The user's statement establishes that the Fold6 is not rooted. It does **not** establish that SDK 37.1/37.2 APIs, the HID service, runtime grant UI, or raw touchscreen reports are accessible to a regular APK on this Samsung build.

### 5.1 Android 17 raw HID: three separate questions

#### 1.1 Does this specific build contain the required API?

| Needed capability | Official reference version |
| --- | --- |
| `android.hardware.hid.HidManager`; `canEnumerateDevices()`; `getDevices()`; device lifecycle listeners | 37.1 |
| `HidDevice`; `getReportDescriptor()`; `getTransport()`; `open()`; `getFeatureReport()`; `sendFeatureReport()`; `sendOutputReport()` | 37.1 |
| `HidDevice.registerEventListener(Executor, HidEventListener)`; unregister | 37.2 |
| `HidEventListener.onInputReport(Report)`, `onError(Exception)`, `onDisconnected()` | 37.2 |

These are minor SDK versions, not “Android 37.” The official 37.2 API diff explicitly adds the input-listener methods relative to 37.1. Do not infer them from `SDK_INT == 37`. Android documents `Build.VERSION.SDK_INT_FULL` for major-plus-minor checks and `Build.getMajorSdkVersion()` / `getMinorSdkVersion()` for interpretation. [HidManager](https://developer.android.com/reference/android/hardware/hid/HidManager), [HidDevice 37.2 diff](https://developer.android.com/sdk/api_diff/37.2/changes/android.hardware.hid.HidDevice), [HidEventListener](https://developer.android.com/reference/android/hardware/hid/HidEventListener), [Build.VERSION](https://developer.android.com/reference/android/os/Build.VERSION#SDK_INT_FULL), [Build](https://developer.android.com/reference/android/os/Build#getMinorSdkVersion(int)).

This matters because a build with descriptor/feature-report APIs can still lack the public asynchronous input-report listener used to receive button streams. Compile-time availability in a new SDK also does not prove that an older installed phone build exposes the method. Log actual method presence and service availability; do not “fix” a missing method by invoking an unrelated hidden HID host API.

#### 1.2 Can a normal installed APK obtain access?

There is a source conflict which must remain explicit:

| Primary source | Exact relevant claim |
| --- | --- |
| Android 17 enterprise overview, updated 2026-10-16 | Calls `ACCESS_HID` a dangerous-level permission. |
| `Manifest.permission.ACCESS_HID` reference | Added in 37.1; protection `internal\|appop`. |
| AOSP `android-17.0.0_r1/core/res/AndroidManifest.xml` | Declares `android.permission.ACCESS_HID` with `android:protectionLevel="internal\|appop"`, gated by `com.android.hardware.input.hid_api`. |
| `HidManager` reference | Requires `ACCESS_HID`; describes system chooser/permission-dialog access to specific devices; warns that background/cached access may be restricted. |

Sources: [enterprise overview](https://developer.android.com/work/versions/android-17), [permission reference](https://developer.android.com/reference/android/Manifest.permission#ACCESS_HID), [release manifest](https://android.googlesource.com/platform/frameworks/base/+/android-17.0.0_r1/core/res/AndroidManifest.xml), [HidManager](https://developer.android.com/reference/android/hardware/hid/HidManager).

**Engineering conclusion:** “Add a permission to the manifest and call `requestPermissions()`” is not a verified solution for this Fold6. `internal` is a system-level protection category; `appop` is an additional flag. The on-device permission definition and actual service decision must settle the issue. These are distinct from `BLUETOOTH_CONNECT` and `BLUETOOTH_SCAN`. [PermissionInfo](https://developer.android.com/reference/android/content/pm/PermissionInfo#PROTECTION_INTERNAL), [Bluetooth permissions](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions).

I did not find a documented public `requestHidPermission(...)` function in the fetched HidManager reference; its exposed methods are enumeration and lifecycle listening. Therefore do not invent a Settings action, chooser intent, ADB grant, or special permission flow. If this firmware exposes a supported system access UI during the public API operation, exercise it with the user; otherwise record the denial and use the fallback.

#### 1.3 Does the granted access include the F3's relevant reports, and does it stop native actions?

The new `HidDevice` documentation explicitly names USB and Bluetooth and defines `TRANSPORT_BLUETOOTH = 5`. It exposes the raw report descriptor and input/feature/output operations; opening is asynchronous and can report permission rejection, I/O failure, or unavailable service. A `Report` models its report ID separately from the binary data; the ID is zero when unused. Preserve both fields as delivered and verify the returned byte framing on the actual API before normalization. Do not prepend or remove an ID merely because a hidraw capture used a prefix. [HidDevice](https://developer.android.com/reference/android/hardware/hid/HidDevice), [Report](https://developer.android.com/reference/android/hardware/hid/Report).

**Unresolved on this build:** whether every F3 HID collection is exposed; whether touchscreen/consumer-control reports are filtered; whether foreground access survives backgrounding; whether opening a device allows concurrent native input, and whether any native action can be suppressed. The fetched public API does not document an exclusive-grab or consume-input operation. Treat “I receive a raw report” and “the ring no longer scrolls/taps the foreground app” as different test assertions. Do not import WebHID/browser collection restrictions into native Android as if they were proven native-HID rules.

### 5.2 Diagnostic APK specification: settle the new-HID ambiguity without root

This is a proposed diagnostic procedure, not a claim that these tests have passed.

1. Build a small foreground diagnostic Activity against an SDK containing the public minor-version HID APIs. Record `Build.VERSION.RELEASE`, `SDK_INT`, `SDK_INT_FULL`, `Build.getMajorSdkVersion(SDK_INT_FULL)`, `getMinorSdkVersion(SDK_INT_FULL)`, `PREVIEW_SDK_INT`, and `Build.FINGERPRINT`. API existence and the full SDK number are the evidence, not the marketing OS label.
2. Declare `android.permission.ACCESS_HID` in the diagnostic APK. Query `PackageManager.getPermissionInfo("android.permission.ACCESS_HID", 0)`; record whether it exists, `getProtection()`, `getProtectionFlags()`, and `checkSelfPermission()`. If absent, report `permission_not_defined`. If its on-device base category is `PROTECTION_DANGEROUS`, the standard runtime-request workflow is applicable; if `PROTECTION_INTERNAL`, do not assume a normal permission dialog can grant it. Record any actual supported system UI.
3. Check presence of the public classes/methods without invoking hidden APIs. It is acceptable to use ordinary public reflection solely to discover whether the documented class/method exists. Handle `ClassNotFoundException` and `NoSuchMethodException` as unsupported capabilities, not as reasons to bypass the SDK.
4. Obtain the HID manager through the documented system service when present. Record `canEnumerateDevices()`. Only call `getDevices()` on a worker thread; the documentation says a main-thread call fails and enumeration can take seconds. Preserve the actual exception class/message if permission is denied.
5. Before pairing the F3, enumerate all visible devices; then pair through system Bluetooth settings and enumerate again. Repeat with T and C switch positions. Correlate additions using name, transport, VID/PID, descriptor hash, physical address/unique ID where exposed, and observed timing. Do not identify the ring by a guessed vendor ID alone.
6. Save each returned raw report descriptor byte-for-byte, record its hash, and parse its collections/report IDs. Open only the positively identified F3 node. Record both enumeration access and per-device `open()` outcome because success of one does not prove the other.
7. If 37.2's input listener is present and opening succeeds, register `HidEventListener`, copy every report's ID and payload, add monotonic timestamps, and run the complete physical-button/mode matrix. If input listeners are absent but 37.1 calls exist, report this accurately; feature-report polling is not a substitute for an input stream.
8. Repeat while a neutral foreground test app is visible and observe whether the native input still occurs. Compare screen-on/off, foreground/background, phone folded/unfolded, portrait/landscape, reconnect, and switching T/C. These are validation cases, not predicted successes.
9. Leave writes disabled by default. Only send a feature/output report once its purpose and legal payload are documented or captured from a known operation. New Android APIs do not create vendor commands that the ring firmware lacks.

API grounding: [Build.VERSION](https://developer.android.com/reference/android/os/Build.VERSION), [PermissionInfo](https://developer.android.com/reference/android/content/pm/PermissionInfo), [runtime permission workflow](https://developer.android.com/training/permissions/requesting), [HidManager](https://developer.android.com/reference/android/hardware/hid/HidManager), [HidDevice](https://developer.android.com/reference/android/hardware/hid/HidDevice), [HidEventListener](https://developer.android.com/reference/android/hardware/hid/HidEventListener).

Recommended diagnostic result fields (our proposed schema):

```text
os_release, sdk_int, sdk_int_full, sdk_major, sdk_minor, preview_sdk, fingerprint
access_hid_defined, protection_base, protection_flags, permission_granted
hid_manager_class_present, hid_service_present, can_enumerate
get_devices_present, input_listener_present
device_identity, transport, descriptor_sha256, descriptor_bytes
open_success, open_exception_class, open_exception_message
report_id, report_payload_hex, monotonic_timestamp_ns
foreground_or_background, native_action_still_occurs
switch_position, physical_button, gesture_type, press_duration_ms
```

### 5.3 Baseline Android input client: useful even when raw HID is unavailable

#### Ordinary foreground Activity

Let Android pair and own the HID connection. An app can inspect `InputDevice.getDeviceIds()` and `getDevice(id)`; use runtime device IDs to associate received events, and record names, VID/PID, source flags, and motion ranges. `InputDevice.getDescriptor()` is an opaque persistent input-device identifier, **not the binary HID report descriptor**. A physical device can create multiple logical Android input devices; runtime IDs can change on reconnect. [InputDevice](https://developer.android.com/reference/android/view/InputDevice).

For touch macros, record the full `MotionEvent` sequence (DOWN, MOVE, UP/CANCEL, pointer IDs/count, history, coordinates, source, device ID), not just one key. For mouse-wheel reports, look for `ACTION_SCROLL` and `AXIS_VSCROLL`/`AXIS_HSCROLL`. Button press/release generic-motion actions use `getActionButton()`; touch and generic motion follow different dispatch paths. Preserve the raw normalized values before interpreting them as “up button” or “swipe.” [MotionEvent](https://developer.android.com/reference/android/view/MotionEvent).

For keys, retain action, key code, scan code, source, device ID, repeat count and timing. Do not equate a Linux scan code, Android key code, HID usage ID, and report ID. AOSP explicitly describes the translation from HID usages through Linux key codes to Android key codes. [AOSP keyboard devices](https://source.android.com/docs/core/interaction/input/keyboard-devices).

This baseline characterizes the normalized key and motion events Android delivers to the foreground app. It does not guarantee visibility into events consumed by system policy or other handlers, and it does not expose the original HID reports. It does not by itself grant background capture from other apps, raw GATT reports, or exclusive control over the ring.

#### Global key remapping through AccessibilityService

If a mode actually emits key events, a user-enabled accessibility service can request `FLAG_REQUEST_FILTER_KEY_EVENTS` and declare `android:canRequestFilterKeyEvents="true"` in accessibility-service metadata. `onKeyEvent()` receives keys before downstream routing; return true to consume or false to pass them through. Match the F3's device identity, handle both DOWN and UP consistently, and copy an event if retaining it after the callback. Mutating the callback's copy does not rewrite the downstream event. [AccessibilityServiceInfo](https://developer.android.com/reference/android/accessibilityservice/AccessibilityServiceInfo#FLAG_REQUEST_FILTER_KEY_EVENTS), [AccessibilityService.onKeyEvent](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService#onKeyEvent(android.view.KeyEvent)).

This route can support user-defined shortcuts from whatever distinct keys actually arrive. It cannot infer separate physical buttons if firmware emits indistinguishable reports, and it does not convert touchscreen macros into key callbacks. Test compatibility with other accessibility services; avoid assuming every reserved/system event is delivered identically on Samsung.

#### Global motion capture has a serious limitation

`AccessibilityService.onMotionEvent()` exists from API 34, but the service must select source types using `AccessibilityServiceInfo.setMotionEventSources()`. Events from selected sources are withheld from the rest of the system. This is a source mask, not a per-device selector. Consequently, requesting `SOURCE_TOUCHSCREEN` to capture an F3 touchscreen collection can also intercept ordinary finger touches. Filtering by `event.deviceId` inside the callback does not retroactively forward all other touches; the callback returns void. Touch exploration also changes whether these callbacks receive touchscreen events. [AccessibilityService.onMotionEvent](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService#onMotionEvent(android.view.MotionEvent)), [setMotionEventSources](https://developer.android.com/reference/android/accessibilityservice/AccessibilityServiceInfo#setMotionEventSources(int)).

**Recommendation:** start with app-local motion observation. Do not enable global touchscreen interception as the default product solution. A user can end up with broken normal touch behavior. `dispatchGesture()` requires the gesture capability and cancels currently ongoing gestures, so it is not a transparent replay mechanism for swallowing and retransmitting arbitrary physical touches. [AccessibilityService.dispatchGesture](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService#dispatchGesture(android.accessibilityservice.GestureDescription,android.accessibilityservice.AccessibilityService.GestureResultCallback,android.os.Handler)).

#### Media-session handling is not universal capture

A real media-key report may route to the foreground Activity or an eligible media session. Android's documented routing selects a session based on activity/playback history; merely declaring an `ACTION_MEDIA_BUTTON` receiver does not guarantee a background ring listener owns every button. Use media APIs when building actual media controls; use accessibility key filtering when the user's required behavior is a global custom shortcut and the device emits usable keys. [Media buttons](https://developer.android.com/media/legacy/media-buttons).

### 5.4 Bluetooth APIs that do not solve the host-access problem

- `android.bluetooth.BluetoothHidDevice` is the **peripheral/device-role** API: it makes Android behave as an HID device to another host. Its documentation says registering an app disables the HID Host service until unregistered and the app unregisters when not foreground. It is not the API to read a ring connected to the phone. [BluetoothHidDevice](https://developer.android.com/reference/android/bluetooth/BluetoothHidDevice).
- The legacy `BluetoothHidHost` class is marked `@SystemApi` and `@hide` in AOSP. A method having a Java `public` modifier in source does not make it an ordinary SDK API. Do not build the release client around reflection against hidden host methods. [BluetoothHidHost source](https://android.googlesource.com/platform/packages/modules/Bluetooth/+/refs/heads/main/framework/java/android/bluetooth/BluetoothHidHost.java).
- Ordinary BLE `BluetoothGatt` access is not a reliable workaround for standard HID-over-GATT. The fetched AOSP GattService protects HID characteristic UUIDs `2A4A` (HID Information), `2A4B` (Report Map), `2A4C` (Control Point), `2A4D` (Report) and their descriptors under service `1812`, enforcing `BLUETOOTH_PRIVILEGED`. This directly includes report notifications and report-map access. The exact restriction is not “all BLE” or necessarily every HID characteristic. [GattService](https://android.googlesource.com/platform/packages/modules/Bluetooth/+/refs/heads/main/android/app/src/com/android/bluetooth/gatt/GattService.java).
- `BLUETOOTH_PRIVILEGED` is explicitly not for third-party applications. A runtime `BLUETOOTH_CONNECT` grant does not supply it. A vendor-specific unprotected GATT service, if actually present, remains a separate possibility; discover it rather than inventing UUIDs. [BLUETOOTH_PRIVILEGED](https://developer.android.com/reference/android/Manifest.permission#BLUETOOTH_PRIVILEGED).

### 5.5 Permissions and background lifetime

For app-driven Bluetooth discovery/connection on current Android, request `BLUETOOTH_SCAN` and/or `BLUETOOTH_CONNECT` as appropriate. An app that only receives OS input events need not create a redundant GATT connection just to see keys. Advertising permission applies only if the app actually advertises. If asserting scan results will never derive physical location, Android supports `neverForLocation`; the docs warn this can filter some beacons. None of these permissions grants raw HID, accessibility access, or background input interception. [Bluetooth permissions](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions).

For a persistent app-owned BLE connection, the official alternatives include a `connectedDevice` foreground service and companion-device presence/service mechanisms; process death closes the connection. The companion pairing mechanism is assistance with selection/association and lifecycle, not a privileged HID bypass. Keep Android's OS-managed HID connection conceptually separate from an application's custom GATT connection. [Background BLE](https://developer.android.com/develop/connectivity/bluetooth/ble/background), [Companion-device pairing](https://developer.android.com/develop/connectivity/bluetooth/companion-device-pairing).

Samsung battery/process behavior, service restart after reboot, and any 37.1/37.2 HID background limits require on-device tests. Do not promise indefinite always-on mapping just because a foreground-service manifest is present.

### 5.6 No-root ADB evidence collection

The following are diagnostic commands to run from the coding agent's Linux/macOS/Windows machine after ordinary USB-debugging authorization. They do not require rooting the phone. A shell command can still be denied by this firmware; record the denial rather than changing SELinux or attempting privileged grants.

```sh
adb devices -l
adb shell getprop ro.product.model
adb shell getprop ro.build.fingerprint
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.sdk
adb shell getprop ro.build.version.sdk_full
adb shell getprop ro.build.version.preview_sdk
adb shell dumpsys input > fold6-input-before.txt
adb shell dumpsys bluetooth_manager > fold6-bluetooth-before.txt
adb shell pm list permissions -f > fold6-permissions.txt
```

`ro.build.version.sdk_full` is the actual property used by AOSP `Build.VERSION.SDK_INT_FULL`; retain its string exactly. If it is empty, do not infer that all minor APIs are missing—use the diagnostic APK's public API checks. `adb devices`, shell commands, and package-manager commands are documented Android tooling; Bluetooth's official debugging guide specifically uses `dumpsys bluetooth_manager`. [Build.java](https://android.googlesource.com/platform/frameworks/base/+/android-17.0.0_r1/core/java/android/os/Build.java), [ADB](https://developer.android.com/tools/adb), [Bluetooth debugging](https://source.android.com/docs/core/connect/bluetooth/verifying_debugging).

Pair the F3, gather an “after” `dumpsys input` file, switch mode, and gather another. The comparison is designed to reveal logical input nodes and source classifications. Add diagnostic APK output for actual event data.

Optional kernel-event attempt:

```sh
adb shell getevent -lp
adb shell getevent -lt
```

Stop the live stream with Ctrl+C. **This is conditional, not a guaranteed no-root capture route.** Google's full getevent documentation uses `su` in its examples; the earlier page extraction omitted those command blocks, which is why I re-fetched it. A stock Samsung build may deny the shell permission to open `/dev/input/event*`. The absence of output or a permission error does not show the ring emitted no reports. Use the diagnostic Activity/accessibility probe or HCI logs. [getevent full documentation](https://source.android.com/docs/core/interaction/input/getevent).

#### HCI snoop: the best phone-side protocol evidence if the vendor includes it in bugreports

1. Enable Developer options and **Bluetooth HCI snoop log**.
2. Restart Bluetooth as the AOSP guide requires.
3. Pair/reconnect the F3 and execute a timestamped test sequence for each mode/button.
4. Capture a bugreport:

```sh
adb bugreport fold6-f3-bugreport.zip
```

Inspect the ZIP for an included Bluetooth log under its `FS` tree. AOSP says full snoop files are usually under `/data/misc/bluetooth/logs`, but direct `adb pull` from that protected path must not be promised on an unrooted Fold6. If the text bugreport contains the in-memory Bluetooth section, use the official `btsnooz.py` extraction method. Always-on in-memory logging is deliberately limited; enable full HCI logging first if report payloads are required. Vendor retention/export still needs verification. [Bluetooth debug guide](https://source.android.com/docs/core/connect/bluetooth/verifying_debugging), [capture/read bugreports](https://developer.android.com/studio/debug/bug-report), [official btsnooz.py](https://cs.android.com/android/platform/superproject/+/android-latest-release:packages/modules/Bluetooth/system/tools/scripts/btsnooz.py).

Host-side HCI logs can establish the device's actual ATT/GATT HID traffic or Bluetooth Classic channels. A successful capture is evidence; the menu toggle alone is not. Hand the coding agent the ring-specific capture and decoded report map, rather than assuming an entire bugreport must become part of the final published artifact.

### 5.7 Predicted result on CJ's Fold6, stated at the appropriate certainty

| Goal | Prediction / restriction |
| --- | --- |
| Use stock F3 functions with a normally paired phone | Expected according to the product's Android targeting; test exact app/layout/mode behavior. |
| Read F3 input while our own app is in foreground | Strong baseline: normalized key/motion input; inspect all device nodes and sources. |
| Global custom shortcuts from distinct key/consumer-key reports | Plausible with user-enabled accessibility key filtering; test actual delivered events and suppression. |
| Global custom shortcuts from touchscreen swipe/tap macros | Significantly harder: key callbacks do not see them; global motion capture is source-wide and can disrupt normal touch. |
| Raw Bluetooth report descriptor/input stream through new native HID API | Conditional on 37.1/37.2 availability, ACCESS_HID grant mechanism, per-device opening and collection exposure; cannot be promised from screenshot. |
| Standard HID GATT notification reader implemented as ordinary APK | Predict rejection for protected report/map UUIDs under AOSP rules; Nearby Devices consent is insufficient. |
| Reprogram physical T/C switch or firmware button mapping | No Android OS API creates this ability; requires a real F3 vendor command/feature report, if one exists. |
| Suppress all native F3 actions while reading raw HID | Unverified; the new public HID reference does not document an exclusive grab. |
| Indefinite background operation, screen locked, after reboot | Must be validated separately; input ownership, foreground restrictions, service lifecycle and Samsung behavior matter. |

This table is engineering judgment derived from the sources above, not a claim that the phone or ring was physically tested.

## 6. Shared decoder, integration contract, and implementation order

### 6.1 Normalize the transport once

The following adapter contract is a proposed design. Preserve the backend's original bytes and metadata, then produce a canonical `(report_id, payload)` before invoking the parser. The canonical payload excludes any OS report-ID prefix and excludes ATT/HCI framing.

| Backend | Expected framing / action |
|---|---|
| Direct BLE GATT report characteristic | Report Reference 2908 supplies the ID; the notification value is 4 bytes for ID3 or 2 bytes for ID2. Do not strip its first byte as if it were an ID. [HOGP §4.8.1](https://www.bluetooth.com/specifications/specs/html/?src=HOGP_v1.0/out/en/index-en.html). |
| Linux numbered hidraw read | First byte is report ID; separate it once. Known ID3 read is 5 bytes including ID, ID2 is 3. [Kernel hidraw](https://docs.kernel.org/hid/hidraw.html). |
| HIDAPI numbered input | First byte is report ID. Backend access limitations still apply. [Upstream header](https://raw.githubusercontent.com/libusb/hidapi/master/hidapi/hidapi.h). |
| Apple CoreHID input notification | For a multiple-report device, `data` includes the report ID as its first byte **even though `id` is supplied separately**. Cross-check them, strip once, then decode. [Apple notification contract](https://developer.apple.com/documentation/corehid/hiddeviceclient/notification/inputreport(id:data:timestamp:)). |
| Android native `Report` | `getReportId()` and `getData()` are separately modeled. Preserve both verbatim and verify actual returned framing/length on this new API before normalizing; do not blindly duplicate or remove an ID. [Android Report](https://developer.android.com/reference/android/hardware/hid/Report). |
| Linux evdev, Android MotionEvent/KeyEvent, Windows pointer events | These are translated input structures, not the four-byte BLE payload. Use a separate semantic-input adapter. [Linux input](https://docs.kernel.org/input/input.html), [Android MotionEvent](https://developer.android.com/reference/android/view/MotionEvent), [Windows POINTER_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-pointer_info). |

### 6.2 Minimal pure decoder for the verified candidate descriptor

This is newly written reference code derived from the captured Report Map. It performs no Bluetooth I/O and sends no commands. Use it only after confirming the report-map fingerprint, or after independently parsing an equivalent descriptor. It does not reconstruct physical button identity or long-press duration.

```python
def decode_f3_payload(report_id: int, payload: bytes) -> dict:
    # Input is canonical: no report-ID prefix and no ATT/HCI headers.
    if report_id == 3:
        if len(payload) != 4:
            raise ValueError(f"F3 report 3: expected 4 bytes, got {len(payload)}")
        b0, b1, b2, b3 = payload
        x = b1 | ((b2 & 0x0F) << 8)
        y = (b2 >> 4) | (b3 << 4)
        return {
            "kind": "touch_sample",
            "tip": bool(b0 & 0x01),
            "in_range": bool(b0 & 0x02),
            "confidence": bool(b0 & 0x04),
            "contact_id": b0 >> 3,
            "x": x,
            "y": y,
            "outside_declared_range": x > 1000 or y > 1000,
            "raw_hex": payload.hex(),
        }
    if report_id == 2:
        if len(payload) != 2:
            raise ValueError(f"F3 report 2: expected 2 bytes, got {len(payload)}")
        mask = int.from_bytes(payload, "little")
        return {
            "kind": "consumer_state",
            "mask": mask,
            "active_bits": [n for n in range(16) if mask & (1 << n)],
            "released": mask == 0,
            "raw_hex": payload.hex(),
        }
    return {"kind": "unknown_report", "report_id": report_id,
            "raw_hex": payload.hex()}

# Derived fixture checks; these do not establish hardware compatibility.
assert decode_f3_payload(3, bytes.fromhex("07f4014b"))["y"] == 1200
assert decode_f3_payload(3, bytes.fromhex("02bc421f"))["tip"] is False
assert decode_f3_payload(2, bytes.fromhex("4000"))["active_bits"] == [6]
assert decode_f3_payload(2, bytes.fromhex("8000"))["active_bits"] == [7]
assert decode_f3_payload(2, bytes.fromhex("0000"))["released"] is True
```

The first vector deliberately preserves the captured Y=1200 anomaly. The inactive `02` vector deliberately prevents treating “in range” as a finger-down event. These are observed protocol properties, not arbitrary sample numbers. [Frozen capture B](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T061403Z-eb800388708b.jsonl).

### 6.3 Keep raw reports, generated gestures, physical controls, and app actions separate

A useful internal event chain is **backend input → normalized report/contact → generated gesture or consumer key → optional physical-control attribution → application action**. This is an implementation recommendation. For example, an incoming left swipe is not intrinsically “next page,” “profile,” or “upper button”: the captured F3 generates the same bytes for **T/M and C/U**, and application behavior depends on context. [Corrected physical mapping](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1#issuecomment-6205704870).

Implement the following rules:

1. Keep contact state keyed by the observed logical device and contact ID. Begin on Tip 0→1, collect coordinates while Tip=1, finish once on Tip 1→0. Do not count In Range, Confidence, hover positions, or lift-tail positions as additional presses.
2. Classify a finished stroke from its active path. Use a configurable displacement threshold learned from the actual ring; retain the full path so an unexpected macro can be diagnosed. Do not assign one action per packet.
3. Process consumer reports as state changes. For a calibrated C/M shortcut, accept both Volume Increment and Decrement; fire once on the relevant rising edge and release on zero. Do not assume a particular initial alternation phase after power or reconnection.
4. Maintain an explicit mode value with an **unknown** state. A settings choice or guided physical switch prompt can supply mode. A vertical gesture can be evidence for the known T profile, but a volume event cannot reliably prove C: T-mode holds are documented as volume actions too. Never use HID Protocol Mode as the physical switch value. [FiKavi T functions](https://fikavi.com/f3-shorts-scrolling/), [HIDS Protocol Mode](https://www.bluetooth.com/specifications/specs/html/?src=hids_v1-0_1765320236/HIDS_v1.0/out/en/index-en.html).
5. Make three backend capabilities explicit: **observe**, **suppress native input**, and **emit replacement input**. Enable custom global actions only after checking whether the original gesture still reaches the foreground application. Desktop/phone APIs differ here; success reading a report does not grant exclusive control.
6. Clear contact/consumer state after disconnect, device removal, read failure, capture overflow, or timeout. Reidentify all logical collections on reconnect; never persist `/dev/input/event2` or a transient Android device ID as a permanent identity.
7. Keep a raw-data mode for unknown descriptors, report IDs, lengths, or modes. Report “unsupported profile; capture needed” instead of mislabeling input. Parser and calibration changes should be versioned with their evidence.

These are proposed engineering rules grounded in the known F3 sequences and the platform interfaces described above. No exact firmware debounce duration, double-click window, physical hold timer, or hidden state machine has been verified.

### 6.4 Recommended work sequence for the coding agent

**First: build a read-only diagnostic logger on Linux.** Save the raw map, all collection identities, raw reports, evdev frames and a labeled capture. Linux's hidraw/evdev/grab interfaces make it the clearest reference platform. This is a recommendation based on the documented interfaces, not a claim that other operating systems are incapable. [Linux HID guide](https://docs.kernel.org/hid/hidintro.html), [hidraw](https://docs.kernel.org/hid/hidraw.html).

**Second: implement the shared decoder and gesture recognizer against captured fixtures, then test on the physical unit.** Start with known single presses in T and C. Add double/triple/hold macros only after measuring them. A simulated test should use observed packet streams and check one completed action per input; a decoder passing its own handcrafted examples alone does not validate a real ring.

**Third: add the preferred desktop backend and verify suppression separately.** On macOS use native HID access; on Windows test the actual touchscreen collection through Raw Input/pointer routes before committing to a globally acting product. Keep the dedicated Bumble/serial-HCI research setup distinct from ordinary native Windows Bluetooth support.

**In parallel: run the small Android capability probe.** That resolves the largest feasibility question early: whether this exact Fold6 has the new native HID input-listener API and an access path available to an ordinary APK. If that probe fails, deliver app-local motion handling and any usable accessibility key shortcuts as explicitly limited capabilities; do not claim complete global ring remapping.

**Finally: validate the user-facing action.** If the ring is intended to start dictation, for example, test the complete chain from one physical input to exactly one start/stop action, with no unwanted foreground swipe or volume change. The physical-control decoder and application integration should remain separate so application commands can change without rewriting the protocol parser.

## 7. Exact capture plan to close the remaining gaps

This is the proposed next experiment on the user's device, not a record of tests performed in this investigation. No destructive writes or firmware flashing are needed to establish the input protocol.

### 7.1 Capture identity first

Record a photograph of the labeled buttons and switch, host OS/build/Bluetooth adapter, advertised name/address type, discovered service instances, characteristic properties, all report references, full Report Map bytes/hash, PnP bytes, and any revision strings actually exposed. Repeat the inventory in T and C and after a cold power cycle. Disconnect competing hosts during the test so reconnecting to another phone does not look like an input failure.

Use a neutral test surface that logs input and does not publish, like, call, or send anything. Record screen effects separately in the actual target application after the input capture works. This matters concretely because the manufacturer's D double-click is a “like” action in short-video browsing. [Manufacturer diagram](https://fikavi.com/wp-content/uploads/2025/06/TIKTOK-VIDEO.jpg).

### 7.2 Button/mode experiment matrix

| Dimension | Proposed cases | Evidence to save |
|---|---|---|
| Basic identity | T then C; U, M, D; at least 10 isolated short presses each | Every raw report and exactly which labeled physical button was pressed; packet count versus completed action count. |
| Click grouping | Singles, doubles, triples, initially around 100/200/350/500 ms between clicks | Whether firmware sends separate gestures, suppresses singles, emits a different macro, or emits consumer bits. These timings are test choices, not known thresholds. |
| Hold | 0.2/0.5/1/2/3/5 seconds on each button | Raw input during the hold and on release; any repeat frequency or changed gesture; compare physical duration with synthetic touch duration. |
| Combined buttons | U+M, M+D, U+D, then all three, only after basic capture | Whether there is a documented/observed special operation. Stop if the device enters reset/pairing behavior; do not interpret silence as a valid command. |
| Physical switch | O→T, O→C, T→C, C→T while connected and while disconnected | Advertising changes, connection loss, Report Map changes, characteristic values and notifications. |
| Power/sleep | Increasing idle intervals, first press after idle, reconnect, charger connected/unplugged | Whether the wake press is delivered, time to reconnect, persistence of mode/bond, and center alternation phase. |
| Phone display | Folded and unfolded; portrait; both landscape directions; optional external display/DeX only if used | Android source device, motion ranges, rotation, resulting coordinates and visible action. |
| App behavior | Exact camera/reader/video-app versions and settings | Separate packet sequence from intended and actual effect; test default-input suppression. |
| Lifetime | Foreground/background, display off/locked, process restart, Bluetooth reconnect, phone reboot | Delivered/missed/duplicated input, permission retention, logical-device identity changes. |

Do not generate a misleading “all commands captured” result merely because all test steps were marked complete. The public logs themselves requested 36 ordinary presses but received 31, owing to disconnect gaps. Match physical trials to actual received sequences and mark missing trials as missing. [Capture A](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T060407Z-eb800388708b.jsonl), [capture B](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T061403Z-eb800388708b.jsonl).

### 7.3 Output of each experiment

The coding agent should produce a machine-readable capture manifest and a human-readable table. This proposed schema is sufficient to distinguish physical behavior from host interpretation:

```text
device_profile: model, FCC_ID, physical_label_photo, address_type, PnP_raw
host: OS, build, adapter, Bluetooth_stack, backend, API_versions, permissions
profile: service_instances, characteristic_handles, properties, report_references
report_map: exact_bytes, SHA256, source_transport, any_host_patch
trial: id, switch_position, button_label, click_count, hold_ms, interval_ms
context: foreground_app, app_version, display_id, folded_state, rotation
input: monotonic_timestamp_ns, backend_device_id, report_id, original_hex
decoded: contact_id, tip, in_range, confidence, x, y, consumer_mask
result: completed_gesture, inferred_control, intended_action, native_action
quality: received_trial, disconnects, dropped_frames, errors, ambiguity
```

For OS-translated input, retain original key/motion/event records even if the raw BLE payload is unavailable. An Android `InputDevice` descriptor string is an identifier, not the HID Report Map; Windows preparsed data is parser metadata, not necessarily original descriptor bytes. Record the provenance of every artifact. [Android InputDevice](https://developer.android.com/reference/android/view/InputDevice), [Windows Raw Input device information](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getrawinputdeviceinfoa).

## 8. Unknowns register and exact disambiguation method

| Unresolved question | Why the current evidence is insufficient | Exact next action |
|---|---|---|
| Is this physical ring firmware-identical to the public sample? | Same ASIN/model/FCC chain is strong identity evidence, but the sample lacks a manufacturer firmware revision. | Read the user's Report Map and full GATT table; compare binary hash and button traces. A matching map proves layout compatibility, not all firmware timing. |
| What are double/triple/hold packet sequences? | Manufacturer describes effects; available packet trials are short single presses. | Run the explicit timing matrix, preserving all packets before/during/after the physical action. |
| What button really advances a C-mode eBook? | Old leaflet and newer portrait diagram disagree; app interpretation varies. | Record U/M/D separately in the exact reader with paging enabled; use raw gesture direction independently of page direction. |
| Can physical T/C be read or set remotely? | No mode characteristic or command established; identical left-swipe sequences have multiple physical causes. | Compare complete read-only discovery and notifications across a physical switch. Ask manufacturer for a documented mode command if none appears. |
| What does FAB0 do? | Only UUIDs/properties are captured; FAB1/FAB2 are writable and FAB3 notifies, with no public command contract found. | Request UUID definitions, framing, opcodes, lengths, checksums, security, responses, version applicability; or capture an official app's known exchange. Do not fuzz writes just to discover a button API. |
| Are report IDs 1,4,5 meaningful? | GATT references exist but the descriptor defines only IDs2/3 and recorded notifications use only2/3. | Log all input report characteristics during the full matrix; preserve unknown bytes. Do not create parser fields without a descriptor or reproducible evidence. |
| Is battery level available? | Captured table has no Battery Service180F or battery characteristic. | Inspect this unit's actual services and manufacturer documentation. Never equate LED state with an exact percentage. |
| Does USB-C provide data or firmware access? | Product instructions identify charging only. | Connect with a known data cable and inspect host USB enumeration. Ask manufacturer if no interface appears; absence with one cable is inconclusive. |
| Can ordinary Android APK use new native HID on this Fold6? | Android version label lacks minor API level; permission overview and manifest/reference conflict. | Execute the Android diagnostic APK and no-root ADB inventory below; record class/method presence, permission category, enumeration/open/listener results. |
| Can Android read the ring without its swipe reaching other apps? | New native HID docs do not specify exclusive access; source-wide accessibility motion capture can affect normal touch. | Observe native effects while raw listener is active. Reject global-touch design unless normal finger input remains correct and behavior is explicitly supported. |
| Does Windows permit this touch collection through the chosen API? | System-exclusive HID access differs from Raw Input and pointer routing; external serial-HCI capture is not native Windows proof. | Enumerate usages; test Raw Input/background delivery, pointer source identity and actual read errors on the installed Windows build. |
| Is arbitrary on-device remapping/OTA supported? | WS8100 silicon supports programmable firmware/OTA in principle; no F3 image or update protocol established. | Obtain vendor SDK/protocol and exact revision compatibility first. Keep firmware work out of the host-client deliverable unless separately requested. |
| What are bond/reset/sleep rules? | No complete firmware state machine published; public captures include disconnects. | Measure controlled reconnect/idle/power trials and obtain exact manufacturer reset instructions. |

Manufacturer questions should identify **ASIN B0F9DZPJ9Y, Model F3, FCC2BPGR-F3, IC34005-F3**, include the label photo, and ask for the firmware revision, host SDK/HID Report Map, all click/hold/chord mappings, FAB0 protocol, physical-mode query/write support, battery reporting, pairing/reset commands, and USB/OTA support. The available support addresses are [FiKavi](https://fikavi.com/contact/) and [the support page linked from the ring](https://tsmartelectronic.com/f3-i-need-help/). No support message was sent during this research.

## 9. Acceptance criteria and source audit

### 9.1 What counts as complete

The coding agent should only claim **complete for the tested ring/build** when it can identify the device/descriptor, observe every supported physical action in both switch modes, distinguish or explicitly mark indistinguishable controls, recover from reconnect, and execute the requested action without duplicate or unintended native input. Every advertised mapping must have either an actual capture/test result or a precise “unsupported on this host” explanation. Unknown vendor firmware commands are not required for a successful host-side input client, but they must remain unknown rather than being replaced by guesses.

The implementation should retain a capability report per platform. For example, “foreground touch recognition works, global touchscreen suppression unavailable” is a valid limited Android result; it is not full global control. “Raw reports received through external serial HCI” is a valid research result; it does not establish native Windows API support. “Report Map matched” validates the decoder layout; it does not validate hold timing or shutter behavior.

### 9.2 Research performed and limits

The research used Jasa search to locate sources and Jasa full-page fetching for claims. Missing or wrong extractions were retried using another provider. Manufacturer images and the one-page FCC leaflet were inspected visually; the ring's QR was decoded from the supplied photograph. Actual capture files were parsed as JSONL, their report lengths/bit layouts and hash were independently checked, and the public author's reversed up/down-label correction was incorporated. The reference decoder in this handoff is derived from the bytes, not a claimed successful connection to the user's ring.

The frozen capture repository revision is **b21c12636439e1e705ad8c8e354253c0cae88980**. The exact input fixtures are [20261015T060407Z-eb800388708b.jsonl](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T060407Z-eb800388708b.jsonl) and [20261015T061403Z-eb800388708b.jsonl](https://github.com/JPHutchins/ble-page-turner-investigations/blob/b21c12636439e1e705ad8c8e354253c0cae88980/captures/20261015T061403Z-eb800388708b.jsonl). The full hardware comment is [here](https://github.com/JPHutchins/kindle-button-mapper-rs/pull/1#issuecomment-6205704870); its raw-event attachment is [f3_ring_hil_raw_data.zip](https://github.com/user-attachments/files/33520175/f3_ring_hil_raw_data.zip). The attachment is an additional source artifact linked by the report; the raw BLE fixtures and comment itself were the directly analyzed evidence in this investigation.

**Retrieval limitations:** the QR-linked FAQ could not be retrieved; a Canadian IC certification entry was not independently verified; public manufacturer firmware/SDK/FAB0 command documentation was not found; the current USB HID Usage Tables PDF could not be retrieved, so the relevant stable consumer-usage names were checked against USB-IF's [HUT1.12](https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf). Android17 API availability and permission inconsistencies remain explicit. This handoff documents the most concrete available input protocol and exactly what must be measured before claiming full coverage.
