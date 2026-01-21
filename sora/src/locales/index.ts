import { createI18n } from 'vue-i18n'
import en from './en'
import zh from './zh'

// Get saved language from localStorage, default to 'en'
const savedLanguage = localStorage.getItem('app-language') || 'en'

const i18n = createI18n({
    legacy: false, // Use Composition API mode
    locale: savedLanguage,
    fallbackLocale: 'en',
    messages: {
        en,
        zh
    }
})

export default i18n
