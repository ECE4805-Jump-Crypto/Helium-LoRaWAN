mapboxgl.accessToken = 'pk.eyJ1Ijoic2hhcGVpMzZlIiwiYSI6ImNsN3VrZjdxajAya2ozdW1zZ3cwaTl1MXUifQ.7dWrn7Jx3zvbocP2BmKGMQ';
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/shapei36e/cl822g760004a15sey3q5ovoo',
    zoom: 12,
    center: [-87.623177, 41.881832]
});


// Fetch all nodes from API
async function getHotspots() {


    const originalUrl = 'https://api.helium.io/v1/hotspots/location/distance?lat=41.881832&lon=-87.623177&distance=3000';
    let updatedUrl = originalUrl;
    var res = await fetch(updatedUrl);
    var data = await res.json();
    let totalData = [];
    with (Array.prototype) {
        totalData.push(data);
    }

    // Save all data in totalData
    while (data.cursor) {
        var res = await fetch(updatedUrl);
        var data = await res.json();
        with (Array.prototype) {
            totalData.push(data);
        }
        updatedUrl = originalUrl;
        console.log(totalData);
        updatedUrl = updatedUrl + '&cursor=' + data.cursor;
    }
    console.log(totalData[0]);

    //----------------------------------------------------------
    // *****Need Debugging here:
    // show all data in totalData
    //----------------------------------------------------------
    //for(let i = 0; i < totalData.length; i++){
        var hotspots = totalData[0].data.map(hotspot => {
            //if(hotspot.status.online == 'online'){
            return {
    
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: [hotspot.lng, hotspot.lat] // icon position [lng, lat]
                },
                properties: {
                    description:
                        //'blabla'
                        '<p> </p>' +
                        '<p><strong>Name: </strong>' + hotspot.name +
                        '<p><strong>Gain: </strong>' + hotspot.gain +
                        '<p><strong>Status: </strong>' + hotspot.status.online +
                        '<p><strong>Elevation: </strong>' + hotspot.elevation + '</p>'
                }
            }
        });  
        loadMap(hotspots); 
   // }
      
}


// Load map with nodes
function loadMap(hotspots) {

    map.on('load', function () {
        const size = 150;

        const pulsingDot = {
            width: size,
            height: size,
            data: new Uint8Array(size * size * 4),

            // When the layer is added to the map,
            // get the rendering context for the map canvas.
            onAdd: function () {
                const canvas = document.createElement('canvas');
                canvas.width = this.width;
                canvas.height = this.height;
                this.context = canvas.getContext('2d');
            },

            // Call once before every frame where the icon will be used.
            render: function () {
                const duration = 1000;
                const t = (performance.now() % duration) / duration;

                const radius = (size / 2) * 0.3;
                const outerRadius = (size / 2) * 0.7 * t + radius;
                const context = this.context;

                // Draw the outer circle.
                context.clearRect(0, 0, this.width, this.height);
                context.beginPath();
                context.arc(
                    this.width / 2,
                    this.height / 2,
                    outerRadius,
                    0,
                    Math.PI * 2
                );
                context.fillStyle = `rgba(255, 200, 200, ${1 - t})`;
                context.fill();

                // Draw the inner circle.
                context.beginPath();
                context.arc(
                    this.width / 2,
                    this.height / 2,
                    radius,
                    0,
                    Math.PI * 2
                );
                context.fillStyle = 'rgba(255, 100, 100, 1)';
                context.strokeStyle = 'white';
                context.lineWidth = 2 + 4 * (1 - t);
                context.fill();
                context.stroke();

                // Update this image's data with data from the canvas.
                this.data = context.getImageData(
                    0,
                    0,
                    this.width,
                    this.height
                ).data;

                // Continuously repaint the map, resulting
                // in the smooth animation of the dot.
                map.triggerRepaint();

                // Return `true` to let the map know that the image was updated.
                return true;
            }
        };
        map.addImage('pulsing-dot', pulsingDot, { pixelRatio: 2 });
        //Add a layer to use the image to represent the data.

        //source
        map.addSource('places', {
            type: 'geojson',
            data: {
                type: 'FeatureCollection',
                features: hotspots,
            }

        });


        map.addLayer({
            id: 'places',
            type: 'symbol',
            source: 'places',
            layout: {
                'icon-image': 'pulsing-dot', // reference the image
                'icon-size': 0.3,
                'icon-allow-overlap': true
            }
        });
    }
    );

    //click and popup
    map.on('click', 'places', function (hotspots) {
        // Copy coordinates array.
        const coordinates = hotspots.features[0].geometry.coordinates.slice();
        const description = hotspots.features[0].properties.description;

        // Ensure that if the map is zoomed out such that multiple
        // copies of the feature are visible, the popup appears
        // over the copy being pointed to.
        while (Math.abs(hotspots.lngLat.lng - coordinates[0]) > 180) {
            coordinates[0] += hotspots.lngLat.lng > coordinates[0] ? 360 : -360;
        }

        new mapboxgl.Popup()
            .setLngLat(coordinates)
            .setHTML(description)
            .addTo(map);
    });
    // Change the cursor to a pointer when the mouse is over the places layer.
    map.on('mouseenter', 'places', function () {
        map.getCanvas().style.cursor = 'pointer';
    });

    // Change it back to a pointer when it leaves.
    map.on('mouseleave', 'places', function () {
        map.getCanvas().style.cursor = '';
    });


}

//loadMap();
getHotspots();
