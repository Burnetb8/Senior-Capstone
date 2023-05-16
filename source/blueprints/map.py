from enum import Enum
import json

from flask import Blueprint, render_template, make_response
from opensky_api import OpenSkyApi
from ..secrets import OpenSkyCredentials


bp = Blueprint("map", __name__, url_prefix="/map")

initial_center = {"lon": -81.0580422, "lat": 29.1799089, "zoom": 8}
#! Initial latitude and longitude set to Daytona Beach. Zoom level found through trial and error

opensky = OpenSkyApi(
    username=OpenSkyCredentials.USERNAME, password=OpenSkyCredentials.PASSWORD
)

# markers = [{"lat": 29.1802, "lon": -81.098}]
#! Latitudinal and longitudinal coordinates of the planes from the opensky API


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


@bp.route("plane_states")
def plane_states():
    data = {"plane_data": []}
    states = opensky.get_states(
        bbox=(
            initial_center["lat"] - 3,
            initial_center["lat"] + 3,
            initial_center["lon"] - 3,
            initial_center["lon"] + 3,
        )
    ).states

    for state in states:
        data["plane_data"].append(
            {
                "icao24": state.icao24,
                "callsign": state.callsign,
                "origin_country": state.origin_country,
                "time_position": state.time_position,
                "last_contact": state.last_contact,
                "longitude": state.longitude,
                "latitude": state.latitude,
                "geo_altitude": state.geo_altitude,
                "on_ground": state.on_ground,
                "velocity": state.velocity,
                "true_track": state.true_track,
                "vertical_rate": state.vertical_rate,
                "squawk": state.squawk,
                "position_source": state.position_source,
                "category": state.category,
            }
        )

    return make_response(
        data,
        200,
    )
