# LunaTranslator Overlay for Steam Deck

> Play Japanese Visual Novels on Steam Deck with real-time translation overlay in Gaming Mode!

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Steam Deck](https://img.shields.io/badge/Steam%20Deck-Compatible-green.svg)](https://www.steamdeck.com/)
[![Decky Loader](https://img.shields.io/badge/Decky%20Loader-Plugin-orange.svg)](https://decky.xyz/)

---

## What is this?

A **Decky Loader plugin** that displays [LunaTranslator](https://github.com/HIllya51/LunaTranslator) translations as an overlay directly in Steam Deck's Gaming Mode.

**No more switching windows!** See translations right on top of your game.

### How it works

```
┌─────────────────────────────────────────────────────────┐
│ Wine/Proton (via Lutris)                                │
│  ├── Visual Novel (your game)                           │
│  └── LunaTranslator (hooks & translates)               │
│         │                                               │
│         └── WebSocket Server (port 8080)                │
└─────────────┬───────────────────────────────────────────┘
              │ localhost:8080
              ▼
┌─────────────────────────────────────────────────────────┐
│ Steam Deck (Gaming Mode)                                │
│  └── Decky Plugin                                       │
│        ├── WebSocket Client (connects to LunaTranslator)│
│        └── Overlay (displays translations on screen)    │
└─────────────────────────────────────────────────────────┘
```

---

## Features

- **Real-time translation display** - See translations as they happen
- **Customizable overlay** - Position, size, colors, opacity
- **Original + Translation** - Show both or just translation
- **Auto-hide** - Overlay disappears after configurable timeout
- **Easy configuration** - All settings accessible from Decky menu
- **Low overhead** - Minimal performance impact

---

## Screenshots

*Coming soon*

---

## Requirements

- Steam Deck (or Linux PC with Steam Gaming Mode)
- [Decky Loader](https://decky.xyz/) installed
- [Lutris](https://lutris.net/) (to run LunaTranslator via Wine)
- [LunaTranslator](https://github.com/HIllya51/LunaTranslator) (Windows version)
- Node.js/pnpm (for building)

---

## Quick Install

### 1. Clone and build

```bash
git clone https://github.com/tobidashite/AnulTranslator
cd AnulTranslator/decky-plugin-lunatranslator
./build.sh
./install.sh
```

### 2. Configure LunaTranslator

In LunaTranslator settings, enable **Network Service**:
- Host: `0.0.0.0`
- Port: `8080`

### 3. Use in Gaming Mode

1. Start your game (with LunaTranslator running)
2. Press **...** (Quick Access)
3. Open **Decky** → **LunaTranslator**
4. Click **Connect**
5. Play!

---

## Detailed Installation

See the complete guides:

- **English:** [SETUP_LUTRIS.md](SETUP_LUTRIS.md)
- **Portugues:** [GUIA_COMPLETO_PT-BR.md](GUIA_COMPLETO_PT-BR.md)

---

## Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| **Enable Overlay** | Show/hide the overlay | On |
| **Host** | LunaTranslator IP address | `127.0.0.1` |
| **Port** | LunaTranslator port | `8080` |
| **Show Original** | Display original Japanese text | On |
| **Show Translation** | Display translated text | On |
| **Position** | Overlay position on screen | Bottom |
| **Font Size** | Text size in pixels | 18 |
| **Width %** | Overlay width percentage | 80% |
| **Background Opacity** | Background transparency | 80% |
| **Auto-hide** | Hide after X seconds (0=never) | 10s |

---

## Project Structure

```
decky-plugin-lunatranslator/
├── main.py                  # Python backend (WebSocket client)
├── src/
│   └── index.tsx            # React frontend (overlay + settings UI)
├── plugin.json              # Decky plugin metadata
├── package.json             # Node.js dependencies
├── tsconfig.json            # TypeScript configuration
├── rollup.config.js         # Build configuration
├── defaults/
│   └── defaults.json        # Default settings
├── requirements.txt         # Python dependencies
├── build.sh                 # Build script
├── install.sh               # Installation script
├── uninstall.sh             # Uninstallation script
├── README.md                # This file
├── SETUP_LUTRIS.md          # Lutris setup guide (English)
└── GUIA_COMPLETO_PT-BR.md   # Complete guide (Portuguese)
```

---

## Troubleshooting

### "Connection failed"

1. Make sure LunaTranslator is running
2. Check Network Service is enabled in LunaTranslator settings
3. Verify host is set to `0.0.0.0` (not `127.0.0.1`)

### "websockets not installed"

```bash
pip install --user websockets
```

### Overlay not showing

1. Check "Enable Overlay" is on
2. Verify connection status shows "Connected"
3. Make sure the game is producing text (try a dialogue scene)

### Can't connect from Gaming Mode

The Wine network bridge might use a different IP. Try:

```bash
# Find Wine's IP
ip addr show | grep -E "192\.168|10\."
```

Use that IP in the plugin settings.

---

## Development

### Build

```bash
pnpm install
pnpm build
```

### Watch mode

```bash
pnpm watch
```

### Deploy for testing

```bash
pnpm build
cp -r dist main.py plugin.json ~/homebrew/plugins/LunaTranslator\ Overlay/
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## License

GPL-3.0 (same as LunaTranslator)

---

## Credits

- [LunaTranslator](https://github.com/HIllya51/LunaTranslator) - The amazing Visual Novel translator
- [Decky Loader](https://decky.xyz/) - Steam Deck plugin framework
- [Steam Deck Community](https://www.reddit.com/r/SteamDeck/) - For making this possible!

---

## Support

- **Issues:** [GitHub Issues](https://github.com/tobidashite/AnulTranslator/issues)
- **Discussions:** [GitHub Discussions](https://github.com/tobidashite/AnulTranslator/discussions)

---

**Enjoy playing your favorite Visual Novels on Steam Deck!**
