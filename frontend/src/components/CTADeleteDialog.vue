<template>
  <Dialog v-model="open" :options="{ title: title, size: 'sm' }">
    <template #body-content>
      <p class="text-gray-600">
        {{ message }}
      </p>
      <div class="flex mt-5">
        <Button
          :variant="buttonVariant"
          theme="red"
          icon-left="trash-2"
          class="w-full"
          :loading="$resources.action.loading"
          @click="$resources.action.submit()"
        >
          {{ buttonText }}
        </Button>
      </div>
    </template>
  </Dialog>
</template>
<script>
import { Dialog } from "frappe-ui"

export default {
  name: "CTADeleteDialog",
  components: {
    Dialog,
  },
  props: {
    modelValue: {
      type: Boolean,
      required: true,
    },
    entities: {
      type: Array,
      required: false,
      default: null,
    },
    clearAll: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  emits: ["update:modelValue", "success"],
  data: () => ({
    title: "",
    message: "",
    buttonText: "",
    buttonVariant: "subtle",
    url: null,
  }),
  computed: {
    open: {
      get() {
        return this.modelValue
      },
      set(value) {
        this.$emit("update:modelValue", value)
      },
    },
  },
  mounted() {
    this.evalDialog()
  },
  methods: {
    evalDialog() {
      if (this.$route.name === "Recents") {
        this.title = __("Clear Recents?")
        this.message = __("All your recently viewed files will be cleared")
        this.buttonText = __("Clear")
        this.url = "drive.api.files.remove_recents"
      }
      if (this.$route.name === "Favourites") {
        this.title = __("Clear Favourites?")
        this.message =
          __("All your favourited items will be marked as unfavourite.")
        this.buttonText = __("Unfavourite")
        this.url = "drive.api.files.add_or_remove_favourites"
      }
      if (this.$route.name === "Trash") {
        this.title = __("Delete Forever?")
        this.message =
          __("All items in your Trash will be deleted forever. This is an irreversible process.")
        this.buttonVariant = "solid"
        this.buttonText = __("Delete")
        this.url = "drive.api.files.delete_entities"
      }
    },
  },
  resources: {
    action() {
      return {
        url: this.url,
        params: {
          clear_all: true,
        },
        onSuccess(data) {
          this.$emit("success", data)
        },
        onError(error) {
        },
      }
    },
  },
}
</script>
