import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble.jsx'
import TypingIndicator from './TypingIndicator.jsx'
import { useAppState } from '../../context/useAppState.js'

export default function MessageList() {
  const { state } = useAppState()
  const { messages, isAgentTyping } = state.chat
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, isAgentTyping])

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4">
      <div className="mx-auto flex max-w-2xl flex-col gap-3">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isAgentTyping && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
