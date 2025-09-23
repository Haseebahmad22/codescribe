import { Card, CardTitle } from '../ui/Card'

export function ResultsPanel({ result, error }: { result: string; error: string | null }) {
  return (
    <Card>
      <CardTitle title="Results" subtitle="Generated documentation" />
      {error && (
        <div className="mb-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>
      )}
      <div className="rounded-lg border bg-gray-50 p-4 text-sm text-gray-700 min-h-[160px] whitespace-pre-wrap">
        {result ? result : <p className="text-gray-400">Documentation will appear here…</p>}
      </div>
    </Card>
  )
}
