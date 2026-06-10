"""
Example 8 - Local market graph viewer.

Run:
    python examples/08_market_graph_viewer.py

Then open:
    http://127.0.0.1:8000
"""
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists():
    sys.path.insert(0, str(SRC))

from kolmo_stats.graph import market_graph_json  # noqa: E402


HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kolmo Market Graph</title>
  <script src="https://cdn.jsdelivr.net/npm/cytoscape@3/dist/cytoscape.min.js"></script>
  <style>
    :root {
      color-scheme: dark;
      --bg: #0d1117;
      --panel: #151b23;
      --panel-2: #1c2430;
      --text: #f0f6fc;
      --muted: #9ba7b4;
      --line: #303b49;
      --accent: #58a6ff;
      --danger: #ff7b72;
      --good: #7ee787;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      min-height: 100vh;
      overflow: hidden;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--text);
    }

    .app {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 380px;
      grid-template-rows: auto minmax(0, 1fr);
      height: 100vh;
    }

    header {
      grid-column: 1 / -1;
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      border-bottom: 1px solid var(--line);
      background: #10161f;
    }

    h1 {
      margin: 0;
      font-size: 17px;
      line-height: 1.2;
      font-weight: 700;
      white-space: nowrap;
    }

    .toolbar {
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 9px;
      min-width: 0;
      flex: 1;
    }

    input,
    select,
    button {
      height: 36px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel);
      color: var(--text);
      font: inherit;
      font-size: 13px;
    }

    input[type="search"] {
      width: min(30vw, 320px);
      min-width: 190px;
      padding: 0 11px;
    }

    select {
      width: 142px;
      padding: 0 9px;
    }

    button {
      min-width: 76px;
      padding: 0 10px;
      cursor: pointer;
    }

    button:hover,
    input:focus,
    select:focus {
      outline: 1px solid var(--accent);
      border-color: var(--accent);
    }

    .strength {
      display: grid;
      grid-template-columns: auto 112px;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
    }

    input[type="range"] {
      width: 112px;
      accent-color: var(--accent);
      border: 0;
      background: transparent;
    }

    main {
      position: relative;
      min-width: 0;
      min-height: 0;
      background: var(--bg);
    }

    #cy {
      width: 100%;
      height: 100%;
    }

    aside {
      min-width: 0;
      min-height: 0;
      overflow: auto;
      border-left: 1px solid var(--line);
      background: var(--panel);
    }

    .stats {
      position: absolute;
      left: 14px;
      bottom: 14px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      max-width: calc(100% - 28px);
      pointer-events: none;
      z-index: 4;
    }

    .pill {
      min-height: 28px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 9px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: rgba(21, 27, 35, 0.9);
      color: var(--muted);
      font-size: 12px;
    }

    .pill b {
      color: var(--text);
      font-weight: 650;
    }

    .panel {
      padding: 16px;
    }

    .eyebrow {
      margin: 0 0 6px;
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    h2 {
      margin: 0 0 8px;
      font-size: 22px;
      line-height: 1.15;
    }

    .description {
      margin: 0 0 14px;
      color: #d2dbe6;
      font-size: 14px;
      line-height: 1.45;
    }

    .section {
      padding: 14px 0;
      border-top: 1px solid var(--line);
    }

    h3 {
      margin: 0 0 10px;
      font-size: 13px;
      color: var(--muted);
      font-weight: 650;
    }

    .meta {
      display: grid;
      grid-template-columns: 96px minmax(0, 1fr);
      gap: 8px 10px;
      font-size: 13px;
    }

    .meta span:nth-child(odd) {
      color: var(--muted);
    }

    .chips {
      display: flex;
      gap: 7px;
      flex-wrap: wrap;
    }

    .chip {
      max-width: 100%;
      padding: 5px 8px;
      border-radius: 6px;
      background: var(--panel-2);
      color: #dbe6f2;
      font-size: 12px;
      line-height: 1.2;
      overflow-wrap: anywhere;
    }

    .edge-list {
      display: grid;
      gap: 8px;
    }

    .edge-item {
      padding: 9px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--panel-2);
      cursor: pointer;
    }

    .edge-item:hover {
      border-color: var(--accent);
    }

    .edge-title {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      color: var(--text);
      font-size: 13px;
      line-height: 1.3;
    }

    .edge-note {
      margin-top: 5px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }

    .legend {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px;
    }

    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #dbe6f2;
      font-size: 12px;
    }

    .swatch {
      width: 12px;
      height: 12px;
      border-radius: 3px;
      flex: 0 0 auto;
    }

    .empty {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
    }

    .notice {
      position: absolute;
      inset: 16px;
      display: grid;
      place-items: center;
      padding: 24px;
      text-align: center;
      color: var(--muted);
    }

    @media (max-width: 980px) {
      body { overflow: auto; }

      .app {
        grid-template-columns: 1fr;
        grid-template-rows: auto 68vh auto;
        min-height: 100vh;
        height: auto;
      }

      header {
        align-items: stretch;
        flex-direction: column;
      }

      .toolbar {
        justify-content: flex-start;
        flex-wrap: wrap;
      }

      input[type="search"],
      select,
      button {
        flex: 1 1 180px;
      }

      aside {
        border-left: 0;
        border-top: 1px solid var(--line);
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <header>
      <h1>Kolmo Market Graph</h1>
      <div class="toolbar">
        <input id="search" type="search" placeholder="Search Brent, diesel crack, TTF">
        <select id="cluster"></select>
        <select id="layout">
          <option value="market">Market map</option>
          <option value="concentric">Concentric</option>
          <option value="breadthfirst">Breadthfirst</option>
          <option value="cose">Force</option>
        </select>
        <label class="strength">
          <span id="strengthLabel">Edges >= 0.75</span>
          <input id="strength" type="range" min="0.40" max="0.90" step="0.05" value="0.75">
        </label>
        <button id="reset" type="button">Reset</button>
      </div>
    </header>
    <main>
      <div id="cy"></div>
      <div class="stats" id="stats"></div>
    </main>
    <aside>
      <div class="panel" id="details"></div>
    </aside>
  </div>

  <script>
    const cyEl = document.getElementById("cy");
    const details = document.getElementById("details");
    const statsEl = document.getElementById("stats");
    const searchEl = document.getElementById("search");
    const clusterEl = document.getElementById("cluster");
    const layoutEl = document.getElementById("layout");
    const strengthEl = document.getElementById("strength");
    const strengthLabel = document.getElementById("strengthLabel");
    const resetEl = document.getElementById("reset");

    const CLUSTER_ORDER = ["macro", "geo", "balance", "crude", "product", "energy"];
    const STRONG_ROOTS = ["brent", "wti", "diesel_crack", "gasoline_crack", "ttf_gas"];

    const state = {
      data: null,
      cy: null,
      selected: null,
      selectedType: null,
      minWeight: 0.75,
      cluster: "all",
      query: ""
    };

    const escapeHtml = (value) => String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");

    const nodeText = (node) => [
      node.data("id"),
      node.data("label"),
      node.data("description"),
      ...(node.data("aliases") || []),
      ...(node.data("related_formulas") || [])
    ].join(" ").toLowerCase();

    function nodeSize(tier) {
      if (tier === 1) return 36;
      if (tier === 2) return 28;
      return 22;
    }

    function edgeColor(sign) {
      return sign > 0 ? "#7ee787" : "#ff7b72";
    }

    function buildElements(data) {
      const nodes = data.nodes.map((node) => ({
        data: {
          ...node,
          color: data.clusters[node.cluster]?.color || node.color || "#58a6ff",
          size: nodeSize(node.tier)
        },
        position: marketPosition(node, data.nodes)
      }));
      const edges = data.edges.map((edge) => ({
        data: {
          ...edge,
          color: edgeColor(edge.sign),
          width: 1.2 + edge.weight * 3.4
        },
        classes: edge.sign > 0 ? "positive" : "negative"
      }));
      return [...nodes, ...edges];
    }

    function marketPosition(node, allNodes) {
      const width = Math.max(760, cyEl.clientWidth || 760);
      const height = Math.max(620, cyEl.clientHeight || 620);
      const clusterIndex = Math.max(0, CLUSTER_ORDER.indexOf(node.cluster));
      const columns = CLUSTER_ORDER.length;
      const laneWidth = width / columns;
      const laneNodes = allNodes
        .filter((candidate) => candidate.cluster === node.cluster)
        .sort((a, b) => a.tier - b.tier || a.label.localeCompare(b.label));
      const row = Math.max(0, laneNodes.findIndex((candidate) => candidate.id === node.id));
      const laneCount = Math.max(1, laneNodes.length);
      const x = laneWidth * clusterIndex + laneWidth / 2;
      const top = 88;
      const usableHeight = Math.max(320, height - 160);
      const y = top + (usableHeight * (row + 1)) / (laneCount + 1);
      return { x, y };
    }

    function initGraph(data) {
      state.cy = cytoscape({
        container: cyEl,
        elements: buildElements(data),
        minZoom: 0.25,
        maxZoom: 2.5,
        wheelSensitivity: 0.16,
        style: [
          {
            selector: "node",
            style: {
              "background-color": "data(color)",
              "border-color": "#f0f6fc",
              "border-width": 2,
              "color": "#f0f6fc",
              "content": "data(label)",
              "font-size": 11,
              "height": "data(size)",
              "label": "data(label)",
              "min-zoomed-font-size": 8,
              "overlay-opacity": 0,
              "shape": "ellipse",
              "text-background-color": "#0d1117",
              "text-background-opacity": 0.76,
              "text-background-padding": 2,
              "text-margin-y": -5,
              "text-outline-color": "#0d1117",
              "text-outline-width": 2,
              "text-valign": "top",
              "width": "data(size)",
              "z-index": 3
            }
          },
          {
            selector: "node[tier = 1]",
            style: {
              "border-width": 3,
              "font-size": 12,
              "text-background-opacity": 0.86,
              "z-index": 5
            }
          },
          {
            selector: "edge",
            style: {
              "curve-style": "bezier",
              "line-color": "data(color)",
              "line-opacity": 0.42,
              "target-arrow-color": "data(color)",
              "target-arrow-shape": "triangle",
              "target-arrow-fill": "filled",
              "width": "data(width)",
              "z-index": 1
            }
          },
          {
            selector: "edge.negative",
            style: {
              "line-style": "dashed",
              "line-dash-pattern": [8, 6]
            }
          },
          {
            selector: ".hidden-edge",
            style: { "display": "none" }
          },
          {
            selector: ".dim",
            style: {
              "opacity": 0.13,
              "text-opacity": 0.06
            }
          },
          {
            selector: "edge.dim",
            style: { "line-opacity": 0.05 }
          },
          {
            selector: ".search-match",
            style: {
              "border-color": "#ffffff",
              "border-width": 4,
              "z-index": 9
            }
          },
          {
            selector: ".selected",
            style: {
              "border-color": "#ffffff",
              "border-width": 5,
              "text-background-opacity": 0.95,
              "z-index": 10
            }
          },
          {
            selector: "edge.selected",
            style: {
              "line-opacity": 0.95,
              "width": 5,
              "z-index": 8
            }
          }
        ],
        layout: { name: "preset", fit: true, padding: 48 }
      });

      state.cy.on("tap", "node", (event) => selectNode(event.target));
      state.cy.on("tap", "edge", (event) => selectEdge(event.target));
      state.cy.on("tap", (event) => {
        if (event.target === state.cy) {
          clearSelection();
        }
      });
      state.cy.ready(() => {
        state.cy.fit(undefined, 48);
        state.cy.center();
      });
    }

    function runLayout(name) {
      if (!state.cy) return;
      if (name === "market") {
        state.cy.nodes().forEach((node) => {
          const raw = state.data.nodes.find((candidate) => candidate.id === node.id());
          node.position(marketPosition(raw, state.data.nodes));
        });
        state.cy.fit(undefined, 48);
        applyFilters();
        return;
      }

      const common = { fit: true, padding: 54, animate: true, animationDuration: 450 };
      const options = {
        concentric: {
          ...common,
          name: "concentric",
          concentric: (node) => 4 - Number(node.data("tier") || 3),
          levelWidth: () => 1,
          minNodeSpacing: 42
        },
        breadthfirst: {
          ...common,
          name: "breadthfirst",
          directed: true,
          roots: STRONG_ROOTS.filter((id) => state.cy.getElementById(id).length > 0),
          spacingFactor: 1.35
        },
        cose: {
          ...common,
          name: "cose",
          nodeRepulsion: 90000,
          idealEdgeLength: 110,
          edgeElasticity: 0.24,
          gravity: 0.35,
          numIter: 1200
        }
      }[name];
      state.cy.layout(options || { ...common, name: "preset" }).run();
      applyFilters();
    }

    function applyFilters() {
      if (!state.cy) return;
      const cy = state.cy;
      cy.elements().removeClass("dim search-match selected hidden-edge");

      cy.edges().forEach((edge) => {
        if (Number(edge.data("weight")) < state.minWeight) {
          edge.addClass("hidden-edge");
        }
      });

      if (state.cluster !== "all") {
        cy.nodes().forEach((node) => {
          if (node.data("cluster") !== state.cluster) node.addClass("dim");
        });
        cy.edges().forEach((edge) => {
          if (
            edge.source().data("cluster") !== state.cluster &&
            edge.target().data("cluster") !== state.cluster
          ) {
            edge.addClass("dim");
          }
        });
      }

      if (state.query) {
        const matches = cy.nodes().filter((node) => nodeText(node).includes(state.query));
        matches.addClass("search-match");
        cy.nodes().not(matches).addClass("dim");
        cy.edges().not(matches.connectedEdges()).addClass("dim");
      }

      if (state.selected) {
        state.selected.addClass("selected");
        const keep = state.selectedType === "node"
          ? state.selected.closedNeighborhood()
          : state.selected.union(state.selected.connectedNodes());
        cy.elements().not(keep).addClass("dim");
        keep.removeClass("dim");
      }
    }

    function selectNode(node) {
      state.selected = node;
      state.selectedType = "node";
      renderNodeDetails(node);
      applyFilters();
      state.cy.animate({ fit: { eles: node.closedNeighborhood(), padding: 80 } }, { duration: 280 });
    }

    function selectEdge(edge) {
      state.selected = edge;
      state.selectedType = "edge";
      renderEdgeDetails(edge);
      applyFilters();
      state.cy.animate({ fit: { eles: edge.union(edge.connectedNodes()), padding: 96 } }, { duration: 280 });
    }

    function clearSelection() {
      state.selected = null;
      state.selectedType = null;
      renderOverview();
      applyFilters();
    }

    function edgeContext(edge) {
      return {
        id: edge.id(),
        source_label: edge.data("source_label"),
        target_label: edge.data("target_label"),
        label: edge.data("label"),
        rationale: edge.data("rationale"),
        sign: edge.data("sign"),
        weight: edge.data("weight")
      };
    }

    function renderStats() {
      const health = state.data.health || {};
      statsEl.innerHTML = [
        ["Nodes", health.node_count ?? state.data.nodes.length],
        ["Edges", health.edge_count ?? state.data.edges.length],
        ["Visible edges", state.cy ? state.cy.edges().not(".hidden-edge").length : state.data.edges.length],
        ["Isolated", (health.isolated_nodes || []).length],
        ["Version", state.data.version]
      ].map(([label, value]) => `<span class="pill">${escapeHtml(label)} <b>${escapeHtml(value)}</b></span>`).join("");
    }

    function renderOverview() {
      details.innerHTML = `
        <p class="eyebrow">Graph</p>
        <h2>Energy Market Map</h2>
        <p class="description">A structured view of market variables and directional relationships. The default layout groups nodes by cluster and filters weaker edges so the graph starts readable.</p>
        ${legendHtml()}
        <div class="section">
          <h3>How to read it</h3>
          <div class="meta">
            <span>Green edges</span><span>Same-direction relationship</span>
            <span>Red dashed</span><span>Opposite-direction relationship</span>
            <span>Node size</span><span>Tier 1 nodes are larger</span>
            <span>Click</span><span>Focus a node or edge and inspect rationale</span>
          </div>
        </div>
      `;
    }

    function renderNodeDetails(node) {
      const incoming = node.incomers("edge").sort((a, b) => b.data("weight") - a.data("weight"));
      const outgoing = node.outgoers("edge").sort((a, b) => b.data("weight") - a.data("weight"));
      details.innerHTML = `
        <p class="eyebrow">${escapeHtml(node.data("cluster"))} node</p>
        <h2>${escapeHtml(node.data("label"))}</h2>
        <p class="description">${escapeHtml(node.data("description"))}</p>
        <div class="section">
          <div class="meta">
            <span>ID</span><span>${escapeHtml(node.id())}</span>
            <span>Tier</span><span>${escapeHtml(node.data("tier"))}</span>
            <span>Unit</span><span>${escapeHtml(node.data("unit"))}</span>
            <span>Value</span><span>${escapeHtml(node.data("value"))}</span>
          </div>
        </div>
        ${chipsSection("Aliases", node.data("aliases"))}
        ${chipsSection("Related formulas", node.data("related_formulas"))}
        <div class="section">
          <h3>Strategy hint</h3>
          <p class="description">${escapeHtml(node.data("strategy_hint") || "No strategy hint yet.")}</p>
        </div>
        ${edgeList("Drivers", incoming.map(edgeContext))}
        ${edgeList("Outputs", outgoing.map(edgeContext))}
      `;
    }

    function renderEdgeDetails(edge) {
      details.innerHTML = `
        <p class="eyebrow">Relationship</p>
        <h2>${escapeHtml(edge.data("source_label"))} -> ${escapeHtml(edge.data("target_label"))}</h2>
        <p class="description">${escapeHtml(edge.data("rationale") || edge.data("label"))}</p>
        <div class="section">
          <div class="meta">
            <span>Label</span><span>${escapeHtml(edge.data("label"))}</span>
            <span>Direction</span><span>${edge.data("sign") > 0 ? "Same direction" : "Opposite direction"}</span>
            <span>Strength</span><span>${escapeHtml(edge.data("weight"))}</span>
          </div>
        </div>
      `;
    }

    function legendHtml() {
      const items = Object.entries(state.data.clusters || {}).map(([id, attrs]) => `
        <div class="legend-item">
          <span class="swatch" style="background:${escapeHtml(attrs.color || "#58a6ff")}"></span>
          <span>${escapeHtml(attrs.label || id)}</span>
        </div>
      `).join("");
      return `<div class="section"><h3>Clusters</h3><div class="legend">${items}</div></div>`;
    }

    function chipsSection(title, values) {
      if (!values || values.length === 0) return "";
      return `
        <div class="section">
          <h3>${escapeHtml(title)}</h3>
          <div class="chips">${values.map((value) => `<span class="chip">${escapeHtml(value)}</span>`).join("")}</div>
        </div>
      `;
    }

    function edgeList(title, edges) {
      if (!edges.length) {
        return `<div class="section"><h3>${escapeHtml(title)}</h3><p class="empty">None</p></div>`;
      }
      return `
        <div class="section">
          <h3>${escapeHtml(title)}</h3>
          <div class="edge-list">
            ${edges.map((edge) => `
              <div class="edge-item" data-edge-id="${escapeHtml(edge.id)}">
                <div class="edge-title">
                  <span>${escapeHtml(edge.source_label)} -> ${escapeHtml(edge.target_label)}</span>
                  <span>${edge.sign > 0 ? "+" : "-"}${escapeHtml(edge.weight)}</span>
                </div>
                <div class="edge-note">${escapeHtml(edge.rationale || edge.label)}</div>
              </div>
            `).join("")}
          </div>
        </div>
      `;
    }

    function buildControls() {
      clusterEl.innerHTML = `<option value="all">All clusters</option>` + CLUSTER_ORDER
        .filter((id) => state.data.clusters[id])
        .map((id) => `<option value="${escapeHtml(id)}">${escapeHtml(state.data.clusters[id].label || id)}</option>`)
        .join("");
    }

    function bindControls() {
      searchEl.addEventListener("input", () => {
        state.query = searchEl.value.trim().toLowerCase();
        applyFilters();
      });
      clusterEl.addEventListener("change", () => {
        state.cluster = clusterEl.value;
        applyFilters();
      });
      layoutEl.addEventListener("change", () => runLayout(layoutEl.value));
      strengthEl.addEventListener("input", () => {
        state.minWeight = Number(strengthEl.value);
        strengthLabel.textContent = `Edges >= ${state.minWeight.toFixed(2)}`;
        applyFilters();
        renderStats();
      });
      resetEl.addEventListener("click", () => {
        searchEl.value = "";
        clusterEl.value = "all";
        layoutEl.value = "market";
        strengthEl.value = "0.75";
        strengthLabel.textContent = "Edges >= 0.75";
        state.query = "";
        state.cluster = "all";
        state.minWeight = 0.75;
        clearSelection();
        runLayout("market");
      });
      details.addEventListener("click", (event) => {
        const item = event.target.closest?.("[data-edge-id]");
        if (!item || !state.cy) return;
        const edge = state.cy.getElementById(item.dataset.edgeId);
        if (edge.length) selectEdge(edge);
      });
      window.addEventListener("resize", () => {
        if (layoutEl.value === "market") runLayout("market");
      });
    }

    async function boot() {
      if (!window.cytoscape) {
        cyEl.innerHTML = `<div class="notice">Cytoscape.js could not be loaded. Check your internet connection or vendor the library locally.</div>`;
        return;
      }

      const response = await fetch("/graph.json");
      state.data = await response.json();
      buildControls();
      initGraph(state.data);
      bindControls();
      renderOverview();
      applyFilters();
      renderStats();
    }

    boot().catch((error) => {
      details.innerHTML = `<p class="eyebrow">Error</p><h2>Graph failed to load</h2><p class="description">${escapeHtml(error.message)}</p>`;
      console.error(error);
    });
  </script>
</body>
</html>
"""


class GraphViewerHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            self._send_text(HTML, "text/html; charset=utf-8")
            return
        if path == "/graph.json":
            payload = json.dumps(market_graph_json(), indent=2).encode("utf-8")
            self._send_bytes(payload, "application/json; charset=utf-8")
            return
        if path == "/health":
            payload = json.dumps(market_graph_json()["health"], indent=2).encode("utf-8")
            self._send_bytes(payload, "application/json; charset=utf-8")
            return
        self.send_error(404, "Not found")

    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write(f"[market-graph-viewer] {format % args}\n")

    def _send_text(self, body: str, content_type: str) -> None:
        self._send_bytes(body.encode("utf-8"), content_type)

    def _send_bytes(self, body: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the Kolmo market graph viewer.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind. Default: 127.0.0.1")
    parser.add_argument("--port", default=8000, type=int, help="Port to bind. Default: 8000")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), GraphViewerHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"Market graph viewer running at {url}", flush=True)
    print("Press Ctrl-C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping market graph viewer.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
