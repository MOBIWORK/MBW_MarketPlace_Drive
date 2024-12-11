<template>
    <div class="w-full h-full flex flex-col lg:flex-row">
        <div id="mapPreviewID" class="relative w-full h-3/5 lg:h-full lg:w-8/12">
            <LoadingIndicator v-if="loading" class="w-10 h-full text-neutral-100 mx-auto z-50" />
        </div>
        <div class="w-full h-auto bg-white lg:h-full lg:w-4/12">
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
                    <div class="p-1 h-full" v-if="tab.name == 'table'">
                        <ListView class="h-full" :columns="columns" :rows="dataProperties" :options="{
                            selectable: false,
                            showTooltip: true,
                            resizeColumn: true,
                            emptyState: {
                                title: 'There are no records'
                            },
                            onRowClick: (row) => onActiveRow(row)
                        }" row-key="ID">
                            <ListHeader class="mx-0" />
                            <ListRows id="list-rows">
                                <ListRow class="mx-0" v-for="row in dataProperties" :key="row.ID"
                                    v-slot="{ idx, column, item }" :row="row">
                                    <template v-if="column.key == 'image'">
                                        <a :href="row.image" target="_blank"
                                            style="text-decoration: underline;color: rgb(14 165 233);">Link</a>
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
        label: 'Table',
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

const geojsonStringfyRef = ref("")

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
        console.log(objRes)
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
    mapPreview.value.getCanvas().style.cursor = 'pointer'
    mapPreview.value.on('click', 'l_object_detect', clickInfoPointPopup)
}

function clickInfoPointPopup(evt) {
    if (popupQueryInfo.value != null) {
        popupQueryInfo.value.remove()
    }
    // let features = mapPreview.value.queryRenderedFeatures(evt.point, { layers: ['l_object_detect'] })
    // if (features.length > 0) {
    //     const coordinates = evt.features[0].geometry.coordinates.slice()
    //     const properties = evt.features[0].properties
    //     const description = `
    //         <div class="w-52 h-36">
    //             <img draggable="false" class="h-full w-full" src=${properties.image} id-="" />
    //         </div>
    //     `
    //     while (Math.abs(evt.lngLat.lng - coordinates[0]) > 180) {
    //         coordinates[0] += evt.lngLat.lng > coordinates[0] ? 360 : -360;
    //     }
    //     new maplibregl.Popup({closeButton: false})
    //         .setLngLat(coordinates)
    //         .setHTML(description)
    //         .addTo(mapPreview.value);
    // }
}

function onActiveRow(row){
    let feature = {
        type: "Feature",
        geometry: {
            type: "Point",
            coordinates: [row.longitude, row.latitude]
        }
    }
    onAddLayerActivateRow(feature)
    mapPreview.value.flyTo({
        center: [row.longitude, row.latitude]
    })
}

function onAddLayerActivateRow(feature) {
    const sizeAnimateCircle = 100
    const pulsingDot = {
        width: sizeAnimateCircle,
        height: sizeAnimateCircle,
        data: new Uint8Array(sizeAnimateCircle * sizeAnimateCircle * 4),
        onAdd() {
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
    if (mapPreview.value.getSource("s_object_detect_activate")) {
        mapPreview.value.getSource("s_object_detect_activate").setData(feature)
    } else {
        if (!mapPreview.value.getImage("pulsing-dot")) mapPreview.value.addImage('pulsing-dot', pulsingDot, { pixelRatio: 2 })
        mapPreview.value.addSource("s_object_detect_activate", {
            'type': "geojson",
            'data': feature
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
        title: "Copy successfully",
        position: "bottom-right",
        timeout: 2,
    })
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
