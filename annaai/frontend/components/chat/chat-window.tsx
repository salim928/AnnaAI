'use client'

import { useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'
import { MessageBubble } from './message-bubble'
import { ChatInput } from './chat-input'
import { api } from '@/lib/api'

interface Msg {
  role: 'user' | 'assistant'
  content: string
}

export function ChatWindow() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: 'assistant',
      content:
        "Hi, I'm Anna. Ask me about your content strategy, analytics, or what I should work on next.",
    },
  ])
  const [streaming, setStreaming] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: 'smooth',
    })
  }, [messages])

  async function handleSend(text: string) {
    const history = messages.map((m) => ({ role: m.role, content: m.content }))
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: text },
      { role: 'assistant', content: '' },
    ])
    setStreaming(true)

    try {
      await api.streamChat(text, history, (delta) => {
        setMessages((prev) => {
          const next = [...prev]
          const last = next[next.length - 1]
          if (last && last.role === 'assistant') {
            next[next.length - 1] = {
              role: 'assistant',
              content: last.content + delta,
            }
          }
          return next
        })
      })
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Chat failed')
      setMessages((prev) => prev.slice(0, -1))
    } finally {
      setStreaming(false)
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col overflow-hidden rounded-xl border border-border bg-bg">
      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-6">
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} content={m.content} />
        ))}
      </div>
      <ChatInput onSend={handleSend} disabled={streaming} />
    </div>
  )
}
