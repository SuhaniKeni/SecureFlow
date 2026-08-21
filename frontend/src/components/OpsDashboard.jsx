import React, { useState, useEffect } from 'react';
import { Search, Filter, AlertTriangle, ShieldCheck, X, ArrowRight, ExternalLink } from 'lucide-react';

export default function OpsDashboard() {
  const [events, setEvents] = useState([]);
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState('ALL');

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = () => {
    setLoading(true);
    fetch('/api/protection-events?limit=50')
      .then((res) => res.json())
      .then((data) => {
        const evts = Array.isArray(data) ? data : [];
        setEvents(evts);
        setFilteredEvents(evts);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    let result = events;
    if (actionFilter !== 'ALL') {
      result = result.filter((e) => e.action === actionFilter);
    }
    if (searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (e) =>
          e.event_id.toLowerCase().includes(q) ||
          e.transaction_id.toLowerCase().includes(q) ||
          e.explanation.toLowerCase().includes(q)
      );
    }
    setFilteredEvents(result);
  }, [searchQuery, actionFilter, events]);

  return (
    <div>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ fontSize: '22px', fontWeight: 700 }}>Risk Operations & Forensic Audit Log</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Review payment protection decisions, signal evidence, and systemic recommendations.</p>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ padding: '16px 24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input 
              className="form-input" 
              style={{ paddingLeft: '38px', width: '100%' }}
              placeholder="Search by Event ID, Transaction ID, or Reason..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={18} color="var(--text-muted)" />
            <select 
              className="form-select"
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
            >
              <option value="ALL">All Actions</option>
              <option value="BLOCK">BLOCK Only</option>
              <option value="HOLD">HOLD Only</option>
              <option value="VERIFY">VERIFY Only</option>
              <option value="ALLOW">ALLOW Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Events Table */}
      <div className="card" style={{ padding: 0 }}>
        {loading ? (
          <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading protection events...</div>
        ) : filteredEvents.length === 0 ? (
          <div style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <AlertTriangle size={32} style={{ marginBottom: '12px', color: '#94a3b8' }} />
            <div style={{ fontWeight: 600 }}>No protection events found</div>
            <div style={{ fontSize: '13px' }}>Try adjusting your filters or search query.</div>
          </div>
        ) : (
          <div className="table-container" style={{ border: 'none' }}>
            <table>
              <thead>
                <tr>
                  <th>Event ID</th>
                  <th>Transaction ID</th>
                  <th>Action Taken</th>
                  <th>Primary Reason</th>
                  <th>Timestamp</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredEvents.map((evt) => (
                  <tr key={evt.event_id}>
                    <td style={{ fontWeight: 600, fontFamily: 'monospace' }}>{evt.event_id}</td>
                    <td style={{ fontFamily: 'monospace', color: 'var(--text-muted)' }}>{evt.transaction_id}</td>
                    <td>
                      <span className={`badge badge-${evt.action.toLowerCase()}`}>
                        {evt.action}
                      </span>
                    </td>
                    <td style={{ maxWidth: '360px' }}>{evt.explanation}</td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '13px' }}>{new Date(evt.timestamp).toLocaleString()}</td>
                    <td>
                      <button 
                        className="btn btn-secondary" 
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                        onClick={() => setSelectedEvent(evt)}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Forensic Inspection Drawer */}
      {selectedEvent && (
        <div className="drawer-overlay" onClick={() => setSelectedEvent(null)}>
          <div className="drawer-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '16px', borderBottom: '1px solid var(--border-color)' }}>
              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--primary-blue)', textTransform: 'uppercase' }}>Risk Operations Inspection</div>
                <h3 style={{ fontSize: '18px', fontWeight: 700 }}>Event: {selectedEvent.event_id}</h3>
              </div>
              <button className="btn btn-secondary" style={{ padding: '6px' }} onClick={() => setSelectedEvent(null)}>
                <X size={18} />
              </button>
            </div>

            {/* 5-Question Forensic Hierarchy */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>1. WHAT HAPPENED?</div>
                <div style={{ fontSize: '15px', fontWeight: 600 }}>{selectedEvent.explanation}</div>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Transaction ID: <span style={{ fontFamily: 'monospace' }}>{selectedEvent.transaction_id}</span>
                </div>
              </div>

              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>2. WHY DID SECUREFLOW INTERVENE?</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {selectedEvent.evidence?.evidence_items?.map((item, idx) => (
                    <div key={idx} style={{ padding: '10px 14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: '#f8fafc', fontSize: '13px' }}>
                      <div style={{ fontWeight: 600, color: 'var(--primary-blue)' }}>{item.signal_type}</div>
                      <div>{item.description}</div>
                    </div>
                  )) || <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Evidence bundle details recorded.</div>}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>3. WHAT DID SECUREFLOW DO?</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span className={`badge badge-${selectedEvent.action.toLowerCase()}`} style={{ fontSize: '14px', padding: '6px 14px' }}>
                    {selectedEvent.action}
                  </span>
                  <span style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Deterministic Policy Rule Executed</span>
                </div>
              </div>

              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>4. RECOMMENDED ANALYST ACTION</div>
                <div style={{ padding: '12px', backgroundColor: 'var(--primary-blue-light)', color: 'var(--primary-blue-hover)', borderRadius: 'var(--radius-sm)', fontSize: '13px', fontWeight: 600 }}>
                  Confirm payee destination block and maintain recipient monitoring.
                </div>
              </div>

              <div>
                <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>5. SYSTEMIC PREVENTION RECOMMENDATION</div>
                <div style={{ padding: '12px', backgroundColor: '#f1f5f9', borderRadius: 'var(--radius-sm)', fontSize: '13px' }}>
                  Place phishing URL domain under network security blocklist.
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
