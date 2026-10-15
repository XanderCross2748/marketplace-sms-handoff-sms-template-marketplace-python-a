from marketplace_sms.approved_copy import SellerSmsAssets
from marketplace_sms.handoff_service import OrderHandoffRequest
from marketplace_sms.infrai_sms import InfraiClient
from marketplace_sms.marketplace_route import handoff_order


assets = SellerSmsAssets(
    seller_id="seller_204",
    signature="[NorthPier]",
    buyer_update_template="{signature} Order {order_id} has an update.",
    handoff_template=(
        "{signature} Order {order_id} is with {courier_name}. "
        "Handoff window: {handoff_window}."
    ),
    approved=True,
)
request = OrderHandoffRequest(
    order_id="ORD-9001",
    seller_id="seller_204",
    buyer_phone="+15551234567",
    courier_name="Flash Express",
    handoff_window="14:00-16:00",
    pickup_ready=True,
)

result = handoff_order(assets, request, InfraiClient())
print({"order_id": result.order_id, "state": result.state, "message_id": result.message_id})
