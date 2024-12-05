<template>
    <Dialog v-model="open" :options="{
        size: '3xl',
        title: 'New Video',
    }" @after-leave="onCleanData">
        <template #body-content>
            <div class="flex items-center mt-3">
                <input type="radio" value="Video_GPS" v-model="typeInput" id="Video_GPS" />
                <label for="Video_GPS" class="ml-2 text-sm">Video + GPS</label>
                <input class="ml-10" type="radio" value="Video_Velocity" v-model="typeInput" id="Video_Velocity" />
                <label for="Video_Velocity" class="ml-2 text-base">Video + Speed</label>
            </div>
            <div class="grid gap-5 mt-3" :class="typeInput == 'Video_GPS' && processVideo==2 ? 'grid-cols-2' : 'grid-cols-1'">
                <div>
                    <div class="text-sm mb-1 text-gray-600">Video 1</div>
                    <div class="h-28 border-2 border-dashed rounded-lg flex cursor-pointer items-center justify-center"
                        @click="onChooseVideoFirst">
                        <input class="hidden" type="file" accept="video/mp4" id="video_1"
                            @change="onChangeFirstVideo" />
                        <div id="dropzone-area" class="hidden"></div>
                        <div class="flex flex-col items-center text-center">
                            <FeatherIcon name="plus" class="h-6" />
                            <div class="text-center" v-if="fFile != null">
                                <span class="text-sm font-medium">{{ renderFileName(fFile) }} -
                                    {{ renderFileSize(fFile) }} MB</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-if="typeInput == 'Video_GPS' && processVideo == 2">
                    <div class="text-sm mb-1 text-gray-600">Video 2</div>
                    <div class="h-28 border-2 border-dashed rounded-lg flex cursor-pointer items-center justify-center"
                        @click="onChooseVideoSecond">
                        <input class="hidden" type="file" accept="video/mp4" id="video_2"
                            @change="onChangeSecondVideo" />
                        <div class="flex flex-col items-center text-center">
                            <FeatherIcon name="plus" class="h-6" />
                            <div class="text-center" v-if="sFile != null">
                                <span class="text-sm font-medium">{{ renderFileName(sFile) }} -
                                    {{ renderFileSize(sFile) }} MB</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="grid grid-cols-1 mt-3" v-if="typeInput == 'Video_GPS'">
                <div class="text-sm mb-1 text-gray-600">File GPS</div>
                <div class="h-28 border-2 border-dashed rounded-lg flex cursor-pointer items-center justify-center"
                    @click="onChooseFileGPS">
                    <input class="hidden" type="file" id="f_gps" accept="gpx" @change="onChangeFileGPS" />
                    <div class="flex flex-col items-center text-center">
                        <FeatherIcon name="plus" class="h-6" />
                        <div class="text-center" v-if="fGPS != null">
                            <span class="text-sm font-medium">{{ renderFileName(fGPS) }} -
                                {{ renderFileSizeKB(fGPS) }} Kb</span>
                        </div>
                    </div>
                </div>
            </div>
            <FormControl class="mt-3" :type="'text'" :ref_for="true" size="sm" variant="subtle"
                placeholder="Nhập tốc độ" :disabled="false" label="Tốc độ(km/h)" v-model="velocity"
                v-if="typeInput == 'Video_Velocity'" />
            <ErrorMessage class="my-1" :message="errorMessage" />
        </template>
        <template #actions>
            <div class="flex flex-row-reverse gap-2">
                <Button variant="solid" :label="label" :loading="isVideoCreating" @click="createNewVideo" />
            </div>
        </template>
    </Dialog>
</template>

<script>
import { Dialog, FeatherIcon, FormControl, ErrorMessage, Button, createResource } from 'frappe-ui'
import { toast } from "@/utils/toasts.js"
import Dropzone from "dropzone";

export default {
    name: 'NewVideoDialog',
    components: {
        Dialog,
        FeatherIcon,
        FormControl,
        ErrorMessage,
        Button
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
    emits: ["update:modelValue", "success"],
    data() {
        return {
            typeInput: "Video_Velocity",
            fFile: null,
            sFile: null,
            fGPS: null,
            velocity: 7,
            isVideoCreating: false,
            completedUpload: false,
            completedCount: 0,
            errorMessage: "",
            nameFVideo: null,
            nameSVideo: null,
            nameGPS: null,
            label: "Create new",
            dropzone: null,
            processVideo: 1
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
        initDropzone() {
            var me = this
            if (!this.dropzone) {
                this.dropzone = new Dropzone("#dropzone-area", {
                    url: "/api/method/drive.api.files.upload_file",
                    autoProcessQueue: true,
                    addRemoveLinks: false,
                    chunking: true,
                    maxFilesize: 10 * 1024, // 10GB
                    timeout: 240000, // 4 minutes
                    chunkSize: 20 * 1024 * 1024, // 20MB
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
                        console.log("Form Data:", formData);
                    },
                    params: function (files, xhr, chunk) {
                        if (chunk) {
                            return {
                                uuid: chunk.file.upload.uuid,
                                chunk_index: chunk.index,
                                total_file_size: chunk.file.size,
                                chunk_size: me.dropzone.options.chunkSize,
                                total_chunk_count: chunk.file.upload.totalChunkCount,
                                chunk_byte_offset: chunk.index * me.dropzone.options.chunkSize,
                            }
                        }
                    }
                })
                this.dropzone.on('success', function (file, response) {
                    if (me.typeInput == "Video_GPS") {
                        let name_entity = response["message"]["name"]
                        if (file.name == me.fFile.name) me.nameFVideo = name_entity
                        else if (me.processVideo == 2 && file.name == me.sFile.name) me.nameSVideo = name_entity
                        else if (file.name == me.fGPS.name) me.nameGPS = name_entity
                        me.completedCount += 1
                        if (me.processVideo == 2 && me.completedCount == 3) {
                            me.completedUpload = true
                            me.onAnalyticVideo()
                        }else if(me.completedCount == 2 && me.processVideo == 1){
                            me.completedUpload = true
                            me.onAnalyticVideo()
                        }
                    } else {
                        me.nameFVideo = response["message"]["name"]
                        me.onAnalyticVideo()
                    }
                })
                this.dropzone.on('error', function (file, errorMessage) {
                    let server_message = JSON.parse(errorMessage["_server_messages"])
                    if(server_message.length > 0){
                        let item_server_message = server_message[0]
                        let objServerMessage = JSON.parse(item_server_message)
                        me.errorMessage = objServerMessage["message"]
                    }
                    me.isVideoCreating = false
                })
            }
        },
        onAddFileToDropZone(file) {
            this.dropzone.addFile(file)
            console.log(this.dropzone)
        },
        onChooseVideoFirst() {
            document.getElementById('video_1').click()
        },
        onChooseVideoSecond() {
            document.getElementById('video_2').click()
        },
        onChooseFileGPS() {
            document.getElementById('f_gps').click()
        },
        onChangeFirstVideo(evt) {
            this.fFile = evt.target.files[0]
        },
        onChangeSecondVideo(evt) {
            this.sFile = evt.target.files[0]
        },
        onChangeFileGPS(evt) {
            this.fGPS = evt.target.files[0]
        },
        renderFileName(file) {
            return file.name
        },
        renderFileSize(file) {
            return (file.size / (1024 * 1024)).toFixed(2)
        },
        renderFileSizeKB(file){
            return (file.size / 1024).toFixed(2)
        },
        createNewVideo() {
            if (this.fFile == null && this.typeInput == "Video_GPS") {
                this.errorMessage = "First file video is not empty"
                return
            }
            if (this.processVideo == 2 && this.sFile == null && this.typeInput == "Video_GPS") {
                this.errorMessage = "Second file video is not empty"
                return
            }
            if (this.fGPS == null && this.typeInput == "Video_GPS") {
                this.errorMessage = "File GPS is not empty"
                return
            }
            if (this.fFile == null && this.typeInput == "Video_Velocity") {
                this.errorMessage = "File video is not empty"
                return
            }
            if (this.velocity <= 0 && this.typeInput == "Video_Velocity") {
                this.errorMessage = "Field velocity is not empty"
                return
            }
            this.label = "Upload"
            this.isVideoCreating = true
            this.completedUpload = false
            this.completedCount = 0
            this.initDropzone()
            if (this.typeInput == "Video_Velocity") {
                this.onAddFileToDropZone(this.fFile)
            } else {
                this.onAddFileToDropZone(this.fFile)
                if(this.processVideo == 2) this.onAddFileToDropZone(this.sFile)
                this.onAddFileToDropZone(this.fGPS)
            }
        },
        onAnalyticVideo() {
            var me = this
            if (this.typeInput == "Video_GPS") {
                this.$store.commit("pushToAnalysis", {
                    uuid: this.nameFVideo,
                    name: this.processVideo == 2? `${this.fFile.name}_${this.sFile.name}` : `${this.fFile.name}`,
                    completed: false,
                    progress: 0
                })
                let urlAnalysisVideo = "drive.api.analysis_video.analytic_video_with_geometry"
                let paramsAnalysisVideo = {
                    name_fvideo: this.nameFVideo,
                    name_gps: this.nameGPS,
                    parent: this.$store.state.currentFolderID
                }
                if(this.processVideo == 2){
                    urlAnalysisVideo = "drive.api.analysis_video.analytic_videos_with_geometry"
                    paramsAnalysisVideo = {
                        name_fvideo: this.nameFVideo,
                        name_svideo: this.nameSVideo,
                        name_gps: this.nameGPS,
                        parent: this.$store.state.currentFolderID
                    }
                }
                createResource({
                    url: urlAnalysisVideo,
                    method: "POST",
                    auto: true,
                    params: paramsAnalysisVideo,
                    onSuccess(data) {
                        if (data.name != null) {
                            me.open = false
                            toast({
                                title: "Video uploaded successfully. The analysis process takes some time, please wait",
                                position: "bottom-right",
                                timeout: 2,
                            })
                            me.$emit("success")
                        }
                    }
                })
            } else {
                this.$store.commit("pushToAnalysis", {
                    uuid: this.nameFVideo,
                    name: this.fFile.name,
                    completed: false,
                    progress: 0
                })
                createResource({
                    url: "drive.api.analysis_video.analytic_without_geometry",
                    method: "POST",
                    auto: true,
                    params: {
                        name_fvideo: this.nameFVideo,
                        velocity: this.velocity,
                        parent: this.$store.state.currentFolderID
                    },
                    onSuccess(data) {
                        if (data.name != null) {
                            me.open = false
                            toast({
                                title: "Video uploaded successfully. The analysis process takes some time, please wait",
                                position: "bottom-right",
                                timeout: 2,
                            })
                            me.$emit("success")
                        }
                    }
                })
            }
        },
        onCleanData() {
            this.typeInput = "Video_Velocity"
            this.fFile = null
            this.sFile = null
            this.fGPS = null
            this.velocity = 7
            this.isVideoCreating = false
            this.dropzone = null
            this.completedUpload = false
            this.completedCount = 0
            this.errorMessage = ""
            this.nameFVideo = null
            this.nameSVideo = null
            this.nameGPS = null
            this.label = "Create new"
        }
    }
}
</script>