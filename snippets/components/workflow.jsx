export const WorkflowDiagram = ({ workflow }) => {
  const stateColors = {
    processing: "yellow",
    sent: "blue",
    received: "blue",
    registered: "green",
    completed: "green",
    error: "red",
  };

  const StateChip = ({ state, label }) => (
    <Badge size="sm" color={stateColors[state] || "gray"} icon="square-small" iconType="solid">
      {label.charAt(0).toUpperCase() + label.slice(1)}
    </Badge>
  );

  // Icon URL per provider. Keys can be a full provider ("silo.state") or any
  // prefix ("silo", "gov-fr.directory") — the most specific match wins, so a
  // per-action entry overrides its app-wide one. Providers that resolve to no
  // entry (or null) render an empty square.
  const providerIcons = {
    // Core actions
    "silo.state": "https://silo.invopop.com/images/status.svg",
    "silo.close": "https://silo.invopop.com/images/check-badge.svg",
    "silo.if": "https://assets.invopop.com/apps/silo/if.svg",
    "silo.folder": "https://silo.invopop.com/images/folder.svg",
    "silo.modify": "https://silo.invopop.com/images/modify.svg",
    "silo.correct": "https://silo.invopop.com/images/replace.svg",
    "silo.sleep": "https://assets.invopop.com/icons/sleep.svg",
    silo: "https://assets.invopop.com/apps/silo/icon.svg",
    "sequence.enumerate": "https://sequence.invopop.com/images/enumerate.svg",
    "transform.job.create": "https://transform.invopop.com/images/jobs.svg",
    webhook: "https://webhook.invopop.com/icon.svg",
    lookup: "https://lookup.invopop.com/icon.png",
    dropbox: "https://dropbox.invopop.com/icon.png",
    pdf: "https://pdf.invopop.com/file-pdf.svg",
    // Apps
    peppol: "https://assets.invopop.com/apps/peppol/icon.svg",
    ubl: "https://assets.invopop.com/apps/ubl/logo.svg",
    cii: "https://assets.invopop.com/apps/cii/logo.svg",
    "gov-dk": "https://assets.invopop.com/flags/dk.svg",
    "gov-fi": "https://assets.invopop.com/flags/fi.svg",
    "gov-fr": "https://assets.invopop.com/flags/fr.svg",
    "chorus-pro": "https://assets.invopop.com/apps/chroruspro/icon.svg",
    "gov-es": "https://assets.invopop.com/apps/gov-es/icon.svg",
    "gov-es.sii": "https://assets.invopop.com/apps/sii/icon.svg",
    "gov-es.ticketbai": "https://assets.invopop.com/apps/ticketbai/icon.svg",
    "gov-es.facturae": "https://assets.invopop.com/apps/facturae/icon.svg",
    verifactu: "https://assets.invopop.com/apps/verifactu/icon.svg",
    "gov-pl": "https://assets.invopop.com/apps/ksef/icon.svg",
    "gov-sa": "https://assets.invopop.com/apps/zatca/icon.svg",
    "gov-ar": "https://assets.invopop.com/apps/arca/icon.svg",
    "at-pt": "https://assets.invopop.com/apps/at-pt/icon.svg",
    "sat-mx": "https://assets.invopop.com/apps/sat-mexico/icon.svg",
    "sw-sapien": "https://assets.invopop.com/apps/sw-sapien/icon.svg",
    "sdi-it": "https://assets.invopop.com/apps/sdi-italy/icon.svg",
    "ticket-it": "https://assets.invopop.com/apps/agenzia-entrate/icon.svg",
    "nfe-br": "https://assets.invopop.com/apps/notas-fiscais-eletronicas-brazil/icon.svg",
    chargebee: "https://assets.invopop.com/apps/chargebee/icon.svg",
    stripe: "https://assets.invopop.com/apps/stripe/icon.svg",
    email: "https://assets.invopop.com/apps/email/icon.svg",
    cron: "https://assets.invopop.com/apps/cron/icon.svg",
    ilyda: "https://assets.invopop.com/apps/ilyda/icon.svg",
    invoicexpress: "https://assets.invopop.com/apps/invoicexpress/icon.svg",
    plemsi: "https://assets.invopop.com/flags/co.svg",
  };

  const iconFor = (provider) => {
    const parts = (provider || "").split(".");
    for (let i = parts.length; i > 0; i--) {
      const url = providerIcons[parts.slice(0, i).join(".")];
      if (url) return url;
    }
    return null;
  };

  const StepIcon = ({ provider }) => {
    const url = iconFor(provider);
    return (
      <span
        title={provider}
        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md border border-gray-950/10 bg-white dark:border-white/10 dark:bg-white/5"
      >
        {url ? <img src={url} alt="" className="h-4 w-4" /> : null}
      </span>
    );
  };

  // Summaries use inline code with pandoc-style attributes,
  // e.g. "Set state to `sent`{.state .sent}".
  const renderSummary = (summary) => {
    const nodes = [];
    const re = /`([^`]+)`(\{[^}]*\})?/g;
    let last = 0;
    let m;
    let k = 0;
    while ((m = re.exec(summary)) !== null) {
      if (m.index > last) nodes.push(summary.slice(last, m.index));
      const attrs = m[2] || "";
      if (attrs.indexOf(".state") >= 0) {
        const state = (attrs.match(/\.state\s+\.([\w-]+)/) || [])[1] || m[1];
        nodes.push(<StateChip key={k++} state={state} label={m[1]} />);
      } else if (attrs) {
        nodes.push(
          <span key={k++} className="text-sm font-medium text-gray-700 dark:text-gray-300">
            {m[1]}
          </span>
        );
      } else {
        nodes.push(
          <code key={k++} className="text-sm rounded bg-gray-100 px-1 font-mono text-sm dark:bg-white/10">
            {m[1]}
          </code>
        );
      }
      last = m.index + m[0].length;
    }
    if (last < summary.length) nodes.push(summary.slice(last));
    return nodes;
  };

  const NoteRow = ({ text }) => (
    <div className="mt-4 mb-1 font-mono text-sm leading-5 text-gray-400 dark:text-gray-500">{"// " + text}</div>
  );

  const renderSteps = (steps, counter) =>
    (steps || []).map((step) => {
      counter.n += 1;
      const n = counter.n;
      const branches = (step.next || []).filter((b) => b.steps && b.steps.length > 0);
      return (
        <div key={step.id || "step-" + n}>
          {step.notes ? <NoteRow text={step.notes} /> : null}
          <div className="mt-2.5 flex items-center">
            <span className="absolute left-0 w-10 text-center font-mono text-sm text-gray-400 select-none dark:text-gray-500">
              {n}
            </span>
            <div className="flex min-w-0 flex-1 items-center gap-2 rounded-xl border border-gray-950/5 bg-white px-2 py-2 dark:border-white/10 dark:bg-gray-900">
              <StepIcon provider={step.provider} />
              <span className="text-sm shrink-0 font-medium text-gray-900 dark:text-gray-100">{step.name}</span>
              {step.summary ? (
                <span className="text-sm min-w-0 truncate text-gray-500 dark:text-gray-400">{renderSummary(step.summary)}</span>
              ) : null}
            </div>
          </div>
          {branches.length > 0 ? (
            <div className="ml-5 border-l border-gray-200 -my-1 py-1 pl-6 dark:border-white/10">
              {branches.map((branch, bi) => (
                <div key={branch.code || branch.status || bi}>
                  <div className="mt-4">
                    <span className="rounded-md bg-gray-200/70 px-2 py-1 font-mono text-sm text-gray-600 dark:bg-white/10 dark:text-gray-300">
                      {branch.code || branch.status}
                    </span>
                  </div>
                  {renderSteps(branch.steps, counter)}
                </div>
              ))}
            </div>
          ) : null}
        </div>
      );
    });

  const counter = { n: 0 };
  const wf = workflow || {};
  return (
    <div className="not-prose relative my-5 rounded-2xl border border-gray-950/5 bg-gray-50 py-3 pr-4 pb-5 pl-12 dark:border-white/10 dark:bg-white/[0.03]">
      {renderSteps(wf.steps, counter)}
      {wf.rescue && wf.rescue.length > 0 ? (
        <div className="mt-6 border-t border-dashed border-gray-300 dark:border-white/10">
          <NoteRow text="If any step fails" />
          {renderSteps(wf.rescue, counter)}
        </div>
      ) : null}
    </div>
  );
};
