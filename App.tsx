import { useState } from 'react'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

type Finding = { title: string; severity: string; description: string; recommendation: string }
type Analysis = {
  mode: string; summary: string; safety_findings: Finding[]; crack_findings: Finding[]
  planning_advice: string[]; limitations: string[]; project: Record<string, unknown>
}
type EstimateItem = { material: string; quantity: number; unit: string; illustrative_rate_inr: number; estimated_cost_inr: number }
type Estimate = {
  built_area_sqft: number; items: EstimateItem[]; total_material_cost_inr: number; disclaimer: string
  budget_inr?: number; budget_usage_percent?: number; within_budget?: boolean; budget_note?: string
}
type Valuation = { area_sqft: number; base_rate_inr_per_sqft: number; condition: string; illustrative_value_inr: number; disclaimer: string }
type Phase = { phase: string; start_month: number; end_month: number; duration_months: number; key_checks: string[] }
type Plan = { total_duration_months: number; built_area_sqft: number; phases: Phase[]; disclaimer: string }

const inr = (n: number) => `₹${Number(n).toLocaleString('en-IN')}`
const errMsg = (err: unknown, fallback: string) =>
  axios.isAxiosError(err)
    ? (typeof err.response?.data?.detail === 'string'
        ? err.response.data.detail
        : err.response?.data?.detail
          ? 'Please check the values you entered.'
          : 'Could not reach the API. Ensure the FastAPI server is running.')
    : fallback

export default function App() {
  const [description, setDescription] = useState('')
  const [projectName, setProjectName] = useState('Sample Construction Project')
  const [location, setLocation] = useState('')
  const [buildingType, setBuildingType] = useState('Residential')
  const [area, setArea] = useState('1000')
  const [floors, setFloors] = useState('1')
  const [budget, setBudget] = useState('')
  const [stage, setStage] = useState('Under construction')
  const [rate, setRate] = useState('3500')
  const [age, setAge] = useState('2')
  const [condition, setCondition] = useState('Good')
  const [image, setImage] = useState<File | null>(null)
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [estimate, setEstimate] = useState<Estimate | null>(null)
  const [valuation, setValuation] = useState<Valuation | null>(null)
  const [plan, setPlan] = useState<Plan | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function runAnalysis(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); setError(''); setAnalysis(null)
    const form = new FormData()
    form.append('description', description)
    form.append('project_json', JSON.stringify({
      project_name: projectName, location: location || 'Not specified', building_type: buildingType,
      area_sqft: Number(area), floors: Number(floors), stage,
      ...(budget ? { budget_inr: Number(budget) } : {}),
    }))
    if (image) form.append('image', image)
    try {
      setAnalysis((await axios.post<Analysis>(`${API}/api/analyze`, form)).data)
    } catch (err) {
      setError(errMsg(err, 'Analysis request failed.'))
    } finally { setBusy(false) }
  }

  async function runEstimate() {
    setError('')
    try {
      setEstimate((await axios.post<Estimate>(`${API}/api/estimate`, {
        area_sqft: Number(area), floors: Number(floors), ...(budget ? { budget_inr: Number(budget) } : {}),
      })).data)
    } catch (err) { setError(errMsg(err, 'Estimate request failed.')) }
  }

  async function runValuation() {
    setError('')
    try {
      setValuation((await axios.post<Valuation>(`${API}/api/valuation`, {
        area_sqft: Number(area), rate_per_sqft: Number(rate), age_years: Number(age), condition,
      })).data)
    } catch (err) { setError(errMsg(err, 'Valuation request failed.')) }
  }

  async function runPlan() {
    setError('')
    try {
      setPlan((await axios.post<Plan>(`${API}/api/plan`, {
        area_sqft: Number(area), floors: Number(floors), building_type: buildingType,
      })).data)
    } catch (err) { setError(errMsg(err, 'Planning request failed.')) }
  }

  return <main className="shell">
    <header className="hero">
      <div className="eyebrow">SMART CONSTRUCTION • AI ASSISTANT</div>
      <h1>Build with better insight.</h1>
      <p>Review site images, surface safety questions, assess visible cracks, and explore planning estimates.</p>
      <div className="pills"><span>Image + text input</span><span>Safety screening</span><span>Planning, cost & valuation</span></div>
    </header>

    <section className="panel">
      <div className="section-head"><div><div className="eyebrow">01 / PROJECT INPUT</div><h2>Tell us about the site</h2></div><span className="tag">Analysis</span></div>
      <form onSubmit={runAnalysis}>
        <div className="grid">
          <label>Project name<input value={projectName} onChange={e => setProjectName(e.target.value)} required /></label>
          <label>Location<input value={location} onChange={e => setLocation(e.target.value)} placeholder="City, state" /></label>
          <label>Building type<select value={buildingType} onChange={e => setBuildingType(e.target.value)}><option>Residential</option><option>Commercial</option><option>Industrial</option><option>Infrastructure</option></select></label>
          <label>Construction stage<select value={stage} onChange={e => setStage(e.target.value)}><option>Planning</option><option>Foundation</option><option>Under construction</option><option>Finishing</option><option>Completed</option></select></label>
          <label>Area (sq ft)<input type="number" min="1" value={area} onChange={e => setArea(e.target.value)} required /></label>
          <label>Number of floors<input type="number" min="1" max="100" value={floors} onChange={e => setFloors(e.target.value)} required /></label>
          <label>Total budget (₹, optional)<input type="number" min="1" value={budget} onChange={e => setBudget(e.target.value)} placeholder="e.g. 2500000" /></label>
        </div>
        <label>Site description<textarea rows={4} value={description} onChange={e => setDescription(e.target.value)} placeholder="Describe visible conditions, work completed, concerns, materials, or schedule constraints..." /></label>
        <label className="upload"><span className="upload-icon">＋</span><span><strong>Upload site image</strong><small>JPEG, PNG or WEBP • max 10 MB</small></span><input type="file" accept="image/jpeg,image/png,image/webp" onChange={e => setImage(e.target.files?.[0] || null)} /></label>
        {image && <p className="file-name">Selected: {image.name}</p>}
        <button disabled={busy} type="submit">{busy ? 'Analyzing…' : 'Analyze project →'}</button>
      </form>
    </section>

    {error && <div className="error" role="alert">{error}</div>}

    {analysis && <section className="panel results">
      <div className="section-head"><div><div className="eyebrow">02 / ANALYSIS RESULTS</div><h2>Project review</h2></div><span className={`tag ${analysis.mode === 'gemini' ? 'live' : ''}`}>{analysis.mode === 'gemini' ? 'AI analysis' : 'Demo mode'}</span></div>
      <p className="summary">{analysis.summary}</p>
      <div className="result-grid">
        <ResultGroup title="Safety findings" items={analysis.safety_findings} />
        <ResultGroup title="Crack findings" items={analysis.crack_findings} />
      </div>
      <h3>Planning advice</h3><ul>{analysis.planning_advice.map((x, i) => <li key={i}>{x}</li>)}</ul>
      <h3>Limitations</h3><ul>{analysis.limitations.map((x, i) => <li key={i}>{x}</li>)}</ul>
    </section>}

    <section className="panel">
      <div className="section-head"><div><div className="eyebrow">03 / PROJECT PLANNING</div><h2>Schedule, estimate & valuation</h2></div></div>
      <p className="muted">Uses illustrative assumptions to demonstrate the workflow. Confirm quantities and rates locally.</p>
      <div className="grid val-inputs">
        <label>Valuation rate (₹/sq ft)<input type="number" min="1" value={rate} onChange={e => setRate(e.target.value)} /></label>
        <label>Building age (years)<input type="number" min="0" value={age} onChange={e => setAge(e.target.value)} /></label>
        <label>Condition<select value={condition} onChange={e => setCondition(e.target.value)}><option>Excellent</option><option>Good</option><option>Fair</option><option>Poor</option></select></label>
      </div>
      <div className="actions">
        <button type="button" onClick={runPlan}>Generate schedule</button>
        <button type="button" onClick={runEstimate}>Estimate materials</button>
        <button type="button" className="secondary" onClick={runValuation}>Estimate property value</button>
      </div>

      {plan && <div className="estimate"><h3>Indicative schedule</h3>
        <p className="big-number">{plan.total_duration_months} months</p>
        <p className="muted">For {plan.built_area_sqft} sq ft built area</p>
        <ol className="phases">{plan.phases.map(p => <li key={p.phase}>
          <div className="phase-head"><strong>{p.phase}</strong><span className="tag">Month {p.start_month} – {p.end_month}</span></div>
          <div className="bar"><span style={{ width: `${Math.min(100, (p.duration_months / plan.total_duration_months) * 100)}%` }} /></div>
          <small>{p.key_checks.join(' • ')}</small>
        </li>)}</ol>
        <small>{plan.disclaimer}</small></div>}

      {estimate && <div className="estimate"><h3>Material estimate</h3>
        <p className="big-number">{inr(estimate.total_material_cost_inr)}</p>
        <p className="muted">Illustrative material cost for {estimate.built_area_sqft} sq ft built area</p>
        {estimate.budget_inr !== undefined && <p className={`budget ${estimate.within_budget ? 'ok' : 'over'}`}>
          {estimate.budget_usage_percent}% of your {inr(estimate.budget_inr)} budget · {estimate.within_budget ? 'materials fit within budget' : 'materials alone exceed budget'}
          <small> {estimate.budget_note}</small></p>}
        <div className="table-wrap"><table><thead><tr><th>Material</th><th>Quantity</th><th>Rate</th><th>Cost</th></tr></thead><tbody>
          {estimate.items.map(x => <tr key={x.material}><td>{x.material}</td><td>{x.quantity} {x.unit}</td><td>₹{x.illustrative_rate_inr}</td><td>{inr(x.estimated_cost_inr)}</td></tr>)}
        </tbody></table></div>
        <small>{estimate.disclaimer}</small></div>}

      {valuation && <div className="estimate"><h3>Property valuation</h3>
        <p className="big-number">{inr(valuation.illustrative_value_inr)}</p>
        <p className="muted">{valuation.area_sqft} sq ft · base rate ₹{valuation.base_rate_inr_per_sqft}/sq ft · {valuation.condition} condition</p>
        <small>{valuation.disclaimer}</small></div>}
    </section>
    <footer>Construction AI Assistant · Educational prototype · Not a substitute for qualified professional review.</footer>
  </main>
}

function ResultGroup({ title, items }: { title: string; items: Finding[] }) {
  return <div className="finding-group"><h3>{title}</h3>{items.length
    ? items.map((f, i) => <article className="finding" key={i}>
        <div className="finding-title"><strong>{f.title}</strong><span className={`severity ${f.severity.toLowerCase()}`}>{f.severity}</span></div>
        <p>{f.description}</p><p><b>Recommended action:</b> {f.recommendation}</p></article>)
    : <p className="muted">No findings returned. This does not mean the site is safe.</p>}</div>
}
