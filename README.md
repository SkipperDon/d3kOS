# d3kOS — Helm Intelligence for Your Boat

**An open-source operating system for Raspberry Pi that gives your boat a brain.**

If your boat doesn't have radar, a weather station, or a $5,000 multifunction display — d3kOS was built for you.
Flash an SD card, plug it into a Raspberry Pi 4 at your helm, and you have a fully working marine intelligence centre running on a touchscreen. No programming required after installation.

**Version**: v0.9.9.5 | **Released**: October 9, 2026 | **Platform**: Raspberry Pi 4B (8 GB RAM)

---

## Is This for Me?

d3kOS is built for the boater who:

- Wants more situational awareness without spending thousands of dollars on marine electronics
- Is comfortable with basic computer tasks but has little or no Raspberry Pi experience
- Keeps a pleasure boat, fishing boat, or small cruiser on fresh water or coastal waters
- Values safety features that work even when there is no internet connection

If you can burn an SD card and connect a screen to a Pi, you can run d3kOS.
The setup wizard walks you through the rest.

---

## Download

**Latest Release: v0.9.9.5**

| | |
|---|---|
| **Archive.org page** | https://archive.org/details/d3kos-v0.9.9.5-20261009.img |
| **Direct download** | https://archive.org/download/d3kos-v0.9.9.5-20261009.img/d3kos-v0.9.9.5-20261009.img.gz |
| **Format** | `.img.gz` — flash directly with Raspberry Pi Imager |
| **Size** | 128 GB SD card minimum |
| **Hardware** | Raspberry Pi 4B, 8 GB RAM minimum |
| **SHA-256** | `28437d4bd6b29a2640a5303cfdc5510781a648945aea82ff141b8b264f85f878` |

**How to flash:**

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/) — free, works on Windows, Mac, Linux
2. Open Imager → **Choose OS** → **Use custom** → select the `.img` file
3. **Choose Storage** → select your SD card (128 GB minimum)
4. Click **Write** — done

Power on your Pi, wait 60 seconds, and the d3kOS setup wizard will launch automatically on your screen.

> **Updates require registration.** Download and install v0.9.9.5 once. To receive all incremental over-the-air (OTA) updates after that, your Pi must be registered at [AtMyBoat.com](https://atmyboat.com) — scan the QR code in the setup wizard.

---

## What d3kOS Does

d3kOS gives you nine dedicated tools, all accessible from the touchscreen at your helm:

| Tool | What It Does |
|------|-------------|
| **AI Navigation** | Ask plain-English questions about navigation, regulations, or your route — powered by Gemini AI (your own free API key) |
| **Engine Dashboard** | Live engine gauges — RPM, coolant temperature, oil pressure, battery voltage, fuel level. Alerts when something needs attention |
| **Helm Assistant** | Hands-free voice AI. Say "Helm" and ask anything. Voice needs free registration (Tier 1) in this release |
| **Anchor Watch** | Monitors your anchor position while you rest. Sounds an alarm if the boat drifts beyond your set radius |
| **Marine Vision** | IP cameras for your deck, dock lines and surroundings, plus Forward Watch bow-camera hazard detection. Cameras need free registration (Tier 1) in this release. Fish species identification is in development |
| **Boat Log** | Keeps an automatic log of your trips — engine starts and stops, position snapshots, and voice notes you record yourself |
| **Upload Documents** | Load your engine manual, flare checklist, or any PDF onto the Pi |
| **Settings** | Configure your vessel, units (metric or imperial), language, display, and connected hardware |
| **Help / Manual** | The full user manual, always available on the Pi even without internet |

The main dashboard also includes:

- **Charts** — AvNav chart plotter integrated directly into the dashboard
- **Weather** — live wind and wave map (Windy) for voyage planning
- **Camera view** — all connected cameras at a glance

---

## Supported by AtMyBoat.com

d3kOS is the open-source software. **[AtMyBoat.com](https://atmyboat.com)** is the community and support platform built around it.

When you register at AtMyBoat.com you get:

- **Cameras, Helm voice and over-the-air updates** — in this release these need a free, approved registration (Tier 1)
- **Mobile companion app** — check your boat's status from your phone, receive engine alerts, and view your boat log remotely
- **Fix My Pi** — if something goes wrong, the app walks you through diagnosing and recovering your system
- **Community forum** — other d3kOS boaters, setup questions, tips, and trip reports
- **AI Help Centre** — ask boating questions from any browser, even when you are not on the boat

AtMyBoat.com is free to join. The mobile app has free and supported tiers.

---

## What You Need

### Required Hardware

| Item | What to Look For |
|------|-----------------|
| Raspberry Pi 4B | 8 GB RAM minimum |
| microSD Card | 128 GB minimum, Class 10 or better |
| Touchscreen | 10.1 inch, 1280×800, HDMI + USB touch. Must be rated for your environment. |
| Power supply | 12V to 5V DC-DC converter rated at 5A minimum. Use a marine-grade isolated converter. |

### Optional Hardware

| Item | What It Adds |
|------|-------------|
| USB speakerphone (e.g. Anker S330) | Hands-free HELM voice assistant |
| IP cameras (PoE, RTSP stream) | Marine Vision camera system |
| NMEA 2000 adapter (PiCAN-M or USB-CAN-A) | Live engine data from your NMEA 2000 network — detected automatically at boot |
| USB GPS receiver | GPS position — needed only if your NMEA 2000 network has no GPS |

See the [user manual](https://github.com/SkipperDon/d3kOS/blob/main/docs/D3KOS_USER_MANUAL_v2.9.0.md) and [`INSTALLATION.md`](https://github.com/SkipperDon/d3kOS/blob/main/docs/INSTALLATION.md) for detailed setup guides.

---

## Language Support

d3kOS supports 18 languages. Change the display language in Settings → Language at any time.

Arabic · Danish · German · Greek · English · Spanish · Finnish · French · Croatian · Italian · Japanese · Dutch · Norwegian · Portuguese · Swedish · Turkish · Ukrainian · Chinese

---

## Documentation

| Document | Description |
|----------|-------------|
| [User Manual v2.9.0](https://github.com/SkipperDon/d3kOS/blob/main/docs/D3KOS_USER_MANUAL_v2.9.0.md) | Full user manual for v0.9.9.5 — setup wizard, all features, troubleshooting (also at [atmyboat.com/manual](https://atmyboat.com/manual/)) |
| [`INSTALLATION.md`](https://github.com/SkipperDon/d3kOS/blob/main/docs/INSTALLATION.md) | Step-by-step installation guide |
| [`OPENCPN_FLATPAK_OCHARTS.md`](https://github.com/SkipperDon/d3kOS/blob/main/docs/OPENCPN_FLATPAK_OCHARTS.md) | Installing OpenCPN and paid o-charts chart packs |
| [`CHANGELOG.md`](CHANGELOG.md) | Full version history |

---

## Important — Safety Notice

> **d3kOS is not a certified navigation instrument and is not a substitute for proper seamanship, certified charts, or the navigation equipment required by the laws of your jurisdiction.**
>
> Always maintain a proper watch. Always carry the safety equipment required by law. Always have current certified charts for your waters. d3kOS is an aid to awareness — it does not replace your legal obligations as a vessel operator.
>
> **This software is provided as-is, with no warranty of any kind.** See [LICENSE](LICENSE) for the full terms. The authors and contributors accept no liability for loss, damage, injury, or death arising from the use of this software.
>
> AI-generated responses from HELM may be incorrect. Do not rely on AI output for safety-critical navigation decisions.

---

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Follow the existing code style — Flask backend, vanilla JavaScript frontend, no UI frameworks
4. Submit a pull request with a clear description of what changed and why

For questions or to report an issue: [GitHub Issues](https://github.com/SkipperDon/d3kOS/issues)

---

## License

d3kOS is dual licensed:

**Open Source — GPL v3**
Free to use, modify, and distribute under the GNU General Public License v3.0.
Any derivative works must also be released under GPL v3. See [LICENSE](LICENSE).

**Commercial License**
Commercial use — including bundling with hardware for resale or distribution in paid products — requires a separate commercial license agreement.
Contact: skipperdon@atmyboat.com

---

## Acknowledgements

Built on these outstanding open-source projects:

- **[Signal K](https://signalk.org/)** — universal marine data standard
- **[AvNav](https://www.wellenvogel.net/software/avnav/docs/en_index.html)** — marine chart navigation
- **[OpenCPN](https://opencpn.org/)** — open-source chartplotter
- **[Vosk](https://alphacephei.com/vosk/)** — offline speech recognition
- **[Piper](https://github.com/rhasspy/piper)** — fast offline text-to-speech
- **[YOLOv8](https://github.com/ultralytics/ultralytics)** — real-time object detection
- **[ChromaDB](https://www.trychroma.com/)** — local vector database
- **[Node-RED](https://nodered.org/)** — flow-based automation

---

*Built by boaters, for boaters. Supported by [AtMyBoat.com](https://atmyboat.com).*
