#!/usr/bin/env python3
"""Check the Mexico spec data files against the SAT schemas and the GOBL addon.

Two checks:

1. Completeness. For each section that has an "xsd" path, every attribute and
   child element of that node in the SAT schema must have a row, and every row
   must exist in the schema.
2. Rules. Every rule number in the GOBL addon (rules.Assert("NN", ...)) must be
   in the "rules" list of the spec, and the reverse.

Usage:

    python3 scripts/check-specs.py --xsd DIR --addon DIR

  --xsd    folder with cfdv40.xsd and Pagos20.xsd (from the SAT Anexo 20 page)
  --addon  the addon folder of a clone of invopop/gobl.mx.cfdi

The script exits with code 1 if it finds a difference.
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NS = {"xs": "http://www.w3.org/2001/XMLSchema"}
XSD_FILE = {"Comprobante": "cfdv40.xsd", "Pagos": "Pagos20.xsd"}
ADDON_FILE = {"invoice": "bill_invoice.go", "payment": "bill_payment.go"}


def schema_node(xsd_dir, path):
    parts = path.split("/")
    root = ET.parse(xsd_dir / XSD_FILE[parts[0]]).getroot()
    node = next(e for e in root.findall("xs:element", NS) if e.get("name") == parts[0])
    for name in parts[1:]:
        node = next(e for e in node.iter("{%s}element" % NS["xs"]) if e.get("name") == name)
    ctype = node.find("xs:complexType", NS)
    names = {}
    for attr in ctype.findall("xs:attribute", NS):
        names["@" + attr.get("name")] = "M" if attr.get("use") == "required" else "O"
    seq = ctype.find("xs:sequence", NS)
    if seq is not None:
        for el in seq.findall("xs:element", NS):
            names[el.get("name")] = "M" if el.get("minOccurs", "1") != "0" else "O"
    return names


def check_xsd(spec, xsd_dir):
    problems = []
    for sec in spec["sections"]:
        if "xsd" not in sec:
            continue
        schema = schema_node(xsd_dir, sec["xsd"])
        seen = set()
        for row in sec["rows"]:
            for field in row["cfdi"].split(", "):
                name = field.split("/")[0]
                seen.add(name)
                if name not in schema:
                    problems.append(f"{row['id']}: {name} is not in {sec['xsd']}")
                elif schema[name] == "M" and row["req"] != "M":
                    problems.append(f"{row['id']}: {name} is required in the schema, the row says {row['req']}")
                elif schema[name] == "O" and row["req"] == "M":
                    problems.append(f"{row['id']}: {name} is optional in the schema, the row says M")
        for name in schema:
            if name not in seen:
                problems.append(f"{spec['key']}/{sec['key']}: no row for {name} ({sec['xsd']})")
    return problems


def check_rules(spec, addon_dir):
    name = ADDON_FILE.get(spec["key"])
    if not name:
        return []
    source = (addon_dir / name).read_text()
    in_code = set(re.findall(r'rules\.Assert\("(\d+)"', source))
    in_spec = {r["n"] for r in spec.get("rules", [])}
    problems = []
    for n in sorted(in_code - in_spec):
        problems.append(f"{spec['key']}: rule {n} is in {name}, not in the spec")
    for n in sorted(in_spec - in_code):
        problems.append(f"{spec['key']}: rule {n} is in the spec, not in {name}")
    ids = {r["id"] for s in all_specs() for sec in s["sections"] for r in sec["rows"]}
    for rule in spec.get("rules", []):
        for row in rule["rows"]:
            if row not in ids:
                problems.append(f"{spec['key']}: rule {rule['n']} points to unknown row {row}")
    return problems


def all_specs():
    return [json.loads(p.read_text()) for p in sorted((ROOT / "scripts" / "specs" / "mx").glob("*.json"))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xsd", type=Path)
    ap.add_argument("--addon", type=Path)
    args = ap.parse_args()
    problems = []
    ids = [r["id"] for s in all_specs() for sec in s["sections"] for r in sec["rows"]]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        problems.append(f"duplicate row ID {dup}")
    for spec in all_specs():
        if args.xsd:
            problems += check_xsd(spec, args.xsd)
        if args.addon:
            problems += check_rules(spec, args.addon)
    for p in problems:
        print("DIFF", p)
    print(f"{len(ids)} rows checked, {len(problems)} differences")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
