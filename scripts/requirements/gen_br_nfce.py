#!/usr/bin/env python3
"""Spike: generate one NFC-e requirements spec (OpenAPI) per scenario.

Sources:
- GOBL: the br-nfe-v4 validation rules, read from docs.gobl.org, give the errors
  table. Real 422 examples come from the GOBL build API on purposely broken
  copies of each scenario.
- SEFAZ and the field notes below: what GOBL doesn't know, such as SEFAZ rules
  and XML tags. In the full version they move to a reviewed per-country YAML.
- The built example snippets in snippets/invoices/br/.

Output: openapi/requirements/br-nfce-<scenario>.yaml

Run from the repo root: python3 scripts/requirements/gen_br_nfce.py
It calls https://docs.gobl.org and https://gobl.dev, so it needs the network.
"""
import copy
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SNIPPETS = ROOT / "snippets/invoices/br"
OUT = ROOT / "openapi/requirements"
RULES_MD = "https://docs.gobl.org/addons/br-nfe-v4.md"
RULES = "https://docs.gobl.org/addons/br-nfe-v4#validation-rules"
MOC = "https://www.nfe.fazenda.gov.br/portal/exibirArquivo.aspx?conteudo=J%20I%20v4eN00E="
BUILD = "https://gobl.dev/v0/build"


# ---------- sources

def snippet(name):
    text = (SNIPPETS / f"{name}.mdx").read_text()
    return json.loads(text.split("\n", 1)[1].rsplit("```", 1)[0])


def gobl_build(doc):
    req = urllib.request.Request(BUILD, data=json.dumps({"data": doc}).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)


SECTION_PATH = {
    "bill.Invoice": "", "bill.Line": "lines[].", "tax.Combo": "lines[].taxes[].",
    "org.Identity": "identities[].", "org.Party": "supplier or customer ", "pay.Instructions": "payment.instructions.",
    "pay.Record": "payment.advances[].",
}
NFE_ONLY = ("Invoice is NFe", "NFe model", "Credit note purpose", "Debit note purpose")


def gobl_rules():
    """Rows of the add-on's validation rules that apply to an NFC-e."""
    md = urllib.request.urlopen(RULES_MD).read().decode()
    rows, section = [], None
    for line in md.splitlines():
        m = re.match(r"> \[accordion\] (\S+)", line)
        if m:
            section = m.group(1)
            continue
        m = re.match(r"> \| (.+?) \| (<ul>.*</ul>) \| `(GOBL-BR-NFE-[A-Z-]+-\d+)` (.+) \|$", line)
        if not m:
            continue
        field, tests, code, msg = m.groups()
        tests = [re.sub(r"\\(.)", r"\1", t) for t in re.findall(r"<li>(.*?)</li>", tests)]
        if any(t in NFE_ONLY for t in tests):
            continue
        field = field.strip("`")
        path = SECTION_PATH.get(section, "") + ("" if field in ("Invoice", "Line") else field)
        rows.append({"code": code, "path": path.strip() or "invoice", "when": "; ".join(tests).replace("|", "\\|"),
                     "message": re.sub(r"\\(.)", r"\1", msg).replace("|", "\\|")})
    return rows


# ---------- what GOBL doesn't know

SEFAZ = [  # rule, rejection, check, scenarios ("all" or a tag)
    ("B09-10, B09-40", "703, 704", "Issue date and time within 5 minutes of SEFAZ receipt", "all"),
    ("B26-10", "244", "Series `0` to `889`", "all"),
    ("I05-10, I05-20", "777, 778", "NCM present and in the official table", "all"),
    ("I03-10, I03-30", "611, 883", "GTIN with a valid check digit, or `SEM GTIN`", "all"),
    ("I08-150", "725", "CFOP only `5101`-`5104`, `5115`, `5405`, `5656`, `5667` or `5933`", "all"),
    ("N12-40, N12a-40", "382, 386", "CST or CSOSN paired with the CFOP", "all"),
    ("O01-10", "742", "No IPI on an NFC-e", "all"),
    ("W16-40", "750", "Above R$10,000, the consumer is identified", "all"),
    ("YA02-40, YA02-50", "899, 436", "Payment means `90` and `99` refused", "all"),
    ("N12-30", "766", "CST only `00`, `20`, `40`, `41` or `60`. `90` is a state option", "normal"),
    ("N12a-20", "383", "CSOSN only `102`, `103`, `300`, `400` or `500`. `900` is a state option", "simples"),
    ("YA04-10", "391", "A card payment needs the card group", "card"),
    ("YA09-10", "869", "A payment above the total needs the change amount", "cash"),
    ("E01-20, E05-20", "787, 788", "Home delivery: the consumer's ID and address are present", "delivery"),
    ("B25b-30", "785", "Home delivery: the state allows NFC-e with home delivery", "delivery"),
    ("B25c-10", "434", "Home delivery: presence `4` needs the intermediary flag", "delivery"),
]


def gobl_ref(*codes):
    return ", ".join(f"[`{c}`]({RULES})" for c in codes)


def by(who, *refs):
    """Who checks the field, appended to its description."""
    return f"Checked by {who}: " + ", ".join(refs) + "."


def sefaz_ref(rule, rejection):
    return f"[MOC]({MOC}) rule `{rule}`, rejection `{rejection}`"


# ---------- schema building blocks

def f(type_, text, *notes, default=None, enum=None, example=None, xml=None):
    parts = [text] + ([f"NF-e XML: `{xml}`."] if xml else []) + list(notes)
    out = {"type": type_, "description": "\n\n".join(parts)}
    for k, v in (("default", default), ("enum", enum), ("example", example)):
        if v is not None:
            out[k] = v
    return out


def o(desc, props, required=()):
    out = {"type": "object", "description": desc, "properties": props}
    if required:
        out["required"] = list(required)
    return out


def arr(desc, items, min_items=None):
    out = {"type": "array", "description": desc, "items": items}
    if min_items:
        out["minItems"] = min_items
    return out


def address(who):
    return o(f"The {who} address.", {
        "street": f("string", "Street name.", xml="xLgr"),
        "num": f("string", "Street number.", xml="nro"),
        "locality": f("string", "Neighbourhood (_bairro_).", xml="xBairro"),
        "state": f("string", "Two-letter state code.", example="SP", xml="UF"),
        "code": f("string", "Postal code (CEP).", example="01426-001", xml="CEP"),
        "country": f("string", "ISO country code. GOBL fills it from the tax ID.", default="BR"),
    }, required=("street", "num", "locality", "state", "code"))


def base_schema():
    tax_ext = o("Tax codes. GOBL fills the normal-regime defaults when you leave them out.", {
        "br-nfe-icms-cst": f("string", "ICMS CST, normal regime.", by("GOBL", gobl_ref("GOBL-BR-NFE-TAX-COMBO-01")), by("SEFAZ", sefaz_ref("N12-30", "766")), default="00", enum=["00", "20", "40", "41", "60"], xml="CST"),
        "br-nfe-icms-origin": f("string", "Goods origin. `0` national, `1` direct import, `2` foreign bought in Brazil.", by("GOBL", gobl_ref("GOBL-BR-NFE-TAX-COMBO-02")), default="0", xml="orig"),
        "br-nfe-pis-cst": f("string", "PIS CST.", default="01"),
        "br-nfe-cofins-cst": f("string", "COFINS CST.", default="01"),
    })
    tax = o("One entry per category: ICMS, PIS and COFINS. " + by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-LINE-01", "GOBL-BR-NFE-BILL-LINE-02", "GOBL-BR-NFE-BILL-LINE-03")), {
        "cat": f("string", "Tax category.", enum=["ICMS", "PIS", "COFINS"]),
        "percent": f("string", "Rate set by the tax advisor. `0%` for ICMS CST `40`, `41` and `60`.", by("GOBL", gobl_ref("GOBL-BR-NFE-TAX-COMBO-07")), example="18%"),
        "ext": tax_ext,
    }, required=("cat", "percent"))
    line = o("One line per product.", {
        "quantity": f("string", "Quantity.", example="1", xml="qCom"),
        "item": o("The product.", {
            "name": f("string", "Product name.", xml="xProd"),
            "price": f("string", "Unit price paid by the consumer, taxes included.", example="899.90", xml="vUnCom"),
            "identities": arr("Product codes. `ncm`: the 8-digit NCM code, no dots. " + by("GOBL", gobl_ref("GOBL-BR-NFE-ORG-IDENTITY-02")) + " " + by("SEFAZ", sefaz_ref("I05-10", "777")) + " `gtin`: the barcode, when the product has one.",
                              o("A product code.", {"key": f("string", "Code type.", enum=["ncm", "gtin"]), "code": f("string", "The code.", example="64041100", xml="NCM, cEAN")}, required=("key", "code")), min_items=1),
        }, required=("name", "price", "identities")),
        "taxes": arr("ICMS, PIS and COFINS.", tax, min_items=3),
        "ext": o("Line extensions.", {
            "br-nfe-cfop": f("string", "CFOP of the operation. `5102` resells goods bought from third parties.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-35")), by("SEFAZ", sefaz_ref("I08-150", "725")), enum=["5101", "5102", "5103", "5104", "5115", "5405", "5656", "5667", "5933"], example="5102", xml="CFOP"),
        }, required=("br-nfe-cfop",)),
    }, required=("quantity", "item", "taxes", "ext"))
    supplier = o("The establishment issuing the receipt. One registered supplier per establishment.", {
        "name": f("string", "Legal name.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-10")), xml="xNome"),
        "tax_id": o("Tax ID.", {
            "country": f("string", "Always `BR`.", enum=["BR"]),
            "code": f("string", "CNPJ, 14 digits.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-01", "GOBL-BR-NFE-BILL-INVOICE-02")), example="48219376000118", xml="CNPJ"),
        }, required=("country", "code")),
        "identities": arr("The state registration (IE), key `br-nfe-state-reg`. GOBL accepts the document without it. SEFAZ needs it.\n\nNF-e XML: `IE`.",
                          o("An identity.", {"key": f("string", "Identity type.", enum=["br-nfe-state-reg"]), "code": f("string", "IE number.", example="110042490114")}, required=("key", "code")), min_items=1),
        "addresses": arr("At least one address. " + by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-03", "GOBL-BR-NFE-BILL-INVOICE-04", "GOBL-BR-NFE-BILL-INVOICE-08", "GOBL-BR-NFE-BILL-INVOICE-11")), address("establishment's"), min_items=1),
        "ext": o("Supplier extensions.", {
            "br-ibge-municipality": f("string", "7-digit IBGE municipality code.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-09")), example="3550308", xml="cMun"),
            "br-nfe-regime": f("string", "Tax regime. `3` normal. It decides CST or CSOSN on every line.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-39", "GOBL-BR-NFE-BILL-INVOICE-42")), default="3", enum=["2", "3"], xml="CRT"),
        }, required=("br-ibge-municipality",)),
    }, required=("name", "tax_id", "identities", "addresses", "ext"))
    payment = o("How the consumer pays: `instructions` when nothing is recorded as paid. " + by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-31", "GOBL-BR-NFE-BILL-INVOICE-32")), {
        "instructions": o("One payment means.", {
            "key": f("string", "`cash` gives `01`, `card` gives `03`, `card+debit` gives `04`. Use `other` with the extension for any other means.", example="card"),
            "ext": o("Payment extensions.", {
                "br-nfe-payment-means": f("string", "Payment means code. GOBL fills it from the key, except `other`.", by("SEFAZ", sefaz_ref("YA02-40", "899"), sefaz_ref("YA02-50", "436")), xml="tPag"),
            }),
        }, required=("key",)),
    }, required=("instructions",))
    return o("A GOBL invoice for an NFC-e, model 65. Fields not listed follow the [GOBL invoice schema](https://docs.gobl.org/draft-0/bill/invoice).", {
        "$schema": f("string", "GOBL schema.", enum=["https://gobl.org/draft-0/bill/invoice"]),
        "$addons": arr("Must include `br-nfe-v4`.", {"type": "string", "enum": ["br-nfe-v4"]}, min_items=1),
        "$tags": arr("`simplified` sets model `65`, NFC-e. Without it, the document is an NF-e.", {"type": "string", "enum": ["simplified"]}, min_items=1),
        "series": f("string", "Series. GOBL accepts `0` to `999`.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-23", "GOBL-BR-NFE-BILL-INVOICE-24")), by("SEFAZ", sefaz_ref("B26-10", "244")), example="1", xml="serie"),
        "code": f("string", "Receipt number. The workflow's sequence step fills it when left out.", xml="nNF"),
        "issue_date": f("string", "Sale date. GOBL fills the upload date.", by("SEFAZ", sefaz_ref("B09-10", "703")), xml="dhEmi"),
        "tax": o("Document-level extensions.", {
            "ext": o("Tax extensions.", {
                "br-nfe-presence": f("string", "`1`, in person.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-26", "GOBL-BR-NFE-BILL-INVOICE-28")), enum=["1"], xml="indPres"),
            }, required=("br-nfe-presence",)),
        }, required=("ext",)),
        "supplier": supplier,
        "lines": arr("At least one line.", line, min_items=1),
        "payment": payment,
        "notes": arr("A note with key `reason`: the nature of the operation, 1 to 60 characters. " + by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-29", "GOBL-BR-NFE-BILL-INVOICE-30")),
                     o("A note.", {"key": f("string", "Note key.", enum=["reason"]), "text": f("string", "Nature of the operation.", example="Venda de mercadoria", xml="natOp")}, required=("key", "text")), min_items=1),
    }, required=("$schema", "$addons", "$tags", "series", "tax", "supplier", "lines", "payment", "notes"))


def customer_schema(with_address):
    props = {
        "name": f("string", "The consumer's name.", xml="xNome"),
        "tax_id": o("The consumer's CPF. " + by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-36")), {
            "country": f("string", "Always `BR`.", enum=["BR"]),
            "code": f("string", "CPF, 11 digits.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-15")), example="39851726419", xml="CPF"),
        }, required=("country", "code")),
        "ext": o("Customer extensions.", {
            "br-nfe-state-reg-ind": f("string", "Always `9`, non-taxpayer, on an NFC-e.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-53")), default="9", enum=["9"], xml="indIEDest"),
        }),
    }
    required = ["tax_id"]
    if with_address:
        props["addresses"] = arr("The delivery address. " + by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-16", "GOBL-BR-NFE-BILL-INVOICE-21")) + " " + by("SEFAZ", sefaz_ref("E05-20", "788")), address("delivery"), min_items=1)
        props["ext"]["properties"]["br-ibge-municipality"] = f("string", "IBGE code of the delivery city.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-22")), example="3550308")
        props["ext"]["required"] = ["br-ibge-municipality"]
        required += ["addresses", "ext"]
        who = by("SEFAZ", sefaz_ref("E01-20", "787"))
    else:
        who = by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-36"))
    return o("The consumer. " + who, props, required=required)


# ---------- scenarios

DELETE = object()


def set_path(doc, path, value):
    *head, last = path
    for k in head:
        doc = doc[k]
    if value is DELETE:
        doc.pop(last, None)
    else:
        doc[last] = value


COMMON_BREAKS = [
    ("internet-sale", "Presence 2, an internet sale", [(("tax", "ext", "br-nfe-presence"), "2")]),
    ("missing-cfop", "A line without CFOP", [(("lines", 0, "ext"), DELETE)]),
    ("ncm-with-dots", "NCM written with dots", [(("lines", 0, "item", "identities", 0, "code"), "6404.11.00")]),
    ("missing-supplier-state", "Supplier address without state", [(("supplier", "addresses", 0, "state"), DELETE)]),
    ("missing-ibge", "Supplier without IBGE code", [(("supplier", "ext", "br-ibge-municipality"), DELETE)]),
]


def simples_schema(inv):
    sup = inv["properties"]["supplier"]["properties"]["ext"]
    sup["properties"]["br-nfe-regime"] = f("string", "Tax regime: `1` Simples Nacional, `4` MEI. Every ICMS line then needs a CSOSN.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-39", "GOBL-BR-NFE-BILL-INVOICE-43")), enum=["1", "4"], xml="CRT")
    sup["required"] = ["br-ibge-municipality", "br-nfe-regime"]
    tax = inv["properties"]["lines"]["items"]["properties"]["taxes"]["items"]
    tax["properties"]["percent"]["description"] = "`0%` for every CSOSN an NFC-e accepts. " + by("GOBL", gobl_ref("GOBL-BR-NFE-TAX-COMBO-06"))
    ext = tax["properties"]["ext"]
    ext["properties"].pop("br-nfe-icms-cst")
    ext["properties"]["br-nfe-icms-csosn"] = f("string", "ICMS CSOSN, on the ICMS entry.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-43")), by("SEFAZ", sefaz_ref("N12a-20", "383")), enum=["102", "103", "300", "400", "500"], xml="CSOSN")
    ext["properties"]["br-nfe-pis-cst"]["description"] = "PIS CST. Set it on the PIS entry, for example `49`. GOBL's default `01` is the normal-regime code."
    ext["properties"]["br-nfe-cofins-cst"]["description"] = "COFINS CST. Set it on the COFINS entry, for example `49`. GOBL's default `01` is the normal-regime code."
    ext["required"] = ["br-nfe-icms-csosn"]
    tax["required"] = ["cat", "percent", "ext"]


def st_schema(inv):
    line = inv["properties"]["lines"]["items"]
    line["description"] = "One line per product. A line taxed by substitution (ICMS-ST) uses CFOP `5405`, CST `60` and ICMS `0%`."
    tax = line["properties"]["taxes"]["items"]
    tax["properties"]["percent"]["description"] = "`0%` on the ICMS entry with CST `60`. " + by("GOBL", gobl_ref("GOBL-BR-NFE-TAX-COMBO-07"))


def advances_schema(inv, desc):
    inv["properties"]["payment"] = o("What the consumer paid. " + by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-33", "GOBL-BR-NFE-PAY-RECORD-01")), {
        "advances": arr(desc, o("One tender.", {
            "description": f("string", "Free text."),
            "amount": f("string", "Amount kept for this tender. The sum can't exceed the total.", example="400.00"),
            "key": f("string", "`cash`, `card`, `card+debit`, or `other` with the extension.", example="cash"),
            "ext": o("Payment extensions.", {"br-nfe-payment-means": f("string", "Payment means code. GOBL fills it from `cash`, `card` and `card+debit`. With key `other` and no code, GOBL fills `99`, which SEFAZ refuses on an NFC-e.", by("GOBL", gobl_ref("GOBL-BR-NFE-PAY-RECORD-02")), by("SEFAZ", sefaz_ref("YA02-50", "436")), xml="tPag")}),
        }, required=("amount", "key")), min_items=1),
    }, required=("advances",))


def identified_schema(inv):
    inv["properties"]["customer"] = customer_schema(False)
    inv["required"].append("customer")
    advances_schema(inv, "One entry per tender, here cash and a debit card.")


def delivery_schema(inv):
    inv["properties"]["customer"] = customer_schema(True)
    inv["required"].append("customer")
    inv["properties"]["tax"]["properties"]["ext"]["properties"]["br-nfe-presence"] = f(
        "string", "`4`, NFC-e with home delivery in the establishment's state.", by("GOBL", gobl_ref("GOBL-BR-NFE-BILL-INVOICE-28")), enum=["4"], xml="indPres")


SCENARIOS = [
    {"slug": "in-person-sale", "title": "In-person sale", "snippet": "dfe-consumer-invoice", "guide": "in-person-sale",
     "summary": "The consumer pays in person and takes the goods. No consumer data.",
     "tags": {"normal", "card"}, "schema": None,
     "breaks": [("csosn-normal-regime", "CSOSN with the normal regime", [(("lines", 0, "taxes", 0), {"cat": "ICMS", "percent": "0%", "ext": {"br-nfe-icms-csosn": "102"}})])]},
    {"slug": "identified-consumer", "title": "Identified consumer", "snippet": "dfe-consumer-invoice-identified", "guide": "identified-consumer",
     "summary": "The consumer gives their CPF. The example also splits the payment between cash and a debit card.",
     "tags": {"normal", "card", "cash"}, "schema": identified_schema,
     "breaks": [("overpayment", "Cash above the total", [(("payment", "advances"), [{"amount": "1000.00", "key": "cash"}])]),
                ("taxpayer-indicator", "Customer marked as taxpayer", [(("customer", "ext"), {"br-nfe-state-reg-ind": "1"})])]},
    {"slug": "home-delivery", "title": "Home delivery", "snippet": "dfe-consumer-invoice-delivery", "guide": "home-delivery",
     "summary": "Sold in the store, delivered to the consumer's home in the same state.",
     "tags": {"normal", "card", "delivery"}, "schema": delivery_schema,
     "breaks": [("address-without-ibge", "Delivery address without IBGE code", [(("customer", "ext"), {})]),
                ("address-without-street", "Delivery address without street", [(("customer", "addresses", 0, "street"), DELETE)])]},
    {"slug": "simples-nacional", "title": "Simples Nacional", "snippet": "dfe-consumer-invoice-simples", "guide": "tax-regime-normal-or-simples-nacional",
     "summary": "The same sale from a Simples Nacional establishment: CSOSN instead of CST.",
     "tags": {"simples", "card"}, "schema": simples_schema,
     "breaks": [("cst-with-simples", "CST with Simples Nacional", [(("lines", 0, "taxes", 0, "ext"), {"br-nfe-icms-cst": "00"})]),
                ("csosn-with-rate", "CSOSN 102 with an ICMS rate", [(("lines", 0, "taxes", 0, "percent"), "18%")])]},
    {"slug": "tax-substitution", "title": "Tax substitution", "snippet": "dfe-consumer-invoice-st", "guide": "what-you-sell-cfop-and-icms-code",
     "summary": "A line already taxed by substitution (ICMS-ST), next to a resale line.",
     "tags": {"normal", "card"}, "schema": st_schema,
     "breaks": [("cst60-with-rate", "CST 60 with an ICMS rate", [(("lines", 1, "taxes", 0, "percent"), "18%")])]},
    {"slug": "pix", "title": "PIX payment", "snippet": "dfe-consumer-invoice-pix", "guide": "payment-means-cash-cards-pix-vouchers",
     "summary": "The consumer pays by PIX, recorded as paid.",
     "tags": {"normal"}, "schema": lambda inv: advances_schema(inv, "One entry: PIX, key `other` with `br-nfe-payment-means` `17`."),
     "breaks": [("invalid-payment-means", "Payment means 20, not in the code list", [(("payment", "advances", 0, "ext"), {"br-nfe-payment-means": "20"})])]},
]


def faults_table(rows):
    out = ["| Code | Field | Message |", "|---|---|---|"]
    for r in rows:
        short = r["code"].replace("GOBL-BR-NFE-", "")
        out.append(f"| [`{short}`]({RULES}) | `{r['path']}` | {r['message']} |")
    return "\n".join(out)


def sefaz_table(tags):
    out = ["| MOC rule | Rejection | Check |", "|---|---|---|"]
    for rule, rej, check, who in SEFAZ:
        if who == "all" or who in tags:
            out.append(f"| `{rule}` | `{rej}` | {check} |")
    return "\n".join(out)


def build_spec(sc, rules):
    inv = base_schema()
    if sc["schema"]:
        sc["schema"](inv)
    good = snippet(sc["snippet"] + ".min")
    status, built = gobl_build(good)
    assert status == 200, (sc["slug"], built)
    examples = {}
    for key, summary, changes in COMMON_BREAKS + sc["breaks"]:
        doc = copy.deepcopy(good)
        for path, value in changes:
            set_path(doc, path, value)
        status, body = gobl_build(doc)
        assert status == 422, (sc["slug"], key, status, body)
        examples[key] = {"summary": summary, "value": body}
    errors_desc = "\n\n".join([
        "GOBL faults returned by this call. Each example in the menu is a real response to a broken copy of this scenario.",
        "**All GOBL `br-nfe-v4` faults that apply to an NFC-e.** Full codes start with `GOBL-BR-NFE-`.",
        faults_table(rules),
        "**SEFAZ rejections, returned later by the issue job.** GOBL doesn't check these. Source: [MOC 7.0 Annex I](" + MOC + ").",
        sefaz_table(sc["tags"]),
    ])
    return {
        "openapi": "3.0.3",
        "info": {"title": f"NFC-e requirements: {sc['title']}", "version": "spike",
                 "description": "Generated by scripts/requirements/gen_br_nfce.py. Do not edit by hand."},
        "servers": [{"url": "https://api.invopop.com", "description": "production"}],
        "security": [{"authToken": []}],
        "paths": {"/silo/v1/gobl/build": {"post": {
            "summary": sc["title"],
            "description": sc["summary"] + " Required means required for this scenario: by GOBL at upload, or by SEFAZ at authorization. Each field says who checks it.",
            "requestBody": {"required": True, "content": {"application/json": {
                "schema": o("Build request.", {"data": inv, "envelop": f("boolean", "When true, returns a full GOBL envelope.", default=False)}, required=("data",)),
                "examples": {sc["slug"]: {"summary": sc["title"], "value": {"data": good}}},
            }}},
            "responses": {
                "422": {"description": errors_desc,
                        "content": {"application/json": {"schema": o("GOBL faults.", {
                            "key": f("string", "Always `validation`."),
                            "faults": arr("One entry per failed rule.", o("A fault.", {
                                "code": f("string", "The GOBL rule code."),
                                "paths": arr("JSON paths of the fields.", {"type": "string"}),
                                "message": f("string", "Human-readable message.")})),
                        }), "examples": examples}}},
            },
        }}},
        "components": {"securitySchemes": {"authToken": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT", "description": "Use a sandbox workspace token."}}},
    }


def main():
    rules = gobl_rules()
    OUT.mkdir(parents=True, exist_ok=True)
    for sc in SCENARIOS:
        spec = build_spec(sc, rules)
        path = OUT / f"br-nfce-{sc['slug']}.yaml"
        path.write_text(yaml.safe_dump(spec, sort_keys=False, allow_unicode=True, width=1000))
        n = len(spec["paths"]["/silo/v1/gobl/build"]["post"]["responses"]["422"]["content"]["application/json"]["examples"])
        print(f"wrote {path.relative_to(ROOT)}: {len(rules)} GOBL faults, {n} real 422 examples")


if __name__ == "__main__":
    main()
