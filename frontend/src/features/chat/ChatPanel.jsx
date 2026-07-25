import MessageList from './MessageList.jsx'
import ChatInput from './ChatInput.jsx'
import ChatSidebar from './ChatSidebar.jsx'

export default function ChatPanel() {
  return (
    <div className="flex h-full overflow-hidden bg-wheat-100">
      <ChatSidebar />
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <MessageList />
        <ChatInput />
      </div>
    </div>
  )
}
