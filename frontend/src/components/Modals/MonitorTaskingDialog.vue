<template>
    <Dialog v-model="open" :options="{
        size: '4xl',
        title: __('Tasking'),
    }">
        <template #body-content>
            <ListView class="h-[350px] w-full" :columns="columnTask" :rows="arrTask" :options="{
                selectable: false,
                showTooltip: true,
                resizeColumn: true,
                emptyState: {
                    description: __('There are no records')
                }
            }" row-key="name">
                <template #cell="{ item, row, column }">
                    <template v-if="column.key == 'type_analysis'">
                        <span v-if="row['type_analysis'] == 'video_with_gps'" class="text-base">{{__('Video With GPS')}}</span>
                        <span v-else class="text-base">{{__('Video Without GPS')}}</span>
                    </template>
                    <template v-else-if="column.key == 'status'">
                        <Badge v-if="row['status'] == 'Success'" :variant="'subtle'" :ref_for="true" theme="green" size="sm">
                            {{__('Success')}}
                        </Badge>
                        <Tooltip v-else-if="row['status'] == 'Error'"
                            :placement="'top'"
                            :hoverDelay="0"
                        >
                        <template #body>
                            <div class="max-w-80 relative group">
                                <div
                                    class="w-full rounded px-2 py-1 text-xs text-ink-gray-9 shadow-xl overflow-y-auto text-white bg-gray-900"
                                >
                                    {{row['error_message']}}
                                </div>
                                <div class="absolute top-1 right-1 p-0 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <Button :variant="'outline'" theme="gray" size="sm" @click="() => onCopyError(row['error_message'])">
                                        <FeatherIcon name="copy" class="w-3" />
                                    </Button>
                                </div>
                            </div>
                            
                        </template>
                            <Badge  :variant="'subtle'" :ref_for="true" theme="red" size="sm" class="cursor-pointer">
                                {{__('Error')}}
                            </Badge>
                        </Tooltip>
                        <Badge v-else-if="row['status'] == 'Pending'" :variant="'subtle'" :ref_for="true" theme="gray" size="sm">
                            {{__('Pending')}}
                        </Badge>
                        <Badge v-else :variant="'subtle'" :ref_for="true" theme="blue" size="sm">
                            {{__('Processing')}}
                        </Badge>
                    </template>
                    <template v-else-if="column.key == 'file_size'">
                        <span class="text-sm">{{ formatSizeFile(row["file_size"]) }}</span>
                    </template>
                    <template v-else-if="['uploaded_time','start_processing_time','end_processing_time'].includes(column.key)">
                        <span class="text-sm">{{ formatDateFile(row[column.key]) }}</span>
                    </template>
                    <template v-else>
                        <span class="text-base">{{ row[column.key] }}</span>
                    </template>
                </template>
            </ListView>
        </template>
        <template #actions>
            <div class="flex flex-row-reverse gap-2">
                <Button variant="solid" label="Cancel" @click="onCloseDialog" />
            </div>
        </template>
    </Dialog>

</template>

<script>
import { Dialog, ListView, Badge, Button, Tooltip, FeatherIcon } from 'frappe-ui'
import { formatSize, formatDate } from "@/utils/format"
import { toast } from "@/utils/toasts.js"

export default{
    name: "MonitorTaskingDialog",
    components: {
        Dialog,
        ListView,
        Badge,
        Button,
        Tooltip,
        FeatherIcon
    },
    props: {
        modelValue: {
            type: Boolean,
            required: true,
        }
    },
    emits: ["update:modelValue"],
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
    resources:{
        tasks(){
            return {
                url: "drive.api.analysis_video.list_tasks",
                method: "GET",
                auto: true,
                onSuccess(data){
                    this.arrTask = data
                }
            }
        }
    },
    data(){
        return {
            arrTask: [],
            columnTask: [
                {
                    label: __('Title'),
                    key: 'title'
                },
                {
                    label: __('File Size'),
                    key: 'file_size',
                    width: '90px'
                },
                {
                    label: __('Type Analysis'),
                    key: 'type_analysis'
                },
                {
                    label: __("PUPV(Process Unit Per's Video)"),
                    key: 'pupv'
                },
                {
                    label: __('Uploaded Time'),
                    key: 'uploaded_time'
                },
                {
                    label: __('Status'),
                    key: 'status',
                    width: '150px'
                },
                {
                    label: __('Start Processing Time'),
                    key: 'start_processing_time'
                },
                {
                    label: __('End Processing Time'),
                    key: 'end_processing_time'
                }
            ],
            messageError: ""
        }
    },
    methods: {
        onCloseDialog(){
            this.open = false
        },
        formatSizeFile(size_file){
            if(size_file == null) return ""
            return formatSize(size_file)
        },
        formatDateFile(date){
            if(date == null) return ""
            return formatDate(date)
        },
        onCopyError(errorMessage){
            const textarea = document.createElement('textarea')
            textarea.value = errorMessage
            document.body.appendChild(textarea)

            // Chọn nội dung và sao chép
            textarea.select()
            textarea.setSelectionRange(0, errorMessage.length) // Đảm bảo chọn hết nội dung
            document.execCommand('copy')

            // Loại bỏ textarea khỏi DOM
            document.body.removeChild(textarea)
            toast({
                title: __("Copy successfully"),
                position: "bottom-right",
                timeout: 2,
            })
        }
    },
    mounted(){
        var me = this
        this.$realtime.on('event_analytic_video_job', (data) => {
            me.$resources.tasks.fetch()
        })
    },
    unmounted(){
        this.$realtime.off("event_analytic_video_job")
    }

}
</script>