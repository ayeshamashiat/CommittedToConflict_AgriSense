import MessageList from './MessageList.jsx'
import ChatInput from './ChatInput.jsx'

export default function ChatPanel() {
  return (
    <div className="flex h-full flex-col overflow-hidden bg-wheat-100">
      <MessageList />
      <ChatInput />
    </div>
  )
}
