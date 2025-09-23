export function Header({ apiBase }: { apiBase: string }) {
  return (
    <header className="sticky top-0 z-10 border-b bg-white/70 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-brand-600 text-white grid place-items-center font-bold">C</div>
          <div>
            <div className="text-sm font-semibold text-gray-900">CodeScribe</div>
            <div className="text-xs text-gray-500">AI Code Documentation</div>
          </div>
        </div>
        <div className="text-xs text-gray-500">API: {apiBase}</div>
      </div>
    </header>
  )
}
