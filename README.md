# d3kOS — Helm Intelligence for Your Boat

**An open-source operating system for Raspberry Pi that gives your boat a brain.**

If your boat doesn't have radar, a weather station, or a $5,000 multifunction display — d3kOS was built for you.
Flash an SD card, plug it into a Raspberry Pi 4 at your helm, and you have a fully working marine intelligence centre running on a touchscreen. No programming required after installation.

**Version**: v0.9.9.2 | **Released**: April 12, 2026 | **Platform**: Raspberry Pi 4B

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

**Latest Release: v0.9.9.2**

| | |
|---|---|
| **Archive.org page** | https://archive.org/details/d3kos_v0.9.9.2 |
| **Direct download** | https://archive.org/download/d3kos_v0.9.9.2/d3kos_v0.9.9.2.img |
| **Format** | `.img` file — flash directly with Raspberry Pi Imager |
| **Size** | ~50 GB uncompressed |
| **Hardware** | Raspberry Pi 4B, 4 GB RAM minimum |

**How to flash:**

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/) — free, works on Windows, Mac, Linux
2. Open Imager → **Choose OS** → **Use custom** → select the `.img` file
3. **Choose Storage** → select your SD card (32 GB or larger recommended)
4. Click **Write** — done

Power on your Pi, wait 60 seconds, and the d3kOS setup wizard will launch automatically on your screen.

---

## What d3kOS Does

d3kOS gives you nine dedicated tools, all accessible from the touchscreen at your helm:

| Tool | What It Does |
|------|-------------|
| **AI Navigation** | Ask plain-English questions about navigation, regulations, or your route — powered by Gemini AI with an offline knowledge base backup |
| **Engine Dashboard** | Live engine gauges — RPM, coolant temperature, oil pressure, battery voltage, fuel level. Alerts when something needs attention |
| **Helm Assistant** | Hands-free voice AI. Say "Helm" and ask anything. Works offline using a local knowledge base when there is no internet |
| **Anchor Watch** | Monitors your anchor position while you rest. Sounds an alarm if the boat drifts beyond your set radius |
| **Marine Vision** | Connects up to 20 IP cameras. Monitors your deck, dock lines, and surroundings. Includes fish detection for fishing boats |
| **Boat Log** | Keeps an automatic log of your trips — engine starts and stops, position snapshots, and voice notes you record yourself |
| **Upload Documents** | Load your engine manual, flare checklist, or any PDF onto the Pi so HELM can answer questions from your own documents |
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
| Raspberry Pi 4B | 4 GB RAM minimum — 8 GB recommended |
| microSD Card | 32 GB minimum, Class 10 or better |
| Touchscreen | 10.1 inch, 1280×800, HDMI + USB touch. Must be rated for your environment. |
| Power supply | 12V to 5V DC-DC converter rated at 5A minimum. Use a marine-grade isolated converter. |
| USB GPS receiver | Any standard USB GPS (gpsd-compatible) |

### Optional Hardware

| Item | What It Adds |
|------|-------------|
| USB speakerphone (e.g. Anker S330) | Hands-free HELM voice assistant |
| IP cameras (PoE, RTSP stream) | Marine Vision camera system |
| NMEA 2000 gateway (e.g. CX5106 or PiCAN-M) | Live engine data from your NMEA 2000 network |

See [`docs/INSTALLATION.md`](docs/INSTALLATION.md) and [`docs/CX5106_CONFIGURATION_GUIDE.md`](docs/CX5106_CONFIGURATION_GUIDE.md) for detailed setup guides.

---

## Language Support

d3kOS supports 18 languages. Change the display language in Settings → Language at any time.

Arabic · Danish · German · Greek · English · Spanish · Finnish · French · Croatian · Italian · Japanese · Dutch · Norwegian · Portuguese · Swedish · Turkish · Ukrainian · Chinese

---

## Documentation

| Document | Description |
|----------|-------------|
| [`docs/D3KOS_USER_MANUAL_v2.3.0.md`](docs/D3KOS_USER_MANUAL_v2.3.0.md) | Full user manual — installation, setup wizard, all features, troubleshooting |
| [`docs/INSTALLATION.md`](docs/INSTALLATION.md) | Step-by-step installation guide |
| [`docs/SIGNALK_CONFIGURATION.md`](docs/SIGNALK_CONFIGURATION.md) | Connecting NMEA 0183 and NMEA 2000 instruments |
| [`docs/CX5106_CONFIGURATION_GUIDE.md`](docs/CX5106_CONFIGURATION_GUIDE.md) | CX5106 NMEA gateway setup and DIP switch reference |
| [`docs/REMOTE_ACCESS_SETUP.md`](docs/REMOTE_ACCESS_SETUP.md) | Accessing d3kOS from another device on your network |
| [`docs/OPENCPN_FLATPAK_OCHARTS.md`](docs/OPENCPN_FLATPAK_OCHARTS.md) | Installing OpenCPN and paid o-charts chart packs |
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
Contact: skipperdont@atmyboat.com

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
