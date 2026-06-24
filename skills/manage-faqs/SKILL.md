---
name: manage-faqs
description: Add, remove, reorder, or wire country FAQ questions across the Invopop docs. Use whenever the user wants to update FAQ content, import questions from Pylon/support, or hook FAQs into a new consumer page (compliance page, app page, guide).
---

# Managing country FAQs

FAQ snippets are organized as a `country / scope / task` grid. **Leaves** hold the actual `<Accordion>` blocks; **composers** group them for a specific consumer page (a country FAQ page, a compliance page, an app page, a guide). Consumer pages import exactly one composer.

## Axes

- **Country** — ISO-2 lowercase: `ar`, `be`, `br`, `de`, `es`, `fr`, `gr`, `it`, `mx`, `pl`, `pt`. Plus `peppol`, a top-level pseudo-country (see below).
- **Scope** — `country` (cross-regime, country-level answers) or one regime from the manifest.
- **Task** — `invoicing`, `supplier`, `receiving`, `reporting`. Populate only the tasks that genuinely apply to the scope. Plus `compliance` as a special scope-wide file (see below).

Cells exist only when they have applicable content — no empty files, no "doesn't apply" stubs.

### Leaf file layout

Each scope has up to five leaf files:

```
<country>/leaves/<scope>/
├── compliance.mdx     # all compliance accordions for the scope (mixed across tasks)
├── invoicing.mdx      # operations + tech for invoicing
├── supplier.mdx       # operations + tech for supplier
├── receiving.mdx      # operations + tech for receiving
└── reporting.mdx      # operations + tech for reporting
```

`compliance.mdx` holds every compliance-flavoured accordion for that scope, ordered by task (invoicing → supplier → receiving → reporting). The four task files hold non-compliance accordions for that task — operations and tech are not split at the file level, since composers always render them together.

### Country scope shape depends on regime count

The country scope holds answers that aren't tied to a specific regime:

- **Single-regime countries** (`ar`, `gr`, `mx`, `pl`, `pt`) — country scope is a single flat file: `<country>/leaves/country/compliance.mdx`. Country-level operations/tech content is folded directly into the regime's leaves (since there's only one regime, country-level == regime-level for those tasks). Only genuinely cross-cutting compliance answers live in `country/compliance.mdx`.
- **Multi-regime countries** (`be`, `br`, `de`, `es`, `fr`, `it`) — country scope keeps the full task layout under `<country>/leaves/general/`. The `general/` folder name is legacy; the display label in composers is the country name. Multi-regime countries can't safely merge country-level ops/tech into any one regime, so per-task files are preserved.

Regime leaves always use the full layout: `<country>/leaves/<regime>/{compliance,invoicing,supplier,receiving,reporting}.mdx`.

### Peppol is a top-level pseudo-country

Peppol gets its own folder at the country level (`snippets/faqs/peppol/`) with no scope subdirectory — peppol is itself the scope. Layout:

```
snippets/faqs/peppol/leaves/{compliance,invoicing,supplier,receiving}.mdx
```

Tasks: `invoicing`, `receiving`, `supplier`. **No `reporting`** — periodic reporting is country-specific and stays under each country's regimes.

Peppol-using countries (currently BE, DE, FR) import Peppol leaves into their composers as an additional scope alongside their country scope and regimes.

### Which tasks apply to a regime

Pick task buckets from the regime's actual flow shape **and** match the documentation we publish — if no guide covers a flow, don't add an FAQ for it.

- **Issuance only** (one-way clearance, no recipient delivery, no separate reporting) — `invoicing` + `supplier`. Examples: ARCA, VERI*FACTU, No-VERI*FACTU, Facturae, NF-e, NFS-e, Chorus Pro.
- **Issuance + supplementary reporting** — add `reporting`. Examples: TicketBAI (Bizkaia LROE), Smart Receipts (corrispettivi), AT (SAF-T monthly export / real-time submission).
- **Bidirectional clearance / delivery** — add `receiving`. Examples: SDI, KSeF, SAT/CFDI, Peppol, myDATA.
- **Reporting regime** (the regime *is* the reporting channel) — all four tasks apply. Examples: SII, France PA.

The country scope only populates a task if the corresponding country-level flow exists in the docs. Periodic VAT returns (Modelos in ES, ELSTER in DE, LIPE in IT, etc.) are filed by accountants outside Invopop and have no guide — do **not** add a `<scope>/reporting.mdx` for them.

## Manifest

| Country | ISO | Regimes |
|---|---|---|
| Argentina | ar | `arca` |
| Belgium | be | (uses `peppol` only) |
| Brazil | br | `nfe`, `nfse` |
| Germany | de | (uses `peppol` only) |
| Spain | es | `verifactu`, `ticketbai`, `sii`, `noverifactu`, `facturae` |
| France | fr | `pa`, `choruspro` (also uses `peppol`) |
| Greece | gr | `mydata` |
| Italy | it | `sdi`, `ticket` |
| Mexico | mx | `sat` |
| Poland | pl | `ksef` |
| Portugal | pt | `at` |
| Saudi Arabia | sa | `zatca` |
| — | peppol | (top-level, scopeless) |

### Display labels

Folder slugs are lowercase; subheadings in composers use the canonical brand spelling.

| Slug | Label |
|---|---|
| `arca` | ARCA |
| `peppol` | Peppol |
| `nfe` | NF-e |
| `nfse` | NFS-e |
| `verifactu` | VERI*FACTU |
| `ticketbai` | TicketBAI |
| `sii` | SII |
| `noverifactu` | No-VERI*FACTU |
| `facturae` | Facturae |
| `pa` | PA (Plateforme Agréée) |
| `choruspro` | Chorus Pro |
| `mydata` | myDATA |
| `sdi` | SDI |
| `ticket` | Smart Receipts |
| `sat` | SAT/CFDI |
| `ksef` | KSeF |
| `at` | AT (SAF-T) |
| `zatca` | ZATCA |

For the country scope, the subheading is the **country name** (e.g. `Spain`, `Belgium`, `Argentina`), not "General". The label `General` is deprecated. Replace it with the country name when touching a composer.

In `page-faq.mdx` only, scope subheadings are written in bold (`**Spain**`); everywhere else (page-compliance, app-*, guide-*) they are plain text. See the composer rules below.

## Leaf format

A leaf is a sequence of bare `<Accordion>` blocks. **Never wrap in `<AccordionGroup>` inside a leaf** — the composer does that, which lets one accordion group span multiple leaves (e.g. all four tasks of one scope).

```mdx
<Accordion title="What is …?">…</Accordion>
<Accordion title="How does …?">…</Accordion>
```

Leaves can have their own MDX imports for shared snippets (absolute paths starting `/snippets/...`).

**Auto-generated content marker.** When a question is drafted by an automated pass, prepend `¿ ` to the title. Strip the prefix once a human has reviewed the answer. Find unreviewed accordions:

```sh
grep -rl '<Accordion title="¿' snippets/faqs/
```

## Composer types

Each consumer page imports one composer from `snippets/faqs/<country>/composers/`.

| Composer | Used by | Organised by | Renders |
|---|---|---|---|
| `page-faq.mdx` | `faq/<country>.mdx` | task (Compliance + 4 task sections) | All scopes × Compliance + all four tasks |
| `page-compliance.mdx` | `compliance/<country>.mdx` | scope | Compliance file × all scopes |
| `app-<regime>.mdx` | `apps/<file>.mdx` | task | Country scope + `<regime>`, all four tasks (no compliance) |
| `guide-<regime>-<task>.mdx` | `guides/<file>.mdx` | single group | Country scope + `<regime>` for one task |

### Task ordering

Always use this order, matching the natural document flow: **Invoicing → Supplier → Receiving → Reporting**. Skip tasks that don't apply.

Compliance comes first when present (it sets the regulatory frame before operational details).

### Composer body

Wrap each group of leaves in one `<AccordionGroup>`. The "only one open at a time" UX applies within a group.

#### `page-faq.mdx` — five sections, scope subheadings in **bold**

```mdx
import EsCompliance from '/snippets/faqs/es/leaves/general/compliance.mdx';
import VfCompliance from '/snippets/faqs/es/leaves/verifactu/compliance.mdx';
import EsInv from '/snippets/faqs/es/leaves/general/invoicing.mdx';
import VfInv from '/snippets/faqs/es/leaves/verifactu/invoicing.mdx';
…

### Compliance questions

**Spain**
<AccordionGroup>
  <EsCompliance />
</AccordionGroup>

**VERI*FACTU**
<AccordionGroup>
  <VfCompliance />
</AccordionGroup>

### Invoicing questions

**Spain**
<AccordionGroup>
  <EsInv />
</AccordionGroup>

**VERI*FACTU**
<AccordionGroup>
  <VfInv />
</AccordionGroup>

### Registering supplier questions
…

### Receiving questions
…

### Reporting questions
…
```

#### `page-compliance.mdx` — scope groups, plain-text scope labels, no h3 headings

```mdx
Spain
<AccordionGroup>
  <EsCompliance />
</AccordionGroup>

VERI*FACTU
<AccordionGroup>
  <VfCompliance />
</AccordionGroup>
```

#### `app-<regime>.mdx` — task-organised, plain-text task headings, mixed scopes

One `<AccordionGroup>` per task, holding the task leaf from each scope (country scope first, then regimes alphabetically). No compliance — that lives on the compliance page.

```mdx
import GenInv from '/snippets/faqs/es/leaves/general/invoicing.mdx';
import VfInv from '/snippets/faqs/es/leaves/verifactu/invoicing.mdx';
…

Invoicing questions
<AccordionGroup>
  <GenInv />
  <VfInv />
</AccordionGroup>

Registering supplier questions
<AccordionGroup>
  …
</AccordionGroup>
```

#### `guide-<regime>-<task>.mdx` — single AccordionGroup, no heading

```mdx
import GenInv from '/snippets/faqs/it/leaves/general/invoicing.mdx';
import SdiInv from '/snippets/faqs/it/leaves/sdi/invoicing.mdx';

<AccordionGroup>
  <GenInv />
  <SdiInv />
</AccordionGroup>
```

If the guide spans several tasks, use the same task-organised shape as `app-<regime>.mdx`.

### Wiring a Peppol-using country

In BE, DE, FR composers, Peppol acts as another scope alongside the country scope and any country-specific regimes:

```mdx
import PepCompliance from '/snippets/faqs/peppol/leaves/compliance.mdx';
import PepInv from '/snippets/faqs/peppol/leaves/invoicing.mdx';
…

**Peppol**
<AccordionGroup>
  <PepCompliance />
</AccordionGroup>
```

## Consumer page wiring

```mdx
import FAQ from '/snippets/faqs/<country>/composers/<composer>.mdx';

## FAQ

<FAQ />

More available in our [<Country> FAQ](/faq/<country>) section
```

`compliance/<country>.mdx` uses `### Compliance questions` instead of `## FAQ`.

## Recipes

**Add a question.** Pick the cell:
- If the answer is regulatory → append `<Accordion>` to `<scope>/compliance.mdx`.
- Otherwise → append to `<scope>/<task>.mdx` (where `<task>` is invoicing/supplier/receiving/reporting).

No composer changes.

For single-regime countries, country-level operations or tech content goes into the regime's task leaf (since there's no `country/<task>.mdx` file). Only country-level *compliance* lives in `country/compliance.mdx`.

**Move a question.** Cut from source leaf, paste into target leaf. No composer changes.

**Reorder within a cell.** Reorder `<Accordion>` blocks in the leaf.

**Remove a cell.** Delete the leaf and remove every composer's import + JSX usage. Composers must never reference a missing leaf.

**Add a regime to a country.**
1. Add the row to the manifest.
2. Decide which tasks apply.
3. Create only the leaves with content: `leaves/<regime>/{compliance,invoicing,supplier,receiving,reporting}.mdx` (skip files that have no content).
4. Add the regime block to `page-faq.mdx` and `page-compliance.mdx`.
5. Create `app-<regime>.mdx` and any guide composers.

**Hook a Peppol country into Peppol leaves.** In each affected composer, import the relevant `peppol/leaves/...` files and add a Peppol scope group.

**Bulk-import questions.** Cluster source data into either `compliance` (regulatory) or one of the four task buckets, then append `<Accordion>` blocks to the matching leaves. No structural changes.

## Consumer page registry

| Consumer page | Composer |
|---|---|
| `faq/argentina.mdx` | `ar/composers/page-faq.mdx` |
| `compliance/argentina.mdx` | `ar/composers/page-compliance.mdx` |
| `apps/argentina.mdx` | `ar/composers/app-arca.mdx` |
| `guides/ar-arca-invoices.mdx` | `ar/composers/guide-arca-invoicing.mdx` |
| `guides/ar-arca-suppliers.mdx` | `ar/composers/guide-arca-supplier.mdx` |
| `faq/belgium.mdx` | `be/composers/page-faq.mdx` |
| `compliance/belgium.mdx` | `be/composers/page-compliance.mdx` |
| `guides/be-peppol.mdx` | `be/composers/guide-peppol-invoicing.mdx` |
| `faq/brazil.mdx` | `br/composers/page-faq.mdx` |
| `compliance/brazil.mdx` | `br/composers/page-compliance.mdx` |
| `apps/documentos-fiscais-electronicos-brazil.mdx` | `br/composers/app-dfe.mdx` |
| `guides/br-dfe.mdx` | `br/composers/guide-dfe-invoicing.mdx` |
| `faq/germany.mdx` | `de/composers/page-faq.mdx` |
| `compliance/germany.mdx` | `de/composers/page-compliance.mdx` |
| `guides/de-ubl.mdx` | `de/composers/guide-peppol-invoicing.mdx` |
| `faq/spain.mdx` | `es/composers/page-faq.mdx` |
| `compliance/spain.mdx` | `es/composers/page-compliance.mdx` |
| `apps/spain.mdx` | `es/composers/app-spain.mdx` |
| `apps/verifactu-spain.mdx` | `es/composers/app-verifactu.mdx` |
| `apps/ticketbai-spain.mdx` | `es/composers/app-ticketbai.mdx` |
| `apps/facturae-spain.mdx` | `es/composers/app-facturae.mdx` |
| `guides/es-verifactu.mdx` | `es/composers/guide-verifactu-invoicing.mdx` |
| `guides/es-verifactu-supplier.mdx` | `es/composers/guide-verifactu-supplier.mdx` |
| `guides/es-ticketbai.mdx` | `es/composers/guide-ticketbai-invoicing.mdx` |
| `guides/es-ticketbai-supplier.mdx` | `es/composers/guide-ticketbai-supplier.mdx` |
| `guides/es-sii.mdx` | `es/composers/guide-sii-invoicing.mdx` |
| `guides/es-sii-supplier.mdx` | `es/composers/guide-sii-supplier.mdx` |
| `guides/es-noverifactu.mdx` | `es/composers/guide-noverifactu-invoicing.mdx` |
| `guides/es-noverifactu-supplier.mdx` | `es/composers/guide-noverifactu-supplier.mdx` |
| `guides/es-facturae.mdx` | `es/composers/guide-facturae-invoicing.mdx` |
| `faq/france.mdx` | `fr/composers/page-faq.mdx` |
| `compliance/france.mdx` | `fr/composers/page-compliance.mdx` |
| `apps/choruspro-france.mdx` | `fr/composers/app-choruspro.mdx` |
| `guides/fr-pa.mdx` | `fr/composers/app-pa.mdx` |
| `guides/fr-pa-invoicing.mdx` | `fr/composers/guide-pa-invoicing.mdx` |
| `guides/fr-pa-registration.mdx` | `fr/composers/guide-pa-supplier.mdx` |
| `guides/fr-pa-reporting.mdx` | `fr/composers/guide-pa-reporting.mdx` |
| `guides/fr-pa-status.mdx` | `fr/composers/guide-pa-reporting.mdx` |
| `guides/fr-chorus-pro.mdx` | `fr/composers/guide-choruspro-invoicing.mdx` |
| `faq/greece.mdx` | `gr/composers/page-faq.mdx` |
| `compliance/greece.mdx` | `gr/composers/page-compliance.mdx` |
| `apps/ilyda-greece.mdx` | `gr/composers/app-mydata.mdx` |
| `guides/gr-iapr.mdx` | `gr/composers/guide-mydata-invoicing.mdx` |
| `faq/italy.mdx` | `it/composers/page-faq.mdx` |
| `compliance/italy.mdx` | `it/composers/page-compliance.mdx` |
| `apps/sdi-italy.mdx` | `it/composers/app-sdi.mdx` |
| `apps/smart-receipts-italy.mdx` | `it/composers/app-ticket.mdx` |
| `guides/it-sdi-sending.mdx` | `it/composers/guide-sdi-invoicing.mdx` |
| `guides/it-sdi-receiving.mdx` | `it/composers/guide-sdi-receiving.mdx` |
| `guides/it-ticket.mdx` | `it/composers/guide-ticket-invoicing.mdx` |
| `faq/mexico.mdx` | `mx/composers/page-faq.mdx` |
| `compliance/mexico.mdx` | `mx/composers/page-compliance.mdx` |
| `apps/sat-mexico.mdx` | `mx/composers/app-sat.mdx` |
| `guides/mx-sat-issuing.mdx` | `mx/composers/guide-sat-invoicing.mdx` |
| `guides/mx-sat-receiving.mdx` | `mx/composers/guide-sat-receiving.mdx` |
| `faq/poland.mdx` | `pl/composers/page-faq.mdx` |
| `compliance/poland.mdx` | `pl/composers/page-compliance.mdx` |
| `apps/poland.mdx` | `pl/composers/app-ksef.mdx` |
| `guides/pl-ksef.mdx` | `pl/composers/guide-ksef-invoicing.mdx` |
| `faq/portugal.mdx` | `pt/composers/page-faq.mdx` |
| `compliance/portugal.mdx` | `pt/composers/page-compliance.mdx` |
| `apps/at-portugal.mdx` | `pt/composers/app-at.mdx` |
| `guides/pt-at.mdx` | `pt/composers/guide-at-invoicing.mdx` |
| `faq/saudi-arabia.mdx` | `sa/composers/page-faq.mdx` |
| `apps/saudi-arabia.mdx` | `sa/composers/app-zatca.mdx` |
| `guides/sa-zatca-clearance-reporting.mdx` | `sa/composers/guide-zatca-invoicing.mdx` |
| `guides/sa-zatca-registration.mdx` | `sa/composers/guide-zatca-supplier.mdx` |

## Categorising new questions

Decide whether the answer is **compliance** (goes in `compliance.mdx`) or **task content** (goes in the relevant `<task>.mdx`):

- **compliance** — regulatory / legal: who must comply, what does the law say, deadlines, mandates, scope, archival rules.
- **task content** (operations + tech mixed) — anything else: how to run a flow, error codes, GOBL field mappings, supplier registration, cancellations, time zones.

Pick the task by what the question is *about*: invoicing for issuance flow, supplier for onboarding/registration, receiving for inbound, reporting for periodic returns.

## Validation checklist

- [ ] Every regime in the manifest has a folder under `<country>/leaves/`.
- [ ] Each leaf file (`compliance.mdx` or `<task>.mdx`) has at least one `<Accordion>`. No empties.
- [ ] No leaf contains `<AccordionGroup>` — wrappers belong in composers.
- [ ] Every composer's imports resolve to existing leaves.
- [ ] No consumer page imports a leaf directly — always via a composer.
- [ ] Country-scope subheadings use the country name, not `General`.
- [ ] Single-regime countries: country scope is a single `country/compliance.mdx`. No task files at country scope.
- [ ] `page-faq.mdx` uses 5 sections: Compliance + Invoicing + Supplier + Receiving + Reporting.
- [ ] Task ordering everywhere: Compliance → Invoicing → Supplier → Receiving → Reporting.
- [ ] Outside `page-faq.mdx`, scope/task headings are plain text (no bold, no italic).
- [ ] Every non-compliance leaf maps to a task we actually document — no `receiving.mdx` if there's no receiving guide, no `reporting.mdx` if periodic reporting is filed outside Invopop.

```sh
# Find broken composer imports
for f in $(find snippets/faqs -path "*/composers/*.mdx"); do
  for path in $(grep -oE "/snippets/faqs/[a-z]+/leaves(/[a-z]+){1,2}\.mdx" "$f"); do
    real="snippets/faqs/${path#/snippets/faqs/}"
    [ ! -f "$real" ] && echo "BROKEN: $f -> $real"
  done
done

# Find leaves that wrongly contain AccordionGroup (should be empty)
grep -rl "AccordionGroup" $(find snippets/faqs -path "*/leaves/*")

# Find composers still using the deprecated **General** label
grep -rln '\*\*General\*\*' snippets/faqs/*/composers/

# Find leaves still using the legacy task/category subdirectory layout (should be empty)
find snippets/faqs -type d -name invoicing -path "*/leaves/*"

# Audit: every non-compliance leaf should have a corresponding guide flow.
# Lists leaves alongside the country's guides so you can eyeball mismatches.
python3 - <<'PY'
import pathlib
for cc_leaves in sorted(pathlib.Path("snippets/faqs").glob("*/leaves")):
    cc = cc_leaves.parent.name
    if cc == "peppol":
        continue
    guides = sorted(g.name for g in pathlib.Path("guides").glob(f"{cc}-*.mdx"))
    print(f"{cc}: guides = {guides}")
    for scope_dir in sorted(cc_leaves.iterdir()):
        if not scope_dir.is_dir():
            continue
        files = sorted(f.name for f in scope_dir.glob("*.mdx"))
        print(f"  {scope_dir.name}: {files}")
PY
```
