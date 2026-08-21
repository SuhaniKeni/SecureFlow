import React, { useState } from 'react';
import { ShieldCheck, Lock, AlertCircle, CheckCircle, Clock, XCircle, ArrowRight } from 'lucide-react';

const PRESET_SCENARIOS = [
  {
    label: "Legitimate Electricity Bill (₹1,450)",
    customer_id: "CUST-001",
    amount: 1450.00,
    recipient_id: "RCP-001",
    claimed_merchant: "BESCOM Electricity",
    payment_note: "Monthly electricity bill payment ref #10492",
    url: "https://bescom.co.in/pay"
  },
  {
    label: "Fake Electricity Disconnection Scam (₹8,742)",
    customer_id: "CUST-001",
    amount: 8742.00,
    recipient_id: "RCP-004",
    claimed_merchant: "BESCOM Electricity Board",
    payment_note: "URGENT: Electricity power line will be disconnected tonight at 9.30pm. Pay overdue bill Rs 8742 immediately",
    url: "http://elect-pay-bill.top/pay"
  },
  {
    label: "Legitimate High-Value Purchase (₹85,000)",
    customer_id: "CUST-001",
    amount: 85000.00,
    recipient_id: "RCP-002",
    claimed_merchant: "Amazon India",
    payment_note: "Payment for laptop order #94012",
    url: "https://amazon.in/checkout/pay"
  }
];

export default function CustomerCheckout() {
  const [formData, setFormData] = useState({
    customer_id: 'CUST-001',
    amount: '1450.00',
    recipient_id: 'RCP-001',
    claimed_merchant: 'BESCOM Electricity',
    payment_note: 'Monthly electricity bill payment ref #10492',
    url: 'https://bescom.co.in/pay',
    channel: 'UPI'
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSelectPreset = (e) => {
    const idx = e.target.value;
    if (idx === "") return;
    const s = PRESET_SCENARIOS[idx];
    setFormData({
      customer_id: s.customer_id,
      amount: String(s.amount),
      recipient_id: s.recipient_id,
      claimed_merchant: s.claimed_merchant,
      payment_note: s.payment_note,
      url: s.url,
      channel: 'UPI'
    });
    setResult(null);
  };

  const handlePayNow = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const res = await fetch('/api/payments/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_id: formData.customer_id,
          amount: parseFloat(formData.amount),
          recipient_id: formData.recipient_id,
          claimed_merchant: formData.claimed_merchant,
          payment_note: formData.payment_note,
          url: formData.url,
          channel: formData.channel
        })
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      alert("Payment processing failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '680px', margin: '0 auto' }}>
      <div className="card" style={{ boxShadow: 'var(--shadow-md)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', paddingBottom: '16px', borderBottom: '1px solid var(--border-color)' }}>
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--primary-blue)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Razorpay Checkout Demo</div>
            <h2 style={{ fontSize: '20px', fontWeight: 700, letterSpacing: '-0.02em' }}>Complete Your Payment</h2>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-muted)' }}>
            <Lock size={14} color="#059669" />
            256-Bit Encrypted
          </div>
        </div>

        {/* Preset Selector */}
        <div className="form-group">
          <label className="form-label">Load Preset Scenario</label>
          <select className="form-select" onChange={handleSelectPreset} defaultValue="">
            <option value="" disabled>-- Select a Payment Preset --</option>
            {PRESET_SCENARIOS.map((s, idx) => (
              <option key={idx} value={idx}>{s.label}</option>
            ))}
          </select>
        </div>

        <form onSubmit={handlePayNow}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Customer ID</label>
              <input 
                className="form-input"
                type="text" 
                value={formData.customer_id}
                onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                required 
              />
            </div>

            <div className="form-group">
              <label className="form-label">Amount (INR)</label>
              <input 
                className="form-input"
                type="number" 
                step="0.01"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                required 
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label className="form-label">Claimed Merchant</label>
              <input 
                className="form-input"
                type="text" 
                value={formData.claimed_merchant}
                onChange={(e) => setFormData({ ...formData, claimed_merchant: e.target.value })}
                required 
              />
            </div>

            <div className="form-group">
              <label className="form-label">Recipient VPA / Account</label>
              <input 
                className="form-input"
                type="text" 
                value={formData.recipient_id}
                onChange={(e) => setFormData({ ...formData, recipient_id: e.target.value })}
                required 
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Payment Note / Request Message</label>
            <input 
              className="form-input"
              type="text" 
              value={formData.payment_note}
              onChange={(e) => setFormData({ ...formData, payment_note: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Payment URL / Destination Link</label>
            <input 
              className="form-input"
              type="url" 
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', padding: '14px', marginTop: '8px', fontSize: '15px' }}
            disabled={loading}
          >
            {loading ? 'Evaluating Protection Rules...' : `Pay ₹${parseFloat(formData.amount || 0).toLocaleString('en-IN')}`}
          </button>
        </form>

        {/* Customer Result UX Modal / Panel */}
        {result && (
          <div style={{ marginTop: '24px', padding: '20px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', backgroundColor: result.action === 'ALLOW' ? 'var(--bg-allow)' : result.action === 'VERIFY' ? 'var(--bg-verify)' : result.action === 'HOLD' ? 'var(--bg-hold)' : 'var(--bg-block)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
              {result.action === 'ALLOW' && <CheckCircle size={28} color="var(--color-allow)" />}
              {result.action === 'VERIFY' && <ShieldCheck size={28} color="var(--color-verify)" />}
              {result.action === 'HOLD' && <Clock size={28} color="var(--color-hold)" />}
              {result.action === 'BLOCK' && <XCircle size={28} color="var(--color-block)" />}
              
              <div>
                <div style={{ fontSize: '16px', fontWeight: 700 }}>
                  {result.customer_explanation?.message || result.action}
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                  Transaction ID: {result.transaction_id}
                </div>
              </div>
            </div>

            <div style={{ fontSize: '14px', marginBottom: '12px', lineHeight: 1.5 }}>
              {result.customer_explanation?.details}
            </div>

            <div style={{ padding: '12px', backgroundColor: '#ffffff', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', fontSize: '13px' }}>
              <span style={{ fontWeight: 600 }}>Safe Recommended Action:</span> {result.recommended_next_step}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
