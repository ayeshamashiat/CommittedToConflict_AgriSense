"""CRUD for PaymentTransaction rows (Tier 2: bdapps CaaS sandbox receipts)."""

from sqlalchemy.orm import Session as DBSession

from app.db.models import PaymentTransaction


def save_transaction(
    db: DBSession,
    session_id: str | None,
    external_trx_id: str,
    internal_trx_id: str,
    reference_id: str,
    subscriber_id: str,
    payment_instrument_name: str,
    amount: float,
    currency: str,
    purpose: str,
    status_code: str,
    status_detail: str,
) -> PaymentTransaction:
    trx = PaymentTransaction(
        session_id=session_id,
        external_trx_id=external_trx_id,
        internal_trx_id=internal_trx_id,
        reference_id=reference_id,
        subscriber_id=subscriber_id,
        payment_instrument_name=payment_instrument_name,
        amount=amount,
        currency=currency,
        purpose=purpose,
        status_code=status_code,
        status_detail=status_detail,
    )
    db.add(trx)
    db.commit()
    db.refresh(trx)
    return trx


def list_transactions(
    db: DBSession, subscriber_id: str | None = None, session_id: str | None = None, limit: int = 50
) -> list[PaymentTransaction]:
    query = db.query(PaymentTransaction)
    if subscriber_id:
        query = query.filter(PaymentTransaction.subscriber_id == subscriber_id)
    if session_id:
        query = query.filter(PaymentTransaction.session_id == session_id)
    return query.order_by(PaymentTransaction.created_at.desc()).limit(limit).all()
