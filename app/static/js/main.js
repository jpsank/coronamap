
// Required: mapboxAccessToken


// -------------------- INIT MAP --------------------

let map;

function initMap() {
    map = L.map('map').setView([37.8, -96], 4);

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=' + mapboxAccessToken, {
        maxZoom: 18,
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, ' +
            '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
            'Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        id: 'mapbox/light-v9',
        tileSize: 512,
        zoomOffset: -1
    }).addTo(map);
}

// -------------------- INFO POPUP --------------------

let info;

function addInfo() {
    // control that shows state info on hover
    info = L.control();

    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info');
        this.update();
        return this._div;
    };

    info.update = function (props) {
        let innerHTML = '<h4>COVID-19 Cases vs. ICU Capacity</h4>';
        if (props) {
            let cases_per_bed = Math.round(100 * props['cases per bed']) / 100;
            innerHTML += `<b>${props.name}</b><br>`;
            innerHTML += `${props['confirmed'][0]} Confirmed cases ` +
                `<span class="small">(${props['confirmed'][1]})</span><br>`;
            innerHTML += `&nbsp;&nbsp;&nbsp;&nbsp;${props['deaths'][0]} Deaths ` +
                `<span class="small">(${props['deaths'][1]})</span><br>`;
            innerHTML += `&nbsp;&nbsp;&nbsp;&nbsp;${props['recovered'][0]} Recovered cases ` +
                `<span class="small">(${props['deaths'][1]})</span><br>`;
            innerHTML += `${props['Intensive-care beds']} Intensive-care beds<br>` +
                `<b>${cases_per_bed}</b> Cases per bed`;
        } else {
            innerHTML += 'Hover over a state'
        }
        this._div.innerHTML = innerHTML;
    };

    info.addTo(map);
}


// -------------------- FEATURE STYLING --------------------

// get color depending on value
function getColor(d) {
    return d > 200   ? '#FF00FF' :
            d > 100   ? '#C000FF' :
            d > 50   ? '#8000AC' :
            d > 20   ? '#800026' :
            d > 10  ? '#BD0026' :
            d > 5  ? '#E31A1C' :
            d > 2  ? '#FC4E2A' :
            d > 1  ? '#FD8D3C' :
            d > .5 ? '#FEB24C' :
            d > .2 ? '#FED976' :
            d > .1 ? '#FFEDA0' :
                     '#FFFAC0';
}

function style(feature) {
    return {
        weight: 2,
        opacity: 1,
        color: 'white',
        dashArray: '3',
        fillOpacity: 0.7,
        fillColor: getColor(feature.properties['confirmed'][0] / feature.properties['Intensive-care beds'])
    };
}

// -------------------- FEATURE CONTROL --------------------

let geojson;

let currentlyHighlighted;

function highlightFeature(e) {
    if (currentlyHighlighted)
        geojson.resetStyle(currentlyHighlighted);

    let layer = e.target;

    layer.setStyle({
        weight: 5,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }

    info.update(layer.feature.properties);

    currentlyHighlighted = layer;
}

function resetHighlight(e) {
    geojson.resetStyle(e.target);
    info.update();
}

function zoomToFeature(e) {
    map.fitBounds(e.target.getBounds());
}

let isTouchDevice = ('ontouchstart' in document.documentElement);

function onEachFeature(feature, layer) {
    if (isTouchDevice)
        layer.on({
            click: highlightFeature,
            dblclick: zoomToFeature
        });
    else
        layer.on({
            mouseover: highlightFeature,
            mouseout: resetHighlight,
            click: zoomToFeature
        });
}


// -------------------- FEATURE DATA --------------------

let geoData;

function addGeoJSON() {
    geojson = L.geoJson(geoData, {
        style: style,
        onEachFeature: onEachFeature
    }).addTo(map);

    map.attributionControl.addAttribution('Hospital stats &copy; <a href="https://www.modernhealthcare.com/hospitals/covid-19-could-fill-hospital-beds-how-many-are-there">Modern Healthcare</a>, COVID-19 data from <a href="https://github.com/CSSEGISandData/COVID-19">CSSE</a>');
}

// -------------------- LEGEND --------------------
function addLegend() {
    let legend = L.control({position: 'bottomright'});

    legend.onAdd = function (map) {

        let div = L.DomUtil.create('div', 'info legend'),
            grades = [0, .1, .2, .5, 1, 2, 5, 10, 20, 50, 100, 200],
            labels = [],
            from, to;

        for (let i = 0; i < grades.length; i++) {
            from = grades[i];
            to = grades[i + 1];

            labels.push(
                '<i style="background:' + getColor(from + .0001) + '"></i> ' +
                from + (to ? '&ndash;' + to : '+'));
        }

        div.innerHTML = labels.join('<br>');
        return div;
    };

    legend.addTo(map);
}


// -------------------- WORST/SAFEST --------------------

function setWorst(region, cases_per_bed) {
    document.getElementById("worst").innerText = region;
    document.getElementById("worst-value").innerText = Math.round(100*cases_per_bed)/100;
}


function setSafest(region, cases_per_bed) {
    document.getElementById("safest").innerText = region;
    document.getElementById("safest-value").innerText = Math.round(100*cases_per_bed)/100;
}

// -------------------- MAIN --------------------

async function main() {
    let data = await fetch(`fetch`)
        .then(response => {
            return response.json()
        })
        .catch(err => {
            console.log(err)
        });
    geoData = data['geojson'];

    setWorst(...data['worst']);
    setSafest(...data['safest']);

    initMap();
    addInfo();
    addGeoJSON();
    addLegend();
}

main();
