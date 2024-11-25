<template>
    <div class="w-full h-full flex">
        <div id="mapPreviewID" class="h-full relative" :class="showDetailInfoPoint? 'w-3/4' : 'w-full'">
            <LoadingIndicator v-if="loading" class="w-10 h-full text-neutral-100 mx-auto z-50" />
        </div>
        <div class="h-full w-1/4" v-if="showDetailInfoPoint">
            <div class="w-full flex justify-between">
                <div>Kết quả tra cứu</div>
                <Button icon="x" variant="ghost" @click="onCloseDetailPoint" />
            </div>
        </div>
    </div>
    

    <Dialog v-model="showPropertiesDialog" :options="{
        size: '3xl',
        title: 'Bảng thuộc tính',
    }">
        <template #body-content>
            <ListView class="max-h-[350px]" :columns="[
                {
                    label: 'ID',
                    key: 'ID',
                    width: '50px'
                },
                {
                    label: 'Diện tích(m)',
                    key: 'area_real'
                },
                {
                    label: 'Diện tích(pixel)',
                    key: 'area_pixel'
                },
                {
                    label: 'Ảnh',
                    key: 'image '
                }
            ]" :rows="dataProperties" :options="{
                selectable: false,
                showTooltip: true,
                resizeColumn: true,
                emptyState: {
                    title: 'Không có bản ghi'
                }
            }" 
            row-key="ID">
                
            </ListView>
        </template>
    </Dialog>
</template>

<script setup>
import { LoadingIndicator, Dialog, ListView, ListRows } from "frappe-ui"
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

//Biến Bảng thuộc tính
const showPropertiesDialog = ref(false)
const dataProperties = ref([])

//Biến tra cứu một điểm trên bản đồ
const popupQueryInfo = ref(null)
const showDetailInfoPoint = ref(false)
const detailInfoPoint = ref(null)

watch(props.previewEntity, () => {
    loading.value = true
    fetchContent()
})

watch(showDetailInfoPoint, async () => {
    if(mapPreview.value){
        await nextTick()
        mapPreview.value.resize()
        console.log(mapPreview)
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
                title: "Bản đồ nền Đêm",
                thumbnail: "https://docs.ekgis.vn/assets/dem-map.png",
                width: "50px",
                height: "50px",
            },
            {
                id: "OSM:Bright",
                title: "Bản đồ nền Sáng",
                thumbnail: "https://docs.ekgis.vn/assets/map-sang.png",
                width: "50px",
                height: "50px",
            },
            {
                id: "OSM:Standard",
                title: "Bản đồ nền Tiêu chuẩn",
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
    var tl = "Hiển thị 2D";
    if (!is3DMap) {
        cl = "maplibregl-terrain3d-control";
        tl = "Bản đồ 3D";
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
            btn._div.title = "Hiển thị 2D";
        } else {
            btn._div.className = btn._div.className.replaceAll(
                "maplibregl-terrain2d-control",
                "maplibregl-terrain3d-control"
            );
            btn._div.title = "Hiển thị 3D";
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
        tooltip: "Bảng thuộc tính"
    })
    btnProperties.on("click", (btn) => {
        showPropertiesDialog.value = true
    })
    mapPreview.value.addControl(btnProperties, "bottom-right")

    let btnQueryPoint = new ekmapplf.control.Button({
        className: "btn-ctl-group icon_query_point",
        icon: "",
        tooltip: "Tra cứu thông tin một điểm"
    })
    btnQueryPoint.on('click', (btn) => {
        initPopupQueryInfo()
        mapPreview.value.on('mousemove', showPopupControl)
        mapPreview.value.on('click', clickInfoPoint)
        mapPreview.value.getCanvas().style.cursor = 'pointer'
    })
    mapPreview.value.addControl(btnQueryPoint, "bottom-right")
}

function initPopupQueryInfo(){  
    if(popupQueryInfo.value == null){
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

function showPopupControl(evt){
    popupQueryInfo.value.setLngLat([evt.lngLat.lng, evt.lngLat.lat]).setHTML('<span>Click vào vị trí để tra cứu thông tin</span>')
}

function clickInfoPoint(evt){
    mapPreview.value.off('mousemove', showPopupControl)
    mapPreview.value.off('click', clickInfoPoint)
    mapPreview.value.getCanvas().style.cursor = ''
    if(popupQueryInfo.value != null){
        popupQueryInfo.value.remove()
    }
    let features = mapPreview.value.queryRenderedFeatures(evt.point, {layers: ['l_object_detect']})
    showDetailInfoPoint.value = true
    if(features.length > 0){
        detailInfoPoint.value = features[0].properties
    }else{
        detailInfoPoint.value = null
    }
    console.log("Dòng 253 ", features)
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
        properties["ID"] = i+1
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

function onCloseDetailPoint(){
    detailInfoPoint.value = null
    showDetailInfoPoint.value = false
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
.icon_query_point{
    background-position: center;
    background-repeat: no-repeat;
    background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9ImN1cnJlbnRDb2xvciIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIGNsYXNzPSJmZWF0aGVyIGZlYXRoZXItaW5mbyI+PGNpcmNsZSBjeD0iMTIiIGN5PSIxMiIgcj0iMTAiPjwvY2lyY2xlPjxsaW5lIHgxPSIxMiIgeTE9IjE2IiB4Mj0iMTIiIHkyPSIxMiI+PC9saW5lPjxsaW5lIHgxPSIxMiIgeTE9IjgiIHgyPSIxMi4wMSIgeTI9IjgiPjwvbGluZT48L3N2Zz4=");
}
</style>