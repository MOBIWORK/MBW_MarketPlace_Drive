<template>
  <GenericPage
    :getEntities="getTrash"
    :icon="Trash"
    :primaryMessage="__('Trash is Empty')"
  />
</template>

<script setup>
import GenericPage from "@/components/GenericPage.vue"
import Trash from "../components/EspressoIcons/Trash.vue"
import { getTrash } from "@/resources/files"
</script>
