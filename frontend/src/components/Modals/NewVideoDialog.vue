<template>
    <Dialog v-model="open" :options="{
        size: '3xl',
        title: 'New Video',
    }" @after-leave="onCleanData">
        <template #body-content>
            <div class="flex items-center mt-3">
                <input type="radio" value="Video_GPS" v-model="typeInput" id="Video_GPS" />
                <label for="Video_GPS" class="ml-2">Video + GPS</label>
                <input class="ml-10" type="radio" value="Video_Velocity" v-model="typeInput"
                    id="Video_Velocity" />
                <label for="Video_Velocity" class="ml-2">Video + Speed</label>
            </div>
            <div class="grid gap-5 mt-3" :class="typeInput == 'Video_GPS' ? 'grid-cols-2' : 'grid-cols-1'">
                <div>
                    <div class="text-sm mb-1 text-gray-600">Video 1</div>
                    <div class="h-28 border-2 border-dashed rounded-lg flex cursor-pointer items-center justify-center"
                        @click="onChooseVideoFirst">
                        <input class="hidden" type="file" id="video_1" @change="onChangeFirstVideo" />
                        <div class="flex flex-col items-center text-center">
                            <FeatherIcon name="plus" class="h-6" />
                            <div class="text-center" v-if="fFile != null">
                                <span class="text-sm font-medium">{{ renderFileName(fFile) }} -
                                    {{ renderFileSize(fFile) }} MB</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-if="typeInput == 'Video_GPS'">
                    <div class="text-sm mb-1 text-gray-600">Video 2</div>
                    <div class="h-28 border-2 border-dashed rounded-lg flex cursor-pointer items-center justify-center"
                        @click="onChooseVideoSecond">
                        <input class="hidden" type="file" id="video_2" @change="onChangeSecondVideo" />
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
                    <input class="hidden" type="file" id="f_gps" @change="onChangeFileGPS" />
                    <div class="flex flex-col items-center text-center">
                        <FeatherIcon name="plus" class="h-6" />
                        <div class="text-center" v-if="fGPS != null">
                            <span class="text-sm font-medium">{{ renderFileName(fGPS) }} -
                                {{ renderFileSize(fGPS) }} MB</span>
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
                <Button variant="solid" label="Tạo mới" :loading="isVideoCreating" @click="createNewVideo" />
            </div>
        </template>
    </Dialog>
</template>

<script>
import { Dialog, FeatherIcon, FormControl, ErrorMessage, Button, createResource } from 'frappe-ui'
import Uppy from '@uppy/core'
import Tus from '@uppy/tus'
import { v4 as uuidv4 } from "uuid"
import { toast } from "@/utils/toasts.js"

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
            uppy: null,
            completedUpload: false,
            completedCount: 0,
            errorMessage: "",
            nameFVideo: null,
            nameSVideo: null,
            nameGPS: null
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
        initUppy(){
            if(!this.uppy){
                this.uppy = new Uppy({
                    autoProceed: false,
                    showProgressDetails: false
                })
                this.uppy.use(Tus, {
                    endpoint: "/api/method/drive.api.upload.handle_tus_request",
                    chunkSize: 20 * 1024 * 1024,
                    headers: {
                        "X-Frappe-CSRF-Token": window.csrf_token,
                        "X-Request-ID": uuidv4(),
                        "Content-Type": "application/offset+octet-stream",
                    }
                })
                this.uppy.on("file-added", (file) => {
                    this.uppy.setFileMeta(file.id, {
                        fileId: file.id,
                        fileParent: this.$store.state.currentFolderID,
                        lastModified: file.data.lastModified,
                    })
                })
                this.uppy.on('upload-success', async (file, response) => {
                    let fileIDs = response.uploadURL.split("?")
                    let urlInfoFile = "/api/method/drive.api.upload.get_file_info?" + fileIDs[1]
                    let fetInfoFile = await fetch(urlInfoFile)
                    let objFile = await fetInfoFile.json()
                    if(this.typeInput == "Video_GPS"){
                        if(this.completedCount == 0) this.nameFVideo = objFile.message.name_entity
                        else if(this.completedCount == 1) this.nameSVideo = objFile.message.name_entity
                        else if(this.completedCount == 2) this.nameGPS = objFile.message.name_entity
                        this.completedCount += 1
                        if(this.completedCount == 3){
                            this.completedUpload = true
                            this.onAnalyticVideo()
                        }
                    }else{
                        this.nameFVideo = objFile.message.name_entity
                        this.onAnalyticVideo()
                    }
                })
                this.uppy.on('error', (error) => {
                    //Thông báo lỗi 
                    this.isVideoCreating = false 
                })
            }
        },
        onAddFileToUppy(file){
            this.uppy.addFile({
                name: file.name,
                type: file.type,
                data: file
            })
        },
        onChooseVideoFirst(){
            document.getElementById('video_1').click()
        },
        onChooseVideoSecond(){
            document.getElementById('video_2').click()
        },
        onChooseFileGPS(){
            document.getElementById('f_gps').click()
        },
        onChangeFirstVideo(evt){
            this.fFile = evt.target.files[0]
        },
        onChangeSecondVideo(evt){
            this.sFile = evt.target.files[0]
        },
        onChangeFileGPS(evt){
            this.fGPS = evt.target.files[0]
        },
        renderFileName(file){
            return file.name
        },
        renderFileSize(file){
            return (file.size / (1024 * 1024)).toFixed(2)
        },
        createNewVideo(){
            if(this.fFile == null && this.typeInput == "Video_GPS"){
                this.errorMessage = "First file video is not empty"
                return
            }
            if(this.sFile == null && this.typeInput == "Video_GPS"){
                this.errorMessage = "Second file video is not empty"
                return
            }
            if(this.fGPS == null && this.typeInput == "Video_GPS"){
                this.errorMessage = "File GPS is not empty"
                return
            }
            if(this.fFile == null && this.typeInput == "Video_Velocity"){
                this.errorMessage = "File video is not empty"
                return
            }
            if(this.velocity <= 0 && this.typeInput == "Video_Velocity"){
                this.errorMessage = "Field velocity is not empty"
                return
            }

            this.isVideoCreating = true
            this.completedUpload = false
            this.completedCount = 0
            this.initUppy()
            if(this.typeInput == "Video_Velocity"){
                this.onAddFileToUppy(this.fFile)
                this.uppy.upload()
            }else{
                this.onAddFileToUppy(this.fFile)
                this.onAddFileToUppy(this.sFile)
                this.onAddFileToUppy(this.fGPS)
                this.uppy.upload()
            }
        },
        onAnalyticVideo(){
            if(this.typeInput == "Video_GPS"){

            }else{
                var me = this
                createResource({
                    url: "drive.api.analysis_video.analytic_without_geometry",
                    method: "POST",
                    auto: true,
                    params: {
                        name_fvideo: this.nameFVideo,
                        velocity: this.velocity,
                        parent: this.$store.state.currentFolderID
                    },
                    onSuccess(data){
                        console.log("Dòng 252 ", data)
                        if(data.name != null){
                            me.open = false
                            toast({
                                title: "Tải video lên thành công. Quá trình phân tích mất khoảng thời gian, xin vui lòng đợi",
                                position: "bottom-right",
                                timeout: 2,
                            })
                            me.$emit("success")
                        }
                    }
                })
            }
        },
        onCleanData(){
            this.typeInput = "Video_Velocity"
            this.fFile = null
            this.sFile = null
            this.fGPS = null
            this.velocity = 7
            this.isVideoCreating = false
            this.uppy = null
            this.completedUpload = false
            this.completedCount = 0
            this.errorMessage = ""
            this.nameFVideo = null
            this.nameSVideo = null
            this.nameGPS = null
        }
    },
    beforeDestroy(){
        if(this.uppy){
            this.uppy.close()
        }
    }
}
</script>