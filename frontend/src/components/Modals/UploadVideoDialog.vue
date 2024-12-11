<template>
    <Dialog v-model="open" :options="{
        size: '3xl',
        title: 'Upload Videos',
    }" @after-leave="onCleanData">
        <template #body-content>
            <div class="flex items-center mt-3">
                <input type="radio" value="video_gps" v-model="typeInput" id="video_gps" />
                <label for="video_gps" class="ml-2 text-sm">Video With GPS</label>
                <input class="ml-10" type="radio" value="video_without_gps" v-model="typeInput"
                    id="video_without_gps" />
                <label for="video_without_gps" class="ml-2 text-base">Video Without GPS</label>
            </div>
            <div v-if="typeInput == 'video_gps'" class="grid mt-3 grid-cols-1">
                <div class="text-sm text-gray-600 mb-1">Files</div>
                <div class="h-28 border-2 border-dashed rounded-lg flex cursor-pointer items-center justify-center"
                    @click="onChooseFileWithGPS">
                    <input class="hidden" type="file" accept="video/mp4,.gpx" id="file_with_gps" multiple
                        @change="onChangeFileWithGPS" />
                    <div id="dropzone-area" class="hidden"></div>
                    <div class="flex flex-col items-center text-center">
                        <FeatherIcon name="plus" class="h-6" />
                        <div class="text-center">
                            <span class="text-sm font-medium">The video and gps file names must be the same to be able
                                to extract information</span>
                        </div>
                    </div>
                </div>
            </div>
            <div v-if="typeInput == 'video_without_gps'" class="grid mt-3 grid-cols-1">
                <div class="text-sm text-gray-600 mb-1">Files</div>
                <div class="h-28 border-2 border-dashed rounded-lg flex cursor-pointer items-center justify-center"
                    @click="onChooseFileWithOutGPS">
                    <input class="hidden" type="file" accept="video/mp4" id="file_without_gps" multiple
                        @change="onChangeFileWithoutGPS" />
                    <div id="dropzone-area" class="hidden"></div>
                    <div class="flex flex-col items-center text-center">
                        <FeatherIcon name="plus" class="h-6" />
                        <div class="text-center">
                            <span class="text-sm font-medium">Select video files to extract information</span>
                        </div>
                    </div>
                </div>
            </div>
        </template>
        <template #actions>
            <div class="flex flex-row-reverse gap-2">
                <Button variant="solid" label="Cancel" @click="onCloseDialog" />
            </div>
        </template>
    </Dialog>
</template>

<script>
import { Dialog, Button, FeatherIcon, createResource } from 'frappe-ui'
import Dropzone from "dropzone";

export default {
    name: "UploadVideoDialog",
    components: {
        Dialog,
        Button,
        FeatherIcon
    },
    props: {
        modelValue: {
            type: Boolean,
            required: true,
        },
        parent: {
            type: String,
            default: "",
        },
    },
    emits: ["update:modelValue"],
    data() {
        return {
            typeInput: "video_gps",
            dropzone: null,
            arrFile: []
        }
    },
    computed: {
        open: {
            get() {
                return this.modelValue
            },
            set(value) {
                this.$emit("update:modelValue", value)
            },
        },
    },
    methods: {
        onCleanData() {
            this.dropzone = null
        },
        onCloseDialog() {
            this.open = false
        },
        onChooseFileWithGPS() {
            document.getElementById('file_with_gps').click()
        },
        onChangeFileWithGPS(evt) {
            this.initDropzone()
            this.arrFile = []
            for(let i = 0; i < evt.target.files.length; i++){
                let file = evt.target.files[i]
                this.arrFile.push(file)
                if(file.type != null && file.type != ""){
                    this.addFileToTracking(file, i)
                    this.dropzone.addFile(file)
                }
            }
            this.onCloseDialog()
        },
        onChooseFileWithOutGPS() {
            document.getElementById('file_without_gps').click()
        },
        onChangeFileWithoutGPS(evt) {
            this.initDropzone()
            this.arrFile = []
            for(let i = 0; i < evt.target.files.length; i++){
                let file = evt.target.files[i]
                this.arrFile.push(file)
                if(file.type != null && file.type != ""){
                    this.addFileToTracking(file, i)
                    this.dropzone.addFile(file)
                }
            }
            this.onCloseDialog()
        },
        initDropzone(){
            var me = this
            if (!this.dropzone){
                let chunkSize = 1024*1024 // 1MB
                this.dropzone = new Dropzone("#dropzone-area", {
                    url: "/api/method/drive.api.files.upload_file",
                    autoProcessQueue: true,
                    addRemoveLinks: false,
                    chunking: true,
                    maxFilesize: 10 * 1024, // 10GB
                    timeout: 240000, // 4 minutes
                    chunkSize: chunkSize, // 1MB
                    headers: {
                        "X-Frappe-Csrf-Token": window.csrf_token
                    },
                    accept: function (file, done) {
                        if (file.size == 0) {
                            done("Empty files will not be uploaded.")
                        } else {
                            done()
                        }
                    },
                    sending: function (file, xhr, formData) {
                        if (file.lastModified) {
                            formData.append("last_modified", file.lastModified)
                        }
                        if (me.parent) {
                            formData.append("parent", me.parent)
                        }
                        if (file.newFullPath) {
                            formData.append("fullpath", file.newFullPath)
                        } else if (file.webkitRelativePath) {
                            formData.append("fullpath", file.webkitRelativePath)
                        } else if (file.fullPath) {
                            formData.append("fullpath", file.fullPath)
                        }
                    },
                    params: function (files, xhr, chunk) {
                        if (chunk) {
                            return {
                                uuid: chunk.file.upload.uuid,
                                chunk_index: chunk.index,
                                total_file_size: chunk.file.size,
                                chunk_size: chunkSize,
                                total_chunk_count: chunk.file.upload.totalChunkCount,
                                chunk_byte_offset: chunk.index * chunkSize,
                            }
                        }
                    }
                })
                this.dropzone.on('success', function (file, response) {
                    let indexFile = me.arrFile.findIndex(x => x.name == file.name)
                    me.$store.commit("updateFileUploaded", {
                        title: `${response["message"]["title"]}_${indexFile}`,
                        title_file: response["message"]["title"],
                        completed: true,
                        progress: 100,
                        folder_name: response["message"]["name"]
                    })
                    me.$store.commit("updateIdFolderUpload", {
                        id: response["message"]["name"]
                    })
                    me.onAnalysisFile(response["message"]["name"])
                })
                this.dropzone.on('error', function (file, errorMessage) {
                    let indexFile = me.arrFile.findIndex(x => x.name == file.name)
                    let server_message = JSON.parse(errorMessage["_server_messages"])
                    if(server_message.length > 0){
                        let item_server_message = server_message[0]
                        let objServerMessage = JSON.parse(item_server_message)
                        me.$store.commit("updateFileUploaded", {
                            title: `${file.name}_${indexFile}`,
                            title_file: file.name,
                            completed: true,
                            progress: 100,
                            error: objServerMessage["message"]
                        })
                    }
                    
                })
            }
        },
        addFileToTracking(file, index){
            this.$store.commit("pushToFileUploaded", {
                title: `${file.name}_${index}`,
                title_file: file.name,
                completed: false,
                progress: 0
            })
        },
        onAnalysisFile(idFile){
            if(this.typeInput == "video_gps"){
                createResource({
                    url: "drive.api.analysis_video.analytic_with_geometry",
                    method: "POST",
                    auto: true,
                    params: {
                        name_file: idFile,
                        parent: this.$store.state.currentFolderID
                    }
                })
            } else if(this.typeInput == "video_without_gps"){
                createResource({
                    url: "drive.api.analysis_video.analytic_without_geometry",
                    method: "POST",
                    auto: true,
                    params: {
                        name_file: idFile,
                        parent: this.$store.state.currentFolderID
                    }
                })
            }
        }
    }
}
</script>