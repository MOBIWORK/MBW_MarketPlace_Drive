<template>
  <Dialog v-model="open" :options="{ title: __('New Version'), size: 'sm' }">
    <template #body-content>
      <Input v-model="snapshotMessage" :label="__('Message')" />
    </template>
    <template #actions>
      <Button :variant="'solid'" class="w-full" @click="save">{{__('Create')}}</Button>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, defineEmits, defineProps, onBeforeUnmount } from "vue"
import { Dialog, Button, Input } from "frappe-ui"

defineOptions({
  inheritAttrs: false,
})
const snapshotMessage = ref("")

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
})
const emit = defineEmits(["update:modelValue", "success"])

const open = computed({
  get: () => props.modelValue,
  set: (value) => emit("update:modelValue", value),
})

const save = () => {
  emit("success", snapshotMessage.value)
  emit("update:modelValue", false)
}
</script>
