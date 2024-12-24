<template>
    <div class="w-full h-full flex flex-col lg:flex-row">
        <div id="mapPreviewID" class="relative w-full h-3/5 lg:h-full lg:w-8/12">
            <LoadingIndicator v-if="loading" class="w-10 h-full text-neutral-100 mx-auto z-50" />
        </div>
        <div class="w-full h-full bg-white lg:h-full lg:w-4/12">
            <Tabs v-model="tabIndex" :tabs="tabsContent" class="w-full h-full">
                <template #default="{ tab }">
                    <div class="p-0 w-full h-full" v-if="tab.name == 'json'">
                        <div class="w-full h-full relative">
                            <Textarea :variant="'outline'" :ref_for="true" size="md" :disabled="true"
                                :modelValue="geojsonStringfyRef" class="w-full h-full" />
                            <div class="absolute top-0 right-3 p-2">
                                <Button :variant="'outline'" theme="gray" size="sm" @click="onCopyData">
                                    <FeatherIcon name="copy" class="w-4" />
                                </Button>
                            </div>
                        </div>
                    </div>
                    <div class="p-1 h-full flex flex-col" v-if="tab.name == 'table'">
                        <ListView class="h-full flex-1 overflow-auto" :columns="columns" :rows="dataProperties" :options="{
                            selectable: false,
                            showTooltip: true,
                            resizeColumn: true,
                            emptyState: {
                                title: __('There are no records')
                            },
                            onRowClick: (row) => onActiveRow(row)
                        }" row-key="ID">
                            <ListHeader class="mx-0" />
                            <ListRows id="list-rows">
                                <ListRow class="mx-0" :class="idRowActivateRef==row.ID? 'bg-[#F3F3F3]' : ''" v-for="row in dataProperties" :key="row.ID"
                                    v-slot="{ idx, column, item }" :row="row">
                                    <template v-if="column.key == 'image'">
                                        <a href="javascript:;" @click="openFullscreen(row.image)" class="z-50 w-full"
                                            style="text-decoration: underline;color: rgb(14 165 233);">{{__('Link')}}</a>
                                    </template>
                                    <template v-else>
                                        {{ row[column.key] }}
                                    </template>
                                </ListRow>
                            </ListRows>
                        </ListView>
                    </div>
                </template>
            </Tabs>
        </div>
    </div>
</template>

<script setup>
import { LoadingIndicator, Dialog, ListView, ListRows, ListHeader, ListRow, FeatherIcon, Tabs, Textarea, Button } from "frappe-ui"
import { ref, watch, onMounted, onBeforeUnmount, nextTick, h } from 'vue'
import { useStore } from "vuex"
import { toast } from "@/utils/toasts.js"

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
const tabIndex = ref(0)
const tabsContent = ref([
    {
        name: "json",
        label: 'JSON',
        icon: h(FeatherIcon, {
            name: "code",
            class: "h-4 w-4"
        })
    },
    {
        name: "table",
        label: __('Table'),
        icon: h(FeatherIcon, {
            name: "table",
            class: "h-4 w-4"
        })

    }
])

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
            label: __('Acreage(m)'),
            key: 'area_real'
        },
        {
            label: __('Acreage(pixel)'),
            key: 'area_pixel'
        },
        {
            label: __('Image'),
            key: 'image'
        }
    ]
)

const geojsonStringfyRef = ref("")
const idRowActivateRef = ref(null)

//Biến tra cứu một điểm trên bản đồ
const popupQueryInfo = ref(null)

watch(props.previewEntity, () => {
    loading.value = true
    fetchContent()
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
        geojsonStringfyRef.value = JSON.stringify(objRes, null, 4)
        if (mapPreview.value.isStyleLoaded()) {
            onAddLayerSatellite()
            if (contentGeoJson.value != null) onAddLayer()
        } else {
            mapPreview.value.on("load", () => {
                onAddLayerSatellite()
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
                title: __("Night basemap"),
                thumbnail: "https://docs.ekgis.vn/assets/dem-map.png",
                width: "50px",
                height: "50px",
            },
            {
                id: "OSM:Bright",
                title: __("Bright basemap"),
                thumbnail: "https://docs.ekgis.vn/assets/map-sang.png",
                width: "50px",
                height: "50px",
            },
            {
                id: "OSM:Standard",
                title: __("Basemap Standard"),
                thumbnail: "https://docs.ekgis.vn/assets/map-chuan.png",
                width: "50px",
                height: "50px",
            },
            {
                id: 'satellite',
                title: __('Satellite'),
                thumbnail: 'https://files.ekgis.vn/widget/v1.0.0/assets/image/satellite.png',
                width: '50px',
                height: '50px'
            }
        ],
    })
    mapPreview.value.addControl(basemapControl, "bottom-left")
    basemapControl.on("changeBaseLayer", async function (response) {
        if(response.layer != "satellite"){
            await new ekmapplf.VectorBaseMap(response.layer, apiKey).addTo(mapPreview.value)
            mapPreview.value.once("styledata", () => {
                onAddLayerSatellite()
                onAddLayer()
            })
        }else{
            let layers = mapPreview.value.getStyle().layers
            for(let i = 0; i < layers.length; i++){
                if(["l_satellite", "l_object_detect", "l_object_detect_activate"].includes(layers[i].id)){
                    mapPreview.value.setLayoutProperty(layers[i].id, 'visibility', 'visible')
                }else{
                    mapPreview.value.setLayoutProperty(layers[i].id, 'visibility', 'none')
                }
            }
        }
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
        tooltip: __(tl),
    });
    btn3D.on("click", (btn) => {
        is3DMap = !is3DMap;
        if (is3DMap) {
            btn._div.className = btn._div.className.replaceAll(
                "maplibregl-terrain3d-control",
                "maplibregl-terrain2d-control"
            );
            btn._div.title = __("2D display");
        } else {
            btn._div.className = btn._div.className.replaceAll(
                "maplibregl-terrain2d-control",
                "maplibregl-terrain3d-control"
            );
            btn._div.title = __("3D display");
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
    mapPreview.value.getCanvas().style.cursor = 'pointer'
    mapPreview.value.on('click', 'l_object_detect', clickInfoPointPopup)
}

function clickInfoPointPopup(evt) {
    let features = mapPreview.value.queryRenderedFeatures(evt.point, { layers: ['l_object_detect'] })
    if (features.length > 0) {
        let properties = features[0].properties
        let dataPropertisFilter = dataProperties.value.filter(x => x.longitude == properties.longitude && x.latitude == properties.latitude)
        if(dataPropertisFilter.length > 0){
            idRowActivateRef.value = dataPropertisFilter[0].ID
        }
        showInfoPopup(evt.features[0], evt.lngLat)
    }
}

function showInfoPopup(feature, lngLat){
    if (popupQueryInfo.value != null) {
        popupQueryInfo.value.remove()
    }
    const coordinates = feature.geometry.coordinates.slice()
    const properties = feature.properties
    const description = `
        <div class="w-52 h-36 relative group">
            <img draggable="false" class="h-full w-full object-cover" src="${properties.image}" alt="Image" />
            <!-- Fullscreen Icon -->
            <div id="fullscreen_icon"
                class="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer"
            >
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-maximize text-white"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path></svg>
            </div>
        </div>
    `
    if(lngLat != null){
        while (Math.abs(lngLat.lng - coordinates[0]) > 180) {
            coordinates[0] += lngLat.lng > coordinates[0] ? 360 : -360;
        }
    }
    popupQueryInfo.value = new maplibregl.Popup({closeButton: false})
            .setLngLat(coordinates)
            .setHTML(description)
            .addTo(mapPreview.value);
    document.getElementById("fullscreen_icon").addEventListener('click', () => {
        openFullscreen(properties.image)
    })
}

function onActiveRow(row){
    if(idRowActivateRef.value == row.ID){
        idRowActivateRef.value = null
        if(popupQueryInfo.value != null) popupQueryInfo.value.remove()
        return
    }else{
        idRowActivateRef.value = row.ID
    }
    let feature = {
        type: "Feature",
        geometry: {
            type: "Point",
            coordinates: [row.longitude, row.latitude]
        },
        properties: row
    }
    mapPreview.value.flyTo({
        center: [row.longitude, row.latitude]
    })
    showInfoPopup(feature)
}

function onAddLayerSatellite(){
    if(!mapPreview.value.getSource("s_satellite")){
        mapPreview.value.addSource("s_satellite", {
            "type": "raster",
            "tileSize": 256,
            "tiles": [
                "https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
            ]
        })
        mapPreview.value.addLayer({
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

function onAddLayer() {
    if(contentGeoJson.value == null){
        contentGeoJson.value = {
            type: "FeatureCollection",
            features: []
        }
    }
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

function onCopyData() {
    const textarea = document.createElement('textarea')
    textarea.value = geojsonStringfyRef.value
    document.body.appendChild(textarea)

    // Chọn nội dung và sao chép
    textarea.select()
    textarea.setSelectionRange(0, geojsonStringfyRef.value.length) // Đảm bảo chọn hết nội dung
    document.execCommand('copy')

    // Loại bỏ textarea khỏi DOM
    document.body.removeChild(textarea)
    toast({
        title: __("Copy successfully"),
        position: "bottom-right",
        timeout: 2,
    })
}

function openFullscreen(imageSrc) {
    // Tạo phần tử mới để hiển thị ảnh fullscreen
    const fullscreenDiv = document.createElement('div');
    fullscreenDiv.className = 'fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50';

    // Thêm ảnh vào fullscreenDiv
    fullscreenDiv.innerHTML = `
        <img src="${imageSrc}" class="max-h-full max-w-full object-contain" alt="Fullscreen Image" />
        <button id="btn-close-image" class="absolute top-4 right-4 text-white text-3xl font-bold">&times;</button>
    `;

    // Thêm fullscreenDiv vào body
    document.body.appendChild(fullscreenDiv);
    document.getElementById('btn-close-image').addEventListener("click", () => {
        closeFullscreen()
    })
}

function closeFullscreen() {
    // Xóa phần tử fullscreen
    const fullscreenDiv = document.querySelector('.fixed.inset-0');
    if (fullscreenDiv) {
        fullscreenDiv.remove();
    }
}

onMounted(() => {
    initMap()
    fetchContent()
})

onBeforeUnmount(() => {
    mapPreview.value.off('click', 'l_object_detect', clickInfoPointPopup)
    loading.value = true
    contentGeoJson.value = true
    showPropertiesDialog.value = false
})
</script>

<style>
#basemap_control{
    max-width: 100% !important;
}

.fixed {
    position: fixed;
  }

  .inset-0 {
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
  }

  .z-50 {
    z-index: 50;
  }

  .bg-opacity-90 {
    background-opacity: 0.9;
  }

  .absolute {
    position: absolute;
  }

  .top-4 {
    top: 1rem;
  }

  .right-4 {
    right: 1rem;
  }
</style>