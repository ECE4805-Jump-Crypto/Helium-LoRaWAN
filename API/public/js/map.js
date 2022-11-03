//if needed to store information
class Static {
  static counter = 0;
  static Lat ='';
  static Lng=''; 
  static Gain= '';
  static Elevation='';
  static center=[-87.623177, 41.881832];
}

var storage = window.sessionStorage; 
//storage.setItem('Counter','0'); 

const nodeForm = document.getElementById('Hotspots-form');
const nodeGain = document.getElementById('Hotspots-gain');
const nodeElevation = document.getElementById('Hotspots-elevation');





mapboxgl.accessToken = 'pk.eyJ1Ijoic2hhcGVpMzZlIiwiYSI6ImNsN3VrZjdxajAya2ozdW1zZ3cwaTl1MXUifQ.7dWrn7Jx3zvbocP2BmKGMQ';
var Coord = document.getElementById('coordinates');
var HNT = document.getElementById('confi');
//center = [storage.getItem('TestLng'), storage.getItem('TestLat')]; 
// if(storage.getItem('TestLng')!=null && storage.getItem('TestLat')!=null){
//   Static.center = [storage.getItem('TestLng'), storage.getItem('TestLat')];
// }
 


//map.flyTo({center: [storage.getItem('TestLng'), storage.getItem('TestLat')]}); 




var marker = new mapboxgl.Marker();
var nodes = new mapboxgl.Marker();


// confidence interval
function confi(){
  HNT.innerHTML = `Loading...`; 
  
}
function prediction(){
  predict.innerHTML = `Loading...`; 
  
}
async function getResults(){
  //need change api to confidence interval
  var confiRes = await fetch('https://localhost:3000/simulate');
  var confiData = await confiRes.json();

  var confiLow = confiData.data.interval[0];
  var confiHigh =  confiData.data.interval[1];
  var pdPD = confiData.rewards;
  HNT.innerHTML = `Confidence Interval:   (${confiLow},${confiHigh}) HNT`
  predict.innerHTML = `Prediction:   ${pdPD} HNT`; 
}



// Get calculated prediction from backend
// async function getPrediction(){
//   var pdRes = await fetch('https://api.helium.io/v1/oracle/prices/current');
//   var pdData = await pdRes.json();

//   var hntPrice = pdData.data.price; 
//   hntPrice = hntPrice/100000000; 
//   hntPrice = hntPrice.toFixed(2); 
//   console.log(hntPrice); 
//   HNT.innerHTML = `HNT Price:   $${hntPrice}`
  
// }


var map = new mapboxgl.Map({
  container: "map",
  style: 'mapbox://styles/shapei36e/cl822g760004a15sey3q5ovoo',
  zoom: 12,
  center: [-87.623177, 41.881832]
});

// Get prediction

async function addLines(){
  var ndRes = await fetch('/api/v1/hotspots');
  var ndData = await ndRes.json();
  var nd = ndData.data;
  console.log(nd); 
  var Lat = nd[nd.length-1].Lat;
  var Lng = nd[nd.length-1].Lng;
  var Gain = nd[nd.length-1].gain;
  var Elevation = nd[nd.length-1].elevation;
  storage.setItem('TestLat',Lat);
  storage.setItem('TestLng',Lng);
  storage.setItem('TestGain',Gain);
  storage.setItem('TestElevation',Elevation);
  console.log(storage); 
  node.innerHTML = `Configuration of Hotspot: <br />Lat:${Lat},<br /> Lng:${Lng}, <br />Gain:${Gain}, <br />Elevation:${Elevation}`
  Test_cor = [storage.getItem('TestLng'), storage.getItem('TestLat')]; 
  marker.setLngLat(Test_cor).addTo(map);
  map.flyTo({center: Test_cor}); 
  Coord.innerHTML= `Longitude: ${storage.getItem('TestLng')}<br />Latitude: ${storage.getItem('TestLat')}`;

  
  var lines = nd.map(line => {
    return {

      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates: [
          [line.Lng, line.Lat],
          [storage.getItem('TestLng'),storage.getItem('TestLat')]
        ]// icon position [lng, lat]
      }
    }
  });
  var Linehotspots = nd.map(Linehotspot => {
    //if(hotspot.status.online == 'online'){ 
    return {

      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [Linehotspot.Lng, Linehotspot.Lat] // icon position [lng, lat]
      },
      properties: {
        description:
          //'blabla'
          '<p> </p>' +
          '<p><strong>Gain: </strong>' + Linehotspot.gain +
          '<p><strong>Elevation: </strong>' + Linehotspot.elevation +'</p>'
      }
    }
  });
  map.on('load', ()=>{
  map.addSource('lines', {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features: lines,
    }

  });
  map.addLayer({
    'id': 'lines',
    'type': 'line',
    'source': 'lines',
    'layout': {
    'line-join': 'round',
    'line-cap': 'round'
    },
    'paint': {
    'line-color': '#888',
    'line-width': 4
    }
    });
  });
  map.addSource('linenode', {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features: Linehotspots,
    }

  });

  map.addLayer({
    'id': 'linenode',
    'type': 'circle',
    'source': 'linenode',
    'paint': {
    'circle-color': '#fbb03b',
    'circle-radius': 5,
    'circle-stroke-width': 2,
    'circle-stroke-color': '#ffffff'
    }
    });
    //click and popup
  var popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnclick: false
  });
  // Change the cursor to a pointer when the mouse is over the places layer.
  map.on('mouseenter', 'linenode', function (Linehotspots) {
    map.getCanvas().style.cursor = 'pointer';

    // Copy coordinates array.
    const coordinates = Linehotspots.features[0].geometry.coordinates.slice();
    const description = Linehotspots.features[0].properties.description;

    // Ensure that if the map is zoomed out such that multiple
    // copies of the feature are visible, the popup appears
    // over the copy being pointed to.
    while (Math.abs(Linehotspots.lngLat.lng - coordinates[0]) > 180) {
      coordinates[0] += Linehotspots.lngLat.lng > coordinates[0] ? 360 : -360;
    }

    popup.setLngLat(coordinates).setHTML(description).addTo(map);
  });

  // Change it back to a pointer when it leaves.
  map.on('mouseleave', 'linenode', function () {
    map.getCanvas().style.cursor = '';
    popup.remove();
  });
  



}
addLines();

// Add marker(added node) by click 
async function add_marker(event) {
  
  var coordinates = event.lngLat;
  console.log('Lng:', coordinates.lng, 'Lat:', coordinates.lat);
  var Lat = coordinates.lat.toString();
  var Lng = coordinates.lng.toString();
  Static.Lat = coordinates.lat;
  Static.Lng = coordinates.lng; 
  console.log('sLng:', Static.Lng, 'sLat:', Static.Lat);
  Coord.innerHTML= `Longitude: ${coordinates.lng}<br />Latitude: ${coordinates.lat}`;


  // Update API link
  originalUrl = 'https://api.helium.io/v1/hotspots/location/distance?lat=' + Lat + '&lon=' + Lng + '&distance=2000';
  console.log(originalUrl);


  // Fetch API and get nodes data
  let updatedUrl = originalUrl;
  var res = await fetch(updatedUrl);
  var data = await res.json();
  let totalData = [];
  with (Array.prototype) {
    totalData.push(data);
  }

  // Save all data in totalData, and then save in newObj
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
  let newObj = {"data": []}
  for(var i=0;i<totalData.length;i++){
      for(var j = 0;j<totalData[i].data.length;j++){
        with (Array.prototype) {
          newObj.data.push(totalData[i].data[j]);
        }
    }
  }
  console.log(newObj);



  marker.setLngLat(coordinates).addTo(map);
  //here add existing nodes--------------------------------------------------
  //online 
  var obj = newObj.data.filter(item => item.status.online=="online");
  console.log(obj);
  //const params = list.filter(item=> arr.indexOf(item.id) > -1)
  var hotspots = obj.map(hotspot => {
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
  // offline 
  var offobj = newObj.data.filter(item => item.status.online=="offline");
  var offhotspots = offobj.map(offhotspot => {
    //if(hotspot.status.online == 'online'){ 
    return {

      type: 'Feature',
      geometry: {
        type: 'Point',
        coordinates: [offhotspot.lng, offhotspot.lat] // icon position [lng, lat]
      },
      properties: {
        description:
          //'blabla'
          '<p> </p>' +
          '<p><strong>Name: </strong>' + offhotspot.name +
          '<p><strong>Gain: </strong>' + offhotspot.gain +
          '<p><strong>Status: </strong>' + offhotspot.status.online +
          '<p><strong>Elevation: </strong>' + offhotspot.elevation + '</p>'
      }
    }
  });

  // here add map source/features
  loadMap(hotspots,offhotspots);
  console.log('if load');

}

function loadMap(hotspots,offhotspots) {
  //-----------------------------------------------
  //Change load on to click on
  //-----------------------------------------------
  // map.on('load', function () {
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
      //context.fillStyle = `rgba(255, 200, 200, ${1 - t})`;
      context.fillStyle = `rgba(178, 222, 39, ${1 - t})`;
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
      context.fillStyle = 'rgba(46, 204, 113, 1)';
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

  map.addSource('offplaces', {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features: offhotspots,
    }

  });

  map.addLayer({
    'id': 'offplaces',
    'type': 'circle',
    'source': 'offplaces',
    'paint': {
    'circle-color': '#e55e5e',
    'circle-radius': 3,
    'circle-stroke-width': 2,
    'circle-stroke-color': '#ffffff'
    }
    });



  Static.counter++;
  console.log(Static.counter);
  //}
  //);

  //click and popup
  var popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnclick: false
  });
  // Change the cursor to a pointer when the mouse is over the places layer.
  map.on('mouseenter', 'places', function (hotspots) {
    map.getCanvas().style.cursor = 'pointer';

    // Copy coordinates array.
    const coordinates = hotspots.features[0].geometry.coordinates.slice();
    const description = hotspots.features[0].properties.description;

    // Ensure that if the map is zoomed out such that multiple
    // copies of the feature are visible, the popup appears
    // over the copy being pointed to.
    while (Math.abs(hotspots.lngLat.lng - coordinates[0]) > 180) {
      coordinates[0] += hotspots.lngLat.lng > coordinates[0] ? 360 : -360;
    }

    popup.setLngLat(coordinates).setHTML(description).addTo(map);
  });
  map.on('mouseenter', 'offplaces', function (offhotspots) {
    map.getCanvas().style.cursor = 'pointer';

    // Copy coordinates array.
    const offcoordinates = offhotspots.features[0].geometry.coordinates.slice();
    const offdescription = offhotspots.features[0].properties.description;

    // Ensure that if the map is zoomed out such that multiple
    // copies of the feature are visible, the popup appears
    // over the copy being pointed to.
    while (Math.abs(offhotspots.lngLat.lng - offcoordinates[0]) > 180) {
      offcoordinates[0] += offhotspots.lngLat.lng > offcoordinates[0] ? 360 : -360;
    }

    popup.setLngLat(offcoordinates).setHTML(offdescription).addTo(map);
  });

  // Change it back to a pointer when it leaves.
  map.on('mouseleave', 'places', function () {
    map.getCanvas().style.cursor = '';
    popup.remove();
  });
  map.on('mouseleave', 'offplaces', function () {
    map.getCanvas().style.cursor = '';
    popup.remove();
  });
  


}


// on click
map.on('click', (event) => {
  if (Static.counter == 0){
  map.removeSource('lines');
  map.removeLayer('lines');
  map.removeSource('linenode');
  map.removeLayer('linenode');
}
  add_marker(event);
  map.flyTo({
    center: event.lngLat,
  })
  console.log('try');
  if (Static.counter > 0) {
    map.removeImage('pulsing-dot');
    map.removeLayer('places');
    map.removeLayer('offplaces');
    map.removeSource('places');
    map.removeSource('offplaces');
  }
});


// cookies    
// function setCookie(name, value, seconds) {
//   seconds = seconds || 0;      
//   var expires = "";
//   if (seconds != 0) {         
//     var date = new Date();
//     date.setTime(date.getTime() + (seconds * 1000));
//     expires = "expires=" + date.toGMTString();
//   }
//   document.cookie = name + "=" + escape(value) + expires + "; path=/"; 
// }  
//  //get cookie    
//  function getCookie(name) {
//   var nameEQ = name + "=";
//   var ca = document.cookie.split(';');     
//   for (var i = 0; i < ca.length; i++) {
//     var c = ca[i];     
//     while (c.charAt(0) == ' ') {    
//       c = c.substring(1, c.length);    
//     }
//     if (c.indexOf(nameEQ) == 0) {    
//       return unescape(c.substring(nameEQ.length, c.length)); 
//     }
//   }
//   return false;
// }








// Add node
async function addNodes(e){
  e.preventDefault();
  
  if(Static.Lat === ''||Static.Lng === ''){
      alert('Please click to choose a location on the map');
      return; 
  }
  console.log(storage.getItem('Gain'));
    
  // storage.setItem('Counter','1');
  // storage.setItem('Gain',nodeGain.value);
  // storage.setItem('Elevation',nodeElevation.value);

  
  // if(nodeGain.value != '' && nodeElevation.value !=''){
  //     storage.setItem('Gain',nodeGain.value);
  //     storage.setItem('Elevation',nodeElevation.value);
  // }
  
    if (nodeGain.value === '' ||nodeElevation.value ===''){
      if(storage.getItem('Gain') ===null||storage.getItem('Elevation')===null){
      
      alert('Please fill in the fields');
      return;
      }   else{
        console.log(typeof(nodeElevation.value));
        // storage.setItem('Gain',nodeGain.value);
        // storage.setItem('Elevation',nodeElevation.value);
        // setCookie('Gain','1');
        // setCookie('Elevation','2');
        Static.Elevation = storage.getItem('Elevation');
        Static.Gain = storage.getItem('Gain');
        // storage.removeItem('Gain');
        // storage.removeItem('Elevation');
  
  
        console.log(Static);
      }
    
    }
    else{
      console.log(typeof(nodeElevation.value));
      storage.setItem('Gain',nodeGain.value);
      storage.setItem('Elevation',nodeElevation.value);
      // setCookie('Gain','1');
      // setCookie('Elevation','2');
      Static.Elevation = storage.getItem('Elevation');
      Static.Gain = storage.getItem('Gain');
      // storage.removeItem('Gain');
      // storage.removeItem('Elevation');


      console.log(Static);
    }
    


  const sendBody = {
      // HotspotsId: nodeName.value,
      // address: nodeAddress.value,
      Lat: Static.Lat,
      Lng: Static.Lng,
      gain:Static.Gain,
      elevation:Static.Elevation,
  }
  Static.Lat =='';
  Static.Lng ==''; 

  try {
      console.log(JSON.stringify(sendBody))
      const res = await fetch('/api/v1/hotspots',{
          method: 'POST',
          headers: {
              'Content-Type':'application/json'
          },
          body: JSON.stringify(sendBody)
      });
      if(res.status === 400){
          throw Error('Nodes already exists!')

      }
      alert('Node added!');
      window.location.href = '/index.html';
      
  } catch (error) {
      alert(error);
      return;
  }
}
function placeholder(){
  if(storage.getItem('Gain') ===null){
    nodeGain.placeholder = "Suggest: 6 dB";
  }
  else{
    nodeGain.placeholder = `Saved Default:  ${storage.getItem('Gain')} dB`;
  }

  if(storage.getItem('Elevation') ===null){
    nodeElevation.placeholder = "Suggest: 10 m";
  }
  else{
    nodeElevation.placeholder = `Saved Default:  ${storage.getItem('Elevation')} m`;
  }
}


nodeForm.addEventListener('submit', addNodes);
confi();
prediction();
getResults();
placeholder();






















