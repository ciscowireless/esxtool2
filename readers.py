"""Read Ekahau JSON structures into domain models."""

from __future__ import annotations

from typing import Any

import console
import json_io
from models import Ap, Floor, Point, SlotConfig


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def read_floors(json_dir: str) -> list[Floor]:
    """Load floors and their reference points from an extracted ESX."""
    floors = _read_floor_plans(json_dir)
    _attach_reference_points(floors, json_dir)
    return floors


def read_aps(json_dir: str, floors: list[Floor]) -> list[Ap]:
    """Load APs and enrich with radio / antenna / measurement data."""
    floor_by_id = {f.id: f for f in floors}
    aps = _read_access_points(json_dir, floor_by_id)
    ap_by_id = {ap.id: ap for ap in aps}

    _attach_simulated_radios(ap_by_id, json_dir)
    _resolve_antenna_names(ap_by_id, json_dir)
    _attach_measured_radios(ap_by_id, json_dir)
    _attach_measurements(ap_by_id, json_dir)

    return aps


# ---------------------------------------------------------------------------
# Floor helpers
# ---------------------------------------------------------------------------

def _read_floor_plans(json_dir: str) -> list[Floor]:
    data = json_io.load(json_dir, "floorPlans.json")
    return [
        Floor(
            id=item["id"],
            name=item["name"],
            width=item["width"],
            height=item["height"],
            image_id=item["imageId"],
            scaling=item["metersPerUnit"],
        )
        for item in data["floorPlans"]
    ]


def _attach_reference_points(floors: list[Floor], json_dir: str) -> None:
    data = json_io.load_optional(json_dir, "referencePoints.json")
    if data is None:
        return

    floor_by_id = {f.id: f for f in floors}
    for reference in data["referencePoints"]:
        for proj in reference["projections"]:
            floor = floor_by_id.get(proj["floorPlanId"])
            if floor is not None:
                coord = proj["coord"]
                floor.points.append(Point(round(coord["x"]), round(coord["y"])))


# ---------------------------------------------------------------------------
# AP helpers
# ---------------------------------------------------------------------------

def _read_access_points(
    json_dir: str, floor_by_id: dict[str, Floor]
) -> list[Ap]:
    data = json_io.load_optional(json_dir, "accessPoints.json")
    if data is None:
        return []

    aps: list[Ap] = []
    for item in data["accessPoints"]:
        location, floor_id, floor_name = _parse_location(item, floor_by_id)
        aps.append(
            Ap(
                id=item["id"],
                name=item["name"],
                hidden=item.get("hidden", False),
                vendor=item.get("vendor", ""),
                model=item.get("model", ""),
                colour=item.get("color", ""),
                location=location,
                floor_id=floor_id,
                floor_name=floor_name,
            )
        )
    return aps


def _parse_location(
    item: dict[str, Any], floor_by_id: dict[str, Floor]
) -> tuple[Point | None, str, str]:
    loc = item.get("location")
    if loc is None:
        return None, "", ""

    coord = loc.get("coord", {})
    x = coord.get("x")
    y = coord.get("y")
    floor_plan_id = loc.get("floorPlanId", "")

    if x is None or y is None:
        return None, floor_plan_id, ""

    floor = floor_by_id.get(floor_plan_id)
    floor_name = floor.name if floor else ""
    return Point(round(x), round(y)), floor_plan_id, floor_name


def _attach_simulated_radios(
    ap_by_id: dict[str, Ap], json_dir: str
) -> None:
    data = json_io.load_optional(json_dir, "simulatedRadios.json")
    if data is None:
        return

    for item in data["simulatedRadios"]:
        ap = ap_by_id.get(item["accessPointId"])
        if ap is None or item.get("radioTechnology") == "BLUETOOTH":
            continue

        ap.ekahau_type = "Simulated"
        slot_index = item["accessPointIndex"]

        channel = _parse_channel(item)
        enabled = item.get("enabled", False)
        txpower = round(item["transmitPower"]) if enabled else 0

        ap.slots[slot_index] = SlotConfig(
            index=slot_index,
            channel=channel,
            enabled=enabled,
            txpower=txpower,
            antenna_height=round(item.get("antennaHeight", 0), 1),
            antenna_tilt=round(item.get("antennaTilt", 0)),
            antenna_direction=round(item.get("antennaDirection", 0)),
            antenna_id=item.get("antennaTypeId", ""),
            antenna_mounting=item.get("antennaMounting", ""),
        )


def _parse_channel(item: dict[str, Any]) -> int:
    try:
        freq = item["channelByCenterFrequencyDefinedNarrowChannels"][0]
    except (KeyError, IndexError):
        console.info("Simulated radio does not have channel, setting to 0")
        return 0
    ch = freq_to_channel(freq)
    if ch is None:
        console.info(f"Unknown frequency {freq}, setting channel to 0")
        return 0
    return ch


def _resolve_antenna_names(
    ap_by_id: dict[str, Ap], json_dir: str
) -> None:
    data = json_io.load_optional(json_dir, "antennaTypes.json")
    if data is None:
        return

    antenna_name_by_id = {
        item["id"]: item.get("name", "")
        for item in data["antennaTypes"]
    }

    for ap in ap_by_id.values():
        for slot in ap.slots.values():
            name = antenna_name_by_id.get(slot.antenna_id)
            if name is None:
                console.info("Antenna does not have name, setting to NULL")
                slot.antenna_type = "NULL"
            else:
                slot.antenna_type = name or "NA"


def _attach_measured_radios(
    ap_by_id: dict[str, Ap], json_dir: str
) -> None:
    data = json_io.load_optional(json_dir, "measuredRadios.json")
    if data is None:
        return

    for radio in data["measuredRadios"]:
        ap = ap_by_id.get(radio["accessPointId"])
        if ap is not None:
            ids = radio.get("accessPointMeasurementIds", [])
            if ids:
                ap.measured_radio_id = ids[0]


def _attach_measurements(
    ap_by_id: dict[str, Ap], json_dir: str
) -> None:
    data = json_io.load_optional(json_dir, "accessPointMeasurements.json")
    if data is None:
        return

    measurement_by_id = {m["id"]: m for m in data["accessPointMeasurements"]}

    for ap in ap_by_id.values():
        if not ap.measured_radio_id:
            continue
        meas = measurement_by_id.get(ap.measured_radio_id)
        if meas is None:
            continue
        ap.ssid = meas.get("ssid", "")
        ap.mac = meas.get("mac", "")
        ap.ekahau_type = "Measured"


# ---------------------------------------------------------------------------
# Frequency / channel conversion
# ---------------------------------------------------------------------------

def freq_to_channel(freq: int) -> int | None:
    """Convert centre frequency (MHz) to Wi-Fi channel number."""
    if 2412 <= freq < 2485:
        return (freq - 2405) // 5
    if 5180 <= freq < 5886:
        return freq // 5 - 1000
    if 5955 <= freq < 7116:
        return (freq - 5955) // 5 + 1
    return None
