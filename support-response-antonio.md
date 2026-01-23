# Support Response - Credit Note from Migrated Invoice

Hi Antonio,

Thank you for reaching out. I understand you're trying to create a credit note for an invoice that was originally issued through your previous provider before migrating to Invopop.

The error "Preceding document (FT PFA2025/1605) is not recorded" occurs because Invopop needs to validate that the original invoice exists in the system before it can create a credit note that references it. Since the invoice was created outside Invopop, it's not currently recorded in your silo.

## Solution: Upload the Original Invoice First

To create a credit note for an existing validated invoice, you'll need to first upload the original invoice to your Invopop silo. Once it's recorded, you can then create the credit note referencing it.

### Step 1: Upload the Original Invoice

Upload the original invoice (FT PFA2025/1605) to your silo using the [Create an Entry](/api-ref/silo/entries/create-an-entry-post) endpoint. You can upload it as a GOBL document with all the original details, including:
- The original `series` (FT)
- The original `code` (PFA2025/1605)
- The original `issue_date`
- All other invoice details

This will create a silo entry for the invoice, making it "recorded" in the system.

### Step 2: Create the Credit Note

Once the original invoice is in your silo, you have two options:

#### Option A: Auto-Generate Credit Note (Recommended)

Use the auto-generation feature, which will handle all the complex details automatically:

```json
{
  "correct": { "type": "credit-note" },
  "previous_id": "silo_entry_id_of_original_invoice"
}
```

This approach is particularly useful for Portugal, as it automatically handles all the required references and tax calculations.

#### Option B: Upload a Complete Credit Note

Alternatively, you can upload a fully defined credit note with a `preceding` block that references the original invoice by its silo entry UUID:

```json
{
  "content_type": "application/json",
  "data": {
    "$schema": "https://gobl.org/draft-0/bill/credit-note",
    "type": "credit-note",
    "preceding": [
      {
        "uuid": "silo_entry_uuid_of_original_invoice",
        "type": "standard",
        "issue_date": "2025-01-XX",
        "series": "FT",
        "code": "PFA2025/1605"
      }
    ]
    // ... rest of credit note details
  }
}
```

## Important Notes

- The original invoice must be uploaded to the silo before creating the credit note, as the system validates the preceding document reference during the sealing process.
- For Portugal invoices, ensure you include the `pt-saft-v1` addon and set `$regime` to `PT` when uploading the original invoice.
- After uploading the original invoice, you don't need to run it through any workflows—it just needs to exist in the silo for reference purposes.

If you need help with the specific structure for uploading your Portugal invoice, or if you encounter any issues during this process, please don't hesitate to reach out.

Best regards,
Mark MacKay
