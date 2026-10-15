from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .approved_copy import SellerSmsAssets
from .handoff_service import AwaitingPickup, OrderHandoffRequest, SmsDispatch, decide_order_handoff
from .infrai_sms import InfraiClient


@dataclass(frozen=True)
class HandoffResult:
    order_id: str
    state: str
    message_id: str | None


def handoff_order(
    assets: SellerSmsAssets, request: OrderHandoffRequest, infrai: InfraiClient
) -> HandoffResult:
    decision = decide_order_handoff(assets, request)
    if isinstance(decision, AwaitingPickup):
        return HandoffResult(decision.order_id, decision.state, None)

    assert isinstance(decision, SmsDispatch)
    delivery = infrai.sms.batch.send(
        [{"to": decision.buyer_phone, "text": decision.text}],
        decision.idempotency_key,
    )
    message_id = delivery.get("message_id")
    if not isinstance(message_id, str):
        raise ValueError("SMS response did not include message_id")
    return HandoffResult(decision.order_id, "sent", message_id)


def request_from_json(payload: dict[str, Any]) -> OrderHandoffRequest:
    return OrderHandoffRequest(
        order_id=str(payload["order_id"]),
        seller_id=str(payload["seller_id"]),
        buyer_phone=str(payload["buyer_phone"]),
        courier_name=str(payload["courier_name"]),
        handoff_window=str(payload["handoff_window"]),
        pickup_ready=bool(payload["pickup_ready"]),
    )
