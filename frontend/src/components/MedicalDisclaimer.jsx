import React from 'react'
import { useTranslation } from 'react-i18next'

export default function MedicalDisclaimer() {
  const { t } = useTranslation()
  return <aside className="disclaimer" role="note">
    ℹ️ {t('not_a_medical_device')}
  </aside>
}

export { MedicalDisclaimer }
