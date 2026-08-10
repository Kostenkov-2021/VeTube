# Release Notes

**Version history and changelog for VeTube** — Track what's new, what's fixed, and what's changed in each release.

---

## [v3.94] - 2025

### 🚀 New Features
- **GitHub Actions workflow for WinGet publishing** — Automated publishing to WinGet package manager

### 🐛 Bug Fixes
- **Fix silent failures in settings** — Corrected two silent failures found during code review of PR #91
- **Cancel/Escape in Settings reverts hot-applied changes** — Pressing Cancel or Escape now properly reverts changes made during the session
- **Fix TikTok history filter and username calculation** — Avoided calculating username twice in `on_follow` event
- **Fix duplicate AjustesController instantiation** — Removed duplicate controller instance
- **Thread safety improvements** — Wrapped remaining UI/reader/player calls in `wx.CallAfter` for Twitch, Sala, and YouTube services

### 🔧 Improvements
- Code quality improvements from canary branch integration
- Better error handling in settings dialog

### 👥 Contributors
- @enzowenterstein-collab — Settings fixes, TikTok improvements, thread safety
- @metalalchemist — Canary integration, WinGet workflow

---

## [v3.93] - 2025

### 🔧 Improvements
- Testing and validation improvements
- Stability enhancements

### 👥 Contributors
- @metalalchemist

---

## [v3.92] - 2025

### 🚀 New Features
- **Central logging system** — New centralized logging with unhandled error capture
- **Service logging migration** — All services now use the logging system instead of `print()` statements

### 🐛 Bug Fixes
- **Fix audio device disappearing** — Returns to first audio device when saved device no longer exists
- **Fix Kick asyncio loop close condition** — Corrected inverted condition when closing Kick's asyncio loop
- **Accessibility robustness improvements** — Minor corrections to accessibility features

### 🔧 Improvements
- Root log level set to INFO, VeTube modules to DEBUG
- Enhanced service logging after auto-review
- Better error reporting and diagnostics

### 👥 Contributors
- @enzowenterstein-collab — Logging system, audio device fix, Kick fix, accessibility
- @metalalchemist — Integration and review

---

## [v3.91] - 2025

### 🚀 New Features
- **Canary integration** — Major integration of canary branch features

### 🔧 Improvements
- Stability and performance improvements
- Code consolidation from canary branch

### 👥 Contributors
- @metalalchemist

---

## [v3.9] - 2025

### 🚀 New Features
- Platform improvements and new features

### 🐛 Bug Fixes
- Various bug fixes and stability improvements

### 👥 Contributors
- @metalalchemist
- @enzowenterstein-collab

---

## [v3.8] - 2025

### 🚀 New Features
- Enhanced chat monitoring capabilities

### 🐛 Bug Fixes
- Bug fixes for platform integrations

### 👥 Contributors
- @metalalchemist

---

## [v3.7] - 2025

### 🚀 New Features
- New platform support and features

### 🐛 Bug Fixes
- Stability improvements

### 👥 Contributors
- @metalalchemist

---

## [v3.6] - 2025

### 🚀 New Features
- TTS improvements

### 🐛 Bug Fixes
- Bug fixes and performance enhancements

### 👥 Contributors
- @metalalchemist

---

## [v3.5] - 2025

### 🚀 New Features
- UI improvements

### 🐛 Bug Fixes
- Various bug fixes

### 👥 Contributors
- @metalalchemist

---

## [v3.4] - 2025

### 🚀 New Features
- New features and enhancements

### 🐛 Bug Fixes
- Bug fixes

### 👥 Contributors
- @metalalchemist

---

## [v3.3] - 2025

### 🚀 New Features
- Feature additions

### 🐛 Bug Fixes
- Bug fixes

### 👥 Contributors
- @metalalchemist

---

## [v3.2] - 2025

### 🚀 New Features
- New capabilities

### 🐛 Bug Fixes
- Fixes and improvements

### 👥 Contributors
- @metalalchemist

---

## [v3.1] - 2025

### 🚀 New Features
- Initial 3.x features

### 🐛 Bug Fixes
- Bug fixes

### 👥 Contributors
- @metalalchemist

---

## [v3.0] - 2025

### 🚀 Major Release
- **Major version upgrade** — Significant architectural changes
- New features and improvements

### 🐛 Bug Fixes
- Comprehensive bug fixes

### 👥 Contributors
- @metalalchemist

---

## [v2.x] - Historical

Versions 2.x represent the earlier development of VeTube with foundational features:

- Multi-platform chat monitoring
- Text-to-speech integration
- Basic UI and settings
- Sound effects and customization

---

## Release Categories

### 🚀 New Features
New functionality, platform support, or major enhancements.

### 🐛 Bug Fixes
Corrections to existing functionality that was broken or not working as expected.

### 🔧 Improvements
Enhancements to existing features, performance improvements, code quality, and refactoring.

### ⚠️ Breaking Changes
Changes that may require user action or affect compatibility.

### 📦 Dependencies
Updates to third-party libraries and dependencies.

---

## How to Update

### Scoop (Recommended)
```powershell
scoop update vetube
```

### Manual Installation
Download the latest MSI installer from the [Releases page](https://github.com/metalalchemist/VeTube/releases).

---

## Stay Informed

- **GitHub Releases**: [github.com/metalalchemist/VeTube/releases](https://github.com/metalalchemist/VeTube/releases)
- **GitHub Discussions**: [github.com/metalalchemist/VeTube/discussions](https://github.com/metalalchemist/VeTube/discussions)
- **Issue Tracker**: [github.com/metalalchemist/VeTube/issues](https://github.com/metalalchemist/VeTube/issues)

---

**Note**: For detailed technical changes, see the [commit history](https://github.com/metalalchemist/VeTube/commits/main).
