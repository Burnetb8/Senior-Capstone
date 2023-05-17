from enum import Enum

from flask import Blueprint, render_template, make_response, g

bp = Blueprint("map", __name__, url_prefix="/map")

initial_center = {"lon": -81.0580422, "lat": 29.1799089, "zoom": 8}
#! Initial latitude and longitude set to Daytona Beach. Zoom level found through trial and error

# markers = [{"lat": 29.1802, "lon": -81.098}]
# Latitudinal and longitudinal coordinates of the planes from the opensky API


class MapSelector(Enum):
    GEOGRAPHIC = "geo"
    SECTIONAL = "aero"


@bp.route("/<type>")
def map(type: str):
    map_type = MapSelector(type)
    if map_type == MapSelector.GEOGRAPHIC:
        return render_template(
            "map/geographic_map.html",
            initial_center=initial_center,
        )
    elif map_type == MapSelector.SECTIONAL:
        return render_template(
            "map/sectional_map.html",
            initial_center=initial_center,
        )
