"""Tier 2: bdapps CaaS sandbox payment schemas — field names mirror the real
bdapps CAAS response shapes (see app/integrations/bdapps_caas.py docstring)."""

from pydantic import BaseModel


class BalanceResponse(BaseModel):
    statusCode: str
    statusDetail: str
    chargeableBalance: str | None = None
    accountStatus: str | None = None
    accountType: str | None = None
    paymentInstrumentName: str | None = None


class PaymentInstrument(BaseModel):
    name: str
    type: str


class PaymentInstrumentListResponse(BaseModel):
    statusCode: str
    statusDetail: str
    paymentInstrumentList: list[PaymentInstrument] = []


class CheckoutRequest(BaseModel):
    subscriber_id: str
    amount: float
    purpose: str
    payment_instrument_name: str = "Mobile Account"
    currency: str = "BDT"
    session_id: str | None = None


class CheckoutResponse(BaseModel):
    statusCode: str
    statusDetail: str
    externalTrxId: str
    internalTrxId: str | None = None
    referenceId: str | None = None
    timeStamp: str | None = None
    newBalance: str | None = None


class TransactionOut(BaseModel):
    external_trx_id: str
    internal_trx_id: str
    reference_id: str
    subscriber_id: str
    payment_instrument_name: str
    amount: float
    currency: str
    purpose: str
    status_code: str
    status_detail: str
    created_at: str

    model_config = {"from_attributes": True}
