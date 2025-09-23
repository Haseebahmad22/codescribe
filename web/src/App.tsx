import { useEffect, useMemo, useState } from 'react'
import { api, type Provider } from './lib/api'
import { Header } from './components/layout/Header'
import { ProviderPanel } from './components/panels/ProviderPanel'
import { SettingsPanel } from './components/panels/SettingsPanel'
import { CodePanel } from './components/panels/CodePanel'
import { FilePanel } from './components/panels/FilePanel'
import { BatchPanel } from './components/panels/BatchPanel'
import { ResultsPanel } from './components/panels/ResultsPanel'

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
      <Header apiBase={apiBase} />

      {/* Layout */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Sidebar */}
        <aside className="lg:col-span-4 xl:col-span-3 space-y-6">
          <ProviderPanel provider={provider} setProvider={setProvider} model={model} setModel={setModel} models={models} />
          <SettingsPanel verbosity={verbosity} setVerbosity={setVerbosity} style={style} setStyle={setStyle} />

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
            <CodePanel
              code={code}
              setCode={setCode}
              loading={loading}
              language={language}
              setLanguage={setLanguage}
              onSubmit={async () => {
                setLoading(true)
                setError(null)
                setResult('')
                try {
                  const res = await api.documentCode({ code, language, verbosity, style, provider, model })
                  if (!res.success) throw new Error(res.message)
                  setResult(res.documentation || '')
                } catch (e: any) {
                  setError(e.message || 'Failed to generate documentation')
                } finally {
                  setLoading(false)
                }
              }}
            />
          )}

          {activeTab === 'file' && (
            <FilePanel provider={provider} model={model} style={style} verbosity={verbosity} setResult={setResult} setError={setError} />
          )}

          {activeTab === 'batch' && <BatchPanel provider={provider} model={model} style={style} verbosity={verbosity} />}

          <ResultsPanel result={result} error={error} />
        </main>
      </div>
    </div>
  )
}
 
