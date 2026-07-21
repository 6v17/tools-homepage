(function () {
  function setText(nodes, value) {
    Array.prototype.forEach.call(nodes, function (node) {
      node.textContent = value;
    });
  }

  function setHref(nodes, value) {
    Array.prototype.forEach.call(nodes, function (node) {
      node.setAttribute("href", value);
    });
  }

  function renderRequirements(items) {
    var list = document.getElementById("requirements-list");
    if (!list || !Array.isArray(items)) {
      return;
    }
    list.innerHTML = items.map(function (item) {
      return "<li>" + item + "</li>";
    }).join("");
  }

  function renderChangelog(changelog) {
    var root = document.getElementById("changelog-root");
    if (!root || !changelog || !Array.isArray(changelog.sections)) {
      return;
    }

    var summary = document.getElementById("changelog-summary");
    if (summary) {
      summary.textContent = "v" + changelog.version + " 更新说明";
    }

    root.innerHTML = changelog.sections.map(function (section) {
      var items = (section.items || []).map(function (item) {
        return "<li>" + item + "</li>";
      }).join("");
      return (
        '<section class="changelog-group">' +
        "<h4>" + section.title + "</h4>" +
        "<ul>" + items + "</ul>" +
        "</section>"
      );
    }).join("");
  }

  function updateSchema(site) {
    var node = document.querySelector('script[type="application/ld+json"]');
    if (!node) {
      return;
    }
    try {
      var data = JSON.parse(node.textContent);
      var graph = data["@graph"] || [];
      graph.forEach(function (entry) {
        if (entry["@type"] === "SoftwareApplication") {
          entry.softwareVersion = site.version.current;
          entry.downloadUrl = site.downloads.current.url;
        }
      });
      node.textContent = JSON.stringify(data);
    } catch (_error) {
      /* keep static fallback */
    }
  }

  function applyLinks(links) {
    if (!links) {
      return;
    }
    Object.keys(links).forEach(function (key) {
      setHref(document.querySelectorAll('[data-site="link-' + key + '"]'), links[key]);
    });
  }

  function applySite(site) {
    setText(document.querySelectorAll('[data-site="version-label"]'), site.version.label);
    setText(document.querySelectorAll('[data-site="download-current-label"]'), site.downloads.current.label);
    setText(document.querySelectorAll('[data-site="download-previous-label"]'), site.downloads.previous.label);
    setHref(document.querySelectorAll('[data-site="download-current"]'), site.downloads.current.url);
    setHref(document.querySelectorAll('[data-site="download-previous"]'), site.downloads.previous.url);
    setHref(document.querySelectorAll('[data-site="runtime-link"]'), site.resources.runtime.url);
    applyLinks(site.links);
    renderRequirements(site.requirements);
    renderChangelog(site.changelog);
    updateSchema(site);
  }

  fetch("./site.json", { cache: "no-cache" })
    .then(function (response) {
      if (!response.ok) {
        throw new Error("site.json unavailable");
      }
      return response.json();
    })
    .then(applySite)
    .catch(function () {
      /* HTML fallback values remain visible */
    });
})();
