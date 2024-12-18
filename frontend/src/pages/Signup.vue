<template>
  <LoginBox
    v-if="!request_status_ok"
    title="Create your account"
    :class="{ 'pointer-events-none': loading }"
  >
    <form class="flex flex-col" @submit.prevent="signup()">
      <Input
        v-model="fullName"
        class="mb-2"
        :label="__('Name')"
        type="text"
        autocomplete="name"
        required
      />
      <Input
        v-model="email"
        class="mb-2"
        label="Email"
        type="email"
        autocomplete="email"
        required
      />
      <Input
        v-model="pwd"
        :label="__('Password')"
        type="password"
        required
      />
      <ErrorMessage class="mt-4" :message="errorMessage" />
      <Button
        class="mt-4 focus:ring-0 focus:ring-offset-0"
        :loading="loading"
        variant="solid"
      >
        {{__('Submit')}}
      </Button>
      <div class="mt-10 text-center border-t">
        <div class="transform -translate-y-1/2">
          <span
            class="px-2 text-xs leading-8 tracking-wider text-gray-800 bg-white"
          >
            {{__('OR')}}
          </span>
        </div>
      </div>
      <div class="flex justify-center items-center">
        <span>{{__('Already have an account?')}}</span>
        <span>&nbsp;&nbsp;</span>
        <router-link class="text-base text-blue-500" to="/login">
          {{__('LOG IN')}}
        </router-link>
      </div>
    </form>
  </LoginBox>
  <div v-else class="p-5 sm:p-20">
    <div
      class="flex flex-col flex-1 items-center p-10 text-base bg-white rounded-lg mx-auto shadow-lg w-full sm:w-96"
    >
      <div class="w-8 h-8 p-1 rounded-full" :class="iconContainerClass">
        <FeatherIcon :name="icon" :class="iconClass" />
      </div>
      <h2 class="mt-4 text-lg font-medium text-center text-gray-900">
        {{ response.title }}
      </h2>
      <p class="text-base text-center text-gray-700 mt-2">
        <!-- eslint-disable-next-line vue/no-v-html -->
        <span v-html="response.message" />
      </p>
    </div>
  </div>
</template>

<script>
import { Input, ErrorMessage, FeatherIcon } from "frappe-ui"
import LoginBox from "@/components/LoginBox.vue"

export default {
  name: "Signup",
  components: {
    Input,
    ErrorMessage,
    FeatherIcon,
    LoginBox,
  },
  data() {
    return {
      email: null,
      fullName: null,
      pwd: null,
      errorMessage: null,
      loading: false,
      request_status_ok: false,
      response: {
        title: null,
        message: null,
        color: null,
      },
    }
  },
  computed: {
    iconClass() {
      return {
        red: "text-red-500",
        green: "text-green-500",
      }[this.response.color]
    },
    iconContainerClass() {
      return {
        red: "bg-red-100",
        green: "bg-green-100",
      }[this.response.color]
    },
    icon() {
      return {
        red: "x",
        green: "check",
      }[this.response.color]
    },
  },
  methods: {
    async signup() {
      try {
        this.errorMessage = null
        this.loading = true
        if (this.email && this.fullName && this.pwd) {
          let res = await this.$call("drive.api.user.sign_up", {
            full_name: this.fullName,
            email: this.email,
            redirect_to: "drive",
            pwd: this.pwd
          })
          if (res) {
            let [code] = res
            if (code > 0) this.request_status_ok = true
            if (code === 0) {
              this.errorMessage = __("This account already exists")
            } else if (code === 1) {
              this.response = {
                title: __("Register Account Successfully"),
                message: `${__('Your account was created successfully. Please')} <a href="/drive" class="text-base text-blue-500">${__('LOGIN IN')}</a> ${__('to use the service')}.`,
                color: "green",
              }
            } else {
              this.request_status_ok = true
              this.response = {
                title: __("Verification Needed"),
                message: __('Verification email was not sent. Please ask your administrator to verify your sign-up'),
                color: "red",
              }
            }
          }
        }
      } catch (error) {
        this.errorMessage = error.messages.join("\n")
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
