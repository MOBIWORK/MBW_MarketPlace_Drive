<template>
  <div
    class="flex gap-x-3 flex-wrap justify-start items-center w-full px-2 my-3"
  >
    <div class="flex w-full justify-start items-center flex-wrap">
      <Breadcrumbs :items="modifiedBreadcrumbs" />

      <div
        v-if="$route.name === 'Shared'"
        class="ml-5 bg-gray-100 rounded-[10px] space-x-0.5 h-7 flex items-center px-0.5 py-1"
      >
        <Button
          variant="ghost"
          class="max-h-6 leading-none transition-colors focus:outline-none"
          :class="[
            $store.state.shareView === 'with'
              ? 'bg-white shadow-sm hover:bg-white active:bg-white'
              : '',
          ]"
          @click="$store.commit('toggleShareView', 'with')"
        >
          {{__('With you')}}
        </Button>
        <Button
          variant="ghost"
          class="max-h-6 leading-none transition-colors focus:outline-none"
          :class="[
            $store.state.shareView === 'by'
              ? 'bg-white shadow-sm hover:bg-white active:bg-white'
              : '',
          ]"
          @click="$store.commit('toggleShareView', 'by')"
        >
         {{__('By you')}}
        </Button>
      </div>
      <div class="flex flex-wrap items-start justify-end gap-1 ml-3">
        <div v-for="(item, index) in activeFilters" :key="index">
          <div class="flex items-center border rounded pl-2 py-1 h-7 text-base">
            <component :is="item.icon"></component>
            <span class="text-sm ml-2">{{ item.label }}</span>

            <Button
              variant="minimal"
              @click="
                item.title
                  ? activeTags.splice(index, 1)
                  : activeFilters.splice(index, 1)
              "
            >
              <template #icon>
                <FeatherIcon class="h-3 w-3" name="x" />
              </template>
            </Button>
          </div>
        </div>
        <div v-for="(item, index) in activeTags" :key="index">
          <div class="flex items-center border rounded pl-2 py-1 h-7 text-base">
            <svg
              v-if="item.color"
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle
                r="4.5"
                cx="8"
                cy="8"
                :fill="item.color"
                :stroke="item.color"
                stroke-width="3"
              />
            </svg>
            <span class="text-sm ml-2">{{ item.title }}</span>

            <Button
              variant="minimal"
              @click="$store.state.activeTags.splice(index, 1)"
            >
              <template #icon>
                <FeatherIcon class="h-3 w-3" name="x" />
              </template>
            </Button>
          </div>
        </div>
      </div>

      <div class="ml-auto flex gap-x-3 items-center">
        <Dropdown
          v-if="columnHeaders"
          :options="orderByItems"
          placement="right"
          class="basis-auto"
        >
          <div class="flex items-center whitespace-nowrap">
            <Button
              class="text-sm h-7 border-r border-slate-200 rounded-r-none"
              @click.stop="toggleAscending"
            >
              <DownArrow
                :class="{ '[transform:rotateX(180deg)]': sortOrder.ascending }"
                class="h-3.5"
              />
            </Button>
            <Button class="text-sm h-7 rounded-l-none flex-1 md:block">
              {{ sortOrder.label }}
            </Button>
          </div>
        </Dropdown>
        <Dropdown :options="filterItems" placement="right">
          <Button class="whitespace-nowrap"
            >{{__('Filter')}}
            <template #prefix>
              <Filter />
            </template>
            <template #suffix>
              <ChevronDown />
            </template>
          </Button>
        </Dropdown>
        <div
          v-if="false"
          class="bg-gray-100 rounded-md space-x-0.5 h-7 px-0.5 py-1 flex items-center"
        >
          <Button
            variant="ghost"
            class="max-h-6 leading-none transition-colors focus:outline-none"
            :class="[
              $store.state.view === 'grid'
                ? 'bg-white shadow-sm hover:bg-white active:bg-white'
                : '',
            ]"
            @click="$store.commit('toggleView', 'grid')"
          >
            <ViewGrid />
          </Button>
          <Button
            variant="ghost"
            class="max-h-6 leading-none transition-colors focus:outline-none"
            :class="[
              $store.state.view === 'list'
                ? 'bg-white shadow-sm hover:bg-white active:bg-white'
                : '',
            ]"
            @click="$store.commit('toggleView', 'list')"
          >
            <ViewList />
          </Button>
        </div>

        <div v-if="!$store.getters.isLoggedIn" class="ml-2">
          <Button variant="solid" @click="$router.push({ name: 'Login' })">
            {{__('Sign In')}}
          </Button>
        </div>
        <template v-for="button of possibleButtons" :key="button.route">
          <Button
            v-if="$route.name === button.route"
            class="line-clamp-1 truncate w-full"
            :disabled="!button.entities.data.length"
            variant="subtle"
            :theme="button.theme || 'gray'"
            @click="emitter.emit('showCTADelete')"
          >
            <template #prefix>
              <FeatherIcon :name="button.icon" class="w-4" />
            </template>
            {{ button.label }}
          </Button>
        </template>
        <Dropdown
          :options="newEntityOptions"
          placement="left"
          class="basis-5/12 lg:basis-auto"
        >
          <Button variant="solid">
            <FeatherIcon name="upload" class="w-4" />
          </Button>
        </Dropdown>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FeatherIcon, Button, Dropdown, Breadcrumbs } from "frappe-ui"
import ViewGrid from "@/components/EspressoIcons/ViewGrid.vue"
import ViewList from "@/components/EspressoIcons/ViewList.vue"
import DownArrow from "./EspressoIcons/DownArrow.vue"
import Filter from "./EspressoIcons/Filter.vue"
import ChevronDown from "./EspressoIcons/ChevronDown.vue"
import Folder from "./MimeIcons/Folder.vue"
import Archive from "./MimeIcons/Archive.vue"
import Document from "./MimeIcons/Document.vue"
import Spreadsheet from "./MimeIcons/Spreadsheet.vue"
import Presentation from "./MimeIcons/Presentation.vue"
import Audio from "./MimeIcons/Audio.vue"
import Image from "./MimeIcons/Image.vue"
import Video from "./MimeIcons/Video.vue"
import PDF from "./MimeIcons/PDF.vue"
import Unknown from "./MimeIcons/Unknown.vue"
import NewFolder from "./EspressoIcons/NewFolder.vue"
import Link from "./EspressoIcons/Link.vue"
import FileUpload from "./EspressoIcons/File-upload.vue"
import FolderUpload from "./EspressoIcons/Folder-upload.vue"
import NewFile from "./EspressoIcons/NewFile.vue"
import emitter from "@/emitter"
import { computed, onMounted, watch, ref } from "vue"
import { useStore } from "vuex"
import {
  getRecents,
  getFavourites,
  getTrash,
  createDocument,
} from "@/resources/files"
import { useRoute, useRouter } from "vue-router"

const store = useStore()
const props = defineProps({
  columnHeaders: Array,
  getEntitities: Object,
})
const a = ref(store.state.breadcrumbs)
const modifiedBreadcrumbs = computed(() => {
  return store.state.breadcrumbs.map((item) => ({
    ...item,
    label: __(item.label),
  }));
});
const sortOrder = ref(store.state.sortOrder)
watch(sortOrder, (val) => store.commit("setSortOrder", val))
const activeFilters = ref(store.state.activeFilters)
watch(activeFilters.value, (val) => store.commit("setActiveFilters", val))
const route = useRoute()
const router = useRouter()

const activeTags = computed(() => store.state.activeTags)
const orderByItems = computed(() => {
  return props.columnHeaders.map((header) => ({
    ...header,
    onClick: () =>
      (sortOrder.value = {
        field: header.field,
        label: header.label,
        ascending: sortOrder.value?.ascending,
      }),
  }))
})
const TYPES = [
  {
    label: __("Folder"),
    value: "Folder",
    icon: Folder,
  },
  {
    label: __("Image"),
    value: "Image",
    icon: Image,
  },
  {
    label: __("Audio"),
    value: "Audio",
    icon: Audio,
  },
  {
    label: __("Video"),
    value: "Video",
    icon: Video,
  },
  {
    label: __("PDF"),
    value: "PDF",
    icon: PDF,
  },
  {
    label: __("Document"),
    value: "Document",
    icon: Document,
  },
  {
    label: __("Spreadsheet"),
    value: "Spreadsheet",
    icon: Spreadsheet,
  },
  {
    label: __("Archive"),
    value: "Archive",
    icon: Archive,
  },
  {
    label: __("Presentation"),
    value: "Presentation",
    icon: Presentation,
  },
  {
    label: __("Unknown"),
    value: "Unknown",
    icon: Unknown,
  },
]
TYPES.forEach((t) => {
  t.onClick = () => activeFilters.value.push(t)
})
const filterItems = computed(() => {
  return TYPES.filter((item) => !activeFilters.value.includes(item.value))
})
onMounted(() => {
  for (let element of document.getElementsByTagName("button")) {
    element.classList.remove("focus:ring-2", "focus:ring-offset-2")
  }
})
const toggleAscending = () => {
  sortOrder.value = {
    field: sortOrder.value.field,
    label: sortOrder.value.label,
    ascending: !sortOrder.value.ascending,
  }
}

const possibleButtons = [
  { route: "Recents", label: __("Clear"), icon: "clock", entities: getRecents },
  {
    route: "Favourites",
    label: __("Clear"),
    icon: "star",
    entities: getFavourites,
  },
  {
    route: "Trash",
    label: __("Empty Trash"),
    icon: "trash",
    entities: getTrash,
    theme: "red",
  },
]

const newDocument = async () => {
  let data = await createDocument.submit({
    title: "Untitled Document",
    team: route.params.team,
    personal: store.state.breadcrumbs[0].label === "Home" ? 1 : 0,
    content: null,
    parent: store.state.currentFolderID,
  })
  window.open(
    router.resolve({
      name: "Document",
      params: { team: route.params.team, entityName: data.name },
    }).href
  )
}
const newEntityOptions = [
  {
    group: __("Upload"),
    items: [
      {
        label: __("Upload File"),
        icon: FileUpload,
        onClick: () => emitter.emit("uploadFile"),
      },
      {
        label: __("Upload Folder"),
        icon: FolderUpload,
        onClick: () => emitter.emit("uploadFolder"),
      },
    ],
  },
  {
    group: __("New..."),
    items: [
      {
        label: __("Document"),
        icon: NewFile,
        onClick: newDocument,
      },
      {
        label: __("Folder"),
        icon: NewFolder,
        onClick: () => emitter.emit("newFolder"),
      },

      {
        label: __("New Link"),
        icon: Link,
        onClick: () => emitter.emit("newLink"),
      },
    ],
  },
]
</script>
