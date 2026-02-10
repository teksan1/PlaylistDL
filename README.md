# PlaylistDL

PlaylistDL is a terminal-based music playlist downloader with interactive backup and restore functionality. It can find track lists, download audio from multiple sources (YouTube, SoundCloud), and manage your playlists.

---

## Features

- Download playlists from YouTube, SoundCloud, and other sources.
- Search and extract tracklists from URLs, descriptions, or comments.
- Backup & restore your PlaylistDL environment interactively.
- Multi-threaded downloading for faster performance.
- Fully interactive CLI with clear instructions.

---

## Requirements

- Termux (Android) or Linux/macOS terminal
- Python 3.10+
- Optional but recommended: rsync for fast backup/restore

Install dependencies:

\`\`\`bash
pkg update
pkg install python
pkg install rsync   # Termux only
pip install -r requirements.txt
\`\`\`

> Note: If rsync is not installed, backup-restore will fallback to Python copy functions (slower).

---

## Installation

Clone the repository:

\`\`\`bash
git clone https://github.com/YOUR_USERNAME/PlaylistDL.git
cd PlaylistDL
\`\`\`

Make scripts executable:

\`\`\`bash
chmod +x backup-restore
chmod +x startapp
\`\`\`

---

## Usage

### Launch the CLI

\`\`\`bash
./startapp
# Or using the global launcher if added to ~/bin/pldl
pldl
\`\`\`

This opens the interactive CLI to download playlists, search for tracks, and manage your library.

### Backup & Restore

\`\`\`bash
python3 backup-restore --backup   # Interactive backup
python3 backup-restore --restore  # Interactive restore
\`\`\`

- Full backup: backs up all app files except downloads/ and backups/.
- File/Folder backup: select individual files or folders.
- Restore: restore full backup or selected files/folders.

---

### Command-line Options

- --backup → Open backup workflow
- --restore → Open restore workflow
- -l → List available CLI options
- -d → Start download mode
- No flag → Interactive mode

---

## Directory Structure

\`\`\`
PlaylistDL/
├── ui/                # CLI interface
├── core/              # Core modules and pipeline
├── backups/           # Saved backups
├── downloads/         # Downloaded tracks
├── backup-restore     # Backup/Restore script
├── startapp           # Optional launcher
├── config.py          # Configurations
└── README.md          # Documentation
\`\`\`

---

## Contributing

1. Fork the repository
2. Create a branch (git checkout -b feature-name)
3. Make changes
4. Commit (git commit -am 'Add feature')
5. Push (git push origin feature-name)
6. Open a Pull Request

---

## License

MIT License – Free to use, modify, and distribute.
