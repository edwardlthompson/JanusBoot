"""Windows Tk surface (elevation-gated)."""

from __future__ import annotations

from pathlib import Path

from janusbootctl.gui_usb import USB_TAB_TITLE, build_usb_tab
from janusbootctl.linux_gui import install_dry_run_via_cli, set_timeout_via_cli
from janusbootctl.windows_gui import ELEVATION_WARNING, is_elevated, windows_gui_snapshot


def launch_windows_tk(esp: Path) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
    except ModuleNotFoundError as exc:
        raise RuntimeError("tkinter unavailable; install python3-tk") from exc

    state = windows_gui_snapshot(esp)
    root = tk.Tk()
    root.title("JanusBoot (Windows)")
    root.minsize(560, 520)
    nb = ttk.Notebook(root)
    nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
    main = ttk.Frame(nb, padding=12)
    usb = ttk.Frame(nb, padding=12)
    nb.add(main, text="Entries")
    nb.add(usb, text=USB_TAB_TITLE)
    tk.Label(main, text=state.warning, wraplength=480, fg="darkred", justify=tk.LEFT).pack(
        anchor="w", pady=(0, 8)
    )
    elev = tk.StringVar(
        value="Elevated: yes" if state.elevated else "Elevated: NO — writes blocked"
    )
    ttk.Label(main, textvariable=elev).pack(anchor="w")
    listbox = tk.Listbox(main, height=10, width=64)
    listbox.pack(fill=tk.BOTH, expand=True, pady=8)
    for entry in state.entries:
        listbox.insert(tk.END, f"{entry.get('title')} — {entry.get('id')}")
    timeout_var = tk.StringVar(value="5")

    def guard() -> bool:
        if is_elevated():
            return True
        messagebox.showerror("JanusBoot", ELEVATION_WARNING)
        return False

    def on_timeout() -> None:
        if not guard():
            return
        result = set_timeout_via_cli(esp, int(timeout_var.get()))
        messagebox.showinfo("JanusBoot", result.stdout or result.stderr or "ok")

    def on_install() -> None:
        if not guard():
            return
        result = install_dry_run_via_cli(esp)
        messagebox.showinfo("Install dry-run", result.stdout or result.stderr)

    row = ttk.Frame(main)
    row.pack(fill=tk.X, pady=8)
    ttk.Label(row, text="Timeout").pack(side=tk.LEFT)
    ttk.Entry(row, textvariable=timeout_var, width=8).pack(side=tk.LEFT, padx=6)
    ttk.Button(row, text="Apply timeout", command=on_timeout).pack(side=tk.LEFT)
    ttk.Button(main, text="Install (dry-run)", command=on_install).pack(anchor="w")
    build_usb_tab(usb)
    root.mainloop()
