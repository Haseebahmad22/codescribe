import { useEffect, useMemo, useState } from 'react'
import { api, type Provider } from './lib/api'
import type { BatchStatus } from './lib/api'

const SectionTitle = ({ title, subtitle }: { title: string; subtitle?: string }) => (
  <div className="mb-4">
    <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
    {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
  </div>
)

export default function App() {
  const [provider, setProvider] = useState<Provider>('deepseek')
  const [model, setModel] = useState('deepseek-r1')
  const [apiBase] = useState<string>(import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000')
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState<'python' | 'javascript' | 'typescript'>('python')
  const [verbosity, setVerbosity] = useState<'low' | 'medium' | 'high'>('medium')
  const [style, setStyle] = useState<'google' | 'numpy' | 'sphinx' | 'jsdoc'>('google')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<string>('')

  const models = useMemo(() => {
    if (provider === 'openai') return ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo-preview']
    if (provider === 'huggingface') return ['microsoft/DialoGPT-medium', 'microsoft/CodeBERT-base']
    return ['deepseek-r1', 'deepseek-chat']
  }, [provider])

  useEffect(() => {
    setModel(models[0] || '')
  }, [provider])

  const [activeTab, setActiveTab] = useState<'code' | 'file' | 'batch'>('code')

  return (
    <div className="min-h-screen">
      {/* Top Bar */}
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

      {/* Layout */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Sidebar */}
        <aside className="lg:col-span-4 xl:col-span-3 space-y-6">
          <div className="rounded-xl border bg-white p-5 shadow-sm">
            <SectionTitle title="Provider" subtitle="Choose your AI backend" />
            <div className="grid grid-cols-3 gap-2">
              {(['deepseek', 'openai', 'huggingface'] as const).map((p) => (
                <button
                  key={p}
                  onClick={() => setProvider(p)}
                  className={`h-9 rounded-lg border text-sm capitalize transition ${
                    provider === p ? 'border-brand-600 bg-brand-50 text-brand-700' : 'hover:bg-gray-50'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
            <div className="mt-3">
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="h-9 w-full rounded-lg border bg-white px-3 text-sm"
              >
                {models.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="rounded-xl border bg-white p-5 shadow-sm">
            <SectionTitle title="Settings" subtitle="Documentation preferences" />
            <div className="grid grid-cols-2 gap-3">
              <select value={verbosity} onChange={(e) => setVerbosity(e.target.value as any)} className="h-9 rounded-lg border bg-white px-3 text-sm">
                <option value="low">low</option>
                <option value="medium">medium</option>
                <option value="high">high</option>
              </select>
              <select value={style} onChange={(e) => setStyle(e.target.value as any)} className="h-9 rounded-lg border bg-white px-3 text-sm">
                <option value="google">google</option>
                <option value="numpy">numpy</option>
                <option value="sphinx">sphinx</option>
                <option value="jsdoc">jsdoc</option>
              </select>
            </div>
            <div className="mt-3 grid grid-cols-3 gap-3">
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" defaultChecked /> Examples</label>
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" defaultChecked /> Params</label>
              <label className="flex items-center gap-2 text-sm"><input type="checkbox" defaultChecked /> Returns</label>
            </div>
          </div>

          <div className="rounded-xl border bg-white p-2 shadow-sm">
            <nav className="grid grid-cols-3 gap-2 p-1">
              {(['code', 'file', 'batch'] as const).map((t) => (
                <button
                  key={t}
                  onClick={() => setActiveTab(t)}
                  className={`h-9 rounded-lg text-sm capitalize border ${
                    activeTab === t ? 'bg-brand-600 text-white' : 'hover:bg-gray-50'
                  }`}
                >
                  {t}
                </button>
              ))}
            </nav>
          </div>
        </aside>

        {/* Main */}
        <main className="lg:col-span-8 xl:col-span-9 space-y-6">
          {activeTab === 'code' && (
            <div className="rounded-xl border bg-white p-5 shadow-sm">
              <SectionTitle title="Code" subtitle="Paste code to document" />
              <div className="grid gap-3">
                <div className="grid grid-cols-2 gap-3">
                  <select value={language} onChange={(e) => setLanguage(e.target.value as any)} className="h-10 rounded-lg border bg-white px-3 text-sm">
                    <option value="python">python</option>
                    <option value="javascript">javascript</option>
                    <option value="typescript">typescript</option>
                  </select>
                  <div />
                </div>
                <textarea value={code} onChange={(e) => setCode(e.target.value)} className="min-h-[220px] w-full rounded-lg border p-3 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" placeholder="// Paste your code here" />
              </div>
              <div className="mt-4 flex gap-3">
                <button
                  disabled={loading || !code.trim()}
                  onClick={async () => {
                    setLoading(true)
                    setError(null)
                    setResult('')
                    try {
                      const res = await api.documentCode({
                        code,
                        language,
                        verbosity,
                        style,
                        provider,
                        model,
                      })
                      if (!res.success) throw new Error(res.message)
                      setResult(res.documentation || '')
                    } catch (e: any) {
                      setError(e.message || 'Failed to generate documentation')
                    } finally {
                      setLoading(false)
                    }
                  }}
                  className="h-10 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
                >
                  {loading ? 'Generating…' : 'Generate'}
                </button>
                <button onClick={() => { setCode(''); setResult(''); setError(null) }} className="h-10 rounded-lg border px-4 text-sm">Clear</button>
              </div>
            </div>
          )}

          {activeTab === 'file' && (
            <div className="rounded-xl border bg-white p-5 shadow-sm space-y-4">
              <SectionTitle title="File Upload" subtitle="Upload a file to document" />
              <input id="single-file" type="file" className="block w-full text-sm" accept=".py,.js,.ts,.tsx,.jsx" />
              <div className="flex gap-3">
                <button
                  className="h-10 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
                  onClick={async () => {
                    const input = document.getElementById('single-file') as HTMLInputElement
                    const f = input?.files?.[0]
                    if (!f) return
                    setLoading(true); setError(null); setResult('')
                    try {
                      const resp = await api.documentFile(f, { provider, model, style, verbosity, output_format: 'markdown' })
                      if (resp instanceof Blob) {
                        const url = URL.createObjectURL(resp)
                        const a = document.createElement('a')
                        a.href = url; a.download = `${f.name.replace(/\.[^.]+$/, '')}_docs.md`
                        document.body.appendChild(a); a.click(); a.remove()
                        URL.revokeObjectURL(url)
                      } else if (resp && 'documentation' in resp) {
                        setResult(resp.documentation || '')
                      }
                    } catch (e: any) {
                      setError(e.message || 'File documentation failed')
                    } finally { setLoading(false) }
                  }}
                >Generate</button>
                <button className="h-10 rounded-lg border px-4 text-sm" onClick={() => setResult('')}>Clear</button>
              </div>
              {error && (<div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>)}
              {result && (
                <div className="rounded-lg border bg-gray-50 p-4 text-sm text-gray-700 whitespace-pre-wrap">{result}</div>
              )}
            </div>
          )}

          {activeTab === 'batch' && (
            <BatchPanel provider={provider} model={model} style={style} verbosity={verbosity} />
          )}

          <div className="rounded-xl border bg-white p-5 shadow-sm">
            <SectionTitle title="Results" subtitle="Generated documentation" />
            {error && (<div className="mb-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>)}
            <div className="rounded-lg border bg-gray-50 p-4 text-sm text-gray-700 min-h-[160px] whitespace-pre-wrap">
              {result ? result : <p className="text-gray-400">Documentation will appear here…</p>}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

function BatchPanel({ provider, model, style, verbosity }: { provider: Provider; model: string; style: any; verbosity: any }) {
  const [jobId, setJobId] = useState<string | null>(null)
  const [status, setStatus] = useState<BatchStatus | null>(null)
  const [polling, setPolling] = useState<number | null>(null)

  async function start() {
    const input = document.getElementById('batch-files') as HTMLInputElement
    const files = Array.from(input?.files || [])
    if (!files.length) return
    const resp = await api.startBatch(files, { provider, model, style, verbosity })
    setJobId(resp.job_id)
    if (polling) window.clearInterval(polling)
    const t = window.setInterval(async () => {
      if (!resp.job_id) return
      const s = await api.batchStatus(resp.job_id)
      setStatus(s)
      if (s.status === 'completed' || s.status === 'failed') {
        window.clearInterval(t)
      }
    }, 1500)
    setPolling(t)
  }

  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm space-y-4">
      <SectionTitle title="Batch Processing" subtitle="Upload multiple files and process asynchronously" />
      <input id="batch-files" type="file" multiple className="block w-full text-sm" accept=".py,.js,.ts,.tsx,.jsx" />
      <div className="flex gap-3">
        <button onClick={start} className="h-10 rounded-lg bg-brand-600 px-4 text-sm font-medium text-white hover:bg-brand-700">Start</button>
        {jobId && <div className="text-sm text-gray-600">Job: {jobId}</div>}
      </div>
      {status && (
        <div className="rounded-lg border bg-gray-50 p-4 text-sm">
          <div>Status: {status.status}</div>
          <div>Progress: {Math.round(status.progress ?? 0)}%</div>
          <div className="text-gray-500">{status.message}</div>
        </div>
      )}
    </div>
  )
}
