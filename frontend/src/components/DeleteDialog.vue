<template>
  <Dialog v-model="open" :options="{ title: 'Delete Forever?', size: 'sm' }">
    <template #body-content>
      <p class="text-gray-600" v-if="entities != null">
        {{
            entities.length === 1
            ? `${entities.length} item`
            : `${entities.length} items`
        }}
        will be deleted forever. This is an irreversible process.
      </p>
      <div class="flex mt-5">
        <Button
          variant="solid"
          theme="red"
          icon-left="trash-2"
          class="w-full"
          :loading="$resources.delete.loading"
          @click="$resources.delete.submit()"
        >
          Delete Forever
        </Button>
      </div>
    </template>
  </Dialog>
</template>
<script>
import { Dialog } from "frappe-ui"
import { del } from "idb-keyval"

export default {
  name: "DeleteDialog",
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
      default: [],
    },
  },
  emits: ["update:modelValue", "success"],
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
  resources: {
    delete() {
      var me = this
      return {
        url: "drive.api.files.delete_entities",
        params: {
          entity_names: JSON.stringify(
            this.entities?.map((entity) => entity.name)
          ),
        },
        onSuccess(data) {
          me.entities.map((entity) => del(entity.name))
          me.$emit("success")
        },
        onError(error) {
        },
      }
    },
  },
}
</script>
