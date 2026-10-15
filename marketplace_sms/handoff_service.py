from __future__ import annotations

from dataclasses import dataclass

from .approved_copy import SellerSmsAssets


@dataclass(frozen=True)
class OrderHandoffRequest:
    order_id: str
    seller_id: str
    buyer_phone: str
    courier_name: str
    handoff_window: str
    pickup_ready: bool


@dataclass(frozen=True)
class AwaitingPickup:
    order_id: str
    state: str = "awaiting_pickup_ready"


@dataclass(frozen=True)
class SmsDispatch:
    order_id: str
    buyer_phone: str
    text: str
    idempotency_key: str
    state: str = "ready_to_send"


def decide_order_handoff(
    assets: SellerSmsAssets, request: OrderHandoffRequest
) -> AwaitingPickup | SmsDispatch:
    if assets.seller_id != request.seller_id:
        raise ValueError("seller assets do not match the handoff request")
    if not request.pickup_ready:
        return AwaitingPickup(order_id=request.order_id)
    return SmsDispatch(
        order_id=request.order_id,
        buyer_phone=request.buyer_phone,
        text=assets.render_handoff(
            request.order_id, request.courier_name, request.handoff_window
        ),
        idempotency_key=f"order-handoff:{request.order_id}:{request.seller_id}",
    )
