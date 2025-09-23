import { Card, CardTitle } from '../ui/Card'
import { Button } from '../ui/Button'

export function CodePanel({ code, setCode, onSubmit, loading, language, setLanguage }: {
  code: string; setCode: (v: string) => void; onSubmit: ()=>void; loading: boolean; language: 'python'|'javascript'|'typescript'; setLanguage: (l: 'python'|'javascript'|'typescript')=>void
}) {
  return (
    <Card>
      <CardTitle title="Code" subtitle="Paste code to document" />
      <div className="grid grid-cols-2 gap-3 mb-3">
        <select value={language} onChange={(e)=> setLanguage(e.target.value as any)} className="h-10 rounded-lg border bg-white px-3 text-sm">
          <option value="python">python</option>
          <option value="javascript">javascript</option>
          <option value="typescript">typescript</option>
        </select>
        <div />
      </div>
      <textarea value={code} onChange={(e)=> setCode(e.target.value)} placeholder="Paste your code here..." className="h-56 w-full resize-y rounded-lg border px-3 py-2 font-mono text-sm" />
      <div className="mt-3 flex justify-end">
        <Button onClick={onSubmit} disabled={!code.trim() || loading} loading={loading}>
          {loading? 'Generating...' : 'Generate Documentation'}
        </Button>
      </div>
    </Card>
  )
}
