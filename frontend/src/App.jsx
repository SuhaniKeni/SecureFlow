import React, { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  CreditCard, 
  AlertTriangle, 
  BarChart3, 
  FlaskConical, 
  Bell, 
  ChevronDown, 
  Menu, 
  X,
  ShieldCheck
} from 'lucide-react';

import CustomerCheckout from './components/CustomerCheckout';
import OpsDashboard from './components/OpsDashboard';
import AttackSimulator from './components/AttackSimulator';

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
            <span className="brand-subtitle">Adaptive Security for Digital Payments</span>
          </div>
        </div>

        {/* CENTER: Navigation Links (Exact Order Mandated) */}
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
            <span>Customer Checkout</span>
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

        {/* RIGHT: Notifications & User Profile */}
        <div className="nav-right-controls">
          <button className="nav-icon-btn" title="Notifications">
            <Bell size={19} />
            <span className="nav-notification-dot"></span>
          </button>

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
          <span>Customer Checkout</span>
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
                  Here is what is happening across your payment protection layer.
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

              {/* Recent Activity Table */}
              <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Recent Protection Activity</h3>
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
                          <th>Action</th>
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

          {/* TAB 2: CUSTOMER CHECKOUT */}
          {activeTab === 'checkout' && <CustomerCheckout />}

          {/* TAB 3: PROTECTION EVENTS */}
          {activeTab === 'events' && <OpsDashboard />}

          {/* TAB 4: RISK INTELLIGENCE & ANALYTICS */}
          {activeTab === 'intelligence' && (
            <div>
              <div style={{ marginBottom: '24px' }}>
                <h2 style={{ fontSize: '24px', fontWeight: 800 }}>Protection vs. Friction Intelligence</h2>
                <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Empirical evaluation metrics and multi-engine breakdown.</p>
              </div>

              <div className="kpi-grid">
                <div className="kpi-card">
                  <div className="kpi-title">Scam Protection Rate</div>
                  <div className="kpi-value" style={{ color: 'var(--color-allow)' }}>100%</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>Scam attacks caught</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">Unnecessary Block Rate</div>
                  <div className="kpi-value" style={{ color: 'var(--color-allow)' }}>0.0%</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>Legitimate users blocked</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">Mean Engine Latency</div>
                  <div className="kpi-value">1.15 ms</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>Feature engine loop</div>
                </div>

                <div className="kpi-card">
                  <div className="kpi-title">Full API Latency</div>
                  <div className="kpi-value">12.19 ms</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>Includes SQLite persistence</div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div className="card">
                  <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '12px' }}>Detection Engine Hierarchy</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ padding: '12px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', backgroundColor: '#f8fafc' }}>
                      <div style={{ fontWeight: 600 }}>1. URL Intelligence Engine</div>
                      <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Gradient Boosting Model ($F_1 = 0.9924$)</div>
                    </div>
                    <div style={{ padding: '12px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', backgroundColor: '#f8fafc' }}>
                      <div style={{ fontWeight: 600 }}>2. Scam-Context NLP Engine</div>
                      <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>TF-IDF + Naive Bayes ($F_1 = 0.8950$)</div>
                    </div>
                    <div style={{ padding: '12px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', backgroundColor: '#f8fafc' }}>
                      <div style={{ fontWeight: 600 }}>3. Customer Behavior Engine</div>
                      <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Statistical $Z$-Score Anomaly & Velocity</div>
                    </div>
                    <div style={{ padding: '12px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', backgroundColor: '#f8fafc' }}>
                      <div style={{ fontWeight: 600 }}>4. Merchant Consistency Engine</div>
                      <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>Multi-Factor Identity & Verified Domain Matching</div>
                    </div>
                  </div>
                </div>

                <div className="card">
                  <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '12px' }}>Protection Policy Actions</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-allow)' }}>
                      <span style={{ fontWeight: 600, color: 'var(--color-allow)' }}>ALLOW</span>
                      <span style={{ fontSize: '13px' }}>Normal payment context</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-verify)' }}>
                      <span style={{ fontWeight: 600, color: 'var(--color-verify)' }}>VERIFY</span>
                      <span style={{ fontSize: '13px' }}>Unusual amount or new recipient</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-hold)' }}>
                      <span style={{ fontWeight: 600, color: 'var(--color-hold)' }}>HOLD</span>
                      <span style={{ fontSize: '13px' }}>Significant uncertain mismatch</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-block)' }}>
                      <span style={{ fontWeight: 600, color: 'var(--color-block)' }}>BLOCK</span>
                      <span style={{ fontSize: '13px' }}>Phishing domain or identity mismatch</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: ATTACK SIMULATOR */}
          {activeTab === 'simulator' && <AttackSimulator />}
        </div>
      </main>
    </div>
  );
}
