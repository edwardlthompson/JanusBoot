"""Bootable USB Tk panel (CLI-only writes)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from janusbootctl.linux_gui import usb_list_via_cli, usb_preview_via_cli

_USB = {
    "title": "Bootable USB",
    "empty": "No removable media. Insert a USB stick and refresh.",
    "preview": "Preview / dry-run",
    "write": "Write to USB",
    "refresh": "Refresh",
}


def build_usb_tab(frm: Any) -> None:
    import tkinter as tk
    from tkinter import messagebox, ttk

    iso_var = tk.StringVar(value="")
    mock_var = tk.StringVar(value="")
    status = tk.StringVar(value=_USB["empty"])
    listbox = tk.Listbox(frm, height=8, width=64)
    listbox.grid(row=0, column=0, columnspan=3, sticky="nsew", pady=4)
    devices: list[dict[str, Any]] = []

    def refresh() -> None:
        nonlocal devices
        listbox.delete(0, tk.END)
        mock = mock_var.get().strip()
        result = usb_list_via_cli(mock_json=Path(mock) if mock else None)
        if not result.ok:
            status.set(result.stderr or "usb list failed")
            return
        payload = json.loads(result.stdout or "{}")
        devices = list(payload.get("removable") or [])
        if not devices:
            status.set(_USB["empty"])
            return
        for d in devices:
            listbox.insert(tk.END, f"{d.get('path')} — {d.get('size_bytes')} B — {d.get('model')}")
        status.set(f"{len(devices)} removable target(s)")

    def preview() -> None:
        iso = iso_var.get().strip()
        sel = list(listbox.curselection())  # type: ignore[no-untyped-call]
        if not iso or not devices or not sel:
            messagebox.showinfo("JanusBoot", "Pick an ISO and a removable device first")
            return
        d = devices[int(sel[0])]
        result = usb_preview_via_cli(
            Path(iso),
            device=str(d["path"]),
            size_bytes=int(d["size_bytes"]),
            model=str(d["model"]),
            vendor=str(d.get("vendor") or ""),
            removable=True,
            tran="usb",
        )
        messagebox.showinfo(_USB["preview"], result.stdout or result.stderr)

    def write_guard() -> None:
        messagebox.showwarning(
            _USB["write"],
            "Destructive write is LOCAL + HUMAN only. Use Preview / dry-run here; "
            "real write needs a disposable stick and make usb-smoke.",
        )

    ttk.Label(frm, text="Rescue ISO path").grid(row=1, column=0, sticky="w")
    ttk.Entry(frm, textvariable=iso_var, width=40).grid(row=1, column=1, sticky="we")
    ttk.Label(frm, text="Mock devices JSON (optional)").grid(row=2, column=0, sticky="w")
    ttk.Entry(frm, textvariable=mock_var, width=40).grid(row=2, column=1, sticky="we")
    row = ttk.Frame(frm)
    row.grid(row=3, column=0, columnspan=3, sticky="we", pady=8)
    ttk.Button(row, text=_USB["refresh"], command=refresh).pack(side=tk.LEFT)
    ttk.Button(row, text=_USB["preview"], command=preview).pack(side=tk.LEFT, padx=8)
    ttk.Button(row, text=_USB["write"], command=write_guard).pack(side=tk.LEFT)
    ttk.Label(frm, textvariable=status, wraplength=480).grid(
        row=4, column=0, columnspan=3, sticky="w"
    )
    refresh()


USB_TAB_TITLE = _USB["title"]
