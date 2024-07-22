const DATA_ROOT = '/data/';
let CATEGORIES = {};
let PLACES = {};
let TEXT = {};
let DETAIL_MAP;
let DETAIL_MAP_LAYER;

// ---------------------
// Helper
// ---------------------

async function loadJson(url) {
    const res = await fetch(url);
    return await res.json();
}

function highlight(div) {
    const prev = div.style;
    div.style.transition = 'background-color .7s';
    div.style.backgroundColor = 'yellow';
    setTimeout(() => div.style = prev, 800);
}

// ---------------------
// HTML utils
// ---------------------

function makeMarker(place) {
    return L.marker(L.latLng(place.loc), {
        pid: place.id,
        title: place.later ? 'Noch nicht verfügbar' : place.name,
        icon: L.divIcon({
            className: 'pin ff-c' + place.cat + (place.later ? ' later' : ''),
            html: '<svg id="pin-' + place.id + '"><use href="/icons.svg#mark"></use></svg>',
            iconSize: [34, 55],
            iconAnchor: [17, 55],
            popupAnchor: [0, -20],
            tooltipAnchor: [0, -20],
            offset: [10, 20],
        }),
    });
}

function setBadge(div, category) {
    const badge = div.querySelector('.badge');
    // clear previous color
    badge.classList.remove('inv');
    for (const cls of badge.classList) {
        if (cls.startsWith('bg-c')) {
            badge.classList.remove(cls);
        }
    }
    // set new values
    badge.innerText = category.name || '';
    badge.classList.add('bg-c' + category.id);
    if (category.inv) {
        badge.classList.add('inv');
    }
}

function loadAudio(detailDiv, srcUrl) {
    const x = detailDiv.querySelector('audio');
    x.hidden = !srcUrl;
    x.querySelectorAll('source').forEach(x => x.remove());
    if (srcUrl) {
        const audioSrc = document.createElement('source');
        audioSrc.src = srcUrl;
        audioSrc.type = 'audio/mpeg';
        x.appendChild(audioSrc);
    }
    x.load(); // stops playing and reloads source
}

function comeBackLater() {
    showNotice('come-back-later');
}


// ---------------------
// Interactive
// ---------------------

function selectPin(e) {
    document.getElementById('pin-' + e.target.dataset.pk)
        .parentNode.classList.add('selected');
}

function unselectPin(e) {
    unselectPinById(e.target.dataset.pk);
}

function unselectPinById(pid) {
    document.getElementById('pin-' + pid)
        .parentNode.classList.remove('selected');
}

function openDetails(placeId, password) {
    initDetails(placeId);
    new bootstrap.Modal('#detail').show(); // trigger modal
}

function showNotice(id) {
    const txt = TEXT[id];
    if (txt) {
        const div = document.getElementById('notice');
        const sz = txt.wide ? 'lg' : 'md';
        div.firstElementChild.className = `modal-dialog modal-${sz} modal-fullscreen-${sz}-down`;
        div.querySelector('.modal-title').innerText = txt.title;
        div.querySelector('.modal-title').innerText = txt.title;
        div.querySelector('.modal-body').innerHTML = txt.body;
        new bootstrap.Modal(div).show();
    } else {
        console.error(`Missing text for "${id}"`)
    }
    return false;
}

function hideTab(tab) {
    document.getElementById('map-container').classList.remove('hidden-tab');
    document.getElementById('list-container').classList.remove('hidden-tab');
    document.getElementById(tab + '-container').classList.add('hidden-tab');
}

// ---------------------
// Initializer
// ---------------------

function initColors() {
    let rv = '';
    for (const cat of Object.values(CATEGORIES)) {
        rv += `.ff-c${cat.id} { fill: ${cat.color} }\n`;
        rv += `.bg-c${cat.id} { background: ${cat.color} }\n`;
    }
    document.getElementById('colors').innerHTML = rv;
}

function initCard(placeId) {
    const place = PLACES[placeId];
    const category = CATEGORIES[place.cat];
    const x = document.getElementById('card-template').cloneNode(true);
    document.getElementById('cards').append(x);
    x.id = 'card-' + placeId;
    x.dataset.pk = placeId;
    if (place.loc) {
        x.onmouseenter = selectPin;
        x.onmouseleave = unselectPin;
    }
    x.querySelector('a').href = '#' + placeId;
    x.querySelector('img').dataset.src = place.cov || '';
    x.querySelector('.card-title').innerText = place.name || '';
    setBadge(x, category);
}

function initLoadingCard() {
    const x = document.getElementById('card-template').cloneNode(true);
    x.id = 'card-loading';
    x.classList.add('placeholder-glow');
    document.getElementById('cards').append(x);
    x.querySelectorAll('img,h3,span').forEach(elem => {
        elem.classList.add('placeholder');
        elem.alt = '';
        if (elem.tagName === 'H3') {
            elem.classList.add('w-100');
        }
    });
    return x;
}

function initDetails(placeId) {
    const place = PLACES[placeId];
    const category = CATEGORIES[place.cat];
    const x = document.getElementById('detail');
    x.querySelector('img').src = place.img || '';
    x.querySelector('.modal-title').innerText = place.name || '';
    x.querySelector('#detail-desc').innerHTML = place.desc || '';
    setBadge(x, category);
    loadAudio(x, place.audio);
    // external map links
    x.querySelector('#detail-map-container').hidden = !place.loc;
    if (place.loc) {
        const [lat, long] = place.loc;
        x.querySelector('#osm-link').href = `https://www.openstreetmap.org/?mlat=${lat}&mlon=${long}&zoom=18`;
        x.querySelector('#g-maps').href = `https://www.google.com/maps/search/?api=1&query=${lat}%2C${long}&zoom=18`;
    }
    setDetailMarker(place);
    document.title = place.name + ' – ' + document.title;
}

function clearDetails() {
    const x = document.getElementById('detail');
    loadAudio(x, '');
    // in case of youtube videos or other media: stops everything else
    x.querySelector('#detail-desc').innerHTML = '';
    setDetailMarker(null);
    document.title = document.title.split(' – ').pop();
}

// ---------------------
// Map stuff
// ---------------------

function initGPS(map) {
    L.control.locate({
        returnToPrevBounds: true,
        showPopup: false,
    }).addTo(map);
}

function initDetailMap() {
    const map = L.map('detail-map');
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);
    initGPS(map);
    DETAIL_MAP_LAYER = L.layerGroup([]).addTo(map);
    DETAIL_MAP = map;
}

function setDetailMarker(place) {
    if (place && place.loc) {
        const pos = makeMarker(place).addTo(DETAIL_MAP_LAYER).getLatLng();
        DETAIL_MAP.setView(pos, 17);
        DETAIL_MAP.setMaxBounds(pos.toBounds(0));
        setTimeout(() => DETAIL_MAP.invalidateSize(), 300);
        setTimeout(() => DETAIL_MAP.invalidateSize(), 1000);
    } else {
        DETAIL_MAP_LAYER.clearLayers();
    }
}

async function initMainMap() {
    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: [
            '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
            '<a href="" onclick="return showNotice(\'imprint\')">Impressum</a>',
        ].join(' | '),
    });
    const map = L.map('map', {
        layers: [osm],
        center: [49.894413, 10.880028],
        zoom: 14,
        // minZoom: 11,
    });
    initGPS(map);
    // load data
    const layers = {};
    var bounds = L.latLngBounds();
    var layerControl = L.control.layers(null, null, {
        position: 'bottomright',
        // sortLayers: true,
    }).addTo(map);

    // init checkbox to toggle groups
    for (const cat of await loadJson(DATA_ROOT + 'categories.json')) {
        CATEGORIES[cat.id] = cat;
        layers[cat.id] = L.layerGroup([]).addTo(map);
        layerControl.addOverlay(layers[cat.id],
            '<i class="group-dot" style="background:' + cat.color + '"></i> '
            + cat.name);
    }

    // init places
    for (const place of await loadJson(DATA_ROOT + 'places.json')) {
        PLACES[place.id] = place;
        const group = layers[place.cat];
        if (place.loc) {
            const marker = makeMarker(place).addTo(group);
            marker.on('click', place.later ? comeBackLater : onMarkerClick);
            bounds.extend(marker.getLatLng());
        }
        if (!place.later) {
            initCard(place.id);
        }
    }

    // adjust bounds & zoom
    if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [100, 100] });
    }

    // tooltip
    function onTooltip(pin) {
        const div = document.getElementById("card-" + pin.options.pid);
        div.scrollIntoView({ behavior: 'smooth' });
        highlight(div);
        return '';
        // const place = PLACES[pin.options.pid];
        // return place.name;
    }

    // click events
    function onMarkerClick(e) {
        location.hash = e.target.options.pid; // triggers openDetails()
    }
}

async function start() {
    const temp = initLoadingCard();
    await initMainMap();
    initDetailMap();
    initColors();
    document.getElementById('spin').remove();
    onHashChange();
    loadJson(DATA_ROOT + 'text.json').then(x => TEXT = x)
    temp.remove();

    document.getElementById('detail').addEventListener('hidden.bs.modal', e => {
        location.hash = '';
    });

    const observer = lozad();
    observer.observe();
}

// event listener
function onHashChange() {
    if (location.hash.length > 1) {
        const [id, pw] = location.hash.slice(1).split(':', 1);
        unselectPinById(id);
        openDetails(id, pw);
    } else {
        clearDetails();
    }
}
addEventListener('hashchange', onHashChange);
