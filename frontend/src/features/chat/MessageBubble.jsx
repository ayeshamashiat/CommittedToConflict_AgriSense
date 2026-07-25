import { useState } from 'react'
import clsx from 'clsx'
import { formatTime } from '../../lib/formatters.js'
import { useTranslation } from '../../context/useTranslation.js'
import { SPEECH_LANG } from '../../lib/i18n.js'

const speechSupported = typeof window !== 'undefined' && 'speechSynthesis' in window

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  const { t, language } = useTranslation()
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [speechError, setSpeechError] = useState('')

  const toggleReadAloud = () => {
    if (!speechSupported) return
    if (isSpeaking) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
      return
    }
    setSpeechError('')
    const utterance = new SpeechSynthesisUtterance(message.content)
    utterance.lang = SPEECH_LANG[language] ?? 'en-US'
    utterance.onend = () => setIsSpeaking(false)
    // The Web Speech API gives no message text on failure (e.g. no voices
    // installed for this language, or synthesis unsupported) — without
    // surfacing something here, the button just silently does nothing,
    // indistinguishable from being broken.
    utterance.onerror = (event) => {
      setIsSpeaking(false)
      setSpeechError(`Couldn't read this aloud (${event.error || 'unknown error'}).`)
    }
    window.speechSynthesis.cancel()
    window.speechSynthesis.speak(utterance)
    setIsSpeaking(true)
  }

  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={clsx(
          'group max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm',
          isUser
            ? 'rounded-br-sm bg-leaf-600 text-wheat-50'
            : 'rounded-bl-sm border border-earth-100 bg-wheat-50 text-stone-800',
        )}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        <div className="mt-1 flex items-center gap-2">
          <p className={clsx('text-[10px]', isUser ? 'text-leaf-100' : 'text-stone-400')}>
            {formatTime(message.timestamp)}
          </p>
          {!isUser && speechSupported && (
            <button
              type="button"
              onClick={toggleReadAloud}
              title={isSpeaking ? t('stopReading') : t('readAloud')}
              aria-label={isSpeaking ? t('stopReading') : t('readAloud')}
              className="text-[11px] text-stone-400 opacity-0 transition-opacity hover:text-leaf-700 group-hover:opacity-100"
            >
              {isSpeaking ? '⏹️' : '🔊'}
            </button>
          )}
        </div>
        {speechError && <p className="mt-1 text-[10px] text-red-500">{speechError}</p>}
      </div>
    </div>
  )
}
