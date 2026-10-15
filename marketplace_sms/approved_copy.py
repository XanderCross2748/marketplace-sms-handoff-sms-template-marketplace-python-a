from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SellerSmsAssets:
    seller_id: str
    signature: str
    buyer_update_template: str
    handoff_template: str
    approved: bool

    def render_handoff(self, order_id: str, courier_name: str, handoff_window: str) -> str:
        if not self.approved:
            raise ValueError("seller SMS assets must be approved")
        return self.handoff_template.format(
            signature=self.signature,
            order_id=order_id,
            courier_name=courier_name,
            handoff_window=handoff_window,
        )
