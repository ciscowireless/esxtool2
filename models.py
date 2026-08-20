"""Domain models for Ekahau ESX project data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import NamedTuple


class Point(NamedTuple):
    x: float
    y: float


@dataclass
class SlotConfig:
    index: int
    channel: int = 0
    enabled: bool = False
    txpower: int = 0
    antenna_height: float = 0.0
    antenna_tilt: int = 0
    antenna_direction: int = 0
    antenna_id: str = ""
    antenna_type: str = ""
    antenna_mounting: str = ""


@dataclass
class Floor:
    id: str
    name: str
    width: float
    height: float
    image_id: str
    scaling: float
    points: list[Point] = field(default_factory=list)


@dataclass
class Ap:
    id: str
    name: str
    hidden: bool = False
    mac: str = ""
    ssid: str = ""
    vendor: str = ""
    model: str = ""
    location: Point | None = None
    floor_id: str = ""
    floor_name: str = ""
    colour: str = ""
    ekahau_type: str = ""
    slots: dict[int, SlotConfig] = field(default_factory=dict)
    measured_radio_id: str = ""


@dataclass
class ApChange:
    """A requested change from a CSV import row."""
    name: str
    new_name: str = ""
    new_x: float | None = None
    new_y: float | None = None
