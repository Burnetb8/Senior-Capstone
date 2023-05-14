from flask import Blueprint, render_template
from enum import Enum

bp = Blueprint("map", __name__, url_prefix="/map")

initial_center = {"lon": -81.0598, "lat": 29.1802, "zoom": 8}
#! Initial latitude and longitude set to Daytona Beach. Zoom level found through trial and error

markers = [{"lat": 29.1802, "lon": -81.098}]
#! Latitudinal and longitudinal coordinates of the planes from the opensky API


class MapSelector(Enum):
    GEOGRAPHIC = "geo"
    SECTIONAL = "aero"


@bp.route("/<type>")
def map(type: str):
    if type == "geo":
        return render_template(
            "map/geographic_map.html", markers=markers, initial_center=initial_center
        )
    elif type == "aero":
        return render_template("map/sectional_map.html", markers=markers)
