"use strict";

/* ------------------------------------------------------------------ utils */
const $ = (id) => document.getElementById(id);
const pct = (v, d = 1) => (v === null || v === undefined ? "—" : (v * 100).toFixed(d) + "%");
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const esc = (s) => String(s).replace(/[&<>"]/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const SVG_NS = "http://www.w3.org/2000/svg";
function el(tag, attrs = {}, text) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (text !== undefined) node.textContent = text;
  return node;
}

const tip = $("tip");
function bindTip(node, html) {
  node.addEventListener("mousemove", (e) => {
    tip.innerHTML = html;
    tip.classList.add("on");
    const pad = 14;
    let x = e.clientX + pad, y = e.clientY + pad;
    const box = tip.getBoundingClientRect();
    if (x + box.width > innerWidth - 8) x = e.clientX - box.width - pad;
    if (y + box.height > innerHeight - 8) y = e.clientY - box.height - pad;
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  });
  node.addEventListener("mouseleave", () => tip.classList.remove("on"));
}

async function api(path, options) {
  const res = await fetch(path, options);
  const data = await res.json();
  if (data && data.error && !data.models) throw new Error(data.error);
  return data;
}

/* -------------------------------------------------------------- run panel */
let DATASET = null;

function checkbox(container, value, label, note, checked) {
  const wrap = document.createElement("label");
  wrap.innerHTML =
    `<input type="checkbox" value="${esc(value)}"${checked ? " checked" : ""}>` +
    `<span>${esc(label)}${note ? ` <span class="note">${esc(note)}</span>` : ""}</span>`;
  container.appendChild(wrap);
  return wrap.querySelector("input");
}

const checkedValues = (id) =>
  [...$(id).querySelectorAll("input:checked")].map((i) => i.value);

function backendQuery() {
  const backend = $("backend").value;
  const params = new URLSearchParams({ backend });
  if (backend === "ollama") params.set("host", $("host").value);
  else {
    params.set("base_url", $("base_url").value);
    if ($("api_key").value) params.set("api_key", $("api_key").value);
  }
  return params;
}

async function loadModels() {
  const box = $("models");
  box.innerHTML = "";
  $("models-msg").textContent = "loading…";
  try {
    const data = await api("/api/models?" + backendQuery());
    $("models-msg").textContent = data.error || `${data.models.length} available`;
    const judge = $("judge");
    judge.innerHTML = '<option value="">none</option>';
    if (!data.models.length) {
      box.innerHTML = '<div class="hint">No models found on this backend.</div>';
    }
    data.models.forEach((name) => {
      // Reasoning models emit chain-of-thought into the response body, which
      // contains both the Quebec and the France term and so reads as high
      // retention and high drift at once. Off by default; the report flags it.
      const reasoning = /qwen3|deepseek-r1|\br1\b|thinking|reasoner/i.test(name);
      checkbox(box, name, name, reasoning ? "· leaks reasoning" : "", !reasoning);
      judge.appendChild(new Option(name, name));
    });
    updatePlan();
  } catch (err) {
    $("models-msg").textContent = String(err.message || err);
  }
  box.addEventListener("change", updatePlan);
}

async function loadDataset() {
  DATASET = await api("/api/dataset");
  const conds = $("conditions");
  conds.innerHTML = "";
  for (const [key, meta] of Object.entries(DATASET.conditions)) {
    checkbox(conds, key, key, meta.label, true);
  }
  const cats = $("categories");
  cats.innerHTML = "";
  for (const [name, counts] of Object.entries(DATASET.categories)) {
    checkbox(cats, name, name, `${counts.qc} QC · ${counts.fr} FR`, true);
  }
  conds.addEventListener("change", updatePlan);
  cats.addEventListener("change", updatePlan);
  updatePlan();
}

function updatePlan() {
  if (!DATASET) return;
  const cats = checkedValues("categories");
  const nTests = Object.entries(DATASET.categories)
    .filter(([name]) => cats.includes(name))
    .reduce((sum, [, c]) => sum + c.qc + c.fr, 0);
  const cells = nTests * checkedValues("conditions").length * checkedValues("models").length;
  $("plan").textContent = cells
    ? `${cells.toLocaleString()} cells (${nTests} tests × ${checkedValues("conditions").length} conditions × ${checkedValues("models").length} models)`
    : "nothing selected";
}

async function start() {
  const backend = $("backend").value;
  const cfg = {
    models: checkedValues("models"),
    conditions: checkedValues("conditions"),
    categories: checkedValues("categories"),
    judge: $("judge").value || null,
    temperature: parseFloat($("temperature").value),
    seed: parseInt($("seed").value, 10),
    num_ctx: parseInt($("num_ctx").value, 10),
    resume: $("resume").checked,
  };
  if (backend === "openai") {
    cfg.base_url = $("base_url").value;
    cfg.api_key = $("api_key").value || null;
  }
  try {
    const state = await api("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cfg),
    });
    render(state);
  } catch (err) {
    $("progress").textContent = String(err.message || err);
  }
}

function render(state) {
  const pill = $("status-pill");
  pill.className = "pill" + (state.running ? " live" : state.error ? " err" : "");
  pill.textContent = state.error ? "error" : state.running ? state.phase : "idle";

  $("start").disabled = state.running;
  $("stop").disabled = !state.running;

  const frac = state.total ? state.done / state.total : 0;
  $("bar").style.width = (frac * 100).toFixed(1) + "%";
  $("progress").textContent = state.total
    ? `${state.done} / ${state.total} cells` +
      (state.current_model ? ` · ${state.current_model}` : "") +
      (state.running ? "" : " · finished")
    : state.error
    ? state.error
    : "Not running.";

  const log = $("log");
  log.innerHTML = state.log
    .map((l) => `<div><span class="t">${esc(l.t)}</span><span>${esc(l.message)}</span></div>`)
    .join("");
  log.scrollTop = log.scrollHeight;
}

let wasRunning = false;
async function poll() {
  try {
    const state = await api("/api/status");
    render(state);
    if (wasRunning && !state.running) loadReport();
    wasRunning = state.running;
  } catch (e) { /* server restarting; the next tick retries */ }
  setTimeout(poll, 1200);
}

/* --------------------------------------------------------------- charts */

/** Grouped horizontal bars: two series, legend + direct value labels. */
function groupedBars(rows, opts) {
  const { labelKey, series, maxValue } = opts;
  const rowH = 46, barH = 13, gap = 2, padL = 178, padR = 62, padT = 8;
  const width = 720, height = padT + rows.length * rowH + 34;
  const plotW = width - padL - padR;
  // Round the domain up to a clean tenth so the ticks read 0/25/50/75/100%
  // of a round number rather than 18/36/55% of the data maximum.
  const rawMax = Math.max(0.1, ...rows.flatMap((r) => series.map((s) => r[s.key] || 0)));
  const max = maxValue || Math.min(1, Math.ceil(rawMax * 10) / 10);
  const x = (v) => (v / max) * plotW;

  const svg = el("svg", {
    viewBox: `0 0 ${width} ${height}`, width: "100%", height: "auto",
    role: "img", "aria-label": opts.aria || "grouped bar chart",
  });

  // Recessive hairline grid, solid, one shade off the surface.
  const ticks = [0, 0.25, 0.5, 0.75, 1].map((t) => t * max);
  ticks.forEach((t) => {
    svg.appendChild(el("line", {
      x1: padL + x(t), x2: padL + x(t), y1: padT, y2: padT + rows.length * rowH,
      stroke: css("--grid"), "stroke-width": 1,
    }));
    svg.appendChild(el("text", {
      x: padL + x(t), y: height - 14, "text-anchor": "middle",
      "font-size": 11, fill: css("--text-muted"),
    }, pct(t, 0)));
  });

  rows.forEach((row, i) => {
    const top = padT + i * rowH;
    svg.appendChild(el("text", {
      x: padL - 12, y: top + rowH / 2 + 4, "text-anchor": "end",
      "font-size": 12, fill: css("--text-primary"),
    }, row[labelKey]));

    series.forEach((s, j) => {
      const value = row[s.key];
      if (value === null || value === undefined) return;
      const w = Math.max(2, x(value));
      const y = top + (rowH - series.length * barH - (series.length - 1) * gap) / 2
              + j * (barH + gap);
      const bar = el("rect", {
        x: padL, y, width: w, height: barH, rx: 4,
        fill: css(s.color),
      });
      bindTip(bar, `<b>${esc(row[labelKey])}</b><br>${esc(s.label)}: <b>${pct(value)}</b>` +
        (row.tipExtra ? `<br>${row.tipExtra}` : ""));
      svg.appendChild(bar);
      svg.appendChild(el("text", {
        x: padL + w + 7, y: y + barH - 2, "font-size": 11,
        fill: css("--text-secondary"),
      }, pct(value, 0)));
    });
  });

  svg.appendChild(el("line", {
    x1: padL, x2: padL, y1: padT, y2: padT + rows.length * rowH,
    stroke: css("--baseline"), "stroke-width": 1,
  }));
  return svg;
}

const BINS = [
  { max: 0.10, varName: "--seq-100", label: "0–10%" },
  { max: 0.25, varName: "--seq-250", label: "10–25%" },
  { max: 0.40, varName: "--seq-400", label: "25–40%" },
  { max: 0.60, varName: "--seq-550", label: "40–60%" },
  { max: 1.01, varName: "--seq-700", label: "60%+" },
];
const binOf = (v) => BINS.findIndex((b) => v < b.max);

/** Pick readable ink for a fill by its luminance.
 *  The ramp runs surface-ward for low values, so which end is light flips
 *  between light and dark mode -- keying the label off the bin index would be
 *  right in one mode and unreadable in the other. */
function inkOn(hex) {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex.trim());
  if (!m) return css("--text-primary");
  const n = parseInt(m[1], 16);
  const lin = (c) => (c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4));
  const L = 0.2126 * lin(((n >> 16) & 255) / 255)
          + 0.7152 * lin(((n >> 8) & 255) / 255)
          + 0.0722 * lin((n & 255) / 255);
  return L > 0.42 ? "#0b0b0b" : "#ffffff";
}

/** Heatmap over one sequential hue; every cell carries its own value label. */
function heatmap(rowNames, colNames, valueAt, opts = {}) {
  const cellW = 104, cellH = 40, padL = 178, padT = 30, gap = 2;
  const width = padL + colNames.length * cellW;
  const height = padT + rowNames.length * cellH;
  const svg = el("svg", {
    viewBox: `0 0 ${width} ${height}`, width: "100%", height: "auto",
    role: "img", "aria-label": opts.aria || "heatmap",
  });

  colNames.forEach((c, j) => svg.appendChild(el("text", {
    x: padL + j * cellW + cellW / 2, y: padT - 11, "text-anchor": "middle",
    "font-size": 11, fill: css("--text-secondary"),
  }, c)));

  rowNames.forEach((r, i) => {
    svg.appendChild(el("text", {
      x: padL - 12, y: padT + i * cellH + cellH / 2 + 4, "text-anchor": "end",
      "font-size": 12, fill: css("--text-primary"),
    }, r));
    colNames.forEach((c, j) => {
      const v = valueAt(r, c);
      const x = padL + j * cellW, y = padT + i * cellH;
      if (v === null || v === undefined) {
        svg.appendChild(el("text", {
          x: x + cellW / 2, y: y + cellH / 2 + 4, "text-anchor": "middle",
          "font-size": 12, fill: css("--text-muted"),
        }, "—"));
        return;
      }
      const bin = binOf(v);
      const fill = css(BINS[bin].varName);
      const cell = el("rect", {
        x, y, width: cellW - gap, height: cellH - gap, rx: 4, fill,
      });
      bindTip(cell, `<b>${esc(r)}</b> · ${esc(c)}<br>drift <b>${pct(v)}</b>`);
      svg.appendChild(cell);
      // Value labels are not decoration: three ramp steps sit below 3:1 on the
      // light surface, so the number carries the reading, not the fill alone.
      svg.appendChild(el("text", {
        x: x + (cellW - gap) / 2, y: y + cellH / 2 + 4, "text-anchor": "middle",
        "font-size": 12, "font-weight": 600, fill: inkOn(fill),
      }, pct(v, 0)));
    });
  });
  return svg;
}

function rampLegend() {
  const wrap = document.createElement("div");
  wrap.className = "legend";
  wrap.innerHTML = BINS.map((b) =>
    `<span><i class="swatch" style="background:${css(b.varName)}"></i>${b.label}</span>`
  ).join("");
  return wrap;
}

/* --------------------------------------------------------------- results */
function section(title, hint) {
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `<h2>${esc(title)}</h2>` + (hint ? `<p class="hint">${hint}</p>` : "");
  return card;
}

async function loadReport() {
  const report = await api("/api/report");
  const body = $("results-body");
  body.innerHTML = "";

  if (!report.models || !report.models.length) {
    body.innerHTML = '<div class="card"><div class="empty">No results yet. ' +
      'Run the experiment from the Run tab.</div></div>';
    return;
  }
  const models = report.models.map((m) => m.meta.model);

  /* Headline — matched pairs answer the question the whole harness exists for. */
  const matched = report.matched_attractor || {};
  if (Object.keys(matched).length) {
    const card = section("Is “generic French” actually generic?",
      "Under the <strong>baseline</strong> prompt, which names no variety. Each Quebec " +
      "sentence is paired with a France sentence that differs only in variety, so this " +
      "compares like with like. Symmetric drift means the model is simply rewriting; " +
      "Quebec drifting further means its default French has a centre of gravity.");

    const rows = Object.entries(matched).map(([name, a]) => ({
      model: name, qc: a.qc_to_fr_drift, fr: a.fr_to_qc_drift,
      tipExtra: `Quebec drifted more in <b>${a.pairs_qc_higher}</b> of ` +
                `${a.n_pairs} pairs, France in <b>${a.pairs_fr_higher}</b>`,
    }));
    const legend = document.createElement("div");
    legend.className = "legend";
    legend.innerHTML =
      `<span><i class="swatch" style="background:${css("--series-1")}"></i>Quebec input → France forms</span>` +
      `<span><i class="swatch" style="background:${css("--series-2")}"></i>France input → Quebec forms</span>`;
    card.appendChild(legend);
    card.appendChild(groupedBars(rows, {
      labelKey: "model",
      series: [
        { key: "qc", label: "Quebec → France", color: "--series-1" },
        { key: "fr", label: "France → Quebec", color: "--series-2" },
      ],
      aria: "Drift rate by model and input variety, matched pairs",
    }));

    const table = document.createElement("div");
    table.className = "scroll-x";
    table.innerHTML = `<table><thead><tr>
      <th>Model</th><th class="num">Pairs</th><th class="num">QC→FR</th>
      <th class="num">FR→QC</th><th class="num">Asymmetry</th>
      <th class="num">QC higher</th><th class="num">FR higher</th>
      <th class="num">Tied</th><th class="num">p (McNemar)</th></tr></thead><tbody>` +
      Object.entries(matched).map(([name, a]) => {
        const st = a.sign_test;
        const p = !st ? "—" : st.p_value < 0.001 ? "&lt; 0.001" : st.p_value.toFixed(3);
        return `<tr><td>${esc(name)}</td><td class="num">${a.n_pairs}</td>
          <td class="num">${pct(a.qc_to_fr_drift)}</td>
          <td class="num">${pct(a.fr_to_qc_drift)}</td>
          <td class="num">${pct(a.asymmetry)}</td>
          <td class="num">${a.pairs_qc_higher}</td><td class="num">${a.pairs_fr_higher}</td>
          <td class="num">${a.pairs_tied}</td><td class="num">${p}</td></tr>`;
      }).join("") + "</tbody></table>";
    card.appendChild(table);
    card.insertAdjacentHTML("beforeend",
      '<p class="hint" style="margin-top:12px">Two-sided exact McNemar (sign) test on ' +
      'the discordant pairs. Tied pairs carry no directional information and are ' +
      'excluded from the test but shown for context.</p>');
    body.appendChild(card);
  }

  /* Per-model scorecard. */
  const card = section("Scorecard", "Quebec-origin items only. All figures mechanical.");
  card.insertAdjacentHTML("beforeend", `<div class="scroll-x"><table><thead><tr>
    <th>Model</th><th class="num">CLR baseline</th><th class="num">MDR baseline</th>
    <th class="num">MDR Quebec prompt</th><th class="num">QFCR proofread</th>
    <th class="num">Left untouched</th><th>Positive control</th>
    </tr></thead><tbody>` +
    report.models.map((m) => {
      const s = m.scorecard, pc = m.positive_control;
      const ctrl = !pc ? "—" : pc.passed
        ? '<span class="status good">✓ passed</span>'
        : '<span class="status bad">✕ failed</span>';
      return `<tr><td>${esc(m.meta.model)}</td>
        <td class="num">${pct(s.CLR_baseline)}</td>
        <td class="num">${pct(s.MDR_baseline)}</td>
        <td class="num">${pct(s.MDR_prompted)}</td>
        <td class="num">${pct(s.QFCR_proofread)}</td>
        <td class="num">${pct(s.unchanged_proofread)}</td>
        <td>${ctrl}</td></tr>`;
    }).join("") + "</tbody></table></div>");
  card.insertAdjacentHTML("beforeend",
    '<p class="hint" style="margin-top:12px"><strong>QFCR and “left untouched” are ' +
    'entangled</strong> — a model that declines to edit anything scores a perfect ' +
    'false-correction rate. The <strong>positive control</strong> checks that naming ' +
    'France drives more drift than naming no variety at all; where it fails, that ' +
    'model’s conditions are not cleanly separated and its numbers are not ' +
    'interpretable on their own.</p>');
  body.appendChild(card);

  /* Category heatmap. */
  const cats = [...new Set(report.models.flatMap((m) => Object.keys(m.by_category)))];
  if (cats.length) {
    const h = section("Baseline drift by category",
      "Quebec-origin items under the variety-neutral prompt. The scale runs from " +
      "least to most drift; every cell also carries its value.");
    h.appendChild(rampLegend());
    const byModel = Object.fromEntries(report.models.map((m) => [m.meta.model, m.by_category]));
    const wrap = document.createElement("div");
    wrap.className = "scroll-x";
    wrap.appendChild(heatmap(models, cats,
      (m, c) => (byModel[m][c] ? byModel[m][c].cross_substitution : null),
      { aria: "Baseline drift by model and category" }));
    h.appendChild(wrap);
    body.appendChild(h);
  }

  /* Condition heatmap. */
  const conds = [...new Set(report.models.flatMap((m) => Object.keys(m.by_condition)))];
  if (conds.length) {
    const h = section("Quebec drift by prompt condition",
      "How much the instruction actually changes the outcome.");
    h.appendChild(rampLegend());
    const byModel = Object.fromEntries(report.models.map((m) => [m.meta.model, m.by_condition]));
    const wrap = document.createElement("div");
    wrap.className = "scroll-x";
    wrap.appendChild(heatmap(models, conds,
      (m, c) => (byModel[m][c] ? byModel[m][c].qc.cross_substitution : null),
      { aria: "Drift by model and prompt condition" }));
    h.appendChild(wrap);
    body.appendChild(h);
  }

  /* Worst failures, per model — more useful than any aggregate. */
  report.models.forEach((m) => {
    if (!m.failures.length) return;
    const f = section(`Worst failures — ${m.meta.model}`,
      `${m.n_results} results${m.suspect_reasoning_leaks
        ? ` · <strong style="color:${css("--critical")}">${m.suspect_reasoning_leaks} outputs look like leaked reasoning; treat this model's scores as unreliable</strong>`
        : ""}`);
    m.failures.slice(0, 8).forEach((x) => {
      const subs = (x.substitutions || [])
        .map((s) => `${esc(s.from)} → ${esc(s.to)}`).join(", ");
      const div = document.createElement("div");
      div.className = "failure";
      div.innerHTML =
        `<div class="meta"><strong>${esc(x.test_id)}</strong> · ${esc(x.category)} · ` +
        `${esc(x.condition)}${subs ? ` · <span class="sub">${subs}</span>` : ""}</div>` +
        `<p class="in">${esc(x.input)}</p><p>${esc(x.output)}</p>`;
      f.appendChild(div);
    });
    body.appendChild(f);
  });
}

/* ------------------------------------------------------------------ boot */
function selectTab(name) {
  for (const t of ["run", "results"]) {
    $("tab-" + t).setAttribute("aria-selected", String(t === name));
    $("panel-" + t).hidden = t !== name;
  }
  if (name === "results") loadReport();
}

$("tab-run").onclick = () => selectTab("run");
$("tab-results").onclick = () => selectTab("results");
$("refresh-models").onclick = loadModels;
$("start").onclick = start;
$("stop").onclick = () => api("/api/stop", { method: "POST" }).then(render);
$("backend").onchange = () => {
  const isOllama = $("backend").value === "ollama";
  $("field-host").hidden = !isOllama;
  $("field-baseurl").hidden = isOllama;
  $("field-apikey").hidden = isOllama;
  loadModels();
};

loadDataset().then(loadModels);
poll();
