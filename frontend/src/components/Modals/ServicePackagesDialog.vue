<template>
    <Dialog v-model="open" :options="{
        size: '4xl',
        title: 'Service Packages',
    }" @after-leave="onCleanData">
        <template #body-content>
            <div class="text-base">Set the service package you want to reserve</div>
            <div class="container">
                <div v-for="(item, index) in list_package" :key="index" class="package-card">
                    <div class="package-content">
                        <div class="package-title">{{ item.title }} ({{renderStorageVolume(item.storage_volume)}} {{renderUnitStorageVolume(item.storage_volume)}})</div>
                        <div class="package-price">{{renderPrice(item.unit_price)}} đ</div>
                        <div class="flex justify-center">
                            <Button
                                :variant="'outline'"
                                :ref_for="true"
                                theme="gray"
                                size="md"
                                :disabled="package_used == item.code"
                                class="w-[150px] mb-4"
                                @click="() => onRegisterPackage(item)"
                            >
                                Register package
                            </Button>
                        </div>
                        <div class="w-full border-t border-gray-500"></div>
                        <div class="ml-1 mt-4">
                            <div class="flex items-start mb-1">
                                <FeatherIcon name="check" class="h-5 w-5 mr-2" />
                                <div class="text-base">
                                    {{renderStorageVolume(item.storage_volume)}} {{renderUnitStorageVolume(item.storage_volume)}} storage capacity
                                </div>
                            </div>
                            <div class="flex items-start mb-1">
                                <FeatherIcon name="check" class="h-5 w-5 mr-2" />
                                <div class="text-base">
                                    {{item.pupv}} PUPV(Process Unit Per's Videos)
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <ErrorMessage class="mt-2" :message="errorMessage" />
        </template>
    </Dialog>
    <CheckOutDialog v-model="showCheckOutDialog" :package="packageSelect" :qrCodeDataUrl="qrDataURL" :contentTransaction="contentTransaction"></CheckOutDialog>
</template>
<script>
import { Dialog, Button, FeatherIcon, ErrorMessage } from 'frappe-ui'
import { toast } from "@/utils/toasts.js"
import { VietQR } from 'vietqr'
import CheckOutDialog from '@/components/Modals/CheckOutDialog.vue';

export default {
    name: "ServicePackagesDialog",
    components: {
        Dialog,
        Button,
        FeatherIcon,
        ErrorMessage,
        CheckOutDialog
    },
    props: {
        modelValue: {
            type: Boolean,
            required: true,
        }
    },
    emits: ["update:modelValue"],
    resources: {
        servicePackages(){
            return {
                url: "drive.api.service_package.list_package",
                method: "GET",
                auto: true
            }
        },
        payments(){
            return {
                type: 'list',
                doctype: "Drive Payment",
                insert: {
                    onSuccess(data){
                        if(data.price == 0){
                            toast({
                                title: "Bạn đã thay đổi gói thành công",
                                position: "bottom-right",
                                timeout: 2,
                            })
                            this.open = false
                        }else{
                            toast({
                                title: "Hóa đơn tạo thành công. Vui lòng thanh toán để trải nghiệm dịch vụ",
                                position: "bottom-right",
                                timeout: 2,
                            })
                            let vietQR = new VietQR({
                                clientID: this.$store.state.clientIDQRCode,
                                apiKey: this.$store.state.apiKeyQRCode
                            })
                            vietQR.genQRCodeBase64({
                                bank: this.$store.state.codeBank,
                                accountName: this.$store.state.accountNameBanking,
                                accountNumber: this.$store.state.accountNumberBanking,
                                amount: this.packageSelect.unit_price.toString(),
                                memo: data.name,
                                template: "compact"
                            }).then((res) => {
                                if (res.status == 200) {
                                    this.qrDataURL = res.data.data.qrDataURL
                                }
                            })
                            this.contentTransaction = data.name
                            this.showCheckOutDialog = true
                        }
                        
                    },
                    onError(error){
                        if (error.messages) {
                            this.errorMessage = error.messages.join("\n")
                        } else {
                            this.errorMessage = error.message
                        }
                    }
                }
            }
        }
    },
    data(){
        return {
            packageSelect: null,
            errorMessage: "",
            qrDataURL: "",
            showCheckOutDialog: false,
            contentTransaction: ""
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
        list_package() {
            return this.$resources.servicePackages.data || []
        },
        package_used(){
            return this.$store.state.packageUsed
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
        },
        onRegisterPackage(item){
            this.packageSelect = item
            this.$resources.payments.insert.submit({
                'form_of_payment': "QRCode",
                'code_package': item.code,
                'price': item.unit_price,
                'status': "Outstanding"
            })
        },
        onCleanData(){
            this.packageSelect = null
            this.errorMessage =""
            this.qrDataURL = ""
            this.showCheckOutDialog = false
            this.contentTransaction = ""
        }
    }
}
</script>

<style scoped>
/* Container layout */
.container {
  display: grid;
  grid-template-columns: repeat(1, 1fr); /* Mobile: mỗi dòng 1 gói */
  gap: 1rem; /* Khoảng cách giữa các gói */
  padding: 1rem;
}

/* Responsive layout for desktop */
@media (min-width: 768px) {
  .container {
    grid-template-columns: repeat(3, 1fr); /* Desktop: 3 gói trên 1 dòng */
    grid-auto-rows: minmax(150px, auto); /* Tự động giãn chiều cao */
  }
}

/* Card styling */
.package-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 1rem;
  background-color: #f9f9f9;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.package-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.2);
}

.package-content{
    display: flex;
    flex-direction: column;
}

/* Title styling */
.package-title {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #333;
  justify-content: center;
  display: flex;
}
.package-price{
    font-size: 1.5rem;
    font-weight: 400;
    letter-spacing: 0;
    line-height: 2rem;
    color: #1f1f1f;
    margin-top: 8px;
    margin-bottom: 10px;
    justify-content: center;
    display: flex;
}

</style>