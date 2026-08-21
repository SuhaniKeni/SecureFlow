import React, { useState } from 'react';
import { 
  Play, ShieldAlert, ShieldCheck, Clock, CheckCircle, XCircle, 
  ArrowRight, Terminal, RefreshCw, Cpu, Layers, HelpCircle
} from 'lucide-react';

const BENCHMARK_SCENARIOS = [
  {
    id: "SCN-001",
    name: "1. Legitimate Recurring Electricity Payment",
    category: "Legitimate Normal",
    expected_action: "ALLOW",
    input: {
      customer_id: "CUST-001",
      amount: 1450.00,
      recipient_id: "RCP-001",
      claimed_merchant: "BESCOM Electricity",
      payment_note: "Monthly electricity bill payment ref #400192839",
      url: "https://bescom.co.in/pay"
    }
  },
  {
    id: "SCN-002",
    name: "2. Fake Electricity Disconnection Payment Scam",
    category: "Social Engineering Attack",
    expected_action: "BLOCK",
    input: {
      customer_id: "CUST-001",
      amount: 8742.00,
      recipient_id: "RCP-004",
      claimed_merchant: "BESCOM Electricity Board",
      payment_note: "URGENT: Electricity power line will be disconnected tonight at 9.30pm. Pay overdue bill Rs 8742 immediately",
      url: "http://elect-pay-bill.top/pay"
    }
  },
  {
    id: "SCN-003",
    name: "3. Fake Bank Security Alert / KYC Phishing",
    category: "Phishing Attack",
    expected_action: "BLOCK",
    input: {
      customer_id: "CUST-002",
      amount: 15000.00,
      recipient_id: "RCP-005",
      claimed_merchant: "State Bank of India",
      payment_note: "DEAR CUSTOMER, your account is suspended due to missing KYC. Update immediately or legal action will be taken.",
      url: "http://bank-kyc-update.online/login"
    }
  },
  {
    id: "SCN-004",
    name: "4. Fake Courier Duty / Customs Payment",
    category: "Impersonation Attack",
    expected_action: "HOLD",
    input: {
      customer_id: "CUST-003",
      amount: 1499.00,
      recipient_id: "RCP-006",
      claimed_merchant: "India Post Express",
      payment_note: "COURIER ALERT: International parcel held at customs due to unpaid duty Rs 1499. Pay immediately to release.",
      url: "http://customs-clearance-pay.com/duty"
    }
  },
  {
    id: "SCN-005",
    name: "5. Fake Customer-Support Refund Fee Scam",
    category: "Refund Bait Attack",
    expected_action: "HOLD",
    input: {
      customer_id: "CUST-004",
      amount: 199.00,
      recipient_id: "RCP-005",
      claimed_merchant: "Customer Care Refund Portal",
      payment_note: "Dear User, customer support refund of Rs 4999 is approved. Pay processing fee of Rs 199 at refund portal.",
      url: "http://refund-support-portal.site/fee"
    }
  },
  {
    id: "SCN-006",
    name: "6. Fake Government Income Tax Refund Fee",
    category: "Government Impersonation",
    expected_action: "BLOCK",
    input: {
      customer_id: "CUST-005",
      amount: 850.00,
      recipient_id: "RCP-005",
      claimed_merchant: "Income Tax Refund Cell",
      payment_note: "URGENT: Income tax refund Rs 14,200 pending. Pay service tax Rs 850 immediately or account blocked.",
      url: "http://incometax-refund-gov.in.net/claim"
    }
  },
  {
    id: "SCN-007",
    name: "7. Legitimate High-Value Laptop Purchase",
    category: "Legitimate Unusual",
    expected_action: "VERIFY",
    input: {
      customer_id: "CUST-001",
      amount: 85000.00,
      recipient_id: "RCP-002",
      claimed_merchant: "Amazon India",
      payment_note: "Payment for Apple Laptop order #940182 via Amazon Pay",
      url: "https://amazon.in/checkout/pay"
    }
  },
  {
    id: "SCN-008",
    name: "8. New Legitimate Local Merchant",
    category: "Legitimate New Merchant",
    expected_action: "VERIFY",
    input: {
      customer_id: "CUST-002",
      amount: 3200.00,
      recipient_id: "RCP-003",
      claimed_merchant: "Local Hardware Store",
      payment_note: "Purchase of construction tools",
      url: "https://sbi.co.in/portal/pay"
    }
  },
  {
    id: "SCN-009",
    name: "9. Suspicious Recipient with Legitimate-Looking Request",
    category: "Disguised Fraud",
    expected_action: "HOLD",
    input: {
      customer_id: "CUST-003",
      amount: 4500.00,
      recipient_id: "RCP-004",
      claimed_merchant: "City Power Supply",
      payment_note: "Payment for monthly electricity charges",
      url: "http://elect-pay-bill.top/pay"
    }
  },
  {
    id: "SCN-010",
    name: "10. Merchant Identity Mismatch Scam",
    category: "Identity Impersonation",
    expected_action: "BLOCK",
    input: {
      customer_id: "CUST-001",
      amount: 12450.00,
      recipient_id: "RCP-004",
      claimed_merchant: "BESCOM Power Supply",
      payment_note: "Urgent: BESCOM electric bill due. Avoid penalty of Rs 5000. Pay now.",
      url: "http://bill-pay-fast.online/electricity"
    }
  }
];

export default function AttackSimulator() {
  const [runningId, setRunningId] = useState(null);
  const [scenarioResults, setScenarioResults] = useState({});
  const [isBatchRunning, setIsBatchRunning] = useState(false);

  const runSingleScenario = async (scenario) => {
    setRunningId(scenario.id);
    try {
      const response = await fetch('/api/scenarios/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: scenario.id })
      });
      if (response.ok) {
        const data = await response.json();
        setScenarioResults(prev => ({ ...prev, [scenario.id]: data }));
      }
    } catch (err) {
      console.error("Scenario execution error:", err);
    } finally {
      setRunningId(null);
    }
  };

  const runAllScenarios = async () => {
    setIsBatchRunning(true);
    for (const sc of BENCHMARK_SCENARIOS) {
      await runSingleScenario(sc);
    }
    setIsBatchRunning(false);
  };

  const getBadgeClass = (act) => {
    switch (act) {
      case 'BLOCK': return 'badge-block';
      case 'HOLD': return 'badge-hold';
      case 'VERIFY': return 'badge-verify';
      default: return 'badge-allow';
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      {/* Header Banner */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-cyan)', marginBottom: '0.25rem' }}>
            <Cpu size={20} />
            <span style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Benchmark Security Test Suite
            </span>
          </div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800 }}>SecureFlow Attack Scenario Simulator</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
            Evaluates the adaptive security layer against 10 controlled social-engineering and legitimate edge-case scenarios.
          </p>
        </div>

        <button
          onClick={runAllScenarios}
          disabled={isBatchRunning}
          className="btn-primary"
          style={{ padding: '0.75rem 1.25rem' }}
        >
          {isBatchRunning ? <RefreshCw size={18} className="animate-spin" /> : <Play size={18} />}
          Run All 10 Scenarios
        </button>
      </div>

      {/* Scenario Cards Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {BENCHMARK_SCENARIOS.map((sc) => {
          const res = scenarioResults[sc.id];
          const isRunning = runningId === sc.id;
          const isMatched = res ? (res.action === sc.expected_action) : null;

          return (
            <div key={sc.id} className="glass-panel" style={{ padding: '1.5rem', borderRadius: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', pb: '0.75rem', borderBottom: '1px solid var(--border-card)' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>{sc.category}</span>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>{sc.name}</h3>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <button
                    onClick={() => runSingleScenario(sc)}
                    disabled={isRunning}
                    className="btn-secondary"
                    style={{ fontSize: '0.8rem', padding: '0.4rem 0.85rem' }}
                  >
                    {isRunning ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} style={{ marginRight: '4px' }} />}
                    Run Scenario
                  </button>

                  {res && (
                    <span className={`badge ${isMatched ? 'badge-allow' : 'badge-block'}`} style={{ fontSize: '0.8rem' }}>
                      {isMatched ? <CheckCircle size={14} style={{ marginRight: '4px' }} /> : <XCircle size={14} style={{ marginRight: '4px' }} />}
                      {isMatched ? 'MATCH (PASS)' : 'MISMATCH'}
                    </span>
                  )}
                </div>
              </div>

              {/* 4 Pipeline Flow Grid: INPUT → DETECTED EVIDENCE → PROTECTION ACTION → EXPLANATION & EXPECTED OUTCOME */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', fontSize: '0.8rem' }}>
                
                {/* 1. INPUT */}
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.85rem', borderRadius: '10px' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>1. INPUT</span>
                  <p style={{ marginTop: '0.35rem', fontWeight: 600, color: '#fff' }}>₹{sc.input.amount.toLocaleString('en-IN')}</p>
                  <p style={{ color: 'var(--accent-cyan)', marginTop: '0.15rem' }}>{sc.input.claimed_merchant}</p>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '0.35rem', fontStyle: 'italic' }}>
                    "{sc.input.payment_note}"
                  </p>
                </div>

                {/* 2. DETECTED EVIDENCE */}
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.85rem', borderRadius: '10px' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>2. DETECTED EVIDENCE</span>
                  {res ? (
                    <div style={{ marginTop: '0.35rem', display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
                      {res.evidence_bundle?.evidence_items?.length > 0 ? (
                        res.evidence_bundle.evidence_items.map((item, idx) => (
                          <p key={idx} style={{ color: '#fbbf24', fontSize: '0.75rem' }}>• {item.signal_type}</p>
                        ))
                      ) : (
                        <p style={{ color: '#34d399', fontSize: '0.75rem' }}>• Clean normal baseline</p>
                      )}
                    </div>
                  ) : (
                    <p style={{ color: 'var(--text-muted)', marginTop: '0.35rem', fontStyle: 'italic' }}>Click "Run Scenario"</p>
                  )}
                </div>

                {/* 3. PROTECTION ACTION */}
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.85rem', borderRadius: '10px' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>3. PROTECTION ACTION</span>
                  {res ? (
                    <div style={{ marginTop: '0.5rem' }}>
                      <span className={`badge ${getBadgeClass(res.action)}`} style={{ fontSize: '0.85rem' }}>
                        {res.action}
                      </span>
                    </div>
                  ) : (
                    <p style={{ color: 'var(--text-muted)', marginTop: '0.35rem', fontStyle: 'italic' }}>Pending execution</p>
                  )}
                </div>

                {/* 4. EXPLANATION & EXPECTED OUTCOME */}
                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.85rem', borderRadius: '10px' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>4. EXPECTED OUTCOME</span>
                  <p style={{ marginTop: '0.35rem', color: '#fff', fontWeight: 600 }}>Expected: {sc.expected_action}</p>
                  {res && (
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                      {res.customer_explanation?.what_happened}
                    </p>
                  )}
                </div>

              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
