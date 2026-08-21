import React, { useState } from 'react';
import { Shield, ShieldAlert, ShieldCheck, Clock, Lock, CheckCircle, AlertTriangle, ArrowRight, RefreshCw } from 'lucide-react';

const PRESET_SCENARIOS = [
  {
    id: "SCN-001",
    name: "Normal Utility Bill Payment",
    claimed_merchant: "BESCOM Electricity",
    recipient_id: "RCP-001",
    amount: 1450.00,
    payment_note: "Monthly electricity bill payment ref #400192839",
    url: "https://bescom.co.in/pay",
    type: "Legitimate"
  },
  {
    id: "SCN-002",
    name: "Fake Electricity Disconnection Scam",
    claimed_merchant: "BESCOM Electricity Board",
    recipient_id: "RCP-004",
    amount: 8742.00,
    payment_note: "URGENT: Electricity power line will be disconnected tonight at 9.30pm. Pay overdue bill Rs 8742 immediately",
    url: "http://elect-pay-bill.top/pay",
    type: "Social Engineering Attack"
  },
  {
    id: "SCN-003",
    name: "Fake Bank Security / KYC Phishing",
    claimed_merchant: "State Bank of India",
    recipient_id: "RCP-005",
    amount: 15000.00,
    payment_note: "DEAR CUSTOMER, your account is suspended due to missing KYC. Update immediately or legal action will be taken.",
    url: "http://bank-kyc-update.online/login",
    type: "Phishing Attack"
  },
  {
    id: "SCN-004",
    name: "Fake Courier Duty Payment",
    claimed_merchant: "India Post Express",
    recipient_id: "RCP-006",
    amount: 1499.00,
    payment_note: "COURIER ALERT: International parcel held at customs due to unpaid duty Rs 1499. Pay immediately to release.",
    url: "http://customs-clearance-pay.com/duty",
    type: "Impersonation Attack"
  },
  {
    id: "SCN-007",
    name: "Legitimate Large Purchase (Amazon Pay)",
    claimed_merchant: "Amazon India",
    recipient_id: "RCP-002",
    amount: 85000.00,
    payment_note: "Payment for Apple Laptop order #940182",
    url: "https://amazon.in/checkout/pay",
    type: "Legitimate Unusual"
  }
];

export default function CustomerCheckout() {
  const [customerId, setCustomerId] = useState("CUST-001");
  const [claimedMerchant, setClaimedMerchant] = useState("BESCOM Electricity Board");
  const [recipientId, setRecipientId] = useState("RCP-004");
  const [amount, setAmount] = useState(8742.00);
  const [paymentNote, setPaymentNote] = useState("URGENT: Electricity power line will be disconnected tonight at 9.30pm. Pay overdue bill Rs 8742 immediately");
  const [url, setUrl] = useState("http://elect-pay-bill.top/pay");
  
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState(null);
  const [selectedPreset, setSelectedPreset] = useState("SCN-002");

  const loadPreset = (scenario) => {
    setSelectedPreset(scenario.id);
    setClaimedMerchant(scenario.claimed_merchant);
    setRecipientId(scenario.recipient_id);
    setAmount(scenario.amount);
    setPaymentNote(scenario.payment_note);
    setUrl(scenario.url);
    setResult(null);
  };

  const handlePayNow = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    setResult(null);

    try {
      const response = await fetch('/api/payments/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          customer_id: customerId,
          amount: parseFloat(amount),
          recipient_id: recipientId,
          claimed_merchant: claimedMerchant,
          payment_note: paymentNote,
          url: url,
          channel: "UPI"
        })
      });

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error("Payment submission error:", err);
      // Fallback offline simulation if backend API is not running
      setResult({
        action: "BLOCK",
        customer_explanation: {
          what_happened: "This payment could not be completed because the payment destination could not be verified.",
          why: "The payment destination could not be verified.",
          what_action_was_taken: "BLOCK",
          what_should_happen_next: "Do not proceed with this payment. Contact the payee directly via verified official channels.",
          how_to_prevent_recurrence: "Always initiate bill payments directly inside official provider mobile applications."
        }
      });
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div style={{ maxWidth: '650px', margin: '0 auto' }}>
      {/* Preset Scenario Selector for Demonstration */}
      <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '1.5rem', borderRadius: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-cyan)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Interactive Scenario Sandbox
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Select scenario to test security layer</span>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {PRESET_SCENARIOS.map((sc) => (
            <button
              key={sc.id}
              onClick={() => loadPreset(sc)}
              className="btn-secondary"
              style={{
                fontSize: '0.8rem',
                padding: '0.4rem 0.75rem',
                borderColor: selectedPreset === sc.id ? 'var(--accent-blue)' : 'rgba(255,255,255,0.1)',
                background: selectedPreset === sc.id ? 'rgba(59,130,246,0.15)' : 'transparent',
                color: selectedPreset === sc.id ? '#60a5fa' : 'var(--text-muted)'
              }}
            >
              {sc.name}
            </button>
          ))}
        </div>
      </div>

      {/* Customer Payment Checkout Form */}
      <div className="glass-panel" style={{ padding: '2rem', position: 'relative', overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', borderBottom: '1px solid var(--border-card)', pb: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ background: 'rgba(59,130,246,0.15)', padding: '0.6rem', borderRadius: '12px', color: 'var(--accent-blue)' }}>
              <Lock size={22} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Razorpay Secure Checkout</h2>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Adaptive Payment Protection Layer</p>
            </div>
          </div>
          <span className="badge badge-allow" style={{ fontSize: '0.7rem' }}>
            <Shield Check size={12} style={{ marginRight: '4px' }} /> Encrypted UPI
          </span>
        </div>

        <form onSubmit={handlePayNow}>
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
              Payee / Claimed Merchant
            </label>
            <input
              type="text"
              value={claimedMerchant}
              onChange={(e) => setClaimedMerchant(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid var(--border-card)',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '1rem'
              }}
              required
            />
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
              Payment Amount (INR ₹)
            </label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid var(--border-card)',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '1.25rem',
                fontWeight: 700
              }}
              required
            />
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
              Payment Note / Message
            </label>
            <textarea
              value={paymentNote}
              onChange={(e) => setPaymentNote(e.target.value)}
              rows={2}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid var(--border-card)',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '0.9rem'
              }}
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>
              Attached Destination Link (Optional)
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                background: 'rgba(0,0,0,0.3)',
                border: '1px solid var(--border-card)',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '0.85rem'
              }}
            />
          </div>

          <button
            type="submit"
            disabled={isProcessing}
            className="btn-primary"
            style={{ width: '100%', padding: '1rem', fontSize: '1.1rem' }}
          >
            {isProcessing ? (
              <>
                <RefreshCw size={20} className="animate-spin" /> Securing Transaction...
              </>
            ) : (
              <>
                Pay ₹{parseFloat(amount || 0).toLocaleString('en-IN')} <ArrowRight size={20} />
              </>
            )}
          </button>
        </form>
      </div>

      {/* Customer Protection Action Feedback Modal (Strictly No ML Jargon / Scores) */}
      {result && (
        <div style={{ marginTop: '1.5rem' }}>
          {result.action === 'ALLOW' && (
            <div className="glass-panel" style={{ padding: '1.75rem', borderColor: 'rgba(16, 185, 129, 0.4)', background: 'rgba(6, 78, 59, 0.25)' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <div style={{ background: 'rgba(16, 185, 129, 0.2)', padding: '0.75rem', borderRadius: '50%', color: '#34d399' }}>
                  <CheckCircle size={32} />
                </div>
                <div style={{ flex: 1 }}>
                  <span className="badge badge-allow" style={{ marginBottom: '0.5rem' }}>Payment Successful</span>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#ecfdf5', marginBottom: '0.5rem' }}>
                    Payment successful.
                  </h3>
                  <p style={{ fontSize: '0.9rem', color: '#a7f3d0', marginBottom: '1rem' }}>
                    Your payment of ₹{parseFloat(amount).toLocaleString('en-IN')} to {claimedMerchant} was completed securely.
                  </p>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Next Step: {result.recommended_next_step || "No further action required."}
                  </p>
                </div>
              </div>
            </div>
          )}

          {result.action === 'VERIFY' && (
            <div className="glass-panel" style={{ padding: '1.75rem', borderColor: 'rgba(245, 158, 11, 0.4)', background: 'rgba(120, 53, 15, 0.25)' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <div style={{ background: 'rgba(245, 158, 11, 0.2)', padding: '0.75rem', borderRadius: '50%', color: '#fbbf24' }}>
                  <ShieldCheck size={32} />
                </div>
                <div style={{ flex: 1 }}>
                  <span className="badge badge-verify" style={{ marginBottom: '0.5rem' }}>Verification Required</span>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fffbeb', marginBottom: '0.5rem' }}>
                    We need to verify this payment before it can be completed.
                  </h3>
                  <p style={{ fontSize: '0.9rem', color: '#fde68a', marginBottom: '1rem' }}>
                    {result.customer_explanation?.why || "This payment is to a new or unusual recipient for your account."}
                  </p>
                  <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>
                    <p style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>Recommended Action:</p>
                    <p style={{ fontSize: '0.85rem', color: '#fef3c7' }}>{result.customer_explanation?.what_should_happen_next || "Confirm recipient payment details."}</p>
                  </div>
                  <button className="btn-primary" style={{ background: 'linear-gradient(135deg, #f59e0b, #d97706)' }}>
                    Verify & Proceed
                  </button>
                </div>
              </div>
            </div>
          )}

          {result.action === 'HOLD' && (
            <div className="glass-panel" style={{ padding: '1.75rem', borderColor: 'rgba(59, 130, 246, 0.4)', background: 'rgba(30, 58, 138, 0.25)' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <div style={{ background: 'rgba(59, 130, 246, 0.2)', padding: '0.75rem', borderRadius: '50%', color: '#60a5fa' }}>
                  <Clock size={32} />
                </div>
                <div style={{ flex: 1 }}>
                  <span className="badge badge-hold" style={{ marginBottom: '0.5rem' }}>Under Review</span>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#eff6ff', marginBottom: '0.5rem' }}>
                    This payment is temporarily under review.
                  </h3>
                  <p style={{ fontSize: '0.9rem', color: '#bfdbfe', marginBottom: '1rem' }}>
                    {result.customer_explanation?.why || "Additional security checks are in progress to confirm payee details."}
                  </p>
                  <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>
                    <p style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff' }}>What should happen next:</p>
                    <p style={{ fontSize: '0.85rem', color: '#dbeafe' }}>{result.customer_explanation?.what_should_happen_next || "Verify recipient identity with the payee."}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {result.action === 'BLOCK' && (
            <div className="glass-panel" style={{ padding: '1.75rem', borderColor: 'rgba(239, 68, 68, 0.4)', background: 'rgba(127, 29, 29, 0.3)' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                <div style={{ background: 'rgba(239, 68, 68, 0.2)', padding: '0.75rem', borderRadius: '50%', color: '#f87171' }}>
                  <ShieldAlert size={32} />
                </div>
                <div style={{ flex: 1 }}>
                  <span className="badge badge-block" style={{ marginBottom: '0.5rem' }}>Payment Blocked</span>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fef2f2', marginBottom: '0.5rem' }}>
                    This payment could not be completed because the payment destination could not be verified.
                  </h3>
                  <p style={{ fontSize: '0.9rem', color: '#fca5a5', marginBottom: '1rem' }}>
                    Do not attempt to resend funds to this recipient.
                  </p>
                  <div style={{ background: 'rgba(0,0,0,0.4)', padding: '1rem', borderRadius: '8px', marginBottom: '1rem', borderLeft: '4px solid #ef4444' }}>
                    <p style={{ fontSize: '0.85rem', fontWeight: 600, color: '#fff', marginBottom: '0.25rem' }}>Safe Next Steps:</p>
                    <p style={{ fontSize: '0.85rem', color: '#fecaca' }}>{result.customer_explanation?.what_should_happen_next || "Contact the payee directly via verified official channels."}</p>
                    <p style={{ fontSize: '0.8rem', color: '#f87171', marginTop: '0.5rem' }}>
                      Prevention Tip: {result.customer_explanation?.how_to_prevent_recurrence || "Always initiate utility payments inside official provider applications."}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
