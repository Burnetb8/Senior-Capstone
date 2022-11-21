// https://www.w3schools.com/howto/howto_js_draggable.asp
function dragElement(element) {
    var pos1 = 0,
        pos2 = 0,
        pos3 = 0,
        pos4 = 0;

    element.onmousedown = dragMouseDown;

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        element.style.top = (element.offsetTop - pos2) + "px";
        element.style.left = (element.offsetLeft - pos1) + "px";
    }

    function closeDragElement() {
        // stop moving when mouse button is released:
        document.onmouseup = null;
        document.onmousemove = null;
    }
}

function createTilingMap() {
    // Render the tiling map 
    var viewer = OpenSeadragon({
        id: "image_map",
        prefixUrl: "/openseadragon/images/",
        tileSources: {
            height: 12412,
            width: 16617,
            tileSize: 512,
            minLevel: 4,
            defaultZoomLevel: 17,
            getTileUrl: function( level, x, y ){
                return "/assets/output_files/" + level + "/" + x + "_" + y + ".png";
            }
        }
    });

    // Set tiling map initial zoom and pan
    viewer.addHandler('open', function() {
        viewer.viewport.zoomTo(4, null, true);
    })
}

window.onload = function () {
    setTimeout(function () {
        dragElement(document.getElementById("popup"));

        createTilingMap();
    }, 1000);
}