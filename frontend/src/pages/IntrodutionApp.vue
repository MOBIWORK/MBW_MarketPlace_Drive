<template>
    <div ref="container" class="h-full w-full pt-3.5 px-4 pb-5 overflow-y-auto">
        <DriveToolBar :action-items="actionItems" :column-headers="showSort ? columnHeaders : null" />
        <GridView
            :folder-contents="groupedByFolder"
            :selected-entities="selectedEntities"
            :override-can-load-more="overrideCanLoadMore"
        />
        <div v-show="isBeforeViewResult">
            <div>
                <span
                    class="text-base text-gray-600 font-medium leading-6 pl-1 my-0"
                >
                    {{ __("Folders") }}
                </span>
                <div class="grid-container mt-2 mb-4">
                    <div class="rounded-lg border group select-none entity cursor-pointer relative group: p-3 w-[162px] sm:w-[172px] h-[98px] sm:h-[108px] border-gray-200" id="result-analysis">
                        <div>
                            <div class="flex items-start">
                                <svg
                                    class="h-7.5 w-auto"
                                    :draggable="false"
                                    :style="{ fill: 'rgb(82, 82, 82)' }"
                                    width="16"
                                    height="16"
                                    viewBox="0 0 16 16"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                >
                                    <g clip-path="url(#clip0_1942_59507)">
                                    <path
                                        d="M7.83412 2.88462H1.5C1.22386 2.88462 1 3.10847 1 3.38462V12.5C1 13.6046 1.89543 14.5 3 14.5H13C14.1046 14.5 15 13.6046 15 12.5V2C15 1.72386 14.7761 1.5 14.5 1.5H9.94008C9.88623 1.5 9.83382 1.51739 9.79065 1.54957L8.13298 2.78547C8.04664 2.84984 7.94182 2.88462 7.83412 2.88462Z"
                                    />
                                    </g>
                                    <defs>
                                    <clipPath id="clip0_1942_59507">
                                        <rect width="16" height="16" fill="white" />
                                    </clipPath>
                                    </defs>
                                </svg>
                            </div>
                            <div class="content-center grid mt-2 sm:mt-3.5">
                            <span class="truncate text-base font-medium text-gray-800">
                                Result_1735286278_20241128_100645_ER.mp4
                            </span>
                            <p :title="modified" class="truncate text-sm text-gray-600 mt-2">
                                {{ localizeRelativeModified("19 minutes ago") }}
                            </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div>
                <span
                    class="text-base text-gray-600 font-medium leading-6 pl-1 my-0"
                >
                    {{ __("Files") }}
                </span>
                <div class="grid-container mt-2 mb-4" id="input-data">
                    <div class="rounded-lg border group select-none entity cursor-pointer relative group: w-[162px] h-[162px] sm:w-[172px] sm:h-[172px]">
                        <div
                            class="h-2/3 flex items-center justify-center rounded-t-[calc(theme(borderRadius.lg)-1px)] overflow-hidden"
                            >
                            <ExampleThumb />
                        </div>
                        <div class="p-2 h-1/3 content-center grid border-t border-gray-100">
                            <span class="truncate text-base font-medium text-gray-800">
                                20241128_100645_ER.mp4
                            </span>
                            <div class="flex items-center justify-start mt-2">
                                <p class="truncate text-xs text-gray-600">
                                    77MB ∙ {{ localizeRelativeModified("36 minutes ago") }}
                                </p>
                            </div>
                        </div>
                    </div>
                    <div class="rounded-lg border group select-none entity cursor-pointer relative group: w-[162px] h-[162px] sm:w-[172px] sm:h-[172px]">
                        <div
                            class="h-2/3 flex items-center justify-center rounded-t-[calc(theme(borderRadius.lg)-1px)] overflow-hidden"
                            >
                            <UnknowThumb />
                        </div>
                        <div class="p-2 h-1/3 content-center grid border-t border-gray-100">
                            <span class="truncate text-base font-medium text-gray-800">
                                20241128_100645_ER.gpx
                            </span>
                            <div class="flex items-center justify-start mt-2">
                                <p class="truncate text-xs text-gray-600">
                                    230 KB ∙ {{ localizeRelativeModified("39 minutes ago") }}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import DriveToolBar from "@/components/DriveToolBar.vue"
import Share from "@/components/EspressoIcons/Share.vue"
import Download from "@/components/EspressoIcons/Download.vue"
import Link from "@/components/EspressoIcons/Link.vue"
import Rename from "@/components/EspressoIcons/Rename.vue"
import Move from "@/components/EspressoIcons/Move.vue"
import Info from "@/components/EspressoIcons/Info.vue"
import Star from "@/components/EspressoIcons/Star.vue"
import Preview from "@/components/EspressoIcons/Preview.vue"
import Trash from "@/components/EspressoIcons/Trash.vue"
import ExampleThumb from "@/components/EspressoIcons/ExampleThumb.vue"
import UnknowThumb from "@/components/EspressoIcons/UnknowThumb.vue"
import introJs from "intro.js";
import "intro.js/introjs.css";

export default {
    name: "IntrodutionApp",
    components: {
        DriveToolBar,
        ExampleThumb,
        UnknowThumb
    },
    data() {
        return {
            showSort: true,
            selectedEntities: [],
            overrideCanLoadMore: false,
            groupedByFolder: [],
            isBeforeViewResult: true
        }
    },
    computed: {
        actionItems() {
            return [
                {
                    label: __("Preview"),
                    icon: Preview,
                    isEnabled: () => {
                        return true
                    },
                },
                {
                    label: __("Download"),
                    icon: Download,
                    isEnabled: () => {
                        return true
                    },
                },
                {
                    label: __("Share"),
                    icon: Share,
                    isEnabled: () => {
                        return true
                    },
                },
                {
                    label: __("Get Link"),
                    icon: Link,
                    isEnabled: () => {
                        return true
                    },
                },
                {
                    label: __("Rename"),
                    icon: Rename,
                    isEnabled: () => {
                        return true
                    },
                },
                {
                    label: __("Move"),
                    icon: Move,
                    isEnabled: () => {
                        return true
                    },
                },
                {
                    label: __("Show Info"),
                    icon: Info,
                    isEnabled: () => {
                        return true
                    },
                },
                {
                    label: __("Favourite"),
                    icon: Star,
                    isEnabled: () => {
                        return true
                    },
                },
                {
                    label: __("Color"),
                    isEnabled: () => {
                        return true
                    },
                },
                {
                    label: __("Move to Trash"),
                    icon: Trash,
                    danger: true,
                    isEnabled: () => {
                        return true
                    },
                },
            ].filter((item) => item.isEnabled())
        },
        columnHeaders() {
            return [
                {
                    label: __("Name"),
                    field: "title",
                    sortable: true,
                },
                {
                    label: __("Owner"),
                    field: "owner",
                    sortable: true,
                },
                {
                    label: __("Modified"),
                    field: "modified",
                    sortable: true,
                },
                {
                    label: __("Size"),
                    field: "file_size",
                    sortable: true,
                },
                {
                    label: __("Type"),
                    field: "mime_type",
                    sortable: true,
                },
            ].filter((item) => item.sortable)
        }
    },
    mounted() {
        let me = this
        let introduction = introJs().setOptions({
            disableInteraction: true,
            showProgress: true,
            showBullets: false,
            nextLabel: __('NEXT'),
            prevLabel: __('BACK'),
            doneLabel: __('DONE'),
            steps: [
                {
                    title: "RoadAI",
                    intro: __("RoadAI is a video analysis application that detects road defects from uploaded videos. Designed to streamline road quality assessments, RoadAI operates seamlessly, much like your drive for office documents, enabling users to upload, process, and collaborate on road condition data effortlessly in the cloud.")
                },{
                    title: "Folders",
                    intro: "The Results Directory in RoadAI stores analysis outputs, including defect reports, visual overlays, and geospatial data. It’s organized for easy access, download, and sharing.",
                    element: document.getElementById("result-analysis")
                },{
                    title: "Input Data",
                    intro: "RoadAI accepts video files and GPX files as input. The video captures road conditions, while the GPX file provides geolocation data, enabling precise mapping of detected defects.",
                    element: document.getElementById("input-data")
                },{
                    title: "Your Data",
                    intro: "Now let’s upload some data ourselves!"
                },{
                    title: "Create Video Analysis Task",
                    intro: "Upload a video and GPX file to start detecting road defects with geolocation mapping. Track progress and view results easily.",
                    element: document.getElementById("btn-upload-video")
                },{
                    title: "Video Analysis Tasking",
                    intro: "A table showing the processing status of uploaded videos, including video names, file sizes, processing units, and real-time status updates.",
                    element: document.getElementById("btn-tasking")
                }
            ]
        })
        introduction.start()
        introduction.onexit(function(){
            me.$router.push({
                name: "Home",
            })
        })
        introduction.onbeforechange(function(targetElement){
            //console.log("Dòng 52 ", targetElement.id)
        })
    },
    methods: {
        localizeRelativeModified(modifiTime){
            if (typeof modifiTime === "string" && modifiTime.trim() !== "") {
                const arrMatch = modifiTime.trim().match(/^(\d+)\s*(.*)$/);
                if(arrMatch){
                    let number = parseInt(arrMatch[1], 10)
                    let text = arrMatch[2]
                    return __(`{0} ${text}`, [number])
                }
            } 
            return __(modifiTime)
        }
    }
}
</script>

<style scoped>
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(162px, 1fr));
  gap: 20px;
}
</style>