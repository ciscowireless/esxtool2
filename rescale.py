"""Pure coordinate-transformation logic for map replacement."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, NamedTuple

from models import Ap, Floor, Point

_REQUIRED_POINTS = 2


class ReferencePointError(ValueError):
    """A floor does not carry a usable pair of reference points."""


@dataclass
class FloorMatch:
    """A pair of matched floors between project and map source."""
    name: str
    old_floor: Floor
    new_floor: Floor


class _Transform(NamedTuple):
    """Linear mapping from one floor's coordinate space onto another's."""
    old_a: Point
    old_b: Point
    new_a: Point
    new_b: Point

    def apply(self, point: Point) -> Point:
        return Point(
            round(_interpolate(point.x, self.old_a.x, self.old_b.x,
                               self.new_a.x, self.new_b.x)),
            round(_interpolate(point.y, self.old_a.y, self.old_b.y,
                               self.new_a.y, self.new_b.y)),
        )


def match_floors(
    project_floors: list[Floor],
    map_floors: list[Floor],
) -> list[FloorMatch]:
    """Match project floors to map-source floors by name."""
    map_by_name = {f.name: f for f in map_floors}
    matches = []
    for pf in project_floors:
        mf = map_by_name.get(pf.name)
        if mf is not None:
            matches.append(FloorMatch(name=pf.name, old_floor=pf, new_floor=mf))
    return matches


def compute_new_positions(
    aps: list[Ap],
    matched: list[FloorMatch],
) -> dict[str, Point]:
    """Calculate new AP positions by interpolating between reference points.

    Returns a mapping of AP name -> new Point.
    Raises ReferencePointError if any matched floor lacks a usable pair of
    reference points. All floors are validated before any AP is moved.
    """
    transforms = {m.name: _build_transform(m) for m in matched}

    return {
        ap.name: transforms[ap.floor_name].apply(ap.location)
        for ap in aps
        if ap.location is not None and ap.floor_name in transforms
    }


def build_floor_updates(matched: list[FloorMatch]) -> dict[str, dict[str, Any]]:
    """Build the update dict consumed by writers.update_floor_plans."""
    return {
        m.name: {
            "width": m.new_floor.width,
            "height": m.new_floor.height,
            "scaling": m.new_floor.scaling,
        }
        for m in matched
    }


def build_image_mapping(matched: list[FloorMatch]) -> dict[str, str]:
    """Build old_image_id -> new_image_id mapping for image swapping."""
    return {m.old_floor.image_id: m.new_floor.image_id for m in matched}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_transform(match: FloorMatch) -> _Transform:
    """Validate both floors of a match and derive their coordinate mapping."""
    old_a, old_b = _reference_pair(match.name, match.old_floor)
    new_a, new_b = _reference_pair(match.name, match.new_floor)
    return _Transform(old_a, old_b, new_a, new_b)


def _reference_pair(floor_name: str, floor: Floor) -> tuple[Point, Point]:
    """Return a floor's two reference points, ordered by ascending X."""
    points = sorted(floor.points, key=lambda p: p.x)

    if len(points) != _REQUIRED_POINTS:
        raise ReferencePointError(
            f"Floor {floor_name!r} needs exactly {_REQUIRED_POINTS} "
            f"reference points to be rescaled, but has {len(points)}"
        )

    if points[0].x == points[1].x or points[0].y == points[1].y:
        raise ReferencePointError(
            f"Floor {floor_name!r} has two reference points in line with "
            f"each other; they must differ in both X and Y"
        )

    return points[0], points[1]


def _interpolate(
    value: float,
    old_a: float, old_b: float,
    new_a: float, new_b: float,
) -> float:
    """Linear interpolation: map *value* from [old_a, old_b] to [new_a, new_b]."""
    ratio = (value - old_a) / (old_b - old_a)
    return new_a + (new_b - new_a) * ratio
