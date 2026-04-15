import { ChatWindow } from '@/components/chat/chat-window'

export default function ChatPage() {
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Chat with Anna</h1>
        <p className="text-sm text-muted">
          Talk to your marketing crew in natural language.
        </p>
      </div>
      <ChatWindow />
    </div>
  )
}
