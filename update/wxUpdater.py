# -*- coding: utf-8 -*-
import wx
from . import utils
from .channel import get_channel, set_channel

progress_dialog = None
backup_dialog = None


def channel_selection_dialog() -> bool:
    """Show a dialog for selecting the update channel (stable or beta).

    Returns:
        True if the user clicked OK, False if cancelled.
    """
    current = get_channel()

    dlg = wx.Dialog(None, title=_(u"Update Channel"), size=(420, 260))
    vbox = wx.BoxSizer(wx.VERTICAL)

    header = wx.StaticText(
        dlg, label=_(u"Choose which updates you want to receive:")
    )
    header.SetFont(header.GetFont().Bold())
    vbox.Add(header, 0, wx.ALL | wx.EXPAND, 12)

    radio_stable = wx.RadioButton(
        dlg, label=_(u"Stable"), style=wx.RB_GROUP
    )
    vbox.Add(radio_stable, 0, wx.LEFT | wx.RIGHT, 24)
    desc_stable = wx.StaticText(
        dlg, label=_(u"Only official releases. Recommended for most users.")
    )
    desc_stable.SetForegroundColour(wx.Colour(100, 100, 100))
    vbox.Add(desc_stable, 0, wx.LEFT | wx.BOTTOM, 24)

    radio_beta = wx.RadioButton(dlg, label=_(u"Beta"))
    vbox.Add(radio_beta, 0, wx.LEFT | wx.RIGHT, 24)
    desc_beta = wx.StaticText(
        dlg,
        label=_(u"Includes pre-releases and early features. May be unstable."),
    )
    desc_beta.SetForegroundColour(wx.Colour(100, 100, 100))
    vbox.Add(desc_beta, 0, wx.LEFT | wx.BOTTOM, 24)

    if current == "beta":
        radio_beta.SetValue(True)
    else:
        radio_stable.SetValue(True)

    btn_sizer = dlg.CreateButtonSizer(wx.OK | wx.CANCEL)
    vbox.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 12)

    dlg.SetSizer(vbox)

    if dlg.ShowModal() == wx.ID_OK:
        chosen = "beta" if radio_beta.GetValue() else "stable"
        set_channel(chosen)
        dlg.Destroy()
        return True

    dlg.Destroy()
    return False


def backup_progress_callback(current: int, total: int) -> None:
    """Update backup progress dialog.

    Args:
        current: Number of files processed so far.
        total: Total number of files to back up.
    """
    global backup_dialog

    def _update():
        global backup_dialog
        if backup_dialog is None:
            backup_dialog = wx.ProgressDialog(
                _(u"Backup"),
                _(u"Creating backup..."),
                maximum=max(total, 1),
                parent=None,
                style=wx.PD_CAN_ABORT | wx.PD_APP_MODAL,
            )
            backup_dialog.Show()

        if current >= total:
            backup_dialog.Destroy()
            backup_dialog = None
        else:
            pct = int((current * 100) / max(total, 1))
            backup_dialog.Update(
                current, _(u"Creating backup... %d%%") % pct
            )

    wx.CallAfter(_update)


def rollback_notification(reason: str) -> None:
    """Show a warning dialog informing the user that a rollback is happening.

    Args:
        reason: Description of why the update failed.
    """

    def _show():
        wx.MessageDialog(
            None,
            _(
                u"Update failed: %s\n\n"
                u"Rolling back to the previous version. "
                u"Your data is safe."
            )
            % reason,
            _(u"Update Failed — Rolling Back"),
            style=wx.OK | wx.ICON_WARNING,
        ).ShowModal()

    wx.CallAfter(_show)


def checking_updates_dialog() -> wx.ProgressDialog:
    """Create and show an indeterminate progress dialog for update checks.

    Returns:
        The dialog instance. Caller must call ``Destroy()`` when done.
    """
    dlg = wx.ProgressDialog(
        _(u"Checking for Updates"),
        _(u"Connecting to update server..."),
        parent=None,
        style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE,
    )
    dlg.Pulse()
    dlg.Show()
    return dlg


def no_updates_dialog(version: str) -> None:
    """Inform the user they are running the latest version.

    Args:
        version: The current version string.
    """

    def _show():
        ch = get_channel().capitalize()
        wx.MessageDialog(
            None,
            _(u"You are running the latest version (v%s) — %s channel.")
            % (version, ch),
            _(u"No Updates Available"),
            style=wx.OK | wx.ICON_INFORMATION,
        ).ShowModal()

    wx.CallAfter(_show)


def available_update_dialog(version, description):
    ch = get_channel().capitalize()
    dialog = wx.MessageDialog(
        None,
        _(
            u"New version available for %s channel.\n\n"
            u"VeTube version: %s\n\n"
            u"Would you like to download it now?\n\n"
            u"Changes:\n%s"
        )
        % (ch, version, description),
        _(u"New VeTube Version"),
        style=wx.YES | wx.NO | wx.ICON_WARNING,
    )
    if dialog.ShowModal() == wx.ID_YES:
        return True
    else:
        return False


def create_progress_dialog():
    return wx.ProgressDialog(
        _(u"Download in Progress"),
        _(u"Downloading update..."),
        parent=None,
        maximum=100,
    )


def progress_callback(total_downloaded, total_size):
    global progress_dialog

    def update_ui():
        global progress_dialog
        if progress_dialog is None:
            progress_dialog = create_progress_dialog()
            progress_dialog.Show()
        if total_downloaded == total_size:
            progress_dialog.Destroy()
            progress_dialog = None
        else:
            pct = int((total_downloaded * 100) / total_size)
            progress_dialog.Update(
                pct,
                _(u"Downloading... %s of %s")
                % (
                    str(utils.convert_bytes(total_downloaded)),
                    str(utils.convert_bytes(total_size)),
                ),
            )

    wx.CallAfter(update_ui)


def update_finished():
    def show_msg():
        wx.MessageDialog(
            None,
            _(
                u"The update has been downloaded and installed successfully. "
                u"Click OK to continue."
            ),
            _(u"Done!"),
        ).ShowModal()

    wx.CallAfter(show_msg)
