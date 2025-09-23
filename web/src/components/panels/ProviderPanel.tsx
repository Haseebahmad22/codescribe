import { Card, CardTitle } from '../ui/Card'
import type { Provider } from '../../lib/api'

export function ProviderPanel({ provider, setProvider, model, setModel, models }: {
  provider: Provider; setProvider: (p: Provider) => void; model: string; setModel: (m: string) => void; models: string[]
}) {
  return (
    <Card>
      <CardTitle title="Provider" subtitle="Choose your AI backend" />
      <div className="grid grid-cols-3 gap-2">
        {(['deepseek','openai','huggingface'] as const).map(p => (
          <button key={p} onClick={() => setProvider(p)} className={`h-9 rounded-lg border text-sm capitalize transition ${provider===p? 'border-brand-600 bg-brand-50 text-brand-700':'hover:bg-gray-50'}`}>{p}</button>
        ))}
      </div>
      <div className="mt-3">
        <select value={model} onChange={(e) => setModel(e.target.value)} className="h-9 w-full rounded-lg border bg-white px-3 text-sm">
          {models.map(m => <option key={m} value={m}>{m}</option>)}
        </select>
      </div>
    </Card>
  )
}
