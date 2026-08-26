---
name: create-app-page
description: Create a new app page under apps/ (country connector, utility, format, or integration app). Use whenever adding an Invopop app to the docs, restructuring an app page, or updating its actions/workflows/documents tabs — covers the Tabs shell, apps/index.mdx card, and docs.json registration.
---

# Creating app pages

An app page is a **catalogue/reference page**: what the app is, the workflow actions it exposes, the workflow templates available, and the GOBL documents it consumes. Tutorials live in `guides/` — the app page links to them. Every app page (except `index.mdx` and partner stubs) is a single `<Tabs>` shell with a fixed tab set plus a footer. There are no configuration/settings sections and no screenshots on app pages.

Reference implementations, newest first: `apps/france.mdx` (preferred country app), `apps/saudi-arabia.mdx` (smaller second reference), `apps/sat-mexico.mdx` (fullest snippet wiring), `apps/spain.mdx` (umbrella multi-regime), `apps/chargebee.mdx` (integration), `apps/pdf-generator.mdx` / `apps/email.mdx` (utility), `apps/index.mdx` (directory).

## File naming

`apps/<slug>.mdx` → `/apps/<slug>`:

- **Country umbrella app (preferred for new country apps)**: `<country>.mdx` — `france.mdx`, `poland.mdx`, `argentina.mdx`, `saudi-arabia.mdx`, `spain.mdx`. Invopop is moving to one app per country grouping several regimes.
- Regime-specific app (legacy direction, still valid when the system name is the brand): `<regime>-<country>.mdx` — `verifactu-spain.mdx`, `sdi-italy.mdx`, `at-portugal.mdx`.
- Utility / format / integration: `<vendor-or-function>.mdx` — `pdf-generator.mdx`, `email.mdx`, `chargebee.mdx`, `peppol.mdx`.

Renames get a `docs.json` `redirects` entry (e.g. `/apps/ksef-poland` → `/apps/poland`).

## Frontmatter

Four fields, `mode: wide` mandatory (the two-column header and tab layout depend on it):

```yaml
---
title: "DIAN Colombia"
description: "Submit invoices to the Colombian DIAN system."
keywords: ['colombia', 'dian', 'co']
mode: wide
---
```

- `title` — the app's display name as it appears in Console. Brand punctuation literal (`VERI*FACTU Spain`) — no escaping in frontmatter.
- `description` — one imperative sentence; **reused verbatim as the card body in `apps/index.mdx`**, so write it to stand alone.
- `keywords` — lowercase: country name, regime/system acronyms, format names, ISO-2 code.
- No `icon`, no `sidebarTitle` (only `index.mdx` uses `sidebarTitle: "Discover"`).

## Page shell

Tab order is fixed: **Description → (Limitations) → Actions → Workflows → Documents → (API Endpoints)**.

```
imports…
<Tabs>
	<Tab title="Description">   ← header Columns + prose + Key features + ## FAQ
	<Tab title="Limitations">   ← optional: capability/status table
	<Tab title="Actions">       ← workflow actions the app exposes
	<Tab title="Workflows">     ← workflow templates as accordions
	<Tab title="Documents">     ← GOBL party/invoice examples
</Tabs>
---
<CountryResources />
<Card title="Participate in our community" icon="forumbee" … >
```

Indent tab bodies with hard tabs (one per nesting level); markdown inside a `<Tab>` must be indented to render — the indented `## FAQ` still becomes a real H2/anchor.

### Description tab

Two-column header: guide cards left, metadata table right.

```mdx
	<Tab title="Description">
		<Columns cols="2">
			<div class="flex flex-col grow items-center justify-center">
				<Card title="Register suppliers" icon="https://assets.invopop.com/flags/co.svg"
				  href="/guides/co-dian-registration" horizontal>
				  Supplier registration guide ›
				</Card>
				<Card title="Issue invoices" icon="https://assets.invopop.com/flags/co.svg"
				  href="/guides/co-dian-invoicing" horizontal>
				  Invoicing guide ›
				</Card>
			</div>

				|           |                                        |
				|-----------|----------------------------------------|
				| Developer | [Invopop](https://invopop.com)         |
				| Category  | Government                             |
				| Scope     | B2B, B2C                               |
				| Country   | [Colombia](/compliance/colombia)       |
		</Columns>
```

- The **empty header row is deliberate** — `styles.css` hides it. Don't drop it.
- `Category` must match the app's `docs.json` group name (Network / Government / Notify / Format / Document / Storage / Automation / Integrations).
- `Scope` = `B2B` / `B2C` / `B2G` comma-joined; format and integration apps drop `Scope` and `Country`. Optional `System` row for the authority platform (`| System | FATOORA (ZATCA) |`).
- Card body text uses `›` (not `→`): `Supplier registration guide ›`, `View guide ›`.
- Country umbrella apps use the flag as icon: `https://assets.invopop.com/flags/<cc>.svg`.

Then, in order:

1. **2–4 paragraphs of prose** — what the authority/system is (outbound link, local-language name in italics), whether e-invoicing is mandatory and on what model, how Invopop simplifies it, and any partner/PSP disclosure ("Invopop has partnered with [Alegra](https://www.alegra.com) … to onboard suppliers and issue documents on their behalf").
2. **`#### Key features`** — `**Bold label:** Sentence.` bullets. Near-universal first item: `**Workflow automation:**`.
3. **Guide pointer** — newest shape is a middot-joined list: `Check out the guides below to get started:` then `- [Registration](/guides/fr-pa-registration) · [Invoicing](/guides/fr-pa-invoicing) · [Reporting](/guides/fr-pa-reporting)`.
4. **`## FAQ`** — always last in the tab, the only `##` on the page:

```mdx
	## FAQ

	<FAQ />

	More answers in our [Colombia FAQ](/faq/colombia) section
```

### Limitations tab (optional)

Only where scope is incomplete. Capability table with badges — green `Available`, blue `Beta`, yellow `In development`:

```mdx
		| Capability | Status | Notes |
		|---|---|---|
		| Annuaire registration | <Badge color="green">Available</Badge> | Self-serve KYC in development |
		| E-reporting (Flow 10) | <Badge color="yellow">In development</Badge> | Add-on not yet released |
```

### Actions tab

Lead-in: `The following workflow actions will be available once you install and enable this app:` — then one horizontal `<Card>` per action. **Title = the exact action name in the Console step picker.**

```mdx
		<Card title="Send invoice to SDI" icon="https://assets.invopop.com/apps/sdi-italy/icon.svg" horizontal>
		 <div class="pop-count"><Icon icon="https://assets.invopop.com/icons/pops.svg" /> 3</div>
		 Issue GOBL invoices in the Italian SDI using the FatturaPA format.
		</Card>
```

- The `pop-count` div is the step's credit cost (absolutely positioned by `styles.css`). **Omit it entirely for zero-cost actions** (register, wait, cancel, import).
- Card bodies may embed essential input/output in prose (`Generates a unique URL in the \`meta\` property…`). No settings tables or parameter lists — the workflow JSON's `config` and the guides carry configuration detail.
- Many actions → cluster them under plain-text label lines (`Registration`, `Clearance & Reporting`), not headings.

### Workflows tab

`<AccordionGroup>` of `<Accordion title="<App> <verb phrase>">` (e.g. "PA send invoice", "SAT Mexico register supplier"), each containing the workflow snippet component. Newest style groups by object type under plain-text labels and omits lead-in and template links:

```mdx
		Invoice workflows
		<AccordionGroup>
			<Accordion title="PA send invoice">
				<PaSendInvoiceWorkflow />
			</Accordion>
		</AccordionGroup>

		Party workflows
		<AccordionGroup>
			<Accordion title="PA register party">
				<PaRegisterWorkflow />
			</Accordion>
		</AccordionGroup>
```

Only add `[Add to my workspace →](https://console.invopop.com/redirect/workflows/new?template=<slug>)` if the template slug is verified to exist in Console — it 404s silently otherwise. Utility apps with no templates replace this tab with prose about where the step fits (see `email.mdx`), or omit it.

### Documents tab

Party examples first (one-line explanation of the regime-specific identity fields above each snippet), then the invoice accordion, then a closing pointer:

```mdx
	<Tab title="Documents">
		<AccordionGroup>
			<Accordion title="SAT Mexico supplier">
				An RFC with the `mx-cfdi-fiscal-regime` extension and the registered postal code (Lugar de Expedición).
				<Supplier />
			</Accordion>
			<Accordion title="SAT Mexico customer">
				…
				<Customer />
			</Accordion>
		</AccordionGroup>

		<InvoiceAccordion />

		Copy and paste these documents into the [GOBL builder](https://build.gobl.org) in order to preview and verify them.
	</Tab>
```

### Footer

After `</Tabs>`, a `---`, the country resources snippet, and the community card:

```mdx
<Card title="Participate in our community"
  icon="forumbee"
  href="https://community.invopop.com"
  arrow="true"
  horizontal
>
  Ask and answer questions about the <X> app →
</Card>
```

Use `forumbee` (not the older `square-question`).

## Archetypes

| | Country connector | Utility (PDF, Email, Slack, Drive, Cron) | Format (UBL, CII, Facturae) | Integration (Chargebee, Stripe) |
|---|---|---|---|---|
| Tabs | Description, [Limitations], Actions, Workflows, Documents | Description, Actions, [Workflows] | Description, Actions, Documents | Description, Actions, Workflows |
| Metadata rows | Developer, Category, Scope, Country | Developer, Category | Developer, Category | Developer, Category |
| `## FAQ` | Yes | No | No | No |
| `<CountryResources />` | Yes | No | No | No |
| Documents tab | Parties + invoice examples | — | Invoice examples only | — |

Partner apps not yet self-serve get a stub: frontmatter + a single `<Note>` with a `mailto:` (see `netsuite.mdx`).

## Snippet wiring

Imports right after frontmatter — workflows → invoices/documents → parties → resources table → FAQ:

```mdx
import RegisterSupplier from '/snippets/workflows/mx/sat-register-supplier.mdx';
import IssueInvoice from '/snippets/workflows/mx/sat-issue-invoice.mdx';
import Supplier from '/snippets/parties/mx/supplier.mdx';
import Customer from '/snippets/parties/mx/customer.mdx';
import InvoiceAccordion from '/snippets/invoices/mx/accordion.mdx';
import MexicoResources from '/snippets/tables/mexico-resources.mdx';
import FAQ from '/snippets/faqs/mx/composers/app-sat.mdx';
```

- App pages import the workflow **content** snippet (`<name>.mdx`, the fenced JSON) and render it bare (`<IssueInvoice />`). They do **not** use `<WorkflowDiagram>` or the `-data.mdx` exports — that pairing is for guides. If you touch a workflow JSON, still sync both files of the pair (see `skills/create-country-guide/SKILL.md`).
- FAQ composer: always exactly one, aliased `FAQ`, at `/snippets/faqs/<cc>/composers/app-<regime>.mdx` where `<regime>` is the *system* name. **Read `skills/manage-faqs/SKILL.md` before creating it**, and register the page in that skill's registry table. App composers are task-organised (Invoicing → Supplier → Receiving → Reporting), plain-text task headings, no compliance leaf.
- Resources table: add the new app to the `Apps` row of `snippets/tables/<country>-resources.mdx`.
- `snippets/coverage/` is for compliance pages, not apps.

## Icons

No `assets/` references — every icon is an absolute CDN URL:

- App icon: `https://assets.invopop.com/apps/<app-id>/icon.svg`. **The CDN app-id often differs from the page slug** (`zatca` for saudi-arabia, `at-pt` for at-portugal) — verify against an existing usage rather than deriving; some legacy apps use `logo.svg`.
- Country flags: `https://assets.invopop.com/flags/<cc>.svg`.
- Credits: `https://assets.invopop.com/icons/pops.svg`; GOBL: `https://assets.invopop.com/icons/gobl.svg`.

## Registration (three places, keep in sync)

1. **`docs.json`** — Apps tab, add the slug to the matching group's `pages`, alphabetical within the group. Groups and icons: Network `chart-network`, Government `building-columns`, Notify `bullhorn`, Format `code-compare`, Document `file`, Storage `garage-car`, Automation `clock`, Integrations `plug`.
2. **`apps/index.mdx`** — add a horizontal `<Card>` in the same category block, alphabetical: `title` = page title, body = page `description` verbatim, `icon` = app SVG or flag, `href` = `/apps/<slug>`.
3. **Country resources table** — `Apps` row entry (country apps only).

Plus the `app-<regime>` FAQ composer and, if renaming, a `redirects` entry.

## Checklist: adding a new app page

1. Create `apps/<slug>.mdx` with `mode: wide` frontmatter and the Tabs shell for the right archetype.
2. Wire snippets: workflow content snippets, parties, invoice accordion, resources table, FAQ composer (create per `skills/manage-faqs/SKILL.md` if new).
3. Register in `docs.json` (group `pages`) and `apps/index.mdx` (category card).
4. Update `snippets/tables/<country>-resources.mdx` Apps row (country apps).
5. Cross-link from the country's guides and compliance page.
6. Validate: cold `mint dev`, `mint broken-links`.

## Gotchas

- `mode: wide` missing → the two-column header collapses.
- Drop the empty metadata-table header row → stray empty header renders.
- `Category` cell diverging from the docs.json group name (the `portal.mdx` "Utility" bug).
- Escape `VERI\*FACTU` in body prose and Card *bodies*; literal `VERI*FACTU` in JSX prop strings and frontmatter.
- `class` strings (`flex flex-col …`, `pop-count`) must stay static literals — Mintlify only compiles static Tailwind classes.
- Built-in components (`Badge`, `Icon`, `Note`, `Accordion`) need no import.
- Legacy patterns not to copy: `icon: "transporter-empty"` frontmatter, redundant `sidebarTitle`, `square-question` community icon, `####` headings in the Actions tab, `.png` app icons.
