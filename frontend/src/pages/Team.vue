<template>
  <GenericPage
    :get-entities="getHome"
    :icon="Home"
    :primary-message="__('Home is empty')"
    :secondary-message="__('Add files by dropping them here')"
  />
</template>

<script setup>
import Home from "../components/EspressoIcons/Home.vue"
import GenericPage from "@/components/GenericPage.vue"
import { getHome } from "@/resources/files"
import { useStore } from "vuex"

const store = useStore()
store.commit("setCurrentFolder", "")
store.commit("setCurrentFolderID", "")
</script>
