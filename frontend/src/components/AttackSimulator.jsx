import React, { useState } from 'react';
import { Play, CheckCircle, AlertTriangle, RefreshCw, ArrowRight, ShieldCheck } from 'lucide-react';

const BENCHMARK_SCENARIOS = [
  { scenario_id: "SCN-001", name: "Legitimate Recurring Electricity Payment", expected_action: "ALLOW", amount: 1450, payee: "BESCOM Electricity" },
  { scenario_id: "SCN-002", name: "Fake Electricity Disconnection Scam", expected_action: "BLOCK", amount: 8742, payee: "BESCOM Electricity Board" },
  { scenario_id: "SCN-003", name: "Fake Bank KYC Phishing Alert", expected_action: "BLOCK", amount: 15000, payee: "HDFC Bank Online" },
  { scenario_id: "SCN-004", name: "Fake Courier Customs Duty Scam", expected_action: "BLOCK", amount: 1499, payee: "India Post Courier" },
  { scenario_id: "SCN-005", name: "Fake Customer-Support Refund Scam", expected_action: "BLOCK", amount: 199, payee: "Customer Support Portal" },
  { scenario_id: "SCN-006", name: "Fake Government Tax Refund", expected_action: "BLOCK", amount: 850, payee: "Income Tax Department" },
  { scenario_id: "SCN-007", name: "Legitimate Large Laptop Purchase", expected_action: "VERIFY", amount: 85000, payee: "Amazon India" },
  { scenario_id: "SCN-008", name: "New Legitimate Merchant Payment", expected_action: "VERIFY", amount: 3200, payee: "Local Hardware Store" },
  { scenario_id: "SCN-009", name: "Suspicious Recipient Destination", expected_action: "BLOCK", amount: 4500, payee: "City Municipal Utility" },
  { scenario_id: "SCN-010", name: "Merchant Identity Mismatch", expected_action: "BLOCK", amount: 12450, payee: "BESCOM Electricity" }
];

export default function AttackSimulator() {
  const [running, setRunning] = useState(false);
  const [activeScenarioId, setActiveScenarioId] = useState(null);
  const [results, setResults] = useState({});

  const runSingleScenario = async (scId) => {
    setActiveScenarioId(scId);
    try {
      const res = await fetch('/api/scenarios/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_id: scId })
      });
      const data = await res.json();
      setResults((prev) => ({ ...prev, [scId]: data }));
    } catch (err) {
      console.error("Scenario execution error:", err);
    } finally {
      setActiveScenarioId(null);
    }
  };

  const runAllScenarios = async () => {
    setRunning(true);
    for (const sc of BENCHMARK_SCENARIOS) {
      await runSingleScenario(sc.scenario_id);
    }
    setRunning(false);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: 800 }}>Agentic Security Benchmark & Simulation Lab</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
            Execute real benchmark scenarios across the multi-agent detection, investigation, and deterministic policy pipeline.
          </p>
        </div>

        <button 
          className="btn btn-primary" 
          onClick={runAllScenarios} 
          disabled={running}
          style={{ padding: '12px 22px', fontSize: '14px' }}
        >
          {running ? <RefreshCw size={16} className="spin" /> : <Play size={16} />}
          {running ? 'Executing Pipeline Benchmarks...' : 'Run All 10 Scenarios'}
        </button>
      </div>

      {/* Scenario Grid */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {BENCHMARK_SCENARIOS.map((sc) => {
          const res = results[sc.scenario_id];
          const isCurrentRunning = activeScenarioId === sc.scenario_id;
          const actualAction = res?.action;
          const isMatch = actualAction && actualAction === sc.expected_action;

          return (
            <div key={sc.scenario_id} className="card" style={{ padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: (res || isCurrentRunning) ? '16px' : '0' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ fontWeight: 700, fontFamily: 'monospace', color: 'var(--primary-blue)', backgroundColor: 'var(--primary-blue-light)', padding: '4px 8px', borderRadius: 'var(--radius-sm)', fontSize: '12px' }}>
                    {sc.scenario_id}
                  </div>
                  <div>
                    <h3 style={{ fontSize: '16px', fontWeight: 700 }}>{sc.name}</h3>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Target Expected Policy Action: <strong style={{ color: 'var(--text-main)' }}>{sc.expected_action}</strong></div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {actualAction && (
                    <span className={`badge badge-${actualAction.toLowerCase()}`}>
                      Actual: {actualAction}
                    </span>
                  )}

                  <button 
                    className="btn btn-secondary" 
                    onClick={() => runSingleScenario(sc.scenario_id)}
                    disabled={running || isCurrentRunning}
                    style={{ padding: '8px 14px', fontSize: '13px', gap: '6px' }}
                  >
                    {isCurrentRunning ? <RefreshCw size={14} className="spin" /> : <Play size={14} />}
                    {isCurrentRunning ? 'Analyzing...' : 'Run Scenario'}
                  </button>
                </div>
              </div>

              {/* Live Pipeline Flow Graphic */}
              {(res || isCurrentRunning) && (
                <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '16px', marginTop: '12px', backgroundColor: '#f8fafc', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
                  {/* Step Progress Visual Bar */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', marginBottom: '16px', flexWrap: 'wrap', fontSize: '11px', fontWeight: 700 }}>
                    <div style={{ padding: '6px 10px', borderRadius: 'var(--radius-sm)', background: '#ffffff', border: '1px solid #cbd5e1', color: '#0f172a' }}>
                      1. INPUT RECEIVED
                    </div>
                    <ArrowRight size={14} color="#94a3b8" />
                    <div style={{ padding: '6px 10px', borderRadius: 'var(--radius-sm)', background: res ? '#dbeafe' : '#f1f5f9', border: '1px solid #93c5fd', color: '#1e40af' }}>
                      2. DETECTION ENGINES
                    </div>
                    <ArrowRight size={14} color="#94a3b8" />
                    <div style={{ padding: '6px 10px', borderRadius: 'var(--radius-sm)', background: res ? '#dbeafe' : '#f1f5f9', border: '1px solid #93c5fd', color: '#1e40af' }}>
                      3. MERCHANT & INVESTIGATION AGENTS
                    </div>
                    <ArrowRight size={14} color="#94a3b8" />
                    <div style={{ padding: '6px 10px', borderRadius: 'var(--radius-sm)', background: res ? '#dbeafe' : '#f1f5f9', border: '1px solid #93c5fd', color: '#1e40af' }}>
                      4. EVIDENCE SYNTHESIS
                    </div>
                    <ArrowRight size={14} color="#94a3b8" />
                    <div style={{ padding: '6px 10px', borderRadius: 'var(--radius-sm)', background: res ? (res.action === 'ALLOW' ? '#dcfce7' : res.action === 'BLOCK' ? '#ffe4e6' : '#fef3c7') : '#f1f5f9', border: '1px solid #cbd5e1', color: '#0f172a' }}>
                      5. POLICY & RESPONSE ({res ? res.action : '...'})
                    </div>
                  </div>

                  {res && (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
                      <div>
                        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>Payment Context</div>
                        <div style={{ fontSize: '13px', fontWeight: 600 }}>₹{sc.amount.toLocaleString('en-IN')} to {sc.payee}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px', fontFamily: 'monospace' }}>TXN: {res.transaction_id}</div>
                      </div>

                      <div>
                        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>Synthesized Evidence</div>
                        <div style={{ fontSize: '12px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                          {res.evidence_bundle?.evidence_items?.length > 0 ? (
                            res.evidence_bundle.evidence_items.map((item, idx) => (
                              <div key={idx} style={{ color: '#1d4ed8' }}>• {item.description}</div>
                            ))
                          ) : (
                            <div style={{ color: 'var(--color-allow)' }}>• Clean transaction context baseline.</div>
                          )}
                        </div>
                      </div>

                      <div>
                        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>Benchmark Outcome</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          {isMatch ? (
                            <span style={{ color: 'var(--color-allow)', fontWeight: 700, fontSize: '13px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <CheckCircle size={16} /> 100% Action Match
                            </span>
                          ) : (
                            <span style={{ color: 'var(--color-block)', fontWeight: 700, fontSize: '13px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <AlertTriangle size={16} /> Action Mismatch
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                          {res.customer_explanation?.why || res.reasons?.[0]}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
