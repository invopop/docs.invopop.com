---
name: invopop
description: Use when building or debugging an integration with Invopop, the e-invoicing platform, or when writing GOBL (Go Business Language) documents such as invoices, credit notes and parties. Covers the API loop (create silo entry, run a workflow job, read results), the GOBL rules agents most often get wrong (string amounts, tax rate keys, regimes and addons, corrections, UUIDs) and where the authoritative Markdown docs live for each country, schema and endpoint.
license: Apache-2.0
metadata:
  version: "2.0"
  source: https://github.com/invopop/docs.invopop.com
  canonical: https://docs.invopop.com/AGENTS.md
---

# Invopop

Invopop issues, receives and processes business documents in compliance with local tax rules across 30 countries. You send every document in one open JSON format, GOBL, and Invopop converts, signs, numbers and delivers it to tax authorities, networks such as Peppol, and customers. The REST API at `https://api.invopop.com` is organised as Silo (document storage and GOBL validation), Transform (workflows and jobs), Sequences (sequential numbering), Access (workspaces) and Utils (ping, UUIDs). The Console at `https://console.invopop.com` is the web UI over the same API.

## When to use

- Mapping an application's invoices, customers or products onto GOBL documents.
- Creating silo entries, running workflow jobs, reading states, files and faults.
- Registering suppliers with a tax authority before their first invoice.
- Handling corrections (credit notes, corrective invoices) and webhooks.
- Diagnosing a `422` validation error or a failed job.

## Read first

1. https://docs.invopop.com/AGENTS.md - the condensed rules. Keep it in context.
2. https://docs.invopop.com/llms.md - the same rules with worked examples and prompts.
3. https://docs.invopop.com/llms.txt - the index of every page. Fetch pages as Markdown by appending `.md`.
4. https://docs.gobl.org/llms.txt - the GOBL schema, regime and addon index.

## Working method

1. Identify the supplier's country. Read `https://docs.invopop.com/compliance/<country>.md`, then the country's supplier registration guide and invoicing guide under `https://docs.invopop.com/guides/`. Note the addon key and the workflow template they name.
2. Write the minimal GOBL document: `$schema`, `$regime`, `$addons` if the guide names one, `series`, `issue_date`, `supplier` and `customer` with `tax_id` objects, `lines` with `quantity`, `item.name`, `item.price` and `taxes` as `cat` plus `rate` key. Amounts are strings. Do not write totals or percentages.
3. Validate before touching Invopop: `POST https://gobl.dev/v0/build` with `{"data": <document>}` (no auth), or `gobl build -i doc.json` with the CLI from `go install github.com/invopop/gobl.dev/cmd/gobl@latest`, or the `build` tool of the local MCP server `gobl mcp`. Fix every fault by its `code` and `paths`.
4. In a sandbox workspace: `GET /utils/v1/ping`, then `PUT /silo/v1/entries/{uuid}` with `{"data": <document>}`, then `PUT /transform/v1/jobs/{uuid}?wait=30` with `{"workflow_id", "silo_entry_id"}`, then `GET /silo/v1/entries/{id}` for `state`, `signed` and `attachments`, and `GET /transform/v1/jobs/{id}` for `faults` and `intents`.
5. For corrections, never edit the issued document. `POST /silo/v1/entries` with `{"previous_id": <entry id>, "correct": {"type": "credit-note"}}` and run the workflow on the new entry.
6. In production, replace polling with a "Send Webhook" step in the workflow and its error branch.

## Rules that prevent the common failures

- Let build calculate. Hand-written `totals` are silently replaced, never checked.
- `{"cat": "VAT", "rate": "standard"}` is resolved per regime and `issue_date`; build returns `key: standard, rate: general, percent: ...`. Unknown rate keys fail. Category codes vary by regime (`VAT`, `ST`, `IVA`, `GST`).
- A supplier country without a GOBL regime needs an explicit `currency` and explicit tax `percent` values; the error otherwise is `currency: missing or invalid`.
- Never invent addon extension codes. Read `https://docs.gobl.org/addons/<key>.md`.
- Leave `code` empty when the workflow has an "Add sequential code" step. `code` is required only to sign.
- Use valid tax identities from the country guides. Checksums are enforced.
- Three UUIDs: silo entry `id` (API handle), envelope `head.uuid`, document `uuid` (used in `preceding`). Generate entry and job IDs yourself with `PUT` for idempotency; time-based versions for invoices, random for parties.
- Workflows must be published and match the document schema. Apps must be enabled per workspace. Government apps need the supplier registered first.
- Send a `User-Agent` header; Cloudflare answers `403 error code: 1010` to some default clients (Python `urllib`).
- Repeated `PUT`s and repeated `POST` keys return `409 Conflict` even for identical bodies; treat it as "already created" and `GET` the record.
- Jobs are asynchronous: `202` stub without `wait`, `200` full job with `?wait=30`. Entry `state` is a label set by workflow steps; the job's `faults` (absent when clean) are the truth about failures, even when `status` says `OK`.
- Treat signed entries as immutable even though the API will store a new signed version if you `PATCH` one; `PATCH` only before signing, correct afterwards.
- `validate` is not `build`; validating a partial document fails.

## Reference

- API reference: https://docs.invopop.com/api-ref/introduction.md
- Workflows: https://docs.invopop.com/guides/workflows.md
- Webhooks: https://docs.invopop.com/guides/webhooks.md
- Corrections: https://docs.invopop.com/guides/correct-invoice.md
- White label: https://docs.invopop.com/workspace/white-label.md
- Invoice schema: https://docs.gobl.org/draft-0/bill/invoice.md
- Party schema: https://docs.gobl.org/draft-0/org/party.md
- MCP servers: `https://docs.invopop.com/mcp`, `https://docs.gobl.org/mcp`
