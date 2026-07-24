import clsx from 'clsx'
import { formatTime } from '../../lib/formatters.js'

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <div className={clsx('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={clsx(
          'max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm',
          isUser
            ? 'rounded-br-sm bg-leaf-600 text-wheat-50'
            : 'rounded-bl-sm border border-earth-100 bg-wheat-50 text-stone-800',
        )}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        <p className={clsx('mt-1 text-[10px]', isUser ? 'text-leaf-100' : 'text-stone-400')}>
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  )
}
