"""Write modifications back into extracted ESX JSON files and images."""

from __future__ import annotations

import os
import shutil
from typing import Any

import console
import json_io
from models import ApChange, Point


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_ap_changes(json_dir: str, changes: list[ApChange]) -> None:
    """Rename APs and/or update their coordinates from CSV data."""
    ap_json = json_io.load(json_dir, "accessPoints.json")

    change_by_name: dict[str, ApChange] = {c.name: c for c in changes}
    name_count = 0
    coord_count = 0

    for ap in ap_json["accessPoints"]:
        change = change_by_name.get(ap["name"])
        if change is None:
            continue

        if change.new_name:
            ap["name"] = change.new_name
            name_count += 1

        if (
            change.new_x is not None
            and change.new_y is not None
            and ap.get("location")
        ):
            ap["location"]["coord"]["x"] = change.new_x
            ap["location"]["coord"]["y"] = change.new_y
            coord_count += 1

    json_io.save(json_dir, "accessPoints.json", ap_json)
    console.ok(f"{console.green(name_count)} AP(s) changed names")
    console.ok(f"{console.green(coord_count)} AP(s) changed coordinates")


def update_ap_positions(
    json_dir: str, positions: dict[str, Point]
) -> None:
    """Overwrite AP x/y coordinates for the given AP names."""
    ap_json = json_io.load(json_dir, "accessPoints.json")

    for ap in ap_json["accessPoints"]:
        pos = positions.get(ap["name"])
        if pos is not None:
            ap["location"]["coord"]["x"] = pos.x
            ap["location"]["coord"]["y"] = pos.y

    json_io.save(json_dir, "accessPoints.json", ap_json)


def update_floor_plans(
    json_dir: str,
    floor_updates: dict[str, dict[str, Any]],
) -> None:
    """Update width, height, crop, and scaling on matched floors."""
    floor_json = json_io.load(json_dir, "floorPlans.json")

    for floor in floor_json["floorPlans"]:
        update = floor_updates.get(floor["name"])
        if update is None:
            continue
        floor["width"] = update["width"]
        floor["height"] = update["height"]
        floor["cropMaxX"] = update["width"]
        floor["cropMaxY"] = update["height"]
        floor["metersPerUnit"] = update["scaling"]

    json_io.save(json_dir, "floorPlans.json", floor_json)


def remove_reference_points(json_dir: str) -> None:
    path = os.path.join(json_dir, "referencePoints.json")
    if os.path.exists(path):
        os.remove(path)


def swap_images(
    project_dir: str,
    map_dir: str,
    image_mapping: dict[str, str],
) -> None:
    """Copy new map images over old ones, keyed by old_image_id -> new_image_id."""
    for old_id, new_id in image_mapping.items():
        old_path = os.path.join(project_dir, f"image-{old_id}")
        new_path = os.path.join(map_dir, f"image-{new_id}")
        if os.path.exists(old_path):
            os.remove(old_path)
        shutil.copy(new_path, old_path)
