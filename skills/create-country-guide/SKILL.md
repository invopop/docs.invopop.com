---
name: create-country-guide
description: Create a new country guide (supplier registration + issuing invoices pair) under guides/. Use whenever adding e-invoicing docs for a new country or regime, splitting an existing guide, or restructuring a country's guide family — covers page skeletons, workflow snippet pairs, FAQ wiring, and docs.json registration.
---

# Creating country guides

A country's docs ship as a **guide family**: one supplier registration guide plus one issuing/invoicing guide per regime (split established in #498), optionally extended with receiving, reporting, or status guides. Guides are tutorials — the paired `apps/` page is the catalogue/reference. Reference implementations, newest first: `guides/sa-zatca-*.mdx`, `guides/fr-pa-*.mdx` (large families), and the canonical two-page shape in `guides/co-dian.mdx` + `guides/co-dian-supplier.mdx` (also `pt-at`, `pl-ksef`, `gr-iapr`, `br-dfe`). Don't copy the older Spain pages (`es-verifactu*`) — they predate the current pattern.

## File naming

Flat files in `guides/`, slug `<iso2>-<regime>[-<task>].mdx`:

- Issuing guide: bare `<iso2>-<regime>.mdx` (`co-dian.mdx`, `pl-ksef.mdx`) — or explicit task when the family has several flows (`mx-sat-issuing.mdx`, `it-sdi-sending.mdx`, `fr-pa-invoicing.mdx`, `sa-zatca-clearance-reporting.mdx`).
- Supplier guide: `<iso2>-<regime>-supplier.mdx` (or `-registration` in the newest families: `fr-pa-registration.mdx`, `sa-zatca-registration.mdx`).
- Other tasks: `-receiving`, `-reporting`, `-status`, `-lookup`.
- Family hub: when a family has ≥3 pages, the bare slug becomes an overview page (`fr-pa.mdx`, sidebarTitle "Overview") with one horizontal `<Card>` per child guide.
- Peppol-only countries get a single page: `<iso2>-peppol.mdx` (`be-peppol.mdx`, `no-peppol.mdx`).

Don't copy the outliers `ar-arca-suppliers.mdx` (plural) or `de-ubl.mdx` (format name as regime).

## Frontmatter

```yaml
---
title: "DIAN issuing invoices guide"
sidebarTitle: "Issuing invoices"
description: Issue invoices and credit notes in Colombia through the DIAN.
---
```

- Sentence case; brand casing preserved (`VERI*FACTU`, `TicketBAI`, `KSeF`, `myDATA`). **No backslash escaping in frontmatter** — only in MDX body text.
- Title patterns: `"<REGIME> issuing invoices guide"` / `"<REGIME> supplier registration guide"`; the newest generation drops "guide" (`"Invoicing in France"`, `"ZATCA supplier registration in Saudi Arabia"`). Either is fine; be consistent within a family.
- `sidebarTitle` is a small closed enum — reuse verbatim: `Supplier registration`, `Issuing invoices`, `Receiving invoices`, `Reporting`, `Registration`, `Invoicing`, `Status`, `Clearance & reporting`, `Overview`.
- `icon` only on pages that sit directly in the nav without a flag-bearing group (e.g. `be-peppol.mdx` sets `https://assets.invopop.com/flags/be.svg`). Guides inside a country group must **not** set `icon` — the group carries the flag.

## Issuing guide skeleton

```
[frontmatter]
[imports — see Snippet wiring]

## Introduction        <- what the regime is, who runs it, partner disclosure, companion-guide link
[sandbox/live table]
## Prerequisites       <- bullets; FIRST bullet is always the registered supplier + link
## Setup               <- <Info> handoff to supplier guide, then <Steps>, one <Step> per workflow to create
[<Prompt />]          <- optional agent prompt (CLAUDE.md § Agent-facing files); reference: guides/es-verifactu.mdx
## Running             <- (or "## Send an invoice") upload entry → run job, with API links
### <sub-flows>        <- Cancel a document, Import received invoices, …
[## Example invoices]  <- <ExampleAccordion />
## FAQ
<FAQ />

More available in our [<Country> FAQ](/faq/<country>) section

---

<CountryResources />

<Card title="Participate in our community"
  icon="forumbee"
  href="https://community.invopop.com"
  arrow="true"
  horizontal
>
  Ask and answer questions about invoicing in <Country> →
</Card>
```

No "Next steps" section, no `<CardGroup>` — the FAQ + resources + community card trio is the closer on every guide.

Stock idioms:

- Companion link in the intro: `For onboarding suppliers with the DIAN and Plemsi, see the companion guide: [Colombia: Supplier registration](/guides/co-dian-supplier).`
- Sandbox/live table right after the intro, with a literal `-` first header cell:

  ```mdx
  | - | Sandbox | Live |
  |---|---|---|
  | **Supplier** | Pre-enabled test supplier with tax ID `177472438` | Registered supplier required |
  | **Environment** | myDATA test | myDATA production |
  ```

- Prerequisites first bullet: `- **A registered supplier**: follow the [AT supplier registration guide](/guides/pt-at-supplier) to connect the AT Portugal app, register the supplier, and register their document series before issuing.`
- Before `<Steps>`: `All of the following steps must be carried out from the [Invopop Console](https://console.invopop.com).`
- Optional step: `<Info>You can skip this step if you don't plan to issue invoices.</Info>`
- Recommended API flow: `<Info>The recommended approach for running jobs is to perform two steps: first upload the document to the [silo](/api-ref/silo/entries/create-an-entry-put), then [create a job](/api-ref/transform/jobs/create-a-job-post).</Info>`
- Optional enrichment from the newest guides: a `### How it works` heading with a purely descriptive `<Steps>` (one `<Step>` per workflow step, no user action) before the workflow block — see `guides/sa-zatca-clearance-reporting.mdx`.

## Supplier guide skeleton

```
## Introduction            <- regime + partner; handoff: "Once a supplier is registered, continue with
                              the companion guide: [<Country>: Issuing invoices](/guides/<slug>)."
[sandbox/live table]
## Prerequisites           <- data/credentials to collect from the supplier
## Setup                   <- <Steps>: "Connect the <X> app" → registration workflow →
                              post-registration workflow → "Configure the <X> app"
## Register a supplier     <- <Steps>: upload party → run workflow → complete wizard → wait for approval
[## Register a supplier via the API]
[## Unregister a supplier] <- own Card+Tabs workflow block, <Warning> about re-onboarding
[## <domain extras>]       <- Series management, Legal information, credentials, …
[handoff sentence]
## FAQ + footer trio
```

Differences vs the issuing guide:

- Setup opens with the app connection as prose+bold, not screenshots-first:
  `1. Navigate to **Configuration** → **Apps**` / `2. Find **Poland** in the app discovery list` / `3. Click **Connect** to activate`.
- Workflow templates are party-based: `Copy and paste into a new [Empty Party workflow](https://console.invopop.com/redirect/workflows/new?template=empty-party) code view.`
- Imports `/snippets/parties/<cc>/supplier.mdx` (or a party accordion), not invoice examples.
- FAQ composer is `guide-<regime>-supplier.mdx`.
- Registration wizard walkthroughs are `<Steps>` with one `<Frame>` screenshot per screen.
- Closing handoff: `At this point, you're ready to start sending invoices on behalf of the supplier. Head over to the [DIAN issuing invoices guide](/guides/co-dian) to continue.`

## The workflow block (most repeated shape)

Every workflow a guide asks the reader to create uses this Card + Tabs pair:

```mdx
<Card iconType="duotone" title="KSeF send invoice workflow" icon="code-branch" href="https://console.invopop.com/redirect/workflows/new?template=pl-send" horizontal>
  Add to my workspace →
</Card>
<Tabs>
  <Tab title="Workflow">
    <WorkflowDiagram workflow={plSendWorkflow} />
  </Tab>
  <Tab title="Code">
    Copy and paste into a new [Empty Invoice workflow](https://console.invopop.com/redirect/workflows/new?template=empty-invoice) code view.

    <SendInvoiceWorkflow />
  </Tab>
</Tabs>
```

- Tab titles are always exactly `"Workflow"` and `"Code"`.
- **Never use workflow screenshots** — diagrams render from JSON (#505).
- Starter templates by schema: `empty-invoice`, `empty-party`, `empty-payment`, `empty-delivery`, `empty-status`.
- The `?template=<slug>` on the Card is registered server-side in Console, **not in this repo** — verify the slug exists (`grep -ho 'template=[a-z0-9-]*' guides/*.mdx | sort -u` lists known ones) rather than inventing it. Omit the Card if there's no template.

## Snippet wiring

Import block right after frontmatter — plain snippet imports first, then the component, then workflow data exports (`guides/es-verifactu.mdx:8-18` shape):

```mdx
import WorkflowExample from '/snippets/workflows/co/dian-invoice.mdx';
import ExampleAccordion from '/snippets/invoices/co/accordion.mdx';
import Supplier from '/snippets/parties/co/supplier.mdx';
import ColombiaResources from '/snippets/tables/colombia-resources.mdx';
import FAQ from '/snippets/faqs/co/composers/guide-dian-invoicing.mdx';
import { WorkflowDiagram } from '/snippets/components/workflow.jsx';
import { coDianInvoiceWorkflow } from '/snippets/workflows/co/dian-invoice-data.mdx';
```

Naming: FAQ composer → always `FAQ`; resources table → `<Country>Resources`; example accordion → `ExampleAccordion`; workflow JSON snippet → descriptive PascalCase (`SendInvoiceWorkflow`, `RegisterWorkflow`). Country-prefix component names when a page composes several countries.

### Workflow snippet pairs

Each workflow lives as a **pair** under `snippets/workflows/<cc>/`:

- `<name>.mdx` — frontmatter (`title`, `description`, `countryCode`, `appId`, `schema`) + one fenced ` ```json ` block. Rendered in the Code tab.
- `<name>-data.mdx` — **only** `export const <export>Workflow = {…};`, nothing else. No frontmatter, no markdown — mixing content compiles to an `undefined` stub on a cold build and silently kills the section (warm `mint dev` masks it).
- Export name = globally unique camelCase of `<dir>-<basename>` + `Workflow`: `co/dian-invoice-data.mdx` ⇒ `coDianInvoiceWorkflow`; acronyms camelCased (`Nfse`, not `NFSe`). Never `workflow`.
- Import without aliasing — `{ x as y }` double-declares in Mintlify's inlining.
- **When updating the JSON, paste it into both files** — they must stay in sync.
- If the workflow uses an app new to `<WorkflowDiagram>`, add its provider key to `providerIcons` in `snippets/components/workflow.jsx` (longest-prefix match; static `className` literals only).

### Invoice / party examples

- `snippets/invoices/<cc>/` holds `.min.mdx` (hand-authored) + `.mdx` (built by `./gobl-build.sh`) pairs. **Edit only `.min.mdx`, then rebuild** — never hand-edit the built file. Requires the `gobl` CLI.
- Guides import a per-regime **accordion composer** (`snippets/invoices/<cc>/accordion.mdx` for single-regime countries; `<regime>-accordion.mdx` for multi-regime) that wraps each scenario's min+built pair in `<CodeGroup>` inside an `<Accordion>`.
- `snippets/parties/<cc>/` — single files (`supplier.mdx`, `customer.mdx`), no min/built pairing; validate with `gobl build` when editing.
- Same pairing exists in `snippets/payments/`, `snippets/deliveries/`, `snippets/documents/` for non-invoice flows (Portugal uses `snippets/documents/pt/accordion.mdx`).

### FAQ composer

Every guide imports exactly one composer: `/snippets/faqs/<cc>/composers/guide-<regime>-<task>.mdx` (task ∈ invoicing | supplier | receiving | reporting). **Read `skills/manage-faqs/SKILL.md` before creating leaves or composers**, and register the new consumer page in that skill's registry table. Page usage is always:

```mdx
## FAQ

<FAQ />

More available in our [Colombia FAQ](/faq/colombia) section
```

### Resources table

`snippets/tables/<full-country-name>-resources.mdx` — an `<AccordionGroup>` with one flag-emoji-titled `<Accordion>` wrapping a two-column table (Compliance / Apps / Guides / FAQ / GOBL rows). Create it for a new country; **add every new guide to the country's `Guides` row**.

## Screenshots

- Path: `/assets/guides/<iso2>-<regime>-<topic>[-<n>].png`.
- `<Frame caption="…"><img width="600" src="/assets/guides/…" alt="…" /></Frame>` — explicit pixel `width` tuned to the crop, `alt` always present, `caption` optional.
- Use screenshots for Console UI and hosted wizard screens only — never for workflows.
- Console UI labels in prose are bolded (`**Invoices**`, `**Run Workflow**`); buttons may use `<kbd>Save</kbd>`.

## docs.json registration

Guides live in the Guides tab under the `Countries` group, one flag-icon group per country, **supplier guide first**:

```json
{
  "group": "Colombia",
  "icon": "https://assets.invopop.com/flags/co.svg",
  "pages": [
    "/guides/co-dian-supplier",
    "/guides/co-dian"
  ]
}
```

- Countries alphabetical by English name; within a country: supplier → issuing → receiving → reporting.
- Multi-regime countries nest a regime sub-group **without an icon** (see Spain/France/Italy in `docs.json`). Group labels use raw `VERI*FACTU` — no escaping in JSON.
- Single-page Peppol countries are bare strings in the Countries list, carrying the flag in page frontmatter instead.
- "Coming soon" countries append `?coming-soon` to the flag icon URL (dimmed via `styles.css`).
- When renaming/moving a page, add a `redirects` entry (or use `mint rename OLD NEW`). When splitting, prefer keeping the existing slug for one half so no redirect is needed (#498 did this).

## Cross-linking

Root-relative page slugs, never file paths. Compliance/FAQ/timelines use the **full country name** (`/compliance/spain`, `/faq/colombia`); snippets use **ISO-2** (`snippets/invoices/co/`). Stock API links: `[Create an entry](/api-ref/silo/entries/create-an-entry-put)`, `[Create a job](/api-ref/transform/jobs/create-a-job-post)`. GOBL docs are absolute (`https://docs.gobl.org/regimes/pl`, `…/addons/es-verifactu-v1`).

## Checklist: adding a new country/regime

1. Create the guide pair: `guides/<iso2>-<regime>-supplier.mdx` + `guides/<iso2>-<regime>.mdx` (plus receiving/reporting if the regime has those flows).
2. Author workflow snippet pairs under `snippets/workflows/<cc>/` (both files each, unique exports).
3. Author GOBL examples: `snippets/parties/<cc>/{supplier,customer}.mdx`, `snippets/invoices/<cc>/*.min.mdx` + `accordion.mdx`, run `./gobl-build.sh`.
4. Create FAQ leaves + `guide-<regime>-invoicing.mdx` / `guide-<regime>-supplier.mdx` composers per `skills/manage-faqs/SKILL.md`; update its manifest and registry.
5. Create or update `snippets/tables/<country>-resources.mdx` (Guides row).
6. Register both pages in `docs.json` under Countries (flag SVG icon, supplier first, alphabetical placement).
7. Cross-link: companion links between the pair, links from `apps/<app>.mdx` and `compliance/<country>.mdx`, community card country name.
8. Add screenshots to `assets/guides/` if the flow has Console/wizard steps.
9. Validate: `mint dev` **from a cold start** (to catch broken workflow data snippets), `mint broken-links`.

## Gotchas

- Escape `VERI\*FACTU` in MDX body text and headings only — not in frontmatter, JSX prop strings, or `docs.json`.
- Sentence case in `<Step title="…">` props — Title Case in old Spain guides is a bug, not a pattern.
- Workflow data snippets: export-only file, unique export name, no import aliasing, keep the pair in sync (all four break silently otherwise).
- Never hand-edit built `snippets/invoices/**/<name>.mdx`; `./gobl-build.sh` overwrites them.
- `mint broken-links` is the only automated validation — there's no test suite.
- Develop on a branch, never on `main`.
