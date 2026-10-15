from marketplace_sms.approved_copy import SellerSmsAssets
from marketplace_sms.handoff_service import AwaitingPickup, OrderHandoffRequest, decide_order_handoff


def test_handoff_waits_for_pickup_ready() -> None:
    assets = SellerSmsAssets(
        seller_id="seller_204",
        signature="[NorthPier]",
        buyer_update_template="{signature} Order {order_id} has an update.",
        handoff_template="{signature} Order {order_id} is with {courier_name}.",
        approved=True,
    )
    request = OrderHandoffRequest(
        order_id="ORD-9001",
        seller_id="seller_204",
        buyer_phone="+15551234567",
        courier_name="Flash Express",
        handoff_window="14:00-16:00",
        pickup_ready=False,
    )

    decision = decide_order_handoff(assets, request)

    assert isinstance(decision, AwaitingPickup)
    assert decision.order_id == "ORD-9001"
    assert decision.state == "awaiting_pickup_ready"
