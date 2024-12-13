<template>
    <LoadingIndicator v-show="loading" class="w-10 h-full text-neutral-100 mx-auto" />
    <div class="flex w-full" v-show="!loading">
        
        <div class="w-full max-h-full relative" id="map" v-show="isDashcam">
            <div class="absolute z-10 bg-white h-[280px] w-[489px] left-1 bottom-1">
                <video :key="src" ref="mediaRef" class="h-full w-full" autoplay muted preload="none"
                    controlslist="nodownload noremoteplayback noplaybackrate disablepictureinpicture" controls draggable="false"
                    @loadedmetadata="handleMediaReady" @timeupdate="onTimeUpdate">
                    <source :src="src" :type="type" />
                </video>
            </div>
        </div>
        <video :key="src" ref="mediaRef" class="max-h-full w-full" autoplay muted preload="none"
            controlslist="nodownload noremoteplayback noplaybackrate disablepictureinpicture" controls draggable="false"
            @loadedmetadata="handleMediaReady" v-show="!isDashcam">
            <source :src="src" :type="type" />
        </video>
    </div>
</template>

<script setup>
/* 
  Add codec evaluation currently assumes its a valid H264/5 (MP4/Webm)
  Look into the feasibility of client side mp4 moov fragmentation pre processing using
  https://github.com/gpac/gpac/wiki/MP4Box
  Server side byte is good enough for now 
*/

import { LoadingIndicator, createResource } from "frappe-ui"
import { ref, onBeforeUnmount, watch, onMounted } from "vue"
import { useStore } from "vuex"

const store = useStore()
const props = defineProps({
    previewEntity: {
        type: String,
        default: "",
    },
})
const loading = ref(true)
const src = ref(null)
const type = ref(
    props.previewEntity.mime_type === "video/quicktime"
        ? "video/mp4"
        : props.previewEntity.mime_type
)
const mediaRef = ref("")
const mapRef = ref(null)
const geojsonRef = ref(null)
const dataGPSRef = ref(null)
const alongPath = ref([])
const isDashcam = ref(true)
const fpsRef = ref(null)
const featureLocationMarker = ref({
    type: "FeatureCollection",
    features: []
})
const featureLocationHistory = ref({
    type: "FeatureCollection",
    features: []
})
const bearingRef = ref(null)

const handleMediaReady = (event) => {
    mediaRef.value = event.target
    if (mediaRef.value.readyState === 1) {
        loading.value = false
    }
}

watch(
    () => props.previewEntity,
    (newValue) => {
        loading.value = true
        onCallDataGPS()
        type.value = newValue.mime_type
    }
)

onMounted(() => {
    if (props.previewEntity.name != null) {
        onCallDataGPS()
    }
})

function onCallDataGPS() {
    let resourceMetaData = createResource({
        url: "drive.api.files.get_file_gps",
        method: "GET",
        params: {
            entity_name: props.previewEntity.name
        },
        onSuccess(data) {
            if(data.fps != null && data.fps != 0) fpsRef.value = data.fps
            else fpsRef.value = 30
            if(data.arr_gps.length == 0) isDashcam.value = false
            if(isDashcam.value) initMap()
            dataGPSRef.value = data.arr_gps
            let geojson = {
                'type': "Feature",
                'geometry': {
                    'type': "LineString",
                    'coordinates': []
                }
            }
            for (let i = 0; i < data.arr_gps.length; i++) {
                geojson.geometry.coordinates.push([data.arr_gps[i].lon, data.arr_gps[i].lat])
            }
            if (mapRef.value != null && mapRef.value.isStyleLoaded()) {
                onAddLayerSatellite()
                onAddLayerLine(geojson)
                onAddLayerCar()
                onAddLayerHistorialPath()
            } else if(mapRef.value != null) {
                mapRef.value.on("load", () => {
                    onAddLayerSatellite()
                    onAddLayerLine(geojson)
                    onAddLayerCar()
                    onAddLayerHistorialPath()
                })
            }
            geojsonRef.value = geojson
            setTimeout(()=>{
                src.value = `/api/method/drive.api.files.get_file_content?entity_name=${props.previewEntity.name}`
            }, 300)
            
        }
    })
    resourceMetaData.fetch()
}

function onTimeUpdate(evt) {
    const fps = fpsRef.value
    const currentTime = evt.target.currentTime
    const currentFrame = Math.floor(currentTime * fps)
    if (dataGPSRef.value[currentFrame] != null) {
        let feature = {
            'type': "Feature",
            'geometry': {
                'type': "Point",
                'coordinates': [dataGPSRef.value[currentFrame].lon, dataGPSRef.value[currentFrame].lat]
            },
            'properties': {}
        }
        let coordinateActive = feature.geometry.coordinates
        alongPath.value = alongPath.value.concat([coordinateActive])
        if (dataGPSRef.value[currentFrame - 1] != null) {
            let coordinate_last = [dataGPSRef.value[currentFrame - 1].lon, dataGPSRef.value[currentFrame - 1].lat]
            var bearing = turf.bearing(
                turf.point(coordinate_last),
                turf.point(coordinateActive)
            )
            feature.properties["bearing"] = bearing
            bearingRef.value = bearing
            mapRef.value.panTo(coordinateActive, { animate: true, essential: true, curve: 1.42, duration: 100, pitch: 60, bearing: bearing, zoom: 17 })
            if (mapRef.value.getSource('locationMarker')) {
                featureLocationMarker.value = feature
                mapRef.value.getSource('locationMarker').setData(feature)
            }
            if (alongPath.value.length > 1) {
                if (mapRef.value.getSource("LocationHistory")) {
                    featureLocationHistory.value = {
                        type: "FeatureCollection",
                        features: [turf.lineString(alongPath.value)]
                    }
                    mapRef.value.getSource("LocationHistory").setData(featureLocationHistory.value)
                }
            }
        }

    }

}

function initMap() {
    let apiKey = store.state.apiKeyMap
    mapRef.value = new maplibregl.Map({
        container: 'map',
        center: [108.485, 16.449],
        zoom: 5.43
    })
    let mapOSMNight = new ekmapplf.VectorBaseMap("OSM:Night", apiKey).addTo(mapRef.value)
    let basemapControl = new ekmapplf.control.BaseMap({
        id: "basemap_control",
        baseLayers: [
            {
                id: "OSM:Night",
                title: "Night basemap",
                thumbnail: "https://docs.ekgis.vn/assets/dem-map.png",
                width: "50px",
                height: "50px",
            },
            {
                id: "OSM:Bright",
                title: "Bright basemap",
                thumbnail: "https://docs.ekgis.vn/assets/map-sang.png",
                width: "50px",
                height: "50px",
            },
            {
                id: "OSM:Standard",
                title: "Basemap Standard",
                thumbnail: "https://docs.ekgis.vn/assets/map-chuan.png",
                width: "50px",
                height: "50px",
            },
            {
                id: 'satellite',
                title: 'Vệ tinh',
                thumbnail: 'https://files.ekgis.vn/widget/v1.0.0/assets/image/satellite.png',
                width: '50px',
                height: '50px'
            }
        ],
    })
    mapRef.value.addControl(basemapControl, "top-left")
    basemapControl.on("changeBaseLayer", async function (response) {
        if(response.layer != "satellite"){
            await new ekmapplf.VectorBaseMap(response.layer, apiKey).addTo(mapRef.value)
            mapRef.value.once('styledata', () => {
                onAddLayerSatellite()
                onAddLayerLine(geojsonRef.value)
                onAddLayerCar()
                onAddLayerHistorialPath()
                if(bearingRef.value != null){
                    mapRef.value.panTo(mapRef.value.getCenter(), { animate: true, essential: true, curve: 1.42, duration: 100, pitch: 60, bearing: bearingRef.value, zoom: 17 })
                }
            })
        }else{
            let layers = mapRef.value.getStyle().layers
            for(let i = 0; i < layers.length; i++){
                if(["l_satellite", "l_line_gps", "locationMarker", "LocationHistory"].includes(layers[i].id)){
                    mapRef.value.setLayoutProperty(layers[i].id, 'visibility', 'visible')
                }else{
                    mapRef.value.setLayoutProperty(layers[i].id, 'visibility', 'none')
                }
            }
        }
        
    })
    mapRef.value.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "bottom-right")
    var is3DMap = false;
    if (mapRef.value.getPitch() > 0) is3DMap = true;
    else is3DMap = false;
    var cl = "maplibregl-terrain2d-control";
    var tl = "2D display";
    if (!is3DMap) {
        cl = "maplibregl-terrain3d-control";
        tl = "3D map";
    }
    let btn3D = new ekmapplf.control.Button({
        className: "btn-ctl-group " + cl,
        icon: "none",
        tooltip: tl,
    });
    btn3D.on("click", (btn) => {
        is3DMap = !is3DMap;
        if (is3DMap) {
            btn._div.className = btn._div.className.replaceAll(
                "maplibregl-terrain3d-control",
                "maplibregl-terrain2d-control"
            );
            btn._div.title = "2D display";
        } else {
            btn._div.className = btn._div.className.replaceAll(
                "maplibregl-terrain2d-control",
                "maplibregl-terrain3d-control"
            );
            btn._div.title = "3D display";
        }
        if (is3DMap) {
            mapRef.value.easeTo({ pitch: 60 });
            mapRef.value.setLayoutProperty("building-3d", "visibility", "visible");
        } else {
            mapRef.value.easeTo({ pitch: 0 });
            mapRef.value.setLayoutProperty("building-3d", "visibility", "none");
        }
    });
    mapRef.value.addControl(btn3D, "bottom-right");
}

function onAddLayerSatellite(){
    if(!mapRef.value.getSource("s_satellite")){
        mapRef.value.addSource("s_satellite", {
            "type": "raster",
            "tileSize": 256,
            "tiles": [
                "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
            ]
        })
        mapRef.value.addLayer({
            "id": "l_satellite",
            "type": "raster",
            "source": "s_satellite",
            "minzoom": 0,
            "maxzoom": 22,
            "layout": {
                "visibility": "none"
            }
        })
    }
}

function onAddLayerLine(geojson) {
    if (mapRef.value.getSource('s_line_gps')) {
        mapRef.value.getSource('s_line_gps').setData(geojson)
    } else {
        mapRef.value.addSource("s_line_gps", {
            type: "geojson",
            data: geojson
        })
        mapRef.value.addLayer({
            'id': "l_line_gps",
            'type': 'line',
            'source': "s_line_gps",
            'layout': {
                'line-join': 'round',
                'line-cap': 'round'
            },
            'paint': {
                'line-color': '#888',
                'line-width': 8
            }
        })
    }
    let arrLine = geojson.geometry.coordinates
    if (arrLine.length > 0) {
        let line = turf.lineString(arrLine)
        let bbox = turf.bbox(line)
        mapRef.value.fitBounds(bbox, {
            padding: { top: 50, bottom: 50, left: 25, right: 35 }
        })
    }
}

function onAddLayerCar() {
    let icon_navigation = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" width="26px" height="32px" style="shape-rendering:geometricPrecision; text-rendering:geometricPrecision; image-rendering:optimizeQuality; fillRule:evenodd; clipRule:evenodd"><g><path style="opacity:0.998" fill="#43c5fb" d="M 16.5,9.5 C 17.1052,14.0317 18.7719,18.0317 21.5,21.5C 22.0081,24.1761 22.1747,26.8428 22,29.5C 21.3292,28.7476 20.4959,28.4142 19.5,28.5C 18.0085,25.3657 15.5085,23.3657 12,22.5C 10.2509,22.7483 9.41755,23.7483 9.5,25.5C 6.83333,26.5 4.16667,27.5 1.5,28.5C 2.95475,22.6465 5.12141,16.9799 8,11.5C 8.56704,8.83228 9.06704,6.16562 9.5,3.5C 10.4674,2.19376 11.8007,1.52709 13.5,1.5C 13.7329,4.54176 14.7329,7.20843 16.5,9.5 Z"/></g><g><path style="opacity:0.357" fill="#bfe2ee" d="M 16.5,9.5 C 14.7329,7.20843 13.7329,4.54176 13.5,1.5C 11.8007,1.52709 10.4674,2.19376 9.5,3.5C 9.5,2.5 9.5,1.5 9.5,0.5C 11.1667,0.5 12.8333,0.5 14.5,0.5C 15.4608,3.42607 16.1274,6.42607 16.5,9.5 Z"/></g><g><path style="opacity:0.224" fill="#afdcf1" d="M 16.5,9.5 C 19.2367,12.9831 20.9034,16.9831 21.5,21.5C 18.7719,18.0317 17.1052,14.0317 16.5,9.5 Z"/></g><g><path style="opacity:0.306" fill="#c2e3f4" d="M 9.5,3.5 C 9.06704,6.16562 8.56704,8.83228 8,11.5C 5.12141,16.9799 2.95475,22.6465 1.5,28.5C 4.16667,27.5 6.83333,26.5 9.5,25.5C 7.68383,27.1366 5.68383,28.6366 3.5,30C 2.07153,30.5791 0.738195,30.4124 -0.5,29.5C -0.5,28.1667 -0.5,26.8333 -0.5,25.5C 2.83333,18.1667 6.16667,10.8333 9.5,3.5 Z"/></g><g><path style="opacity:0.831" fill="#ade2fd" d="M 19.5,28.5 C 16.6277,27.4744 14.1277,25.8077 12,23.5C 11.2917,24.3805 10.4584,25.0472 9.5,25.5C 9.41755,23.7483 10.2509,22.7483 12,22.5C 15.5085,23.3657 18.0085,25.3657 19.5,28.5 Z"/></g><g><path style="opacity:0.047" fill="#c4e9f7" d="M 21.5,21.5 C 23.4725,24.0836 24.4725,27.0836 24.5,30.5C 22.302,30.8799 20.6354,30.2132 19.5,28.5C 20.4959,28.4142 21.3292,28.7476 22,29.5C 22.1747,26.8428 22.0081,24.1761 21.5,21.5 Z"/></g></svg>`
    if (!mapRef.value.getImage("marker_navigation")) {
        var marker_navigation = new Image()
        marker_navigation.onload = function () {
            if (!mapRef.value.hasImage("marker_navigation"))
                mapRef.value.addImage("marker_navigation", marker_navigation);
        }
        marker_navigation.src =
            "data:image/svg+xml;charset=utf-8;base64," +
            btoa(icon_navigation);
    }
    var locationMarker = featureLocationMarker.value
    if (!mapRef.value.getSource("locationMarker")) {
        mapRef.value.addSource("locationMarker", {
            type: "geojson",
            data: locationMarker,
        })
        mapRef.value.addLayer({
            id: "locationMarker",
            source: "locationMarker",
            type: "symbol",
            layout: {
                "icon-size": 0.7,
                "icon-offset": [0, -10],
                "icon-allow-overlap": true,
                "icon-image": "marker_navigation",
                "icon-rotate": ["get", "bearing"],
                "icon-rotation-alignment": "map",
                "icon-overlap": "always",
                "icon-ignore-placement": true,
            },
        })
    } else {
        mapRef.value.getSource("locationMarker").setData(locationMarker)
    }
}

function onAddLayerHistorialPath() {
    let fHistorialPath = featureLocationHistory.value
    if (!mapRef.value.getSource("LocationHistory")) {
        mapRef.value.addSource("LocationHistory", {
            type: "geojson",
            data: fHistorialPath
        })
        mapRef.value.addLayer({
            id: "LocationHistory",
            type: "line",
            source: "LocationHistory",
            layout: {
                "line-cap": "round",
                "line-join": "round",
            },
            paint: {
                "line-color": "#29b55c",
                "line-width": 6.5,
                "line-opacity": 0.85,
            },
            filter: ["==", "$type", "LineString"]
        })
    } else {
        mapRef.value.getSource("LocationHistory").setData(fHistorialPath)
    }
}

onBeforeUnmount(() => {
    loading.value = true
    src.value = ""
    type.value = ""
})
</script>
<style>
#basemap_control{
    max-width: 100% !important;
}
</style>