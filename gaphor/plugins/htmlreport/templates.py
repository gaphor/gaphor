"""HTML, CSS, and JavaScript templates for the HTML model report."""

from pathlib import Path

VENDOR_SVG_PAN_ZOOM_PATH = Path(__file__).parent / "vendor_svg_pan_zoom.js"

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gaphor Model Report</title>
<style>
{css}
</style>
</head>
<body>
<div id="sidebar">
  <div id="sidebar-header">
    <h2>Model Browser</h2>
    <input type="text" id="search" placeholder="Search..." autocomplete="off">
  </div>
  <div id="tree-container"></div>
</div>
<div id="main">
  <div id="welcome-view">
    <h1>Model Report</h1>
    <p>Select a diagram or element from the sidebar, or choose a diagram below.</p>
    <div id="diagram-list"></div>
  </div>
  <div id="diagram-view" style="display:none;">
    <div id="diagram-header"><h2 id="diagram-title"></h2></div>
    <div id="diagram-content"></div>
  </div>
  <div id="element-view" style="display:none;">
    <h2 id="element-title"></h2>
    <div id="element-type"></div>
    <div id="element-details"></div>
    <div id="element-diagrams"></div>
  </div>
  <div id="element-panel" class="panel-hidden">
    <div id="panel-header">
      <h3 id="panel-title"></h3>
      <span id="panel-type"></span>
      <button id="panel-close" title="Close">&times;</button>
    </div>
    <div id="panel-body"></div>
  </div>
</div>
<script src="assets/svg-pan-zoom.min.js"></script>
<script>
var MODEL_DATA = {model_data};
{js}
</script>
</body>
</html>
"""

CSS_TEMPLATE = """\
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; display: flex; height: 100vh; overflow: hidden; color: #333; }
#sidebar { width: 300px; min-width: 200px; background: #f5f5f5; border-right: 1px solid #ddd; display: flex; flex-direction: column; overflow: hidden; }
#sidebar-header { padding: 12px; border-bottom: 1px solid #ddd; }
#sidebar-header h2 { font-size: 14px; margin-bottom: 8px; color: #555; }
#search { width: 100%; padding: 6px 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; }
#tree-container { flex: 1; overflow-y: auto; padding: 8px 0; }
#main { flex: 1; overflow-y: auto; padding: 24px; }
#welcome-view h1 { margin-bottom: 12px; }
#welcome-view p { color: #666; margin-bottom: 20px; }
.diagram-card { display: inline-block; padding: 10px 16px; margin: 4px; border: 1px solid #ddd; border-radius: 6px; cursor: pointer; text-decoration: none; color: #333; background: #fff; }
.diagram-card:hover { background: #e8f0fe; border-color: #4285f4; }
.tree-list { list-style: none; padding-left: 16px; }
.tree-list.root { padding-left: 4px; }
.tree-node { cursor: pointer; padding: 3px 8px; font-size: 13px; border-radius: 3px; white-space: nowrap; display: flex; align-items: center; }
.tree-node:hover { background: #e0e0e0; }
.tree-node.active { background: #d2e3fc; }
.tree-toggle { display: inline-block; width: 16px; text-align: center; font-size: 10px; color: #888; flex-shrink: 0; }
.tree-label { margin-left: 4px; overflow: hidden; text-overflow: ellipsis; }
.tree-children { display: none; }
.tree-children.open { display: block; }
.tree-group { font-style: italic; color: #888; }
.hidden { display: none !important; }
#diagram-header { margin-bottom: 16px; }
#diagram-header h2 { font-size: 18px; }
#diagram-content { overflow: hidden; background: #fafafa; border: 1px solid #eee; border-radius: 4px; position: relative; height: calc(100vh - 120px); }
#diagram-content svg { width: 100%; height: 100%; }
.zoom-controls { position: absolute; top: 10px; right: 10px; display: flex; flex-direction: column; gap: 4px; z-index: 10; }
.zoom-controls button { width: 32px; height: 32px; border: 1px solid #ccc; border-radius: 4px; background: #fff; cursor: pointer; font-size: 16px; display: flex; align-items: center; justify-content: center; color: #555; }
.zoom-controls button:hover { background: #e8f0fe; border-color: #4285f4; }
#element-view h2 { margin-bottom: 4px; }
#element-type { color: #888; font-size: 13px; margin-bottom: 16px; }
#element-details { margin-bottom: 20px; }
.props-table { border-collapse: collapse; width: 100%; max-width: 600px; }
.props-table th, .props-table td { text-align: left; padding: 6px 12px; border-bottom: 1px solid #eee; font-size: 13px; }
.props-table th { color: #666; width: 160px; }
#element-diagrams h3 { font-size: 14px; margin-bottom: 8px; }
#element-diagrams a { display: inline-block; margin: 2px 6px; color: #4285f4; text-decoration: none; }
#element-diagrams a:hover { text-decoration: underline; }
.element-section { margin-bottom: 16px; }
.element-section h3 { font-size: 14px; color: #555; margin-bottom: 6px; border-bottom: 1px solid #eee; padding-bottom: 4px; }
.element-section ul { list-style: none; padding: 0; }
.element-section li { padding: 3px 0; font-size: 13px; }
.element-section code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 12px; background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
.stereotype-tag { display: inline-block; background: #e8f0fe; color: #1a73e8; font-size: 12px; padding: 2px 8px; border-radius: 10px; margin: 2px 4px 2px 0; }
.element-section a { color: #4285f4; text-decoration: none; }
.element-section a:hover { text-decoration: underline; }
.assoc-table { border-collapse: collapse; width: 100%; max-width: 700px; }
.assoc-table th, .assoc-table td { text-align: left; padding: 6px 12px; border-bottom: 1px solid #eee; font-size: 13px; }
.assoc-table th { color: #666; font-weight: 600; }
#main { position: relative; }
#element-panel { position: absolute; bottom: 0; left: 0; right: 0; max-height: 45%; background: #fff; border-top: 2px solid #ccc; box-shadow: 0 -2px 8px rgba(0,0,0,0.1); transition: transform 0.2s ease; z-index: 20; display: flex; flex-direction: column; }
#element-panel.panel-hidden { transform: translateY(100%); }
#panel-header { display: flex; align-items: center; gap: 10px; padding: 8px 16px; border-bottom: 1px solid #eee; flex-shrink: 0; }
#panel-header h3 { font-size: 14px; margin: 0; }
#panel-type { color: #888; font-size: 12px; }
#panel-close { margin-left: auto; background: none; border: none; font-size: 20px; cursor: pointer; color: #888; padding: 0 4px; line-height: 1; }
#panel-close:hover { color: #333; }
#panel-body { overflow-y: auto; padding: 12px 16px; flex: 1; }
#panel-body .element-section { margin-bottom: 12px; }
#panel-body .element-section h3 { font-size: 13px; }
#panel-body .props-table th, #panel-body .props-table td { padding: 4px 10px; }
"""

JS_TEMPLATE = """\
(function() {
  var data = MODEL_DATA;

  function $(sel) { return document.querySelector(sel); }
  function $$(sel) { return document.querySelectorAll(sel); }

  // Build tree
  function renderTree(nodes, container, isRoot) {
    var ul = document.createElement("ul");
    ul.className = "tree-list" + (isRoot ? " root" : "");
    nodes.forEach(function(node) {
      var li = document.createElement("li");
      var div = document.createElement("div");
      div.className = "tree-node";
      div.dataset.id = node.id;
      div.dataset.type = node.node_type;
      div.dataset.name = (node.name || "").toLowerCase();

      var toggle = document.createElement("span");
      toggle.className = "tree-toggle";
      if (node.children && node.children.length > 0) {
        toggle.textContent = "\\u25b6";
      }
      div.appendChild(toggle);

      var label = document.createElement("span");
      label.className = "tree-label";
      label.textContent = node.name || "(unnamed)";
      div.appendChild(label);

      li.appendChild(div);

      if (node.children && node.children.length > 0) {
        var childDiv = document.createElement("div");
        childDiv.className = "tree-children";
        renderTree(node.children, childDiv, false);
        li.appendChild(childDiv);

        toggle.addEventListener("click", function(e) {
          e.stopPropagation();
          var open = childDiv.classList.toggle("open");
          toggle.textContent = open ? "\\u25bc" : "\\u25b6";
        });
      }

      if (node.node_type === "group") {
        div.classList.add("tree-group");
        div.addEventListener("click", function() {
          // Groups only toggle children, no navigation
          if (node.children && node.children.length > 0) {
            var childDiv = div.nextElementSibling;
            if (childDiv) {
              var open = childDiv.classList.toggle("open");
              var t = div.querySelector(".tree-toggle");
              if (t) t.textContent = open ? "\\u25bc" : "\\u25b6";
            }
          }
        });
      } else {
        div.addEventListener("click", function() {
          if (node.node_type === "diagram") {
            location.hash = "diagram/" + node.id;
          } else {
            location.hash = "element/" + node.id;
          }
        });
      }

      ul.appendChild(li);
    });
    container.appendChild(ul);
  }

  renderTree(data.tree, $("#tree-container"), true);

  // Welcome view: list diagrams
  var listEl = $("#diagram-list");
  Object.keys(data.diagrams).forEach(function(id) {
    var d = data.diagrams[id];
    var a = document.createElement("a");
    a.className = "diagram-card";
    a.href = "#diagram/" + id;
    a.textContent = d.name || "(unnamed)";
    listEl.appendChild(a);
  });

  // Router
  function route() {
    var hash = location.hash.slice(1);
    var parts = hash.split("/");
    var view = parts[0];
    var id = parts.slice(1).join("/");

    // If a diagram is showing and we navigate to an element, show panel instead
    if (view === "element" && data.elements[id] && diagramVisible) {
      showPanel(id);
      return;
    }

    closePanel();
    $("#welcome-view").style.display = "none";
    $("#diagram-view").style.display = "none";
    $("#element-view").style.display = "none";
    diagramVisible = false;

    // Clear active states
    $$(".tree-node.active").forEach(function(n) { n.classList.remove("active"); });

    if (view === "diagram" && data.diagrams[id]) {
      showDiagram(id);
    } else if (view === "element" && data.elements[id]) {
      showElement(id);
    } else {
      $("#welcome-view").style.display = "";
    }
  }

  var currentPanZoom = null;

  function showDiagram(id) {
    var d = data.diagrams[id];
    $("#diagram-title").textContent = d.name || "(unnamed)";
    var content = $("#diagram-content");
    content.innerHTML = "";

    // Destroy previous pan-zoom instance
    if (currentPanZoom) {
      currentPanZoom.destroy();
      currentPanZoom = null;
    }

    // Add zoom controls
    var controls = document.createElement("div");
    controls.className = "zoom-controls";
    controls.innerHTML = '<button id="zoom-in" title="Zoom in">+</button>'
      + '<button id="zoom-reset" title="Reset view">\\u2302</button>'
      + '<button id="zoom-out" title="Zoom out">\\u2212</button>';
    content.appendChild(controls);

    // Parse embedded SVG content and insert inline
    var svgText = d.svg_content || "";
    if (!svgText) return;

    var parser = new DOMParser();
    var doc = parser.parseFromString(svgText, "image/svg+xml");
    var svg = doc.documentElement;
    if (!svg || svg.nodeName !== "svg") return;

    // Remove fixed width/height so it fills the container, keep viewBox
    svg.removeAttribute("width");
    svg.removeAttribute("height");
    content.appendChild(document.adoptNode(svg));

    // Make view visible BEFORE initializing svg-pan-zoom so the SVG has
    // layout dimensions (getScreenCTM needs a non-zero bounding box)
    $("#diagram-view").style.display = "";
    diagramVisible = true;
    activateTreeNode(id);

    // Initialize svg-pan-zoom after layout is available
    requestAnimationFrame(function() {
      if (typeof svgPanZoom === "function") {
        currentPanZoom = svgPanZoom(svg, {
          zoomEnabled: true,
          panEnabled: true,
          controlIconsEnabled: false,
          fit: true,
          center: true,
          minZoom: 0.1,
          maxZoom: 20,
          zoomScaleSensitivity: 0.3
        });

        // Wire up control buttons
        $("#zoom-in").addEventListener("click", function() { currentPanZoom.zoomIn(); });
        $("#zoom-out").addEventListener("click", function() { currentPanZoom.zoomOut(); });
        $("#zoom-reset").addEventListener("click", function() { currentPanZoom.reset(); });
      }
    });

    // Preserve clickable overlay links within inline SVG
    svg.querySelectorAll("a[href]").forEach(function(a) {
      a.addEventListener("click", function(e) {
        var href = a.getAttribute("href") || a.getAttributeNS("http://www.w3.org/1999/xlink", "href");
        if (href && href.indexOf("#") === 0) {
          e.preventDefault();
          location.hash = href.slice(1);
        }
      });
    });
  }

  function makeSection(title, content) {
    var sec = document.createElement("div");
    sec.className = "element-section";
    var h3 = document.createElement("h3");
    h3.textContent = title;
    sec.appendChild(h3);
    sec.appendChild(content);
    return sec;
  }

  // Render element details into a container (reused by full view and panel)
  function renderElementDetails(el, container) {
    container.innerHTML = "";

    // Properties table
    if (el.properties && el.properties.length > 0) {
      var table = document.createElement("table");
      table.className = "props-table";
      el.properties.forEach(function(p) {
        var tr = document.createElement("tr");
        var th = document.createElement("th");
        th.textContent = p.name;
        var td = document.createElement("td");
        td.textContent = p.value;
        tr.appendChild(th);
        tr.appendChild(td);
        table.appendChild(tr);
      });
      container.appendChild(makeSection("Properties", table));
    }

    // Stereotypes
    if (el.stereotypes && el.stereotypes.length > 0) {
      var div = document.createElement("div");
      el.stereotypes.forEach(function(s) {
        var span = document.createElement("span");
        span.className = "stereotype-tag";
        span.textContent = "\\u00ab" + s + "\\u00bb";
        div.appendChild(span);
      });
      container.appendChild(makeSection("Stereotypes", div));
    }

    // Attributes
    if (el.attributes && el.attributes.length > 0) {
      var ul = document.createElement("ul");
      el.attributes.forEach(function(a) {
        var li = document.createElement("li");
        var code = document.createElement("code");
        code.textContent = a;
        li.appendChild(code);
        ul.appendChild(li);
      });
      container.appendChild(makeSection("Attributes", ul));
    }

    // Operations
    if (el.operations && el.operations.length > 0) {
      var ul = document.createElement("ul");
      el.operations.forEach(function(o) {
        var li = document.createElement("li");
        var code = document.createElement("code");
        code.textContent = o;
        li.appendChild(code);
        ul.appendChild(li);
      });
      container.appendChild(makeSection("Operations", ul));
    }

    // Enumeration literals
    if (el.literals && el.literals.length > 0) {
      var ul = document.createElement("ul");
      el.literals.forEach(function(l) {
        var li = document.createElement("li");
        li.textContent = l;
        ul.appendChild(li);
      });
      container.appendChild(makeSection("Enumeration Literals", ul));
    }

    // Association ends
    if (el.associations && el.associations.length > 0) {
      var table = document.createElement("table");
      table.className = "assoc-table";
      var thead = document.createElement("thead");
      var hr = document.createElement("tr");
      ["Type", "End Name", "Multiplicity", "Aggregation", "Navigable"].forEach(function(h) {
        var th = document.createElement("th");
        th.textContent = h;
        hr.appendChild(th);
      });
      thead.appendChild(hr);
      table.appendChild(thead);
      var tbody = document.createElement("tbody");
      el.associations.forEach(function(a) {
        var tr = document.createElement("tr");
        [a.type, a.name || "-", a.multiplicity || "-", a.aggregation, a.navigable ? "Yes" : "No"].forEach(function(v) {
          var td = document.createElement("td");
          td.textContent = v;
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      container.appendChild(makeSection("Association Ends", table));
    }

    // Generalizations
    if (el.generalizations && el.generalizations.length > 0) {
      var ul = document.createElement("ul");
      el.generalizations.forEach(function(g) {
        var li = document.createElement("li");
        var a = document.createElement("a");
        a.href = "#element/" + g.id;
        a.textContent = g.name + " (" + g.type + ")";
        li.appendChild(a);
        ul.appendChild(li);
      });
      container.appendChild(makeSection("Generalizations", ul));
    }

    // Diagrams
    if (el.diagrams && el.diagrams.length > 0) {
      var dDiv = document.createElement("div");
      el.diagrams.forEach(function(d) {
        var a = document.createElement("a");
        a.href = "#diagram/" + d.id;
        a.textContent = d.name || "(unnamed)";
        a.style.marginRight = "10px";
        dDiv.appendChild(a);
      });
      container.appendChild(makeSection("Appears in diagrams", dDiv));
    }
  }

  function elementTitle(el) {
    var t = el.name || el.formatted || "(unnamed)";
    if (el.stereotypes && el.stereotypes.length > 0) {
      t = "\\u00ab" + el.stereotypes.join(", ") + "\\u00bb " + t;
    }
    return t;
  }

  function showElement(id) {
    var el = data.elements[id];
    if (!el) return;

    closePanel();
    $("#element-title").textContent = elementTitle(el);
    $("#element-type").textContent = el.type;
    renderElementDetails(el, $("#element-details"));
    $("#element-diagrams").innerHTML = "";

    $("#element-view").style.display = "";
    activateTreeNode(id);
  }

  // Bottom panel for showing element details over the diagram
  var diagramVisible = false;

  function showPanel(id) {
    var el = data.elements[id];
    if (!el) return;

    $("#panel-title").textContent = elementTitle(el);
    $("#panel-type").textContent = el.type;
    renderElementDetails(el, $("#panel-body"));
    $("#element-panel").classList.remove("panel-hidden");
  }

  function closePanel() {
    $("#element-panel").classList.add("panel-hidden");
  }

  $("#panel-close").addEventListener("click", closePanel);

  function activateTreeNode(id) {
    $$(".tree-node").forEach(function(n) {
      if (n.dataset.id === id) {
        n.classList.add("active");
        // Expand parents
        var parent = n.parentElement;
        while (parent) {
          if (parent.classList && parent.classList.contains("tree-children")) {
            parent.classList.add("open");
            var toggle = parent.previousElementSibling;
            if (toggle) {
              var t = toggle.querySelector(".tree-toggle");
              if (t) t.textContent = "\\u25bc";
            }
          }
          parent = parent.parentElement;
        }
        n.scrollIntoView({block: "nearest"});
      }
    });
  }

  // Search
  $("#search").addEventListener("input", function() {
    var q = this.value.toLowerCase().trim();
    $$(".tree-node").forEach(function(n) {
      var li = n.parentElement;
      if (!q || (n.dataset.name && n.dataset.name.indexOf(q) !== -1)) {
        li.classList.remove("hidden");
      } else {
        li.classList.add("hidden");
      }
    });
    if (q) {
      $$(".tree-children").forEach(function(c) { c.classList.add("open"); });
    }
  });

  window.addEventListener("hashchange", route);
  route();
})();
"""
