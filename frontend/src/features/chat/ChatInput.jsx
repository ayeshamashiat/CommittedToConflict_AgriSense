import { useRef, useState } from 'react'
import clsx from 'clsx'
import Button from '../../components/ui/Button.jsx'
import { useAppState } from '../../context/useAppState.js'
import { useTranslation } from '../../context/useTranslation.js'
import { useSendMessage } from './useSendMessage.js'
import { SPEECH_LANG } from '../../lib/i18n.js'

// Tier 2: voice interaction (speech-to-text) via the browser's built-in Web
// Speech API — no external service/key needed, works fully client-side.
// Support varies by browser (best in Chrome/Edge); the mic button simply
// doesn't render where it's unavailable rather than showing a dead control.
const SpeechRecognitionAPI =
  typeof window !== 'undefined' ? window.SpeechRecognition || window.webkitSpeechRecognition : null

// Maps the Web Speech API's terse error codes to something a farmer can
// actually act on — the API only ever reports these on its onerror event,
// with no message text, so without this the mic button would fail silently
// and look identical to "voice isn't working" from a stuck/broken button.
const MIC_ERROR_MESSAGES = {
  'not-allowed': 'Microphone access was blocked. Please allow microphone permission and try again.',
  'no-speech': "Didn't catch that — no speech detected. Try again.",
  'audio-capture': 'No microphone was found on this device.',
  network: 'Voice recognition needs an internet connection.',
}

export default function ChatInput() {
  const [text, setText] = useState('')
  const [isListening, setIsListening] = useState(false)
  const [micError, setMicError] = useState('')
  const recognitionRef = useRef(null)
  const { state } = useAppState()
  const { t, language } = useTranslation()
  const send = useSendMessage()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!text.trim() || state.chat.isAgentTyping) return
    send(text)
    setText('')
  }

  const toggleListening = () => {
    if (!SpeechRecognitionAPI) return

    if (isListening) {
      recognitionRef.current?.stop()
      return
    }

    setMicError('')
    const recognition = new SpeechRecognitionAPI()
    recognition.lang = SPEECH_LANG[language] ?? 'en-US'
    recognition.interimResults = false
    recognition.maxAlternatives = 1

    recognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript ?? ''
      setText((prev) => (prev ? `${prev} ${transcript}` : transcript))
    }
    recognition.onend = () => setIsListening(false)
    recognition.onerror = (event) => {
      setIsListening(false)
      if (event.error !== 'aborted') {
        setMicError(MIC_ERROR_MESSAGES[event.error] ?? `Voice input failed (${event.error}).`)
      }
    }

    recognitionRef.current = recognition
    recognition.start()
    setIsListening(true)
  }

  return (
    <form onSubmit={handleSubmit} className="flex shrink-0 flex-col gap-1 border-t border-earth-100 p-3">
      {micError && <p className="px-1 text-xs text-red-600">{micError}</p>}
      <div className="flex items-end gap-2">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSubmit(e)
          }
        }}
        rows={1}
        placeholder={isListening ? t('listening') : t('chatPlaceholder')}
        className="max-h-32 flex-1 resize-none rounded-xl border border-earth-100 bg-wheat-50 px-3 py-2.5 text-sm text-stone-800 outline-none focus:border-leaf-400"
      />
      {SpeechRecognitionAPI && (
        <button
          type="button"
          onClick={toggleListening}
          title={t('speak')}
          aria-label={t('speak')}
          className={clsx(
            'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border text-lg transition-colors',
            isListening
              ? 'border-red-300 bg-red-50 text-red-600 animate-pulse'
              : 'border-earth-100 bg-wheat-50 text-stone-500 hover:bg-wheat-100',
          )}
        >
          🎤
        </button>
      )}
      <Button type="submit" disabled={!text.trim() || state.chat.isAgentTyping}>
        {t('send')}
      </Button>
      </div>
    </form>
  )
}
