# Solana Sniper Bot - Desktop Application

Electron-based desktop wrapper for the Solana Sniper Bot.

## Features

- Native desktop application (Windows, macOS, Linux)
- Auto-starts backend server
- System tray integration
- Native notifications
- Auto-updates (configurable)

## Prerequisites

- Node.js 18+
- Python 3.9+
- Frontend built (`npm run build` in frontend/)

## Development

```bash
# Install dependencies
npm install

# Run in development mode
npm start
```

## Building

### Windows
```bash
npm run build:win
```
Output: `dist/Solana Sniper Bot Setup.exe`

### macOS
```bash
npm run build:mac
```
Output: `dist/Solana Sniper Bot.dmg`

### Linux
```bash
npm run build:linux
```
Output: `dist/Solana Sniper Bot.AppImage`

## Build All Platforms
```bash
npm run build
```

## Distribution

The built applications are in the `dist/` directory:
- Windows: `.exe` installer
- macOS: `.dmg` disk image
- Linux: `.AppImage` executable

## Configuration

Edit `package.json` to customize:
- App name
- App ID
- Icons
- Build targets

## Notes

- Backend starts automatically on port 8000
- Frontend is bundled from `../frontend/dist`
- Python backend must be installed with dependencies
- First run may take longer while backend initializes

## Troubleshooting

### Backend won't start
- Check Python installation: `python3 --version`
- Install backend dependencies: `cd ../backend && pip install -r requirements.txt`

### Build fails
- Ensure frontend is built: `cd ../frontend && npm run build`
- Check Node.js version: `node --version` (should be 18+)

### App won't launch
- Check console logs for errors
- Verify all dependencies are installed
- Try running in development mode first

## File Structure

```
desktop/
├── main.js           # Electron main process
├── preload.js        # Preload script for security
├── package.json      # Electron config
└── assets/           # App icons
    ├── icon.ico      # Windows icon
    ├── icon.icns     # macOS icon
    └── icon.png      # Linux icon
```

## License

MIT
