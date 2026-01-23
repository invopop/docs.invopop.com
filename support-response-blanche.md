# Support Response - PDF Embedding in Peppol UBL Invoices

Hi Blanche,

Thank you for reaching out, and thank you to David Jones for the referral.

I understand your concern about PDF previews not displaying in receiver access points for your Peppol invoices. This is indeed an important aspect of the user experience for your customers.

## Sending PDFs with Invoices

To include a PDF file with your invoices when sending through Peppol, you should use the **Create a File** endpoint to attach the PDF to your silo entry before exporting:

**POST** `/silo/v1/entries/{entry_id}/files`

This endpoint allows you to attach files (including PDFs) to your invoice entries. When you attach a PDF file with the appropriate category (typically `"format"` for human-readable documents), it will be properly embedded in the UBL output as an `AdditionalDocumentReference` when exporting to Peppol BIS Billing 3.0 format.

You can provide the PDF data inline as base64-encoded content, or create a placeholder and upload the file separately. The file will be automatically included in the Peppol UBL output in the `cac:AdditionalDocumentReference` structure you mentioned.

Documentation: https://docs.invopop.com/api-ref/silo/entries/files-post

## Receiving PDFs from Peppol Invoices

When you receive Peppol invoices that include embedded PDFs, you can retrieve these files using the **Fetch a File** endpoint:

**GET** `/silo/v1/entries/{entry_id}/files/{id}`

This allows you to download any PDF files that were embedded in incoming Peppol invoices, which you can then use for preview or storage purposes.

Documentation: https://docs.invopop.com/api-ref/silo/entries/files-fetch

## Peppol Compliance

This approach maintains full Peppol BIS Billing 3.0 compliance, as the PDF is properly embedded in the UBL structure according to the standard. The file attachment system is designed to work seamlessly with Peppol exports, ensuring that receiver access points can properly extract and display the embedded PDFs.

If you need any assistance implementing this, or if you encounter any issues with PDF embedding in your Peppol exports, please don't hesitate to reach out.

Best regards,
[Your Name]
