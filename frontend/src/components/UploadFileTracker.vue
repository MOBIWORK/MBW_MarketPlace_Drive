<template>
    <div
        class="flex flex-col items-start fixed bottom-0 right-0 w-[300px] m-5  z-10 rounded-2xl overflow-hidden shadow-2xl 500 bg-white p-4">
        <div class="flex items-center justify-between w-full mb-4 pr-1.5" :class="[collapsed ? 'cursor-pointer' : '']"
            @click="collapsed = false">
            <div v-if="uploadFilesInProgress.length > 0" class="font-medium truncate text-lg">
                Uploading {{ uploadFilesInProgress.length }}
                {{ uploadFilesInProgress.length == 1 ? "file" : "files" }}
            </div>
            <div v-else-if="uploadFilesCompleted.length > 0" class="font-medium truncate text-lg">
                {{ uploadFilesCompleted.length }}
                {{ uploadFilesCompleted.length == 1 ? "file" : "files" }} complete
            </div>
            <div v-else-if="uploadFilesFailed.length > 0" class="font-medium truncate text-lg">
                {{ uploadFilesFailed.length }}
                {{ uploadFilesFailed.length == 1 ? "file" : "files" }} failed
            </div>
            <div class="ml-auto flex items-center gap-4">
                <button class="focus:outline-none" @click="close">
                    <FeatherIcon name="x" class="h-4 w-4 text-gray-800" />
                </button>
            </div>
        </div>
        <div class="bg-gray-100 rounded-[10px] space-x-0.5 h-7 flex items-center px-0.5 py-1 mb-2">
            <Button variant="ghost" class="max-h-6 leading-none transition-colors focus:outline-none" :class="[
                currentTab === 1
                    ? 'bg-white shadow-sm hover:bg-white active:bg-white'
                    : '',
            ]" @click="currentTab = 1">
                In Progress
            </Button>
            <Button variant="ghost" class="max-h-6 leading-none transition-colors focus:outline-none" :class="[
                currentTab === 2
                    ? 'bg-white shadow-sm hover:bg-white active:bg-white'
                    : '',
            ]" @click="currentTab = 2">
                Completed
            </Button>
            <Button v-show="uploadFilesFailed.length > 0" variant="ghost"
                class="max-h-6 leading-none transition-colors focus:outline-none" :class="[
                    currentTab === 3
                        ? 'bg-white shadow-sm hover:bg-white active:bg-white'
                        : '',
                ]" @click="currentTab = 3">
                Failed
            </Button>
        </div>
        <div v-if="!collapsed" class="max-h-64 overflow-y-auto bg-white w-full">
            <span v-if="!currentTabGetter().length" class="px-1.5 text-base font-medium text-gray-800">{{ emptyMessage
                }}</span>
            <div v-for="(uploadFile, index) in currentTabGetter()" :key="uploadFile.title"
                class="cursor-pointer truncate hover:bg-gray-50 rounded px-1 group" @mouseover="hoverIndex = index"
                @mouseout="hoverIndex = null">
                <div class="flex items-center gap-3 py-2 pr-[3px]" @click="openFile(uploadFile)">
                    <div class="flex items-center justify-between w-full">
                        <div class="flex justify-start items-center w-full max-w-[80%]">
                            <File class="w-5 mr-2" />
                            <p class="truncate text-sm leading-6 col-span-1 row-span-1">
                                {{ uploadFile.title_file }}
                            </p>
                        </div>
                        <div v-if="uploadFile.completed && hoverIndex !== index"
                            class="grid h-5 w-5 place-items-center rounded-full text-white bg-black"
                            :class="uploadFile.error ? 'bg-red-500' : 'bg-black'">
                            <FeatherIcon :name="uploadFile.error ? 'x' : 'check'" class="h-3 w-3" :stroke-width="3" />
                        </div>
                        <FeatherIcon v-if="uploadFile.completed && hoverIndex === index"
                            class="h-4.5 w-4.5 place-items-center" name="external-link" :stroke-width="1.5" />
                        <button v-if="hoverIndex === index" v-show="!uploadFile.completed && hoverIndex === index"
                            class="rounded-full hover:bg-red-300" variant="'ghost'">
                            <FeatherIcon name="x" class="h-6 w-6 p-1" />
                        </button>
                        <div v-if="hoverIndex !== index" v-show="!uploadFile.completed && !uploadFile.error"
                            class="h-6 w-6">
                            <Spinner class="w-6" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <Dialog v-if="showErrorDialog" v-model="showErrorDialog" :options="{
            title: 'Uploaded Failed',
            message: selectedFileUploaded.error,
            size: 'sm',
            actions: [
                {
                    label: 'Confirm',
                    onClick: () => {
                        showErrorDialog = false
                    },
                },
            ],
        }" />
        <Dialog v-if="showCancelDialog" v-model="showCancelDialog" :options="{
            title: 'Close tracking uploads',
            message: 'Are you sure you want to close tracking uploads?',
            size: 'sm',
            actions: [
                {
                    label: 'Confirm',
                    variant: 'subtle',
                    theme: 'red',
                    onClick: () => {
                        showCancelDialog = false
                        $store.dispatch('clearUploadFile')
                    },
                },
            ],
        }" />
    </div>
</template>

<script>
import { mapGetters } from "vuex"
import { FeatherIcon, Spinner } from "frappe-ui"
import Dialog from "frappe-ui/src/components/Dialog.vue"
import File from "./EspressoIcons/File.vue"

export default {
    name: "UploadFileTracker",
    components: {
        FeatherIcon,
        Spinner,
        Dialog,
        File,
    },
    data() {
        return {
            collapsed: false,
            hoverIndex: null,
            showCancelDialog: false,
            showErrorDialog: false,
            selectedFileUploaded: null,
            currentTab: 1,
            emptyMessage: "No upload in progress",
        }
    },
    computed: {
        uploadFiles() {
            return this.$store.state.uploadFiles
        },
        ...mapGetters(["uploadFilesInProgress", "uploadFilesCompleted", "uploadFilesFailed"]),
    },
    methods: {
        currentTabGetter() {
            switch (this.currentTab) {
                case 1:
                    this.emptyMessage = "No upload in progress"
                    return this.uploadFilesInProgress
                case 2:
                    this.emptyMessage = "No upload completed"
                    return this.uploadFilesCompleted
                case 3:
                    this.emptyMessage = "No upload analysis"
                    return this.uploadFilesFailed
                default:
                    this.emptyMessage = "No upload completed"
                    return this.uploadFilesCompleted
            }
        },
        toggleCollapsed() {
            this.collapsed = !this.collapsed
        },
        openFile(fileUploaded) {
            this.selectedFileUploaded = fileUploaded
            if (fileUploaded.error) {
                this.showErrorDialog = true
            }
            if (fileUploaded.completed && fileUploaded.folder_name) {
                this.$router.push({
                    name: "File",
                    params: { entityName: fileUploaded.folder_name },
                })
            }
        },
        close() {
            if (this.uploadFiles.length === this.uploadFilesCompleted.length) {
                this.$store.dispatch("clearUploadFile")
            } else {
                this.showCancelDialog = true
            }
        }
    }
}
</script>