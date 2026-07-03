(function () {
  var header = document.querySelector(".site-header");
  var nav = document.getElementById("site-nav");
  var toggle = document.querySelector(".nav-toggle");
  var navLinks = nav ? nav.querySelectorAll('a[href^="#"]') : [];
  var sections = [];

  function closeNav() {
    if (!nav || !toggle) {
      return;
    }
    nav.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "打开菜单");
  }

  function onScroll() {
    if (header) {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    }

    var activeId = "";
    sections.forEach(function (section) {
      var rect = section.getBoundingClientRect();
      if (rect.top <= 120 && rect.bottom > 120) {
        activeId = section.id;
      }
    });

    navLinks.forEach(function (link) {
      var href = link.getAttribute("href");
      link.classList.toggle("is-active", href === "#" + activeId);
    });
  }

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      toggle.setAttribute("aria-label", isOpen ? "关闭菜单" : "打开菜单");
    });
  }

  navLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      closeNav();
    });
  });

  document.addEventListener("click", function (event) {
    if (!nav || !toggle || !nav.classList.contains("is-open")) {
      return;
    }
    if (nav.contains(event.target) || toggle.contains(event.target)) {
      return;
    }
    closeNav();
  });

  sections = Array.prototype.slice.call(document.querySelectorAll("main section[id]"));
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();
