<template>
    <Dialog v-model="open" :options="{
        size: '3xl',
        title: 'Check Out',
    }">
        <template #body-content>
            <div class="flex">
                <div class="w-2/3">
                    <div class="mb-3 text-base font-bold">Thông tin đơn hàng</div>
                    <div class="flex justify-between items-center mb-2 text-base">
                        <div>Dung lượng lưu trữ:</div>
                        <div class="font-bold">{{renderStorageVolume(package.storage_volume)}} {{renderUnitStorageVolume(package.storage_volume)}}</div>
                    </div>
                    <div class="flex justify-between items-center mb-2 text-base">
                        <div>Đơn vị xử lý video(PUPV):</div>
                        <div class="font-bold">{{package.pupv}}</div>
                    </div>
                    <div class="flex justify-between items-center mb-3 text-base">
                        <div>Tổng tiền thanh toán:</div>
                        <div class="font-bold">{{renderPrice(package.unit_price)}} đ</div>
                    </div>
                    <div class="text-base mb-3">
                        <div class="font-bold mb-1">Cách thanh toán</div>
                        <div class="mb-1">Phương thức thanh toán bắng Chuyển khoản qua Ngân hàng</div>
                        <div>
                            <span>Bạn vui lòng chuyển khoản đúng số tiền</span><span>&nbsp;</span>
                            <span class="font-bold">{{renderPrice(package.unit_price)}} đ</span><span>&nbsp;</span>
                            <span>để vào tài khoản bên dưới và</span><span>&nbsp;</span>
                            <span class="font-bold">Phải nhập {{contentTransaction}}</span><span>&nbsp;</span>
                            <span>vào nội dung chuyển khoản. Chúng tôi sẽ chuyển đổi gói sử dụng của bạn trong 3-5 phút ngay khi nhận được thông tin chuyển khoản.</span><span>&nbsp;</span>
                        </div>
                    </div>
                    <div>******************************************</div>
                    <div class="flex justify-between items-center text-base mt-3 mb-2">
                        <div>Chủ tài khoản:</div>
                        <div class="font-bold">{{accountNameBanking}}</div>
                    </div>
                    <div class="flex justify-between items-center text-base mb-2">
                        <div>Số tài khoản:</div>
                        <div class="font-bold">{{accountNumberBanking}}</div>
                    </div>
                    <div class="flex justify-between items-center text-base mb-2">
                        <div>Tên ngân hàng:</div>
                        <div class="font-bold">{{nameBank}}</div>
                    </div>
                    <div class="flex justify-between items-center text-base mb-2">
                        <div>Nội dung chuyển khoản:</div>
                        <div class="font-bold">{{contentTransaction}}</div>
                    </div>
                </div>
                <div class="w-1/3">
                    <div class="text-base font-bold pl-4 ml-3">QR Code</div>
                    <div class="ml-3">
                        <img :src="qrCodeDataUrl" class="w-full h-[250px]"/>
                    </div>
                </div>
            </div>
        </template>
    </Dialog>
</template>

<script>
import { Dialog } from 'frappe-ui'

export default{
    name: "CheckOutDialog",
    components: {
        Dialog
    },
    props: {
        modelValue: {
            type: Boolean,
            required: true,
        },
        package: {
            type: Object,
            required: true,
        },
        qrCodeDataUrl: {
            type: String,
            required: false
        },
        contentTransaction: {
            type: String,
            required: true
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
        nameBank(){
            return this.$store.state.nameBank
        },
        accountNameBanking(){
            return this.$store.state.accountNameBanking
        },
        accountNumberBanking(){
            return this.$store.state.accountNumberBanking
        }
    },
    methods: {
        renderStorageVolume(storage){
            if(storage >= 1024) return storage/1024
            return storage
        },
        renderUnitStorageVolume(storage){
            if(storage >= 1024) return "TB"
            return "GB"
        },
        renderPrice(price){
            return price.toLocaleString('vi-VN')
        }
    }   
}
</script>