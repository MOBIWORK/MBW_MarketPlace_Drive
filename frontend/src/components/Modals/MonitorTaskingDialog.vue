<template>
    <Dialog v-model="open" :options="{
        size: '4xl',
        title: 'Tasking',
    }">
        <template #body-content>
            <ListView class="h-[350px] w-full" :columns="columnTask" :rows="arrTask" :options="{
                selectable: false,
                showTooltip: true,
                resizeColumn: true,
                emptyState: {
                    description: 'There are no records'
                }
            }" row-key="name">
                <template #cell="{ item, row, column }">
                    <template v-if="column.key == 'type_analysis'">
                        <span v-if="row['type_analysis'] == 'video_with_gps'" class="text-base">Video With GPS</span>
                        <span v-else class="text-base">Video Without GPS</span>
                    </template>
                    <template v-else-if="column.key == 'status'">
                        <Badge v-if="row['status'] == 'Success'" :variant="'subtle'" :ref_for="true" theme="green" size="sm">
                            Success
                        </Badge>
                        <Tooltip v-else-if="row['status'] == 'Error'"
                            :text="row['error_message']"
                            :placement="'top'"
                            :hoverDelay="0"
                        >
                            <Badge  :variant="'subtle'" :ref_for="true" theme="red" size="sm" class="cursor-pointer">
                                Error
                            </Badge>
                        </Tooltip>
                        <Badge v-else-if="row['status'] == 'Pending'" :variant="'subtle'" :ref_for="true" theme="gray" size="sm">
                            Pending
                        </Badge>
                        <Badge v-else :variant="'subtle'" :ref_for="true" theme="blue" size="sm">
                            Processing
                        </Badge>
                    </template>
                    <template v-else-if="column.key == 'file_size'">
                        {{ formatSizeFile(row["file_size"]) }}
                    </template>
                    <template v-else-if="['uploaded_time','start_processing_time','end_processing_time'].includes(column.key)">
                        {{ formatDateFile(row[column.key]) }}
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
import { Dialog, ListView, Badge, Button, Tooltip } from 'frappe-ui'
import { formatSize, formatDate } from "@/utils/format"

export default{
    name: "MonitorTaskingDialog",
    components: {
        Dialog,
        ListView,
        Badge,
        Button,
        Tooltip
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
                    label: 'Title',
                    key: 'title'
                },
                {
                    label: 'File Size',
                    key: 'file_size',
                    width: '90px'
                },
                {
                    label: 'Type Analysis',
                    key: 'type_analysis'
                },
                {
                    label: 'PUPV',
                    key: 'pupv'
                },
                {
                    label: 'Uploaded Time',
                    key: 'uploaded_time'
                },
                {
                    label: 'Status',
                    key: 'status',
                    width: '90px'
                },
                {
                    label: 'Start Processing Time',
                    key: 'start_processing_time'
                },
                {
                    label: 'End Processing Time',
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