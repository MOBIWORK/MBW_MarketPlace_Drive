<template>
  <div
    class="rounded-full relative flex items-center justify-center"
    :class="[
      colorClasses,
      sizeClasses,
      { 'opacity-50 cursor-not-allowed': props.disabled },
    ]"
  >
    <LucideGlobe2
      v-if="accessType === 'public'"
      :class="size == 'md' ? 'h-[90%] w-[90%]' : 'h-[70%] w-[70%]'"
    />
    <LucideBuilding
      v-else-if="accessType === 'team'"
      :class="size == 'sm' ? 'h-[90%] w-[90%]' : 'h-[70%] w-[70%]'"
    />
    <LucideLock
      v-else
      class=""
      :class="size == 'md' ? 'h-[80%] w-[80%]' : 'h-[65%] w-[65%]'"
    />
  </div>
</template>
<script setup>
import { computed } from "vue"

const props = defineProps({
  accessType: {
    type: String,
    default: "",
  },
  size: {
    type: String,
    default: "md",
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const colorClasses = computed(() => {
  if (props.disabled) {
    return "bg-gray-300 text-gray-500"
  } else if (props.accessType === "team") {
    return "bg-blue-100 text-blue-500"
  } else if (props.accessType === "public") {
    return "bg-red-100 text-red-500"
  }
  return "text-gray-700 bg-gray-300"
})

const sizeClasses = computed(() => {
  return {
    xs: "w-3 h-3",
    sm: "size-4",
    md: "w-6 h-6",
    lg: "w-7 h-7",
    xl: "w-8 h-8",
    "2xl": "w-10 h-10",
    "3xl": "w-11.5 h-11.5",
  }[props.size]
})
</script>
