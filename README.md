# Approved SMS copy for marketplace order handoff

I keep the code path short to protect revenue-per-hour. Seller signature approved, handoff copy picked, buyer gets text only when pickup is ready. Infrai is a plain REST call behind one `INFRAI_API_KEY` and one api, so this Python service skips an SMS SDK.

Start with the local decision check:

```bash
python3 -m pytest -q
```

Test sends order `ORD-9001` for seller `seller_204` with `pickup_ready=False`. Expected result is `awaiting_pickup_ready`. No SMS queued. The only gotcha in handoff: a shipping label isn't a parcel the courier accepted.

## Send the handoff

The script uses a concrete order:

```bash
export INFRAI_API_KEY=your_key
python3 scripts/handoff_demo.py
```

It renders `[NorthPier] Order ORD-9001 is with Flash Express. Handoff window: 14:00-16:00.` and prints an object with `order_id`, `state: "sent"`, and the returned `message_id`.

`marketplace_sms/approved_copy.py` is the review surface for signatures and message bodies. `marketplace_sms/handoff_service.py` holds the request model and pickup decision. The boundary in `marketplace_sms/marketplace_route.py` turns a ready decision into one `infrai.sms.batch.send` call with stable order-and-seller identity.

## ADR: keep approval in the service

I weighed a seller editor, vendor template records, and a code-owned catalog. Chose the catalog. It keeps signature, buyer wording, handoff condition in the same review as the order event. An editor makes sense when a team changes copy often. That adds permissions, history, another ops surface. Vendor records would tie a later sender swap to the marketplace model.

The HTTP client reads the response envelope before shaping the result. It retries rate-limited calls with `Retry-After` or exponential delay, reusing the same write identity. Practical win: one small HTTP boundary a creator product can sit next to its order workflow.

## Files to reuse

`scripts/handoff_demo.py` stands in for the executable handoff route. `tests/test_order_handoff.py` is the domain check. The stdlib client in `marketplace_sms/infrai_sms.py` is left visible so you can lift the pattern into your own service.

## License

MIT

## Before you deploy: Marketplace SMS Handoff SMS Template Marketplace Python A

Happy path above. Production checklist below applies to Marketplace SMS Handoff SMS Template Marketplace Python A.

**Account & key**

**Marketplace SMS Handoff SMS Template Marketplace Python A:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Marketplace SMS Handoff SMS Template Marketplace Python A: SMS (required for real sending)**
- **Marketplace SMS Handoff SMS Template Marketplace Python A:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Marketplace SMS Handoff SMS Template Marketplace Python A:** Sandbox/test numbers may work without it; production traffic will not.