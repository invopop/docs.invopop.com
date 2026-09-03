# Invopop for AI agents

This file is published at https://docs.invopop.com/AGENTS.md. It is the condensed, copy-into-your-context version of https://docs.invopop.com/llms.md, for agents that integrate Invopop into another product. If you are editing the docs.invopop.com repository itself, follow `CLAUDE.md` instead.

## What Invopop is

Invopop issues, receives and processes business documents (invoices, credit notes, orders, deliveries, payments) in compliance with local tax rules. You send every document in one format, GOBL (Go Business Language, https://gobl.org), and Invopop converts it to the local format and delivers it to the tax authority, the network (Peppol, SDI, KSeF) or the customer. GOBL is open source; Invopop is the hosted platform around it.

- API: `https://api.invopop.com`, JSON, Bearer tokens, one token per workspace, same host for sandbox and live.
- Console: `https://console.invopop.com`, the web UI over the same API.
- Docs: any page as Markdown by appending `.md`; index at https://docs.invopop.com/llms.txt; GOBL index at https://docs.gobl.org/llms.txt.
- MCP servers: `https://docs.invopop.com/mcp` and `https://docs.gobl.org/mcp` (HTTP transport).
- Skill: `npx skills add https://docs.invopop.com` installs https://docs.invopop.com/skill.md.

## Mental model

1. A **GOBL document** is JSON whose `$schema` names its type (`https://gobl.org/draft-0/bill/invoice`, `.../org/party`, `.../bill/order`, `.../bill/delivery`, `.../bill/payment`, `.../bill/status`, `.../org/item`).
2. You write a partial document. **Build** normalises it, calculates totals and taxes for the regime and date, and validates it. Invopop builds on upload; you can also build locally or with the public GOBL API.
3. Invopop stores the built document inside an **envelope** (`head` with UUID, digest, stamps and tags; `doc`; `sigs`) as a **silo entry** with an `id`, a `state`, `attachments` and metadata.
4. A **workflow** is a published sequence of steps for one schema. A **job** runs one workflow over one entry. Steps come from **apps** enabled in the **workspace** and do the work: assign a sequential code, sign, convert to local XML, send to the authority, render a PDF, call a webhook, set the state.
5. A **workspace** is an isolated environment (sandbox or live) with its own API keys, apps, workflows and series. An **organization** groups workspaces. Use one workspace per tax regime.

## GOBL rules

1. **Send the minimum, let build calculate.** Never write `sum`, `total`, `totals` or tax `percent` yourself. If you send `totals` they are recalculated and silently replaced, so a wrong figure will not raise an error. Read totals from the built document.
2. **Numbers are strings.** `"90.00"`, `"20.0%"`. JSON numbers are accepted on input and returned as strings. Trailing zeros set precision.
3. **`$schema` is mandatory.** It decides which schema, workflow and apps apply.
4. **`$regime` is the supplier's country code.** Inferred from `supplier.tax_id.country` if omitted; set it anyway. Regimes exist for `AE AR AT BE BR CA CH CO DE DK EL ES FI FR GB IE IN IT MX NL NO PL PT SA SE SG US` (`EL` is Greece). Reference: `https://docs.gobl.org/regimes/<code>.md`. For a country without a regime you must set `currency` and give every tax an explicit `percent`; otherwise build fails with `currency: missing or invalid`.
5. **Taxes are keys.** `{"cat": "VAT", "rate": "standard"}` becomes `key: standard, rate: general, percent: 20.0%` for the regime and `issue_date`. `standard` and `general` mean the same. Other rates: `reduced`, `super-reduced`, `intermediate`, `zero`. Keys without a percent: `exempt`, `reverse-charge`. Unknown keys fail the build. Category codes differ by regime (`VAT`, `ST`, `IVA`, `GST`). Look them up on the regime page rather than guessing.
6. **`$addons` switches on a country format** (`es-verifactu-v1`, `pl-favat-v3`, `pt-saft-v1`, `mx-cfdi-v4`, `it-sdi-v1`, `gr-mydata-v1`, `co-dian-v2`, `sa-zatca-v1`, `fr-facturx-v1`, `de-xrechnung-v3`, `eu-en16931-v2017`, ...). Addons add coded `ext` values; build fills the defaults it can and reports the rest as faults naming the extension key. Never invent extension codes. Reference: `https://docs.gobl.org/addons/<key>.md`. The country's invoicing guide on docs.invopop.com says which addon to use.
7. **`series` + `code` is the invoice number.** Optional at build, required to sign. Most workflows begin with an "Add sequential code" step that sets `code` from a series, so leave `code` empty when using one.
8. **Tax IDs are normalised and checksum-validated.** `es-b-986.026.42` becomes `B98602642`; an invalid identity fails with a code like `GOBL-GB-TAX-IDENTITY-03`. Use the valid test identities from the country guides, never made-up digits.
9. **Never edit an issued invoice; correct it.** `type` is `credit-note` (extends the original), `debit-note` or `corrective` (replaces it, used in Spain and Poland), with the original referenced in `preceding`. Do not build corrections by hand: use `gobl correct --credit` locally or, on Invopop, create an entry with `previous_id` and a `correct` object. `correct.type` is required (the old `credit: true` form is rejected with `missing correction type`); `series` defaults to the original's; `issue_date`, `reason`, `copy_tax` and `stamps` are optional.
10. **Three UUIDs, all different.** Silo entry `id` (what every endpoint takes), envelope `head.uuid`, document `uuid` (what `preceding[].uuid` and party references use). Supplying the entry ID does not make the other two match it. Generate entry IDs yourself for idempotent `PUT`s: version 1 or 7 for invoices and other dated documents, version 3, 4 or 5 for parties and items.
11. **`$tags` name scenarios**: `simplified` (no customer), `reverse-charge`, `self-billed`, `partial`, `customer-rates`. Older examples use `tax.tags`; prefer `$tags`.
12. **`validate` is not `build`.** Validating a partial document fails. Build first.

## Invopop rules

1. **Auth**: `Authorization: Bearer <token>`. Keys are created in Console under Configuration → API Keys and are scoped to one workspace. Check with `GET /utils/v1/ping` → `{"ping":"pong"}`. **Send a `User-Agent` header naming your app**: the API is behind Cloudflare, which answers a bare `403` with body `error code: 1010` to some default client signatures, Python's `urllib` included (`requests`, `httpx`, Go, Node and Java defaults pass).
2. **Sandbox first.** Same API host; the token picks the workspace. `GET /access/v1/workspace` returns `name`, `slug`, `country` and `sandbox: true|false`; check it before creating anything. Sandbox government apps talk to test environments and most countries ship a pre-enabled test supplier. Live needs a subscription, a live workspace and registered suppliers.
3. **Idempotency**: prefer `PUT /silo/v1/entries/{uuid}` and `PUT /transform/v1/jobs/{uuid}` with your own UUIDs. Requests are not replayed: a repeated `PUT` with the same ID, or `POST` with the same `key`, returns `409 Conflict` (`entry already exists with same id` / `same key`) even for an identical body. Treat `409` as "already created" and `GET` the record.
4. **Entry body**: `{"data": <document or envelope>}`. Optional: `key`, `folder`, `sign` (requires a `code`), `allow_invalid` (stores with `invalid: true` and `faults`), and `previous_id` + `correct` for corrections. The `200` response has `id`, `folder`, `doc_schema`, `snippet`, `version`, `versions` and the envelope in `data`; `signed` and `state` are omitted until set (`draft: true` marks an unsigned entry). A `4xx` means nothing was stored; validation errors return `key: "validation"`, `message`, a `faults` array (`code`, `paths`, `message`) and a `fields` object mirroring the document path. Missing `$schema` → `unknown-schema`.
5. **Workflows** are per schema, must be published (not draft) and are identified by UUID. Create them in the Console from templates (deep link `https://console.invopop.com/redirect/workflows/new?template=<name>`, for example `pdf-invoice`, `empty-invoice`), paste the JSON from a country guide into an empty workflow's code view, or `PUT /transform/v1/workflows/{uuid}` with that same JSON (published unless `draft: true`). A job for a draft or unknown workflow → `404 invalid workflow id or not published`. An entry of the wrong schema → the job runs and its first step is `KO` with code `schema-mismatch`.
6. **Jobs are asynchronous**: `PUT /transform/v1/jobs/{uuid}` with `{"workflow_id": "...", "silo_entry_id": "..."}` returns `202` and a stub (`status: "NA"`). Add `?wait=30` to block up to 30 seconds; when the job finishes in time you get `200` and the full job. In production use a "Send Webhook" step in the main flow and in the error branch. A full job has `completed_at`, `status`, `intents[]` (one per step) with `events[].status` going `RUN` then `OK`, `KO`, `SKIP` or `TIMEOUT` plus `code` and `message`, `attachments`, `envelope`, and `faults[]` (`provider`, `code`, `message`), the authoritative error list, absent when nothing failed. `status` can be `OK` while `faults` is non-empty (the error branch ran), so read `faults`.
7. **States are labels** (`empty`, `processing`, `sent`, `error`, `paid`, `void`, ...) set by "Set state" steps or by `POST /silo/v1/entries/{id}/states` with `{"key": "paid"}`; the `state` key is absent until then. They track progress; they do not certify anything. Diagnose failures from the job's `faults`, not the entry's `state` or the entry's legacy `faults` field.
8. **Apps must be enabled** per workspace (Console → Configuration → Apps). Government apps also need each supplier registered: upload an `org/party` entry and run the country's registration workflow until the entry reaches `registered`.
9. **Results live on the entry**: `attachments[]` (PDF, XML, receipts, each with `key`, `mime`, `url`), `state`, and authority identifiers in the envelope's `head.stamps`. Fetch the entry after the job completes.
10. **Signed means stop editing.** Before the "Sign envelope" step you may `PATCH` the entry freely. After it the API still accepts a `PATCH` whose document is complete enough to re-sign and stores a new signed version, but issued invoices must not change: correct or replicate instead. Signing fixes `$schema` and `type`.
11. **Preview totals** without storing anything with `POST /silo/v1/gobl/build` and `{"data": <document>}`; the response is `{"data": <built document>}` (`"envelop": true` returns an envelope). The public GOBL API does the same unauthenticated: `POST https://gobl.dev/v0/build`.

## Minimal examples

Invoice to send (build adds `$regime`, `type`, `currency`, `code` via the workflow, and all totals):

```json
{
  "$schema": "https://gobl.org/draft-0/bill/invoice",
  "series": "TEST",
  "issue_date": "2026-09-03",
  "supplier": {
    "name": "Test Company Ltd.",
    "tax_id": { "country": "GB", "code": "000472631" }
  },
  "customer": {
    "name": "Random Company Ltd.",
    "tax_id": { "country": "GB", "code": "350983637" }
  },
  "lines": [
    {
      "quantity": "20",
      "item": { "name": "Development services", "price": "90.00" },
      "taxes": [{ "cat": "VAT", "rate": "standard" }]
    }
  ]
}
```

Spanish invoice for VERI*FACTU (the addon makes build add `tax.ext` and line `taxes[].ext` codes automatically for this simple case):

```json
{
  "$schema": "https://gobl.org/draft-0/bill/invoice",
  "$regime": "ES",
  "$addons": ["es-verifactu-v1"],
  "series": "SAMPLE",
  "issue_date": "2026-09-03",
  "supplier": {
    "name": "Invopop S.L.",
    "tax_id": { "country": "ES", "code": "B85905495" },
    "addresses": [
      { "num": "42", "street": "Calle Pradillo", "locality": "Madrid", "region": "Madrid", "code": "28002", "country": "ES" }
    ]
  },
  "customer": {
    "name": "Sample Consumer",
    "tax_id": { "country": "ES", "code": "B63272603" }
  },
  "lines": [
    {
      "quantity": "20",
      "item": { "name": "Development services", "price": "90.00", "unit": "h" },
      "taxes": [{ "cat": "VAT", "rate": "general" }]
    }
  ]
}
```

Party to register as a supplier:

```json
{
  "$schema": "https://gobl.org/draft-0/org/party",
  "name": "Invopop S.L.",
  "tax_id": { "country": "ES", "code": "B85905495" },
  "addresses": [
    { "num": "42", "street": "Calle Pradillo", "locality": "Madrid", "region": "Madrid", "code": "28002", "country": "ES" }
  ],
  "emails": [{ "addr": "billing@example.com" }]
}
```

Create entry request body (`PUT /silo/v1/entries/{uuid}`):

```json
{ "data": { "$schema": "https://gobl.org/draft-0/bill/invoice", "...": "..." } }
```

Create job request body (`PUT /transform/v1/jobs/{uuid}?wait=30`):

```json
{ "workflow_id": "186522a6-e697-4e34-8498-eee961bcb845", "silo_entry_id": "03836750-461b-11f0-a07f-051acfb70532" }
```

Credit note from an existing entry (`POST /silo/v1/entries`):

```json
{ "previous_id": "03836750-461b-11f0-a07f-051acfb70532", "correct": { "type": "credit-note", "series": "CN" } }
```

Full loop with curl (`INVOPOP_TOKEN` set, `WORKFLOW_ID` from the Console):

```bash
API=https://api.invopop.com
H=(-H "Authorization: Bearer $INVOPOP_TOKEN" -H "Content-Type: application/json")
curl -s "${H[@]}" $API/utils/v1/ping
ENTRY_ID=$(curl -s "${H[@]}" "$API/utils/v1/uuid?v=7" | jq -r .uuid)
curl -s "${H[@]}" -X PUT "$API/silo/v1/entries/$ENTRY_ID" -d @invoice-entry.json
JOB_ID=$(curl -s "${H[@]}" "$API/utils/v1/uuid?v=7" | jq -r .uuid)
curl -s "${H[@]}" -X PUT "$API/transform/v1/jobs/$JOB_ID?wait=30" \
  -d "{\"workflow_id\":\"$WORKFLOW_ID\",\"silo_entry_id\":\"$ENTRY_ID\"}"   # 200 + full job when done in time, else 202 stub
curl -s "${H[@]}" "$API/silo/v1/entries/$ENTRY_ID" | jq '{state, signed, attachments}'
```

## Endpoint cheat sheet

| Purpose | Call |
| --- | --- |
| Check token | `GET /utils/v1/ping` |
| Generate a UUID | `GET /utils/v1/uuid?v=7` (time-based) or `?v=4` (random) |
| Preview build without storing | `POST /silo/v1/gobl/build` |
| Create entry (idempotent) | `PUT /silo/v1/entries/{id}` |
| Create entry (server ID) | `POST /silo/v1/entries` |
| Fetch entry | `GET /silo/v1/entries/{id}`, by key `GET /silo/v1/entries/key/{key}` |
| Update unsigned entry | `PATCH /silo/v1/entries/{id}` (`content_type` may be a JSON patch type) |
| List, search entries | `GET /silo/v1/entries?folder=invoices&limit=10` (`limit` 10 to 100), `GET /silo/v1/search?q=...` (indexes series, codes, party names and tax IDs, not line items; new entries appear after roughly 45 minutes, so never use it to confirm a fresh write) |
| Related documents | `GET /silo/v1/entries/{id}/related` |
| Entry files | `GET /silo/v1/entries/{id}/files/{file_id}`, `POST .../files` |
| Set state directly | `POST /silo/v1/entries/{id}/states` |
| Create job (idempotent) | `PUT /transform/v1/jobs/{id}` (`?wait=N`) |
| Fetch job | `GET /transform/v1/jobs/{id}`, by key `GET /transform/v1/jobs/key/{key}` |
| Workflows | `GET /transform/v1/workflows`, `PUT /transform/v1/workflows/{id}`, `PATCH .../{id}` |
| Series and sequential codes | `PUT /sequence/v1/series/{id}`, `PUT /sequence/v1/series/{series_id}/entries/{id}` |
| Workspace info | `GET /access/v1/workspace` |

Every service is versioned in the path (`/silo/v1`, `/transform/v1`, `/sequence/v1`, `/access/v1`, `/utils/v1`). Full reference: https://docs.invopop.com/api-ref/introduction.md and the OpenAPI files linked at the bottom of https://docs.invopop.com/llms.txt.

## Decoding errors

- **Validation on upload** (`422`): `{"key": "validation", "message": "...", "fields": {"data": {"doc": {"customer": {"tax_id": {"code": "unknown type"}}}}}}`. The nested path points at the field. Fix the document; nothing was stored.
- **GOBL fault codes** look like `GOBL-<REGIME>-<SCHEMA>-<NN>` (`GOBL-TAX-COMBO-04`, `GOBL-GB-TAX-IDENTITY-03`). The schema page on docs.gobl.org lists each code with its rule.
- **Job failures**: read `faults[]` (`provider`, `code`, `message`) and find the first `intents[].events[]` with status `KO` or `TIMEOUT`. Authority error codes (AEAT, KSeF, SDI, DIAN) are explained in the country FAQ at `https://docs.invopop.com/faq/<country>.md` and in the invoicing guide.
- **`403` with body `error code: 1010`**: Cloudflare rejected your HTTP client's default signature. Send a `User-Agent` header.
- **`409 Conflict`**: the entry ID, job ID or key was already used, even with the same content. The first request succeeded; `GET` the record.
- **`404 invalid workflow id or not published`** on job creation: the workflow is a draft or the ID is wrong.
- **Job step `KO` with code `schema-mismatch`**: the entry's schema is not the workflow's schema.
- **`422 GOBL-ENVELOPE-13 envelope doc is not ready to be signed`**: you asked to sign (or patched a signed entry) with a document that has no `code`.
- **`422 Limit: must be no less than 10`**: list endpoints need `limit` between 10 and 100.
- **A step is missing from the Console action list**: the app that provides it is not enabled in this workspace.
- **A government step fails on the first invoice**: the supplier is not registered. Run the country's supplier registration workflow first.

## Where to look

| Question | URL pattern |
| --- | --- |
| Country obligations and dates | `https://docs.invopop.com/compliance/<country>.md`, `.../timelines/<country>.md` |
| Register a supplier in a country | `https://docs.invopop.com/guides/<iso2>-<regime>-supplier.md` (some newer families use `-registration`) |
| Issue invoices in a country, with template and examples | `https://docs.invopop.com/guides/<iso2>-<regime>.md` |
| Country FAQ and authority error codes | `https://docs.invopop.com/faq/<country>.md` |
| What a workflow step does | `https://docs.invopop.com/apps/<app>.md` |
| Workflows, conditions, error handling | `https://docs.invopop.com/guides/workflows.md` |
| Webhooks | `https://docs.invopop.com/guides/webhooks.md` |
| Corrections | `https://docs.invopop.com/guides/correct-invoice.md` |
| White label (invoicing on behalf of your customers) | `https://docs.invopop.com/workspace/white-label.md` |
| Schema fields and validation rules | `https://docs.gobl.org/draft-0/<schema>.md`, for example `bill/invoice`, `org/party`, `tax/combo` |
| Regime tax categories, rates, tags, corrections | `https://docs.gobl.org/regimes/<code>.md` |
| Addon extension codes | `https://docs.gobl.org/addons/<key>.md` |

Compliance, timeline and FAQ pages use the full country name (`spain`, `saudi-arabia`); guides use ISO codes (`es-verifactu`, `sa-zatca-registration`). The complete page list is in `llms.txt`.

## Local GOBL tooling

- CLI (lives in `gobl.dev`, not the core library): `go install github.com/invopop/gobl.dev/cmd/gobl@latest`, then `gobl build -i doc.json`, `gobl build -i -e doc.json` (envelope), `gobl correct -i --credit built.json`, `gobl validate built.json`.
- Local MCP server: `gobl mcp` (stdio) exposes `build`, `validate`, `correct`, `replicate`, `schema`, `regime`, `regime_list`, `addon`, `addon_list`. Use `regime` and `addon` to look up exact keys and codes.
- Public API, no install: `POST https://gobl.dev/v0/build` with `{"data": <document>}`; `GET https://gobl.dev/v0/regimes`, `GET https://gobl.dev/v0/addons`.
- Browser: https://build.gobl.org.

## Vocabulary

| You might say | Invopop / GOBL term |
| --- | --- |
| Upload an invoice | Create a silo entry |
| Send, report, issue | Create a job on a workflow |
| Invoice number | `series` + `code` from a series ("Add sequential code" step) |
| Customer, vendor, company | `org/party` with a `tax_id` |
| Tax rate 21% | `{"cat": "VAT", "rate": "standard"}` resolved for regime and date |
| Refund, cancel, void | Credit note or corrective invoice with `preceding`, made with `previous_id` + `correct` |
| Status | Entry `state` (label) versus job `faults` and `intents` (truth) |
| PDF, XML, authority receipt | Entry `attachments`; envelope `head.stamps` |
| Callback | "Send Webhook" step |
| Test mode | Sandbox workspace, its own token, same API host |
| Country rules | Regime (`$regime`) plus addons (`$addons`) |
| Tenant, environment | Workspace, inside an organization |
