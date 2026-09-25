import React, { useState } from 'react'
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'
import axios from 'axios'
import LandIntelligenceMap from './components/Map/LandIntelligenceMap'

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30000, retry: 1 } }
})

// ─── Inline SVG icons ────────────────────────────────────
const Icons = {
  Dashboard: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/>
      <rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/>
    </svg>
  ),
  Map: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/>
      <line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/>
    </svg>
  ),
  Alert: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
      <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  ),
  Doc: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/>
      <polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
    </svg>
  ),
  Bot: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/>
      <path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>
    </svg>
  ),
  Shield: () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/>
      <path d="m9 12 2 2 4-4"/>
    </svg>
  ),
  Send: () => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
    </svg>
  ),
  Upload: () => (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
      <polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
    </svg>
  ),
  ChevronRight: () => (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="9 18 15 12 9 6"/>
    </svg>
  ),
}

// ─── Severity badge ──────────────────────────────────────
function SeverityBadge({ level }: { level: string }) {
  const styles: Record<string, string> = {
    CRITICAL: 'bg-red-50 text-red-600 border-red-200',
    HIGH:     'bg-orange-50 text-orange-600 border-orange-200',
    MEDIUM:   'bg-amber-50 text-amber-600 border-amber-200',
    LOW:      'bg-green-50 text-green-600 border-green-200',
    INFO:     'bg-sky-50 text-sky-600 border-sky-200',
  }
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold border ${styles[level] || styles.INFO}`}>
      {level}
    </span>
  )
}

// ─── Stat Card ───────────────────────────────────────────
function StatCard({ label, value, sub, color }: {
  label: string; value: string | number; sub?: string; color?: string
}) {
  return (
    <div className="stat-card">
      <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-3">{label}</p>
      <p className={`text-3xl font-bold tracking-tight ${color || 'text-slate-800'}`}>{value}</p>
      {sub && <p className="text-xs text-slate-400 mt-1.5">{sub}</p>}
    </div>
  )
}

// ─── Progress bar ────────────────────────────────────────
function ProgressRow({ label, value, total, color }: {
  label: string; value: number; total: number; color: string
}) {
  const pct = total > 0 ? (value / total) * 100 : 0
  return (
    <div>
      <div className="flex justify-between text-xs mb-1.5">
        <span className="font-medium text-slate-700">{label}</span>
        <span className="text-slate-400">{value} <span className="text-slate-300">/ {total}</span></span>
      </div>
      <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

// ─── Section heading ─────────────────────────────────────
function SectionHeading({ title, sub }: { title: string; sub?: string }) {
  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold text-slate-800 tracking-tight">{title}</h2>
      {sub && <p className="text-sm text-slate-400 mt-0.5">{sub}</p>}
    </div>
  )
}

// ─── Panel ───────────────────────────────────────────────
function Panel({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white border border-slate-200 rounded-2xl ${className}`}>
      {children}
    </div>
  )
}

// ─── DASHBOARD ───────────────────────────────────────────
function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: () => axios.get('/api/dashboard/summary').then(r => r.data),
  })

  if (isLoading || !data) return <PageLoader label="Loading dashboard data..." />

  const riskData   = data.risk_distribution   || {}
  const landData   = data.land_type_distribution || {}
  const riskTotal  = Object.values(riskData).reduce((a: number, b) => a + (b as number), 0) as number
  const landTotal  = Object.values(landData).reduce((a: number, b) => a + (b as number), 0) as number

  const riskColors: Record<string, string> = {
    CRITICAL: 'bg-red-500', HIGH: 'bg-orange-400', MEDIUM: 'bg-amber-400', LOW: 'bg-emerald-500'
  }
  const landColors: Record<string, string> = {
    Agricultural: 'bg-emerald-500', Residential: 'bg-sky-500',
    Commercial: 'bg-violet-500', Government: 'bg-amber-500'
  }

  return (
    <div className="p-7 space-y-7 overflow-auto h-full animate-fade-in">
      <SectionHeading
        title="Intelligence Dashboard"
        sub="Real-time overview of land governance across all districts"
      />

      {/* KPI Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 stagger-children">
        <StatCard label="Total Parcels"    value={data.parcels.total}         sub={`${data.parcels.total_area_hectares} ha`} />
        <StatCard label="Verified"         value={data.parcels.verified}      sub={`${((data.parcels.verified / Math.max(data.parcels.total, 1)) * 100).toFixed(1)}% of total`} color="text-emerald-600" />
        <StatCard label="Conflicts"        value={data.parcels.conflict}      color="text-orange-500" />
        <StatCard label="Critical Risk"    value={data.parcels.critical_risk} color="text-red-500" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 stagger-children">
        <StatCard label="Total Anomalies"        value={data.anomalies.total}       sub={`${data.anomalies.critical} critical`} color="text-amber-600" />
        <StatCard label="Documents Processed"    value={data.documents.processed}   sub={`of ${data.documents.total} total`} color="text-sky-600" />
        <StatCard label="Pending Verification"   value={data.parcels.pending}       color="text-slate-500" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Panel className="p-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-5">Risk Distribution</h3>
          <div className="space-y-4">
            {Object.entries(riskData).map(([level, count]) => (
              <ProgressRow
                key={level}
                label={level}
                value={count as number}
                total={riskTotal}
                color={riskColors[level] || 'bg-slate-400'}
              />
            ))}
          </div>
        </Panel>

        <Panel className="p-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-5">Land Type Distribution</h3>
          <div className="space-y-4">
            {Object.entries(landData).map(([type, count]) => (
              <ProgressRow
                key={type}
                label={type}
                value={count as number}
                total={landTotal}
                color={landColors[type] || 'bg-slate-400'}
              />
            ))}
          </div>
        </Panel>
      </div>

      {/* Recent Anomalies */}
      <Panel>
        <div className="px-6 py-4 border-b border-slate-100">
          <h3 className="text-sm font-semibold text-slate-700">Recent Anomalies</h3>
        </div>
        <div className="divide-y divide-slate-50">
          {(data.recent_anomalies || []).map((a: any) => (
            <div key={a.id} className="flex items-center gap-4 px-6 py-3 hover:bg-slate-50 transition-colors">
              <SeverityBadge level={a.severity} />
              <span className="font-mono text-xs text-orange-500 shrink-0">{a.survey_number}</span>
              <span className="text-sm text-slate-600 flex-1 truncate">{a.message}</span>
              <span className="text-xs text-slate-400 whitespace-nowrap">{a.detected_at?.split('T')[0]}</span>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  )
}

// ─── MAP PAGE ────────────────────────────────────────────
function MapPage() {
  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="px-6 py-4 border-b border-slate-200 bg-white flex justify-between items-center shrink-0">
        <div>
          <h2 className="text-base font-bold text-slate-800">Spatial Intelligence</h2>
          <p className="text-xs text-slate-400 mt-0.5">GIS-powered land parcel visualisation</p>
        </div>
        <div className="flex items-center gap-5 text-xs text-slate-500">
          {[['bg-red-500','Critical'],['bg-orange-400','High'],['bg-amber-400','Medium'],['bg-emerald-500','Low']].map(([c,l]) => (
            <span key={l} className="flex items-center gap-1.5">
              <span className={`w-2.5 h-2.5 rounded-full ${c}`} />
              {l}
            </span>
          ))}
        </div>
      </div>
      <div className="flex-1"><LandIntelligenceMap /></div>
    </div>
  )
}

// ─── ANOMALIES PAGE ──────────────────────────────────────
function AnomaliesPage() {
  const [filter, setFilter] = useState<string>('')
  const { data, isLoading } = useQuery({
    queryKey: ['anomalies', filter],
    queryFn: () => axios.get(`/api/anomalies${filter ? `?severity=${filter}` : ''}`).then(r => r.data),
  })

  if (isLoading) return <PageLoader label="Scanning anomaly records..." />

  const filters = ['', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW']

  return (
    <div className="p-7 space-y-6 h-full overflow-auto animate-fade-in">
      <div className="flex justify-between items-start flex-wrap gap-4">
        <SectionHeading title="Risk & Anomaly Intelligence" sub="AI-detected irregularities in land records" />
        <div className="flex gap-2 flex-wrap">
          {filters.map(s => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all ${
                filter === s
                  ? 'bg-orange-500 text-white border-orange-500'
                  : 'bg-white text-slate-600 border-slate-200 hover:border-orange-300'
              }`}
            >
              {s || 'All'}
            </button>
          ))}
        </div>
      </div>

      <Panel className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 bg-slate-50">
                {['Severity','Survey #','Location','Rule','Description','Confidence','Detected'].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {(data || []).map((a: any) => (
                <tr key={a.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-4 py-3"><SeverityBadge level={a.severity} /></td>
                  <td className="px-4 py-3 font-mono text-xs text-orange-500">{a.survey_number}</td>
                  <td className="px-4 py-3 text-xs text-slate-600">{a.village}, {a.district}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">{a.rule_id}</td>
                  <td className="px-4 py-3 text-xs text-slate-600 max-w-xs truncate">{a.message}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-14 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-orange-400 rounded-full"
                          style={{ width: `${(a.confidence || 0) * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-slate-400">{((a.confidence || 0) * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">{a.detected_at?.split('T')[0]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {(!data || data.length === 0) && (
          <div className="text-center py-14 text-slate-400 text-sm">No anomalies found for this filter.</div>
        )}
      </Panel>
    </div>
  )
}

// ─── DOCUMENTS PAGE ──────────────────────────────────────
function DocumentsPage() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['documents'],
    queryFn: () => axios.get('/api/documents').then(r => r.data),
  })
  const [uploading, setUploading] = useState(false)

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return
    setUploading(true)
    const form = new FormData()
    form.append('file', e.target.files[0])
    try { await axios.post('/api/documents/upload', form); refetch() }
    catch (err) { console.error(err) }
    setUploading(false)
  }

  if (isLoading) return <PageLoader label="Loading document intelligence..." />

  const statusStyle: Record<string, string> = {
    PROCESSED: 'bg-green-50 text-green-600 border-green-200',
    PENDING:   'bg-amber-50 text-amber-600 border-amber-200',
    FAILED:    'bg-red-50 text-red-600 border-red-200',
  }

  return (
    <div className="p-7 space-y-6 h-full overflow-auto animate-fade-in">
      <div className="flex justify-between items-start flex-wrap gap-4">
        <SectionHeading title="Document Intelligence" sub="OCR processing pipeline & entity extraction" />
        <label className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg cursor-pointer hover:bg-orange-600 transition-colors text-sm font-semibold shadow-sm shadow-orange-200">
          <Icons.Upload />
          {uploading ? 'Processing...' : 'Upload Document'}
          <input type="file" className="hidden" onChange={handleUpload} accept=".pdf,.jpg,.jpeg,.png" />
        </label>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {(data || []).map((doc: any) => (
          <Panel key={doc.id} className="p-5 hover:shadow-sm transition-shadow flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-orange-50 flex items-center justify-center text-orange-500 shrink-0">
              <Icons.Doc />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 flex-wrap">
                <span className="font-semibold text-sm text-slate-800 truncate">{doc.filename}</span>
                <span className={`text-xs px-2 py-0.5 rounded-md border font-medium ${statusStyle[doc.processed_status] || statusStyle.FAILED}`}>
                  {doc.processed_status}
                </span>
              </div>
              <div className="flex items-center gap-4 mt-1.5 text-xs text-slate-400 flex-wrap">
                <span>Type: {doc.document_type}</span>
                {doc.ocr_confidence && <span>OCR: {(doc.ocr_confidence * 100).toFixed(1)}%</span>}
                <span>{doc.upload_date?.split('T')[0]}</span>
              </div>
              {doc.extracted_entities && (
                <div className="mt-2.5 text-xs bg-slate-50 border border-slate-100 rounded-lg p-2.5 font-mono text-slate-500">
                  {JSON.stringify(doc.extracted_entities?.extracted_fields || doc.extracted_entities, null, 0).slice(0, 200)}
                </div>
              )}
            </div>
          </Panel>
        ))}
        {(!data || data.length === 0) && (
          <div className="text-center py-16 text-slate-400">
            <div className="flex justify-center mb-3 text-slate-300"><Icons.Doc /></div>
            <p className="text-sm">No documents uploaded yet. Upload a document to start OCR processing.</p>
          </div>
        )}
      </div>
    </div>
  )
}

// ─── AI ASSISTANT PAGE ───────────────────────────────────
function AIAssistantPage() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<Array<{ role: string; content: string; sources?: any[] }>>([
    { role: 'assistant', content: '🏛️ **Bhu-Intel AI Assistant**\n\nI can help you with land governance queries. Ask me about:\n- Land ceiling regulations\n- Mutation processes\n- Encumbrance certificates\n- Benami transactions\n- Stamp duty & registration\n- Anomaly detection rules\n\nType your question below.' }
  ])
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!query.trim() || loading) return
    const userMsg = query.trim()
    setQuery('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setLoading(true)
    try {
      const res = await axios.post('/api/ai/query', { query: userMsg })
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.answer, sources: res.data.sources }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error processing your query.' }])
    }
    setLoading(false)
  }

  return (
    <div className="h-full flex flex-col animate-fade-in">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-200 bg-white shrink-0">
        <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
          <span className="text-orange-500"><Icons.Bot /></span>
          Bhu-Intel AI Assistant
        </h2>
        <p className="text-xs text-slate-400 mt-0.5">RAG-powered policy intelligence & land governance advisor</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-6 space-y-4 bg-slate-50">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-2xl rounded-2xl px-5 py-3.5 text-sm leading-relaxed ${
              msg.role === 'user'
                ? 'bg-orange-500 text-white rounded-br-md shadow-sm shadow-orange-200'
                : 'bg-white border border-slate-200 text-slate-700 rounded-bl-md shadow-sm'
            }`}>
              <div className="whitespace-pre-wrap">{msg.content}</div>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-2.5 border-t border-slate-100">
                  <span className="text-xs font-semibold text-slate-400">Sources:</span>
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {msg.sources.map((s: any) => (
                      <span key={s.id} className="text-xs px-2 py-0.5 bg-orange-50 text-orange-600 border border-orange-200 rounded-full">
                        {s.title}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 rounded-2xl rounded-bl-md px-5 py-3.5 text-sm shadow-sm">
              <div className="flex items-center gap-1.5 text-slate-400">
                {[0, 150, 300].map(d => (
                  <div key={d} className="w-2 h-2 bg-orange-400 rounded-full animate-bounce" style={{ animationDelay: `${d}ms` }} />
                ))}
                <span className="ml-2 text-xs">Analysing policy documents…</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-slate-200 bg-white shrink-0">
        <div className="flex gap-3 max-w-3xl mx-auto">
          <input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Ask about land governance, policies, or specific parcels…"
            className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-orange-300 focus:border-orange-400 transition-all placeholder:text-slate-300"
          />
          <button
            onClick={handleSend}
            disabled={loading || !query.trim()}
            className="px-5 py-3 bg-orange-500 text-white rounded-xl hover:bg-orange-600 transition-colors disabled:opacity-40 flex items-center gap-2 text-sm font-semibold shadow-sm shadow-orange-200"
          >
            <Icons.Send /> Send
          </button>
        </div>
      </div>
    </div>
  )
}

// ─── AUDIT PAGE ──────────────────────────────────────────
function AuditPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['audit-events'],
    queryFn: () => axios.get('/api/audit').then(r => r.data),
  })

  if (isLoading) return <PageLoader label="Loading cryptographic audit ledger…" />

  return (
    <div className="p-7 space-y-6 h-full overflow-auto animate-fade-in">
      <SectionHeading
        title="Cryptographic Audit Ledger"
        sub="Tamper-proof blockchain-style trail with SHA-256 chain verification"
      />

      <div className="space-y-3">
        {(data || []).map((event: any, idx: number) => (
          <Panel key={event.id} className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className="w-9 h-9 rounded-xl bg-slate-100 flex items-center justify-center text-slate-500 text-xs font-bold shrink-0">
                  #{(data?.length || 0) - idx}
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-sm text-slate-800">{event.event_type}</span>
                    <span className="text-xs px-2 py-0.5 rounded-md bg-sky-50 text-sky-600 border border-sky-200 font-medium">
                      {event.action}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    Actor: <span className="text-slate-600">{event.actor}</span>
                    {' · '}Record: <span className="text-slate-600">{event.record_id}</span>
                  </div>
                </div>
              </div>
              <span className="text-xs text-slate-400 whitespace-nowrap shrink-0">{event.timestamp?.split('T')[0]}</span>
            </div>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-2 font-mono text-xs">
              <div className="bg-slate-50 border border-slate-100 rounded-lg p-3">
                <span className="text-slate-400">Current Hash: </span>
                <span className="text-emerald-600 break-all">{event.current_hash?.slice(0, 32)}…</span>
              </div>
              <div className="bg-slate-50 border border-slate-100 rounded-lg p-3">
                <span className="text-slate-400">Previous: </span>
                <span className="text-amber-500 break-all">
                  {event.previous_hash ? event.previous_hash.slice(0, 32) + '…' : 'GENESIS'}
                </span>
              </div>
            </div>
          </Panel>
        ))}
        {(!data || data.length === 0) && (
          <div className="text-center py-16 text-slate-400 text-sm">No audit events recorded yet.</div>
        )}
      </div>
    </div>
  )
}

// ─── Page Loader ─────────────────────────────────────────
function PageLoader({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-4">
      <div className="relative w-10 h-10">
        <div className="absolute inset-0 border-[3px] border-slate-100 rounded-full" />
        <div className="absolute inset-0 border-[3px] border-transparent border-t-orange-500 rounded-full animate-spin" />
      </div>
      <span className="text-sm text-slate-400">{label}</span>
    </div>
  )
}

// ─── MAIN APP ────────────────────────────────────────────
type Page = 'dashboard' | 'map' | 'anomalies' | 'documents' | 'ai' | 'audit'

const NAV_ITEMS: Array<{ id: Page; label: string; icon: React.FC }> = [
  { id: 'dashboard', label: 'Dashboard',           icon: Icons.Dashboard },
  { id: 'map',       label: 'Spatial Intelligence', icon: Icons.Map       },
  { id: 'anomalies', label: 'Risk & Anomalies',    icon: Icons.Alert     },
  { id: 'documents', label: 'Document Intel',      icon: Icons.Doc       },
  { id: 'ai',        label: 'Bhu-Intel AI',        icon: Icons.Bot       },
  { id: 'audit',     label: 'Audit Ledger',        icon: Icons.Shield    },
]

function AppContent() {
  const [page, setPage] = useState<Page>('dashboard')

  const renderPage = () => {
    switch (page) {
      case 'dashboard': return <DashboardPage />
      case 'map':       return <MapPage />
      case 'anomalies': return <AnomaliesPage />
      case 'documents': return <DocumentsPage />
      case 'ai':        return <AIAssistantPage />
      case 'audit':     return <AuditPage />
    }
  }

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-50">

      {/* ─── Top Header ─── */}
      <header className="h-13 flex items-center px-5 border-b border-slate-200 bg-white z-20 shrink-0 h-14">
        <div className="flex items-center gap-3">
          {/* Logo mark */}
          <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 overflow-hidden"
               style={{ background: 'linear-gradient(135deg, #f97316 0%, #059669 100%)' }}>
            <span className="text-white text-[10px] font-black tracking-tight">BLI</span>
          </div>
          <div>
            <h1 className="text-sm font-extrabold tracking-tight text-slate-800 leading-none">
              BHARAT LAND INTELLIGENCE
            </h1>
            <p className="text-[10px] text-slate-400 leading-none mt-0.5">
              Evidence-Based Governance · SIH26019
            </p>
          </div>
        </div>

        <div className="ml-auto flex items-center gap-3">
          <span className="flex items-center gap-1.5 text-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-500 pulse-live" />
            <span className="text-emerald-600 font-semibold">LIVE</span>
          </span>
          <span className="text-xs px-2.5 py-1 bg-red-50 text-red-500 border border-red-200 rounded-md font-mono font-semibold">
            DEMO MODE
          </span>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">

        {/* ─── Sidebar ─── */}
        <aside className="sidebar w-56 flex flex-col shrink-0">
          <nav className="flex-1 p-3 space-y-0.5">
            {NAV_ITEMS.map(item => {
              const Icon = item.icon
              const active = page === item.id
              return (
                <button
                  key={item.id}
                  onClick={() => setPage(item.id)}
                  className={`sidebar-nav-item ${active ? 'active' : ''}`}
                >
                  <Icon />
                  <span className="flex-1">{item.label}</span>
                  {active && <Icons.ChevronRight />}
                </button>
              )
            })}
          </nav>

          {/* System Status */}
          <div className="p-3 border-t border-white/10">
            <div className="rounded-xl p-3 text-xs" style={{ background: 'rgba(255,255,255,0.06)' }}>
              <div className="font-semibold text-white/80 mb-2.5">System Status</div>
              {[
                ['Database',   'text-emerald-400'],
                ['GIS Engine', 'text-emerald-400'],
                ['ML Pipeline','text-emerald-400'],
                ['RAG Engine', 'text-amber-400'],
              ].map(([name, cls]) => (
                <div key={name} className="flex justify-between mb-1.5 text-white/50">
                  <span>{name}</span><span className={cls}>●</span>
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* ─── Content ─── */}
        <main className="flex-1 overflow-hidden bg-slate-50">
          {renderPage()}
        </main>
      </div>
    </div>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  )
}

export default App
