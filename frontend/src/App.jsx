import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  CreditCard, 
  AlertTriangle, 
  BarChart3, 
  FlaskConical, 
  ChevronDown, 
  Menu, 
  X,
  Bot
} from 'lucide-react';

import CustomerCheckout from './components/CustomerCheckout';
import OpsDashboard from './components/OpsDashboard';
import AttackSimulator from './components/AttackSimulator';
import RiskIntelligence from './components/RiskIntelligence';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Fetch real events for Overview KPI calculations
  useEffect(() => {
    fetch('/api/protection-events?limit=50')
      .then((res) => res.json())
      .then((data) => {
        setEvents(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [activeTab]);

  // Derived real KPI counts
  const totalAnalyzed = events.length;
  const blockedCount = events.filter((e) => e.action === 'BLOCK').length;
  const holdCount = events.filter((e) => e.action === 'HOLD').length;
  const verifyCount = events.filter((e) => e.action === 'VERIFY').length;
  const allowCount = events.filter((e) => e.action === 'ALLOW').length;

  const handleNavClick = (tabKey) => {
    setActiveTab(tabKey);
    setMobileMenuOpen(false);
  };

  return (
    <div className="app-container">
      {/* Sticky Horizontal Top Navigation Bar */}
      <header className="top-navbar">
        {/* LEFT: Logo & Brand Information */}
        <div className="nav-brand-section">
          <div className="logo-badge">SF</div>
          <div className="brand-title-group">
            <span className="brand-name">SECUREFLOW</span>
            <span className="brand-subtitle">Adaptive Agentic Security for Digital Payments</span>
          </div>
        </div>

        {/* CENTER: Navigation Links */}
        <nav className="nav-center-menu">
          <button 
            className={`nav-link ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => handleNavClick('overview')}
          >
            <LayoutDashboard size={17} />
            <span>Overview</span>
          </button>

          <button 
            className={`nav-link ${activeTab === 'checkout' ? 'active' : ''}`}
            onClick={() => handleNavClick('checkout')}
          >
            <CreditCard size={17} />
            <span>Secure Checkout</span>
          </button>

          <button 
            className={`nav-link ${activeTab === 'events' ? 'active' : ''}`}
            onClick={() => handleNavClick('events')}
          >
            <AlertTriangle size={17} />
            <span>Protection Events</span>
          </button>

          <button 
            className={`nav-link ${activeTab === 'intelligence' ? 'active' : ''}`}
            onClick={() => handleNavClick('intelligence')}
          >
            <BarChart3 size={17} />
            <span>Risk Intelligence</span>
          </button>

          <button 
            className={`nav-link ${activeTab === 'simulator' ? 'active' : ''}`}
            onClick={() => handleNavClick('simulator')}
          >
            <FlaskConical size={17} />
            <span>Attack Simulator</span>
          </button>
        </nav>

        {/* RIGHT: User Profile */}
        <div className="nav-right-controls">
          <button className="user-profile-btn">
            <div className="avatar-circle">RA</div>
            <div className="user-info">
              <span className="user-name">Risk Analyst</span>
              <span className="user-role">SecureFlow Ops</span>
            </div>
            <ChevronDown size={15} color="var(--text-muted)" />
          </button>
        </div>

        {/* Mobile Hamburger Button */}
        <button 
          className="mobile-menu-btn" 
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </header>

      {/* Mobile Navigation Drawer */}
      <div className={`mobile-drawer ${mobileMenuOpen ? 'open' : ''}`}>
        <button 
          className={`nav-link ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => handleNavClick('overview')}
        >
          <LayoutDashboard size={17} />
          <span>Overview</span>
        </button>

        <button 
          className={`nav-link ${activeTab === 'checkout' ? 'active' : ''}`}
          onClick={() => handleNavClick('checkout')}
        >
          <CreditCard size={17} />
          <span>Secure Checkout</span>
        </button>

        <button 
          className={`nav-link ${activeTab === 'events' ? 'active' : ''}`}
          onClick={() => handleNavClick('events')}
        >
          <AlertTriangle size={17} />
          <span>Protection Events</span>
        </button>

        <button 
          className={`nav-link ${activeTab === 'intelligence' ? 'active' : ''}`}
          onClick={() => handleNavClick('intelligence')}
        >
          <BarChart3 size={17} />
          <span>Risk Intelligence</span>
        </button>

        <button 
          className={`nav-link ${activeTab === 'simulator' ? 'active' : ''}`}
          onClick={() => handleNavClick('simulator')}
        >
          <FlaskConical size={17} />
          <span>Attack Simulator</span>
        </button>
      </div>

      {/* Main Full-Width Content Area */}
      <main className="main-content">
        <div className="content-body">
          {/* TAB 1: OVERVIEW DASHBOARD */}
          {activeTab === 'overview' && (
            <div>
              <div style={{ marginBottom: '24px' }}>
                <h2 style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.03em' }}>Good afternoon</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                  Live protection status across your adaptive payment security layer.
                </p>
              </div>

              {/* Real KPI Cards */}
              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-title">Payments Analyzed</div>
                  <div className="kpi-value">{totalAnalyzed}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>Live transactions evaluated</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">Protected (Blocked)</div>
                  <div className="kpi-value" style={{ color: 'var(--color-block)' }}>{blockedCount}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>Social engineering scams stopped</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">Under Review (Hold)</div>
                  <div className="kpi-value" style={{ color: 'var(--color-hold)' }}>{holdCount}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>Ambiguous merchant payee mismatches</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">Verified / Allowed</div>
                  <div className="kpi-value" style={{ color: 'var(--color-allow)' }}>{allowCount + verifyCount}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>Legitimate payments preserved</div>
                </div>
              </div>

              {/* Agentic Security Activity Feed */}
              <div className="card" style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                  <Bot size={20} color="var(--primary-blue)" />
                  <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Agentic Security Activity Pipeline</h3>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
                  <div style={{ padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: '#f8fafc' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary-blue)', textTransform: 'uppercase', marginBottom: '4px' }}>
                      Merchant Security Agent
                    </div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>Identity Verification</div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      Cross-references claimed payee names against verified corporate domains & VPAs.
                    </div>
                  </div>

                  <div style={{ padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: '#f8fafc' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary-blue)', textTransform: 'uppercase', marginBottom: '4px' }}>
                      Investigation Agent
                    </div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>Deep Evidence Retrieval</div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      Fetches customer baseline z-score history, recipient account age & transaction velocity.
                    </div>
                  </div>

                  <div style={{ padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: '#f8fafc' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary-blue)', textTransform: 'uppercase', marginBottom: '4px' }}>
                      Evidence Synthesis Agent
                    </div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>Multi-Signal Fusion</div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      Synthesizes NLP intent, URL phishing vectors, and baseline anomalies.
                    </div>
                  </div>

                  <div style={{ padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: '#f8fafc' }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary-blue)', textTransform: 'uppercase', marginBottom: '4px' }}>
                      Security Response Agent
                    </div>
                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>Deterministic Enforcement</div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      Executes deterministic protection action & generates dual audience explanations.
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Activity Table */}
              <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Recent Protection Events</h3>
                  <button className="btn btn-secondary" onClick={() => setActiveTab('events')}>View All Events</button>
                </div>

                {loading ? (
                  <div style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading live audit events...</div>
                ) : (
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          <th>Event ID</th>
                          <th>Transaction ID</th>
                          <th>Policy Action</th>
                          <th>Explanation Summary</th>
                          <th>Timestamp</th>
                        </tr>
                      </thead>
                      <tbody>
                        {events.slice(0, 8).map((evt) => (
                          <tr key={evt.event_id}>
                            <td style={{ fontWeight: 600, fontFamily: 'monospace' }}>{evt.event_id}</td>
                            <td style={{ fontFamily: 'monospace', color: 'var(--text-muted)' }}>{evt.transaction_id}</td>
                            <td>
                              <span className={`badge badge-${evt.action.toLowerCase()}`}>
                                {evt.action}
                              </span>
                            </td>
                            <td style={{ maxWidth: '400px' }}>{evt.explanation}</td>
                            <td style={{ color: 'var(--text-muted)', fontSize: '13px' }}>{new Date(evt.timestamp).toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: SECURE CHECKOUT */}
          {activeTab === 'checkout' && <CustomerCheckout />}

          {/* TAB 3: PROTECTION EVENTS */}
          {activeTab === 'events' && <OpsDashboard />}

          {/* TAB 4: RISK INTELLIGENCE & ANALYTICS */}
          {activeTab === 'intelligence' && <RiskIntelligence />}

          {/* TAB 5: ATTACK SIMULATOR */}
          {activeTab === 'simulator' && <AttackSimulator />}
        </div>
      </main>
    </div>
  );
}
