#!/bin/bash
# Prepend ¿ to every <Accordion title="…"> in leaves I auto-generated.
# The list below is the inverse: cells that were hand-curated and should NOT be marked.

set -euo pipefail

# Hand-curated cells (these stay clean, no ¿ marker)
curated=(
  # Argentina
  "ar/leaves/general/invoicing/compliance.mdx"
  "ar/leaves/arca/invoicing/compliance.mdx"
  "ar/leaves/arca/invoicing/operations.mdx"
  "ar/leaves/arca/invoicing/tech.mdx"
  "ar/leaves/arca/supplier/operations.mdx"
  # Belgium
  "be/leaves/peppol/invoicing/compliance.mdx"
  "be/leaves/peppol/invoicing/operations.mdx"
  "be/leaves/peppol/invoicing/tech.mdx"
  # Brazil
  "br/leaves/general/invoicing/compliance.mdx"
  "br/leaves/general/invoicing/operations.mdx"
  "br/leaves/general/invoicing/tech.mdx"
  "br/leaves/nfe/invoicing/tech.mdx"
  "br/leaves/nfse/invoicing/compliance.mdx"
  "br/leaves/nfse/invoicing/tech.mdx"
  # Germany
  "de/leaves/peppol/invoicing/compliance.mdx"
  "de/leaves/peppol/invoicing/tech.mdx"
  # Spain
  "es/leaves/general/invoicing/compliance.mdx"
  "es/leaves/general/invoicing/operations.mdx"
  "es/leaves/general/supplier/operations.mdx"
  "es/leaves/verifactu/invoicing/compliance.mdx"
  "es/leaves/verifactu/invoicing/operations.mdx"
  "es/leaves/verifactu/invoicing/tech.mdx"
  "es/leaves/ticketbai/invoicing/compliance.mdx"
  "es/leaves/ticketbai/invoicing/tech.mdx"
  "es/leaves/sii/invoicing/compliance.mdx"
  "es/leaves/sii/invoicing/operations.mdx"
  "es/leaves/sii/invoicing/tech.mdx"
  "es/leaves/facturae/invoicing/tech.mdx"
  # France
  "fr/leaves/general/invoicing/tech.mdx"
  "fr/leaves/pa/invoicing/compliance.mdx"
  "fr/leaves/pa/invoicing/operations.mdx"
  "fr/leaves/pa/reporting/compliance.mdx"
  "fr/leaves/choruspro/invoicing/operations.mdx"
  "fr/leaves/choruspro/supplier/operations.mdx"
  # Greece
  "gr/leaves/mydata/invoicing/compliance.mdx"
  "gr/leaves/mydata/invoicing/tech.mdx"
  # Italy
  "it/leaves/sdi/invoicing/compliance.mdx"
  "it/leaves/sdi/invoicing/operations.mdx"
  "it/leaves/sdi/invoicing/tech.mdx"
  "it/leaves/sdi/receiving/operations.mdx"
  "it/leaves/ticket/invoicing/operations.mdx"
  # Mexico
  "mx/leaves/sat/invoicing/compliance.mdx"
  "mx/leaves/sat/invoicing/operations.mdx"
  "mx/leaves/sat/invoicing/tech.mdx"
  "mx/leaves/sat/supplier/operations.mdx"
  "mx/leaves/sat/reporting/operations.mdx"
  # Poland
  "pl/leaves/ksef/invoicing/compliance.mdx"
  "pl/leaves/ksef/invoicing/operations.mdx"
  "pl/leaves/ksef/invoicing/tech.mdx"
  "pl/leaves/ksef/supplier/operations.mdx"
  "pl/leaves/ksef/receiving/operations.mdx"
  # Portugal
  "pt/leaves/at/invoicing/compliance.mdx"
  "pt/leaves/at/invoicing/operations.mdx"
  "pt/leaves/at/invoicing/tech.mdx"
)

# Build an associative-array-style lookup
is_curated() {
  local target="$1"
  for c in "${curated[@]}"; do
    [ "snippets/faqs/$c" = "$target" ] && return 0
  done
  return 1
}

count=0
for f in $(find snippets/faqs -name "*.mdx" -path "*/leaves/*" | sort); do
  if is_curated "$f"; then
    continue
  fi
  # Prepend ¿ to every <Accordion title="…"> that doesn't already have it
  if grep -q '<Accordion title="¿' "$f"; then
    continue
  fi
  sed -i.bak 's/<Accordion title="\([^¿]\)/<Accordion title="¿ \1/g' "$f"
  rm "$f.bak"
  count=$((count+1))
done
echo "Marked $count files"
