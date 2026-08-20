"""Read and write the JSON files inside an extracted ESX project."""

from __future__ import annotations

import json
import os
from typing import Any

import console


def load(json_dir: str, filename: str) -> dict[str, Any]:
    """Load a required JSON file from an extracted ESX directory."""
    path = os.path.join(json_dir, filename)
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_optional(json_dir: str, filename: str) -> dict[str, Any] | None:
    """Load a JSON file, returning None if it is not present."""
    try:
        return load(json_dir, filename)
    except FileNotFoundError:
        console.info(f"Not found: {console.yellow(filename)}")
        return None


def save(json_dir: str, filename: str, data: dict[str, Any]) -> None:
    """Write JSON back into an extracted ESX directory."""
    path = os.path.join(json_dir, filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
