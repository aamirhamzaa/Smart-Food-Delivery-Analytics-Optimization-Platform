#!/usr/bin/env python3
"""
build_viewer.py - Generates a premium HTML dashboard viewer
for all pipeline outputs: charts, maps, reports, and data files.
"""

import os
import glob
import html as html_mod
from pathlib import Path


def build_viewer():
    base = "output"

    # ── Discover output files ──────────────────────────────────
    charts = sorted(glob.glob(f"{base}/charts/*.png"))
    maps_files = sorted(glob.glob(f"{base}/maps/*.html"))
    csv_files = sorted(glob.glob(f"{base}/reports/*.csv"))

    report_path = f"{base}/reports/final_report.txt"
    report_text = ""
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            report_text = f.read()

    dashboard_exists = os.path.exists(f"{base}/reports/executive_dashboard.html")

    # Relative paths from output/ (where viewer.html lives)
    chart_rels = [os.path.relpath(c, base) for c in charts]
    map_rels = [os.path.relpath(m, base) for m in maps_files]
    csv_rels = [os.path.relpath(c, base) for c in csv_files]

    # ── Build chart cards ──────────────────────────────────────
    chart_cards = ""
    for i, path in enumerate(chart_rels):
        name = Path(path).stem.replace("_", " ").title()
        chart_cards += f'''
            <div class="chart-card animate-in" style="animation-delay:{i*0.07}s"
                 onclick="openLightbox('{path}','{name}')">
                <div class="chart-img-wrap">
                    <img src="{path}" alt="{name}" loading="lazy">
                    <div class="chart-hover"><span class="expand-icon">⛶</span></div>
                </div>
                <div class="chart-label">{name}</div>
            </div>'''

    # ── Build map tabs / panels ────────────────────────────────
    map_tabs = ""
    map_panels = ""
    for i, path in enumerate(map_rels):
        name = Path(path).stem.replace("_", " ").title()
        active = " active" if i == 0 else ""
        display = "block" if i == 0 else "none"
        map_tabs += (
            f'<button class="map-tab{active}" '
            f'onclick="switchMap({i},this)">{name}</button>\n'
        )
        map_panels += (
            f'<iframe class="map-frame" id="map-{i}" '
            f'src="{path}" style="display:{display}"></iframe>\n'
        )

    # ── Build data-file cards ──────────────────────────────────
    csv_links = ""
    for i, path in enumerate(csv_rels):
        name = Path(path).stem.replace("_", " ").title()
        csv_links += f'''
            <a href="{path}" class="data-card animate-in"
               style="animation-delay:{i*0.1}s" download>
                <div class="file-icon">📊</div>
                <div class="file-info">
                    <div class="file-name">{name}</div>
                    <div class="file-type">CSV Data File</div>
                </div>
                <div class="dl-icon">⬇</div>
            </a>'''

    report_html = html_mod.escape(report_text) if report_text else (
        "<em>No report generated yet.</em>"
    )

    n_charts = len(chart_rels)
    n_maps = len(map_rels)
    n_data = len(csv_rels)
    n_total = n_charts + n_maps + n_data + (1 if dashboard_exists else 0)

    # ── Optional dashboard section ─────────────────────────────
    dash_section = ""
    dash_nav = ""
    if dashboard_exists:
        dash_nav = (
            '<a class="nav-item" onclick="goTo(\'sec-dash\')">'
            '<span class="ni">▣</span> Dashboard</a>'
        )
        dash_section = '''
        <div class="section" id="sec-dash">
            <div class="sh"><h2>Executive Dashboard</h2>
            <p class="ss">Interactive business-intelligence overview</p></div>
            <div class="dash-wrap animate-in">
                <iframe src="reports/executive_dashboard.html"
                        class="dash-frame"></iframe>
                <a href="reports/executive_dashboard.html" target="_blank"
                   class="ext-link">Open in New Tab ↗</a>
            </div>
        </div>'''

    # ── Particles for loader ───────────────────────────────────
    particles = "".join(
        f'<div class="particle" style="left:{(i*17)%100}%;'
        f'animation-delay:{i*0.4:.1f}s;'
        f'animation-duration:{3+i%3}s"></div>'
        for i in range(20)
    )

    # ── Maps or placeholder ────────────────────────────────────
    maps_body = (
        f'<div class="map-tabs">{map_tabs}</div>'
        f'<div class="map-box">{map_panels}</div>'
        if map_tabs
        else '<p class="empty">No maps found in output/maps/</p>'
    )

    charts_body = (
        chart_cards
        if chart_cards
        else '<p class="empty">No charts found in output/charts/</p>'
    )

    data_body = (
        csv_links
        if csv_links
        else '<p class="empty">No CSV files found in output/reports/</p>'
    )

    # ══════════════════════════════════════════════════════════
    #  FULL HTML
    # ══════════════════════════════════════════════════════════
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Smart Food Delivery — Analytics Viewer</title>
<style>
/* ════════ RESET ════════ */
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg0:#06060e;--bg1:#0d0d1a;
  --card:rgba(255,255,255,.03);--card-h:rgba(255,255,255,.06);
  --bdr:rgba(255,255,255,.06);--bdr-h:rgba(255,255,255,.12);
  --t1:#e8eaf0;--t2:#8a8fa8;--t3:#555a70;
  --a1:#6366f1;--a2:#8b5cf6;--a3:#06b6d4;
  --g1:linear-gradient(135deg,#6366f1,#8b5cf6);
  --g2:linear-gradient(135deg,#06b6d4,#6366f1);
  --g3:linear-gradient(135deg,#8b5cf6,#ec4899);
  --g4:linear-gradient(135deg,#f59e0b,#ef4444);
  --sw:260px;--rad:16px;--rads:10px;
}}
html{{scroll-behavior:smooth}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Inter',Roboto,sans-serif;
  background:var(--bg0);color:var(--t1);line-height:1.6;overflow-x:hidden}}

/* ════════ LOADER ════════ */
#loader{{position:fixed;inset:0;z-index:10000;background:var(--bg0);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  transition:opacity .6s,visibility .6s}}
#loader.done{{opacity:0;visibility:hidden;pointer-events:none}}
.ld-logo{{font-size:2.8rem;font-weight:800;
  background:var(--g1);-webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;margin-bottom:40px;animation:pulse 2s ease-in-out infinite}}
.ld-sub{{color:var(--t2);font-size:.95rem;margin-bottom:30px;
  letter-spacing:3px;text-transform:uppercase}}
.prog-wrap{{width:280px;height:3px;background:rgba(255,255,255,.06);
  border-radius:4px;overflow:hidden}}
.prog-bar{{height:100%;width:0;background:var(--g1);border-radius:4px;
  transition:width .3s;box-shadow:0 0 20px rgba(99,102,241,.4)}}
.ld-stat{{color:var(--t3);font-size:.8rem;margin-top:16px;letter-spacing:1px}}
.particles{{position:absolute;inset:0;overflow:hidden;pointer-events:none}}
.particle{{position:absolute;width:2px;height:2px;background:var(--a1);
  border-radius:50%;opacity:0;animation:floatp 4s ease-in-out infinite}}
@keyframes floatp{{
  0%{{opacity:0;transform:translateY(100vh) scale(0)}}
  50%{{opacity:.6}}
  100%{{opacity:0;transform:translateY(-100px) scale(1)}}}}
@keyframes pulse{{
  0%,100%{{filter:brightness(1);transform:scale(1)}}
  50%{{filter:brightness(1.2);transform:scale(1.02)}}}}
@keyframes shimmer{{
  0%{{background-position:-200% 0}}
  100%{{background-position:200% 0}}}}

/* ════════ SIDEBAR ════════ */
.sidebar{{position:fixed;left:0;top:0;width:var(--sw);height:100vh;
  background:var(--bg1);border-right:1px solid var(--bdr);z-index:100;
  display:flex;flex-direction:column;padding:32px 0;
  transition:transform .3s}}
.sb-brand{{padding:0 24px;margin-bottom:40px}}
.sb-brand h1{{font-size:1.15rem;font-weight:700;
  background:var(--g1);-webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;line-height:1.3}}
.sb-brand span{{font-size:.7rem;color:var(--t3);letter-spacing:2px;
  text-transform:uppercase;display:block;margin-top:6px}}
.sb-nav{{flex:1;display:flex;flex-direction:column;gap:2px;padding:0 12px}}
.nav-item{{display:flex;align-items:center;gap:14px;
  padding:12px 16px;border-radius:var(--rads);color:var(--t2);
  text-decoration:none;font-size:.88rem;font-weight:500;cursor:pointer;
  transition:all .2s;border:1px solid transparent}}
.nav-item:hover{{background:var(--card-h);color:var(--t1);border-color:var(--bdr)}}
.nav-item.active{{background:rgba(99,102,241,.1);color:#a5b4fc;
  border-color:rgba(99,102,241,.2)}}
.ni{{font-size:1.15rem;width:24px;text-align:center}}
.sb-foot{{padding:20px 24px;border-top:1px solid var(--bdr);margin-top:auto}}
.sb-foot p{{font-size:.7rem;color:var(--t3);line-height:1.5}}

/* ════════ MAIN ════════ */
.main{{margin-left:var(--sw);min-height:100vh;position:relative}}
.bg-grid{{position:fixed;inset:0;
  background-image:
    linear-gradient(rgba(255,255,255,.015) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.015) 1px,transparent 1px);
  background-size:60px 60px;pointer-events:none;z-index:0}}
.glow{{position:fixed;width:600px;height:600px;border-radius:50%;
  filter:blur(120px);opacity:.07;pointer-events:none;z-index:0}}
.g1{{top:-200px;right:-100px;background:var(--a1)}}
.g2{{bottom:-200px;left:200px;background:var(--a2)}}
.content{{position:relative;z-index:1;padding:40px 48px 80px}}

/* ════════ HERO ════════ */
.hero{{padding:60px 0 40px;text-align:center}}
.hero h1{{font-size:2.8rem;font-weight:800;line-height:1.15;margin-bottom:16px;
  background:linear-gradient(135deg,#e8eaf0,#a5b4fc,#c4b5fd);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.hero p{{color:var(--t2);font-size:1.05rem;max-width:500px;margin:0 auto}}
.hero-bar{{width:60px;height:3px;background:var(--g1);border-radius:3px;
  margin:28px auto 0}}

/* ════════ STAT CARDS ════════ */
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
  gap:20px;margin:48px 0}}
.sc{{background:var(--card);border:1px solid var(--bdr);border-radius:var(--rad);
  padding:28px;text-align:center;transition:all .35s;position:relative;overflow:hidden}}
.sc::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  opacity:0;transition:opacity .35s}}
.sc:nth-child(1)::before{{background:var(--g1)}}
.sc:nth-child(2)::before{{background:var(--g2)}}
.sc:nth-child(3)::before{{background:var(--g3)}}
.sc:nth-child(4)::before{{background:var(--g4)}}
.sc:hover{{background:var(--card-h);border-color:var(--bdr-h);transform:translateY(-4px)}}
.sc:hover::before{{opacity:1}}
.sn{{font-size:2.2rem;font-weight:800;
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.sc:nth-child(1) .sn{{background:var(--g1);-webkit-background-clip:text;background-clip:text}}
.sc:nth-child(2) .sn{{background:var(--g2);-webkit-background-clip:text;background-clip:text}}
.sc:nth-child(3) .sn{{background:var(--g3);-webkit-background-clip:text;background-clip:text}}
.sc:nth-child(4) .sn{{background:var(--g4);-webkit-background-clip:text;background-clip:text}}
.sl{{color:var(--t2);font-size:.8rem;text-transform:uppercase;
  letter-spacing:1.5px;margin-top:8px}}

/* ════════ SECTIONS ════════ */
.section{{margin-bottom:72px;scroll-margin-top:40px}}
.sh{{margin-bottom:32px}}
.sh h2{{font-size:1.7rem;font-weight:700;display:flex;align-items:center;gap:12px}}
.sh h2::before{{content:'';width:4px;height:28px;background:var(--g1);
  border-radius:4px;display:inline-block}}
.ss{{color:var(--t2);font-size:.9rem;margin-top:8px;margin-left:16px}}
.empty{{color:var(--t3);font-style:italic}}

/* ════════ CHARTS ════════ */
.chart-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(380px,1fr));gap:24px}}
.chart-card{{background:var(--card);border:1px solid var(--bdr);
  border-radius:var(--rad);overflow:hidden;cursor:pointer;
  transition:all .35s cubic-bezier(.4,0,.2,1)}}
.chart-card:hover{{border-color:rgba(99,102,241,.3);transform:translateY(-6px);
  box-shadow:0 20px 40px rgba(0,0,0,.3),0 0 40px rgba(99,102,241,.05)}}
.chart-img-wrap{{position:relative;overflow:hidden;
  background:rgba(255,255,255,.02);aspect-ratio:4/3}}
.chart-img-wrap img{{width:100%;height:100%;object-fit:contain;padding:12px;
  transition:transform .5s cubic-bezier(.4,0,.2,1)}}
.chart-card:hover img{{transform:scale(1.05)}}
.chart-hover{{position:absolute;inset:0;background:rgba(6,6,14,.6);
  display:flex;align-items:center;justify-content:center;
  opacity:0;transition:opacity .3s}}
.chart-card:hover .chart-hover{{opacity:1}}
.expand-icon{{font-size:2rem;color:#fff;
  background:rgba(99,102,241,.3);width:56px;height:56px;
  display:flex;align-items:center;justify-content:center;
  border-radius:50%;border:1px solid rgba(255,255,255,.15);
  backdrop-filter:blur(10px)}}
.chart-label{{padding:16px 20px;font-size:.88rem;font-weight:600;
  color:var(--t2);border-top:1px solid var(--bdr)}}

/* ════════ LIGHTBOX ════════ */
.lb{{position:fixed;inset:0;z-index:9999;background:rgba(6,6,14,.92);
  backdrop-filter:blur(20px);display:flex;align-items:center;
  justify-content:center;flex-direction:column;
  opacity:0;visibility:hidden;transition:all .3s;cursor:pointer}}
.lb.on{{opacity:1;visibility:visible}}
.lb img{{max-width:85vw;max-height:78vh;object-fit:contain;
  border-radius:var(--rad);box-shadow:0 20px 60px rgba(0,0,0,.5);
  transform:scale(.9);transition:transform .4s cubic-bezier(.4,0,.2,1)}}
.lb.on img{{transform:scale(1)}}
.lb-title{{color:var(--t1);font-size:1.1rem;font-weight:600;margin-top:20px;
  opacity:0;transform:translateY(10px);transition:all .4s ease .15s}}
.lb.on .lb-title{{opacity:1;transform:translateY(0)}}
.lb-x{{position:absolute;top:24px;right:32px;font-size:1.4rem;color:var(--t2);
  cursor:pointer;width:44px;height:44px;display:flex;align-items:center;
  justify-content:center;border-radius:50%;border:1px solid var(--bdr);
  background:var(--card);transition:all .2s}}
.lb-x:hover{{background:var(--card-h);color:var(--t1);border-color:var(--bdr-h)}}

/* ════════ MAPS ════════ */
.map-tabs{{display:flex;gap:8px;margin-bottom:20px;flex-wrap:wrap}}
.map-tab{{padding:10px 22px;border-radius:50px;border:1px solid var(--bdr);
  background:var(--card);color:var(--t2);font-size:.85rem;font-weight:500;
  cursor:pointer;transition:all .25s}}
.map-tab:hover{{background:var(--card-h);border-color:var(--bdr-h);color:var(--t1)}}
.map-tab.active{{background:rgba(99,102,241,.15);
  border-color:rgba(99,102,241,.3);color:#a5b4fc}}
.map-box{{border-radius:var(--rad);border:1px solid var(--bdr);
  overflow:hidden;background:var(--card);height:550px;position:relative}}
.map-frame{{width:100%;height:100%;border:none;position:absolute;top:0;left:0}}

/* ════════ DASHBOARD EMBED ════════ */
.dash-wrap{{border-radius:var(--rad);border:1px solid var(--bdr);
  overflow:hidden;background:var(--card);position:relative}}
.dash-frame{{width:100%;height:700px;border:none}}
.ext-link{{position:absolute;top:16px;right:16px;padding:8px 18px;
  border-radius:50px;background:rgba(99,102,241,.15);
  border:1px solid rgba(99,102,241,.3);color:#a5b4fc;text-decoration:none;
  font-size:.8rem;font-weight:500;transition:all .2s;
  backdrop-filter:blur(10px);z-index:10}}
.ext-link:hover{{background:rgba(99,102,241,.25)}}

/* ════════ REPORT ════════ */
.report-box{{background:var(--card);border:1px solid var(--bdr);
  border-radius:var(--rad);padding:40px;max-height:600px;overflow-y:auto}}
.report-box pre{{white-space:pre-wrap;word-wrap:break-word;
  font-family:'SF Mono','Fira Code',Consolas,monospace;
  font-size:.85rem;color:var(--t2);line-height:1.8}}
.report-box::-webkit-scrollbar{{width:6px}}
.report-box::-webkit-scrollbar-track{{background:transparent}}
.report-box::-webkit-scrollbar-thumb{{background:rgba(255,255,255,.1);border-radius:3px}}

/* ════════ DATA FILES ════════ */
.data-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}}
.data-card{{display:flex;align-items:center;gap:16px;padding:20px 24px;
  background:var(--card);border:1px solid var(--bdr);border-radius:var(--rads);
  text-decoration:none;transition:all .25s}}
.data-card:hover{{background:var(--card-h);border-color:var(--bdr-h);
  transform:translateX(4px)}}
.file-icon{{font-size:1.8rem}}
.file-info{{flex:1}}
.file-name{{font-weight:600;font-size:.9rem;color:var(--t1)}}
.file-type{{font-size:.75rem;color:var(--t3);margin-top:2px}}
.dl-icon{{font-size:1.1rem;color:var(--t3);transition:color .2s}}
.data-card:hover .dl-icon{{color:var(--a3)}}

/* ════════ ANIMATIONS ════════ */
.animate-in{{opacity:0;transform:translateY(20px);
  animation:fadeIn .6s ease forwards}}
@keyframes fadeIn{{to{{opacity:1;transform:translateY(0)}}}}
.reveal{{opacity:0;transform:translateY(30px);
  transition:all .7s cubic-bezier(.4,0,.2,1)}}
.reveal.vis{{opacity:1;transform:translateY(0)}}

/* ════════ FOOTER ════════ */
.footer{{text-align:center;padding:40px 0;border-top:1px solid var(--bdr);
  color:var(--t3);font-size:.78rem}}

/* ════════ SCROLLBAR ════════ */
::-webkit-scrollbar{{width:8px}}
::-webkit-scrollbar-track{{background:var(--bg0)}}
::-webkit-scrollbar-thumb{{background:rgba(255,255,255,.08);border-radius:4px}}
::-webkit-scrollbar-thumb:hover{{background:rgba(255,255,255,.14)}}

/* ════════ RESPONSIVE ════════ */
.menu-btn{{display:none;position:fixed;top:16px;left:16px;z-index:200;
  width:44px;height:44px;border-radius:12px;border:1px solid var(--bdr);
  background:var(--bg1);color:var(--t1);font-size:1.3rem;cursor:pointer;
  align-items:center;justify-content:center;transition:all .2s}}
@media(max-width:900px){{
  .sidebar{{transform:translateX(-100%)}}
  .sidebar.open{{transform:translateX(0)}}
  .main{{margin-left:0}}
  .content{{padding:24px 20px 60px}}
  .hero h1{{font-size:1.8rem}}
  .chart-grid{{grid-template-columns:1fr}}
  .stats{{grid-template-columns:repeat(2,1fr)}}
  .menu-btn{{display:flex}}
}}
</style>
</head>
<body>

<!-- ═══ LOADING SCREEN ═══ -->
<div id="loader">
  <div class="particles">{particles}</div>
  <div class="ld-logo">Smart Analytics</div>
  <div class="ld-sub">Food Delivery Platform</div>
  <div class="prog-wrap"><div class="prog-bar" id="pbar"></div></div>
  <div class="ld-stat" id="pstat">Initializing modules…</div>
</div>

<!-- ═══ MOBILE MENU ═══ -->
<button class="menu-btn" id="menubtn" onclick="toggleSidebar()">☰</button>

<!-- ═══ SIDEBAR ═══ -->
<nav class="sidebar" id="sidebar">
  <div class="sb-brand">
    <h1>Smart Food Delivery<br>Analytics</h1>
    <span>Intelligence Platform</span>
  </div>
  <div class="sb-nav">
    <a class="nav-item active" onclick="goTo('sec-overview')">
      <span class="ni">◉</span> Overview</a>
    <a class="nav-item" onclick="goTo('sec-charts')">
      <span class="ni">◫</span> Charts</a>
    <a class="nav-item" onclick="goTo('sec-maps')">
      <span class="ni">◎</span> Geospatial</a>
    {dash_nav}
    <a class="nav-item" onclick="goTo('sec-report')">
      <span class="ni">☰</span> Report</a>
    <a class="nav-item" onclick="goTo('sec-data')">
      <span class="ni">⬡</span> Data Files</a>
  </div>
  <div class="sb-foot">
    <p>Generated by Smart Food<br>Delivery Analytics Pipeline</p>
  </div>
</nav>

<!-- ═══ MAIN ═══ -->
<div class="main">
  <div class="bg-grid"></div>
  <div class="glow g1"></div>
  <div class="glow g2"></div>
  <div class="content">

    <!-- HERO -->
    <div class="hero reveal" id="sec-overview">
      <h1>Analytics Overview</h1>
      <p>Comprehensive insights from your food delivery data pipeline</p>
      <div class="hero-bar"></div>
    </div>

    <!-- STATS -->
    <div class="stats">
      <div class="sc reveal"><div class="sn">{n_charts}</div>
        <div class="sl">Visualizations</div></div>
      <div class="sc reveal"><div class="sn">{n_maps}</div>
        <div class="sl">Geospatial Maps</div></div>
      <div class="sc reveal"><div class="sn">{n_data}</div>
        <div class="sl">Data Exports</div></div>
      <div class="sc reveal"><div class="sn">{n_total}</div>
        <div class="sl">Total Artifacts</div></div>
    </div>

    <!-- CHARTS -->
    <div class="section reveal" id="sec-charts">
      <div class="sh"><h2>Statistical Charts</h2>
        <p class="ss">Click any chart to expand</p></div>
      <div class="chart-grid">{charts_body}</div>
    </div>

    <!-- MAPS -->
    <div class="section reveal" id="sec-maps">
      <div class="sh"><h2>Geospatial Analysis</h2>
        <p class="ss">Interactive map visualizations</p></div>
      {maps_body}
    </div>

    <!-- DASHBOARD -->
    {dash_section}

    <!-- REPORT -->
    <div class="section reveal" id="sec-report">
      <div class="sh"><h2>Final Report</h2>
        <p class="ss">Generated analysis summary</p></div>
      <div class="report-box"><pre>{report_html}</pre></div>
    </div>

    <!-- DATA -->
    <div class="section reveal" id="sec-data">
      <div class="sh"><h2>Data Exports</h2>
        <p class="ss">Download processed datasets</p></div>
      <div class="data-grid">{data_body}</div>
    </div>

    <div class="footer">
      Smart Food Delivery Analytics Platform &middot; Python &amp; PySpark
    </div>
  </div>
</div>

<!-- ═══ LIGHTBOX ═══ -->
<div class="lb" id="lb" onclick="closeLB()">
  <span class="lb-x" onclick="closeLB()">&times;</span>
  <img id="lb-img" src="" alt="">
  <div class="lb-title" id="lb-title"></div>
</div>

<script>
/* ── LOADER ────────────────────────────────── */
const steps=["Initializing modules…","Loading chart assets…",
  "Preparing map layers…","Rendering components…","Finalizing layout…","Ready"];
let si=0;const bar=document.getElementById('pbar'),
  stat=document.getElementById('pstat'),scr=document.getElementById('loader');
function tick(){{if(si<steps.length){{
  bar.style.width=((si+1)/steps.length*100)+'%';stat.textContent=steps[si];
  si++;setTimeout(tick,350+Math.random()*250)}}
  else setTimeout(()=>scr.classList.add('done'),400)}}
setTimeout(tick,300);

/* ── SCROLL REVEAL ─────────────────────────── */
const obs=new IntersectionObserver(e=>{{
  e.forEach(x=>{{if(x.isIntersecting)x.target.classList.add('vis')}})
}},{{threshold:.08,rootMargin:'0px 0px -40px 0px'}});
document.querySelectorAll('.reveal').forEach(e=>obs.observe(e));

/* ── NAV ───────────────────────────────────── */
function goTo(id){{
  document.getElementById(id)?.scrollIntoView({{behavior:'smooth'}});
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  event.currentTarget.classList.add('active');
  document.getElementById('sidebar').classList.remove('open');
}}
const secs=document.querySelectorAll('.section,.hero');
const navs=document.querySelectorAll('.nav-item');
window.addEventListener('scroll',()=>{{
  let cur='';secs.forEach(s=>{{if(s.getBoundingClientRect().top<200)cur=s.id}});
  navs.forEach(n=>{{n.classList.remove('active');
    if(n.getAttribute('onclick')?.includes(cur))n.classList.add('active')}});
}});

/* ── MOBILE SIDEBAR ────────────────────────── */
function toggleSidebar(){{
  document.getElementById('sidebar').classList.toggle('open')}}

/* ── LIGHTBOX ──────────────────────────────── */
function openLightbox(s,t){{const lb=document.getElementById('lb');
  document.getElementById('lb-img').src=s;
  document.getElementById('lb-title').textContent=t;
  lb.classList.add('on');document.body.style.overflow='hidden'}}
function closeLB(){{document.getElementById('lb').classList.remove('on');
  document.body.style.overflow=''}}
document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeLB()}});

/* ── MAP TABS ──────────────────────────────── */
function switchMap(i,btn){{
  document.querySelectorAll('.map-frame').forEach(f=>f.style.display='none');
  document.querySelectorAll('.map-tab').forEach(t=>t.classList.remove('active'));
  const fr=document.getElementById('map-'+i);
  if(fr)fr.style.display='block';if(btn)btn.classList.add('active')}}
</script>
</body>
</html>'''

    return html


def main():
    print("Building analytics viewer...")
    html = build_viewer()
    os.makedirs("output", exist_ok=True)
    with open("output/viewer.html", "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = os.path.getsize("output/viewer.html") / 1024
    print(f"  ✓ Viewer generated: output/viewer.html ({size_kb:.1f} KB)")
    print("  Open in a browser to explore all analytics outputs.")


if __name__ == "__main__":
    main()