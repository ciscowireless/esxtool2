"""
ESX Tool v3
Command line tool for manipulating contents of Ekahau .ESX files

Example use cases:
- Extract static AP radio configuration into CSV for conversion into WLC CLI
- Normalize ESX contents (e.g. AP naming convention) prior to Catalyst Center map upload
- Swap Ekahau map images - update images with different sizes and reposition APs based on alignment points

https://github.com/ciscowireless/esxtool2


Copyright (c) 2026 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

from __future__ import annotations

import argparse
import os
import sys

import console
import csv_io
import writers
from project import EsxProject
from rescale import (
    ReferencePointError,
    build_floor_updates,
    build_image_mapping,
    compute_new_positions,
    match_floors,
)

VERSION = "3"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_template() -> None:
    csv_io.generate_template(os.getcwd())


def cmd_esxtocsv(esx_path: str) -> None:
    with EsxProject(esx_path) as proj:
        console.ok(f"ESX file: {console.green(proj.name)}")
        csv_io.export_aps(proj.aps, proj.dir, proj.name)
        csv_io.export_floors(proj.floors, proj.dir, proj.name)


def cmd_alltocsv() -> None:
    cwd = os.getcwd()
    esx_files = [
        os.path.join(cwd, f)
        for f in os.listdir(cwd)
        if f.endswith(".esx") and os.path.isfile(os.path.join(cwd, f))
    ]

    all_aps = []
    all_floors = []
    for path in esx_files:
        with EsxProject(path) as proj:
            console.ok(f"ESX file: {console.green(proj.name)}")
            all_aps.extend(proj.aps)
            all_floors.extend(proj.floors)

    csv_io.export_aps(all_aps, cwd, "All")
    csv_io.export_floors(all_floors, cwd, "All")


def cmd_csvtoesx(csv_path: str, esx_path: str) -> None:
    with EsxProject(esx_path) as proj:
        console.ok(f"ESX file: {console.green(proj.name)}")
        changes = csv_io.read_ap_changes(csv_path)
        writers.apply_ap_changes(proj.workdir, changes)
        proj.save()


def cmd_mapswap(esx_path: str, map_path: str) -> None:
    with EsxProject(esx_path) as proj, EsxProject(map_path) as map_src:
        console.ok(f"ESX file: {console.green(proj.name)}")
        console.ok(f"MAP file: {console.green(map_src.name)}")

        matched = match_floors(proj.floors, map_src.floors)
        if not matched:
            console.error("No matching floorplans")
            return

        new_positions = compute_new_positions(proj.aps, matched)
        writers.update_ap_positions(proj.workdir, new_positions)
        writers.update_floor_plans(proj.workdir, build_floor_updates(matched))
        writers.swap_images(proj.workdir, map_src.workdir, build_image_mapping(matched))
        writers.remove_reference_points(proj.workdir)

        console.ok(f"Replaced images: {console.green(len(matched))}")
        console.ok(f"Repositioned APs: {console.green(len(new_positions))}")

        proj.save()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_COMMANDS = {
    "esxtocsv": cmd_esxtocsv,
    "alltocsv": cmd_alltocsv,
    "csvtoesx": cmd_csvtoesx,
    "template": cmd_template,
    "mapswap": cmd_mapswap,
}


def _validate_file(path: str) -> str:
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(f"File not found: {path}")
    return path


def main() -> None:
    description = (
        f"\n{console.CYAN}ESX Tool{console.RESET} "
        f"Version {VERSION} - ESX file manipulation tool"
    )
    parser = argparse.ArgumentParser(description=description)
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--esxtocsv", nargs=1, type=_validate_file, metavar="ESX",
        help="Export ESX file contents to CSV",
    )
    group.add_argument(
        "--alltocsv", action="store_true",
        help="Export all ESX files in current directory to CSV",
    )
    group.add_argument(
        "--csvtoesx", nargs=2, type=_validate_file, metavar=("CSV", "ESX"),
        help="Update ESX file using data from CSV template",
    )
    group.add_argument(
        "--template", action="store_true",
        help="Generate empty CSV template",
    )
    group.add_argument(
        "--mapswap", nargs=2, type=_validate_file, metavar=("ESX", "MapESX"),
        help="Replace map from another ESX file, rescale and repositon APs on new map",
    )

    args = parser.parse_args()

    # The group is mutually exclusive and required, so exactly one is set.
    # Flags taking paths hold a list; the rest are simply True.
    name, value = next(
        (k, v) for k, v in vars(args).items() if k in _COMMANDS and v
    )
    paths = value if isinstance(value, list) else []

    try:
        _COMMANDS[name](*paths)
    except ReferencePointError as exc:
        console.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
