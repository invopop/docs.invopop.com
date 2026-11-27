// Interactive view of a document spec. The data comes from the generated
// snippets in snippets/specs/<cc>/<doc>.mdx (see scripts/build-specs.py).
//
// The same data is also on each page as Markdown tables, in the "Tables" tab.
// Custom JSX does not survive into the `.md` export, so the tables are the
// version that agents read. Keep the two views on the page.
//
// Layout: the tables here are CSS grids with ARIA table roles, not <table>
// elements. Mintlify wraps every <table> in its own scroll container, which
// adds a blank band and breaks the column widths.
//
// Tailwind: only static className literals compile in Mintlify. Dynamic
// values (the grid template) go in the style prop.
export const SpecExplorer = ({ spec, errorsHref = "/guides/mx-cfdi-errors" }) => {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("all");
  const [open, setOpen] = useState({});

  // A link such as /guides/mx-cfdi-invoice#MX-INV-H08 opens that row.
  useEffect(() => {
    const id = window.location.hash.replace("#", "");
    const known = spec.sections.some((sec) => sec.rows.some((r) => r.id === id));
    if (!known) return;
    setOpen((prev) => ({ ...prev, [id]: true }));
    setTimeout(() => {
      const el = document.getElementById(id);
      if (el) el.scrollIntoView({ block: "center" });
    }, 100);
  }, []);

  const filters = [
    { key: "all", label: "All" },
    { key: "M", label: "Mandatory" },
    { key: "C", label: "Conditional" },
    { key: "O", label: "Optional" },
    { key: "auto", label: "Auto-filled" },
    { key: "No", label: "Not supported" },
  ];

  const levelColor = { M: "red", C: "orange", O: "blue", No: "gray" };
  const levelName = { M: "Mandatory", C: "Conditional", O: "Optional", No: "Not supported" };

  // One level for each field: the level of the government format.
  // "Set by Invopop" is a second mark, for a value that Invopop sets or defaults.
  const levelOf = (row) => (row.send === "No" ? "No" : row.req);
  const isAuto = (row) => (row.auto === undefined ? row.send === "Auto" : row.auto);
  // "Always": Invopop sets the value. "If empty": Invopop gives a default when you send nothing.
  const autoText = (row) => (!isAuto(row) ? "" : row.send === "Auto" ? "Always" : "If empty");

  const matchesFilter = (row) => {
    if (filter === "all") return true;
    if (filter === "auto") return isAuto(row);
    return levelOf(row) === filter;
  };

  const q = query.trim().toLowerCase();
  const matchesQuery = (row) => {
    if (!q) return true;
    return [row.id, row.cfdi, row.gobl, row.rule, row.when, row.default, row.format, row.values, row.example]
      .filter(Boolean)
      .join(" ")
      .toLowerCase()
      .includes(q);
  };

  const sections = spec.sections
    .map((sec) => ({ ...sec, shown: sec.rows.filter((r) => matchesFilter(r) && matchesQuery(r)) }))
    .filter((sec) => sec.shown.length > 0);

  const total = spec.sections.reduce((n, sec) => n + sec.rows.length, 0);
  const shown = sections.reduce((n, sec) => n + sec.shown.length, 0);
  // Let a long field name wrap after a dot, slash or bracket, not in the middle of a word.
  const soft = (text) =>
    (text || "").split(/(?<=[./\]])/).map((part, i) => (
      <span key={i}>
        {i > 0 && <wbr />}
        {part}
      </span>
    ));

  const toggle = (id) => setOpen((prev) => ({ ...prev, [id]: !prev[id] }));

  const columns = { gridTemplateColumns: "112px minmax(0, 1fr) minmax(0, 1.1fr) 124px 94px" };
  const detailColumns = { gridTemplateColumns: "96px minmax(0, 1fr)" };

  const details = (row) =>
    [
      ["Format", row.format],
      ["Values", row.values],
      ["Condition", row.when ? "When " + row.when + "." : null],
      ["Default", row.default],
      ["Notes", row.rule],
      [
        "GOBL spec",
        row.link ? (
          <a href={row.link.url} target="_blank" rel="noreferrer" className="underline">
            {row.link.label}
          </a>
        ) : null,
      ],
      ["Example", row.example ? <code className="font-mono text-xs">{row.example}</code> : null],
      [
        "Error",
        row.errors && row.errors.length > 0
          ? row.errors.map((n) => (
              <a key={n} href={errorsHref} className="mr-3 font-mono text-xs underline">
                {spec.errorPrefix + n}
              </a>
            ))
          : null,
      ],
    ].filter((d) => d[1]);

  const Chevron = ({ turned }) => (
    <svg
      viewBox="0 0 16 16"
      width="10"
      height="10"
      aria-hidden="true"
      className="shrink-0 text-gray-400"
      style={{ transform: turned ? "rotate(90deg)" : "none" }}
    >
      <path d="M6 3l5 5-5 5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );

  const Check = () => (
    <svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true" className="text-green-600 dark:text-green-400">
      <path d="M3 8.5l3.2 3.2L13 5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );

  return (
    <div className="not-prose">
      <div className="mb-5 flex flex-col gap-2">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search a CFDI field, a GOBL field or an ID"
          aria-label="Search the spec"
          className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 outline-none focus:border-gray-400 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100"
        />
        <div className="flex flex-wrap items-center gap-1.5">
          {filters.map((f) =>
            filter === f.key ? (
              <button
                key={f.key}
                type="button"
                onClick={() => setFilter(f.key)}
                aria-pressed="true"
                className="rounded-full border border-gray-900 bg-gray-900 px-3 py-1 text-xs font-medium text-white dark:border-gray-100 dark:bg-gray-100 dark:text-gray-900"
              >
                {f.label}
              </button>
            ) : (
              <button
                key={f.key}
                type="button"
                onClick={() => setFilter(f.key)}
                aria-pressed="false"
                className="rounded-full border border-gray-200 bg-white px-3 py-1 text-xs font-medium text-gray-700 hover:border-gray-400 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-300"
              >
                {f.label}
              </button>
            )
          )}
          <span className="ml-auto text-xs text-gray-500 dark:text-gray-400">
            {shown} of {total}
          </span>
        </div>
      </div>

      {sections.length === 0 && (
        <div className="rounded-lg border border-gray-200 p-4 text-sm text-gray-600 dark:border-gray-700 dark:text-gray-300">
          No field matches.
        </div>
      )}

      {sections.map((sec) => (
        <div key={sec.key} className="mb-7">
          <div className="mb-2 flex flex-wrap items-baseline gap-2">
            <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">{sec.title}</span>
            <code className="font-mono text-xs text-gray-500 dark:text-gray-400">{sec.node}</code>
          </div>
          <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
            <div role="table" aria-label={sec.title} style={{ minWidth: "660px" }}>
              <div
                role="row"
                style={columns}
                className="grid items-center border-b border-gray-200 bg-gray-50 text-xs font-medium text-gray-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-400"
              >
                <div role="columnheader" className="px-3 py-2">ID</div>
                <div role="columnheader" className="px-3 py-2">CFDI field</div>
                <div role="columnheader" className="px-3 py-2">GOBL field</div>
                <div role="columnheader" className="px-3 py-2">Level</div>
                <div role="columnheader" className="whitespace-nowrap px-2 py-2" title="Invopop or GOBL fills the value: always, or only if you send nothing">
                  Auto-filled
                </div>
              </div>
              {sec.shown.map((row) => (
                <div key={row.id} id={row.id} role="rowgroup" className="border-b border-gray-200 last:border-b-0 dark:border-gray-700">
                  <div
                    role="row"
                    style={columns}
                    onClick={() => toggle(row.id)}
                    className="grid cursor-pointer items-center hover:bg-gray-50 dark:hover:bg-gray-800"
                  >
                    <div role="cell" className="px-3 py-2">
                      <button
                        type="button"
                        aria-expanded={open[row.id] ? "true" : "false"}
                        aria-label={"Details of " + row.id}
                        className="flex items-center gap-1.5 whitespace-nowrap font-mono text-xs text-gray-500 dark:text-gray-400"
                      >
                        <Chevron turned={open[row.id]} />
                        {row.id}
                      </button>
                    </div>
                    <div role="cell" className="break-words px-3 py-2 font-mono text-xs text-gray-900 dark:text-gray-100">
                      {soft(row.cfdi)}
                    </div>
                    <div role="cell" className="break-words px-3 py-2 font-mono text-xs text-gray-700 dark:text-gray-300">
                      {soft(row.gobl)}
                    </div>
                    <div role="cell" className="flex items-center px-3 py-2 leading-none">
                      <Badge size="sm" color={levelColor[levelOf(row)] || "gray"} className="whitespace-nowrap">
                        {levelName[levelOf(row)] || levelOf(row)}
                      </Badge>
                    </div>
                    <div role="cell" className="flex items-center gap-1 whitespace-nowrap px-2 py-2 text-xs text-green-700 dark:text-green-400">
                      {isAuto(row) && <Check />}
                      {autoText(row)}
                    </div>
                  </div>
                  {open[row.id] && (
                    <div className="bg-gray-50 pb-3 pl-8 pr-3 pt-1 dark:bg-gray-900">
                      <div
                        role="table"
                        aria-label={"Details of " + row.id}
                        className="overflow-hidden rounded-md border border-gray-200 bg-white text-sm dark:border-gray-700 dark:bg-gray-950"
                      >
                        {details(row).map((d) => (
                          <div
                            key={d[0]}
                            role="row"
                            style={detailColumns}
                            className="grid border-b border-gray-200 last:border-b-0 dark:border-gray-700"
                          >
                            <div
                              role="rowheader"
                              className="border-r border-gray-200 bg-gray-50 px-3 py-1.5 text-xs font-medium leading-5 text-gray-500 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-400"
                            >
                              {d[0]}
                            </div>
                            <div role="cell" className="break-words px-3 py-1.5 leading-5 text-gray-800 dark:text-gray-200">
                              {d[1]}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
