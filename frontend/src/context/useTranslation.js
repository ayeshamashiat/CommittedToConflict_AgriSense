import { useAppState } from './useAppState.js'
import { translate } from '../lib/i18n.js'

export function useTranslation() {
  const { state } = useAppState()
  const language = state.ui.language
  return { language, t: (key) => translate(language, key) }
}
