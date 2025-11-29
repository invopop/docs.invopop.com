# Link Mismatches Report

This report identifies links where the link text doesn't match the URL destination.

## Issues Found

### 1. Incorrect Path: `/guides/countries/` (should be `/guides/`)

The directory `/guides/countries/` doesn't exist. All these links should use `/guides/` instead.

#### Files with this issue:

1. **guides/it-ticket.mdx** (Line 371)
   - Link: `[SDI](/guides/countries/it-sdi-sending)`
   - Should be: `/guides/it-sdi-sending`

2. **guides/de-zugferd.mdx** (Line 13)
   - Link: `[Factur-X](/guides/countries/fr-facturx)`
   - Should be: `/guides/fr-facturx`

3. **guides/it-sdi-sending.mdx** (Lines 19, 160, 188)
   - Link: `[Italy - SDI: Receiving Invoices](/guides/countries/it-sdi-receiving)`
   - Should be: `/guides/it-sdi-receiving`

4. **guides/es-verifactu.mdx** (Line 29)
   - Link: `[VERI*FACTU supplier registration guide](/guides/countries/es-verifactu-supplier)`
   - Should be: `/guides/es-verifactu-supplier`

5. **guides/es-verifactu-supplier.mdx** (Lines 120, 146, 187, 421)
   - Links:
     - `[what happens if a supplier validation is rejected](/guides/countries/es-verifactu#what-happens-if-a-supplier-validation-is-rejected)` (lines 120, 146)
     - `[VERI\*FACTU Invoicing setup](/guides/countries/es-verifactu)` (line 187)
     - `[Unregister Supplier workflow](/guides/countries/es-verifactu#template-3)` (line 421)
   - Should be: `/guides/es-verifactu` (with appropriate anchors)

6. **guides/it-sdi-receiving.mdx** (Lines 16, 212)
   - Link: `[Italy - SDI: Sending Invoices](/guides/countries/it-sdi-sending)`
   - Should be: `/guides/it-sdi-sending`

7. **apps/invoicexpress-portugal.mdx** (Line 43)
   - Link: `[InvoiceXpress Guide](/guides/countries/pt-invoicexpress)`
   - Should be: `/guides/pt-invoicexpress`

8. **apps/ticketbai-spain.mdx** (Line 40)
   - Link: `[TicketBAI implementation guide](/guides/countries/es-ticketbai)`
   - Should be: `/guides/es-ticketbai`

9. **apps/at-portugal.mdx** (Line 34)
   - Link: `[Implementation&nbsp;guide](/guides/countries/pt-at)`
   - Should be: `/guides/pt-at`

### 2. Wrong App Link

10. **console/apps.mdx** (Line 39)
    - Link: `[Slack](/apps/email)`
    - Issue: Link text says "Slack" but URL points to `/apps/email`
    - Should be: `/apps/slack`

### 3. Anchor Typo

11. **compliance/spain.mdx** (Line 23)
    - Link: `[invoice regulation in Spain](#regluation)`
    - Issue: Typo in anchor - `#regluation` should be `#regulation`
    - Should be: `#regulation`

### 4. Semantic Mismatches

12. **guides/peppol.mdx** (Line 248)
    - Link: `[quickstart guide](/api-ref/introduction)`
    - Issue: Link text says "guide" but URL points to API reference introduction
    - Note: This might be intentional if the API introduction serves as a guide, but the wording suggests it should point to `/get-started/quickstart`

13. **guides/email.mdx** (Line 114)
    - Link: `[using the API to run a workflow](https://docs.invopop.com/api-ref/transform/jobs/create-a-job-put)`
    - Issue: Link text says "workflow" but URL is about creating a job (PUT method)
    - Note: This might be technically correct since jobs are used to run workflows, but the wording could be clearer

14. **timelines/poland.mdx** (Line 43)
    - Link: `[Poland](#ksef)`
    - Issue: Link text says "Poland" but anchor is `#ksef` (which refers to the KSeF system)
    - Should be: `[KSeF](#ksef)` to match the anchor and context

## Summary

- **Total issues found**: 14 unique issues across 19 link instances
- **Most common issue**: Incorrect `/guides/countries/` path (15 instances across 9 files)
- **Critical issues**: 
  - Slack link pointing to email app
  - Anchor typo in Spain compliance page
  - Poland/KSeF link mismatch

