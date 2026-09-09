// Derives a French VAT tax ID (the GOBL `tax_id.code`) from a SIRET or SIREN.
//
// The VAT code is a two-digit key followed by the nine-digit SIREN, where
// key = (SIREN * 100 + 12) mod 97. The same rule is published as a code block
// next to this component so agents reading the Markdown export get the
// algorithm even though they can't run the widget.
export const FrTaxId = ({ value = "34724449635741" }) => {
  const [raw, setRaw] = useState(value);
  const [copied, setCopied] = useState("");

  const digits = (raw || "").replace(/\D/g, "");
  const siren = digits.length >= 9 ? digits.slice(0, 9) : "";
  const siret = digits.length === 14 ? digits : "";
  const complete = digits.length === 9 || digits.length === 14;
  const key = siren ? String((Number(siren) * 100 + 12) % 97).padStart(2, "0") : "";
  const code = siren ? key + siren : "";

  // INSEE numbers carry a Luhn check digit. Fictitious numbers — the Chorus Pro
  // QAS test accounts among them — fail it, which is what stops GOBL from
  // normalizing a bare SIREN into a full VAT code.
  const luhn = (n) => {
    let total = 0;
    for (let i = 0; i < n.length; i++) {
      let d = Number(n[n.length - 1 - i]);
      if (i % 2 === 1) {
        d *= 2;
        if (d > 9) d -= 9;
      }
      total += d;
    }
    return total % 10 === 0;
  };
  const live = complete && luhn(siren);

  const json = siret
    ? '"tax_id": {\n  "country": "FR",\n  "code": "' +
      code +
      '"\n},\n"identities": [\n  {\n    "type": "SIRET",\n    "code": "' +
      siret +
      '"\n  }\n]'
    : '"tax_id": {\n  "country": "FR",\n  "code": "' + code + '"\n}';

  const copy = (text, label) => {
    if (navigator.clipboard) navigator.clipboard.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(""), 1500);
  };

  const CopyButton = ({ text, label }) => (
    <button
      type="button"
      onClick={() => copy(text, label)}
      className="shrink-0 rounded-md border border-gray-950/10 bg-white px-2 py-1 text-xs font-medium text-gray-600 hover:text-gray-900 dark:border-white/10 dark:bg-white/5 dark:text-gray-400 dark:hover:text-gray-100"
    >
      {copied === label ? "Copied" : "Copy"}
    </button>
  );

  const Row = ({ label, children }) => (
    <div className="flex items-baseline gap-3 py-1">
      <span className="w-20 shrink-0 text-xs tracking-wide text-gray-500 uppercase dark:text-gray-400">{label}</span>
      <span className="min-w-0 font-mono text-sm text-gray-900 dark:text-gray-100">{children}</span>
    </div>
  );

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
          <Row label="SIREN">{siren}</Row>
          {siret ? <Row label="SIRET">{siret}</Row> : null}
          <Row label="Key">{key}</Row>
          <div className="mt-2 flex items-center gap-3 rounded-xl border border-gray-950/5 bg-white px-3 py-2 dark:border-white/10 dark:bg-gray-900">
            <span className="w-20 shrink-0 text-xs tracking-wide text-gray-500 uppercase dark:text-gray-400">Tax ID</span>
            <span className="min-w-0 flex-1 truncate font-mono text-sm font-medium text-gray-900 dark:text-gray-100">
              FR {code}
            </span>
            <CopyButton text={code} label="code" />
          </div>

          <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">
            {live
              ? "This SIREN passes the INSEE check digit, so GOBL would also accept the bare nine-digit form and prepend the key itself. The key is computed, not looked up — confirm the VAT code against the company's own records before using it in production."
              : "This SIREN does not pass the INSEE check digit, which is expected for fictitious numbers such as the Chorus Pro QAS test accounts. Send the full 11-character code: GOBL only prepends the key to a bare SIREN when the check digit passes, so a nine-digit code is rejected with a checksum mismatch."}
          </p>

          <div className="mt-4 flex items-center justify-between">
            <span className="text-xs font-medium tracking-wide text-gray-500 uppercase dark:text-gray-400">
              GOBL party fragment
            </span>
            <CopyButton text={json} label="json" />
          </div>
          <pre className="mt-2 overflow-x-auto rounded-xl border border-gray-950/5 bg-white p-3 font-mono text-xs leading-5 text-gray-800 dark:border-white/10 dark:bg-gray-900 dark:text-gray-200">
            {json}
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
