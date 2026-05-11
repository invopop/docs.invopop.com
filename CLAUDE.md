# Project instructions

This is the Mintlify-powered documentation site for [docs.invopop.com](https://docs.invopop.com). Content is authored in MDX, navigation is declared in `docs.json`, and the API reference is generated from OpenAPI specs.

## Writing style

- Always use sentence case for titles and headings, never title case (e.g. "TicketBAI supplier onboarding guide" not "TicketBAI Supplier Onboarding Guide").
- Preserve canonical brand spelling in body text (e.g. `VERI*FACTU`, `TicketBAI`, `Peppol`, `Chorus Pro`, `KSeF`, `SAT/CFDI`). When the asterisk or punctuation must be literal inside MDX, escape it (`VERI\*FACTU`).
- Frontmatter on every page must include `title` and `description`. Use `sidebarTitle` to override the navigation label when it would otherwise be long.

## Repository layout

Top-level content directories — each `.mdx` file under these maps directly to a page slug (`/<dir>/<file>`):

- `index.mdx`, `home.mdx` — site root.
- `get-started/` — quickstart, pricing.
- `compliance/` — per-country compliance pages (one `.mdx` per country, plus regional overviews like `americas.mdx`, `europe.mdx`).
- `timelines/` — country regulation timelines.
- `faq/` — per-country FAQ pages. These import a single composer from `snippets/faqs/<country>/composers/page-faq.mdx`.
- `guides/` — tutorials and how-tos, organised by country, feature, integration.
- `apps/` — one page per Invopop app (Government, Network, Notify, Format, Document, Storage, Automation, Integrations).
- `console/`, `admin/`, `workspace/` — Console and Admin platform docs.
- `api-ref/` — handwritten API guidance plus one `.mdx` per OpenAPI operation. The operation pages are very thin wrappers around the spec.
- `changelog/` — changelog entries.

Supporting directories:

- `openapi/` — OpenAPI 3 specs. Each YAML is registered in `docs.json` under `openapi`; Mintlify generates reference pages from operations the registry references.
- `snippets/` — reusable MDX fragments imported by pages (see below).
- `assets/` — images, logos, diagrams referenced from MDX.
- `scripts/` — small shell scripts that maintain `snippets/faqs/` (`fill-empty-faqs.sh`, `mark-generated.sh`).
- `gobl-build.sh`, `gobl-unbuild.rb` — GOBL invoice example tooling (see below).
- `skills/` — packaged authoring skills (currently `manage-faqs`). Read the skill's `SKILL.md` before doing the work it covers.

## Navigation (`docs.json`)

`docs.json` is the source of truth for site structure, theme, OpenAPI registration, redirects, and footer/navbar links. Whenever you add a new `.mdx` page, add it to the relevant `pages` array under `navigation.tabs` — otherwise it won't appear in the sidebar. When you move or rename a page, add a `redirects` entry rather than relying on URL stability.

Tabs (in order): Get Started, Platform, Guides, Apps, API Reference. The country compliance tree under Get Started groups countries by region (Americas, Asia, Europe, Middle East, Oceania). Country groups use flag emojis in their `group` label.

## Snippets system

`snippets/` holds MDX fragments imported by pages via absolute paths starting `/snippets/...`. Subtrees:

- `snippets/faqs/` — country FAQ leaves + composers. **Read `skills/manage-faqs/SKILL.md` before touching this tree.** Layout in brief: `<country>/leaves/<scope>/{compliance,invoicing,supplier,receiving,reporting}.mdx` hold bare `<Accordion>` blocks; `<country>/composers/<consumer>.mdx` wrap leaves in `<AccordionGroup>` for a specific consumer page (`page-faq`, `page-compliance`, `app-<regime>`, `guide-<regime>-<task>`). Consumer pages import exactly one composer.
- `snippets/invoices/<country>/` — GOBL invoice example fragments. Files come in pairs: `<name>.min.mdx` (minimal hand-authored input) and `<name>.mdx` (built output produced by `gobl-build.sh`). Edit the `.min.mdx`; rebuild to refresh the `.mdx`.
- `snippets/suppliers/`, `snippets/payments/`, `snippets/deliveries/`, `snippets/documents/`, `snippets/coverage/` — country-scoped GOBL examples for other document/flow types, same `.min.mdx`/`.mdx` pairing where applicable.
- `snippets/workflows/<country|integration>/` — reusable workflow descriptions.
- `snippets/tables/<country>-resources.mdx` — country resource tables embedded by compliance pages.

When you import a snippet, prefer giving the import a country-prefixed component name to avoid collisions when a page composes snippets from multiple countries (e.g. `EsCompliance`, `VfInv`).

## GOBL invoice examples workflow

The `.min.mdx` / `.mdx` pairing in `snippets/invoices/` (and the other GOBL-example subtrees) is maintained by two scripts. Both require the `gobl` CLI on `PATH`.

- `./gobl-build.sh` — finds every `*.min.mdx`, extracts the JSON code block, runs `gobl build` (which calculates totals, fills UUIDs, validates), and writes the full output to the matching `*.mdx`. The output block title is hardcoded to `Built version`.
- `ruby gobl-unbuild.rb <file>` — reverse direction: strip a built GOBL document down to the minimal input by removing fields that don't affect the digest, plus all UUIDs. Use `-i` to modify in place. Useful when promoting a hand-authored full example back to a `.min.mdx`.

Never edit `<name>.mdx` directly — your changes will be lost the next time `gobl-build.sh` runs. Edit `<name>.min.mdx` and rebuild.

## API reference pages

Each operation under `api-ref/<service>/...` is a small `.mdx` page that points Mintlify at a specific OpenAPI operation. The OpenAPI YAMLs in `openapi/` are the substantive source. To add an endpoint:

1. Add the operation to the relevant `openapi/<service>_v1.yaml`.
2. Create a thin `api-ref/<service>/<group>/<op>.mdx` mirroring the existing siblings.
3. Register the page in `docs.json` under the matching API Reference group.

`mint openapi-check <file>` validates an OpenAPI spec locally.

## FAQ tooling

Two helper scripts maintain `snippets/faqs/`:

- `scripts/fill-empty-faqs.sh` — generates a single placeholder `<Accordion>` for every empty `leaves/*/(compliance|invoicing|supplier|receiving|reporting).mdx`, with a question tailored to the (country, scope, task, category). The placeholders carry a `*Placeholder — to be replaced with reviewed content.*` body and exist so composers don't import empty files.
- `scripts/mark-generated.sh` — prepends `¿ ` to every `<Accordion title>` in leaves that weren't on the hand-curated allowlist inside the script. The marker means "auto-drafted, not human-reviewed". To find unreviewed questions: `grep -rl '<Accordion title="¿' snippets/faqs/`. Strip the prefix when a human signs off on the answer.

If you add a country or regime to the FAQ system, update the allowlist in `scripts/mark-generated.sh` so future runs don't re-mark curated cells.

## Local development

Prereqs: Node.js + the Mintlify CLI (`npm i -g mint`). For GOBL example tooling: the `gobl` CLI and Ruby 3+.

```
mint dev                 # local preview at http://localhost:3000
mint broken-links        # report broken cross-references
mint openapi-check FILE  # validate one OpenAPI spec
mint rename OLD NEW      # rename a page and rewrite every reference
mint update              # update the CLI if local preview drifts from prod
```

There is no `package.json`, build step, or test suite at the repo root — Mintlify owns the build, and PRs are previewed by the Mintlify GitHub app. The only repo-local scripts are the GOBL and FAQ tooling above.

## Conventions and gotchas

- **Asterisks in MDX**: escape `*` inside body text where it would otherwise start emphasis (`VERI\*FACTU`). Inside `<Accordion title="…">` or other JSX prop strings, the literal `*` is fine.
- **Imports**: snippets import paths are absolute and start `/snippets/...`. Page-to-page links are root-relative (`/guides/es-verifactu`), not file paths.
- **Country folder slugs are ISO-2 lowercase** in `snippets/` (`ar`, `be`, `br`, `de`, `es`, `fr`, `gr`, `it`, `mx`, `pl`, `pt`). Page filenames under `compliance/`, `faq/`, `timelines/` use the full country name (`compliance/spain.mdx`).
- **Region pages** (`compliance/americas.mdx`, `compliance/europe.mdx`, etc.) are the parent pages of each regional group in the nav — they generally summarise their region.
- **Redirects**: prefer adding to `docs.json` `redirects` over leaving stale slugs. Many existing redirects fold legacy `/guides/countries/...` and `/guides/features/...` paths into the flatter current structure.
- **No README/doc creation by default**: only create new top-level `.md`/`.mdx` files when explicitly asked, or when adding a new documentation page that belongs in the nav.
- **Branch policy**: develop on the branch specified in the session brief; never push to `main` directly.
