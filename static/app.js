/* CodeArena front end: vanilla JS, Monaco editor (with a textarea fallback when offline). */
(() => {
  "use strict";

  const MONACO_BASE = "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min";
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

  // ---------- storage (per-browser conveniences; every access guarded) ----------
  const store = {
    get(key, fallback) {
      try { const v = localStorage.getItem("codearena:" + key); return v === null ? fallback : JSON.parse(v); }
      catch { return fallback; }
    },
    set(key, value) {
      try { localStorage.setItem("codearena:" + key, JSON.stringify(value)); } catch { /* ignore */ }
    },
    del(key) { try { localStorage.removeItem("codearena:" + key); } catch { /* ignore */ } },
  };

  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const md = (text) => {
    const html = window.marked ? marked.parse(text) : `<pre>${esc(text)}</pre>`;
    return window.DOMPurify ? DOMPurify.sanitize(html) : html;
  };
  const fmtMs = (ms) => (ms < 10 ? ms.toFixed(2) : ms < 100 ? ms.toFixed(1) : Math.round(ms).toLocaleString());
  const fmtMB = (kb) => (kb / 1024).toFixed(1);

  function toast(msg) {
    const t = $("#toast");
    t.textContent = msg;
    t.classList.remove("hidden");
    clearTimeout(toast._t);
    toast._t = setTimeout(() => t.classList.add("hidden"), 2600);
  }

  async function api(path, body) {
    const res = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) } : {});
    const data = await res.json().catch(() => ({ error: `HTTP ${res.status}` }));
    if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
    return data;
  }

  // ---------- theme ----------
  function currentTheme() {
    const t = document.documentElement.dataset.theme;
    if (t) return t;
    return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function applyTheme(theme) {
    if (theme) document.documentElement.dataset.theme = theme;
    if (window.monaco) monaco.editor.setTheme(currentTheme() === "dark" ? "vs-dark" : "vs");
  }
  applyTheme(store.get("theme", "dark"));
  $("#theme-toggle").addEventListener("click", () => {
    const next = currentTheme() === "dark" ? "light" : "dark";
    store.set("theme", next);
    applyTheme(next);
  });

  // ---------- editor abstraction ----------
  const editor = {
    impl: null, // "monaco" | "textarea"
    monaco: null,
    textarea: null,
    models: new Map(),
    changeHandler: null,

    async init(el) {
      try {
        await loadMonaco();
        this.impl = "monaco";
        this.monaco = monaco.editor.create(el, {
          automaticLayout: true,
          fontFamily: '"JetBrains Mono", Menlo, monospace',
          fontSize: 13.5,
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          tabSize: 4,
          padding: { top: 10 },
          theme: currentTheme() === "dark" ? "vs-dark" : "vs",
        });
        this.monaco.onDidChangeModelContent(() => this.changeHandler && this.changeHandler());
        this.monaco.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => submit());
        this.monaco.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Quote, () => runTests());
        this.monaco.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => saveNow());
      } catch (e) {
        console.warn("Monaco unavailable, using plain editor", e);
        this.impl = "textarea";
        const ta = document.createElement("textarea");
        ta.className = "fallback-editor";
        ta.spellcheck = false;
        ta.addEventListener("input", () => this.changeHandler && this.changeHandler());
        ta.addEventListener("keydown", (ev) => {
          if (ev.key === "Tab") {
            ev.preventDefault();
            const s = ta.selectionStart;
            ta.setRangeText("    ", s, ta.selectionEnd, "end");
            this.changeHandler && this.changeHandler();
          }
        });
        el.appendChild(ta);
        this.textarea = ta;
      }
    },

    open(key, language, value) {
      if (this.impl === "monaco") {
        let model = this.models.get(key);
        if (!model) {
          model = monaco.editor.createModel(value, language);
          this.models.set(key, model);
        }
        this.monaco.setModel(model);
      } else {
        this.textarea.value = value;
      }
    },
    getValue() { return this.impl === "monaco" ? this.monaco.getValue() : this.textarea.value; },
    setValue(v) {
      if (this.impl === "monaco") {
        // pushEditOperations keeps undo history
        const model = this.monaco.getModel();
        model.pushEditOperations([], [{ range: model.getFullModelRange(), text: v }], () => null);
      } else {
        this.textarea.value = v;
        this.changeHandler && this.changeHandler();
      }
    },
    focus() { this.impl === "monaco" ? this.monaco.focus() : this.textarea.focus(); },
  };

  function loadMonaco() {
    return new Promise((resolve, reject) => {
      if (!window.require || !window.require.config) return reject(new Error("loader missing"));
      window.MonacoEnvironment = {
        getWorkerUrl: () => `data:text/javascript;charset=utf-8,${encodeURIComponent(
          `self.MonacoEnvironment={baseUrl:'${MONACO_BASE}/'};importScripts('${MONACO_BASE}/vs/base/worker/workerMain.js');`)}`,
      };
      require.config({ paths: { vs: `${MONACO_BASE}/vs` } });
      const timer = setTimeout(() => reject(new Error("timeout")), 10000);
      require(["vs/editor/editor.main"], () => { clearTimeout(timer); resolve(); }, (err) => { clearTimeout(timer); reject(err); });
    });
  }

  // ---------- app state ----------
  const state = {
    languages: [],
    problems: [],
    details: new Map(),
    problem: null,
    lang: store.get("language", "python"),
    cases: [], // list of arrays of JSON strings (one per param)
    activeCase: 0,
    lastTest: null,
    activeResultCase: 0,
    solutionLang: null,
    busy: false,
    progress: {}, // problem id -> "solved" | "attempted"
    workspace: null, // saved code / cases / submissions for the open problem
  };

  // Progress, code, test cases and submissions are saved on the server (data/codearena.db).
  const progress = {
    all() { return state.progress; },
    get(id) { return state.progress[id] || null; },
    async refresh() { state.progress = (await api("/api/progress")).progress; },
  };

  function setSaveState(text, bad = false) {
    const el = $("#save-state");
    el.textContent = text;
    el.style.color = bad ? "var(--bad)" : "";
  }

  // Debounced writes to the server, one pending write per key (latest wins).
  const saver = {
    pending: new Map(),
    timers: new Map(),
    schedule(key, url, body, delay = 800) {
      this.pending.set(key, { url, body });
      clearTimeout(this.timers.get(key));
      this.timers.set(key, setTimeout(() => this.flush(key), delay));
      setSaveState("Unsaved changes…");
    },
    async flush(key) {
      clearTimeout(this.timers.get(key));
      const job = this.pending.get(key);
      if (!job) return;
      this.pending.delete(key);
      setSaveState("Saving…");
      try {
        await api(job.url, job.body);
        if (!this.pending.size) setSaveState("Saved ✓");
      } catch (e) {
        if (!this.pending.has(key)) this.pending.set(key, job); // keep it unless a newer write replaced it
        setSaveState("Save failed — retrying…", true);
        this.timers.set(key, setTimeout(() => this.flush(key), 3000));
      }
    },
    flushAll() { return Promise.all([...this.pending.keys()].map((k) => this.flush(k))); },
    // Last-chance save when the tab closes; sendBeacon survives page unload.
    beacon() {
      for (const { url, body } of this.pending.values()) {
        navigator.sendBeacon(url, new Blob([JSON.stringify(body)], { type: "application/json" }));
      }
      this.pending.clear();
    },
  };
  window.addEventListener("pagehide", () => saver.beacon());

  // ---------- routing ----------
  function route() {
    const m = location.hash.match(/^#\/problems\/([\w-]+)/);
    if (m) showProblem(m[1]);
    else showList();
  }

  // ---------- list view ----------
  function showList() {
    $("#view-problem").classList.add("hidden");
    $("#view-list").classList.remove("hidden");
    $("#problem-nav").classList.add("hidden");
    $("#run-actions").classList.add("hidden");
    $("#nav-problems").classList.add("active");
    document.title = "CodeArena";
    renderList();
  }

  function renderList() {
    const q = $("#search").value.trim().toLowerCase();
    const diff = $("#difficulty-filter").value;
    const status = $("#status-filter").value;
    const prog = progress.all();
    const rows = state.problems.filter((p) => {
      if (diff && p.difficulty !== diff) return false;
      const st = prog[p.id] || "todo";
      if (status && st !== status) return false;
      if (q && !(p.title.toLowerCase().includes(q) || [p.category, ...p.tags].some((t) => t.toLowerCase().includes(q)))) return false;
      return true;
    });
    const row = (p) => {
      const st = prog[p.id];
      const icon = st === "solved" ? '<span class="status-solved" title="Solved">✓</span>'
        : st === "attempted" ? '<span class="status-attempted" title="Attempted">◐</span>' : "";
      const n = state.problems.indexOf(p) + 1;
      return `<tr data-id="${esc(p.id)}"><td>${icon}</td><td class="title-cell">${n}. ${esc(p.title)}</td>
        <td><span class="diff diff-${esc(p.difficulty)}">${esc(p.difficulty)}</span></td>
        <td>${p.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join("")}</td></tr>`;
    };
    const groupBy = $("#group-by").value;
    let html;
    if (!groupBy) {
      html = rows.map(row).join("");
    } else {
      // Groups appear in the order of their first problem; "tag" puts a problem under each of its tags.
      const keysOf = (p) => groupBy === "tag" ? (p.tags.length ? p.tags : ["Untagged"]) : [p[groupBy]];
      const groups = new Map();
      if (groupBy === "difficulty") ["Easy", "Medium", "Hard"].forEach((d) => groups.set(d, []));
      rows.forEach((p) => keysOf(p).forEach((k) => (groups.get(k) || groups.set(k, []).get(k)).push(p)));
      const collapsed = store.get("collapsed", {})[groupBy] || [];
      html = [...groups].filter(([, ps]) => ps.length).map(([name, ps]) => {
        const closed = collapsed.includes(name);
        const done = ps.filter((p) => prog[p.id] === "solved").length;
        return `<tr class="group-row${closed ? " closed" : ""}" data-group="${esc(name)}"><td colspan="4">
            <span class="group-caret">▾</span> ${esc(name)}
            <span class="group-count">${done} / ${ps.length} solved</span></td></tr>`
          + (closed ? "" : ps.map(row).join(""));
      }).join("");
    }
    $("#problem-rows").innerHTML = html || `<tr><td colspan="4" class="muted">No problems match.</td></tr>`;

    const solved = state.problems.filter((p) => prog[p.id] === "solved");
    const by = (d) => `${solved.filter((p) => p.difficulty === d).length}/${state.problems.filter((p) => p.difficulty === d).length}`;
    $("#progress-card").innerHTML = `
      <div class="progress-ring">${solved.length}<small> / ${state.problems.length} solved</small></div>
      <div class="progress-split">
        <span class="diff-Easy">Easy ${by("Easy")}</span>
        <span class="diff-Medium">Medium ${by("Medium")}</span>
        <span class="diff-Hard">Hard ${by("Hard")}</span>
      </div>`;
  }

  $("#problem-rows").addEventListener("click", (e) => {
    const group = e.target.closest("tr[data-group]");
    if (group) {
      const all = store.get("collapsed", {});
      const key = $("#group-by").value;
      const list = new Set(all[key] || []);
      list.has(group.dataset.group) ? list.delete(group.dataset.group) : list.add(group.dataset.group);
      all[key] = [...list];
      store.set("collapsed", all);
      return renderList();
    }
    const tr = e.target.closest("tr[data-id]");
    if (tr) location.hash = `#/problems/${tr.dataset.id}`;
  });
  $("#group-by").value = store.get("groupBy", "category");
  $("#group-by").addEventListener("input", () => store.set("groupBy", $("#group-by").value));
  ["#search", "#difficulty-filter", "#status-filter", "#group-by"].forEach((s) => $(s).addEventListener("input", renderList));

  // ---------- problem view ----------
  async function showProblem(id) {
    $("#view-list").classList.add("hidden");
    $("#view-problem").classList.remove("hidden");
    $("#problem-nav").classList.remove("hidden");
    $("#run-actions").classList.remove("hidden");
    $("#nav-problems").classList.remove("active");

    await saver.flushAll();
    let p = state.details.get(id);
    let workspace;
    try {
      [p, workspace] = await Promise.all([p || api(`/api/problems/${id}`), api(`/api/problems/${id}/workspace`)]);
    } catch (e) { toast(e.message); location.hash = "#/"; return; }
    state.details.set(id, p);
    state.problem = p;
    state.workspace = workspace;
    document.title = `${p.title} · CodeArena`;

    const idx = state.problems.findIndex((x) => x.id === id);
    $("#problem-nav-title").textContent = `${idx + 1}. ${p.title}`;
    $("#prev-problem").disabled = idx <= 0;
    $("#next-problem").disabled = idx >= state.problems.length - 1;

    $("#problem-title").textContent = `${idx + 1}. ${p.title}`;
    $("#problem-diff").textContent = p.difficulty;
    $("#problem-diff").className = `diff diff-${p.difficulty}`;
    $("#problem-tags").innerHTML = p.tags.map((t) => `<span class="tag">${esc(t)}</span>`).join("");
    $("#problem-description").innerHTML = md(p.description) +
      `<p class="muted small">Submissions run against ${p.test_count} test cases (including edge cases and large inputs).</p>`;
    updateSolvedBadge();

    // reset per-problem panels
    $("#solution-gate").classList.remove("hidden");
    $("#solution-content").classList.add("hidden");
    $("#result-tab").classList.add("hidden");
    state.lastTest = null;
    $("#test-result").innerHTML = '<p class="muted">Run your code to see results here.</p>';
    selectLeftTab("description");
    selectConsoleTab("testcase");

    if (!state.languages.find((l) => l.id === state.lang && l.available)) {
      state.lang = (state.languages.find((l) => l.available) || state.languages[0]).id;
    }
    $("#language-select").value = state.lang;
    openCode();
    loadCases();
    renderSubmissions();
  }

  function updateSolvedBadge() {
    $("#solved-badge").classList.toggle("hidden", progress.get(state.problem.id) !== "solved");
  }

  const codeKey = () => `code:${state.problem.id}:${state.lang}`;

  function openCode() {
    const p = state.problem;
    const lang = state.languages.find((l) => l.id === state.lang);
    const saved = state.workspace.code[state.lang];
    editor.open(codeKey(), lang.monaco, saved ?? p.starters[state.lang]);
    if (!saver.pending.size) setSaveState(saved ? "Restored your saved code" : "");
  }

  function saveCode(code) {
    const pid = state.problem.id, language = state.lang;
    if (code === null) delete state.workspace.code[language];
    else state.workspace.code[language] = code;
    saver.schedule(`code:${pid}:${language}`, `/api/problems/${pid}/code`, { language, code });
  }

  editor.changeHandler = () => {
    if (state.problem) saveCode(editor.getValue());
  };

  $("#language-select").addEventListener("change", (e) => {
    state.lang = e.target.value;
    store.set("language", state.lang);
    openCode();
    state.lastTest = null;
    $("#test-result").innerHTML = '<p class="muted">Run your code to see results here.</p>';
  });

  $("#reset-code").addEventListener("click", () => {
    if (!confirm("Reset to the starter code? Your current code for this language will be replaced.")) return;
    editor.setValue(state.problem.starters[state.lang]);
    saveCode(null); // forget the saved code so the starter is used
  });

  function step(delta) {
    const idx = state.problems.findIndex((x) => x.id === state.problem.id) + delta;
    if (state.problems[idx]) location.hash = `#/problems/${state.problems[idx].id}`;
  }
  $("#prev-problem").addEventListener("click", () => step(-1));
  $("#next-problem").addEventListener("click", () => step(1));

  // ---------- tabs ----------
  function selectLeftTab(name) {
    $$("#left-tabs .tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
    $$("#left-panel .tab-body").forEach((b) => b.classList.toggle("hidden", b.dataset.body !== name));
  }
  $("#left-tabs").addEventListener("click", (e) => {
    const t = e.target.closest(".tab");
    if (t) selectLeftTab(t.dataset.tab);
  });
  function selectConsoleTab(name) {
    $$("#console-panel .tab").forEach((t) => t.classList.toggle("active", t.dataset.ctab === name));
    $$("#console-panel .console-body").forEach((b) => b.classList.toggle("hidden", b.dataset.cbody !== name));
  }
  $("#console-panel .tabs").addEventListener("click", (e) => {
    const t = e.target.closest(".tab");
    if (t) selectConsoleTab(t.dataset.ctab);
  });

  // ---------- test case editor ----------
  const sampleCases = () => state.problem.samples.map((s) => [...s.args]);

  function saveCases(cases) {
    const pid = state.problem.id;
    state.workspace.cases = cases;
    saver.schedule(`cases:${pid}`, `/api/problems/${pid}/cases`, { cases });
  }

  function loadCases() {
    const saved = state.workspace.cases;
    state.cases = Array.isArray(saved) && saved.every((c) => c.length === state.problem.params.length) ? saved : sampleCases();
    state.activeCase = 0;
    renderCases();
  }

  function renderCases() {
    const chips = state.cases.map((_, i) =>
      `<button class="chip ${i === state.activeCase ? "active" : ""}" data-i="${i}">Case ${i + 1}${state.cases.length > 1 ? ` <span class="x" data-del="${i}" title="Remove">✕</span>` : ""}</button>`
    ).join("");
    $("#case-chips").innerHTML = chips + (state.cases.length < 10 ? `<button class="chip" data-add="1" title="Add a test case">＋</button>` : "");
    const c = state.cases[state.activeCase] || [];
    $("#case-editor").innerHTML = state.problem.params.map((p, j) => `
      <div class="field-label">${esc(p.name)} =<span class="muted"> ${esc(p.type)}</span></div>
      <textarea class="field-input" rows="1" data-j="${j}" spellcheck="false">${esc(c[j] ?? "")}</textarea>`).join("");
    $$("#case-editor textarea").forEach(autosize);
  }

  function autosize(ta) {
    ta.style.height = "auto";
    ta.style.height = Math.min(ta.scrollHeight + 2, 160) + "px";
  }

  $("#case-chips").addEventListener("click", (e) => {
    const del = e.target.closest("[data-del]");
    if (del) {
      e.stopPropagation();
      state.cases.splice(+del.dataset.del, 1);
      state.activeCase = Math.min(state.activeCase, state.cases.length - 1);
      saveCases(state.cases);
      return renderCases();
    }
    const chip = e.target.closest(".chip");
    if (!chip) return;
    if (chip.dataset.add) {
      state.cases.push([...state.cases[state.activeCase]]);
      state.activeCase = state.cases.length - 1;
      saveCases(state.cases);
    } else {
      state.activeCase = +chip.dataset.i;
    }
    renderCases();
  });
  $("#case-editor").addEventListener("input", (e) => {
    const ta = e.target.closest("textarea");
    if (!ta) return;
    state.cases[state.activeCase][+ta.dataset.j] = ta.value;
    saveCases(state.cases);
    autosize(ta);
  });
  $("#reset-cases").addEventListener("click", () => {
    state.cases = sampleCases();
    state.activeCase = 0;
    saveCases(null);
    renderCases();
  });

  function parsedCases() {
    return state.cases.map((c, i) => c.map((v, j) => {
      try { return JSON.parse(v); }
      catch { throw new Error(`Case ${i + 1}: "${state.problem.params[j].name}" is not valid JSON`); }
    }));
  }

  // ---------- run / submit ----------
  function setBusy(busy, which) {
    state.busy = busy;
    $("#run-btn").disabled = busy;
    $("#submit-btn").disabled = busy;
    $("#run-btn").innerHTML = busy && which === "test" ? '<span class="spinner"></span> Running' : "▶ Run";
    $("#submit-btn").innerHTML = busy && which === "submit" ? '<span class="spinner"></span> Judging' : "Submit";
  }

  async function runTests() {
    if (state.busy || !state.problem) return;
    let custom;
    try { custom = parsedCases(); } catch (e) { selectConsoleTab("testcase"); return toast(e.message); }
    setBusy(true, "test");
    selectConsoleTab("testresult");
    $("#test-result").innerHTML = '<div class="running"><span class="spinner"></span> Running sample tests…</div>';
    try {
      const res = await api("/api/run", { problem_id: state.problem.id, language: state.lang, code: editor.getValue(), mode: "test", custom_tests: custom });
      state.lastTest = res;
      state.activeResultCase = Math.max(0, (res.cases || []).findIndex((c) => !c.passed));
      renderTestResult();
    } catch (e) {
      $("#test-result").innerHTML = `<div class="error-box">${esc(e.message)}</div>`;
    } finally {
      setBusy(false);
    }
  }

  function verdictClass(v) { return v === "Accepted" ? "ok" : "bad"; }

  function caseDetail(c) {
    let html = c.name ? `<div class="field-label">Test: ${esc(c.name)}</div>` : "";
    html += c.input.map((f) => `<div class="field-label">${esc(f.name)} =</div><div class="field-value">${esc(f.value)}</div>`).join("");
    if (c.error) html += `<div class="field-label">Error</div><div class="error-box">${esc(c.error)}</div>`;
    if (c.output !== undefined) html += `<div class="field-label">Output</div><div class="field-value ${c.passed ? "" : "bad"}">${esc(c.output)}</div>`;
    html += `<div class="field-label">Expected</div><div class="field-value">${esc(c.expected)}</div>`;
    if (c.message) html += `<div class="message-line">${esc(c.message)}</div>`;
    if (c.stdout) html += `<div class="field-label">Stdout</div><div class="field-value">${esc(c.stdout)}</div>`;
    return html;
  }

  function renderTestResult() {
    const r = state.lastTest;
    const el = $("#test-result");
    if (!r.cases) {
      el.innerHTML = `<div class="verdict bad">${esc(r.verdict)}</div><div class="error-box">${esc(r.error || "")}</div>`;
      return;
    }
    const chips = r.cases.map((c, i) =>
      `<button class="chip ${c.passed ? "pass" : "fail"} ${i === state.activeResultCase ? "active" : ""}" data-i="${i}">Case ${i + 1}</button>`).join("");
    const c = r.cases[state.activeResultCase];
    el.innerHTML = `
      <div class="verdict ${verdictClass(r.verdict)}">${esc(r.verdict)}
        <span class="meta">${r.passed}/${r.total} passed · Runtime ${fmtMs(r.runtime_ms)} ms</span></div>
      <div class="case-chips" id="result-chips">${chips}</div>
      ${caseDetail(c)}`;
    $("#result-chips").addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (chip) { state.activeResultCase = +chip.dataset.i; renderTestResult(); }
    });
  }

  async function submit() {
    if (state.busy || !state.problem) return;
    const code = editor.getValue();
    const problem = state.problem;
    const lang = state.lang;
    setBusy(true, "submit");
    $("#result-tab").classList.remove("hidden");
    selectLeftTab("result");
    $("#submit-result").innerHTML = `<div class="running"><span class="spinner"></span> Judging against ${problem.test_count} test cases…</div>`;
    try {
      const res = await api("/api/run", { problem_id: problem.id, language: lang, code, mode: "submit" });
      const [, ws] = await Promise.all([progress.refresh(), api(`/api/problems/${problem.id}/workspace`)]);
      if (state.problem === problem) {
        state.workspace.submissions = ws.submissions;
        renderSubmitResult(res);
        updateSolvedBadge();
        renderSubmissions();
      }
    } catch (e) {
      $("#submit-result").innerHTML = `<div class="error-box">${esc(e.message)}</div>`;
    } finally {
      setBusy(false);
    }
  }

  function renderSubmitResult(r) {
    const el = $("#submit-result");
    const langName = (state.languages.find((l) => l.id === r.language) || {}).name || r.language;
    if (r.passed === undefined) { // compile error, fatal error, or invalid request
      el.innerHTML = `<div class="result-card"><div class="verdict bad">${esc(r.verdict)}</div>
        <div class="error-box">${esc(r.error || "")}</div></div>`;
      return;
    }
    const pct = r.total ? (100 * r.passed) / r.total : 0;
    let html = `<div class="result-card">
      <div class="verdict ${verdictClass(r.verdict)}">${esc(r.verdict)}<span class="meta">${langName}</span></div>
      <div class="muted">${r.passed} / ${r.total} test cases passed</div>
      <div class="progress-track ${r.verdict === "Accepted" ? "" : "bad"}"><div style="width:${pct}%"></div></div>`;
    if (r.verdict === "Accepted") {
      const ref = r.reference;
      const bar = (mine, theirs) => {
        if (!theirs) return "";
        const ratio = Math.min(1, theirs / Math.max(mine, 1e-9));
        return `<div class="compare-bar" title="Relative to reference"><div style="width:${Math.max(4, ratio * 100)}%"></div></div>`;
      };
      html += `<div class="stat-grid">
        <div class="stat"><div class="stat-label">Runtime (all tests)</div>
          <div class="stat-value">${fmtMs(r.runtime_ms)} <small>ms</small></div>
          <div class="stat-sub">${ref ? `Reference: ${fmtMs(ref.runtime_ms)} ms` : "&nbsp;"}</div>${ref ? bar(r.runtime_ms, ref.runtime_ms) : ""}</div>
        <div class="stat"><div class="stat-label">Peak memory</div>
          <div class="stat-value">${fmtMB(r.memory_kb)} <small>MB</small></div>
          <div class="stat-sub">${ref ? `Reference: ${fmtMB(ref.memory_kb)} MB` : "&nbsp;"}</div>${ref ? bar(r.memory_kb, ref.memory_kb) : ""}</div>
        <div class="stat"><div class="stat-label">Slowest test</div>
          <div class="stat-value">${fmtMs(r.slowest_ms)} <small>ms</small></div>
          <div class="stat-sub">Limit ${Math.round(r.time_limit_ms).toLocaleString()} ms total</div></div>
      </div>
      <p class="muted small" style="margin:12px 0 0">Runtime is time spent inside your function, summed across every test. Memory is the peak resident size of the ${esc(langName)} process (includes interpreter/JVM overhead). Bars compare you with the reference solution in the same language.</p>`;
    } else if (r.error && !r.failed_case) {
      html += `<div class="error-box">${esc(r.error)}</div>`;
    }
    html += "</div>";
    if (r.failed_case) {
      html += `<div class="result-card"><div class="field-label" style="margin-top:0">${r.verdict === "Time Limit Exceeded" && !r.failed_case.error ? "Last test" : "Failed test"} #${r.failed_case.index + 1}</div>${caseDetail(r.failed_case)}</div>`;
    } else if (r.verdict === "Time Limit Exceeded") {
      html += `<div class="error-box">${esc(r.error || "")}</div>`;
    }
    el.innerHTML = html;
  }

  async function saveNow() {
    if (!state.problem) return;
    if (!saver.pending.size) saveCode(editor.getValue());
    await saver.flushAll();
    if (!saver.pending.size) toast("Progress saved");
  }

  $("#run-btn").addEventListener("click", runTests);
  $("#submit-btn").addEventListener("click", submit);
  document.addEventListener("keydown", (e) => {
    if (!(e.metaKey || e.ctrlKey) || !state.problem || $("#view-problem").classList.contains("hidden")) return;
    if (e.key === "Enter") { e.preventDefault(); submit(); }
    else if (e.key === "'") { e.preventDefault(); runTests(); }
    else if (e.key.toLowerCase() === "s") { e.preventDefault(); saveNow(); }
  });

  // ---------- submissions history ----------
  function renderSubmissions() {
    const list = state.workspace.submissions;
    const el = $("#submissions-list");
    if (!list.length) { el.innerHTML = '<p class="muted">No submissions yet.</p>'; return; }
    el.innerHTML = `<div class="sub-row head"><span>Status</span><span>Language</span><span>Runtime</span><span>Memory</span><span>When</span></div>` +
      list.map((s, i) => {
        const lname = (state.languages.find((l) => l.id === s.lang) || {}).name || s.lang;
        const ok = s.verdict === "Accepted";
        return `<div class="sub-row" data-i="${i}" title="Click to load this code into the editor">
          <span class="${ok ? "sub-ok" : "sub-bad"}">${esc(s.verdict)}${!ok && s.total ? ` <span class="muted small">${s.passed}/${s.total}</span>` : ""}</span>
          <span>${esc(lname)}</span>
          <span>${ok ? fmtMs(s.runtime_ms) + " ms" : "—"}</span>
          <span>${ok ? fmtMB(s.memory_kb) + " MB" : "—"}</span>
          <span class="muted">${new Date(s.ts).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</span></div>`;
      }).join("");
  }
  $("#submissions-list").addEventListener("click", (e) => {
    const row = e.target.closest(".sub-row[data-i]");
    if (!row) return;
    const s = state.workspace.submissions[+row.dataset.i];
    if (!s || !confirm("Load this submission's code into the editor?")) return;
    if (s.lang !== state.lang) {
      state.lang = s.lang;
      $("#language-select").value = s.lang;
      store.set("language", s.lang);
      openCode();
    }
    editor.setValue(s.code);
  });

  // ---------- solution ----------
  $("#reveal-solution").addEventListener("click", () => {
    $("#solution-gate").classList.add("hidden");
    $("#solution-content").classList.remove("hidden");
    const langs = state.problem.solution_languages;
    state.solutionLang = langs.includes(state.lang) ? state.lang : langs[0];
    $("#solution-langs").innerHTML = langs.map((id) => {
      const name = (state.languages.find((l) => l.id === id) || {}).name || id;
      return `<button data-lang="${id}">${esc(name)}</button>`;
    }).join("");
    loadSolution();
  });
  $("#solution-langs").addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (b) { state.solutionLang = b.dataset.lang; loadSolution(); }
  });

  async function loadSolution() {
    $$("#solution-langs button").forEach((b) => b.classList.toggle("active", b.dataset.lang === state.solutionLang));
    const problem = state.problem;
    const sol = await api(`/api/problems/${problem.id}/solution?lang=${state.solutionLang}`);
    if (state.problem !== problem) return;
    $("#solution-explanation").innerHTML = md(sol.explanation || "");
    const codeEl = $("#solution-code");
    codeEl.dataset.code = sol.code || "";
    codeEl.textContent = sol.code || "No reference solution for this language yet.";
    if (window.monaco && sol.code) {
      const mode = (state.languages.find((l) => l.id === state.solutionLang) || {}).monaco;
      monaco.editor.colorize(sol.code, mode, { tabSize: 4 }).then((html) => { codeEl.innerHTML = html; });
    }
  }

  $("#copy-solution").addEventListener("click", () => {
    const code = $("#solution-code").dataset.code;
    if (!code || !confirm("Replace the code in your editor with the reference solution?")) return;
    if (state.solutionLang !== state.lang) {
      state.lang = state.solutionLang;
      $("#language-select").value = state.lang;
      store.set("language", state.lang);
      openCode();
    }
    editor.setValue(code);
    toast("Solution copied into the editor");
  });

  // ---------- splitters ----------
  function makeSplitter(handle, onMove) {
    handle.addEventListener("pointerdown", (e) => {
      if (matchMedia("(max-width: 860px)").matches) return;
      handle.setPointerCapture(e.pointerId);
      handle.classList.add("dragging");
      document.body.style.userSelect = "none";
      const move = (ev) => onMove(ev);
      const up = () => {
        handle.classList.remove("dragging");
        document.body.style.userSelect = "";
        handle.removeEventListener("pointermove", move);
        handle.removeEventListener("pointerup", up);
      };
      handle.addEventListener("pointermove", move);
      handle.addEventListener("pointerup", up);
    });
  }
  const layout = store.get("layout", {});
  if (layout.left) $("#left-panel").style.flexBasis = layout.left;
  if (layout.console) $("#console-panel").style.flexBasis = layout.console;
  makeSplitter($("#split-v"), (e) => {
    const box = $("#view-problem").getBoundingClientRect();
    const pct = Math.min(75, Math.max(20, ((e.clientX - box.left) / box.width) * 100));
    $("#left-panel").style.flexBasis = pct + "%";
    layout.left = pct + "%";
    store.set("layout", layout);
  });
  makeSplitter($("#split-h"), (e) => {
    const box = $("#right-col").getBoundingClientRect();
    const pct = Math.min(80, Math.max(12, ((box.bottom - e.clientY) / box.height) * 100));
    $("#console-panel").style.flexBasis = pct + "%";
    layout.console = pct + "%";
    store.set("layout", layout);
  });

  // ---------- boot ----------
  // Earlier versions kept progress in this browser's localStorage. Copy it to the server once
  // (the server never overwrites anything it already has, so this is safe to repeat).
  async function importBrowserData() {
    if (store.get("imported", false)) return;
    const data = { code: [], cases: [], submissions: [] };
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        let m;
        if ((m = key.match(/^codearena:code:([\w-]+):(\w+)$/))) {
          data.code.push({ problem_id: m[1], language: m[2], code: JSON.parse(localStorage.getItem(key)) });
        } else if ((m = key.match(/^codearena:cases:([\w-]+)$/))) {
          data.cases.push({ problem_id: m[1], cases: JSON.parse(localStorage.getItem(key)) });
        } else if ((m = key.match(/^codearena:subs:([\w-]+)$/))) {
          for (const s of JSON.parse(localStorage.getItem(key))) data.submissions.push({ problem_id: m[1], ...s });
        }
      }
    } catch { return; }
    const known = new Set(state.problems.map((p) => p.id));
    const keep = (x) => known.has(x.problem_id);
    data.code = data.code.filter(keep);
    data.cases = data.cases.filter(keep);
    data.submissions = data.submissions.filter(keep);
    const total = data.code.length + data.cases.length + data.submissions.length;
    if (total) {
      const { imported } = await api("/api/import", data);
      const n = imported.code + imported.cases + imported.submissions;
      if (n) toast(`Imported ${n} saved item${n === 1 ? "" : "s"} from this browser`);
    }
    store.set("imported", true);
  }

  async function boot() {
    const [languages, problems] = await Promise.all([api("/api/languages"), api("/api/problems")]);
    state.languages = languages;
    state.problems = problems;
    await importBrowserData().catch((e) => console.warn("Import of browser data failed", e));
    await progress.refresh();
    $("#language-select").innerHTML = languages.map((l) =>
      `<option value="${l.id}" ${l.available ? "" : "disabled"}>${esc(l.name)}${l.available ? "" : " (not installed)"}</option>`).join("");
    await editor.init($("#editor"));
    applyTheme();
    window.addEventListener("hashchange", route);
    route();
  }
  boot().catch((e) => {
    // A 404 from an API route usually means the page was updated but the server wasn't restarted.
    const hint = e.message === "Not found"
      ? " — the server looks out of date. Restart it (Ctrl+C, then .venv/bin/python server.py) and reload this page."
      : e instanceof TypeError ? " — can't reach the server. Is it running?" : "";
    document.body.insertAdjacentHTML("beforeend", `<div class="error-box" style="margin:16px">Failed to start: ${esc(e.message)}${esc(hint)}</div>`);
  });
})();
