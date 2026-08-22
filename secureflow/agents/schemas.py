import uuid
import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator

from secureflow.api.schemas import FORBIDDEN_CREDENTIAL_KEYS

class AgentStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATING = "VALIDATING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    REJECTED = "REJECTED"

class ProposedSecurityAction(str, Enum):
    ALLOW = "ALLOW"
    VERIFY = "VERIFY"
    HOLD = "HOLD"
    BLOCK = "BLOCK"
    INVESTIGATE = "INVESTIGATE"
    NO_ACTION = "NO_ACTION"

class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"
    NONE = "NONE"

class AgentExecutionRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"REQ-{uuid.uuid4().hex[:8].upper()}")
    agent_id: str = Field(..., min_length=1, description="Target Security Agent ID")
    transaction_id: str = Field(..., min_length=1, description="Unique payment transaction ID")
    customer_id: str = Field(..., min_length=1, description="Customer ID")
    amount: float = Field(..., gt=0.0, description="Transaction amount in INR")
    recipient_id: str = Field(..., min_length=1, description="Recipient Account/VPA ID")
    claimed_merchant: Optional[str] = Field(default=None, max_length=250)
    payment_note: Optional[str] = Field(default=None, max_length=1000, description="Untrusted payment text note")
    url: Optional[str] = Field(default=None, max_length=1000, description="Payment destination URL")
    channel: str = Field(default="UPI", max_length=50)
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Isolated execution context data")

    @model_validator(mode="before")
    @classmethod
    def check_security_guardrails(cls, values: Any) -> Any:
        """Security Guardrail: Rejects sensitive credential keys and prompt injection attempts."""
        if isinstance(values, dict):
            # 1. Prohibit sensitive credential fields
            for k in values.keys():
                if str(k).lower() in FORBIDDEN_CREDENTIAL_KEYS:
                    raise ValueError(f"Security Violation: Sensitive credential field '{k}' is prohibited.")
            
            # 2. Treat payment_note strictly as untrusted string
            note = values.get("payment_note")
            if note and isinstance(note, str) and len(note) > 1000:
                values["payment_note"] = note[:1000]
        return values

class AgentEvidenceItem(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"EV-{uuid.uuid4().hex[:8].upper()}")
    source_agent_or_engine: str = Field(..., min_length=1)
    signal_type: str = Field(..., min_length=1)
    severity: SeverityLevel = Field(default=SeverityLevel.LOW)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in finding, isolated from customer UI")
    description: str = Field(..., min_length=1, max_length=1000)
    is_agent_generated: bool = Field(default=True, description="Identifies evidence produced by security agents vs ML models")
    transaction_id: str = Field(..., min_length=1)
    supporting_data: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("confidence")
    @classmethod
    def validate_confidence_range(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"Confidence score {v} must be between 0.0 and 1.0.")
        return v

class AgentFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"FND-{uuid.uuid4().hex[:8].upper()}")
    agent_id: str = Field(..., min_length=1)
    finding_type: str = Field(..., min_length=1)
    severity: SeverityLevel = Field(default=SeverityLevel.LOW)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: str = Field(..., min_length=1, max_length=1000)
    source: str = Field(..., min_length=1)
    explanation: str = Field(..., min_length=1, max_length=1000)
    recommended_next_investigation: Optional[str] = Field(default=None, max_length=500)
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    transaction_id: str = Field(..., min_length=1)

class InvestigationRequest(BaseModel):
    investigation_id: str = Field(default_factory=lambda: f"INV-{uuid.uuid4().hex[:8].upper()}")
    requesting_agent_id: str = Field(..., min_length=1)
    target_agent_id: str = Field(..., min_length=1)
    investigation_reason: str = Field(..., min_length=1, max_length=500)
    target_entity_type: str = Field(..., min_length=1)  # merchant, recipient, url, behavior
    target_entity_id: str = Field(..., min_length=1)
    transaction_id: str = Field(..., min_length=1)
    parameters: Dict[str, Any] = Field(default_factory=dict)

class InvestigationResult(BaseModel):
    investigation_id: str = Field(..., min_length=1)
    requesting_agent_id: str = Field(..., min_length=1)
    target_agent_id: str = Field(..., min_length=1)
    status: AgentStatus = Field(default=AgentStatus.COMPLETED)
    findings: List[AgentFinding] = Field(default_factory=list)
    additional_evidence: List[AgentEvidenceItem] = Field(default_factory=list)
    execution_time_ms: float = Field(default=0.0, ge=0.0)
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

class AgentExecutionContext(BaseModel):
    execution_id: str = Field(default_factory=lambda: f"CTX-{uuid.uuid4().hex[:8].upper()}")
    transaction_id: str = Field(..., min_length=1)
    correlation_id: str = Field(default_factory=lambda: f"CORR-{uuid.uuid4().hex[:8].upper()}")
    start_timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    timeout_ms: int = Field(default=150, gt=0, description="Execution timeout budget in milliseconds")
    max_iterations: int = Field(default=1, ge=1, le=3, description="Maximum investigation recursion depth")
    environment: str = Field(default="PROTOTYPE_SANDBOX")
    feature_flags: Dict[str, bool] = Field(default_factory=dict)

class AgentExecutionResult(BaseModel):
    request_id: str = Field(..., min_length=1)
    agent_id: str = Field(..., min_length=1)
    status: AgentStatus = Field(default=AgentStatus.COMPLETED)
    proposed_action: ProposedSecurityAction = Field(default=ProposedSecurityAction.NO_ACTION)
    findings: List[AgentFinding] = Field(default_factory=list)
    evidence_items: List[AgentEvidenceItem] = Field(default_factory=list)
    error_message: Optional[str] = Field(default=None)
    execution_time_ms: float = Field(default=0.0, ge=0.0)
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
