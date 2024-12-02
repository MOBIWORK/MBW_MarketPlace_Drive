<template>
    <div class="w-full h-full flex flex-col" :class="showDetailInfoPoint ? 'lg:flex-row' : ''">
        <div id="mapPreviewID" class="relative w-full" :class="showDetailInfoPoint ? 'h-3/5 lg:h-full lg:w-3/4' : 'h-full'">
            <LoadingIndicator v-if="loading" class="w-10 h-full text-neutral-100 mx-auto z-50" />
        </div>
        <div class="w-full h-auto bg-white lg:h-full lg:w-1/4" v-if="showDetailInfoPoint">
            <div class="w-full h-[200px] relative">
                <img draggable="false" class="h-full w-full" :src="detailInfoPoint.image" id-="" />
                <div class="absolute top-2 right-2 z-50 rounded-full cursor-pointer bg-white p-1 shadow-md hover:bg-gray-200 transition" @click="onCloseDetailPoint">
                    <FeatherIcon name="x" class="w-5 h-5 text-gray-800" />
                </div>
                <div class="absolute -bottom-3 left-2/4 transform -translate-x-2/4 rounded-md bg-white p-1 shadow-md w-16 h-7 flex">
                    <div class="flex justify-between items-center w-full">
                        <FeatherIcon name="chevron-left" class="w-5 h-5 text-gray-800 cursor-pointer" @click="onNextItem"/>
                        <FeatherIcon name="chevron-right" class="w-5 h-5 text-gray-800 cursor-pointer" @click="onPreItem"/>
                    </div>
                </div>
            </div>
            <div class="w-full flex mt-5 ml-2 items-center" v-if="detailInfoPoint.longitude != null && detailInfoPoint.latitude != null">
                <FeatherIcon name="map-pin" class="w-5 h-5 mr-2" />
                <div class="text-base">
                    <span>{{detailInfoPoint.longitude}}</span>
                    <span>&nbsp;</span>
                    <span>{{detailInfoPoint.latitude}}</span>
                </div>
            </div>
            <div class="w-full flex mt-3 ml-2 items-center" v-if="detailInfoPoint.area_real != null">
                <FeatherIcon name="hexagon" class="w-5 h-5 mr-2" />
                <div class="text-base">
                    <span>{{detailInfoPoint.area_real}}</span>
                    <span>&nbsp;</span>
                    <span>m</span><sup>2</sup>
                </div>
            </div>
        </div>
    </div>


    <Dialog v-model="showPropertiesDialog" :options="{
        size: '3xl',
        title: 'Attributes',
    }">
        <template #body-content>
            <ListView class="max-h-[350px]" :columns="columns" :rows="dataProperties" :options="{
                selectable: false,
                showTooltip: true,
                resizeColumn: true,
                emptyState: {
                    title: 'There are no records'
                }
            }" row-key="ID">
                <ListHeader class="mx-5" />
                <ListRows id="list-rows">
                    <ListRow
                        class="mx-5"
                        v-for="row in dataProperties"
                        :key="row.ID"
                        v-slot="{ idx, column, item }"
                        :row="row"
                    >
                        <template v-if="column.key == 'image'">
                            <a :href="row.image" target="_blank" style="text-decoration: underline;color: rgb(14 165 233);">Link</a>
                        </template>
                        <template v-else>
                            {{row[column.key]}}
                        </template>
                    </ListRow>
                </ListRows>
            </ListView>
        </template>
    </Dialog>
</template>

<script setup>
import { LoadingIndicator, Dialog, ListView, ListRows, ListHeader, ListRow, FeatherIcon } from "frappe-ui"
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useStore } from "vuex"

const props = defineProps({
    previewEntity: {
        type: Object,
        default: null,
    },
})
const store = useStore()
const loading = ref(true)
const mapPreview = ref(true)
const contentGeoJson = ref(null)
const indexFeatureActivate = ref(0)

//Biến Bảng thuộc tính
const showPropertiesDialog = ref(false)
const dataProperties = ref([])
const columns = ref(
    [
        {
            label: 'ID',
            key: 'ID',
            width: '50px'
        },
        {
            label: 'Acreage(m)',
            key: 'area_real'
        },
        {
            label: 'Acreage(pixel)',
            key: 'area_pixel'
        },
        {
            label: 'Image',
            key: 'image'
        }
    ]
)

//Biến tra cứu một điểm trên bản đồ
const popupQueryInfo = ref(null)
const showDetailInfoPoint = ref(false)
const detailInfoPoint = ref(null)

watch(props.previewEntity, () => {
    loading.value = true
    fetchContent()
})

watch(showDetailInfoPoint, async () => {
    if (mapPreview.value) {
        await nextTick()
        mapPreview.value.resize()
    }
})

async function fetchContent() {
    loading.value = false
    const headers = {
        Accept: "application/json",
        "Content-Type": "application/json; charset=utf-8",
        "X-Frappe-Site-Name": window.location.hostname,
    }
    const res = await fetch(
        `/api/method/drive.api.files.get_file_content?entity_name=${props.previewEntity.name}`,
        {
            method: "GET",
            headers,
        }
    )
    let objRes = await res.json()
    if (res.ok) {
        contentGeoJson.value = objRes
        if (mapPreview.value.isStyleLoaded()) {
            if (contentGeoJson.value != null) onAddLayer()
        } else {
            mapPreview.value.on("load", () => {
                if (contentGeoJson.value != null) onAddLayer()
            })
        }
    }
    loading.value = false
}

function initMap() {
    let apiKey = store.state.apiKeyMap
    mapPreview.value = new maplibregl.Map({
        container: 'mapPreviewID',
        center: [108.485, 16.449],
        zoom: 5.43
    })
    let mapOSMNight = new ekmapplf.VectorBaseMap("OSM:Night", apiKey).addTo(mapPreview.value)
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
        ],
    })
    mapPreview.value.addControl(basemapControl, "bottom-left")
    basemapControl.on("changeBaseLayer", async function (response) {
        await new ekmapplf.VectorBaseMap(response.layer, apiKey).addTo(mapPreview.value)
        mapPreview.value.once("load", () => {
            onAddLayer()
        })
    })
    mapPreview.value.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "bottom-right")
    var is3DMap = false;
    if (mapPreview.value.getPitch() > 0) is3DMap = true;
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
            mapPreview.value.easeTo({ pitch: 60 });
            mapPreview.value.setLayoutProperty("building-3d", "visibility", "visible");
        } else {
            mapPreview.value.easeTo({ pitch: 0 });
            mapPreview.value.setLayoutProperty("building-3d", "visibility", "none");
        }
    });
    mapPreview.value.addControl(btn3D, "bottom-right");

    let btnProperties = new ekmapplf.control.Button({
        className: "btn-ctl-group icon_properties",
        icon: "",
        tooltip: "Attributes"
    })
    btnProperties.on("click", (btn) => {
        showPropertiesDialog.value = true
    })
    mapPreview.value.addControl(btnProperties, "bottom-right")

    let btnQueryPoint = new ekmapplf.control.Button({
        className: "btn-ctl-group icon_query_point",
        icon: "",
        tooltip: "Look up one-point information"
    })
    btnQueryPoint.on('click', (btn) => {
        initPopupQueryInfo()
        mapPreview.value.on('mousemove', showPopupControl)
        mapPreview.value.on('click', clickInfoPoint)
        mapPreview.value.getCanvas().style.cursor = 'pointer'
    })
    mapPreview.value.addControl(btnQueryPoint, "bottom-right")
}

function initPopupQueryInfo() {
    if (popupQueryInfo.value == null) {
        let markerHeight = 40;
        let markerRadius = 40;
        let linearOffset = 25;
        popupQueryInfo.value = new maplibregl.Popup({
            offset: {
                'top': [0, 20],
                'top-left': [0, 0],
                'top-right': [0, 0],
                'bottom': [0, -markerHeight],
                'bottom-left': [linearOffset, (markerHeight - markerRadius + linearOffset) * -1],
                'bottom-right': [-linearOffset, (markerHeight - markerRadius + linearOffset) * -1],
                'left': [markerRadius, (markerHeight - markerRadius) * -1],
                'right': [-markerRadius, (markerHeight - markerRadius) * -1]
            },
            anchor: 'left',
            closeButton: false,
            closeOnClick: false
        }).addTo(mapPreview.value)
    }
}

function showPopupControl(evt) {
    popupQueryInfo.value.setLngLat([evt.lngLat.lng, evt.lngLat.lat]).setHTML('<span class="text-sm">Click on the location to look up information</span>')
}

function clickInfoPoint(evt) {
    mapPreview.value.off('mousemove', showPopupControl)
    mapPreview.value.off('click', clickInfoPoint)
    mapPreview.value.getCanvas().style.cursor = ''
    if (popupQueryInfo.value != null) {
        popupQueryInfo.value.remove()
        popupQueryInfo.value = null
    }
    let features = mapPreview.value.queryRenderedFeatures(evt.point, { layers: ['l_object_detect'] })
    if (features.length > 0) {
        for(let i = 0; i < dataProperties.value.length; i++){
            let item = dataProperties.value[i]
            if(item["longitude"] == features[0].properties["longitude"] && item["latitude"] == features[0].properties["latitude"]){
                indexFeatureActivate.value = i
                break
            }
        }
        const sizeAnimateCircle = 100
        const pulsingDot= {
            width: sizeAnimateCircle,
            height: sizeAnimateCircle,
            data: new Uint8Array(sizeAnimateCircle*sizeAnimateCircle*4),
            onAdd(){
                const canvas = document.createElement('canvas')
                canvas.width = this.width
                canvas.height = this.height
                this.context = canvas.getContext('2d')
            },
            render() {
                const duration = 1000
                const t = (performance.now() % duration) / duration
                const radius = (sizeAnimateCircle / 2) * 0.3
                const outerRadius = (sizeAnimateCircle / 2) * 0.7 * t + radius
                const context = this.context
                // draw outer circle
                context.clearRect(0, 0, this.width, this.height)
                context.beginPath()
                context.arc(
                    this.width / 2,
                    this.height / 2,
                    outerRadius,
                    0,
                    Math.PI * 2
                )
                context.fillStyle = `rgba(153, 196, 219,${1 - t})`
                context.fill()
                // draw inner circle
                context.beginPath()
                context.arc(
                    this.width / 2,
                    this.height / 2,
                    radius,
                    0,
                    Math.PI * 2
                )
                context.fillStyle = 'rgba(0, 124, 191, 1)'
                context.strokeStyle = 'white'
                context.lineWidth = 2 + 4 * (1 - t)
                context.fill()
                context.stroke()
                this.data = context.getImageData(
                    0,
                    0,
                    this.width,
                    this.height
                ).data
                // continuously repaint the map, resulting in the smooth animation of the dot
                mapPreview.value.triggerRepaint()
                // return `true` to let the map know that the image was updated
                return true
            }
        }
        if(mapPreview.value.getSource("s_object_detect_activate")){
            mapPreview.value.getSource("s_object_detect_activate").setData(features[0])
        }else{
            if(!mapPreview.value.getImage("pulsing-dot")) mapPreview.value.addImage('pulsing-dot', pulsingDot, {pixelRatio: 2})
            mapPreview.value.addSource("s_object_detect_activate", {
                'type': "geojson",
                'data': features[0]
            })
            mapPreview.value.addLayer({
                'id': "l_object_detect_activate",
                'type': "symbol",
                'source': "s_object_detect_activate",
                'layout': {
                    'icon-image': "pulsing-dot"
                }
            })
        }
        detailInfoPoint.value = features[0].properties
        showDetailInfoPoint.value = true
    } else {
        detailInfoPoint.value = null
        showDetailInfoPoint.value = false
    }
}

function onNextItem(){
    if(indexFeatureActivate.value + 1 < dataProperties.value.length){
        indexFeatureActivate.value += 1
        onShowDetailAndLayerItemNextAndPre()
    }
}

function onPreItem(){
    if(indexFeatureActivate.value -1 >= 0){
        indexFeatureActivate.value -= 1
        onShowDetailAndLayerItemNextAndPre()
    }
}

function onShowDetailAndLayerItemNextAndPre(){
    let item = dataProperties.value[indexFeatureActivate.value]
    if(item != null){
        let featureData = {
            'type': "Feature",
            'geometry': {
                'type': "Point",
                'coordinates': [item["longitude"], item["latitude"]]
            },
            'properties': item
        }
        mapPreview.value.getSource("s_object_detect_activate").setData(featureData)
        detailInfoPoint.value = item
        mapPreview.value.flyTo({
            'center': [item["longitude"], item["latitude"]]
        })
    }
}

function onAddLayer() {
    if (mapPreview.value.getSource("s_object_detect")) {
        mapPreview.value.getSource("s_object_detect").setData(contentGeoJson.value)
    } else {
        mapPreview.value.addSource("s_object_detect", {
            type: "geojson",
            data: contentGeoJson.value
        })
        mapPreview.value.addLayer({
            id: "l_object_detect",
            type: "circle",
            source: "s_object_detect",
            paint: {
                "circle-color": "#007cbf",
                "circle-radius": 7,
                // "circle-stroke-color": "#90D667",
                // "circle-stroke-width": 2
            }
        })
    }
    let arrLine = []
    let arrProperties = []
    for (let i = 0; i < contentGeoJson.value.features.length; i++) {
        let geometry = contentGeoJson.value.features[i]["geometry"]
        let properties = contentGeoJson.value.features[i]["properties"]
        arrLine.push(geometry["coordinates"])
        properties["ID"] = i + 1
        arrProperties.push(properties)
    }
    if (arrLine.length > 0) {
        let line = turf.lineString(arrLine)
        let bbox = turf.bbox(line)
        mapPreview.value.fitBounds(bbox, {
            padding: { top: 50, bottom: 50, left: 25, right: 35 }
        })
    }
    dataProperties.value = arrProperties
}

function onCloseDetailPoint() {
    detailInfoPoint.value = null
    showDetailInfoPoint.value = false
    if(mapPreview.value.getSource("s_object_detect_activate")){
        mapPreview.value.removeLayer("l_object_detect_activate")
        mapPreview.value.removeSource("s_object_detect_activate")
    }
    indexFeatureActivate.value = 0
}

onMounted(() => {
    initMap()
    fetchContent()
})

onBeforeUnmount(() => {
    mapPreview.value.off('mousemove', showPopupControl)
    loading.value = true
    contentGeoJson.value = true
    showPropertiesDialog.value = false
})
</script>

<style>
.icon_properties {
    background-position: center;
    background-repeat: no-repeat;
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJmZWF0aGVyIGZlYXRoZXItdGFibGUiPjxwYXRoIGQ9Ik05IDNINWEyIDIgMCAwIDAtMiAydjRtNi02aDEwYTIgMiAwIDAgMSAyIDJ2NE05IDN2MThtMCAwaDEwYTIgMiAwIDAgMCAyLTJWOU05IDIxSDVhMiAyIDAgMCAxLTItMlY5bTAgMGgxOCI+PC9wYXRoPjwvc3ZnPg==")
}

.icon_query_point {
    background-position: center;
    background-repeat: no-repeat;
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJmZWF0aGVyIGZlYXRoZXItaW5mbyI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiPjwvY2lyY2xlPjxsaW5lIHgxPSIxMiIgeTE9IjE2IiB4Mj0iMTIiIHkyPSIxMiI+PC9saW5lPjxsaW5lIHgxPSIxMiIgeTE9IjgiIHgyPSIxMi4wMSIgeTI9IjgiPjwvbGluZT48L3N2Zz4=");
}
</style>