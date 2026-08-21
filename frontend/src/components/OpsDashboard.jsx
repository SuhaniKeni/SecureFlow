import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, ShieldCheck, Clock, Filter, Search, Calendar, 
  UserCheck, AlertTriangle, ArrowUpRight, Eye, CheckCircle2, XCircle
} from 'lucide-react';

export default function OpsDashboard() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState(null);

  // Filter States
  const [filterAction, setFilterAction] = useState("ALL");
  const [filterSeverity, setFilterSeverity] = useState("ALL");
  const [filterMerchant, setFilterMerchant] = useState("ALL");
  const [searchTerm, setSearchTerm] = useState("");

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/protection-events?limit=50');
      if (response.ok) {
        const data = await response.json();
        setEvents(data);
        if (data.length > 0 && !selectedEvent) {
          setSelectedEvent(data[0]);
        }
      }
    } catch (err) {
      console.error("Failed to fetch protection events:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  // Filtered Events List
  const filteredEvents = events.filter((evt) => {
    const evidence = evt.evidence || {};
    const items = evidence.evidence_items || [];
    
    // Action filter
    if (filterAction !== "ALL" && evt.action !== filterAction) return false;
    
    // Severity filter
    const sev = evidence.overall_severity || "low";
    if (filterSeverity !== "ALL" && sev.toUpperCase() !== filterSeverity) return false;

    // Search term
    if (searchTerm) {
      const st = searchTerm.toLowerCase();
      const matchTx = evt.transaction_id.toLowerCase().includes(st);
      const matchEv = evt.event_id.toLowerCase().includes(st);
      if (!matchTx && !matchEv) return false;
    }

    return true;
  });

  const getActionBadgeClass = (action) => {
    switch (action) {
      case 'BLOCK': return 'badge-block';
      case 'HOLD': return 'badge-hold';
      case 'VERIFY': return 'badge-verify';
      default: return 'badge-allow';
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 420px', gap: '1.5rem', alignItems: 'start' }}>
      
      {/* Left Column: Metrics & Event Timeline Feed */}
      <div>
        {/* Metrics Header */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
          <div className="glass-panel" style={{ padding: '1rem 1.25rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Events</span>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff', marginTop: '0.25rem' }}>{events.length}</div>
          </div>
          <div className="glass-panel" style={{ padding: '1rem 1.25rem', borderColor: 'rgba(239, 68, 68, 0.3)' }}>
            <span style={{ fontSize: '0.75rem', color: '#f87171', textTransform: 'uppercase' }}>Blocked Threats</span>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f87171', marginTop: '0.25rem' }}>
              {events.filter(e => e.action === 'BLOCK').length}
            </div>
          </div>
          <div className="glass-panel" style={{ padding: '1rem 1.25rem', borderColor: 'rgba(59, 130, 246, 0.3)' }}>
            <span style={{ fontSize: '0.75rem', color: '#60a5fa', textTransform: 'uppercase' }}>Held Under Review</span>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#60a5fa', marginTop: '0.25rem' }}>
              {events.filter(e => e.action === 'HOLD').length}
            </div>
          </div>
          <div className="glass-panel" style={{ padding: '1rem 1.25rem', borderColor: 'rgba(245, 158, 11, 0.3)' }}>
            <span style={{ fontSize: '0.75rem', color: '#fbbf24', textTransform: 'uppercase' }}>2FA Verification</span>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fbbf24', marginTop: '0.25rem' }}>
              {events.filter(e => e.action === 'VERIFY').length}
            </div>
          </div>
        </div>

        {/* Filter Controls Bar */}
        <div className="glass-panel" style={{ padding: '1rem 1.25rem', marginBottom: '1.25rem', display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1, minWidth: '200px', background: 'rgba(0,0,0,0.3)', padding: '0.5rem 0.85rem', borderRadius: '8px', border: '1px solid var(--border-card)' }}>
            <Search size={16} color="var(--text-muted)" />
            <input
              type="text"
              placeholder="Search Transaction ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: '#fff', outline: 'none', width: '100%', fontSize: '0.85rem' }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Filter size={16} color="var(--text-muted)" />
            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              style={{ background: 'rgba(0,0,0,0.4)', color: '#fff', border: '1px solid var(--border-card)', padding: '0.45rem 0.75rem', borderRadius: '8px', fontSize: '0.85rem' }}
            >
              <option value="ALL">Action: All</option>
              <option value="BLOCK">Action: BLOCK</option>
              <option value="HOLD">Action: HOLD</option>
              <option value="VERIFY">Action: VERIFY</option>
              <option value="ALLOW">Action: ALLOW</option>
            </select>

            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value)}
              style={{ background: 'rgba(0,0,0,0.4)', color: '#fff', border: '1px solid var(--border-card)', padding: '0.45rem 0.75rem', borderRadius: '8px', fontSize: '0.85rem' }}
            >
              <option value="ALL">Severity: All</option>
              <option value="HIGH">Severity: High</option>
              <option value="MEDIUM">Severity: Medium</option>
              <option value="LOW">Severity: Low</option>
            </select>
          </div>
        </div>

        {/* Protection Events Table / Timeline */}
        <div className="glass-panel" style={{ overflow: 'hidden' }}>
          <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-card)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Protection Incident Timeline</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Showing {filteredEvents.length} events</span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ background: 'rgba(255,255,255,0.03)', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-card)' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Transaction ID</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Action Taken</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Severity</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Details</th>
                </tr>
              </thead>
              <tbody>
                {filteredEvents.map((evt) => {
                  const isSelected = selectedEvent?.event_id === evt.event_id;
                  const sev = evt.evidence?.overall_severity || 'low';
                  return (
                    <tr
                      key={evt.event_id}
                      onClick={() => setSelectedEvent(evt)}
                      style={{
                        borderBottom: '1px solid rgba(255,255,255,0.05)',
                        background: isSelected ? 'rgba(59, 130, 246, 0.12)' : 'transparent',
                        cursor: 'pointer',
                        transition: 'background 0.15s ease'
                      }}
                    >
                      <td style={{ padding: '0.75rem 1rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                        {new Date(evt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </td>
                      <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{evt.transaction_id}</td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span className={`badge ${getActionBadgeClass(evt.action)}`}>
                          {evt.action}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span style={{
                          color: sev === 'high' ? '#f87171' : (sev === 'medium' ? '#fbbf24' : '#34d399'),
                          fontWeight: 600,
                          fontSize: '0.75rem',
                          textTransform: 'uppercase'
                        }}>
                          {sev}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <button className="btn-secondary" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}>
                          Inspect <Eye size={12} style={{ marginLeft: '4px' }} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Right Column: Forensic Inspector Panel (Visual Hierarchy Answering 5 Core Questions) */}
      <div className="glass-panel" style={{ padding: '1.5rem', sticky: 'top', top: '90px' }}>
        {selectedEvent ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', pb: '0.75rem', borderBottom: '1px solid var(--border-card)' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Incident Audit Record</span>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800 }}>{selectedEvent.event_id}</h3>
              </div>
              <span className={`badge ${getActionBadgeClass(selectedEvent.action)}`} style={{ fontSize: '0.85rem' }}>
                {selectedEvent.action}
              </span>
            </div>

            {/* Q1: WHAT HAPPENED? */}
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-cyan)', marginBottom: '0.35rem' }}>
                <AlertTriangle size={16} />
                <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>1. WHAT HAPPENED?</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#e2e8f0', background: 'rgba(0,0,0,0.3)', padding: '0.75rem', borderRadius: '8px' }}>
                Transaction <strong style={{ color: '#fff' }}>{selectedEvent.transaction_id}</strong> triggered protection evaluation at {new Date(selectedEvent.timestamp).toLocaleString()}.
              </p>
            </div>

            {/* Q2: WHY? (Forensic Evidence Breakdown) */}
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-amber)', marginBottom: '0.35rem' }}>
                <ShieldAlert size={16} />
                <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>2. WHY? (EVIDENCE BREAKDOWN)</span>
              </div>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.75rem', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {selectedEvent.evidence?.evidence_items?.length > 0 ? (
                  selectedEvent.evidence.evidence_items.map((item, idx) => (
                    <div key={idx} style={{ borderLeft: '3px solid #f59e0b', paddingLeft: '0.5rem' }}>
                      <p style={{ fontSize: '0.8rem', fontWeight: 600, color: '#fff' }}>{item.signal_type}</p>
                      <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.description}</p>
                    </div>
                  ))
                ) : (
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{selectedEvent.explanation || "No risk indicators flagged."}</p>
                )}
              </div>
            </div>

            {/* Q3: WHAT DID SECUREFLOW DO? */}
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-blue)', marginBottom: '0.35rem' }}>
                <ShieldCheck size={16} />
                <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>3. WHAT DID SECUREFLOW DO?</span>
              </div>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.75rem', borderRadius: '8px' }}>
                <p style={{ fontSize: '0.85rem', color: '#fff', fontWeight: 600 }}>
                  Executed Action: <span style={{ color: selectedEvent.action === 'BLOCK' ? '#f87171' : '#60a5fa' }}>{selectedEvent.action}</span>
                </p>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                  Deterministic Policy Rule Evaluated & Audit Trail Saved.
                </p>
              </div>
            </div>

            {/* Q4: WHAT SHOULD THE ANALYST DO? */}
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#34d399', marginBottom: '0.35rem' }}>
                <UserCheck size={16} />
                <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>4. RECOMMENDED ANALYST ACTION</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#a7f3d0', background: 'rgba(6, 78, 59, 0.3)', padding: '0.75rem', borderRadius: '8px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
                {selectedEvent.action === 'BLOCK' ? 'Verify payee identity with merchant and confirm block status.' : 'Review recipient verification documentation.'}
              </p>
            </div>

            {/* Q5: HOW CAN THIS BE PREVENTED? */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-cyan)', marginBottom: '0.35rem' }}>
                <CheckCircle2 size={16} />
                <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>5. SYSTEMIC PREVENTION</span>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', background: 'rgba(0,0,0,0.3)', padding: '0.75rem', borderRadius: '8px' }}>
                Place destination VPA/domain under enhanced monitoring and enforce 2FA authorization.
              </p>
            </div>

          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem 0', color: 'var(--text-muted)' }}>
            Select an incident timeline event to inspect forensic details.
          </div>
        )}
      </div>

    </div>
  );
}
