import { Card, CardTitle } from '../ui/Card'

export function SettingsPanel({ verbosity, setVerbosity, style, setStyle }: {
  verbosity: 'low' | 'medium' | 'high';
  setVerbosity: (v: 'low' | 'medium' | 'high') => void;
  style: 'google' | 'numpy' | 'sphinx' | 'jsdoc';
  setStyle: (s: 'google' | 'numpy' | 'sphinx' | 'jsdoc') => void;
}) {
  return (
    <Card>
      <CardTitle title="Settings" subtitle="Documentation preferences" />
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
    </Card>
  )
}
