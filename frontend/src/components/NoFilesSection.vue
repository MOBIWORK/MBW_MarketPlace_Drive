<template>
  <div class="flex flex-col items-center justify-center">
    <div v-if="icon">
      <component :is="icon" class="w-14 stroke-[0] h-auto text-gray-500 pb-4" />
    </div>
    <svg
      v-else
      viewBox="0 0 78 85"
      class="w-[8%] fill-transparent stroke-2 pb-6"
    >
      <path
        d="M42 31H66 M42 51H66 M42 25H55 M42 45H55 M65 9V8C65 4.13401 61.866 1 58 1H8C4.13401 1 1 4.13401 1 8V66C1 69.866 4.13401 73 8 73H10 M70 12H20C16.134 12 13 15.134 13 19V77C13 80.866 16.134 84 20 84H70C73.866 84 77 80.866 77 77V19C77 15.134 73.866 12 70 12Z"
        stroke="#454545"
      />
      <path
        d="M32 43H26C24.8954 43 24 43.8954 24 45V51C24 52.1046 24.8954 53 26 53H32C33.1046 53 34 52.1046 34 51V45C34 43.8954 33.1046 43 32 43Z M32 23H26C24.8954 23 24 23.8954 24 25V31C24 32.1046 24.8954 33 26 33H32C33.1046 33 34 32.1046 34 31V25C34 23.8954 33.1046 23 32 23Z"
        stroke="#454545"
      />
    </svg>
    <p class="text-base text-gray-600 font-medium">{{ primaryMessage }}</p>
    <p class="text-sm text-gray-600">{{ secondaryMessage }}</p>
    <div class="flex mt-3" v-if="isHomePage">
      <Button
        :variant="'solid'"
        theme="gray"
        size="sm"
        @click="onUploadVideos()"
      >{{__('UPLOAD VIDEOS')}}</Button>
      <Button
        class="ml-3"
        :variant="'outline'"
        theme="gray"
        size="sm"
        @click="onShowMeAround()"
      >
        {{__('SHOW ME AROUND')}}
        <template #suffix>
          <FeatherIcon name="arrow-right" class="w-4" />
        </template>
      </Button>
    </div>
    <UploadVideoDialog
    v-if="showNewVideoDialog"
    v-model="showNewVideoDialog"
    :parent="$route.params.entityName"
  />
  </div>
</template>
<script>
import { Button, FeatherIcon } from 'frappe-ui'
import UploadVideoDialog from "@/components/Modals/UploadVideoDialog.vue"
export default {
  name: "NoFilesSection",
  components: {
    Button,
    UploadVideoDialog,
    FeatherIcon
  },
  props: {
    icon: {
      type: Object,
      default: null,
    },
    primaryMessage: {
      type: String,
      default: "You don't have any files yet",
    },
    secondaryMessage: {
      type: String,
      default: "Drop files here",
    },
    isHomePage: {
      type: Boolean,
      default: false
    }
  },
  data(){
    return {
      showNewVideoDialog: false
    }
  },
  methods: {
    onUploadVideos(){
      this.showNewVideoDialog = true
    },
    onShowMeAround(){
      this.$router.push({
        name: "IntrodutionApp",
      })
    }
  }
}
</script>
