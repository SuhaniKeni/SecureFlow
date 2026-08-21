from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, model_validator

FORBIDDEN_CREDENTIAL_KEYS = {"upi_pin", "card_number", "cvv", "password", "pin", "otp", "secret"}

class PaymentAnalysisRequest(BaseModel):
    customer_id: str = Field(..., json_schema_extra={"example": "CUST-001"}, description="Synthetic Customer ID")
    amount: float = Field(..., gt=0.0, json_schema_extra={"example": 8742.00}, description="Payment transaction amount in INR")
    recipient_id: str = Field(..., json_schema_extra={"example": "RCP-004"}, description="Recipient Account/VPA ID")
    claimed_merchant: Optional[str] = Field(default=None, json_schema_extra={"example": "BESCOM Electricity Board"})
    payment_note: Optional[str] = Field(default=None, json_schema_extra={"example": "URGENT: Electricity disconnected tonight at 9.30pm"})
    url: Optional[str] = Field(default=None, json_schema_extra={"example": "http://elect-pay-bill.top/pay"})
    channel: str = Field(default="UPI", json_schema_extra={"example": "UPI"})

    @model_validator(mode="before")
    @classmethod
    def check_no_sensitive_credentials(cls, values: Any) -> Any:
        """Security Guardrail: Rejects any attempt to send real payment credentials."""
        if isinstance(values, dict):
            for k in values.keys():
                if k.lower() in FORBIDDEN_CREDENTIAL_KEYS:
                    raise ValueError(f"Security Violation: Sensitive payment credential field '{k}' is prohibited.")
        return values

class PaymentSimulationRequest(BaseModel):
    scenario_id: Optional[str] = Field(default=None, json_schema_extra={"example": "SCN-002"})
    customer_id: Optional[str] = Field(default="CUST-001")
    amount: Optional[float] = Field(default=8742.00)
    recipient_id: Optional[str] = Field(default="RCP-004")
    claimed_merchant: Optional[str] = Field(default="BESCOM Electricity")
    payment_note: Optional[str] = Field(default="URGENT: Electricity disconnection notice")
    url: Optional[str] = Field(default="http://elect-pay-bill.top/pay")

class ScenarioRunRequest(BaseModel):
    scenario_id: str = Field(..., json_schema_extra={"example": "SCN-002"}, description="Target scenario benchmark ID to execute")

class PaymentAnalysisResponse(BaseModel):
    transaction_id: str
    action: str  # ALLOW, VERIFY, HOLD, BLOCK
    reasons: List[str]
    customer_explanation: Dict[str, Any]
    ops_explanation: Dict[str, Any]
    evidence_bundle: Dict[str, Any]
    recommended_next_step: str
    prevention_recommendation: str
    audit_trail: Dict[str, Any]

class ProtectionEventSummary(BaseModel):
    event_id: str
    transaction_id: str
    action: str
    evidence: Dict[str, Any]
    explanation: str
    timestamp: str

class MerchantResponse(BaseModel):
    merchant_id: str
    legal_name: str
    brand_name: str
    category: str
    verified_domain: str
    verified_payment_identifier: str
    account_age_days: int
    status: str

class CustomerHistoryResponse(BaseModel):
    customer_id: str
    full_name: str
    email: str
    normal_avg_amount: float
    normal_std_amount: float
    account_age_days: int
    total_transactions: int
    transaction_history: List[Dict[str, Any]]
