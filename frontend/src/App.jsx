import React, { useState } from 'react';
import CustomerCheckout from './components/CustomerCheckout';
import OpsDashboard from './components/OpsDashboard';
import AttackSimulator from './components/AttackSimulator';
import { Shield, Eye, Lock, LayoutDashboard, Cpu } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('customer');

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header Navigation */}
      <header style={{ borderBottom: '1px solid var(--border-card)', background: 'rgba(11, 15, 25, 0.85)', backdropFilter: 'blur(16px)', position: 'sticky', top: 0, zIndex: 100 }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.85rem 1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ background: 'linear-gradient(135deg, #3b82f6, #06b6d4)', padding: '0.55rem', borderRadius: '12px', color: '#fff', boxShadow: '0 4px 15px rgba(59, 130, 246, 0.4)' }}>
              <Shield size={24} />
            </div>
            <div>
              <h1 style={{ fontSize: '1.35rem', fontWeight: 800, background: 'linear-gradient(135deg, #fff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '-0.02em' }}>
                SECUREFLOW
              </h1>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                Adaptive Payment Protection Layer
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(255,255,255,0.05)', padding: '0.3rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
            <button
              onClick={() => setActiveTab('customer')}
              className="btn-secondary"
              style={{
                fontSize: '0.85rem',
                padding: '0.45rem 1rem',
                border: 'none',
                background: activeTab === 'customer' ? 'var(--accent-blue)' : 'transparent',
                color: activeTab === 'customer' ? '#fff' : 'var(--text-muted)',
                borderRadius: '8px',
                fontWeight: activeTab === 'customer' ? 600 : 400
              }}
            >
              <Lock size={15} style={{ marginRight: '6px' }} /> Customer Payment UX
            </button>

            <button
              onClick={() => setActiveTab('ops')}
              className="btn-secondary"
              style={{
                fontSize: '0.85rem',
                padding: '0.45rem 1rem',
                border: 'none',
                background: activeTab === 'ops' ? 'var(--accent-blue)' : 'transparent',
                color: activeTab === 'ops' ? '#fff' : 'var(--text-muted)',
                borderRadius: '8px',
                fontWeight: activeTab === 'ops' ? 600 : 400
              }}
            >
              <LayoutDashboard size={15} style={{ marginRight: '6px' }} /> Risk Operations Console
            </button>

            <button
              onClick={() => setActiveTab('simulator')}
              className="btn-secondary"
              style={{
                fontSize: '0.85rem',
                padding: '0.45rem 1rem',
                border: 'none',
                background: activeTab === 'simulator' ? 'var(--accent-blue)' : 'transparent',
                color: activeTab === 'simulator' ? '#fff' : 'var(--text-muted)',
                borderRadius: '8px',
                fontWeight: activeTab === 'simulator' ? 600 : 400
              }}
            >
              <Cpu size={15} style={{ marginRight: '6px' }} /> Attack Simulator
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="container" style={{ flex: 1, paddingTop: '1.5rem' }}>
        {activeTab === 'customer' && <CustomerCheckout />}
        {activeTab === 'ops' && <OpsDashboard />}
        {activeTab === 'simulator' && <AttackSimulator />}
      </main>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border-card)', padding: '1.25rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: '3rem' }}>
        SecureFlow Prototype — Razorpay AI Builder Internship 2026 (AI Risk Manager Track)
      </footer>
    </div>
  );
}
