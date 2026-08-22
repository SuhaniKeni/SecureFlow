import uuid
import datetime
from typing import Optional, List, Dict, Any

from secureflow.agents.base import BaseSecurityAgent
from secureflow.agents.schemas import (
    AgentStatus,
    ProposedSecurityAction,
    SeverityLevel,
    AgentExecutionRequest,
    AgentExecutionResult,
    AgentFinding,
    AgentEvidenceItem,
    AgentExecutionContext,
)
from secureflow.aggregation.evidence_aggregator import EvidenceAggregator

class EvidenceSynthesisAgent(BaseSecurityAgent):
    """Specialist Security Agent for synthesizing multi-engine & multi-agent evidence signals.
    
    STRICT BOUNDARY:
      - Combines evidence from URL Engine, NLP Engine, Behavior Engine, Merchant Agent, and Investigation Agent.
      - Detects evidence convergence, conflict, or incompleteness.
      - Preserves signal provenance and distinguishes model-generated vs agent-generated evidence.
      - MUST NEVER output final financial block decisions directly.
    """

    def __init__(self):
        super().__init__(
            agent_id="evidence_synthesis_agent",
            agent_name="Evidence Synthesis & Case Aggregation Agent",
            version="1.0.0",
            capabilities=["signal_fusion", "conflict_detection", "provenance_preservation", "case_synthesis"]
        )
        self.aggregator = EvidenceAggregator()

    def _analyze(
        self, 
        request: AgentExecutionRequest, 
        context: AgentExecutionContext
    ) -> AgentExecutionResult:
        """Synthesizes all raw and agent-generated evidence into a structured Evidence Bundle."""
        raw_evidence_items: List[Dict[str, Any]] = request.context_data.get("all_evidence", [])
        
        # 1. Deduplicate items by (signal_type, source) while preserving provenance
        deduped_items: List[Dict[str, Any]] = []
        seen_keys = set()
        
        has_high_threat = False
        has_low_clean = False

        for item in raw_evidence_items:
            sig = item.get("signal_type", "unknown")
            src = item.get("source_agent_or_engine") or item.get("source", "unknown")
            key = (sig, src)
            if key not in seen_keys:
                seen_keys.add(key)
                # Ensure is_agent_generated flag is preserved
                is_agent = item.get("is_agent_generated", src.endswith("_agent"))
                item["is_agent_generated"] = is_agent
                deduped_items.append(item)
                
                sev = item.get("severity", "low")
                if sev in ["high", "critical"]:
                    has_high_threat = True
                elif sev in ["low", "info"]:
                    has_low_clean = True

        # 2. Determine Evidence Convergence / Conflict Status
        if len(deduped_items) == 0:
            evidence_status = "INCOMPLETE"
            explanation = "No evidence signals available for synthesis."
        elif has_high_threat and has_low_clean and len(deduped_items) > 1:
            evidence_status = "CONFLICTING"
            explanation = "Signals disagree; high risk indicators coexist with baseline low risk signals. Policy evaluation required."
        elif has_high_threat and len(deduped_items) >= 2:
            evidence_status = "CONVERGING"
            explanation = "Multiple independent engines report converging high threat signals (phishing/scam/mismatch)."
        elif len(deduped_items) == 1:
            evidence_status = "SINGLE_SIGNAL"
            explanation = "Single evidence signal evaluated."
        else:
            evidence_status = "CONVERGING"
            explanation = "Evidence signals converge on low risk normal payment pattern."

        # 3. Overall Severity Calculation
        if any(item.get("severity") in ["high", "critical", SeverityLevel.HIGH, SeverityLevel.CRITICAL] for item in deduped_items):
            overall_severity = SeverityLevel.HIGH
        elif any(item.get("severity") in ["medium", SeverityLevel.MEDIUM] for item in deduped_items):
            overall_severity = SeverityLevel.MEDIUM
        else:
            overall_severity = SeverityLevel.LOW

        has_critical = any(
            item.get("signal_type") in ["merchant_identity_mismatch", "suspicious_destination", "scam_context_detected", "domain_mismatch"]
            for item in deduped_items
        )

        # 4. Construct Agent Evidence Items for Schema Return
        synthesized_evidence_items: List[AgentEvidenceItem] = []
        for d in deduped_items:
            try:
                raw_sev = d.get("severity", "low")
                sev_enum = SeverityLevel[raw_sev.upper()] if isinstance(raw_sev, str) else raw_sev
            except KeyError:
                sev_enum = SeverityLevel.LOW

            conf = float(d.get("confidence", 0.50))
            conf = max(0.0, min(1.0, conf))

            synthesized_evidence_items.append(
                AgentEvidenceItem(
                    evidence_id=d.get("evidence_id") or f"EV-{uuid.uuid4().hex[:8].upper()}",
                    source_agent_or_engine=d.get("source_agent_or_engine") or d.get("source", "evidence_synthesis_agent"),
                    signal_type=d.get("signal_type", "unknown_signal"),
                    severity=sev_enum,
                    confidence=conf,
                    description=d.get("description", "Synthesized evidence signal."),
                    is_agent_generated=bool(d.get("is_agent_generated", False)),
                    transaction_id=request.transaction_id,
                    supporting_data=d.get("supporting_data", {})
                )
            )

        # 5. Create Primary Synthesis Finding
        synthesis_finding = AgentFinding(
            agent_id=self.agent_id,
            finding_type=f"evidence_synthesis_{evidence_status.lower()}",
            severity=overall_severity,
            confidence=0.95,
            evidence=explanation,
            source=self.agent_name,
            explanation=(
                f"Evidence Status: {evidence_status}. Synthesized {len(deduped_items)} items. "
                f"Critical Indicators Present: {has_critical}. Overall Severity: {overall_severity.value}."
            ),
            recommended_next_investigation="Pass synthesized Evidence Bundle to deterministic ProtectionDecisionEngine.",
            transaction_id=request.transaction_id
        )

        # Determine Bounded Action Proposal
        if overall_severity == SeverityLevel.HIGH and has_critical:
            proposed_action = ProposedSecurityAction.BLOCK
        elif overall_severity == SeverityLevel.HIGH:
            proposed_action = ProposedSecurityAction.HOLD
        elif overall_severity == SeverityLevel.MEDIUM:
            proposed_action = ProposedSecurityAction.VERIFY
        else:
            proposed_action = ProposedSecurityAction.ALLOW

        return AgentExecutionResult(
            request_id=request.request_id,
            agent_id=self.agent_id,
            status=AgentStatus.COMPLETED,
            proposed_action=proposed_action,
            findings=[synthesis_finding],
            evidence_items=synthesized_evidence_items
        )

    def format_evidence_bundle(self, result: AgentExecutionResult) -> Dict[str, Any]:
        """Formats AgentExecutionResult into standard EvidenceBundle payload for ProtectionDecisionEngine."""
        items = []
        for item in result.evidence_items:
            items.append({
                "signal_type": item.signal_type,
                "source": item.source_agent_or_engine,
                "description": item.description,
                "severity": item.severity.value.lower(),
                "confidence": item.confidence,
                "is_agent_generated": item.is_agent_generated,
                "supporting_data": item.supporting_data
            })

        overall_sev = "low"
        if any(i["severity"] in ["high", "critical"] for i in items):
            overall_sev = "high"
        elif any(i["severity"] == "medium" for i in items):
            overall_sev = "medium"

        has_critical = any(
            i["signal_type"] in ["merchant_identity_mismatch", "suspicious_destination", "scam_context_detected", "domain_mismatch"]
            for i in items
        )

        return {
            "bundle_id": f"BDL-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "overall_severity": overall_sev,
            "evidence_count": len(items),
            "has_critical_indicators": has_critical,
            "evidence_items": items
        }
