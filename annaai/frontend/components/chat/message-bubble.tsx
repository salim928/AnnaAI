import { clsx } from 'clsx'
import Image from 'next/image'

export function MessageBubble({
  role,
  content,
}: {
  role: 'user' | 'assistant'
  content: string
}) {
  const isUser = role === 'user'
  return (
    <div
      className={clsx(
        'flex items-start gap-3',
        isUser ? 'flex-row-reverse' : 'flex-row',
      )}
    >
      <div className="h-8 w-8 shrink-0 overflow-hidden rounded-full bg-bg">
        {isUser ? (
          <div className="flex h-full w-full items-center justify-center text-sm font-semibold">
            You
          </div>
        ) : (
          <Image src="/anna-avatar.svg" alt="Anna" width={32} height={32} />
        )}
      </div>
      <div
        className={clsx(
          'max-w-[75%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm',
          isUser
            ? 'bg-primary text-white'
            : 'bg-white border border-border',
        )}
      >
        {content || (
          <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-muted" />
        )}
      </div>
    </div>
  )
}
