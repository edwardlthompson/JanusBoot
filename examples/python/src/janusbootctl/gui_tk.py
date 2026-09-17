"""Tk launchers (optional host dependency: python3-tk)."""

from __future__ import annotations

import json
from pathlib import Path

from janusbootctl.linux_gui import (
    install_dry_run_via_cli,
    list_entries_via_cli,
    set_theme_via_cli,
    set_timeout_via_cli,
)
from janusbootctl.windows_gui import ELEVATION_WARNING, is_elevated, windows_gui_snapshot


def launch_linux_gui(esp: Path) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
    except ModuleNotFoundError as exc:
        raise RuntimeError("tkinter unavailable; install python3-tk") from exc

    root = tk.Tk()
    root.title("JanusBoot")
    root.minsize(520, 420)
    status = tk.StringVar(value="Ready")
    timeout_var = tk.StringVar(value="5")
    theme_var = tk.StringVar(value="")
    frm = ttk.Frame(root, padding=12)
    frm.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    ttk.Label(frm, text="Boot entries (via janusbootctl)").grid(row=0, column=0, sticky="w")
    listbox = tk.Listbox(frm, height=12, width=64)
    listbox.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=8)

    def refresh() -> None:
        listbox.delete(0, tk.END)
        try:
            for entry in list_entries_via_cli(esp):
                listbox.insert(tk.END, f"{entry.get('title')} — {entry.get('id')}")
            status.set(f"Loaded {listbox.size()} entries")
        except (OSError, RuntimeError, json.JSONDecodeError) as err:
            status.set(f"Error: {err}")
            messagebox.showerror("JanusBoot", str(err))

    def on_timeout() -> None:
        try:
            seconds = int(timeout_var.get().strip())
        except ValueError:
            messagebox.showerror("JanusBoot", "Timeout must be an integer")
            return
        result = set_timeout_via_cli(esp, seconds)
        status.set("Timeout updated" if result.ok else result.stderr)

    def on_theme() -> None:
        path = theme_var.get().strip()
        if not path:
            messagebox.showinfo("JanusBoot", "Set a theme directory path first")
            return
        result = set_theme_via_cli(esp, Path(path))
        status.set("Theme applied" if result.ok else result.stderr)

    def on_install_dry() -> None:
        result = install_dry_run_via_cli(esp)
        messagebox.showinfo("Install dry-run", result.stdout or result.stderr or "ok")

    ttk.Label(frm, text="Timeout (seconds)").grid(row=2, column=0, sticky="w")
    ttk.Entry(frm, textvariable=timeout_var, width=8).grid(row=2, column=1, sticky="w")
    ttk.Button(frm, text="Apply timeout", command=on_timeout).grid(row=2, column=2, sticky="e")
    ttk.Label(frm, text="Theme pack dir").grid(row=3, column=0, sticky="w", pady=(8, 0))
    ttk.Entry(frm, textvariable=theme_var, width=40).grid(row=3, column=1, sticky="we", pady=(8, 0))
    ttk.Button(frm, text="Apply theme", command=on_theme).grid(
        row=3, column=2, sticky="e", pady=(8, 0)
    )
    btns = ttk.Frame(frm)
    btns.grid(row=4, column=0, columnspan=3, sticky="we", pady=12)
    ttk.Button(btns, text="Refresh", command=refresh).pack(side=tk.LEFT)
    ttk.Button(btns, text="Install (dry-run)", command=on_install_dry).pack(side=tk.LEFT, padx=8)
    ttk.Label(frm, textvariable=status).grid(row=5, column=0, columnspan=3, sticky="w")
    refresh()
    root.mainloop()


def launch_windows_gui(esp: Path) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
    except ModuleNotFoundError as exc:
        raise RuntimeError("tkinter unavailable; install python3-tk") from exc

    state = windows_gui_snapshot(esp)
    root = tk.Tk()
    root.title("JanusBoot (Windows)")
    root.minsize(520, 440)
    frm = ttk.Frame(root, padding=12)
    frm.pack(fill=tk.BOTH, expand=True)
    tk.Label(frm, text=state.warning, wraplength=480, fg="darkred", justify=tk.LEFT).pack(
        anchor="w", pady=(0, 8)
    )
    elev = tk.StringVar(
        value="Elevated: yes" if state.elevated else "Elevated: NO — writes blocked"
    )
    ttk.Label(frm, textvariable=elev).pack(anchor="w")
    listbox = tk.Listbox(frm, height=12, width=64)
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

    row = ttk.Frame(frm)
    row.pack(fill=tk.X, pady=8)
    ttk.Label(row, text="Timeout").pack(side=tk.LEFT)
    ttk.Entry(row, textvariable=timeout_var, width=8).pack(side=tk.LEFT, padx=6)
    ttk.Button(row, text="Apply timeout", command=on_timeout).pack(side=tk.LEFT)
    ttk.Button(frm, text="Install (dry-run)", command=on_install).pack(anchor="w")
    root.mainloop()
