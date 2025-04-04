<template>
  <Dialog v-model="open" :options="{ title: __('Are you sure?'), size: 'sm' }">
    <template #body-content>
      <p class="text-gray-600">
        {{ current.message }}
      </p>
      <div class="flex mt-5">
        <Button
          :variant="current.buttonVariant"
          theme="red"
          icon-left="trash-2"
          class="w-full"
          :loading="current.resource.loading"
          @click="current.resource.submit(null) && emit('success')"
        >
          {{ current.buttonText }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import { Dialog } from "frappe-ui"
import { computed } from "vue"
import { useRoute } from "vue-router"
import { toggleFav, clearRecent, clearTrash } from "@/resources/files"

const props = defineProps({
  modelValue: String,
  entities: Array,
})
const emit = defineEmits(["update:modelValue", "success"])

const open = computed({
  get: () => {
    return props.modelValue === "cta"
  },
  set: (value) => {
    emit("update:modelValue", value)
  },
})

document.onkeydown = (e) => {
  if (e.key === "Escape") open.value = false
}

const route = useRoute()
const dialogConfigs = [
  {
    route: "Recents",
    message: __("All your recently viewed files will be cleared."),
    buttonText: __("Clear"),
    resource: clearRecent,
  },
  {
    route: "Favourites",
    message: __("All your favourite items will be cleared."),
    buttonText: __("Clear"),
    resource: toggleFav,
  },
  {
    route: "Trash",
    message:
      __("All items in your Trash will be deleted forever. This is an irreversible process."),
    buttonVariant: "solid",
    buttonText: __("Delete"),
    resource: clearTrash,
  },
]
const current = dialogConfigs.find(({ route: _route }) => _route === route.name)
</script>
