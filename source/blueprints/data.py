import pandas as pd
from flask import Blueprint, g, make_response
from opensky_api import OpenSkyApi
from requests.exceptions import ReadTimeout
from .map import initial_center
from pprint import pprint

try:
    # try to use the opensky API with credentials
    from ..secrets import OpenSkyCredentials

    opensky = OpenSkyApi(
        username=OpenSkyCredentials.USERNAME, password=OpenSkyCredentials.PASSWORD
    )
except ImportError:
    # if the username/password secrets weren't configured, use without credentials
    opensky = OpenSkyApi()

bp = Blueprint("data", __name__, url_prefix="/data")

airport_data = pd.read_csv(
    "data/us-airports.csv",
    usecols=[
        "ident",
        "type",
        "name",
        "latitude",
        "longitude",
        "elevation",
        "country_name",
        "region_name",
        "local_region",
        "municipality",
        "gps_code",
        "iata_code",
        "local_code",
        "home_link",
    ],
)


@bp.route("/plane_states")
def plane_states():
    data = {"plane_data": []}

    try:
        states = opensky.get_states(
            bbox=(
                initial_center["lat"] - 3,
                initial_center["lat"] + 3,
                initial_center["lon"] - 3,
                initial_center["lon"] + 3,
            )
        )

        # cache states in case there is a read timeout in the next call
        g.states_cache = states
    except ReadTimeout:
        # reuse cached data if there is a read timeout on the OpenSky API endpoint
        states = g.get("states_cache")

    if states is None:
        return make_response("Too many requests", 500)

    for state in states.states:
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

    return make_response(data, 200)


@bp.route("/flight_track/<icao24>")
def get_flight_track(icao24):
    response_data = {"waypoints": []}

    if "flight_tracks" not in g:
        g.flight_tracks = {}

    try:
        track = opensky.get_track_by_aircraft(icao24)
        g.flight_tracks[icao24] = track
    except ReadTimeout:
        track = g.flight_tracks.get(icao24)
    finally:
        flight_path = track.path

    for waypoint in flight_path:
        response_data["waypoints"].append(
            {
                "time": waypoint[0],
                "latitude": waypoint[1],
                "longitude": waypoint[2],
            }
        )

    return make_response(response_data, 200)


@bp.route("/airports/<state>")
def airports(state):
    response_data = {"airport_data": []}

    for row in airport_data.itertuples():
        if row.local_region == state:
            # filter by medium and large airports, because I didn't realize just
            # how many airports there are in the US
            if row.type == "large_airport" or row.type == "medium_airport":
                data = {
                    "identifier": row.ident,
                    "name": row.name,
                    "latitude": row.latitude,
                    "longitude": row.longitude,
                    "elevation": row.elevation,
                    "region_name": row.region_name,
                    "local_region": row.local_region,
                    "municipality": row.municipality,
                    "gps_code": row.gps_code,
                    "iata_code": row.iata_code,
                    "local_code": row.local_code,
                    "home_link": row.home_link,
                }

                # filter out nan values
                for k, v in data.items():
                    if pd.isna(v):
                        data[k] = "N/A"

                response_data["airport_data"].append(data)

    return make_response(response_data)
