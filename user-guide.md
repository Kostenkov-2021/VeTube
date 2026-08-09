# VeTube User Guide

**Complete guide to using VeTube** — Learn how to connect to live chats, customize text-to-speech, manage messages, and get the most out of VeTube.

## Table of Contents

- [Getting Started](#getting-started)
- [Connecting to a Chat](#connecting-to-a-chat)
- [Platform-Specific Guides](#platform-specific-guides)
- [Text-to-Speech Settings](#text-to-speech-settings)
- [Audio and Sound Settings](#audio-and-sound-settings)
- [Chat Features](#chat-features)
- [Managing Favorites](#managing-favorites)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## Getting Started

### First Launch

1. **Launch VeTube** from Start Menu or desktop shortcut
2. **Main window appears** with platform selector, text field, and control buttons
3. **Configure TTS** (optional but recommended) — see [Text-to-Speech Settings](#text-to-speech-settings)
4. **Connect to a chat** — see [Connecting to a Chat](#connecting-to-a-chat)

### Main Window Overview

```
┌─────────────────────────────────────────────────────────┐
│ VeTube                                                  │
├─────────────────────────────────────────────────────────┤
│ Capturar el chat de: [YouTube ▼]                       │
│ [https://www.youtube.com/@channel/live] [Conectar]     │
├─────────────────────────────────────────────────────────┤
│ [Tab 1: Chat] [Tab 2: Chat] [Tab 3: Chat]             │
│                                                         │
│ Chat messages appear here...                            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Key elements:**
- **Platform selector**: Choose which platform to connect to
- **Text field**: Enter channel URL or username
- **Connect button**: Start monitoring the chat
- **Chat tabs**: Multiple chats can be open simultaneously

---

## Connecting to a Chat

### Basic Connection

1. **Select platform** from the dropdown menu
2. **Enter channel information** in the text field:
   - Full URL: `https://www.youtube.com/@channel/live`
   - Username: `@channel` or just `channel`
3. **Press Enter** or click **Connect**
4. **Chat window opens** and messages start appearing

### Multiple Chats

You can monitor multiple chats simultaneously:

1. Connect to first chat
2. **Without closing**, enter new channel and connect
3. **New tab opens** for the second chat
4. **Switch between tabs** to view different chats
5. **Close individual tabs** to stop monitoring specific chats

---

## Platform-Specific Guides

### YouTube

**Supported URL formats:**
- Full URL: `https://www.youtube.com/@channel/live`
- Short URL: `https://youtu.be/VIDEO_ID`
- Username: `@channel` or `channel`

**Features:**
- Real-time chat messages
- Member notifications
- Super Chat and donations
- Moderator actions

**Example:**
```
@lirik
https://www.youtube.com/@xqc/live
```

### Twitch

**Supported URL formats:**
- Full URL: `https://www.twitch.tv/channel`
- Username: `channel`

**Features:**
- Real-time chat messages
- Subscriptions and bits
- Raid notifications
- Emotes (displayed as text)

**Example:**
```
shroud
https://www.twitch.tv/sodapoppin
```

### TikTok

**Supported URL formats:**
- Full URL: `https://www.tiktok.com/@username/live`
- Short URL: `https://vm.tiktok.com/CODE`
- Username: `@username`

**Features:**
- Real-time chat messages
- Gifts and donations
- New followers
- Share notifications
- Like notifications

**Special notes:**
- TikTok live URLs may need to be simplified
- VeTube automatically handles URL conversion
- Some TikTok lives may not be accessible depending on region

**Example:**
```
@khaby.lame
https://www.tiktok.com/@charlidamelio/live
```

### Kick

**Supported URL formats:**
- Full URL: `https://www.kick.com/channel`
- Username: `channel`

**Features:**
- Real-time chat messages
- Bypass system for chat access
- Member notifications
- Gift notifications

**Special notes:**
- Kick requires a bypass executable (`bypass64.exe`)
- The bypass runs automatically when connecting
- If bypass fails, check logs for errors

**Example:**
```
xqc
https://www.kick.com/adin
```

### Discord

**Supported URL formats:**
- Text channel URL: Right-click channel → Copy Link

**Requirements:**
1. **Discord bot token** required (set in settings)
2. Bot must be invited to the server
3. Bot needs "Read Messages" permission

**Setup:**
1. Go to **Settings** → **Discord**
2. Enter your bot token
3. Copy text channel URL from Discord
4. Paste URL in VeTube and connect

**Features:**
- Real-time messages from Discord channels
- Works with any server where bot is present
- Supports multiple Discord servers simultaneously

**Example:**
```
https://discord.com/channels/SERVER_ID/CHANNEL_ID
```

### La sala de juegos

**Special platform** — No URL required

**How to use:**
1. Select **"La sala de juegos"** from platform dropdown
2. **Leave text field empty**
3. **Press Enter** or click Connect
4. VeTube automatically detects the game process

**Features:**
- Automatic process detection
- In-game chat capture
- Works with supported games

**Troubleshooting:**
- Ensure the game is running before connecting
- Some games may require running as administrator
- Check logs if detection fails

---

## Text-to-Speech Settings

VeTube supports three TTS engines:

### Piper TTS (Recommended)

**High-quality neural voices** — Best quality, requires voice downloads

**Setup:**
1. Go to **Settings** → **TTS**
2. Select **Piper** as TTS engine
3. Click **Download voices** to get voice packs
4. Select desired voice from dropdown

**Features:**
- Natural-sounding voices
- Multiple languages
- Customizable speed, pitch, and volume
- Low CPU usage

**Voice management:**
- Downloaded voices appear in voice list
- Delete unused voices to save space
- Voices are stored in `voices/` directory

### Windows OneCore

**Built-in Windows voices** — Good quality, no downloads needed

**Setup:**
1. Go to **Settings** → **TTS**
2. Select **OneCore** as TTS engine
3. Choose from available Windows voices

**Features:**
- Uses Windows built-in voices
- No additional downloads
- Works out of the box
- Moderate quality

**Available voices:**
- Depends on your Windows installation
- Additional voices can be added via Windows Settings

### SAPI5

**Legacy Windows TTS** — Basic quality, maximum compatibility

**Setup:**
1. Go to **Settings** → **TTS**
2. Select **SAPI5** as TTS engine
3. Choose from available SAPI voices

**Features:**
- Maximum compatibility
- Works on all Windows versions
- Lower quality than Piper/OneCore
- Very low resource usage

### Common TTS Settings

**Speed**: Adjust speech rate (0.5x to 2.0x)

**Pitch**: Adjust voice pitch (lower to higher)

**Volume**: Adjust output volume (0% to 100%)

**Voice selection**: Choose specific voice for TTS engine

**Device selection**: Choose audio output device (speakers, headphones, etc.)

---

## Audio and Sound Settings

### Sound Effects

VeTube plays sound effects for various events:

**Available sounds:**
- Chat message received
- New member joined
- Donation/Super Chat
- Moderator action
- Verified user message
- Owner message
- Share/Follow/Like notifications
- And more...

**Customization:**
1. Go to **Settings** → **Sounds**
2. **Enable/disable** sound effects globally
3. **Toggle individual sounds** on/off
4. **Choose sound theme** (if multiple available)

**Sound themes:**
- Located in `sounds/` directory
- Each theme is a subdirectory with sound files
- Required sounds: `chat.mp3`, `chatmiembro.mp3`, `miembros.mp3`, etc.
- Custom themes can be added

### Audio Output Device

**Select output device:**
1. Go to **Settings** → **Audio**
2. Choose from available devices
3. Test with "Test" button

**Device list:**
- Shows all available audio output devices
- Includes speakers, headphones, USB audio devices
- Bluetooth devices are supported

**Troubleshooting:**
- If device disappears, reconnect and restart VeTube
- Default device is used if selected device is unavailable
- Device index is saved in configuration

---

## Chat Features

### Message Filtering

**Filter by type:**
- All messages
- Members only
- Moderators only
- Verified users
- Owners

**How to filter:**
1. Open chat window
2. Click **Filter** button
3. Select filter type
4. Chat updates to show only matching messages

### Message Archiving

**Save important messages:**

**Archive a message:**
1. Right-click on message
2. Select **Archive message**
3. Message is saved to archive
4. Access archive from menu

**View archived messages:**
1. Go to **Messages** → **Archived**
2. List of all archived messages appears
3. Click to view full message

**Delete archived messages:**
- Individual: Right-click → Delete
- All: Click **Clear all** button

### Highlighted Messages

**Mark messages as important:**

**Highlight a message:**
1. Right-click on message
2. Select **Highlight**
3. Message appears in highlighted list

**View highlighted messages:**
1. Go to **Messages** → **Highlighted**
2. List of all highlighted messages

### Chat Statistics

**Real-time statistics:**
- Total messages
- Members count
- Donations/Super Chats
- New followers
- Shares
- Likes

**View statistics:**
1. Open chat window
2. Click **Statistics** button
3. Detailed stats panel appears

**Export statistics:**
- Statistics are saved automatically
- Access from **Statistics** menu
- Data stored in `data.json`

---

## Managing Favorites

### Adding Favorites

**Save a channel for quick access:**

1. Connect to a chat
2. Click **Add to favorites** button
3. Channel is saved with current settings

**Or manually:**
1. Go to **Favorites** → **Add new**
2. Enter channel URL
3. Select platform
4. Click **Save**

### Using Favorites

**Quick connect:**
1. Go to **Favorites** menu
2. Select channel from list
3. VeTube connects automatically

**Manage favorites:**
- **Edit**: Change channel URL or platform
- **Delete**: Remove from favorites
- **Reorder**: Drag and drop to reorder

### Favorites Storage

Favorites are stored in `favoritos.json`:
- Automatically saved when modified
- Backed up with your configuration
- Can be manually edited (JSON format)

---

## Keyboard Shortcuts

### Global Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Connect to chat (when text field focused) |
| `Ctrl+P` | Pause/resume all TTS |
| `Ctrl+Q` | Quit application |
| `Ctrl+W` | Close current chat tab |
| `Ctrl+Tab` | Switch to next chat tab |
| `Ctrl+Shift+Tab` | Switch to previous chat tab |

### Chat Window Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Open filter dialog |
| `Ctrl+S` | Open statistics |
| `Ctrl+A` | Archive selected message |
| `Ctrl+H` | Highlight selected message |
| `Delete` | Delete selected message |

### Navigation

| Shortcut | Action |
|----------|--------|
| `Tab` | Move focus to next control |
| `Shift+Tab` | Move focus to previous control |
| `Arrow Up/Down` | Navigate message list |
| `Home` | Go to first message |
| `End` | Go to last message |
| `Page Up` | Scroll up one page |
| `Page Down` | Scroll down one page |

---

## Troubleshooting

### Common Issues

#### App won't start

**Symptoms:** Application closes immediately or shows error

**Solutions:**
1. Check `logs/vetube.log` for error details
2. Ensure all dependencies are installed
3. Try running from command line: `uv run python run_main_window.py`
4. Reinstall VeTube

#### No sound

**Symptoms:** Messages appear but no TTS audio

**Solutions:**
1. Check audio device is selected in settings
2. Verify system volume is not muted
3. Test TTS with "Test" button in settings
4. Try different TTS engine (Piper/OneCore/SAPI5)
5. Check audio device hasn't been disconnected

#### Chat not connecting

**Symptoms:** "Connecting..." but messages never appear

**Solutions:**
1. Verify channel URL is correct
2. Check internet connection
3. Ensure channel is live (not offline)
4. Try different platform to isolate issue
5. Check logs for specific error messages

#### Kick bypass fails

**Symptoms:** "Error al iniciar bypass" for Kick

**Solutions:**
1. Ensure `bypass64.exe` exists in `64/` directory
2. Try running VeTube as administrator
3. Check antivirus isn't blocking bypass
4. Review logs for specific error
5. Reinstall VeTube to restore bypass files

#### TTS voices not working

**Symptoms:** Voice selection doesn't change or no voices available

**Solutions:**
1. **Piper**: Download voice packs from settings
2. **OneCore**: Check Windows voice settings
3. **SAPI5**: Verify SAPI voices are installed
4. Restart VeTube after voice changes
5. Check `voices/` directory for Piper voices

#### Compiled app crashes

**Symptoms:** Works in development but crashes when compiled

**Solutions:**
1. Check `logs/vetube.log` for error details
2. Ensure all resources are included in build
3. Verify paths use `globals/paths.py`
4. Check for missing DLLs or executables
5. Rebuild with `uv run cxfreeze build`

### Getting Help

**If issue persists:**

1. **Check logs**: `logs/vetube.log` contains detailed error information
2. **Search issues**: [GitHub Issues](https://github.com/metalalchemist/VeTube/issues)
3. **Ask in discussions**: [GitHub Discussions](https://github.com/metalalchemist/VeTube/discussions)
4. **Report bug**: Use [bug report template](contributing.md#reporting-bugs)

---

## FAQ

### General Questions

**Q: Is VeTube free?**
A: Yes, VeTube is completely free and open-source under the MIT license.

**Q: What platforms does VeTube support?**
A: YouTube, Twitch, TikTok, Kick, Discord, and "La sala de juegos".

**Q: Can I use VeTube on Mac or Linux?**
A: Currently, VeTube is Windows-only. There are no plans for Mac/Linux support at this time.

**Q: Do I need a powerful computer?**
A: No, VeTube is lightweight and runs on most Windows 10+ systems.

### TTS Questions

**Q: Which TTS engine is best?**
A: Piper offers the best quality, OneCore is a good balance, and SAPI5 has maximum compatibility.

**Q: Can I use custom voices?**
A: Yes, for Piper you can download additional voice packs. For OneCore/SAPI5, install voices via Windows settings.

**Q: Why is TTS slow?**
A: Try reducing speed in settings, or switch to a different TTS engine.

### Chat Questions

**Q: Can I monitor multiple chats at once?**
A: Yes, each chat opens in a new tab.

**Q: Are messages saved?**
A: Only messages you explicitly archive or highlight are saved. Regular messages are not stored.

**Q: Can I export chat messages?**
A: Currently, only archived and highlighted messages can be exported via the statistics system.

### Technical Questions

**Q: How do I update VeTube?**
A: If installed via Scoop: `scoop update vetube`. Otherwise, download the latest release.

**Q: Where is my configuration stored?**
A: In `data.json` in the VeTube installation directory.

**Q: Can I backup my settings?**
A: Yes, backup `data.json`, `favoritos.json`, and the `voices/` directory.

**Q: How do I uninstall VeTube?**
A: If installed via Scoop: `scoop uninstall vetube`. Otherwise, use Windows "Add or Remove Programs".

---

## Additional Resources

- **[Contributing Guide](contributing.md)** — How to contribute to VeTube
- **[Release Notes](release-notes.md)** — Version history and changelog
- **[GitHub Repository](https://github.com/metalalchemist/VeTube)** — Source code and issues
- **[Report a Bug](https://github.com/metalalchemist/VeTube/issues/new)** — Report issues
- **[Ask a Question](https://github.com/metalalchemist/VeTube/discussions)** — Community discussions

---

**Need more help?** Check the [Troubleshooting](#troubleshooting) section or [ask in discussions](https://github.com/metalalchemist/VeTube/discussions).
