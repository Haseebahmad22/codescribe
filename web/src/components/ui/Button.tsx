import type { ButtonHTMLAttributes, PropsWithChildren } from 'react'

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
}

export function Button({
  variant = 'primary',
  size = 'md',
  className = '',
  children,
  ...props
}: PropsWithChildren<ButtonProps>) {
  const { loading = false, disabled, ...rest } = props
  const base = 'inline-flex items-center justify-center rounded-lg font-medium transition disabled:opacity-50 disabled:cursor-not-allowed'
  const sizes = {
    sm: 'h-8 px-3 text-xs',
    md: 'h-10 px-4 text-sm',
    lg: 'h-11 px-5 text-base',
  }[size]
  const variants = {
    primary: 'bg-brand-600 text-white hover:bg-brand-700',
    secondary: 'border bg-white hover:bg-gray-50',
    ghost: 'hover:bg-gray-50',
  }[variant]
  return (
    <button className={`${base} ${sizes} ${variants} ${className}`} disabled={loading || disabled} {...rest}>
      {loading && (
        <svg className="-ml-0.5 mr-2 h-4 w-4 animate-spin" viewBox="0 0 24 24" aria-hidden="true">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
        </svg>
      )}
      {children}
    </button>
  )
}
