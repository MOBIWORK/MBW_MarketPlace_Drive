<template>
    <Dialog v-model="open" :options="{
        size: '3xl',
        title: 'Tasking',
    }">
        <template #body-content>
            <ListView class="h-[350px] w-full" :columns="columnTask" :rows="arrTask" :options="{
                selectable: false,
                showTooltip: true,
                resizeColumn: true,
                onRowClick:(row) => clickRow(row),
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
                        <Badge v-else-if="row['status'] == 'Error'" :variant="'subtle'" :ref_for="true" theme="red" size="sm">
                            Error
                        </Badge>
                        <Badge v-else :variant="'subtle'" :ref_for="true" theme="blue" size="sm">
                            Processing
                        </Badge>
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

    <Dialog v-if="showErrorDialog" v-model="showErrorDialog" :options="{
            title: 'Analysis Failed',
            message: messageError,
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
</template>

<script>
import { Dialog, ListView, Badge, Button } from 'frappe-ui'

export default{
    name: "MonitorTaskingDialog",
    components: {
        Dialog,
        ListView,
        Badge,
        Button
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
                    label: 'Type Analysis',
                    key: 'type_analysis'
                },
                {
                    label: 'PUPV',
                    key: 'pupv'
                },
                {
                    label: 'Status',
                    key: 'status'
                }
            ],
            showErrorDialog: false,
            messageError: ""
        }
    },
    methods: {
        onCloseDialog(){
            this.open = false
        },
        clickRow(row){
            console.log("Dòng 114 ", row)
            if(row.status == "Error"){
                this.messageError = row.error_message
                this.showErrorDialog = true
            }
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