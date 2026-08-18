#!/usr/bin/env python
"""Test script for release notes dialog."""

import wx

from update.release_notes_dialog import show_release_notes_dialog


def main():
    """Test the release notes dialog."""
    app = wx.App()

    # Sample release notes in markdown format
    sample_notes = """## What's New in Version 3.95-rc5

### 🚀 New Features

* **Update Channel Selector**: You can now choose between Stable and Beta update channels
  * Stable: Only official releases
  * Beta: Includes pre-releases and early features
* **Formatted Release Notes**: Release notes are now displayed in a beautiful formatted dialog
* **Improved Error Handling**: Better error messages when updates fail

### 🐛 Bug Fixes

* Fixed version parsing error (BOM issue in VERSION file)
* Fixed update channel not being respected during auto-check
* Fixed development mode detection to prevent accidental updates

### 📝 Documentation

* Updated README with new features
* Added troubleshooting guide for common update issues

### 🔧 Technical Changes

* Migrated to GitHub Releases API for update detection
* Added SHA256 checksum verification for security
* Implemented automatic backup before updates

---

**Full Changelog**: https://github.com/metalalchemist/VeTube/compare/v3.94...v3.95-rc5

For more information, visit our [GitHub repository](https://github.com/metalalchemist/VeTube).
"""

    # Show the dialog
    result = show_release_notes_dialog(None, "3.95-rc5", sample_notes)

    if result:
        print("User clicked 'Update Now'")
    else:
        print("User clicked 'Later' or closed the dialog")

    app.MainLoop()


if __name__ == "__main__":
    main()
