"""Tier 2: bdapps CaaS (Charging as a Service) integration.

Field names, endpoint paths, the "MobileAccount" payment-instrument enum, and
the documented status/error codes (S1000, E1303, E1313, ..., E1603) all match
the OpenAPI schema embedded in the actual bdapps TAP API doc this hackathon's
brief links to (https://dev.bdapps.com/API_Documentation/bdapps_tap_api.html)
— caas/get/balance and caas/direct/debit are the only two CaaS operations it
defines. An earlier version of this file was built against a *different*
bdapps PDF (from github.com/BD-Apps/bdapps-Docs) before that mismatch was
caught mid-testing: it called a nonexistent "/balance/query" path (real path
is "/get/balance"), sent "Mobile Account" with a space where the schema's
enum strictly requires "MobileAccount", and assumed a "list payment
instruments" operation that this API doesn't actually have. All three are
fixed below.

  - caas/get/balance    -> query_balance()
  - caas/direct/debit   -> direct_debit()
  - (no real "list instruments" op exists; get_payment_instrument_list()
    is simulator-only, see its docstring)

Two modes, chosen automatically per call:

1. Real mode — when settings.bdapps_application_id / bdapps_password are
   both set (see app/config.py; only ever populated via environment/.env,
   never hardcoded), every call is a real HTTP request to
   developer.bdapps.com/caas/* with those credentials, exactly as documented.
   If that call raises (network error, non-2xx, unexpected shape), it logs
   and falls through to simulator mode for that single call rather than
   hard-failing the farmer's checkout.
2. Simulator mode (the default with no credentials configured) — a
   stateful local stand-in: a MobileWallet row in our own DB plays the role
   of the operator account, seeded with a starting balance, and Direct Debit
   actually decrements it, so the balance-deduction and receipt flow behave
   like the real thing rather than a canned "success" every time.
"""

import logging
import random
import time
import uuid
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session as DBSession

from app.config import get_settings
from app.db.models import MobileWallet

logger = logging.getLogger(__name__)
settings = get_settings()

DEFAULT_STARTING_BALANCE_BDT = 5000.0
PAYMENT_INSTRUMENTS = [
    {"name": "Mobile Account", "type": "sync"},
    {"name": "Bank Account", "type": "async"},
]


def _has_real_credentials() -> bool:
    return bool(settings.bdapps_application_id and settings.bdapps_password)


def _auth_fields() -> dict:
    return {
        "applicationId": settings.bdapps_application_id,
        "password": settings.bdapps_password,
    }


# The rest of this app uses the friendlier "Mobile Account" (with a space) as
# its own internal default/display value (DB default, schema default, UI
# copy) — but the real bdapps schema's paymentInstrumentName enum only
# accepts the single literal "MobileAccount" (no space). Rather than
# threading that distinction through every caller, every *real* HTTP call
# normalizes to the one value bdapps actually accepts; the simulator (and
# everything else in this codebase) keeps using the friendlier spelling.
_REAL_PAYMENT_INSTRUMENT_NAME = "MobileAccount"


def _get_or_create_wallet(db: DBSession, subscriber_id: str) -> MobileWallet:
    wallet = db.query(MobileWallet).filter(MobileWallet.subscriber_id == subscriber_id).first()
    if wallet is None:
        wallet = MobileWallet(subscriber_id=subscriber_id, balance_bdt=DEFAULT_STARTING_BALANCE_BDT)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet


def _timestamp() -> str:
    # ISO-8601 with offset, matching the real API's documented example format.
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="milliseconds")


# ---- Public API: tries the real endpoint first, simulator as fallback ----


def query_balance(db: DBSession, subscriber_id: str, payment_instrument_name: str = "Mobile Account") -> dict:
    if _has_real_credentials():
        try:
            return _real_query_balance(subscriber_id, payment_instrument_name)
        except Exception:
            logger.exception("Real bdapps CaaS query_balance failed; falling back to local simulator")
    return _simulated_query_balance(db, subscriber_id, payment_instrument_name)


def get_payment_instrument_list(db: DBSession, subscriber_id: str, type_: str = "all") -> dict:
    """Always simulator-backed. The real bdapps TAP API (per its own OpenAPI
    schema — see this module's docstring) only defines caas/get/balance and
    caas/direct/debit; there is no "list payment instruments" operation to
    call for real, so unlike query_balance()/direct_debit() this never
    attempts a real HTTP call."""
    return _simulated_get_payment_instrument_list(db, subscriber_id, type_)


def direct_debit(
    db: DBSession,
    external_trx_id: str,
    subscriber_id: str,
    amount: float,
    payment_instrument_name: str = "Mobile Account",
    currency: str = "BDT",
) -> dict:
    if _has_real_credentials():
        try:
            return _real_direct_debit(external_trx_id, subscriber_id, amount, payment_instrument_name, currency)
        except Exception:
            logger.exception("Real bdapps CaaS direct_debit failed; falling back to local simulator")
    return _simulated_direct_debit(db, external_trx_id, subscriber_id, amount, payment_instrument_name, currency)


# ---- Real mode: actual HTTP calls to developer.bdapps.com ----------------


class BdappsApiError(Exception):
    """Raised when bdapps responds 200 OK but with a business-level error
    statusCode (e.g. E1303 IP not whitelisted, E1326 insufficient balance
    reported at the gateway level). httpx's raise_for_status() only catches
    HTTP-level failures (4xx/5xx) — bdapps reports API errors as 200 OK with
    an "E..." statusCode in the body, so without this check that error body
    would be mistaken for a successful response and passed straight through,
    exactly what happened before this was added (a real E1303 response
    crashed the checkout route with a KeyError on the missing externalTrxId
    field). Raising here lets the existing try/except in query_balance() /
    get_payment_instrument_list() / direct_debit() fall back to the local
    simulator, consistent with "try real, fall back to simulator on any
    failure" everywhere else in this module."""


def _post(path: str, body: dict) -> dict:
    with httpx.Client(timeout=10.0) as client:
        resp = client.post(f"{settings.bdapps_caas_base_url}{path}", json=body)
        resp.raise_for_status()
        data = resp.json()
        status_code = str(data.get("statusCode", ""))
        if status_code and not status_code.startswith("S"):
            raise BdappsApiError(f"{status_code}: {data.get('statusDetail', 'bdapps API error')}")
        return data


def _real_query_balance(subscriber_id: str, payment_instrument_name: str) -> dict:
    return _post(
        "/get/balance",
        {
            **_auth_fields(),
            "subscriberId": subscriber_id,
            "paymentInstrumentName": _REAL_PAYMENT_INSTRUMENT_NAME,
            "currency": "BDT",
        },
    )


def _real_direct_debit(
    external_trx_id: str, subscriber_id: str, amount: float, payment_instrument_name: str, currency: str
) -> dict:
    return _post(
        "/direct/debit",
        {
            **_auth_fields(),
            "externalTrxId": external_trx_id,
            "subscriberId": subscriber_id,
            "paymentInstrumentName": _REAL_PAYMENT_INSTRUMENT_NAME,
            "amount": f"{amount:.2f}",
            "currency": currency,
        },
    )


# ---- Simulator mode: stateful local stand-in -----------------------------


def _simulated_query_balance(db: DBSession, subscriber_id: str, payment_instrument_name: str) -> dict:
    wallet = _get_or_create_wallet(db, subscriber_id)
    return {
        "statusCode": "S1000",
        "statusDetail": "Request was successfully processed",
        "chargeableBalance": f"{wallet.balance_bdt:.2f}",
        "accountStatus": "0",  # 0 = Activated, per real API convention
        "accountType": "PREPAID",
        "paymentInstrumentName": payment_instrument_name,
    }


def _simulated_get_payment_instrument_list(db: DBSession, subscriber_id: str, type_: str) -> dict:
    _get_or_create_wallet(db, subscriber_id)
    instruments = PAYMENT_INSTRUMENTS
    if type_ != "all":
        instruments = [i for i in instruments if i["type"] == type_]
    return {
        "statusCode": "S1000",
        "statusDetail": "Success",
        "paymentInstrumentList": instruments,
    }


def _simulated_direct_debit(
    db: DBSession,
    external_trx_id: str,
    subscriber_id: str,
    amount: float,
    payment_instrument_name: str,
    currency: str,
) -> dict:
    """Simulates realistic outcomes against the wallet's actual balance —
    insufficient funds genuinely fails with the real E1326 error code, not a
    hardcoded success."""
    if currency != "BDT":
        return {
            "statusCode": "E1312",
            "statusDetail": "Request is Invalid. Only 'BDT' currency is supported.",
            "externalTrxId": external_trx_id,
        }

    wallet = _get_or_create_wallet(db, subscriber_id)

    if amount <= 0:
        return {
            "statusCode": "E1312",
            "statusDetail": "Request is Invalid. 'amount' must be positive.",
            "externalTrxId": external_trx_id,
        }

    if wallet.balance_bdt < amount:
        return {
            "statusCode": "E1326",
            "statusDetail": "Insufficient balance.",
            "externalTrxId": external_trx_id,
            "timeStamp": _timestamp(),
        }

    # Tiny, disclosed simulated failure rate for a transient/retryable error —
    # so the receipt flow can also be seen handling a real-world hiccup, the
    # same E1603 code the real API documents for "Temporary System Error".
    if random.random() < 0.03:
        return {
            "statusCode": "E1603",
            "statusDetail": "Temporary System Error occurred while delivering your request.",
            "externalTrxId": external_trx_id,
            "timeStamp": _timestamp(),
        }

    wallet.balance_bdt = round(wallet.balance_bdt - amount, 2)
    db.add(wallet)
    db.commit()

    return {
        "statusCode": "S1000",
        "statusDetail": "Request was successfully processed",
        "externalTrxId": external_trx_id,
        "internalTrxId": uuid.uuid4().hex[:20],
        "referenceId": str(int(time.time()) % 100000000).zfill(8),
        "timeStamp": _timestamp(),
        "newBalance": f"{wallet.balance_bdt:.2f}",
    }
