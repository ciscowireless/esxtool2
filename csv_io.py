"""CSV import, export, and template generation."""

from __future__ import annotations

import csv
import os
from typing import Iterable

import console
from models import Ap, ApChange, Floor

_TEMPLATE_HEADER = ["AP Name", "New AP Name", "New Floor X", "New floor Y"]

_AP_COLUMNS = [
    "AP Name",
    "Floor",
    "Floor X",
    "Floor Y",
    "Ekahau AP Type",
    "Ekahau Colour",
    "Hidden",
    "Model",
    "MAC Address",
    "SSID",
]

_SLOT_COLUMNS = [
    "Slot",
    "Enabled",
    "Channel",
    "TxPower",
    "Height",
    "Tilt",
    "Direction",
    "Antenna",
]

_FLOOR_COLUMNS = [
    "Name",
    "ImageId",
    "Width",
    "Height",
    "Scaling (m/unit)",
    "ReferencePoints (x:y)",
]

_MAX_SLOTS = 4


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------

def export_aps(aps: list[Ap], output_dir: str, prefix: str) -> None:
    """Write AP data to a CSV file."""
    path = os.path.join(output_dir, _csv_name(prefix, "APs"))
    headings = _AP_COLUMNS + _SLOT_COLUMNS * _MAX_SLOTS

    if _write_csv(path, headings, (_ap_row(ap) for ap in aps)):
        console.ok(
            f"Exported {console.green(len(aps))} AP(s) to CSV: "
            f"{console.green(path)}"
        )


def export_floors(floors: list[Floor], output_dir: str, prefix: str) -> None:
    """Write floor/map data to a CSV file."""
    path = os.path.join(output_dir, _csv_name(prefix, "Floors"))

    if _write_csv(path, _FLOOR_COLUMNS, (_floor_row(f) for f in floors)):
        console.ok(
            f"Exported {console.green(len(floors))} floor(s) to CSV: "
            f"{console.green(path)}"
        )


def _ap_row(ap: Ap) -> list[object]:
    row: list[object] = [
        ap.name,
        ap.floor_name,
        ap.location.x if ap.location else "",
        ap.location.y if ap.location else "",
        ap.ekahau_type,
        ap.colour,
        ap.hidden,
        ap.model,
        ap.mac,
        ap.ssid,
    ]
    for idx in sorted(ap.slots):
        slot = ap.slots[idx]
        row += [
            slot.index,
            slot.enabled,
            slot.channel,
            slot.txpower,
            slot.antenna_height,
            slot.antenna_tilt,
            slot.antenna_direction,
            slot.antenna_type,
        ]
    return row


def _floor_row(floor: Floor) -> list[object]:
    return [
        floor.name,
        floor.image_id,
        floor.width,
        floor.height,
        floor.scaling,
        [[p.x, p.y] for p in floor.points],
    ]


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def read_ap_changes(csv_path: str) -> list[ApChange]:
    """Read AP rename / reposition data from a CSV template."""
    changes: list[ApChange] = []

    with open(csv_path, encoding="utf-8") as fh:
        reader = csv.reader(fh)
        for row in reader:
            if row == _TEMPLATE_HEADER:
                continue

            new_x: float | None = None
            new_y: float | None = None
            try:
                new_x = float(row[2])
                new_y = float(row[3])
            except (ValueError, IndexError):
                pass

            changes.append(ApChange(
                name=row[0],
                new_name=row[1] if len(row) > 1 else "",
                new_x=new_x,
                new_y=new_y,
            ))

    console.ok(f"Read {console.green(len(changes))} AP(s) from CSV")
    return changes


# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------

def generate_template(output_dir: str) -> None:
    """Create an empty CSV template for --fromcsv imports."""
    path = os.path.join(output_dir, "esxtool-template.csv")
    try:
        with open(path, "w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow(_TEMPLATE_HEADER)
    except PermissionError:
        console.error("Error creating CSV template")
        return

    console.ok(f"Created CSV template: {console.green(path)}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_csv(
    path: str,
    headings: list[str],
    rows: Iterable[list[object]],
) -> bool:
    """Write a header and rows to *path*. Returns False if the file is locked."""
    try:
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(headings)
            writer.writerows(rows)
    except PermissionError:
        console.error(f"Error writing to CSV file: {console.red(path)}")
        return False
    return True


def _csv_name(prefix: str, kind: str) -> str:
    stem = os.path.splitext(prefix)[0]
    return f"{stem}-{kind}.csv"
