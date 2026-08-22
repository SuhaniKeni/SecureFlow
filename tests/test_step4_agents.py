import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from pydantic import ValidationError

from secureflow.db.models import Base, Transaction, Customer, Recipient, ProtectionEvent
from secureflow.db.synthetic_generator import generate_synthetic_database
from secureflow.agents.schemas import (
    AgentStatus,
    ProposedSecurityAction,
    SeverityLevel,
    AgentExecutionRequest,
    AgentExecutionResult,
)
from secureflow.agents.merchant_agent import MerchantSecurityAgent
from secureflow.agents.investigation_agent import InvestigationAgent
from secureflow.agents.evidence_agent import EvidenceSynthesisAgent
from secureflow.agents.response_agent import SecurityResponseAgent
from secureflow.engines.url_intel_engine import URLIntelligenceEngine
from secureflow.engines.scam_nlp_engine import ScamContextNLPEngine
from secureflow.policy.decision_engine import ProtectionDecisionEngine

@pytest.fixture
def db_session():
    """Provides a seeded in-memory SQLite session for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    generate_synthetic_database(session, seed=42)

    # Ensure CUST-001 has prior history with RCP-001 for SCN-001 ALLOW benchmark test
    c1 = session.query(Customer).filter(Customer.customer_id == "CUST-001").first()
    if c1:
        t_hist = Transaction(
            transaction_id="TXN-HIST-001",
            customer_id="CUST-001",
            recipient_id="RCP-001",
            amount=1450.00,
            status="SUCCESS"
        )
        session.add(t_hist)
        session.commit()

    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

# ==============================================================================
# PART 1: EVIDENCE SYNTHESIS AGENT UNIT TESTS
# ==============================================================================

def test_evidence_agent_converging_evidence():
    """1. Test EvidenceSynthesisAgent with converging threat evidence."""
    agent = EvidenceSynthesisAgent()
    req = AgentExecutionRequest(
        agent_id=agent.agent_id,
        transaction_id="TXN-E-001",
        customer_id="CUST-001",
        amount=8742.00,
        recipient_id="RCP-004",
        context_data={
            "all_evidence": [
                {"signal_type": "phishing_domain", "severity": "high", "source": "url_security_agent"},
                {"signal_type": "scam_context_detected", "severity": "high", "source": "scam_nlp_engine"},
                {"signal_type": "merchant_identity_mismatch", "severity": "high", "source": "merchant_security_agent"}
            ]
        }
    )
    res = agent.execute(req)
    assert res.status == AgentStatus.COMPLETED
    assert res.proposed_action == ProposedSecurityAction.BLOCK
    assert "CONVERGING" in res.findings[0].explanation

def test_evidence_agent_conflicting_evidence():
    """2. Test EvidenceSynthesisAgent with conflicting evidence signals."""
    agent = EvidenceSynthesisAgent()
    req = AgentExecutionRequest(
        agent_id=agent.agent_id,
        transaction_id="TXN-E-002",
        customer_id="CUST-001",
        amount=5000.00,
        recipient_id="RCP-001",
        context_data={
            "all_evidence": [
                {"signal_type": "scam_context_detected", "severity": "high", "source": "scam_nlp_engine"},
                {"signal_type": "merchant_identity_match", "severity": "low", "source": "merchant_security_agent"}
            ]
        }
    )
    res = agent.execute(req)
    assert res.status == AgentStatus.COMPLETED
    assert "CONFLICTING" in res.findings[0].explanation

def test_evidence_agent_incomplete_evidence():
    """3. Test EvidenceSynthesisAgent with empty/incomplete evidence."""
    agent = EvidenceSynthesisAgent()
    req = AgentExecutionRequest(
        agent_id=agent.agent_id,
        transaction_id="TXN-E-003",
        customer_id="CUST-001",
        amount=500.00,
        recipient_id="RCP-001",
        context_data={"all_evidence": []}
    )
    res = agent.execute(req)
    assert res.status == AgentStatus.COMPLETED
    assert "INCOMPLETE" in res.findings[0].explanation

def test_evidence_agent_provenance_preservation():
    """5. Test EvidenceSynthesisAgent preserves signal provenance and is_agent_generated flag."""
    agent = EvidenceSynthesisAgent()
    req = AgentExecutionRequest(
        agent_id=agent.agent_id,
        transaction_id="TXN-E-005",
        customer_id="CUST-001",
        amount=1450.00,
        recipient_id="RCP-001",
        context_data={
            "all_evidence": [
                {"signal_type": "merchant_identity_match", "severity": "low", "source": "merchant_security_agent", "is_agent_generated": True}
            ]
        }
    )
    res = agent.execute(req)
    assert res.evidence_items[0].is_agent_generated is True
    assert res.evidence_items[0].source_agent_or_engine == "merchant_security_agent"

def test_evidence_agent_format_evidence_bundle():
    """Format evidence bundle utility test."""
    agent = EvidenceSynthesisAgent()
    req = AgentExecutionRequest(
        agent_id=agent.agent_id,
        transaction_id="TXN-E-006",
        customer_id="CUST-001",
        amount=8742.00,
        recipient_id="RCP-004",
        context_data={
            "all_evidence": [
                {"signal_type": "phishing_domain", "severity": "high", "source": "url_security_agent"}
            ]
        }
    )
    res = agent.execute(req)
    bundle = agent.format_evidence_bundle(res)
    assert bundle["bundle_id"].startswith("BDL-")
    assert bundle["overall_severity"] == "high"

# ==============================================================================
# PART 2: SECURITY RESPONSE AGENT UNIT TESTS
# ==============================================================================

def test_response_agent_allow():
    """1. Test SecurityResponseAgent for ALLOW decision."""
    agent = SecurityResponseAgent()
    req = AgentExecutionRequest(
        agent_id=agent.agent_id,
        transaction_id="TXN-R-001",
        customer_id="CUST-001",
        amount=1450.00,
        recipient_id="RCP-001",
        context_data={"policy_decision": {"action": "ALLOW", "reasons": ["Normal payment context."]}}
    )
    res = agent.execute(req)
    assert res.status == AgentStatus.COMPLETED
    assert res.proposed_action == ProposedSecurityAction.ALLOW
    assert res.evidence_items[0].supporting_data["response_status"] == "PERMITTED"

def test_response_agent_verify():
    """2. Test SecurityResponseAgent for VERIFY decision."""
    agent = SecurityResponseAgent()
    req = AgentExecutionRequest(
        agent_id=agent.agent_id,
        transaction_id="TXN-R-002",
        customer_id="CUST-001",
        amount=3200.00,
        recipient_id="RCP-003",
        context_data={"policy_decision": {"action": "VERIFY", "reasons": ["Unverified recipient."]}}
    )
    res = agent.execute(req)
    assert res.status == AgentStatus.COMPLETED
    assert res.proposed_action == ProposedSecurityAction.VERIFY
    assert res.evidence_items[0].supporting_data["response_status"] == "VERIFICATION_REQUIRED"

def test_response_agent_hold(db_session):
    """3. Test SecurityResponseAgent for HOLD decision creates Protection Event."""
    agent = SecurityResponseAgent(db_session=db_session)
    req = AgentExecutionRequest(
        agent_id=agent.agent_id,
        transaction_id="TXN-R-003",
        customer_id="CUST-001",
        amount=5000.00,
        recipient_id="RCP-004",
        context_data={"policy_decision": {"action": "HOLD", "reasons": ["Merchant identity mismatch."]}}
    )
    res = agent.execute(req)
    assert res.status == AgentStatus.COMPLETED
    assert res.proposed_action == ProposedSecurityAction.HOLD
    assert res.evidence_items[0].supporting_data["protection_event_created"] is True

def test_response_agent_block(db_session):
    """4. Test SecurityResponseAgent for BLOCK decision stops payment & creates Protection Event."""
    agent = SecurityResponseAgent(db_session=db_session)
    req = AgentExecutionRequest(
        agent_id=agent.agent_id,
        transaction_id="TXN-R-004",
        customer_id="CUST-001",
        amount=8742.00,
        recipient_id="RCP-004",
        context_data={"policy_decision": {"action": "BLOCK", "reasons": ["Malicious phishing domain and merchant mismatch."]}}
    )
    res = agent.execute(req)
    assert res.status == AgentStatus.COMPLETED
    assert res.proposed_action == ProposedSecurityAction.BLOCK
    assert res.evidence_items[0].supporting_data["response_status"] == "PAYMENT_BLOCKED"

def test_response_agent_missing_decision_rejection():
    """5. Test missing policy decision is rejected cleanly."""
    agent = SecurityResponseAgent()
    req = AgentExecutionRequest(
        agent_id=agent.agent_id,
        transaction_id="TXN-R-005",
        customer_id="CUST-001",
        amount=100.00,
        recipient_id="RCP-001",
        context_data={"policy_decision": None}
    )
    res = agent.execute(req)
    assert res.status == AgentStatus.FAILED
    assert "requires a valid ProtectionDecisionEngine policy decision" in res.error_message

def test_response_agent_policy_override_rejection(db_session):
    """7. Test Response Agent rejects attempted policy override (Policy decision ALWAYS wins)."""
    agent = SecurityResponseAgent(db_session=db_session)
    req = AgentExecutionRequest(
        agent_id=agent.agent_id,
        transaction_id="TXN-R-007",
        customer_id="CUST-001",
        amount=8742.00,
        recipient_id="RCP-004",
        context_data={
            "policy_decision": {"action": "BLOCK", "reasons": ["Phishing scam"]},
            "attempted_agent_override": "ALLOW"  # Attempted override
        }
    )
    res = agent.execute(req)
    # Policy BLOCK MUST be enforced despite attempted override
    assert res.proposed_action == ProposedSecurityAction.BLOCK
    assert res.evidence_items[0].supporting_data["response_status"] == "PAYMENT_BLOCKED"

def test_response_agent_payment_execution_prohibition():
    """8. Test Response Agent execute_payment() raises PermissionError."""
    agent = SecurityResponseAgent()
    with pytest.raises(PermissionError) as exc_info:
        agent.execute_payment()
    assert "strictly prohibited from executing financial transactions" in str(exc_info.value)

# ==============================================================================
# PART 3: END-TO-END INTEGRATION DEMO SCENARIOS
# ==============================================================================

def test_demo_1_safe_payment_pipeline(db_session):
    """DEMO 1: Safe Payment (Legitimate BESCOM) -> Full Agent Pipeline -> ALLOW -> Response PERMITTED."""
    merchant_agent = MerchantSecurityAgent(db_session=db_session)
    inv_agent = InvestigationAgent(db_session=db_session)
    ev_agent = EvidenceSynthesisAgent()
    policy_engine = ProtectionDecisionEngine()
    resp_agent = SecurityResponseAgent(db_session=db_session)

    # 1. Merchant Agent
    m_req = AgentExecutionRequest(
        agent_id=merchant_agent.agent_id,
        transaction_id="DEMO-1",
        customer_id="CUST-001",
        amount=1450.00,
        recipient_id="RCP-001",
        claimed_merchant="BESCOM Electricity",
        url="https://bescom.co.in/pay"
    )
    m_res = merchant_agent.execute(m_req)

    # 2. Investigation Agent
    inv_req = AgentExecutionRequest(
        agent_id=inv_agent.agent_id,
        transaction_id="DEMO-1",
        customer_id="CUST-001",
        amount=1450.00,
        recipient_id="RCP-001",
        context_data={"initial_evidence": [e.model_dump() for e in m_res.evidence_items]}
    )
    inv_res = inv_agent.execute(inv_req)

    # 3. Evidence Synthesis Agent
    all_evidence = [e.model_dump() for e in m_res.evidence_items] + [e.model_dump() for e in inv_res.evidence_items]
    e_req = AgentExecutionRequest(
        agent_id=ev_agent.agent_id,
        transaction_id="DEMO-1",
        customer_id="CUST-001",
        amount=1450.00,
        recipient_id="RCP-001",
        context_data={"all_evidence": all_evidence}
    )
    e_res = ev_agent.execute(e_req)
    evidence_bundle = ev_agent.format_evidence_bundle(e_res)

    # 4. Deterministic Policy Decision Engine
    decision = policy_engine.evaluate_protection_policy(evidence_bundle)
    assert decision["action"] == "ALLOW"

    # 5. Security Response Agent
    r_req = AgentExecutionRequest(
        agent_id=resp_agent.agent_id,
        transaction_id="DEMO-1",
        customer_id="CUST-001",
        amount=1450.00,
        recipient_id="RCP-001",
        context_data={"policy_decision": decision}
    )
    r_res = resp_agent.execute(r_req)

    assert r_res.proposed_action == ProposedSecurityAction.ALLOW
    assert r_res.evidence_items[0].supporting_data["response_status"] == "PERMITTED"

def test_demo_2_obvious_scam_pipeline(db_session):
    """DEMO 2: Obvious Scam (Fake BESCOM) -> Full Agent Pipeline -> BLOCK -> Response Stops Payment."""
    url_engine = URLIntelligenceEngine()
    nlp_engine = ScamContextNLPEngine()
    merchant_agent = MerchantSecurityAgent(db_session=db_session)
    inv_agent = InvestigationAgent(db_session=db_session)
    ev_agent = EvidenceSynthesisAgent()
    policy_engine = ProtectionDecisionEngine()
    resp_agent = SecurityResponseAgent(db_session=db_session)

    # 1. Detection Engines & Specialist Agents
    url_ev = url_engine.analyze("http://elect-pay-bill.top/pay")
    nlp_ev = nlp_engine.analyze("URGENT: Disconnection notice Rs 8742", claimed_merchant="BESCOM Electricity Board")
    
    m_req = AgentExecutionRequest(
        agent_id=merchant_agent.agent_id,
        transaction_id="DEMO-2",
        customer_id="CUST-001",
        amount=8742.00,
        recipient_id="RCP-004",
        claimed_merchant="BESCOM Electricity Board",
        url="http://elect-pay-bill.top/pay"
    )
    m_res = merchant_agent.execute(m_req)

    initial_ev = [
        {"signal_type": url_ev["signal"], "severity": url_ev["severity"], "source": "url_security_agent"},
        {"signal_type": nlp_ev["signal"], "severity": nlp_ev["severity"], "source": "scam_nlp_engine"}
    ] + [e.model_dump() for e in m_res.evidence_items]

    inv_req = AgentExecutionRequest(
        agent_id=inv_agent.agent_id,
        transaction_id="DEMO-2",
        customer_id="CUST-001",
        amount=8742.00,
        recipient_id="RCP-004",
        context_data={"initial_evidence": initial_ev}
    )
    inv_res = inv_agent.execute(inv_req)

    all_evidence = initial_ev + [e.model_dump() for e in inv_res.evidence_items]

    # 2. Evidence Synthesis Agent
    e_req = AgentExecutionRequest(
        agent_id=ev_agent.agent_id,
        transaction_id="DEMO-2",
        customer_id="CUST-001",
        amount=8742.00,
        recipient_id="RCP-004",
        context_data={"all_evidence": all_evidence}
    )
    e_res = ev_agent.execute(e_req)
    evidence_bundle = ev_agent.format_evidence_bundle(e_res)

    # 3. Deterministic ProtectionDecisionEngine
    decision = policy_engine.evaluate_protection_policy(evidence_bundle)
    assert decision["action"] == "BLOCK"

    # 4. Security Response Agent
    r_req = AgentExecutionRequest(
        agent_id=resp_agent.agent_id,
        transaction_id="DEMO-2",
        customer_id="CUST-001",
        amount=8742.00,
        recipient_id="RCP-004",
        context_data={"policy_decision": decision}
    )
    r_res = resp_agent.execute(r_req)

    assert r_res.proposed_action == ProposedSecurityAction.BLOCK
    assert r_res.evidence_items[0].supporting_data["response_status"] == "PAYMENT_BLOCKED"
    assert r_res.evidence_items[0].supporting_data["protection_event_created"] is True

def test_demo_3_ambiguous_payment_pipeline(db_session):
    """DEMO 3: Ambiguous Payment (₹85,000 New Recipient) -> Investigation Agent triggers tools -> Policy VERIFY -> Response Action."""
    merchant_agent = MerchantSecurityAgent(db_session=db_session)
    inv_agent = InvestigationAgent(db_session=db_session)
    ev_agent = EvidenceSynthesisAgent()
    policy_engine = ProtectionDecisionEngine()
    resp_agent = SecurityResponseAgent(db_session=db_session)

    m_req = AgentExecutionRequest(
        agent_id=merchant_agent.agent_id,
        transaction_id="DEMO-3",
        customer_id="CUST-002",
        amount=85000.00,
        recipient_id="RCP-004",  # Unverified recipient account
        claimed_merchant="Local Hardware Store"
    )
    m_res = merchant_agent.execute(m_req)

    inv_req = AgentExecutionRequest(
        agent_id=inv_agent.agent_id,
        transaction_id="DEMO-3",
        customer_id="CUST-002",
        amount=85000.00,
        recipient_id="RCP-004",
        context_data={"initial_evidence": [e.model_dump() for e in m_res.evidence_items]}
    )
    inv_res = inv_agent.execute(inv_req)

    all_evidence = [e.model_dump() for e in m_res.evidence_items] + [e.model_dump() for e in inv_res.evidence_items]
    
    e_req = AgentExecutionRequest(
        agent_id=ev_agent.agent_id,
        transaction_id="DEMO-3",
        customer_id="CUST-002",
        amount=85000.00,
        recipient_id="RCP-004",
        context_data={"all_evidence": all_evidence}
    )
    e_res = ev_agent.execute(e_req)
    evidence_bundle = ev_agent.format_evidence_bundle(e_res)

    decision = policy_engine.evaluate_protection_policy(evidence_bundle)
    assert decision["action"] in ["VERIFY", "HOLD"]

    r_req = AgentExecutionRequest(
        agent_id=resp_agent.agent_id,
        transaction_id="DEMO-3",
        customer_id="CUST-002",
        amount=85000.00,
        recipient_id="RCP-004",
        context_data={"policy_decision": decision}
    )
    r_res = resp_agent.execute(r_req)

    assert r_res.proposed_action in [ProposedSecurityAction.VERIFY, ProposedSecurityAction.HOLD]

def test_demo_4_agent_response_operational_action(db_session):
    """DEMO 4: Agent Response Operational Action -> BLOCK decision -> Payment stopped, Protection Event created in SQLite DB."""
    policy_engine = ProtectionDecisionEngine()
    resp_agent = SecurityResponseAgent(db_session=db_session)

    # Malicious evidence bundle
    mock_bundle = {
        "bundle_id": "BDL-MOCK-001",
        "timestamp": "2026-08-22T12:00:00Z",
        "overall_severity": "high",
        "has_critical_indicators": True,
        "evidence_items": [
            {"signal_type": "merchant_identity_mismatch", "severity": "high", "description": "Claimed merchant mismatch"},
            {"signal_type": "suspicious_destination", "severity": "high", "description": "Phishing URL"},
            {"signal_type": "scam_context_detected", "severity": "high", "description": "Scam urgency text"}
        ]
    }
    decision = policy_engine.evaluate_protection_policy(mock_bundle)
    assert decision["action"] == "BLOCK"

    req = AgentExecutionRequest(
        agent_id=resp_agent.agent_id,
        transaction_id="DEMO-4-TXN",
        customer_id="CUST-001",
        amount=8742.00,
        recipient_id="RCP-004",
        claimed_merchant="BESCOM Electricity Board",
        context_data={"policy_decision": decision}
    )
    res = resp_agent.execute(req)

    # Operational Response Verification:
    # 1. Proposed action matches decision BLOCK
    assert res.proposed_action == ProposedSecurityAction.BLOCK
    # 2. Payment stopped
    assert res.evidence_items[0].supporting_data["response_status"] == "PAYMENT_BLOCKED"
    # 3. Protection Event persisted in SQLite DB
    assert res.evidence_items[0].supporting_data["protection_event_created"] is True
    
    evt_in_db = db_session.query(ProtectionEvent).filter(ProtectionEvent.transaction_id == "DEMO-4-TXN").first()
    assert evt_in_db is not None
    assert evt_in_db.action == "BLOCK"
