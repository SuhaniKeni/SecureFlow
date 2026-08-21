# SecureFlow: 5-Minute Evaluation & Video Presentation Script

> **Submission Demo Script for Razorpay AI Builder Internship 2026**

---

## ⏱️ Timed Presentation Script & Flow

### 0:00 — Problem Statement & Context
* **Narrative**: "Hello! Today we are presenting **SecureFlow**, an adaptive payment-security layer for digital payments. Across India's digital payment ecosystem, social engineering scams—like fake electricity disconnection notices, fake courier duty demands, and KYC phishing—trick customers into approving payment transfers themselves. Traditional fraud systems rely on post-facto chargebacks or naive amount limits, missing these attacks or blocking legitimate users."

### 0:40 — Normal Payment Walkthrough (Customer UX)
* **Action**: Open the **Customer Payment UX** tab in the web app. Select **Scenario 1: Legitimate Recurring Electricity Payment** (₹1,450 to BESCOM Official). Click **Pay Now**.
* **Narrative**: "Our core design principle is: *Security should feel invisible.* Here, a routine electricity bill payment to a verified provider completes instantly with the response: **'Payment successful.'** Zero friction, zero technical jargon."

### 1:20 — Attack Scenario Simulation
* **Action**: Select **Scenario 2: Fake Electricity Disconnection Payment Scam** (₹8,742 to `elect-pay-bill.top`). Click **Pay Now**.
* **Narrative**: "Now let's test a social engineering attack. An SMS threatens power disconnection tonight at 9.30pm and directs the victim to a fake pay link."

### 2:00 — SecureFlow Intervention & Protection Action
* **Action**: Observe the red feedback notice modal on screen.
* **Narrative**: "SecureFlow intervenes immediately and blocks the payment: **'This payment could not be completed because the payment destination could not be verified.'** Notice how SecureFlow protects the user with a clear, non-alarming safe next action while hiding raw ML probabilities."

### 2:40 — Risk Operations Dashboard Explanation
* **Action**: Switch to the **Risk Operations Console** tab. Select the top blocked incident.
* **Narrative**: "Next, let's look at the analyst view. The Risk Operations Console structures forensic data around 5 core operational questions:
  1. *WHAT HAPPENED?*: High-risk payment of ₹8,742 flagged.
  2. *WHY?*: Aggregated evidence shows identity mismatch (claimed merchant BESCOM vs recipient personal account), phishing URL, and text urgency.
  3. *WHAT DID SECUREFLOW DO?*: Executed deterministic Policy Rule `RULE_BLOCK_MALICIOUS_DESTINATION_AND_IDENTITY_MISMATCH`.
  4. *RECOMMENDED ACTION*: Confirm payee block.
  5. *SYSTEMIC PREVENTION*: Place domain under security blocklist."

### 3:30 — Attack Scenario Simulator Benchmark
* **Action**: Switch to the **Attack Simulator** tab. Click **Run All 10 Scenarios**.
* **Narrative**: "In our Attack Simulator, we benchmark SecureFlow against 10 controlled attack and legitimate edge-case scenarios—including courier scams, bank KYC phishing, and legitimate high-value laptop purchases. The pipeline achieves **100% action-selection accuracy** across all scenarios."

### 4:10 — Technical Architecture Summary
* **Narrative**: "Behind the scenes, SecureFlow fuses signals from 4 independent detection engines: URL Intelligence (Gradient Boosting), Scam NLP (TF-IDF + Naive Bayes), Customer Behavior Z-scores, and Merchant Consistency. Crucially, **an LLM is NEVER allowed to determine or override financial protection decisions.** Decision rules are 100% deterministic and auditable."

### 4:40 — Quantitative Evaluation & Benchmark Results
* **Narrative**: "In quantitative benchmarking against legacy rule engines, SecureFlow achieves an **$F_1$ score of 1.00**, a **100% Scam Protection Rate**, and reduces false customer blocking to **0.0%**, with a mean execution latency of just **1.15 ms**."

### 5:00 — Conclusion
* **Narrative**: "SecureFlow proves that digital payments can be protected proactively without compromising customer trust or adding unnecessary friction. Thank you!"
