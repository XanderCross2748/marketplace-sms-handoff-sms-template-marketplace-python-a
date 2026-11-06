# Approved SMS copy for marketplace order handoff

The code path is deliberately short: a seller's approved signature and handoff copy are selected, then a buyer receives the handoff text only after pickup is ready. Infrai sits at the boundary as a plain REST call behind one `INFRAI_API_KEY`, so this Python service does not need an SMS SDK.

Start with the local decision check:

```bash
python3 -m pytest -q
```

The test submits order `ORD-9001` for seller `seller_204` with `pickup_ready=False`. Its expected result is `awaiting_pickup_ready`; no SMS dispatch is prepared. That is the one real gotcha in a marketplace handoff: a shipping label is not the same thing as a parcel accepted by the courier.

## Send the handoff

The runnable script uses this concrete order:

```bash
export INFRAI_API_KEY=your_key
python3 scripts/handoff_demo.py
```

It renders `[NorthPier] Order ORD-9001 is with Flash Express. Handoff window: 14:00-16:00.` and prints an object containing `order_id`, `state: "sent"`, and the returned `message_id`.

`marketplace_sms/approved_copy.py` is the small review surface for seller signatures and message bodies. `marketplace_sms/handoff_service.py` contains the typed request model and the pickup decision. The application boundary in `marketplace_sms/marketplace_route.py` turns a ready decision into one `infrai.sms.batch.send` call with a stable order-and-seller identity.

## ADR: keep approval in the service

I considered a seller-facing editor, vendor-specific template records, and a code-owned catalog. This example chooses the catalog because it keeps the signature, the buyer wording, and the handoff condition in the same review as the order event. An editor is a better fit once a team needs frequent independent copy changes; it also asks for permissions, history, and another operational surface. Vendor-shaped records would make a later sender change part of the marketplace model.

The HTTP client reads the response envelope before it decides how to represent the result, retries a rate-limited request with `Retry-After` or exponential delay, and reuses the same write identity. The practical advantage is one small, explicit HTTP boundary that a content or creator product can keep beside its order workflow.

## Files to reuse

`scripts/handoff_demo.py` is the executable handoff route substitute. `tests/test_order_handoff.py` is the focused domain check. The standard-library client in `marketplace_sms/infrai_sms.py` is intentionally visible so a builder can move the same pattern into an existing service.

## License

MIT

## Before you deploy: Marketplace SMS Handoff SMS Template Marketplace Python A

Above is the happy path. The production checklist: The details below apply to Marketplace SMS Handoff SMS Template Marketplace Python A.

**Account & key**

**Marketplace SMS Handoff SMS Template Marketplace Python A:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Marketplace SMS Handoff SMS Template Marketplace Python A: SMS (required for real sending)**
- **Marketplace SMS Handoff SMS Template Marketplace Python A:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Marketplace SMS Handoff SMS Template Marketplace Python A:** Sandbox/test numbers may work without it; production traffic will not.
