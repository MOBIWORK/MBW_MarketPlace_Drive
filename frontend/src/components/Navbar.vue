<template>
  <nav
    ondragstart="return false;"
    ondrop="return false;"
    class="bg-white top-0 border-b min-w-full"
  >
    <div
      class="mx-auto pl-4 py-2.5 pr-2 h-12 z-10 flex items-center justify-between"
    >
      <Breadcrumbs :items="$store.state.breadcrumbs" />
      <div class="flex gap-1">
        <div
          v-if="connectedUsers.length > 1 && isLoggedIn"
          class="hidden sm:flex bg-gray-200 rounded justify-center items-center px-1"
        >
          <UsersBar />
        </div>
        <div v-if="isLoggedIn" class="block sm:flex">
          <Button
            v-if="docStatus.length"
            variant="ghost"
            :class="'px-5 text-sm'"
          >
            <template #prefix>
              <FeatherIcon
                :name="
                  docStatus === 'Saved' ? 'cloud-lightning' : 'upload-cloud'
                "
                class="size-4"
              />
            </template>
            <template v-if="docStatus === 'Saved'">{{ docStatus }}</template>
            <i v-else>{{ docStatus }}</i>
          </Button>
          <Button
            v-if="
              ($route.name == 'File' || $route.name == 'Document') &&
              $store.state.activeEntity?.share
            "
            :variant="'solid'"
            class="bg-gray-200 rounded flex justify-center items-center px-1"
            @click="emitter.emit('showShareDialog')"
          >
            <template #prefix>
              <Share class="w-4" />
            </template>
            {{__('Share')}}
          </Button>
        </div>
        <div v-else class="ml-auto">
          <Button variant="solid" @click="$router.push({ name: 'Login' })">
            {{__('Sign In')}}
          </Button>
        </div>
      </div>
    </div>
  </nav>
</template>
<script setup>
import UsersBar from "./UsersBar.vue"
import { Button, Breadcrumbs } from "frappe-ui"
import Share from "./EspressoIcons/Share.vue"
import { FeatherIcon } from "frappe-ui"
import { useStore } from "vuex"
import { computed, ref, inject } from "vue"

const store = useStore()
const isLoggedIn = computed(() => store.getters.isLoggedIn)
const connectedUsers = computed(() => store.state.connectedUsers)

const docStatus = ref("")
const emitter = inject("emitter")

emitter.on("docSaving", () => {
  docStatus.value = "saving..."
})
emitter.on("docSaved", () => {
  docStatus.value = "Saved"
  setTimeout(() => (docStatus.value = ""), 1500)
})
</script>
