import type { PropsWithChildren, HTMLAttributes } from 'react'

export function Card({ className = '', children, ...props }: PropsWithChildren<HTMLAttributes<HTMLDivElement>>) {
  return (
    <div className={`rounded-xl border bg-white p-5 shadow-sm ${className}`} {...props}>
      {children}
    </div>
  )
}

export function CardTitle({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-4">
      <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
      {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
    </div>
  )
}
