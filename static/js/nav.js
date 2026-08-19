/* =====================================================================
   nav.js — Gestion accessible des menus mobiles (header + sidebar).
   Pattern : aria-expanded + aria-controls, fermeture Escape, click
   extérieur, focus trap optionnel, SOAP baseline.
   ===================================================================== */
(function () {
  "use strict";

  function isOpen(el) {
    return el && el.getAttribute("data-open") === "true";
  }
  function setOpen(el, open) {
    if (!el) return;
    el.setAttribute("data-open", open ? "true" : "false");
  }
  function setExpanded(el, expanded) {
    if (!el) return;
    el.setAttribute("aria-expanded", expanded ? "true" : "false");
  }

  /* /////
     Menu mobile du header public (.nav-toggle + .primary-nav + .menu-overlay)
  ///// */
  function setupHeaderNav() {
    var toggle = document.querySelector(".nav-toggle[data-controls='primary-nav']");
    var nav = document.getElementById("primary-nav");
    var overlay = document.querySelector(".menu-overlay");
    if (!toggle || !nav) return;

    var lastFocus = null;

    function open() {
      lastFocus = document.activeElement;
      setOpen(nav, true);
      setExpanded(toggle, true);
      if (overlay) setOpen(overlay, true);
      document.body.style.overflow = "hidden";
      // Met le focus sur le premier lien
      var firstLink = nav.querySelector("a, button");
      if (firstLink) firstLink.focus();
    }
    function close() {
      setOpen(nav, false);
      setExpanded(toggle, false);
      if (overlay) setOpen(overlay, false);
      document.body.style.overflow = "";
      if (lastFocus && typeof lastFocus.focus === "function") {
        lastFocus.focus();
      }
    }
    function toggle() { isOpen(nav) ? close() : open(); }

    toggle.addEventListener("click", toggle);
    if (overlay) overlay.addEventListener("click", close);

    nav.addEventListener("click", function (e) {
      // Ferme sur clic d'un lien de la nav (UX mobile).
      if (e.target.matches("a") && e.target.getAttribute("href") !== "#") {
        // Conserve la navigation : ferme simplement l'overlay.
        var wasOpen = isOpen(nav);
        if (wasOpen) close();
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen(nav)) {
        close();
        toggle.focus();
      }
    });

    // Reset sur passage desktop.
    var mq = window.matchMedia("(min-width: 880px)");
    function resetOnDesktop() {
      if (mq.matches && isOpen(nav)) close();
    }
    if (mq.addEventListener) mq.addEventListener("change", resetOnDesktop);
    else if (mq.addListener) mq.addListener(resetOnDesktop);
  }

  /* /////
     Sidebar dashboard (.sidebar-toggle + .sidebar + .sidebar-overlay)
  ///// */
  function setupSidebar() {
    var toggle = document.querySelector(".sidebar-toggle");
    var sidebar = document.querySelector(".sidebar");
    var overlay = document.querySelector(".sidebar-overlay");
    if (!toggle || !sidebar) return;

    var lastFocus = null;

    function open() {
      lastFocus = document.activeElement;
      setOpen(sidebar, true);
      setExpanded(toggle, true);
      if (overlay) setOpen(overlay, true);
      document.body.style.overflow = "hidden";
      var firstLink = sidebar.querySelector("a, button");
      if (firstLink) firstLink.focus();
    }
    function close() {
      setOpen(sidebar, false);
      setExpanded(toggle, false);
      if (overlay) setOpen(overlay, false);
      document.body.style.overflow = "";
      if (lastFocus && typeof lastFocus.focus === "function") {
        lastFocus.focus();
      }
    }
    function toggleFn() { isOpen(sidebar) ? close() : open(); }

    toggle.addEventListener("click", toggleFn);
    if (overlay) overlay.addEventListener("click", close);

    sidebar.addEventListener("click", function (e) {
      if (e.target.matches("a") && e.target.getAttribute("href") !== "#") {
        if (isOpen(sidebar)) close();
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen(sidebar)) {
        close();
        toggle.focus();
      }
    });

    var mq = window.matchMedia("(min-width: 880px)");
    function resetOnDesktop() {
      if (mq.matches && isOpen(sidebar)) close();
    }
    if (mq.addEventListener) mq.addEventListener("change", resetOnDesktop);
    else if (mq.addListener) mq.addListener(resetOnDesktop);
  }

  /* /////
     Toggle des filtres (panel collapsible mobile)
  ///// */
  function setupFiltersToggle() {
    var toggle = document.querySelector(".filters-toggle");
    var panel = document.querySelector(".filters");
    if (!toggle || !panel) return;
    toggle.addEventListener("click", function () {
      var open = panel.getAttribute("data-open") === "true";
      panel.setAttribute("data-open", open ? "false" : "true");
      toggle.setAttribute("aria-expanded", open ? "false" : "true");
    });
    var mq = window.matchMedia("(min-width: 1024px)");
    function reset() {
      if (mq.matches) {
        panel.setAttribute("data-open", "true");
        toggle.setAttribute("aria-hidden", "true");
      } else {
        panel.setAttribute("data-open", "false");
        toggle.setAttribute("aria-expanded", "false");
        toggle.removeAttribute("aria-hidden");
      }
    }
    if (mq.addEventListener) mq.addEventListener("change", reset);
    else if (mq.addListener) mq.addListener(reset);
    reset();
  }

  /* /////
     Toggle carte (vue map/list sur les structures)
  ///// */
  function setupMapToggle() {
    var toggle = document.querySelector(".map-toggle");
    var wrap = document.querySelector(".map-wrapper");
    if (!toggle || !wrap) return;
    if (window.matchMedia && window.matchMedia("(min-width: 1100px)").matches) return;
    toggle.addEventListener("click", function () {
      var open = wrap.getAttribute("data-open") === "true";
      wrap.setAttribute("data-open", open ? "false" : "true");
      toggle.setAttribute("aria-expanded", open ? "false" : "true");
    });
  }

  function init() {
    setupHeaderNav();
    setupSidebar();
    setupFiltersToggle();
    setupMapToggle();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else { init(); }
})();
