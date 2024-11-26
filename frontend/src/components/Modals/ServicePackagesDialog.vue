<template>
    <Dialog v-model="open" :options="{
        size: '4xl',
        title: 'Service Packages',
    }">
        <template #body-content>
            <div class="text-base">Set the service package you want to reserve</div>
            <div class="container">
                <div v-for="(item, index) in list_package" :key="index" class="package-card">
                    <div class="package-title">{{ item.title }}</div>
                </div>
            </div>
            
        </template>
        <template #actions>
            <div class="flex flex-row-reverse gap-2">
                <Button variant="solid" label="Change plan" @click="onChangePlan" />
            </div>
        </template>
    </Dialog>
</template>
<script>
import { Dialog, Button } from 'frappe-ui'

export default {
    name: "ServicePackagesDialog",
    components: {
        Dialog,
        Button
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
                auto: true,
                onSuccess(data){
                    console.log("Dòng 39 ", data)
                }
            }
        }
    },
    data(){
        return {
            packageSelect: null
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
        }
    },
    methods: {
        onChangePlan(){
            console.log("Dòng 48")
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
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

/* Title styling */
.package-title {
  font-size: 1.25rem;
  font-weight: bold;
  margin-bottom: 0.5rem;
  color: #333;
}

</style>