import { createResource } from "frappe-ui"
import { defaultLanguage } from "./composables/language"
import { ref } from "vue"

export const transformLanguage = ref(false)

export default function translationPlugin(app) {
  app.config.globalProperties.__ = translate
  window.__ = translate
  if (!window.translatedMessages) fetchTranslations()
}

function format(message, replace) {
  return message.replace(/{(\d+)}/g, function (match, number) {
    return typeof replace[number] != "undefined" ? replace[number] : match
  })
}

function translate(message, replace, context = null) {
  let translatedMessages = window.translatedMessages || {}
  let translatedMessage = ""

  if (context) {
    let key = `${message}:${context}`
    if (translatedMessages[key]) {
      translatedMessage = translatedMessages[key]
    }
  }

  if (!translatedMessage) {
    translatedMessage = translatedMessages[message] || message
  }

  const hasPlaceholders = /{\d+}/.test(message)
  if (!hasPlaceholders) {
    return translatedMessage
  }

  return format(translatedMessage, replace)
}

function fetchTranslations(lang) {
  let language = lang || defaultLanguage.value || "vi"
  createResource({
    url: "drive.api.get_translations",
    params: { lang: language },
    cache: `${language}_` + "translations",
    auto: true,
    transform: (data) => {
      window.translatedMessages = data
      transformLanguage.value = !transformLanguage.value
    },
  })
}
