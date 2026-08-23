import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Activity, 
  Clock, 
  AlertCircle, 
  Globe, 
  MessageSquare, 
  UserCheck, 
  Building2, 
  Search, 
  Bot, 
  FileText, 
  CheckCircle2, 
  ShieldAlert, 
  HelpCircle, 
  ArrowRight,
  Shield,
  Layers,
  Sparkles
} from 'lucide-react';

export default function RiskIntelligence() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch real protection events from backend
  useEffect(() => {
    fetch('/api/protection-events?limit=50')
      .then((res) => res.json())
      .then((data) => {
        setEvents(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // Derived real status counts
  const totalEvents = events.length;
  const holdEvents = events.filter(e => e.action === 'HOLD');
  const blockEvents = events.filter(e => e.action === 'BLOCK');
  const verifyEvents = events.filter(e => e.action === 'VERIFY');

  return (
    <div className="risk-intelligence-container" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* PAGE HEADER */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <Shield size={22} color="#0c66e4" />
          <h2 style={{ fontSize: '24px', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em' }}>
            Security Operations Intelligence
          </h2>
        </div>
        <p style={{ color: '#64748b', fontSize: '14px', margin: 0 }}>
          Understand how SecureFlow investigates payment activity and applies protection.
        </p>
      </div>

      {/* 1. TOP SECTION: OPERATIONAL STATUS CARDS */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', 
        gap: '16px' 
      }}>
        {/* Card 1: Security Status */}
        <div className="card" style={{ padding: '20px', border: '1px solid #e2e8f0', borderRadius: '10px', backgroundColor: '#ffffff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: '#64748b', letterSpacing: '0.05em' }}>
              Security Status
            </span>
            <ShieldCheck size={20} color="#16a34a" />
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>
            Protection System Active
          </div>
          <div style={{ fontSize: '13px', color: '#16a34a', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#16a34a', display: 'inline-block' }}></span>
            Operational
          </div>
        </div>

        {/* Card 2: Active Protection */}
        <div className="card" style={{ padding: '20px', border: '1px solid #e2e8f0', borderRadius: '10px', backgroundColor: '#ffffff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: '#64748b', letterSpacing: '0.05em' }}>
              Active Protection
            </span>
            <Activity size={20} color="#0c66e4" />
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>
            Monitoring Payment Activity
          </div>
          <div style={{ fontSize: '13px', color: '#64748b' }}>
            {totalEvents > 0 ? `${totalEvents} events evaluated` : 'Active'}
          </div>
        </div>

        {/* Card 3: Recent Security Activity */}
        <div className="card" style={{ padding: '20px', border: '1px solid #e2e8f0', borderRadius: '10px', backgroundColor: '#ffffff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: '#64748b', letterSpacing: '0.05em' }}>
              Recent Security Activity
            </span>
            <Clock size={20} color="#d97706" />
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>
            Latest Protection Events
          </div>
          <div style={{ fontSize: '13px', color: '#64748b' }}>
            {blockEvents.length + holdEvents.length > 0 
              ? `${blockEvents.length + holdEvents.length} security actions taken`
              : 'Active protection engaged'}
          </div>
        </div>

        {/* Card 4: Investigation Queue */}
        <div className="card" style={{ padding: '20px', border: '1px solid #e2e8f0', borderRadius: '10px', backgroundColor: '#ffffff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: '#64748b', letterSpacing: '0.05em' }}>
              Investigation Queue
            </span>
            <AlertCircle size={20} color={holdEvents.length > 0 ? '#dc2626' : '#2563eb'} />
          </div>
          <div style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>
            Cases Requiring Attention
          </div>
          <div style={{ fontSize: '13px', color: holdEvents.length > 0 ? '#dc2626' : '#64748b', fontWeight: holdEvents.length > 0 ? 600 : 400 }}>
            {holdEvents.length > 0 ? `${holdEvents.length} payments under review` : 'No cases requiring attention'}
          </div>
        </div>
      </div>

      {/* 2. SECURITY SIGNALS SECTION */}
      <div className="card" style={{ padding: '24px', border: '1px solid #e2e8f0', borderRadius: '10px', backgroundColor: '#ffffff' }}>
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>
            Security Signals
          </h3>
          <p style={{ color: '#64748b', fontSize: '13px', margin: 0 }}>
            Evidence SecureFlow uses to understand payment context.
          </p>
        </div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
          gap: '16px' 
        }}>
          {/* Signal 1: URL Intelligence */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#f8fafc', display: 'flex', gap: '14px' }}>
            <div style={{ padding: '10px', borderRadius: '8px', backgroundColor: '#eff6ff', color: '#0c66e4', height: 'fit-content' }}>
              <Globe size={20} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '14px', color: '#0f172a', marginBottom: '4px' }}>
                URL Intelligence
              </div>
              <div style={{ fontSize: '13px', color: '#475569', lineHeight: '1.4' }}>
                Checks whether the payment destination appears trustworthy.
              </div>
            </div>
          </div>

          {/* Signal 2: Scam Context Analysis */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#f8fafc', display: 'flex', gap: '14px' }}>
            <div style={{ padding: '10px', borderRadius: '8px', backgroundColor: '#eff6ff', color: '#0c66e4', height: 'fit-content' }}>
              <MessageSquare size={20} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '14px', color: '#0f172a', marginBottom: '4px' }}>
                Scam Context Analysis
              </div>
              <div style={{ fontSize: '13px', color: '#475569', lineHeight: '1.4' }}>
                Identifies suspicious language, urgency, impersonation, or payment-request patterns.
              </div>
            </div>
          </div>

          {/* Signal 3: Customer Behavior */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#f8fafc', display: 'flex', gap: '14px' }}>
            <div style={{ padding: '10px', borderRadius: '8px', backgroundColor: '#eff6ff', color: '#0c66e4', height: 'fit-content' }}>
              <UserCheck size={20} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '14px', color: '#0f172a', marginBottom: '4px' }}>
                Customer Behavior
              </div>
              <div style={{ fontSize: '13px', color: '#475569', lineHeight: '1.4' }}>
                Identifies unusual payment behavior relative to the customer's history.
              </div>
            </div>
          </div>

          {/* Signal 4: Merchant Consistency */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#f8fafc', display: 'flex', gap: '14px' }}>
            <div style={{ padding: '10px', borderRadius: '8px', backgroundColor: '#eff6ff', color: '#0c66e4', height: 'fit-content' }}>
              <Building2 size={20} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '14px', color: '#0f172a', marginBottom: '4px' }}>
                Merchant Consistency
              </div>
              <div style={{ fontSize: '13px', color: '#475569', lineHeight: '1.4' }}>
                Checks whether merchant identity matches the payment destination.
              </div>
            </div>
          </div>

          {/* Signal 5: Investigation Agent */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#f8fafc', display: 'flex', gap: '14px', gridColumn: '1 / -1' }}>
            <div style={{ padding: '10px', borderRadius: '8px', backgroundColor: '#eff6ff', color: '#0c66e4', height: 'fit-content' }}>
              <Search size={20} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '14px', color: '#0f172a', marginBottom: '4px' }}>
                Investigation Agent
              </div>
              <div style={{ fontSize: '13px', color: '#475569', lineHeight: '1.4' }}>
                Requests additional evidence when the payment context is ambiguous.
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. AGENTIC SECURITY INVESTIGATION SECTION */}
      <div className="card" style={{ padding: '24px', border: '1px solid #e2e8f0', borderRadius: '10px', backgroundColor: '#ffffff' }}>
        <div style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <Bot size={20} color="#0c66e4" />
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              Agentic Security Investigation
            </h3>
          </div>
          <p style={{ color: '#64748b', fontSize: '13px', margin: 0 }}>
            Automated multi-agent workflow investigating payment context and preparing policy evidence.
          </p>
        </div>

        {/* Workflow Diagram Stepper */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between', 
          padding: '16px 20px', 
          borderRadius: '8px', 
          backgroundColor: '#f8fafc', 
          border: '1px solid #e2e8f0',
          marginBottom: '20px',
          overflowX: 'auto',
          gap: '12px'
        }}>
          <div style={{ textAlign: 'center', minWidth: '100px' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#64748b' }}>1. INPUT</div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>Payment Context</div>
          </div>
          <ArrowRight size={16} color="#94a3b8" />
          
          <div style={{ textAlign: 'center', minWidth: '130px' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#0c66e4' }}>2. MERCHANT AGENT</div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>Identity Match</div>
          </div>
          <ArrowRight size={16} color="#94a3b8" />

          <div style={{ textAlign: 'center', minWidth: '130px' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#0c66e4' }}>3. INVESTIGATION</div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>Deep Evidence</div>
          </div>
          <ArrowRight size={16} color="#94a3b8" />

          <div style={{ textAlign: 'center', minWidth: '130px' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#0c66e4' }}>4. EVIDENCE SYNTHESIS</div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>Multi-Signal Bundle</div>
          </div>
          <ArrowRight size={16} color="#94a3b8" />

          <div style={{ textAlign: 'center', minWidth: '130px' }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#16a34a' }}>5. POLICY & RESPONSE</div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>Protection Action</div>
          </div>
        </div>

        {/* Detailed Agent Cards Grid */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', 
          gap: '16px' 
        }}>
          {/* Stage 1: Merchant Security Agent */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#ffffff' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#0c66e4', textTransform: 'uppercase' }}>
                Merchant Security Agent
              </span>
              <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '12px', backgroundColor: '#f0fdf4', color: '#16a34a', fontWeight: 600 }}>
                Active
              </span>
            </div>
            <div style={{ fontSize: '13px', color: '#334155', marginBottom: '8px', lineHeight: '1.4' }}>
              Verifies merchant identity and destination consistency.
            </div>
            <div style={{ fontSize: '12px', color: '#64748b' }}>
              <strong>What it checks:</strong> Legal corporate registrations, official domain records, and recipient VPA binding.
            </div>
          </div>

          {/* Stage 2: Investigation Agent */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#ffffff' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#0c66e4', textTransform: 'uppercase' }}>
                Investigation Agent
              </span>
              <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '12px', backgroundColor: '#f0fdf4', color: '#16a34a', fontWeight: 600 }}>
                Active
              </span>
            </div>
            <div style={{ fontSize: '13px', color: '#334155', marginBottom: '8px', lineHeight: '1.4' }}>
              Requests additional evidence when the initial signals are ambiguous.
            </div>
            <div style={{ fontSize: '12px', color: '#64748b' }}>
              <strong>What it checks:</strong> Customer baseline transaction history, recipient account age, velocity patterns.
            </div>
          </div>

          {/* Stage 3: Evidence Synthesis Agent */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#ffffff' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#0c66e4', textTransform: 'uppercase' }}>
                Evidence Synthesis Agent
              </span>
              <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '12px', backgroundColor: '#f0fdf4', color: '#16a34a', fontWeight: 600 }}>
                Active
              </span>
            </div>
            <div style={{ fontSize: '13px', color: '#334155', marginBottom: '8px', lineHeight: '1.4' }}>
              Combines findings from multiple security sources.
            </div>
            <div style={{ fontSize: '12px', color: '#64748b' }}>
              <strong>What it checks:</strong> Synthesizes normalized evidence indicators into an auditable evidence bundle.
            </div>
          </div>

          {/* Stage 4: Security Response Agent */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#ffffff' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: '#0c66e4', textTransform: 'uppercase' }}>
                Security Response Agent
              </span>
              <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '12px', backgroundColor: '#f0fdf4', color: '#16a34a', fontWeight: 600 }}>
                Active
              </span>
            </div>
            <div style={{ fontSize: '13px', color: '#334155', marginBottom: '8px', lineHeight: '1.4' }}>
              Carries out the approved protection action.
            </div>
            <div style={{ fontSize: '12px', color: '#64748b' }}>
              <strong>What it checks:</strong> Evaluates policy decision, logs audit trail events, and formats audience notices.
            </div>
          </div>
        </div>
      </div>

      {/* 4. PROTECTION ACTIONS SECTION */}
      <div className="card" style={{ padding: '24px', border: '1px solid #e2e8f0', borderRadius: '10px', backgroundColor: '#ffffff' }}>
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>
            Protection Actions
          </h3>
          <p style={{ color: '#64748b', fontSize: '13px', margin: 0 }}>
            Operational security outcomes determined by SecureFlow's protection policy engine.
          </p>
        </div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', 
          gap: '16px' 
        }}>
          {/* Action 1: ALLOW */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #bbf7d0', backgroundColor: '#f0fdf4' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <CheckCircle2 size={18} color="#16a34a" />
              <span style={{ fontWeight: 800, fontSize: '15px', color: '#15803d', letterSpacing: '0.04em' }}>
                ALLOW
              </span>
            </div>
            <div style={{ fontSize: '13px', color: '#166534', lineHeight: '1.4' }}>
              Payment context appears consistent. Normal payment flow continues.
            </div>
          </div>

          {/* Action 2: VERIFY */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #bfdbfe', backgroundColor: '#eff6ff' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <ShieldAlert size={18} color="#2563eb" />
              <span style={{ fontWeight: 800, fontSize: '15px', color: '#1d4ed8', letterSpacing: '0.04em' }}>
                VERIFY
              </span>
            </div>
            <div style={{ fontSize: '13px', color: '#1e40af', lineHeight: '1.4' }}>
              Additional customer confirmation is required before completion.
            </div>
          </div>

          {/* Action 3: HOLD */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #fde68a', backgroundColor: '#fffbeb' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <AlertCircle size={18} color="#d97706" />
              <span style={{ fontWeight: 800, fontSize: '15px', color: '#b45309', letterSpacing: '0.04em' }}>
                HOLD
              </span>
            </div>
            <div style={{ fontSize: '13px', color: '#92400e', lineHeight: '1.4' }}>
              Payment is temporarily paused for security review.
            </div>
          </div>

          {/* Action 4: BLOCK */}
          <div style={{ padding: '16px', borderRadius: '8px', border: '1px solid #fecaca', backgroundColor: '#fef2f2' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <ShieldAlert size={18} color="#dc2626" />
              <span style={{ fontWeight: 800, fontSize: '15px', color: '#b91c1c', letterSpacing: '0.04em' }}>
                BLOCK
              </span>
            </div>
            <div style={{ fontSize: '13px', color: '#991b1b', lineHeight: '1.4' }}>
              Payment is stopped because the security evidence indicates a serious threat.
            </div>
          </div>
        </div>
      </div>

      {/* 5. WHY SECUREFLOW ACTS SECTION */}
      <div className="card" style={{ padding: '24px', border: '1px solid #e2e8f0', borderRadius: '10px', backgroundColor: '#ffffff' }}>
        <div style={{ marginBottom: '20px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', marginBottom: '4px' }}>
            Why SecureFlow Acts
          </h3>
          <p style={{ color: '#64748b', fontSize: '13px', margin: 0 }}>
            Operational security reasoning across protection events without exposure of internal ML probabilities.
          </p>
        </div>

        {loading ? (
          <div style={{ padding: '24px', textAlign: 'center', color: '#64748b' }}>Loading protection event reasoning...</div>
        ) : events.length === 0 ? (
          /* Representative Backend Security Event Breakdown if DB is empty */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ padding: '18px', borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#f8fafc' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                <span style={{ fontSize: '12px', fontWeight: 700, color: '#64748b' }}>SCENARIO: FAKE ELECTRICITY DISCONNECTION SCAM</span>
                <span style={{ fontSize: '12px', fontWeight: 800, color: '#dc2626', backgroundColor: '#fef2f2', padding: '3px 10px', borderRadius: '12px', border: '1px solid #fecaca' }}>
                  ACTION: BLOCK
                </span>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
                <div>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>WHAT HAPPENED</div>
                  <div style={{ fontSize: '13px', color: '#0f172a', marginTop: '2px' }}>Payment destination domain did not match claimed merchant (BESCOM).</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>WHY IT MATTERS</div>
                  <div style={{ fontSize: '13px', color: '#0f172a', marginTop: '2px' }}>Destination is an unauthorized phishing URL impersonating official utility.</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>WHAT SECUREFLOW DID</div>
                  <div style={{ fontSize: '13px', color: '#0f172a', marginTop: '2px' }}>Payment blocked before completion to prevent loss of funds.</div>
                </div>
                <div>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>WHAT TO DO NEXT</div>
                  <div style={{ fontSize: '13px', color: '#0f172a', marginTop: '2px' }}>Pay via official BESCOM portal at verified domain bescom.co.in.</div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Live Protection Events from Backend */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {events.slice(0, 5).map((evt) => (
              <div key={evt.event_id} style={{ padding: '18px', borderRadius: '8px', border: '1px solid #e2e8f0', backgroundColor: '#f8fafc' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span style={{ fontSize: '13px', fontWeight: 700, fontFamily: 'monospace', color: '#0f172a' }}>{evt.event_id}</span>
                    <span style={{ fontSize: '12px', color: '#64748b', fontFamily: 'monospace' }}>TXN: {evt.transaction_id}</span>
                  </div>
                  <span style={{ 
                    fontSize: '12px', 
                    fontWeight: 800, 
                    padding: '3px 10px', 
                    borderRadius: '12px',
                    backgroundColor: evt.action === 'BLOCK' ? '#fef2f2' : evt.action === 'HOLD' ? '#fffbeb' : evt.action === 'VERIFY' ? '#eff6ff' : '#f0fdf4',
                    color: evt.action === 'BLOCK' ? '#dc2626' : evt.action === 'HOLD' ? '#b45309' : evt.action === 'VERIFY' ? '#1d4ed8' : '#15803d',
                    border: `1px solid ${evt.action === 'BLOCK' ? '#fecaca' : evt.action === 'HOLD' ? '#fde68a' : evt.action === 'VERIFY' ? '#bfdbfe' : '#bbf7d0'}`
                  }}>
                    ACTION: {evt.action}
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
                  <div>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>WHAT HAPPENED</div>
                    <div style={{ fontSize: '13px', color: '#0f172a', marginTop: '2px' }}>
                      {evt.explanation || "Security signals evaluated against policy rules."}
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>WHY IT MATTERS</div>
                    <div style={{ fontSize: '13px', color: '#0f172a', marginTop: '2px' }}>
                      {evt.action === 'BLOCK' 
                        ? 'High threat indicator: destination identity mismatch or phishing link.'
                        : evt.action === 'HOLD'
                        ? 'Inconclusive payee evidence requires manual security review.'
                        : evt.action === 'VERIFY'
                        ? 'Unusual amount pattern or new recipient requires step-up confirmation.'
                        : 'Payment context aligns with normal transaction history.'}
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>WHAT SECUREFLOW DID</div>
                    <div style={{ fontSize: '13px', color: '#0f172a', marginTop: '2px' }}>
                      {evt.action === 'BLOCK' ? 'Payment stopped before completion.' : evt.action === 'HOLD' ? 'Payment paused for review.' : evt.action === 'VERIFY' ? 'Step-up verification prompt issued.' : 'Payment allowed to proceed.'}
                    </div>
                  </div>

                  <div>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>WHAT TO DO NEXT</div>
                    <div style={{ fontSize: '13px', color: '#0f172a', marginTop: '2px' }}>
                      {evt.action === 'BLOCK' 
                        ? 'Use official verified merchant channels.' 
                        : evt.action === 'HOLD' 
                        ? 'Confirm payee invoice details before retrying.' 
                        : evt.action === 'VERIFY' 
                        ? 'Complete two-step confirmation.' 
                        : 'No further action needed.'}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
