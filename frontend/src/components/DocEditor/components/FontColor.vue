<template>
  <Popover transition="default">
    <template #target="{ togglePopover, isOpen }">
      <slot
        v-bind="{ onClick: () => togglePopover(), isActive: isOpen }"
      ></slot>
    </template>
    <template #body-main>
      <div class="p-2">
        <div class="text-sm text-gray-700">{{__('Text Color')}}</div>
        <div class="mt-1 grid grid-cols-8 gap-1">
          <Tooltip
            v-for="color in foregroundColors"
            :key="color.name"
            class="flex"
            :text="color.name"
          >
            <button
              :aria-label="color.name"
              class="flex h-5 w-5 items-center justify-center rounded border text-base"
              :style="{
                color: color.hex,
              }"
              @click="setForegroundColor(color)"
            >
              A
            </button>
          </Tooltip>
        </div>
        <div class="mt-2 text-sm text-gray-700">{{__('Background Color')}}</div>
        <div class="mt-1 grid grid-cols-8 gap-1">
          <Tooltip
            v-for="color in backgroundColors"
            :key="color.name"
            class="flex"
            :text="color.name"
          >
            <button
              :aria-label="color.name"
              class="flex h-5 w-5 items-center justify-center rounded border text-base text-gray-900"
              :class="!color.hex ? 'border-gray-200' : 'border-transparent'"
              :style="{
                backgroundColor: color.hex,
              }"
              @click="setBackgroundColor(color)"
            >
              A
            </button>
          </Tooltip>
        </div>
      </div>
    </template>
  </Popover>
</template>
<script>
import { Popover, Tooltip } from "frappe-ui"

export default {
  name: "FontColor",
  components: { Popover, Tooltip },
  props: ["editor"],
  computed: {
    foregroundColors() {
      // tailwind css colors, scale 600
      return [
        { name: "Default", hex: "#1F272E" },
        { name: "Yellow", hex: "#ca8a04" },
        { name: "Orange", hex: "#ea580c" },
        { name: "Red", hex: "#dc2626" },
        { name: "Green", hex: "#16a34a" },
        { name: "Blue", hex: "#1579D0" },
        { name: "Purple", hex: "#9333ea" },
        { name: "Pink", hex: "#db2777" },
      ]
    },
    backgroundColors() {
      // tailwind css colors, scale 100
      return [
        { name: "Default", hex: null },
        { name: "Yellow", hex: "#fef9c3" },
        { name: "Orange", hex: "#ffedd5" },
        { name: "Red", hex: "#fee2e2" },
        { name: "Green", hex: "#dcfce7" },
        { name: "Blue", hex: "#D3E9FC" },
        { name: "Purple", hex: "#f3e8ff" },
        { name: "Pink", hex: "#fce7f3" },
      ]
    },
  },
  methods: {
    setBackgroundColor(color) {
      if (color.name != "Default") {
        this.editor.chain().focus().toggleHighlight({ color: color.hex }).run()
      } else {
        this.editor.chain().focus().unsetHighlight().run()
      }
    },
    setForegroundColor(color) {
      if (color.name != "Default") {
        this.editor.chain().focus().setColor(color.hex).run()
      } else {
        this.editor.chain().focus().unsetColor().run()
      }
    },
  },
}
</script>
