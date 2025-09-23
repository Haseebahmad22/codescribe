import { useState } from 'react'
import type { Provider, BatchStatus } from '../../lib/api'
import { api } from '../../lib/api'
import { Card, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'

export function BatchPanel({ provider, model, style, verbosity }: { provider: Provider; model: string; style: any; verbosity: any }) {
  const [jobId, setJobId] = useState<string | null>(null)
  const [status, setStatus] = useState<BatchStatus | null>(null)
  const [polling, setPolling] = useState<number | null>(null)
  const [files, setFiles] = useState<File[]>([])
  const [loading, setLoading] = useState(false)

  async function start() {
    if (!files.length) return
    setLoading(true)
    try {
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
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardTitle title="Batch Processing" subtitle="Upload multiple files and process asynchronously" />
      <input type="file" multiple onChange={(e)=> setFiles(Array.from(e.target.files || []))} className="block w-full text-sm" accept=".py,.js,.ts,.tsx,.jsx" />
      <div className="mt-3 flex gap-3 items-center">
        <Button onClick={start} disabled={!files.length} loading={loading}>Start</Button>
        {jobId && <div className="text-sm text-gray-600">Job: {jobId}</div>}
      </div>
      {status && (
        <div className="mt-3 rounded-lg border bg-gray-50 p-4 text-sm">
          <div>Status: {status.status}</div>
          <div>Progress: {Math.round(status.progress ?? 0)}%</div>
          <div className="text-gray-500">{status.message}</div>
        </div>
      )}
    </Card>
  )
}
