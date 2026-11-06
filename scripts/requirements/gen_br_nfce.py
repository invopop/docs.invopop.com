#!/usr/bin/env python3
"""Spike: generate the NFC-e requirements spec (OpenAPI) for the API Reference.

Inputs:
- FIELDS below: the per-field requirements. In the full version, the GOBL part
  comes from the br-nfe-v4 add-on rules and the SEFAZ part from a reviewed
  per-country overlay YAML.
- The built example snippets in snippets/invoices/br/, used as named examples.

Output: openapi/requirements/br-nfce.yaml

Run from the repo root: python3 scripts/requirements/gen_br_nfce.py
"""
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SNIPPETS = ROOT / "snippets/invoices/br"
OUT = ROOT / "openapi/requirements/br-nfce.yaml"
RULES = "https://docs.gobl.org/addons/br-nfe-v4#validation-rules"
MOC = "https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=J%20I%20v4eN00E="


def gobl(*codes):
    return "GOBL: " + ", ".join(f"[`{c}`]({RULES})" for c in codes) + "."


def sefaz(rule, rejection):
    return f"SEFAZ: [MOC]({MOC}) rule `{rule}`, rejection `{rejection}`."


def field(type_, text, *notes, required=False, default=None, enum=None, example=None, xml=None):
    """One field. `required` is GOBL's rule, so it drives the OpenAPI required list."""
    lines = [text]
    if xml:
        lines.append(f"NF-e XML: `{xml}`.")
    lines += list(notes)
    out = {"type": type_, "description": "\n\n".join(lines), "x-required": required}
    if default is not None:
        out["default"] = default
    if enum:
        out["enum"] = enum
    if example is not None:
        out["example"] = example
    return out


def obj(desc, props, extra=None):
    req = [k for k, v in props.items() if v.pop("x-required", False)]
    out = {"type": "object", "description": desc, "properties": props}
    if req:
        out["required"] = req
    if extra:
        out.update(extra)
    return out


def ext(desc, props):
    return obj(desc, props)


address = obj("The establishment's address.", {
    "street": field("string", "Street name.", gobl("INVOICE-04"), required=True, xml="xLgr"),
    "num": field("string", "Street number.", gobl("INVOICE-05"), required=True, xml="nro"),
    "locality": field("string", "Neighbourhood (_bairro_).", gobl("INVOICE-06"), required=True, xml="xBairro"),
    "state": field("string", "Two-letter state code.", gobl("INVOICE-07"), required=True, example="SP", xml="UF"),
    "code": field("string", "Postal code (CEP).", gobl("INVOICE-08"), required=True, example="01426-001", xml="CEP"),
    "country": field("string", "ISO country code. GOBL fills it from the tax ID.", default="BR"),
})

supplier = obj("The establishment issuing the receipt. One registered supplier per establishment.", {
    "name": field("string", "Legal name.", gobl("INVOICE-10"), required=True, xml="xNome"),
    "tax_id": obj("Tax ID.", {
        "country": field("string", "Always `BR`.", required=True, example="BR"),
        "code": field("string", "CNPJ, 14 digits.", gobl("INVOICE-01", "INVOICE-02"), required=True, example="48219376000118", xml="CNPJ"),
    }, {"x-required": True}),
    "identities": {"type": "array", "description": "Add the state registration (IE) with key `br-nfe-state-reg`. GOBL accepts the document without it. SEFAZ needs it.\n\nNF-e XML: `IE`.",
                   "items": {"type": "object", "properties": {"key": {"type": "string", "enum": ["br-nfe-state-reg"]}, "code": {"type": "string", "example": "110042490114"}}}},
    "addresses": {"type": "array", "description": "At least one address. " + gobl("INVOICE-03", "INVOICE-11"), "items": address, "minItems": 1, "x-required": True},
    "ext": ext("Supplier extensions.", {
        "br-ibge-municipality": field("string", "7-digit IBGE municipality code.", gobl("INVOICE-09"), required=True, example="3550308", xml="cMun"),
        "br-nfe-regime": field("string", "Tax regime: `1` Simples Nacional, `2` Simples Nacional excess, `3` normal, `4` MEI. It decides CST or CSOSN on every line.", gobl("INVOICE-39", "INVOICE-42", "INVOICE-43"), default="3", enum=["1", "2", "3", "4"], xml="CRT"),
    }),
})
supplier["required"] = ["name", "tax_id", "addresses", "ext"]
supplier["properties"]["tax_id"].pop("x-required", None)
supplier["properties"]["addresses"].pop("x-required", None)

customer = obj("Optional on an NFC-e. Send it to print the consumer's CPF. SEFAZ requires it above R$10,000 and with home delivery.\n\n" + sefaz("W16-40", "750") + " " + sefaz("E01-20", "787"), {
    "name": field("string", "The consumer's name.", xml="xNome"),
    "tax_id": obj("The consumer's CPF. " + gobl("INVOICE-36"), {
        "country": field("string", "Always `BR`.", example="BR"),
        "code": field("string", "CPF, 11 digits.", gobl("INVOICE-15"), example="39851726419", xml="CPF"),
    }),
    "addresses": {"type": "array", "description": "The delivery address. Needed with presence `4`. " + sefaz("E05-20", "788") + " When sent, " + gobl("INVOICE-16", "INVOICE-17", "INVOICE-21"),
                  "items": address},
    "ext": ext("Customer extensions.", {
        "br-ibge-municipality": field("string", "IBGE code of the customer's city. Required when an address is sent.", gobl("INVOICE-22"), example="3550308"),
        "br-nfe-state-reg-ind": field("string", "Always `9`, non-taxpayer, on an NFC-e.", gobl("INVOICE-53"), default="9", enum=["9"], xml="indIEDest"),
    }),
})

tax_combo = obj("One tax per category: ICMS, PIS and COFINS on every line. " + gobl("LINE-01", "LINE-02", "LINE-03"), {
    "cat": field("string", "Tax category.", required=True, enum=["ICMS", "PIS", "COFINS"]),
    "percent": field("string", "Rate set by the tax advisor. `0%` for ICMS CST `40`, `41`, `60` and every NFC-e CSOSN.", gobl("TAX-COMBO-06", "TAX-COMBO-07"), required=True, example="18%"),
    "ext": ext("Tax codes. GOBL fills the normal-regime defaults.", {
        "br-nfe-icms-cst": field("string", "ICMS CST, normal regime. NFC-e accepts `00`, `20`, `40`, `41`, `60`. `90` is a state option.", gobl("TAX-COMBO-01"), sefaz("N12-30", "766"), default="00", xml="CST"),
        "br-nfe-icms-csosn": field("string", "ICMS CSOSN, Simples Nacional. NFC-e accepts `102`, `103`, `300`, `400`, `500`. `900` is a state option.", gobl("INVOICE-43"), sefaz("N12a-20", "383"), xml="CSOSN"),
        "br-nfe-icms-origin": field("string", "Goods origin. `0` national, `1` direct import, `2` foreign bought in Brazil.", gobl("TAX-COMBO-02"), default="0", xml="orig"),
        "br-nfe-pis-cst": field("string", "PIS CST.", gobl("TAX-COMBO-03"), default="01"),
        "br-nfe-cofins-cst": field("string", "COFINS CST.", gobl("TAX-COMBO-04"), default="01"),
    }),
})

line = obj("One line per product.", {
    "quantity": field("string", "Quantity.", required=True, example="1", xml="qCom"),
    "item": obj("The product.", {
        "name": field("string", "Product name.", required=True, xml="xProd"),
        "price": field("string", "Unit price paid by the consumer, taxes included.", required=True, example="899.90", xml="vUnCom"),
        "identities": {"type": "array", "description": "`ncm`: 8-digit NCM code, no dots. GOBL checks the format. " + gobl("ORG-IDENTITY-02") + " " + sefaz("I05-10", "777") + "\n\n`gtin`: the barcode, when the product has one. " + sefaz("I03-10", "611"),
                       "items": {"type": "object", "properties": {"key": {"type": "string", "enum": ["ncm", "gtin"]}, "code": {"type": "string", "example": "64041100"}}}},
    }, {"x-required": True}),
    "taxes": {"type": "array", "items": tax_combo, "x-required": True, "description": "ICMS, PIS and COFINS."},
    "ext": ext("Line extensions.", {
        "br-nfe-cfop": field("string", "CFOP. NFC-e accepts `5101`-`5104`, `5115`, `5405`, `5656`, `5667`, `5933`. CST `60` and CSOSN `500` go with `5405`.", gobl("INVOICE-35"), sefaz("I08-150", "725"), required=True, example="5102", xml="CFOP"),
    }, ) | {"x-required": True},
})
line["required"] = ["quantity", "item", "taxes", "ext"]
for k in ("item", "taxes", "ext"):
    line["properties"][k].pop("x-required", None)

payment = obj("How the consumer pays. Instructions when nothing is recorded as paid, advances for what is paid. " + gobl("INVOICE-31", "INVOICE-32"), {
    "instructions": obj("One payment means.", {
        "key": field("string", "`cash` gives `01`, `card` gives `03`, `card+debit` gives `04`. Use `other` with the extension for any other means.", required=True, example="card"),
        "ext": ext("Payment extensions.", {
            "br-nfe-payment-means": field("string", "Payment means code. NFC-e refuses `90` and `99`.", sefaz("YA02-40", "899"), sefaz("YA02-50", "436"), xml="tPag"),
        }),
    }),
    "advances": {"type": "array", "description": "One entry per tender. Their sum can't exceed the total. " + gobl("INVOICE-33", "PAY-RECORD-01"),
                 "items": {"type": "object", "properties": {"description": {"type": "string"}, "amount": {"type": "string", "example": "400.00"}, "key": {"type": "string", "example": "cash"}}}},
})

invoice = obj("A GOBL invoice for an NFC-e, model 65. Fields not listed follow the [GOBL invoice schema](https://docs.gobl.org/draft-0/bill/invoice).", {
    "$schema": field("string", "GOBL schema.", required=True, enum=["https://gobl.org/draft-0/bill/invoice"]),
    "$addons": {"type": "array", "items": {"type": "string", "enum": ["br-nfe-v4"]}, "description": "Must include `br-nfe-v4`.", "x-required": True},
    "$tags": {"type": "array", "items": {"type": "string", "enum": ["simplified"]}, "description": "`simplified` sets model `65`, NFC-e. Without it, the document is an NF-e.", "x-required": True},
    "series": field("string", "Series. GOBL accepts `0` to `999`, SEFAZ up to `889`.", gobl("INVOICE-23", "INVOICE-24"), sefaz("B26-10", "244"), required=True, example="1", xml="serie"),
    "code": field("string", "Receipt number. The workflow's sequence step fills it when left out.", xml="nNF"),
    "issue_date": field("string", "Sale date. GOBL fills the upload date. SEFAZ wants the issue time within 5 minutes of receipt.", sefaz("B09-10", "703"), xml="dhEmi"),
    "tax": obj("Document-level extensions.", {
        "ext": ext("", {
            "br-nfe-presence": field("string", "`1` in person, `4` home delivery.", gobl("INVOICE-26", "INVOICE-28"), required=True, enum=["1", "4"], xml="indPres"),
        }) | {"x-required": True},
    }, {"x-required": True}),
    "supplier": supplier | {"x-required": True},
    "customer": customer,
    "lines": {"type": "array", "items": line, "minItems": 1, "x-required": True, "description": "At least one line."},
    "payment": payment,
    "notes": {"type": "array", "description": "A note with key `reason`: the nature of the operation, 1 to 60 characters. " + gobl("INVOICE-29", "INVOICE-30"),
              "items": {"type": "object", "properties": {"key": {"type": "string", "enum": ["reason"]}, "text": {"type": "string", "example": "Venda de mercadoria"}}}, "x-required": True},
})
# required lists for nested objects built with pops above
for o in [invoice, invoice["properties"]["tax"]]:
    o["required"] = [k for k, v in o["properties"].items() if v.pop("x-required", False)] or o.get("required", [])


def strip_x(n):
    if isinstance(n, dict):
        n.pop("x-required", None)
        for v in n.values():
            strip_x(v)
    elif isinstance(n, list):
        for v in n:
            strip_x(v)


strip_x(invoice)


def snippet(name):
    text = (SNIPPETS / f"{name}.mdx").read_text()
    return json.loads(text.split("\n", 1)[1].rsplit("```", 1)[0])


EXAMPLES = [
    ("in-person-sale", "In-person sale", "dfe-consumer-invoice.min"),
    ("identified-consumer", "Identified consumer, split tender", "dfe-consumer-invoice-identified.min"),
    ("home-delivery", "Home delivery", "dfe-consumer-invoice-delivery.min"),
    ("tax-substitution", "Tax substitution line", "dfe-consumer-invoice-st.min"),
    ("simples-nacional", "Simples Nacional", "dfe-consumer-invoice-simples.min"),
    ("pix", "PIX payment", "dfe-consumer-invoice-pix.min"),
]

spec = {
    "openapi": "3.0.3",
    "info": {"title": "NFC-e requirements", "version": "spike",
             "description": "Generated by scripts/requirements/gen_br_nfce.py. Do not edit by hand."},
    "servers": [{"url": "https://api.invopop.com", "description": "production"}],
    "security": [{"authToken": []}],
    "paths": {"/silo/v1/gobl/build": {"post": {
        "summary": "NFC-e requirements",
        "description": "Every field an NFC-e needs, with who checks it: GOBL at upload, or SEFAZ at authorization. Pick a scenario example and send it to the build endpoint with a sandbox API key. It returns the built document, or the GOBL faults.",
        "requestBody": {"required": True, "content": {"application/json": {
            "schema": {"type": "object", "required": ["data"], "properties": {
                "data": invoice,
                "envelop": {"type": "boolean", "description": "When true, returns a full GOBL envelope.", "default": False}}},
            "examples": {k: {"summary": s, "value": {"data": snippet(f)}} for k, s, f in EXAMPLES},
        }}},
        "responses": {
            "200": {"description": "The built document, with defaults and totals.",
                    "content": {"application/json": {"schema": {"type": "object"}, "example": snippet("dfe-consumer-invoice")}}},
            "422": {"description": "GOBL faults. Each code links to the add-on rules.",
                    "content": {"application/json": {"schema": {"type": "object"}, "example": {"key": "validation", "faults": [{"code": "GOBL-BR-NFE-BILL-INVOICE-28", "paths": ["$.tax.ext"], "message": "NFC-e invoices require in-person or delivery for 'br-nfe-presence'"}]}}}},
        },
    }}},
    "components": {"securitySchemes": {"authToken": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT",
                                                     "description": "Use a sandbox workspace token."}}},
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=1000))
print(f"wrote {OUT.relative_to(ROOT)}")
