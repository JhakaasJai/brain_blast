import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import en  from './locales/en.json'
import hi  from './locales/hi.json'
import as_ from './locales/as.json'
import kha from './locales/kha.json'
import mni from './locales/mni.json'

const savedLang = localStorage.getItem('lang') || 'en'

i18n
  .use(initReactI18next)
  .init({
    resources: {
      en:  { translation: en },
      hi:  { translation: hi },
      as:  { translation: as_ },
      kha: { translation: kha },
      mni: { translation: mni },
    },
    lng: savedLang,
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
  })

export default i18n
