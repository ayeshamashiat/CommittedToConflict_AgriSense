import { useState } from 'react'
import Button from '../../components/ui/Button.jsx'
import { useAppState } from '../../context/useAppState.js'
import { useSendMessage } from './useSendMessage.js'

export default function ChatInput() {
  const [text, setText] = useState('')
  const { state } = useAppState()
  const send = useSendMessage()

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!text.trim() || state.chat.isAgentTyping) return
    send(text)
    setText('')
  }

  return (
    <form onSubmit={handleSubmit} className="flex shrink-0 items-end gap-2 border-t border-earth-100 p-3">
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
        placeholder="Tell the agent about your farm..."
        className="max-h-32 flex-1 resize-none rounded-xl border border-earth-100 bg-wheat-50 px-3 py-2.5 text-sm text-stone-800 outline-none focus:border-leaf-400"
      />
      <Button type="submit" disabled={!text.trim() || state.chat.isAgentTyping}>
        Send
      </Button>
    </form>
  )
}
