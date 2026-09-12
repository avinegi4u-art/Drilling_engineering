"""Depth-based annular pressure profile for a uniform or piecewise annulus."""

from __future__ import annotations

from collections.abc import Sequence

from mpd_engine.hydraulics.friction import calculate_bingham_annular_pressure_loss
from mpd_engine.models.drillstring import Drillstring
from mpd_engine.models.fluids import FluidProperties
from mpd_engine.models.well import Well, WellSection


def hole_id_at_md(well: Well, md_m: float) -> float:
    """Return the wellbore inner diameter at measured depth *md_m*."""
    for section in well.sections:
        if section.md_top_m - 1.0e-9 <= md_m <= section.md_bottom_m + 1.0e-9:
            return section.hole_id_m
    return well.sections[-1].hole_id_m


def pipe_od_at_md(drillstring: Drillstring, md_m: float) -> float:
    """Return drillstring OD at measured depth, walking components top-down."""
    remaining = max(md_m, 0.0)
    cumulative = 0.0
    last_od = drillstring.components[0].od_m
    for component in drillstring.components:
        cumulative += component.length_m
        last_od = component.od_m
        if remaining <= cumulative + 1.0e-9:
            return component.od_m
    return last_od


def tvd_at_md(well: Well, md_m: float) -> float:
    """Linearly interpolate TVD from the well trajectory (version 1 vertical: TVD = MD)."""
    stations = well.trajectory
    if md_m <= stations[0].md_m:
        return stations[0].tvd_m
    if md_m >= stations[-1].md_m:
        return stations[-1].tvd_m
    for upper, lower in zip(stations, stations[1:], strict=False):
        if upper.md_m <= md_m <= lower.md_m:
            span = lower.md_m - upper.md_m
            if span == 0.0:
                return lower.tvd_m
            weight = (md_m - upper.md_m) / span
            return upper.tvd_m + weight * (lower.tvd_m - upper.tvd_m)
    return stations[-1].tvd_m


def annular_friction_to_surface(
    well: Well,
    drillstring: Drillstring,
    fluid: FluidProperties,
    flow_rate_m3_s: float,
    md_m: float,
) -> float:
    """Integrate annular friction from surface to *md_m* along the string."""
    if md_m <= 0.0 or flow_rate_m3_s == 0.0:
        return 0.0
    loss = 0.0
    cursor = 0.0
    for component in drillstring.components:
        segment_end = min(md_m, cursor + component.length_m)
        length = segment_end - cursor
        if length > 0.0:
            mid = cursor + length / 2.0
            hole_id = hole_id_at_md(well, mid)
            loss += calculate_bingham_annular_pressure_loss(
                mud_density_kg_m3=fluid.mud_density_kg_m3,
                plastic_viscosity_pa_s=fluid.plastic_viscosity_pa_s,
                yield_stress_pa=fluid.yield_stress_pa,
                flow_rate_m3_s=flow_rate_m3_s,
                length_m=length,
                hole_id_m=hole_id,
                pipe_od_m=component.od_m,
            )
        cursor += component.length_m
        if cursor >= md_m - 1.0e-9:
            break
    if cursor < md_m - 1.0e-9:
        raise ValueError(
            "Drillstring length "
            f"({drillstring.total_length_m} m) is shorter than requested MD ({md_m} m)"
        )
    return loss


def section_boundaries(sections: Sequence[WellSection]) -> list[float]:
    """Return unique MD boundaries for profile sampling."""
    depths = [sections[0].md_top_m]
    for section in sections:
        depths.append(section.md_bottom_m)
    return depths
