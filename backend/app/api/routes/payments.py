"""Tier 2: bdapps CaaS (Charging as a Service) sandbox integration —
checkout, operator balance query, and receipt history for marketplace
purchases. See app/integrations/bdapps_caas.py for what's real vs simulated.

Standalone endpoints (same reasoning as /marketplace and /simulate): a
farmer checking out for a specific supplier's offer is initiated from the
Marketplace page on demand, not part of the core intake -> recommend chat flow.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_db
from app.db.repositories.payment_repo import list_transactions, save_transaction
from app.integrations import bdapps_caas
from app.schemas.payment import (
    BalanceResponse,
    CheckoutRequest,
    CheckoutResponse,
    PaymentInstrumentListResponse,
    TransactionOut,
)

router = APIRouter(tags=["payments"])


@router.get("/payments/balance", response_model=BalanceResponse)
def get_balance(
    subscriber_id: str = Query(...),
    payment_instrument_name: str = Query(default="Mobile Account"),
    db: DBSession = Depends(get_db),
) -> BalanceResponse:
    result = bdapps_caas.query_balance(db, subscriber_id, payment_instrument_name)
    return BalanceResponse(**result)


@router.get("/payments/instruments", response_model=PaymentInstrumentListResponse)
def get_instruments(
    subscriber_id: str = Query(...),
    type: str = Query(default="all"),
    db: DBSession = Depends(get_db),
) -> PaymentInstrumentListResponse:
    result = bdapps_caas.get_payment_instrument_list(db, subscriber_id, type)
    return PaymentInstrumentListResponse(**result)


@router.post("/payments/checkout", response_model=CheckoutResponse)
def checkout(payload: CheckoutRequest, db: DBSession = Depends(get_db)) -> CheckoutResponse:
    external_trx_id = uuid.uuid4().hex[:12]
    result = bdapps_caas.direct_debit(
        db,
        external_trx_id=external_trx_id,
        subscriber_id=payload.subscriber_id,
        amount=payload.amount,
        payment_instrument_name=payload.payment_instrument_name,
        currency=payload.currency,
    )

    save_transaction(
        db,
        session_id=payload.session_id,
        external_trx_id=result["externalTrxId"],
        internal_trx_id=result.get("internalTrxId", ""),
        reference_id=result.get("referenceId", ""),
        subscriber_id=payload.subscriber_id,
        payment_instrument_name=payload.payment_instrument_name,
        amount=payload.amount,
        currency=payload.currency,
        purpose=payload.purpose,
        status_code=result["statusCode"],
        status_detail=result["statusDetail"],
    )

    return CheckoutResponse(**result)


@router.get("/payments/history", response_model=list[TransactionOut])
def get_history(
    subscriber_id: str | None = Query(default=None),
    session_id: str | None = Query(default=None),
    db: DBSession = Depends(get_db),
) -> list[TransactionOut]:
    rows = list_transactions(db, subscriber_id=subscriber_id, session_id=session_id)
    return [
        TransactionOut(
            external_trx_id=r.external_trx_id,
            internal_trx_id=r.internal_trx_id,
            reference_id=r.reference_id,
            subscriber_id=r.subscriber_id,
            payment_instrument_name=r.payment_instrument_name,
            amount=r.amount,
            currency=r.currency,
            purpose=r.purpose,
            status_code=r.status_code,
            status_detail=r.status_detail,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]
