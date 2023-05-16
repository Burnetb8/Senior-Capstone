var map = L.map('map').fitWorld();
var planeLayer = L.layerGroup().addTo(map);
var infoLayer = L.layerGroup().addTo(map).setZIndex(800);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a> contributors"
}).addTo(map);

$("#closeButton").on('click', (event) => {
    $("#infoPane").hide();
    $(".leaflet-control-zoom").show();
});

function get_position_source_string(position_source) {
    var source = "";

    switch (position_source) {
        case 0:
            source = "ADS-B";
            break;
        case 1:
            source = "ASTERIX";
            break;
        case 2:
            source = "MLAT";
            break;
        case 3:
            source = "FLARM";
            break;
        default:
            source = "N/A";
    }

    return source;
}

function get_plane_category_string(category) {
    var category = "";

    switch (category) {
        default:
            category = "Unknown";
    }

    return category;
}

function main() {
    // create http request object
    const request = new XMLHttpRequest();

    // add event listener for when a response is received
    request.addEventListener("load", () => {
        // ignore cases where response body is null
        if (request.response == null)
            return;

        planeLayer.clearLayers();

        console.log(request.response.plane_data)
        for (const plane of request.response.plane_data) {
            var marker = L.marker({
                lat: plane.latitude,
                lng: plane.longitude,
            });

            // order in which these methods are called doesn't matter
            marker.setIcon(planeIcon);
            // Rotate icon to match actual plane heading
            marker.setRotationAngle(plane.true_track);
            marker.addTo(planeLayer);

            marker.on('click', (ev) => {
                // Remove previous data
                $("#infoPane tr").each(function (index) {
                    if ($(this).attr("id") != "tableHeader") {
                        $(this).remove();
                    }
                });

                // Add plane entries entries
                $("#infoPane table").append(`<tr><td>ICAO 24-bit Address</td><td>${plane.icao24.toUpperCase()}</td></tr>`);
                $("#infoPane table").append(`<tr><td>Callsign</td><td>${plane.callsign}</td></tr>`);
                $("#infoPane table").append(`<tr><td>Country Origin</td><td>${plane.origin_country}</td></tr>`);
                $("#infoPane table").append(`<tr><td>Time of Last Position Report</td><td>${Date(plane.time_position)}</td></tr>`);
                $("#infoPane table").append(`<tr><td>Last Contact (time)</td><td>${Date(plane.last_contact)}</td></tr>`);
                $("#infoPane table").append(`<tr><td>Position (Latitude, Longitude)</td><td>${plane.latitude}\u00b0N ${plane.longitude}\u00b0W</td></tr>`);
                $("#infoPane table").append(`<tr><td>Geometric Altitude (m)</td><td>${plane.geo_altitude}</td></tr>`);
                $("#infoPane table").append(`<tr><td>On Ground?</td><td>${plane.on_ground ? "Yes" : "No"}</td></tr>`);
                $("#infoPane table").append(`<tr><td>Velocity (m/s)</td><td>${plane.velocity}</td></tr>`);
                $("#infoPane table").append(`<tr><td>Heading (True Track, in degrees)</td><td>${plane.true_track}</td></tr>`);
                $("#infoPane table").append(`<tr><td>Vertical Rate (m/s)</td><td>${plane.vertical_rate}</td></tr>`);
                $("#infoPane table").append(`<tr><td>Squawk</td><td>${plane.squawk}</td></tr>`);
                $("#infoPane table").append(`<tr><td>Position Source</td><td>${get_position_source_string(plane.position_source)}</td></tr>`);
                $("#infoPane table").append(`<tr><td>Plane Category</td><td>${get_plane_category_string(plane.category)}</td></tr>`);

                // Hide zoom controls (draws over top of the table)
                $(".leaflet-control-zoom").hide();

                // Display data
                $("#infoPane").show();
            });
        }
    });

    // Create a GET request to send to the plane_states endpoint
    request.open("GET", "/map/plane_states");
    // Specify a JSON return type
    request.responseType = "json";
    // Send request
    request.send();
}
