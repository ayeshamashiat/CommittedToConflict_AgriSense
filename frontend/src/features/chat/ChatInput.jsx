import { useRef, useState } from 'react'
import clsx from 'clsx'
import Button from '../../components/ui/Button.jsx'
import { useAppState } from '../../context/useAppState.js'
import { useTranslation } from '../../context/useTranslation.js'
import { useSendMessage } from './useSendMessage.js'
import { transcribeAudio } from '../../api/client.js'

// Tier 2: voice interaction (speech-to-text) via server-side OpenAI Whisper
// (see backend/app/api/routes/transcribe.py), not the browser's Web Speech
// API — Whisper gives consistent quality/language support across all
// browsers instead of only Chrome/Edge, at the cost of needing a round trip
// to the backend (and an OpenAI key configured there). The mic button only
// renders where the browser can actually record audio (MediaRecorder +
// getUserMedia) rather than showing a dead control.
const canRecordAudio =
  typeof window !== 'undefined' && typeof window.MediaRecorder !== 'undefined' && !!navigator.mediaDevices?.getUserMedia

const MIC_ERROR_MESSAGES = {
  NotAllowedError: 'Microphone access was blocked. Please allow microphone permission and try again.',
  NotFoundError: 'No microphone was found on this device.',
}

export default function ChatInput() {
  const [text, setText] = useState('')
  const [isRecording, setIsRecording] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [micError, setMicError] = useState('')
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const { state } = useAppState()
  const { t, language } = useTranslation()
  const send = useSendMessage()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!text.trim() || state.chat.isAgentTyping) return
    send(text)
    setText('')
  }

  const stopRecording = () => {
    mediaRecorderRef.current?.stop()
  }

  const startRecording = async () => {
    setMicError('')
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data)
      }

      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop())
        setIsRecording(false)

        const blob = new Blob(chunksRef.current, { type: recorder.mimeType || 'audio/webm' })
        if (blob.size === 0) return

        setIsTranscribing(true)
        try {
          const transcript = await transcribeAudio(blob, language)
          if (transcript?.trim()) {
            setText((prev) => (prev ? `${prev} ${transcript.trim()}` : transcript.trim()))
          }
        } catch (err) {
          setMicError(err.message || 'Voice transcription failed.')
        } finally {
          setIsTranscribing(false)
        }
      }

      mediaRecorderRef.current = recorder
      recorder.start()
      setIsRecording(true)
    } catch (err) {
      setMicError(MIC_ERROR_MESSAGES[err.name] ?? 'Could not access the microphone. Please try again.')
    }
  }

  const toggleRecording = () => {
    if (!canRecordAudio || isTranscribing) return
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
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
        placeholder={isRecording ? t('listening') : isTranscribing ? t('transcribing') : t('chatPlaceholder')}
        className="max-h-32 flex-1 resize-none rounded-xl border border-earth-100 bg-wheat-50 px-3 py-2.5 text-sm text-stone-800 outline-none focus:border-leaf-400"
      />
      {canRecordAudio && (
        <button
          type="button"
          onClick={toggleRecording}
          disabled={isTranscribing}
          title={t('speak')}
          aria-label={t('speak')}
          className={clsx(
            'flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border text-lg transition-colors disabled:opacity-50',
            isRecording
              ? 'border-red-300 bg-red-50 text-red-600 animate-pulse'
              : 'border-earth-100 bg-wheat-50 text-stone-500 hover:bg-wheat-100',
          )}
        >
          {isTranscribing ? '⏳' : '🎤'}
        </button>
      )}
      <Button type="submit" disabled={!text.trim() || state.chat.isAgentTyping}>
        {t('send')}
      </Button>
      </div>
    </form>
  )
}
