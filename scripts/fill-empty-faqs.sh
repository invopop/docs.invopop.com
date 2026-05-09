#!/bin/bash
# Generate placeholder FAQ content for every empty leaf in snippets/faqs/.
# One plausible accordion per cell, scoped by (country, scope, task, category).
# These are stubs — replace the answers with reviewed content as it lands.

set -euo pipefail

country_label() {
  case "$1" in
    ar) echo "Argentina";; be) echo "Belgium";; br) echo "Brazil";;
    de) echo "Germany";; es) echo "Spain";; fr) echo "France";;
    gr) echo "Greece";; it) echo "Italy";; mx) echo "Mexico";;
    pl) echo "Poland";; pt) echo "Portugal";;
  esac
}

regime_label() {
  case "$1" in
    general) echo "";;
    arca) echo "ARCA";; peppol) echo "Peppol";;
    nfe) echo "NF-e";; nfse) echo "NFS-e";;
    verifactu) echo "VERI*FACTU";; ticketbai) echo "TicketBAI";;
    sii) echo "SII";; noverifactu) echo "No-VERI*FACTU";;
    facturae) echo "Facturae";;
    pa) echo "PA";; choruspro) echo "Chorus Pro";;
    mydata) echo "myDATA";; sdi) echo "SDI";; ticket) echo "Smart Receipts";;
    sat) echo "SAT/CFDI";; ksef) echo "KSeF";; at) echo "AT (SAF-T)";;
  esac
}

# Title pattern per (task, category, scope-kind=general|regime)
title() {
  local task="$1" cat="$2" country="$3" regime="$4"
  local clbl rlbl key
  clbl=$(country_label "$country")
  rlbl=$(regime_label "$regime")
  key="$task/$cat"
  if [ "$regime" = "general" ]; then
    case "$key" in
      invoicing/compliance) echo "What invoicing rules apply across all systems in $clbl?";;
      invoicing/operations) echo "How do I configure my workspace for invoicing in $clbl?";;
      invoicing/tech) echo "Where do I find $clbl-specific GOBL documentation?";;
      supplier/compliance) echo "Who can act as a supplier in $clbl?";;
      supplier/operations) echo "How do I onboard a new supplier in $clbl?";;
      supplier/tech) echo "How are supplier credentials stored in Invopop for $clbl?";;
      receiving/compliance) echo "What are the legal obligations for receiving invoices in $clbl?";;
      receiving/operations) echo "How do I import received invoices in $clbl?";;
      receiving/tech) echo "How does Invopop convert received $clbl invoices into GOBL?";;
      reporting/compliance) echo "What periodic reporting obligations exist in $clbl?";;
      reporting/operations) echo "How do I schedule periodic reports for $clbl?";;
      reporting/tech) echo "What format does $clbl expect for periodic reports?";;
    esac
  else
    case "$key" in
      invoicing/compliance) echo "What are the $rlbl mandate timelines in $clbl?";;
      invoicing/operations) echo "What's the workflow for issuing $rlbl invoices?";;
      invoicing/tech) echo "What GOBL addons are required for $rlbl?";;
      supplier/compliance) echo "Are there special supplier obligations under $rlbl?";;
      supplier/operations) echo "How do I register a supplier with $rlbl?";;
      supplier/tech) echo "What certificates does $rlbl require to authenticate a supplier?";;
      receiving/compliance) echo "What are the legal obligations for receiving invoices through $rlbl?";;
      receiving/operations) echo "How do I import received invoices via $rlbl?";;
      receiving/tech) echo "What format do received $rlbl invoices arrive in?";;
      reporting/compliance) echo "What reporting obligations does $rlbl impose?";;
      reporting/operations) echo "How often must I submit $rlbl reports?";;
      reporting/tech) echo "What format does $rlbl expect for periodic reports?";;
    esac
  fi
}

count=0
for f in $(find snippets/faqs -name "*.mdx" -path "*/leaves/*" -size 0 | sort); do
  # path: snippets/faqs/<country>/leaves/<scope>/<task>/<category>.mdx
  rel="${f#snippets/faqs/}"
  country="${rel%%/*}"
  rest="${rel#*/leaves/}"
  scope="${rest%%/*}"
  rest="${rest#*/}"
  task="${rest%%/*}"
  cat="${rest##*/}"
  cat="${cat%.mdx}"

  q=$(title "$task" "$cat" "$country" "$scope")

  cat > "$f" <<EOF
<AccordionGroup>
  <Accordion title="$q">
    *Placeholder — to be replaced with reviewed content.*
  </Accordion>
</AccordionGroup>
EOF
  count=$((count+1))
done
echo "Filled $count empty leaves"
