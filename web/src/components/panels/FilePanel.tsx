import { Card, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'
import type { Provider } from '../../lib/api'
import { api } from '../../lib/api'
import { useState } from 'react'

export function FilePanel({ provider, model, style, verbosity, setResult, setError }: {
  provider: Provider; model: string; style: string; verbosity: string; setResult: (v: string)=>void; setError: (v: string | null)=>void;
}) {
  const [loading, setLoading] = useState(false)
  const [file, setFile] = useState<File | null>(null)

  async function handle() {
    if (!file) return
    setLoading(true); setError(null); setResult('')
    try {
      const resp = await api.documentFile(file, { provider, model, style, verbosity, output_format: 'markdown' })
      if (resp instanceof Blob) {
        const url = URL.createObjectURL(resp)
        const a = document.createElement('a')
        a.href = url; a.download = `${file.name.replace(/\.[^.]+$/, '')}_docs.md`
        document.body.appendChild(a); a.click(); a.remove()
        URL.revokeObjectURL(url)
      } else if (resp && 'documentation' in resp) {
        setResult(resp.documentation || '')
      }
    } catch (e: any) {
      setError(e.message || 'File documentation failed')
    } finally { setLoading(false) }
  }

  return (
    <Card>
      <CardTitle title="File Upload" subtitle="Upload a file to document" />
      <input type="file" onChange={(e)=> setFile(e.target.files?.[0] || null)} className="block w-full text-sm" accept=".py,.js,.ts,.tsx,.jsx" />
      <div className="mt-3 flex gap-3">
        <Button onClick={handle} disabled={!file} loading={loading}>Generate</Button>
        <Button variant="secondary" onClick={() => { setFile(null); setResult(''); setError(null) }}>Clear</Button>
      </div>
    </Card>
  )
}
