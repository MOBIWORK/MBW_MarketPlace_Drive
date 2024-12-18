<template>
    <ListView class="h-full w-full" :columns="columnsPayment" :rows="arrHistorialPayment" :options="{
        selectable: false,
        showTooltip: true,
        resizeColumn: true,
        emptyState: {
            title: __('There are no records')
        }
    }" row-key="name">
        <template #cell="{ item, row, column }">
            <template v-if="column.key == 'price'">
                <span class="text-base">{{ renderPrice(item) }} đ</span>
            </template>
            <template v-else-if="column.key == 'status'">
                <Badge v-if="row['status'] == 'Paid'" :variant="'subtle'" :ref_for="true" theme="green" size="sm">
                    {{__('Paid')}}
                </Badge>
                <Badge v-else :variant="'subtle'" :ref_for="true" theme="red" size="sm">
                    {{__('Outstanding')}}
                </Badge>
            </template>
            <template v-else-if="column.key == 'payment_time'">
                <span v-if="item != null" class="text-base">{{ renderTime(item) }}</span>
            </template>
            <template v-else>
                <span class="text-base">{{ row[column.key] }}</span>
            </template>
        </template>
    </ListView>
</template>
<script>
import { ListView, Badge } from 'frappe-ui'

export default {
    name: "HistorialPayments",
    components: {
        ListView,
        Badge
    },
    data() {
        return {
            arrHistorialPayment: [],
            columnsPayment: [
                {
                    label: __('Title'),
                    key: 'title'
                },
                {
                    label: __('Price'),
                    key: 'price'
                },
                {
                    label: __('Status'),
                    key: 'status'
                },
                {
                    label: __('Payment Time'),
                    key: 'payment_time'
                }
            ]
        }
    },
    resources: {
        historialPayments() {
            return {
                url: "drive.api.payment.historial_payments",
                method: "GET",
                auto: true,
                onSuccess(data) {
                    this.arrHistorialPayment = data
                }
            }
        }
    },
    methods: {
        renderPrice(price) {
            return price.toLocaleString('vi-VN')
        },
        renderTime(inputDate) {
            // Chuyển chuỗi thành đối tượng Date
            const date = new Date(inputDate);

            // Định dạng các thành phần ngày, tháng, năm, giờ, phút, giây
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0'); // Tháng bắt đầu từ 0
            const year = date.getFullYear();

            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            const seconds = String(date.getSeconds()).padStart(2, '0');

            // Trả về chuỗi theo định dạng dd/MM/yyyy hh-mm-ss
            return `${day}/${month}/${year} ${hours}-${minutes}-${seconds}`;
        }
    }
}
</script>