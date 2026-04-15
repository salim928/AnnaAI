import { clsx } from 'clsx'

export function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={clsx(
        'inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent',
        className,
      )}
      aria-label="Loading"
    />
  )
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={clsx('shimmer rounded-md', className)} />
}
