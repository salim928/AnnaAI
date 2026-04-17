import { clsx } from 'clsx'
import type { InputHTMLAttributes, TextareaHTMLAttributes } from 'react'

export function Input({
  className,
  ...rest
}: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...rest}
      className={clsx(
        'w-full rounded-lg border border-border bg-white px-3 py-2.5 text-base outline-none transition focus:border-primary md:py-2 md:text-sm',
        className,
      )}
    />
  )
}

export function Textarea({
  className,
  ...rest
}: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      {...rest}
      className={clsx(
        'w-full rounded-lg border border-border bg-white px-3 py-2.5 text-base outline-none transition focus:border-primary md:py-2 md:text-sm',
        className,
      )}
    />
  )
}

export function Label({
  htmlFor,
  children,
}: {
  htmlFor?: string
  children: React.ReactNode
}) {
  return (
    <label
      htmlFor={htmlFor}
      className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted"
    >
      {children}
    </label>
  )
}
