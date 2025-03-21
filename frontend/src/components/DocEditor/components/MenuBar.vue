<template>
  <div class="flex px-3 bg-white pb-2 shadow-sm">
    <Dropdown :options="fileMenuOptions">
      <template #default="{ open }">
        <button
          :class="[
            'rounded-md px-2 py-1 text-base font-medium',
            open ? 'bg-slate-100' : 'bg-white-200',
          ]"
        >
          {{__('File')}}
        </button>
      </template>
    </Dropdown>
    <Dropdown
      :options="[
        {
          group: __('New'),
          hideLabel: true,
          items: [
            {
              label: __('Undo'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Redo'),
              handler: () => alert(__('New Window')),
              // show/hide option based on condition function
              condition: () => true,
            },
            {
              label: __('Cut'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Copy'),
              handler: () => alert(__('New Window')),
              // show/hide option based on condition function
              condition: () => true,
            },
            {
              label: __('Paste'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Paste without Formatting'),
              handler: () => alert(__('New Window')),
              // show/hide option based on condition function
              condition: () => true,
            },
            {
              label: __('Select All'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Find and Replace'),
              handler: () => alert(__('New Window')),
              // show/hide option based on condition function
              condition: () => true,
            },
          ],
        },
      ]"
    >
      <template #default="{ open }">
        <button
          :class="[
            'rounded-md px-2 py-1 text-base font-medium',
            open ? 'bg-slate-100' : 'bg-white-200',
          ]"
        >
          {{__('Edit')}}
        </button>
      </template>
    </Dropdown>
    <Dropdown
      :options="[
        {
          group: __('New'),
          hideLabel: true,
          items: [
            {
              label: __('Mode'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Text Width'),
              handler: () => alert(__('New Window')),
              // show/hide option based on condition function
              condition: () => true,
            },
            {
              label: __('Focus Mode'),
              handler: () => alert(__('New Window')),
              // show/hide option based on condition function
              condition: () => true,
            },
            {
              label: __('Full screen'),
              handler: () => alert(__('New Window')),
              // show/hide option based on condition function
              condition: () => true,
            },
          ],
        },
      ]"
    >
      <template #default="{ open }">
        <button
          :class="[
            'rounded-md px-2 py-1 text-base font-medium',
            open ? 'bg-slate-100' : 'bg-white-200',
          ]"
        >
          {{__('View')}}
        </button>
      </template>
    </Dropdown>
    <Dropdown
      :options="[
        {
          group: __('Insert'),
          hideLabel: true,
          items: [
            {
              label: __('Image'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Video'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Table'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Link'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Horizontal Line'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Emoji'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Blockquote'),
              handler: () => alert(__('New File')),
            },
          ],
        },
      ]"
    >
      <template #default="{ open }">
        <button
          :class="[
            'rounded-md px-2 py-1 text-base font-medium',
            open ? 'bg-slate-100' : 'bg-white-200',
          ]"
        >
          {{__('Insert')}}
        </button>
      </template>
    </Dropdown>
    <Dropdown
      :options="[
        {
          group: __('New'),
          hideLabel: true,
          items: [
            {
              label: __('Text'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Style'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Alignment'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Line Height'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Horizontal Line'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('List and Numbering'),
              handler: () => alert(__('New File')),
            },
            {
              label: __('Table'),
              handler: () => alert(__('New File')),
            },
          ],
        },
      ]"
    >
      <template #default="{ open }">
        <button
          :class="[
            'rounded-md px-2 py-1 text-base font-medium',
            open ? 'bg-slate-100' : 'bg-white-200',
          ]"
        >
          {{__('Format')}}
        </button>
      </template>
    </Dropdown>
    <!--     <div class="ml-auto">
      <Dropdown :options="modeMenuOptions">
        <template v-slot="{ open }">
          <Button :icon-left="modeButtonIcon" :label="modeButtonText" />
        </template>
      </Dropdown>
    </div> -->
    <ShareDialog
      v-if="showShareDialog"
      v-model="showShareDialog"
      :entity-name="entityName"
    />
    <!-- Ideally convert the component to recieve both an array or a single entity -->
    <GeneralDialog
      v-model="showRemoveDialog"
      :entities="entityName"
      :for="'remove'"
      @success="
        () => {
          $router.go(-1)
        }
      "
    />
  </div>
</template>

<script>
import { Dropdown } from "frappe-ui"
import ShareDialog from "@/components/ShareDialog.vue"
import GeneralDialog from "@/components/GeneralDialog.vue"

export default {
  name: "MenuBar",
  components: {
    Dropdown,
    ShareDialog,
    GeneralDialog,
  },
  props: {
    entityName: {
      default: "",
      type: String,
      required: false,
    },
    editable: {
      type: Boolean,
      required: false,
    },
    isCommentModeOn: {
      type: Boolean,
      required: false,
    },
    isReadOnly: {
      type: Boolean,
      required: false,
    },
  },
  emits: ["toggleCommentMode", "toggleEditMode", "toggleReadMode"],
  data() {
    return {
      showShareDialog: false,
      showRemoveDialog: false,
      modeButtonIcon: "",
      fileMenuOptions: [
        /*         {
          group: "New",
          hideLabel: true,
          items: [
            {
              icon: "file-plus",
              label: "New File",
              handler: () => this.emitter.emit("createNewDocument"),
            },
          ],
        }, */
        {
          group: __("Current File"),
          hideLabel: true,
          items: [
            /* Look into making a modal/dialog/portal for this and opening a file from the current file view*/
            /* {
              icon: "copy",
              label: "Copy File",
              handler: () =>
                this.$store.commit("setPasteData", {
                  entities: this.entityName,
                  action: "copy",
                }),
            }, */
            {
              icon: "share-2",
              label: __("Share File"),
              handler: () => (this.showShareDialog = true),
            },
            {
              icon: "star",
              label: __("Add to favourites"),
              handler: () => alert(__("Open File")),
            },
          ],
        },
        {
          group: __("Delete"),
          hideLabel: true,
          items: [
            {
              icon: "trash-2",
              label: __("Delete File"),
              handler: () => (this.showRemoveDialog = true),
            },
          ],
        },
      ],
      modeMenuOptions: [
        {
          group: __("Mode"),
          hideLabel: true,
          items: [
            {
              icon: "eye",
              label: __("Reading"),
              handler: () => {
                this.emitter.emit("toggleReadMode")
              },
            },
            {
              icon: "edit-3",
              label: __("Editing"),
              handler: () => {
                this.emitter.emit("toggleEditMode")
              },
            },
            {
              icon: "message-square",
              label: __("Suggesting"),
              handler: () => {
                this.emitter.emit("toggleCommentMode")
              },
            },
          ],
        },
      ],
    }
  },
  computed: {
    modeButtonText() {
      if (this.editable) {
        this.modeButtonIcon = "edit-3"
        return __("Editing")
      } else if (this.isReadOnly) {
        this.modeButtonIcon = "eye"
        return __("Reading")
      } else if (this.isCommentModeOn) {
        this.modeButtonIcon = "message-square"
        return __("Suggesting")
      }
    },
  },
}
</script>
