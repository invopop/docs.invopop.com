// Turns a Chorus Pro test SIRET (or SIREN) into a GOBL party fragment.
//
// The VAT code is a two-digit key followed by the nine-digit SIREN, where
// key = (SIREN * 100 + 12) mod 97. The same derivation is published as a code
// block next to this component so agents reading the Markdown export get the
// algorithm even though they can't run the widget.
export const FrTaxId = ({ value = "34724449635741" }) => {
  const [raw, setRaw] = useState(value);
  const [copied, setCopied] = useState(false);

  const digits = (raw || "").replace(/\D/g, "");
  const siren = digits.length >= 9 ? digits.slice(0, 9) : "";
  const siret = digits.length === 14 ? digits : "";
  const complete = digits.length === 9 || digits.length === 14;
  const key = siren ? String((Number(siren) * 100 + 12) % 97).padStart(2, "0") : "";

  const party = [
    "{",
    '  "name": "Example Company",',
    '  "tax_id": {',
    '    "country": "FR",',
    '    "code": "' + key + siren + '"',
    "  }" + (siret ? "," : ""),
    ...(siret
      ? ['  "identities": [', "    {", '      "type": "SIRET",', '      "code": "' + siret + '"', "    }", "  ]"]
      : []),
    "}",
  ].join("\n");

  const copy = () => {
    if (navigator.clipboard) navigator.clipboard.writeText(party);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="not-prose my-5 rounded-2xl border border-gray-950/5 bg-gray-50 p-4 dark:border-white/10 dark:bg-white/[0.03]">
      <label className="block text-xs font-medium tracking-wide text-gray-500 uppercase dark:text-gray-400">
        SIRET (14 digits) or SIREN (9 digits)
      </label>
      <input
        type="text"
        value={raw}
        inputMode="numeric"
        spellCheck="false"
        onChange={(e) => setRaw(e.target.value)}
        placeholder="34724449635741"
        className="mt-2 w-full rounded-xl border border-gray-950/10 bg-white px-3 py-2 font-mono text-sm text-gray-900 dark:border-white/10 dark:bg-gray-900 dark:text-gray-100"
      />

      {complete ? (
        <div className="mt-4">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium tracking-wide text-gray-500 uppercase dark:text-gray-400">
              GOBL party
            </span>
            <button
              type="button"
              onClick={copy}
              className="shrink-0 rounded-md border border-gray-950/10 bg-white px-2 py-1 text-xs font-medium text-gray-600 hover:text-gray-900 dark:border-white/10 dark:bg-white/5 dark:text-gray-400 dark:hover:text-gray-100"
            >
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
          <pre className="mt-2 overflow-x-auto rounded-xl border border-gray-950/5 bg-white p-3 font-mono text-xs leading-5 text-gray-800 dark:border-white/10 dark:bg-gray-900 dark:text-gray-200">
            {party}
          </pre>
        </div>
      ) : (
        <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">
          Enter 9 digits for a SIREN or 14 for a SIRET. {digits.length} entered.
        </p>
      )}
    </div>
  );
};
