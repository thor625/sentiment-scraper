# src/pages.py

def home_page_html() -> str:
    return """<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Stock Sentiment Report</title>

  <style>
    :root{
      --bg0:#0b0f17;
      --bg1:#0f172a;
      --card:#101826;
      --card2:#0f1a2a;
      --text:#e5e7eb;
      --muted:#94a3b8;
      --line:rgba(255,255,255,.08);
      --accent:#7c3aed;
      --accent2:#22c55e;
      --shadow: 0 18px 60px rgba(0,0,0,.45);
    }

    *{ box-sizing:border-box; }
    body{
      margin:0;
      min-height:100vh;
      font-family: system-ui, -apple-system, sans-serif;
      color: var(--text);
      background:
        radial-gradient(1000px 700px at 15% 10%, rgba(124,58,237,.25), transparent 55%),
        radial-gradient(900px 600px at 90% 30%, rgba(34,197,94,.18), transparent 60%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
      display:block;
      padding:28px;
    }

    .wrap{
      width:min(880px, 100%);
    }

    .header{
      display:flex;
      gap:14px;
      align-items:flex-start;
      justify-content:space-between;
      margin-bottom:14px;
    }

    h1{
      font-size:28px;
      letter-spacing:-0.02em;
      margin:0;
    }

    .sub{
      margin-top:6px;
      color:var(--muted);
      font-size:14px;
      line-height:1.45;
      max-width:60ch;
    }

    .card{
      margin-top:14px;
      background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.03));
      border: 1px solid var(--line);
      border-radius: 18px;
      padding:16px;
      box-shadow: var(--shadow);
      overflow:hidden;
    }

    .formrow{
      display:flex;
      gap:10px;
      align-items:center;
      flex-wrap:wrap;
    }

    label{
      display:block;
      font-size:13px;
      color:var(--muted);
      margin-bottom:8px;
    }

    input[name="symbol"]{
      width:min(520px, 100%);
      padding:12px 12px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: rgba(15, 23, 42, .55);
      color: var(--text);
      outline:none;
    }
    input[name="symbol"]::placeholder{ color: rgba(148,163,184,.75); }
    input[name="symbol"]:focus{
      border-color: rgba(124,58,237,.65);
      box-shadow: 0 0 0 4px rgba(124,58,237,.15);
    }

    button[type="submit"]{
      padding:12px 14px;
      border-radius: 14px;
      border: 1px solid rgba(124,58,237,.55);
      background: linear-gradient(180deg, rgba(124,58,237,.95), rgba(124,58,237,.78));
      color: white;
      font-weight:700;
      cursor:pointer;
      box-shadow: 0 10px 25px rgba(124,58,237,.25);
    }
    button[type="submit"]:hover{
      filter: brightness(1.06);
    }

    .hint{
      margin-top:10px;
      font-size:12px;
      color: rgba(148,163,184,.9);
    }
    .pill{
      display:inline-block;
      padding:4px 10px;
      border-radius:999px;
      border:1px solid var(--line);
      background: rgba(255,255,255,.03);
      margin-right:6px;
      margin-top:6px;
      color: rgba(226,232,240,.9);
    }

    #suggestions{
      width:min(520px, 100%);
      margin-top:10px;
      border:1px solid var(--line);
      border-radius: 14px;
      display:none;
      overflow:hidden;
      background: rgba(2,6,23,.72);
      backdrop-filter: blur(8px);
    }
    #suggestions .row{
      padding:10px 12px;
      cursor:pointer;
      border-top:1px solid var(--line);
    }
    #suggestions .row:hover{
      background: rgba(255,255,255,.05);
    }
    .sym{
      font-weight:800;
      margin-right:8px;
    }
    .desc{
      color: rgba(148,163,184,.95);
      font-size: 13px;
    }

    /* Loading overlay */
    #loading-overlay{
      position:fixed;
      inset:0;
      display:none;
      align-items:center;
      justify-content:center;
      z-index:9999;
      background: rgba(2,6,23,.78);
      backdrop-filter: blur(10px);
    }
    .loader{
      width:min(520px, 92vw);
      border-radius: 18px;
      border:1px solid var(--line);
      background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
      box-shadow: var(--shadow);
      padding:18px;
      text-align:left;
    }
    .loader-title{
      font-size:16px;
      font-weight:800;
      margin:0;
    }
    .loader-sub{
      margin-top:6px;
      color: var(--muted);
      font-size: 13px;
    }
    .bar{
      margin-top:14px;
      height:10px;
      border-radius:999px;
      background: rgba(255,255,255,.06);
      overflow:hidden;
      border:1px solid var(--line);
    }
    .bar > div{
      height:100%;
      width:35%;
      background: linear-gradient(90deg, rgba(124,58,237,.0), rgba(124,58,237,.95), rgba(34,197,94,.85));
      animation: slide 1.05s infinite ease-in-out;
      transform: translateX(-120%);
    }
    @keyframes slide{
      0%{ transform: translateX(-120%); }
      60%{ transform: translateX(260%); }
      100%{ transform: translateX(260%); }
    }
  </style>
</head>

<body>
  <div class="wrap">
    <div class="header">
      <div>
        <h1>Stock Sentiment Report</h1>
        <div class="sub">
          Search a ticker or company name, then we’ll collect the latest quote + news sentiment and take you to the report.
        </div>
      </div>
    </div>

    <div class="card">
      <form id="track-form" action="/track" method="POST" autocomplete="off">
        <label for="symbol-input">Symbol or company</label>
        <div class="formrow">
          <input id="symbol-input" name="symbol" placeholder="Try: aapl, $amd, apple, alphabet…" />
          <button type="submit">View report</button>
        </div>
        <div id="suggestions"></div>

        <div class="hint">
          <span class="pill">Autocomplete via Finnhub</span>
          <span class="pill">Quotes via Stooq</span>
          <span class="pill">News via GDELT</span>
        </div>
      </form>
    </div>
  </div>

  <div id="loading-overlay">
    <div class="loader">
      <div class="loader-title">Collecting data…</div>
      <div class="loader-sub">Fetching quote + news sentiment. You’ll be redirected to the report.</div>
      <div class="bar"><div></div></div>
      <div class="loader-sub" style="margin-top:10px; font-size:12px;">
        If this takes unusually long, refresh and try again.
      </div>
    </div>
  </div>

  <script>
    // --- Autocomplete ---
    const input = document.getElementById("symbol-input");
    const box = document.getElementById("suggestions");
    let lastQuery = "";
    let debounceTimer = null;

    function hideBox() {
      box.style.display = "none";
      box.innerHTML = "";
    }

    function showSuggestions(items) {
      if (!items || items.length === 0) { hideBox(); return; }
      box.innerHTML = "";
      for (const item of items) {
        const row = document.createElement("div");
        row.className = "row";
        const sym = document.createElement("span");
        sym.className = "sym";
        sym.textContent = item.symbol || "";
        const desc = document.createElement("span");
        desc.className = "desc";
        desc.textContent = item.description || "";
        row.appendChild(sym);
        row.appendChild(desc);

        row.onclick = () => {
          input.value = item.symbol;
          hideBox();
          input.focus();
        };
        box.appendChild(row);
      }
      box.style.display = "block";
    }

    async function fetchSuggestions(q) {
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
      if (!res.ok) return [];
      return await res.json();
    }

    input.addEventListener("input", () => {
      const q = input.value.trim();
      if (q === lastQuery) return;
      lastQuery = q;

      if (debounceTimer) clearTimeout(debounceTimer);
      if (q.length < 2) { hideBox(); return; }

      debounceTimer = setTimeout(async () => {
        try {
          const items = await fetchSuggestions(q);
          showSuggestions(items);
        } catch (e) {
          hideBox();
        }
      }, 200);
    });

    document.addEventListener("click", (e) => {
      if (e.target !== input && !box.contains(e.target)) hideBox();
    });

    // --- Loading overlay ---
    const form = document.getElementById("track-form");
    const overlay = document.getElementById("loading-overlay");
    let safetyTimer = null;

    function showLoading() {
      // don’t show loading for empty submits
      const q = (input.value || "").trim();
      if (!q) return;

      overlay.style.display = "flex";

      // SAFETY: never get stuck forever
      if (safetyTimer) clearTimeout(safetyTimer);
      safetyTimer = setTimeout(() => {
        overlay.style.display = "none";
      }, 12000);
    }

    // If the browser uses back/forward cache, ensure overlay is hidden on return
    window.addEventListener("pageshow", () => {
      overlay.style.display = "none";
      if (safetyTimer) clearTimeout(safetyTimer);
    });

    // IMPORTANT: only show on submit (no mousedown/touchstart)
    form.addEventListener("submit", showLoading);
  </script>
</body>
</html>
"""


def report_page_html(
    *,
    resolved: str,
    price_str: str,
    count: int,
    avg_str: str,
    sentiment_text: str,
    pos: int,
    neu: int,
    neg: int,
    hour_rows: str,
    rows: str,
) -> str:
    # derive a CSS class for the sentiment badge
    badge_class = "neutral"
    if "Bullish" in (sentiment_text or ""):
        badge_class = "bullish"
    elif "Bearish" in (sentiment_text or ""):
        badge_class = "bearish"

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Report: {resolved}</title>

  <style>
    :root{{
      --bg0:#0b0f17;
      --bg1:#0f172a;
      --card:#101826;
      --text:#e5e7eb;
      --muted:#94a3b8;
      --line:rgba(255,255,255,.08);
      --accent:#7c3aed;
      --good:#22c55e;
      --bad:#ef4444;
      --warn:#eab308;
      --shadow: 0 18px 60px rgba(0,0,0,.45);
    }}

    *{{ box-sizing:border-box; }}
    body{{
      margin:0;
      min-height:100vh;
      font-family: system-ui, -apple-system, sans-serif;
      color: var(--text);
      background:
        radial-gradient(1000px 700px at 15% 10%, rgba(124,58,237,.25), transparent 55%),
        radial-gradient(900px 600px at 90% 30%, rgba(34,197,94,.18), transparent 60%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
      padding:28px;
    }}

    a{{ color: rgba(167, 139, 250, .95); text-decoration:none; }}
    a:hover{{ text-decoration:underline; }}

    .wrap{{ width:min(980px, 100%); margin:0 auto; }}

    .topbar{{
      display:flex;
      align-items:flex-start;
      justify-content:space-between;
      gap:14px;
      margin-bottom:14px;
    }}

    .title{{
      display:flex;
      flex-direction:column;
      gap:6px;
    }}

    h1{{
      margin:0;
      font-size:26px;
      letter-spacing:-0.02em;
      display:flex;
      align-items:center;
      gap:10px;
      flex-wrap:wrap;
    }}

    .subtitle{{
      color:var(--muted);
      font-size:14px;
      line-height:1.45;
    }}

    .badge{{
      display:inline-flex;
      align-items:center;
      gap:8px;
      font-size:12px;
      font-weight:800;
      padding:6px 10px;
      border-radius:999px;
      border:1px solid var(--line);
      background: rgba(255,255,255,.03);
    }}
    .badge.bullish{{ border-color: rgba(34,197,94,.35); }}
    .badge.bearish{{ border-color: rgba(239,68,68,.35); }}
    .badge.neutral{{ border-color: rgba(234,179,8,.35); }}

    .actions{{
      display:flex;
      gap:10px;
      align-items:center;
      flex-wrap:wrap;
    }}

    .btn{{
      appearance:none;
      border:1px solid var(--line);
      background: rgba(255,255,255,.03);
      color: var(--text);
      font-weight:800;
      border-radius:14px;
      padding:10px 12px;
      cursor:pointer;
    }}
    .btn:hover{{ background: rgba(255,255,255,.06); }}

    .btn.primary{{
      border-color: rgba(124,58,237,.55);
      background: linear-gradient(180deg, rgba(124,58,237,.95), rgba(124,58,237,.78));
      box-shadow: 0 10px 25px rgba(124,58,237,.25);
    }}

    .grid{{
      display:grid;
      grid-template-columns: 1fr 1fr;
      gap:14px;
      margin-top:14px;
    }}
    @media (max-width: 900px) {{
      .grid{{ grid-template-columns:1fr; }}
    }}

    .card{{
      background: linear-gradient(180deg, rgba(255,255,255,.05), rgba(255,255,255,.03));
      border:1px solid var(--line);
      border-radius:18px;
      box-shadow: var(--shadow);
      overflow:hidden;
    }}

    .card .hd{{
      padding:14px 14px 10px 14px;
      border-bottom:1px solid var(--line);
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:10px;
    }}
    .card .hd h2{{
      margin:0;
      font-size:14px;
      letter-spacing:.01em;
      color: rgba(226,232,240,.95);
    }}
    .card .bd{{ padding:14px; }}

    .kpis{{
      display:grid;
      grid-template-columns: repeat(4, minmax(0,1fr));
      gap:10px;
    }}
    @media (max-width: 900px) {{
      .kpis{{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
    }}

    .kpi{{
      padding:12px;
      border:1px solid var(--line);
      border-radius:16px;
      background: rgba(2,6,23,.35);
    }}
    .kpi .label{{ color: var(--muted); font-size:12px; }}
    .kpi .val{{ margin-top:6px; font-weight:900; font-size:18px; }}
    .kpi .sub{{ margin-top:2px; color: var(--muted); font-size:12px; }}

    .split{{
      display:grid;
      grid-template-columns: 1fr 1fr;
      gap:10px;
      margin-top:10px;
    }}
    @media (max-width: 560px) {{
      .split{{ grid-template-columns:1fr; }}
    }}

    .pillrow{{ display:flex; gap:8px; flex-wrap:wrap; }}
    .pill{{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:6px 10px;
      border-radius:999px;
      border:1px solid var(--line);
      background: rgba(255,255,255,.03);
      font-size:12px;
      font-weight:800;
    }}
    .pill.good{{ border-color: rgba(34,197,94,.35); }}
    .pill.neu{{ border-color: rgba(234,179,8,.35); }}
    .pill.bad{{ border-color: rgba(239,68,68,.35); }}

    table{{
      width:100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th, td{{
      padding:10px 10px;
      border-top:1px solid var(--line);
      vertical-align:top;
    }}
    th{{
      text-align:left;
      color: rgba(148,163,184,.95);
      font-weight:800;
      font-size:12px;
      letter-spacing:.02em;
      background: rgba(2,6,23,.25);
    }}
    tr:hover td{{ background: rgba(255,255,255,.03); }}

    .muted{{ color: var(--muted); }}

    /* Loading overlay for "Collect latest" button */
    #loading-overlay{{
      position:fixed;
      inset:0;
      display:none;
      align-items:center;
      justify-content:center;
      z-index:9999;
      background: rgba(2,6,23,.78);
      backdrop-filter: blur(10px);
    }}
    .loader{{
      width:min(520px, 92vw);
      border-radius: 18px;
      border:1px solid var(--line);
      background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
      box-shadow: var(--shadow);
      padding:18px;
      text-align:left;
    }}
    .loader-title{{ font-size:16px; font-weight:900; margin:0; }}
    .loader-sub{{ margin-top:6px; color: var(--muted); font-size: 13px; }}
    .bar{{
      margin-top:14px;
      height:10px;
      border-radius:999px;
      background: rgba(255,255,255,.06);
      overflow:hidden;
      border:1px solid var(--line);
    }}
    .bar > div{{
      height:100%;
      width:35%;
      background: linear-gradient(90deg, rgba(124,58,237,.0), rgba(124,58,237,.95), rgba(34,197,94,.85));
      animation: slide 1.05s infinite ease-in-out;
      transform: translateX(-120%);
    }}
    @keyframes slide{{
      0%{{ transform: translateX(-120%); }}
      60%{{ transform: translateX(260%); }}
      100%{{ transform: translateX(260%); }}
    }}
  </style>
</head>

<body>
  <div class="wrap">
    <div class="topbar">
      <div class="title">
        <h1>
          Report: {resolved}
          <span class="badge {badge_class}">{sentiment_text}</span>
        </h1>
        <div class="subtitle">
          Last 24 hours of news sentiment + your latest stored quote for this symbol.
        </div>
      </div>

      <div class="actions">
        <a class="btn" href="/">← New search</a>

        <button id="collect-btn" class="btn primary" data-symbol="{resolved}">
            Collect latest
        </button>
      </div>
    </div>

    <div class="card">
      <div class="hd">
        <h2>Overview</h2>
        <div class="muted">UTC</div>
      </div>
      <div class="bd">
        <div class="kpis">
          <div class="kpi">
            <div class="label">Latest price</div>
            <div class="val">{price_str}</div>
            <div class="sub">From Stooq</div>
          </div>
          <div class="kpi">
            <div class="label">News mentions</div>
            <div class="val">{count}</div>
            <div class="sub">GDELT (24h)</div>
          </div>
          <div class="kpi">
            <div class="label">Avg sentiment</div>
            <div class="val">{avg_str}</div>
            <div class="sub">VADER compound</div>
          </div>
          <div class="kpi">
            <div class="label">Buckets</div>
            <div class="val" style="font-size:14px; margin-top:10px;">
              <div class="pillrow">
                <span class="pill good">👍 {pos}</span>
                <span class="pill neu">➖ {neu}</span>
                <span class="pill bad">👎 {neg}</span>
              </div>
            </div>
            <div class="sub">≥ 0.2 / between / ≤ -0.2</div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <div class="hd">
          <h2>Mentions per hour</h2>
          <div class="muted">last 24h</div>
        </div>
        <div class="bd" style="padding:0;">
          <table>
            <tr><th style="width:65%;">Hour</th><th>Mentions</th></tr>
            {hour_rows if hour_rows else '<tr><td class="muted">No news mentions in the last 24h.</td><td class="muted">0</td></tr>'}
          </table>
        </div>
      </div>

      <div class="card">
        <div class="hd">
          <h2>Recent headlines</h2>
          <div class="muted">top 25</div>
        </div>
        <div class="bd" style="padding:0;">
          <table>
            <tr><th style="width:160px;">Time (UTC)</th><th style="width:110px;">Sentiment</th><th>Headline</th></tr>
            {rows if rows else '<tr><td class="muted">—</td><td class="muted">NA</td><td class="muted">No headlines stored yet. Click “Collect latest”.</td></tr>'}
          </table>
        </div>
      </div>
    </div>
  </div>

  <div id="loading-overlay">
    <div class="loader">
      <div class="loader-title">Collecting data…</div>
      <div class="loader-sub">Fetching quote + news sentiment. You’ll be redirected back to this report.</div>
      <div class="bar"><div></div></div>
      <div class="loader-sub" style="margin-top:10px; font-size:12px;">
        If this takes unusually long, refresh and try again.
      </div>
    </div>
  </div>

    <script>
    const btn = document.getElementById("collect-btn");
    const overlay = document.getElementById("loading-overlay");

    async function collectAndRefresh() {{
        overlay.style.display = "flex";

        const controller = new AbortController();
        const t = setTimeout(() => controller.abort(), 45000); // 45s timeout

        try {{
        const res = await fetch("/collect", {{
            method: "POST",
            headers: {{ "Content-Type": "application/x-www-form-urlencoded" }},
            body: new URLSearchParams({{ symbol: btn.dataset.symbol }}),
            signal: controller.signal
        }});

        if (!res.ok) {{
            overlay.style.display = "none";
            alert("Collect failed.");
            return;
        }}

        // success -> refresh
        location.reload();

        }} catch (err) {{
        overlay.style.display = "none";
        alert(err.name === "AbortError"
            ? "Collect took too long (timed out). Try again."
            : "Network error while collecting.");
        }} finally {{
        clearTimeout(t);
        }}
    }}

    btn.addEventListener("click", collectAndRefresh);
    </script>
</body>
</html>
"""