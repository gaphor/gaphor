/*
 * Gaphor HTML Report - Client-side application
 *
 * Drives the single-page model report: builds the sidebar tree from
 * MODEL_DATA (injected by the generator as a JSON object), handles
 * hash-based routing between diagrams and element detail views, and
 * wires up SVG pan/zoom for interactive diagram exploration.
 *
 * All navigation uses URL hash fragments (#diagram/<id>, #element/<id>)
 * so the report works as a standalone file without a server.
 */
(function() {
  var data = MODEL_DATA;

  function $(sel) { return document.querySelector(sel); }
  function $$(sel) { return document.querySelectorAll(sel); }

  // Map icon names (from gaphor.diagram.iconname) to Font Awesome classes
  // for visual type distinction in the sidebar tree.
  var ICON_CLASSES = {
    "gaphor-diagram-symbolic":          "fa-solid fa-image",
    "gaphor-package-symbolic":          "fa-solid fa-box",
    "gaphor-profile-symbolic":          "fa-solid fa-box",
    "gaphor-class-symbolic":            "fa-solid fa-c",
    "gaphor-interface-symbolic":        "fa-regular fa-circle",
    "gaphor-component-symbolic":        "fa-solid fa-puzzle-piece",
    "gaphor-block-symbolic":            "fa-solid fa-square",
    "gaphor-enumeration-symbolic":      "fa-solid fa-list-ol",
    "gaphor-data-type-symbolic":        "fa-solid fa-hashtag",
    "gaphor-primitive-type-symbolic":   "fa-solid fa-hashtag",
    "gaphor-actor-symbolic":            "fa-solid fa-user",
    "gaphor-use-case-symbolic":         "fa-regular fa-circle-dot",
    "gaphor-activity-symbolic":         "fa-solid fa-play",
    "gaphor-state-machine-symbolic":    "fa-solid fa-diagram-project",
    "gaphor-interaction-symbolic":      "fa-solid fa-arrows-left-right",
    "gaphor-artifact-symbolic":         "fa-regular fa-file",
    "gaphor-node-symbolic":             "fa-solid fa-server",
    "gaphor-device-symbolic":           "fa-solid fa-desktop",
    "gaphor-association-symbolic":      "fa-solid fa-link",
    "gaphor-dependency-symbolic":       "fa-solid fa-arrow-right",
    "gaphor-generalization-symbolic":   "fa-solid fa-arrow-up",
    "gaphor-realization-symbolic":      "fa-solid fa-arrow-up",
    "gaphor-requirement-symbolic":      "fa-solid fa-check",
    "gaphor-constraint-symbolic":       "fa-solid fa-code",
    "gaphor-comment-symbolic":          "fa-regular fa-comment",
    "gaphor-property-symbolic":         "fa-solid fa-circle-info",
    "gaphor-operation-symbolic":        "fa-solid fa-gear",
    "gaphor-port-symbolic":             "fa-solid fa-plug",
    "gaphor-connector-symbolic":        "fa-solid fa-minus",
    "gaphor-stereotype-symbolic":       "fa-solid fa-tag",
    "gaphor-collaboration-symbolic":    "fa-solid fa-people-group",
    "gaphor-information-flow-symbolic": "fa-solid fa-right-long",
    "gaphor-signal-symbolic":           "fa-solid fa-bolt",
    "gaphor-value-type-symbolic":       "fa-solid fa-hashtag",
    "gaphor-constraint-block-symbolic": "fa-solid fa-code",
    "gaphor-interface-block-symbolic":  "fa-regular fa-circle",
    "gaphor-relationship":              "fa-solid fa-folder"
  };

  function iconClass(node) {
    return ICON_CLASSES[node.icon] || "fa-solid fa-circle";
  }

  /*
   * Recursively build the sidebar tree from the nested node structure.
   * "group" nodes act as non-navigable folders (packages, namespaces);
   * diagram and element nodes navigate via hash change on click.
   */
  function toggleNode(childDiv, toggle) {
    var open = childDiv.classList.toggle("open");
    toggle.textContent = open ? "\u25bc" : "\u25b6";
  }

  function renderTree(nodes, container, isRoot) {
    var ul = document.createElement("ul");
    ul.className = "tree-list" + (isRoot ? " root" : "");
    nodes.forEach(function(node) {
      var li = document.createElement("li");
      var div = document.createElement("div");
      div.className = "tree-node";
      div.dataset.id = node.id;
      div.dataset.type = node.node_type;
      // Store lowercase name for case-insensitive search filtering
      div.dataset.name = (node.name || "").toLowerCase();

      var toggle = document.createElement("span");
      toggle.className = "tree-toggle";
      if (node.children && node.children.length > 0) {
        toggle.textContent = "\u25b6";
      }
      div.appendChild(toggle);

      var icon = document.createElement("i");
      icon.className = "tree-icon " + iconClass(node);
      div.appendChild(icon);

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

        // Stop propagation so toggling children doesn't also trigger
        // the node's own click handler (which would navigate away)
        toggle.addEventListener("click", function(e) {
          e.stopPropagation();
          toggleNode(childDiv, toggle);
        });
      }

      if (node.node_type === "group") {
        div.classList.add("tree-group");
        div.addEventListener("click", function() {
          // Groups only toggle children, no navigation
          if (node.children && node.children.length > 0) {
            toggleNode(childDiv, toggle);
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

  // Populate the welcome screen with clickable diagram cards
  var listEl = $("#diagram-list");
  Object.keys(data.diagrams).forEach(function(id) {
    var d = data.diagrams[id];
    var a = document.createElement("a");
    a.className = "diagram-card";
    a.href = "#diagram/" + id;
    a.textContent = d.name || "(unnamed)";
    listEl.appendChild(a);
  });

  /*
   * Hash-based router. Parses the URL fragment to decide which view
   * to display. When a diagram is already visible, element links open
   * in a slide-up panel instead of replacing the diagram -- this lets
   * users inspect elements without losing their place in the diagram.
   */
  function route() {
    var hash = location.hash.slice(1);
    var parts = hash.split("/");
    var view = parts[0];
    // Rejoin remaining parts to support IDs that contain slashes
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

  /*
   * Display a diagram by parsing its embedded SVG string into a live
   * DOM node and initializing svg-pan-zoom for interactive navigation.
   * Also intercepts clicks on overlay <a> elements (injected by
   * svg_overlay.py) to route them through our hash-based navigation.
   */
  function showDiagram(id) {
    var d = data.diagrams[id];
    $("#diagram-title").textContent = d.name || "(unnamed)";
    var content = $("#diagram-content");
    content.innerHTML = "";

    // Clean up previous instance to avoid leaking event listeners
    if (currentPanZoom) {
      currentPanZoom.destroy();
      currentPanZoom = null;
    }

    var controls = document.createElement("div");
    controls.className = "zoom-controls";
    controls.innerHTML = '<button id="zoom-in" title="Zoom in">+</button>'
      + '<button id="zoom-reset" title="Reset view">\u2302</button>'
      + '<button id="zoom-out" title="Zoom out">\u2212</button>';
    content.appendChild(controls);

    var svgText = d.svg_content || "";
    if (!svgText) return;

    var parser = new DOMParser();
    var doc = parser.parseFromString(svgText, "image/svg+xml");
    var svg = doc.documentElement;
    if (!svg || svg.nodeName !== "svg") return;

    // Let the SVG scale to fill its container via CSS; the viewBox
    // attribute (preserved) handles the internal coordinate mapping
    svg.removeAttribute("width");
    svg.removeAttribute("height");
    // adoptNode transfers ownership from the parsed document to ours,
    // avoiding a cross-document insertion error
    content.appendChild(document.adoptNode(svg));

    // The view must be visible BEFORE initializing svg-pan-zoom because
    // getScreenCTM() returns null when the SVG has zero layout dimensions
    $("#diagram-view").style.display = "";
    diagramVisible = true;
    activateTreeNode(id);

    // Defer pan-zoom init to the next frame so the browser has completed
    // layout and the SVG has real dimensions for getScreenCTM()
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

        $("#zoom-in").addEventListener("click", function() { currentPanZoom.zoomIn(); });
        $("#zoom-out").addEventListener("click", function() { currentPanZoom.zoomOut(); });
        $("#zoom-reset").addEventListener("click", function() { currentPanZoom.reset(); });
      }
    });

    // SVG <a> elements injected by svg_overlay.py use fragment hrefs
    // (#element/<id>). Since the SVG is inlined (not in an <object>),
    // we must intercept clicks and update our location.hash manually.
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

  function makeCodeList(items) {
    var ul = document.createElement("ul");
    items.forEach(function(text) {
      var li = document.createElement("li");
      var code = document.createElement("code");
      code.textContent = text;
      li.appendChild(code);
      ul.appendChild(li);
    });
    return ul;
  }

  function makePlainList(items) {
    var ul = document.createElement("ul");
    items.forEach(function(text) {
      var li = document.createElement("li");
      li.textContent = text;
      ul.appendChild(li);
    });
    return ul;
  }

  /* Wrap content in a titled section div for consistent element detail layout. */
  function makeSection(title, content) {
    var sec = document.createElement("div");
    sec.className = "element-section";
    var h3 = document.createElement("h3");
    h3.textContent = title;
    sec.appendChild(h3);
    sec.appendChild(content);
    return sec;
  }

  /*
   * Render all detail sections for a model element (properties, stereotypes,
   * attributes, operations, associations, etc.) into the given container.
   * Shared between the full-page element view and the slide-up panel so
   * both show identical content.
   */
  function renderElementDetails(el, container) {
    container.innerHTML = "";

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

    if (el.stereotypes && el.stereotypes.length > 0) {
      var div = document.createElement("div");
      el.stereotypes.forEach(function(s) {
        var span = document.createElement("span");
        span.className = "stereotype-tag";
        span.textContent = "\u00ab" + s + "\u00bb";
        div.appendChild(span);
      });
      container.appendChild(makeSection("Stereotypes", div));
    }

    if (el.attributes && el.attributes.length > 0) {
      container.appendChild(makeSection("Attributes", makeCodeList(el.attributes)));
    }

    if (el.operations && el.operations.length > 0) {
      container.appendChild(makeSection("Operations", makeCodeList(el.operations)));
    }

    if (el.literals && el.literals.length > 0) {
      container.appendChild(makeSection("Enumeration Literals", makePlainList(el.literals)));
    }

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

  /* Format an element's display title, prepending stereotypes in guillemets. */
  function elementTitle(el) {
    var t = el.name || el.formatted || "(unnamed)";
    if (el.stereotypes && el.stereotypes.length > 0) {
      t = "\u00ab" + el.stereotypes.join(", ") + "\u00bb " + t;
    }
    return t;
  }

  /* Show the full-page element detail view (used when no diagram is active). */
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

  // Tracks whether a diagram is currently displayed, so the router
  // knows to use the slide-up panel for element navigation instead
  // of replacing the diagram view.
  var diagramVisible = false;

  /*
   * Show element details in a slide-up panel overlaying the diagram.
   * This keeps the diagram visible while inspecting an element clicked
   * in the SVG overlay.
   */
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

  /*
   * Highlight a node in the sidebar tree and expand all its ancestor
   * nodes so it becomes visible. This keeps the tree in sync with
   * whatever is shown in the main content area.
   */
  function activateTreeNode(id) {
    var n = document.querySelector('.tree-node[data-id="' + id + '"]');
    if (!n) return;
    n.classList.add("active");
    // Walk up the DOM to expand collapsed ancestor containers,
    // so the active node is visible without manual tree navigation
    var parent = n.parentElement;
    while (parent) {
      if (parent.classList && parent.classList.contains("tree-children")) {
        parent.classList.add("open");
        var toggle = parent.previousElementSibling;
        if (toggle) {
          var t = toggle.querySelector(".tree-toggle");
          if (t) t.textContent = "\u25bc";
        }
      }
      parent = parent.parentElement;
    }
    n.scrollIntoView({block: "nearest"});
  }

  // Live-filter the sidebar tree by substring match on node names.
  // When a query is active, all tree sections are forced open so
  // matches nested deep in the hierarchy are visible.
  $("#search").addEventListener("input", function() {
    var q = this.value.toLowerCase().trim();
    var allNodes = $$(".tree-node");

    if (!q) {
      // No query: show everything, collapse tree
      allNodes.forEach(function(n) { n.parentElement.classList.remove("hidden"); });
      $$(".tree-children").forEach(function(c) { c.classList.remove("open"); });
      return;
    }

    // Hide all first
    allNodes.forEach(function(n) { n.parentElement.classList.add("hidden"); });

    // Show matches and their ancestors
    allNodes.forEach(function(n) {
      if (n.dataset.name && n.dataset.name.indexOf(q) !== -1) {
        var el = n.parentElement;
        while (el) {
          if (el.tagName === "LI") el.classList.remove("hidden");
          if (el.classList && el.classList.contains("tree-children")) el.classList.add("open");
          el = el.parentElement;
        }
      }
    });
  });

  // Run the router on hash changes and on initial page load
  window.addEventListener("hashchange", route);
  route();
})();
