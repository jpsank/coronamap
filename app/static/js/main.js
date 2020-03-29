
// Required:
// mapboxAccessToken
// selectedDate

const DateTime = luxon.DateTime;


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

function formatNum(n) {
    return n === null? 'N/A' : n.toLocaleString();
}
function round2(n) {
    return Math.round(n*100) / 100.;
}

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
            let datetime = DateTime.fromISO(props['checked_at']).toLocaleString(DateTime.DATETIME_SHORT);
            let full_name = props['full_name'],
                positive = formatNum(props['positive']),
                negative = formatNum(props['negative']),
                total_tests = formatNum(props['total_tests']),
                pending = formatNum(props['pending']),
                hospitalized = formatNum(props['hospitalized']),
                death = formatNum(props['death']),
                cases_per_bed = formatNum(round2(props['cases_per_bed'])),
                total_icu_beds = formatNum(props['Total ICU Beds']);

            innerHTML += `<b>${full_name}</b><br>`;
            innerHTML += `${positive} positive tests <span class="small">(${datetime})</span><br>`;
            innerHTML += `&nbsp;&nbsp;&nbsp;&nbsp;${negative} negative tests<br>`;
            innerHTML += `&nbsp;&nbsp;&nbsp;&nbsp;${pending} pending tests<br>`;
            innerHTML += `&nbsp;&nbsp;&nbsp;&nbsp;${total_tests} total tests<br>`;
            innerHTML += `&nbsp;&nbsp;&nbsp;&nbsp;${hospitalized} hospitalized<br>`;
            innerHTML += `&nbsp;&nbsp;&nbsp;&nbsp;${death} deaths<br>`;
            innerHTML += `${total_icu_beds} Total ICU beds<br>`;
            innerHTML += `<b>${cases_per_bed}</b> Cases per bed`;
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
        fillColor: getColor(feature['properties']['cases_per_bed'])
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

    map.attributionControl.addAttribution('Healthcare data &copy; <a href="https://globalepidemics.org/2020/03/17/caring-for-covid-19-patients/">HGHI</a>, COVID-19 data &copy; <a href="https://covidtracking.com/">COVID Tracking Project</a>');
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
                '<span><i style="background:' + getColor(from + .0001) + '"></i> ' +
                from + (to ? '&ndash;' + to : '+') + '</span>');
        }

        div.innerHTML = labels.join('');
        return div;
    };

    legend.addTo(map);
}


// -------------------- INFO ELEMENTS --------------------

function setWorst(feature) {
    let cpb = feature["properties"]["cases_per_bed"];
    document.getElementById("worst").innerText = feature["properties"]["full_name"];
    document.getElementById("worst-value").innerText = formatNum(round2(cpb));
}


function setSafest(feature) {
    let cpb = feature["properties"]["cases_per_bed"];
    document.getElementById("safest").innerText = feature["properties"]["full_name"];
    document.getElementById("safest-value").innerText = formatNum(round2(cpb));
}


function setBadStates(features) {
    let badStates = features.filter(feat => feat['properties']['cases_per_bed'] > 9);

    let num = document.getElementById("num-bad-states");
    num.innerText = badStates.length;

    let list = document.getElementById("bad-states");
    list.innerHTML = badStates.map(feat => `<b>${feat['properties']['full_name']}</b>`);
}

// -------------------- MAIN --------------------

async function main() {
    let url = selectedDate? `fetch/${selectedDate}` : 'fetch';
    geoData = await fetch(url)
        .then(response => {
            return response.json()
        })
        .catch(err => {
            console.log(err)
        });

    let features = geoData["features"];
    setBadStates(features);

    setSafest(features[0]);
    setWorst(features[features.length-1]);

    // Map
    initMap();
    addInfo();
    addGeoJSON();
    addLegend();
}

main();
